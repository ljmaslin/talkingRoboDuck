"""Capture our runtime edits without copying the complete upstream project.

Use after editing xgo-runtime directly. Normal development can edit runtime-overlay
and run bootstrap_project.py to apply those sources to the runtime checkout.
"""
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
vendor = ROOT/'xgo-runtime'
overlay = ROOT/'runtime-overlay'
pin = json.loads((ROOT/'upstream-revisions.json').read_text())['xgo-runtime']['revision']
head = subprocess.check_output(['git', '-C', str(vendor), 'rev-parse', 'HEAD'], text=True).strip()
if head != pin:
    raise RuntimeError('Runtime HEAD differs from the recorded upstream pin; review the dependency update first.')
overlay.mkdir(exist_ok=True)
patch = subprocess.check_output(['git', '-C', str(vendor), 'diff', '--binary', '--no-ext-diff', pin])
(overlay/'upstream.patch').write_bytes(patch)
source = vendor/'python/talkingduck'
count = 0
for path in source.rglob('*'):
    if not path.is_file() or '__pycache__' in path.parts or 'model' in path.relative_to(source).parts:
        continue
    target = overlay/'python/talkingduck'/path.relative_to(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)
    count += 1
print(f'Exported {count} application files and the upstream integration patch.')
