"""Test equipment only: run packaged XGO controller with a simulated Bridge."""
import json
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from bridge import SimulationBridge
from controller import Controller
from talkingduck.speech import SpeechApplication, make_handler

bridge = SimulationBridge(os.environ.get('XGO_BODY_HOST', 'body'))
controller = Controller(bridge)
for name, callback in [('duck_state', controller.receive), ('duck_boot_pd', controller.receive_boot_pd),
    ('duck_raw', controller.receive_raw), ('duck_servo_reply', controller.receive_servo_reply),
    ('duck_cal_reply', controller.receive_cal_reply)]:
    bridge.provide(name, callback)
speech = SpeechApplication(controller)
bridge.start()
threading.Thread(target=controller.run, name='policy50', daemon=True).start()

class VendorAPI(BaseHTTPRequestHandler):
    def log_message(self, *_): pass
    def reply(self, status, value):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        if self.path == '/api/status': self.reply(200, controller.status())
        else: self.reply(404, {'error': 'No such route'})
    def do_POST(self):
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size <= 8192: raise ValueError('Invalid body size')
            body = json.loads(self.rfile.read(size))
            routes = {'/api/mode': lambda: controller.set_mode(body['mode']),
                      '/api/command': lambda: controller.command(**body),
                      '/api/pick': controller.start_pick,
                      '/api/roller': lambda: controller.set_roller_mode(body['enabled'])}
            if self.path not in routes: self.reply(404, {'error': 'No such route'}); return
            self.reply(200, routes[self.path]())
        except (ValueError, KeyError, TypeError) as exc:
            self.reply(400, {'error': str(exc)})

threading.Thread(target=ThreadingHTTPServer(('0.0.0.0', 9527), VendorAPI).serve_forever, daemon=True).start()
print('Packaged XGO speech + vendor Controller; external MCU emulator connected via test Bridge', flush=True)
try:
    ThreadingHTTPServer(('0.0.0.0', 8765), make_handler(speech.recognizer, speech.actions, accept_wav=True)).serve_forever()
finally:
    speech.close()
    controller.stop()
