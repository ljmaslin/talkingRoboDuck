import { execFile } from "node:child_process";

// User text goes over stdin; it is never interpreted as PowerShell code.
const script = `
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$text = [Console]::In.ReadToEnd()
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$buffer = New-Object System.IO.MemoryStream
try {
  $speaker.SetOutputToWaveStream($buffer)
  $speaker.Speak($text)
  $speaker.SetOutputToNull()
  [Console]::Out.Write([Convert]::ToBase64String($buffer.ToArray()))
} finally { $speaker.Dispose(); $buffer.Dispose() }
`;
export function windowsSpeech(text) {
  return new Promise((resolve, reject) => {
    if (process.platform !== "win32") { reject(new Error("Windows speech is unavailable on this server.")); return; }
    const child = execFile("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command", script],
      { windowsHide: true, timeout: 20000, maxBuffer: 8 * 1024 * 1024 },
      (error, stdout) => {
        if (error) { reject(new Error("Windows could not generate speech. Check that a Windows speech voice is installed.")); return; }
        const wav = Buffer.from(stdout.trim(), "base64");
        if (wav.toString("ascii", 0, 4) !== "RIFF") { reject(new Error("Windows returned no playable speech.")); return; }
        resolve(wav);
      });
    child.stdin.on("error", () => {});
    child.stdin.end(text);
  });
}
