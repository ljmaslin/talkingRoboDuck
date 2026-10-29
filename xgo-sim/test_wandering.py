"""Measured room avoidance with real XGO ONNX/BAM physics; no browser gait."""
import json
import math
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def request(url, value=None):
    data = json.dumps(value).encode() if value is not None else None
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as response: return json.load(response)

def command(text):
    return request('http://127.0.0.1:8875/command', {'text': text})

command('stop')
request('http://127.0.0.1:9527/api/mode', {'mode': 'off'})
request('http://127.0.0.1:8766/reset', {})
time.sleep(.5)
assert command('wander')['controller']['accepted']
samples = []
try:
    for i in range(90):
        time.sleep(1)
        robot = request('http://127.0.0.1:8875/state')['controller_state']
        physics = request('http://127.0.0.1:8766/state')
        samples.append({'second': i+1, 'base': physics['base'], 'height': physics['trunk_z'],
            'contacts': physics['room_contact_steps'], 'command': robot['command'],
            'wandering': robot['wandering'], 'error': robot['speech_last_error']})
        assert robot['wandering']['active'], samples[-1]
        assert not robot['speech_last_error'], samples[-1]
        assert .09 < physics['trunk_z'] < .22, samples[-1]
        assert max(abs(v) for v in physics['base'][:2]) < 1.12, samples[-1]
        assert physics['room_contact_steps'] == 0, samples[-1]
        if i % 15 == 0:
            print(json.dumps(samples[-1]), flush=True)
finally:
    command('stop')
assert samples[-1]['wandering']['turns'] >= 2, 'No repeated obstacle avoidance'
travel = sum(math.dist(a['base'][:2], b['base'][:2]) for a, b in zip(samples, samples[1:]))
assert travel > .5, ('No substantial measured movement', travel)
time.sleep(.3)
stopped = request('http://127.0.0.1:8875/state')['controller_state']
assert not stopped['wandering']['active'] and stopped['command'] == [0, 0, 0]
report = {'status': 'passed', 'seconds': len(samples), 'measured_path_m': travel,
    'obstacle_turns': samples[-1]['wandering']['turns'], 'room_contact_steps': samples[-1]['contacts'],
    'sensor': 'Ideal simulated horizontal depth slice; no physical sensor driver',
    'physical_hardware_validated': False, 'samples': samples,
    'package_sha256': json.loads((ROOT/'artifacts/talking-xgo-0.2.0.manifest.json').read_text())['package_sha256']}
(ROOT/'artifacts/xgo-wandering-check.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'samples'}), flush=True)
