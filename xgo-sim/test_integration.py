"""Exercise real packaged ASR + XGO controller + external physics, no paid services."""
import json
import math
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:5173'
def request(path, body=None, audio=False):
    headers = {'Origin': BASE}
    if body is not None:
        headers['Content-Type'] = 'audio/wav' if audio else 'application/json'
        body = body if audio else json.dumps(body).encode()
    req = urllib.request.Request(BASE+path, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)

def command(text): return request('/duck/command', {'text':text})
def audio(name): return request('/duck/audio', (ROOT/'xgo-sim/fixtures'/f'{name}.wav').read_bytes(), True)

report = {'target': 'XGO-Duck', 'physical_hardware_validated': False, 'checks': {}}
report['package_sha256'] = json.loads((ROOT/'artifacts/talking-xgo-0.2.0.manifest.json').read_text())['package_sha256']
request('/duck/reset', {})
time.sleep(.3)
state = request('/duck/state')
assert state['backend'] == 'XGO UNO Q controller'
assert state['controller_state']['full_robot_ready']
assert state['physics']['robot'] == 'XGO-Duck'
assert len(request('/duck/model')['geoms']) >= 14
report['checks']['backend_and_geometry'] = True

for name in ('unprefixed', 'negated', 'ambiguous', 'question'):
    result = audio(name)
    assert not result['controller']['accepted'], (name, result)
    assert request('/duck/state')['controller_state']['mode'] in ('off', 'shadow')
    report['checks'][name] = {'accepted': False, 'transcript': result['transcript']}

result = audio('sit')
assert result['command'] == 'sit' and not result['controller']['accepted'], result
assert 'no deployed' in result['controller']['reason']
report['checks']['sit_unavailable'] = result

result = audio('stand')
assert result['command'] == 'stand' and result['controller']['accepted'], result
time.sleep(3)
before = request('/duck/state')
assert before['controller_state']['mode'] == 'policy'
assert before['physics']['enabled']
assert .10 < before['physics']['trunk_z'] < .19, before['physics']
report['checks']['spoken_stand'] = {'result': result, 'physics': before['physics']}

result = audio('walk')
assert result['command'] == 'walk' and result['controller']['accepted'], result
time.sleep(2.5)
after = request('/duck/state')
travel = math.dist(before['physics']['base'][:2], after['physics']['base'][:2])
assert travel > .03, ('No measured forward movement', travel, after['physics'])
assert .09 < after['physics']['trunk_z'] < .20, after['physics']
assert after['controller_state']['command'] == [0,0,0], 'Walk did not expire'
report['checks']['spoken_walk_and_expiry'] = {'travel_m': travel, 'result': result, 'physics': after['physics']}

assert command('walk')['controller']['accepted']
time.sleep(.2)
assert audio('stop')['controller']['accepted']
time.sleep(.3)
state = request('/duck/state')
assert state['controller_state']['command'] == [0,0,0]
assert not state['controller_state']['last_error'], state['controller_state']['last_error']
report['checks']['spoken_stop_cancels_walk'] = True
report['rates'] = {key: state['controller_state'][key] for key in ('feedback_hz','inference_hz','bad_frames','mcu_invalid_commands')}
report['status'] = 'passed'
(ROOT/'artifacts/xgo-integration.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps({'status':'passed','checks':len(report['checks']),'travel_m':round(travel,3),'rates':report['rates']}, indent=2))
