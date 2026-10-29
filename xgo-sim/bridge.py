"""Test equipment: replace Arduino Bridge transport with external MCU/body emulator."""
import base64
import json
import socket
import threading
import time


class SimulationBridge:
    def __init__(self, host='body', port=7802):
        self.host, self.port = host, port
        self.callbacks = {}
        self.conn = None
        self.lock = threading.Lock()
        self.closed = threading.Event()

    def provide(self, name, callback):
        self.callbacks[name] = callback

    def notify(self, method, payload):
        data = (json.dumps({'method': method, 'payload': base64.b64encode(payload).decode()}) + '\n').encode()
        with self.lock:
            if self.conn:
                try:
                    self.conn.sendall(data)
                except OSError:
                    self.conn.close()
                    self.conn = None

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while not self.closed.is_set():
            try:
                conn = socket.create_connection((self.host, self.port), timeout=3)
                conn.settimeout(3)
                with self.lock:
                    self.conn = conn
                with conn.makefile('rb') as stream:
                    while not self.closed.is_set():
                        raw = stream.readline(8192)
                        if not raw:
                            raise ConnectionError('MCU emulator disconnected')
                        msg = json.loads(raw)
                        callback = self.callbacks.get(msg['method'])
                        if callback:
                            callback(base64.b64decode(msg['payload'], validate=True))
            except (OSError, ValueError, KeyError) as exc:
                print('Simulation bridge:', str(exc), flush=True)
            finally:
                with self.lock:
                    if self.conn:
                        self.conn.close()
                    self.conn = None
            self.closed.wait(1)
