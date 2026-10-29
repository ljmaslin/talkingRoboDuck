// Fallback verification of a newly launched, isolated headless Chrome profile.
// No personal browser, accounts, microphone permission or external pages used.
import {writeFile} from 'node:fs/promises';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const profile=fileURLToPath(new URL('../.chrome-xgo-debug',import.meta.url));
const chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',[
  '--headless=new','--no-first-run','--disable-extensions','--use-angle=swiftshader',
  '--enable-unsafe-swiftshader','--user-data-dir='+profile,'--remote-debugging-port=9223',
  '--remote-debugging-address=127.0.0.1','http://127.0.0.1:5173/'
],{windowsHide:true,stdio:'ignore'});
for(let i=0;i<30;i++){try{await fetch('http://127.0.0.1:9223/json/version');break;}catch{await new Promise(r=>setTimeout(r,500));}}
const tabs=await(await fetch('http://127.0.0.1:9223/json')).json();
const tab=tabs.find(t=>t.type==='page'&&t.url.startsWith('http://127.0.0.1:5173'));
if(!tab)throw Error('Isolated XGO test page not found');
const socket=new WebSocket(tab.webSocketDebuggerUrl), pending=new Map(), errors=[];let id=0;
await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
socket.onmessage=event=>{const m=JSON.parse(event.data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);m.error?p.reject(Error(m.error.message)):p.resolve(m.result);}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);};
function call(method,params={}){return new Promise((resolve,reject)=>{const seq=++id;pending.set(seq,{resolve,reject});socket.send(JSON.stringify({id:seq,method,params}));});}
await call('Runtime.enable');
await call('Emulation.setDeviceMetricsOverride',{width:1400,height:1100,deviceScaleFactor:1,mobile:false});
await call('Page.reload',{ignoreCache:true});
await fetch('http://127.0.0.1:5173/duck/reset',{method:'POST',headers:{Origin:'http://127.0.0.1:5173'},body:'{}'});
await new Promise(r=>setTimeout(r,500));
// Leave physics paused at spawn. Movement is verified by test_integration.py;
// this check verifies the rendered initial state without enabling motors.
let state;
for(let i=0;i<25;i++){
  const reply=await call('Runtime.evaluate',{expression:`JSON.stringify({viewer:document.getElementById('viewer-status')?.textContent,state:document.getElementById('state')?.textContent,recordDisabled:document.getElementById('record')?.disabled,canvas:!!document.querySelector('canvas')})`,returnByValue:true});
  state=JSON.parse(reply.result.value);
  if(state.viewer?.includes('XGO measured pose')&&!state.recordDisabled)break;
  await new Promise(r=>setTimeout(r,1000));
}
const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
await writeFile(new URL('../artifacts/xgo-viewer.png',import.meta.url),Buffer.from(shot.data,'base64'));
await writeFile(new URL('../artifacts/xgo-browser-check.json',import.meta.url),JSON.stringify({state,errors,scope:'Isolated headless Chrome; software renderer; no live mic test'},null,2));
console.log(JSON.stringify({state,errors},null,2));
const closed=new Promise(resolve=>socket.addEventListener('close',resolve,{once:true}));
await Promise.race([call('Browser.close'),closed,new Promise(resolve=>setTimeout(resolve,1500))]);
socket.close();
if(!state.canvas||state.recordDisabled||!state.viewer?.includes('XGO measured pose')||errors.length)process.exitCode=1;
