"""Check packaged files and run on the installed bundle, including under ARM64."""
import hashlib
import json
from pathlib import Path
import platform
import sys
import os
import zipfile

app = Path('/opt/apps/talking-xgo')
bundle = os.environ.get('XGO_BUNDLE_ZIP')
if bundle:
    with zipfile.ZipFile(bundle) as archive:
        archive.extractall('/tmp/xgo-verified')
    app = Path('/tmp/xgo-verified/talking-xgo')
manifest = json.loads((app/'manifest.json').read_text())
for relative, digest in manifest['files'].items():
    assert hashlib.sha256((app/relative).read_bytes()).hexdigest() == digest, relative
assert not manifest['contains_simulator']
assert manifest['target'] == 'Arduino UNO Q / Arduino App Lab'
sys.path.insert(0, str(app/'python'))
from policy import Policy
from talkingduck.speech import Recognizer

models = []
for name in ('walk', 'getup', 'pick', 'roulade', 'roller'):
    policy = Policy()
    ok, reason = policy.load(f'xgoduck_{name}.onnx')
    assert ok, reason
    models.append(reason)
recognizer = Recognizer(str(app/'python/talkingduck/model'), require_wake=True)
speech = {}
for name in ('stand','walk','stop','sit','negated','unprefixed'):
    result = recognizer.recognize((Path('/fixtures')/f'{name}.wav').read_bytes())
    assert result['command'] == (None if name in ('negated','unprefixed') else name), result
    speech[name] = result['transcript']
report = {'architecture': platform.machine(), 'manifest_files_verified': len(manifest['files']),
          'models': models, 'speech': speech, 'status':'passed',
          'physical_hardware_validated': False, 'scope':'Debian bookworm / Python 3.12 ARM64 emulation'}
if bundle:
    report['package_sha256'] = hashlib.sha256(Path(bundle).read_bytes()).hexdigest()
if os.environ.get('XGO_VERIFY_REPORT'):
    Path(os.environ['XGO_VERIFY_REPORT']).write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
