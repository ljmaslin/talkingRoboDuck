import { startNativeView } from "./view.js";
const el = id => document.getElementById(id);
startNativeView(el("view"), el("viewer-status")).catch(error => {
  el("viewer-status").textContent = "Browser renderer unavailable: " + error.message;
});
let ready = false, recorder = null, media = null, pending = false, recordingUrl = null;
let recordingTimer = null, currentRequest = 0;
function controls() {
  el("record").disabled = !ready || pending || recorder?.state === "recording";
  el("finish").disabled = recorder?.state !== "recording";
  el("send").disabled = !ready || pending;
  document.querySelectorAll("[data-command]").forEach(button => { button.disabled = !ready || pending; });
}
async function request(path, options = {}) {
  const response = await fetch(path, { ...options, signal: AbortSignal.timeout(30000) });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error ?? `Request failed (${response.status})`);
  return result;
}
function showResult(result) {
  if ("transcript" in result) el("transcript").textContent = `Heard: ${result.transcript || "(no speech)"} · confidence ${result.confidence} · recognition ${result.recognition_ms} ms`;
  const controller = result.controller;
  el("result").textContent = controller.accepted
    ? `Controller accepted ${result.command ?? "command"}. ${controller.reason ?? "Watch the state and pose for completion."}`
    : `No movement: ${result.command === null && "transcript" in result
      ? 'Speech was not accepted as a complete movement command. Start with “Duck”: say “Duck, stand up”, “Duck, walk forward” or “Duck, stop”. Sit is not deployed for XGO.'
      : controller.reason ?? "Controller refused the command."}`;
}
async function command(text) {
  pending = true; controls();
  try { showResult(await request("/duck/command", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) })); }
  catch (error) { el("result").textContent = error.message; }
  finally { pending = false; controls(); }
}
document.querySelectorAll("[data-command]").forEach(button => button.onclick = () => command(button.dataset.command));
el("typed").onsubmit = event => { event.preventDefault(); if (ready && !pending) command(el("text").value); };

async function wavFromBlob(blob) {
  const Audio = window.AudioContext || window.webkitAudioContext;
  if (!Audio) throw new Error("This browser cannot decode microphone audio. Use Chrome or Edge outside the editor preview.");
  const context = new Audio();
  try {
    const decoded = await context.decodeAudioData(await blob.arrayBuffer());
    const frames = Math.min(160000, Math.ceil(decoded.duration * 16000));
    const offline = new OfflineAudioContext(1, frames, 16000);
    const source = offline.createBufferSource(); source.buffer = decoded; source.connect(offline.destination); source.start();
    const mono = (await offline.startRendering()).getChannelData(0);
    const bytes = new ArrayBuffer(44 + mono.length * 2), view = new DataView(bytes);
    const label = (offset, text) => [...text].forEach((char, i) => view.setUint8(offset + i, char.charCodeAt(0)));
    label(0, "RIFF"); view.setUint32(4, bytes.byteLength - 8, true); label(8, "WAVE"); label(12, "fmt ");
    view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, 1, true);
    view.setUint32(24, 16000, true); view.setUint32(28, 32000, true); view.setUint16(32, 2, true); view.setUint16(34, 16, true);
    label(36, "data"); view.setUint32(40, mono.length * 2, true);
    mono.forEach((sample, i) => view.setInt16(44 + i * 2, Math.max(-1, Math.min(1, sample)) * (sample < 0 ? 32768 : 32767), true));
    return bytes;
  } finally { await context.close(); }
}

el("record").onclick = async () => {
  if (pending || !ready) return;
  const requestId = ++currentRequest;
  pending = true; controls();
  el("mic").textContent = "Waiting for microphone permission…";
  try {
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) throw new Error("Open this page in a separate Chrome or Edge window to use the microphone.");
    media = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
    if (requestId !== currentRequest) { media.getTracks().forEach(track => track.stop()); return; }
    const chunks = [];
    const rec = new MediaRecorder(media); recorder = rec;
    rec.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
    rec.onerror = () => { el("mic").textContent = "Microphone recording failed. Check the input device."; media.getTracks().forEach(track => track.stop()); pending = false; controls(); };
    rec.onstop = async () => {
      clearTimeout(recordingTimer); media.getTracks().forEach(track => track.stop());
      pending = true; controls();
      try {
        if (requestId !== currentRequest) return;
        if (!chunks.length) throw new Error("No audio data captured.");
        const blob = new Blob(chunks, { type: rec.mimeType });
        if (recordingUrl) URL.revokeObjectURL(recordingUrl);
        recordingUrl = URL.createObjectURL(blob); el("recording").src = recordingUrl; el("recording").hidden = false;
        el("mic").textContent = "Processing speech in the local robot service…";
        const wav = await wavFromBlob(blob);
        const result = await request("/duck/audio", { method: "POST", headers: { "Content-Type": "audio/wav" }, body: wav });
        if (requestId !== currentRequest) return;
        showResult(result); el("mic").textContent = "Speech processed. The transcript and controller result are shown below.";
      } catch (error) { el("mic").textContent = error.message; }
      finally { pending = false; controls(); }
    };
    rec.start(250); pending = false; controls();
    el("mic").textContent = "Recording. Say “Duck” followed by one command, then press Stop and process. Maximum 10 seconds.";
    recordingTimer = setTimeout(() => { if (rec.state === "recording") rec.stop(); }, 10000);
  } catch (error) {
    media?.getTracks().forEach(track => track.stop()); pending = false; controls();
    el("mic").textContent = error.name === "NotAllowedError" ? "Microphone permission denied. Allow Microphone in Chrome's site settings and Windows privacy settings." : error.message;
  }
};
el("finish").onclick = () => { if (recorder?.state === "recording") recorder.stop(); };
window.addEventListener("pagehide", () => { currentRequest++; clearTimeout(recordingTimer); if (recorder?.state === "recording") recorder.stop(); media?.getTracks().forEach(track => track.stop()); });

async function poll() {
  try {
    const state = await request("/duck/state");
    const controller = state.controller_state;
    const wander = controller.wandering;
    if (wander) el('wander-state').textContent = `Wandering: ${wander.active ? wander.phase : 'idle'} · turns: ${wander.turns} · ${wander.nearest_m === undefined ? '' : 'nearest: '+wander.nearest_m+' m · '}${wander.sensor}${controller.speech_last_error ? ' · '+controller.speech_last_error : ''}`;
    ready = controller.full_robot_ready === true && controller.control_ready === true;
    el("state").textContent = `${state.backend} · ${ready ? "controller ready" : "waiting for feedback"} · mode: ${controller.mode} · ${Math.round(controller.feedback_hz)} Hz feedback / ${Math.round(controller.inference_hz)} Hz policy`;
    el("physics").textContent = state.physics ? `Physics ${state.physics.realtime_factor}× real time · trunk height ${state.physics.trunk_z} m${state.physics.render_error ? " · Render error: " + state.physics.render_error : ""}` : "";
  } catch (error) { ready = false; el("state").textContent = error.message; }
  controls(); setTimeout(poll, 500);
}
poll();


el("reset").onclick = async () => {
  try { await request('/duck/reset', {method:'POST',body:'{}'}); el('result').textContent='Simulation reset. Stand / get up enables XGO policies.'; }
  catch (error) { el('result').textContent=error.message; }
};
