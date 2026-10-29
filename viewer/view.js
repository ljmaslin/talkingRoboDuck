import * as THREE from 'three';
import { OrbitControls } from './vendor/OrbitControls.js';

// Draw only MuJoCo's measured geometry transforms. No browser physics or gait.
export async function startNativeView(container, status) {
  const renderer = new THREE.WebGLRenderer({antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.setClearColor(0x152c34);
  container.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xf1f7ff,0x5a6570,2));
  const light = new THREE.DirectionalLight(0xfff4dd,3); light.position.set(1,3,2); scene.add(light);
  const grid=new THREE.GridHelper(12,120,0x6f959b,0x35515b);scene.add(grid);
  const camera = new THREE.PerspectiveCamera(40,1,.005,100); camera.position.set(2.1,2.4,2.7);
  const controls = new OrbitControls(camera,renderer.domElement); controls.target.set(0,.12,0); controls.enableDamping=true;
  const root = new THREE.Group(); root.rotation.x=-Math.PI/2; scene.add(root);
  const resize = new ResizeObserver(()=>{const w=container.clientWidth,h=container.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}); resize.observe(container);
  status.textContent='Loading XGO geometry…';
  const response = await fetch('/duck/model'); if(!response.ok)throw Error('XGO model unavailable');
  const model = await response.json(), meshes = new Map();
  const geometry = new Map();
  for(const [id,data] of Object.entries(model.meshes)) {
    const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(data.vertices,3));g.setIndex(data.indices);g.computeVertexNormals();geometry.set(id,g);
  }
  for(const g of model.geoms){
    let shape=geometry.get(g.mesh);
    if(g.type==='box'){shape=new THREE.BoxGeometry(...g.size.map(v=>v*2));geometry.set('room-'+g.id,shape);}
    const mesh=new THREE.Mesh(shape,new THREE.MeshStandardMaterial({color:g.color,roughness:.7}));mesh.visible=false;root.add(mesh);meshes.set(g.id,mesh);
  }
  const samples=[], stream=new EventSource('/duck/poses');let arrival=0,frames=0,report=performance.now(),fps=0,lastSim=-1;
  stream.onmessage=event=>{try{const p=JSON.parse(event.data);if(!Number.isFinite(p.sim_t)||!p.geoms?.every(g=>g.length===8&&g.every(Number.isFinite)))return;if(p.sim_t<lastSim)samples.length=0;lastSim=p.sim_t;p.at=performance.now();arrival=p.at;samples.push(p);while(samples.length>12)samples.shift();}catch{}};
  stream.onerror=()=>{samples.length=0;};
  const qa=new THREE.Quaternion(),qb=new THREE.Quaternion(),v=new THREE.Vector3(),target=new THREE.Vector3(),delta=new THREE.Vector3();let firstPose=true;
  const gl=renderer.getContext(),debug=gl.getExtension('WEBGL_debug_renderer_info');
  const gpu=debug?gl.getParameter(debug.UNMASKED_RENDERER_WEBGL):'WebGL';
  let closed=false;
  function animate(now){
    if(closed)return;
    while(samples.length>2&&samples[1].at<now-80)samples.shift();
    const a=samples[0],b=samples[1]??a;
    if(a&&b){const t=a===b?1:THREE.MathUtils.clamp((now-80-a.at)/(b.at-a.at),0,1);const next=new Map(b.geoms.map(g=>[g[0],g]));for(const g of a.geoms){const h=next.get(g[0])??g,m=meshes.get(g[0]);if(!m)continue;m.position.set(g[1],g[2],g[3]).lerp(v.set(h[1],h[2],h[3]),t);qa.set(g[5],g[6],g[7],g[4]);qb.set(h[5],h[6],h[7],h[4]);m.quaternion.copy(qa).slerp(qb,t);m.visible=true;}
      // Keep the room in frame rather than following every step of the duck.
      target.set(0,.08,0);delta.copy(target).sub(controls.target);controls.target.add(delta);camera.position.add(delta);firstPose=false;
    }
    controls.update();renderer.render(scene,camera);frames++;
    if(now-report>1000){fps=Math.round(frames*1000/(now-report));frames=0;report=now;status.textContent=`${arrival&&now-arrival<500?'XGO measured pose':'Pose paused: waiting for telemetry'} · ${fps} FPS · ${gpu}`;}
    requestAnimationFrame(animate);
  }requestAnimationFrame(animate);
  window.addEventListener('pagehide',()=>{closed=true;stream.close();resize.disconnect();controls.dispose();renderer.dispose();for(const g of geometry.values())g.dispose();for(const mesh of meshes.values())mesh.material.dispose();},{once:true});
}
