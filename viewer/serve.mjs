import http from 'node:http';
import {createReadStream} from 'node:fs';
import {stat} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Readable} from 'node:stream';
import {pipeline} from 'node:stream/promises';
import {windowsSpeech} from './windows-speech.mjs';
const root=fileURLToPath(new URL('./',import.meta.url));
const app=process.env.XGO_APP_URL??'http://127.0.0.1:8875',body=process.env.XGO_BODY_URL??'http://127.0.0.1:8766';
const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.txt':'text/plain'};
http.createServer(async(req,res)=>{
  const route=new URL(req.url,'http://localhost').pathname;
  if(req.method==='POST'&&!['http://127.0.0.1:5173','http://localhost:5173'].includes(req.headers.origin)){res.writeHead(403).end();return;}
  if(route==='/duck/poses'){
    if(req.method!=='GET'){res.writeHead(405).end();return;}
    const cancel=new AbortController();res.on('close',()=>cancel.abort());
    try{const upstream=await fetch(body+'/poses',{signal:cancel.signal});if(!upstream.ok)throw Error();res.writeHead(200,{'Content-Type':'text/event-stream','Cache-Control':'no-store'});res.flushHeaders();await pipeline(Readable.fromWeb(upstream.body),res);}catch{if(!res.headersSent)res.writeHead(503).end('XGO pose stream unavailable');else res.end();}return;
  }
  if(route.startsWith('/duck/')){
    const routes={'/duck/state':[app+'/state','GET'],'/duck/model':[body+'/model','GET'],'/duck/audio':[app+'/audio','POST'],'/duck/command':[app+'/command','POST'],'/duck/reset':[body+'/reset','POST']};
    const target=routes[route];if(!target){res.writeHead(404).end();return;}if(req.method!==target[1]){res.writeHead(405).end();return;}
    try{
      const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>400000){res.writeHead(413).end();return;}chunks.push(chunk);}
      if(route==='/duck/reset'){
        const stopped=await fetch(app+'/command',{method:'POST',headers:{'Content-Type':'application/json'},body:'{"text":"stop"}',signal:AbortSignal.timeout(5000)});
        if(!stopped.ok)throw Error('Could not cancel robot behaviour');
        const off=await fetch('http://127.0.0.1:9527/api/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:'{"mode":"off"}',signal:AbortSignal.timeout(5000)});
        if(!off.ok)throw Error('Could not disarm before reset');
      }
      const upstream=await fetch(target[0],{method:req.method,signal:AbortSignal.timeout(30000),...(req.method==='POST'?{body:Buffer.concat(chunks),headers:{'Content-Type':req.headers['content-type']??'application/octet-stream'}}:{})});
      let payload=Buffer.from(await upstream.arrayBuffer());
      if(route==='/duck/state'&&upstream.ok){const state=JSON.parse(payload);const physics=await fetch(body+'/state',{signal:AbortSignal.timeout(5000)});if(!physics.ok)throw Error('XGO physics unavailable');state.physics=await physics.json();payload=Buffer.from(JSON.stringify(state));}
      res.writeHead(upstream.status,{'Content-Type':'application/json','Content-Length':payload.length,'Cache-Control':'no-store'}).end(payload);
    }catch{res.writeHead(503,{'Content-Type':'application/json'}).end(JSON.stringify({error:'XGO simulator unavailable. Check Docker Desktop and the XGO container logs.'}));}return;
  }
  if(route==='/local-speech'&&req.method==='POST'){
    try{let raw='';for await(const chunk of req){raw+=chunk;if(raw.length>8000)throw Error('Too much text');}const {text}=JSON.parse(raw);const wav=await windowsSpeech(text);res.writeHead(200,{'Content-Type':'audio/wav'}).end(wav);}catch(e){res.writeHead(503,{'Content-Type':'application/json'}).end(JSON.stringify({error:e.message}));}return;
  }
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405).end();return;}
  if(route==='/native.html'){res.writeHead(302,{Location:'/'}).end();return;}
  try{const file=path.resolve(root,'.'+(route==='/'?'/index.html':decodeURIComponent(route)));const relative=path.relative(root,file);if(relative.startsWith('..')||path.isAbsolute(relative)){res.writeHead(403).end();return;}const info=await stat(file);if(!info.isFile())throw Error();res.writeHead(200,{'Content-Type':mime[path.extname(file)]??'application/octet-stream','Content-Length':info.size,'X-Content-Type-Options':'nosniff'});if(req.method==='HEAD')res.end();else createReadStream(file).on('error',()=>res.destroy()).pipe(res);}catch{res.writeHead(404).end();}
}).listen(5173,'127.0.0.1',()=>console.log('Talking XGO Duck: http://127.0.0.1:5173'));
