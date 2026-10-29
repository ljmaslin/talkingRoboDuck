"""Physical microphone adapter; ALSA supplies PCM, not a browser or simulator."""
import io
import json
import subprocess
import threading
import time
import wave


class AlsaCapture:
    def __init__(self, recognizer, robot, device):
        self.recognizer, self.robot, self.device = recognizer, robot, device
        self.closing = threading.Event()
        self.child = None

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        from vosk import KaldiRecognizer
        while not self.closing.is_set():
            try:
                # Select the actual USB microphone device after checking the UNO Q audio setup.
                self.child = subprocess.Popen(["arecord", "-q", "-D", self.device,
                    "-f", "S16_LE", "-r", "16000", "-c", "1", "-t", "raw"],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                decoder = KaldiRecognizer(self.recognizer.model, 16000)
                pcm = bytearray()
                overflow = False
                while not self.closing.is_set():
                    chunk = self.child.stdout.read(8000)
                    if not chunk:
                        raise RuntimeError("ALSA capture stopped; check device access and whether another service owns the microphone")
                    pcm.extend(chunk)
                    with self.recognizer.lock:
                        endpoint = decoder.AcceptWaveform(chunk)
                        partial = json.loads(decoder.PartialResult()).get("partial", "") if not endpoint else ""
                    if len(pcm) > 320000:
                        if endpoint or partial:
                            overflow = True
                        else:
                            # Drop only old silence, not the beginning of an utterance.
                            del pcm[:-64000]
                    if endpoint:
                        if not overflow:
                            buffer = io.BytesIO()
                            with wave.open(buffer, "wb") as output:
                                output.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
                                output.writeframes(pcm)
                            result = self.recognizer.recognize(buffer.getvalue())
                            if result["command"]:
                                result["controller"] = self.robot.execute(result["command"])
                            print(json.dumps({"audio_source": "alsa", **result}), flush=True)
                        pcm.clear()
                        overflow = False
                        decoder = KaldiRecognizer(self.recognizer.model, 16000)
            except Exception as error:
                print(json.dumps({"audio_source": "alsa", "error": str(error)}), flush=True)
            finally:
                if self.child and self.child.poll() is None:
                    self.child.terminate()
                    try:
                        self.child.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        self.child.kill()
                        self.child.wait()
            self.closing.wait(3)

    def close(self):
        self.closing.set()
        if self.child and self.child.poll() is None:
            self.child.terminate()
