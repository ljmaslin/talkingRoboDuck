"""Portable offline speech -> XGO controller service. No browser speech API or cloud inference."""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import re
import socket
import threading
import time
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

APP_VERSION = "0.2.0"

PHRASES = {
    "sit": "sit", "sit down": "sit", "duck sit": "sit",
    "stand": "stand", "stand up": "stand", "duck stand": "stand",
    "walk": "walk", "walk forward": "walk", "duck walk": "walk",
    "stop": "stop", "duck stop": "stop",
    "duck sit down": "sit", "duck stand up": "stand", "duck walk forward": "walk",
    "pick": "pick", "duck pick": "pick", "open beak": "open beak", "duck open beak": "open beak",
    "close beak": "close beak", "duck close beak": "close beak", "rest": "rest", "duck rest": "rest",
    "standup": "stand", "duck standup": "stand",
    "wander": "wander", "duck wander": "wander", "explore": "wander", "duck explore": "wander",
}


def command_for(text: str) -> str | None:
    # Exact, complete utterances only: "do not sit" must never trigger "sit".
    return PHRASES.get(re.sub(r"\s+", " ", text.strip().lower()))


def select_spoken_command(general, candidate, general_conf, candidate_conf, require_wake):
    words = general.split()
    veto = {"not", "don't", "never", "no", "can't", "cannot", "and", "or",
        "what", "where", "when", "why", "who", "how", "could", "would", "can"}
    # The general decoder supplies vetoes, not a comparable probability: its
    # confidence changes with its much larger vocabulary.
    if candidate_conf < 0.95 or veto.intersection(words):
        return None
    if require_wake and (not candidate.startswith("duck ") or len(words) < 2):
        return None
    command = command_for(candidate)
    other = command_for(general)
    if other is not None and other != command:
        return None
    if len(words) > len(candidate.split()) + 1:
        return None
    return command


class Recognizer:
    def __init__(self, model_path: str, require_wake=False):
        # Vosk's aarch64 wheel links libatomic. Ship that small runtime library
        # with its Debian copyright so App Lab needs no ad-hoc apt modification.
        import ctypes
        import platform
        native = Path(__file__).parent / 'native' / platform.machine() / 'libatomic.so.1'
        if native.is_file():
            ctypes.CDLL(str(native), mode=ctypes.RTLD_GLOBAL)
        from vosk import Model, SetLogLevel
        SetLogLevel(-1)
        self.model = Model(model_path)
        self.lock = threading.Lock()
        self.require_wake = require_wake

    def recognize(self, wav_bytes: bytes) -> dict:
        from vosk import KaldiRecognizer
        with wave.open(io.BytesIO(wav_bytes), "rb") as audio:
            if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getcomptype()) != (1, 2, 16000, "NONE"):
                raise ValueError("Audio must be mono 16-bit PCM WAV at 16000 Hz.")
            if not 1600 <= audio.getnframes() <= 168000:
                raise ValueError("Record between 0.1 and 10 seconds.")
            pcm = audio.readframes(audio.getnframes())
        def decode(grammar=None):
            decoder = KaldiRecognizer(self.model, 16000) if grammar is None else KaldiRecognizer(self.model, 16000, json.dumps(grammar))
            decoder.SetWords(True)
            segments = []
            for start in range(0, len(pcm), 8000):
                if decoder.AcceptWaveform(pcm[start:start + 8000]):
                    segments.append(json.loads(decoder.Result()))
            segments.append(json.loads(decoder.FinalResult()))
            text = " ".join(segment.get("text", "") for segment in segments).strip()
            words = [word for segment in segments for word in segment.get("result", [])]
            confidence = min((word.get("conf", 0) for word in words), default=0)
            return text, confidence
        verbs = ("sit", "stand", "walk", "stop", "wander", "explore")
        rejected_phrases = [prefix + "do not " + verb for prefix in ("", "duck ") for verb in verbs]
        rejected_phrases += ["duck " + first + " and " + second for first in verbs for second in verbs]
        with self.lock:
            general, general_conf = decode()
            candidate, candidate_conf = decode(list(PHRASES) + rejected_phrases + ["[unk]"])
        command = select_spoken_command(general, candidate, general_conf, candidate_conf, self.require_wake)
        return {"transcript": candidate if command else general, "general_transcript": general,
            "confidence": round(candidate_conf if command else general_conf, 3), "command": command,
            "command_transcript": candidate, "command_confidence": round(candidate_conf, 3),
            "recognition_mode": "command vocabulary with general-language veto"}


def make_handler(recognizer, robot, accept_wav=False):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send_json(self, status, value):
            payload = json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            try:
                if self.path == "/state":
                    self.send_json(200, {"backend": "XGO UNO Q controller", "app_version": APP_VERSION,
                        "controller_state": robot.snapshot(), "speech": "Vosk offline",
                        "supported": ["stand", "walk", "wander", "stop", "pick", "open beak", "close beak", "rest"],
                        "unavailable": {"sit": "No deployed XGO sit/stand policy"}})
                else:
                    self.send_json(404, {"error": "Not found"})
            except Exception as error:
                self.send_json(503, {"error": str(error)})

        def do_POST(self):
            try:
                if self.headers.get("Origin") not in (None, "http://127.0.0.1:5173", "http://localhost:5173"):
                    self.send_json(403, {"error": "Origin not allowed"})
                    return
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 400000:
                    self.send_json(413, {"error": "Audio or command too large"})
                    return
                body = self.rfile.read(length)
                if self.path == "/audio":
                    if not accept_wav:
                        self.send_json(403, {"error": "WAV input is disabled; select the wav-http audio adapter explicitly."})
                        return
                    started = time.monotonic()
                    result = recognizer.recognize(body)
                    result["recognition_ms"] = round((time.monotonic() - started) * 1000)
                    result["controller"] = robot.execute(result["command"]) if result["command"] else {
                        "accepted": False, "reason": "No confident complete command was recognised. Start with Duck: stand up, walk forward or stop. Sit is not deployed for XGO."}
                    self.send_json(200, result)
                elif self.path == "/command":
                    command = command_for(json.loads(body).get("text", ""))
                    self.send_json(200, {"command": command, "controller": robot.execute(command)})
                else:
                    self.send_json(404, {"error": "Not found"})
            except (ValueError, wave.Error) as error:
                self.send_json(400, {"error": str(error)})
            except Exception as error:
                self.send_json(503, {"error": str(error)})
    return Handler



class SpeechApplication:
    """Robot application logic; hardware and simulation import exactly this class."""
    def __init__(self, controller):
        from .actions import Actions
        from .wandering import HttpRanges
        range_url = os.environ.get('TALKING_DUCK_RANGE_URL')
        self.actions = Actions(controller, HttpRanges(range_url) if range_url else None)
        model = os.environ.get('VOSK_MODEL', str(Path(__file__).parent / 'model'))
        self.recognizer = Recognizer(model, require_wake=True)
        self.capture = None
        if os.environ.get('TALKING_DUCK_AUDIO_SOURCE', 'none') == 'alsa':
            from .alsa_capture import AlsaCapture
            self.capture = AlsaCapture(self.recognizer, self.actions,
                os.environ.get('TALKING_DUCK_ALSA_DEVICE', 'default'))
            self.capture.start()

    def audio(self, wav):
        started = time.monotonic()
        result = self.recognizer.recognize(wav)
        result['recognition_ms'] = round((time.monotonic() - started) * 1000)
        result['controller'] = self.actions.execute(result['command']) if result['command'] else {
            'accepted': False, 'reason': 'Say Duck followed by one complete command.'}
        return result

    def command(self, body: dict):
        command = command_for(body.get('text', ''))
        return {'command': command, 'controller': self.actions.execute(command)}

    def close(self):
        self.actions.stop()
        if self.capture:
            self.capture.close()
