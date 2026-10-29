"""Build an App Lab import ZIP and a manifest; no simulator files are shipped."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
OUT.mkdir(exist_ok=True)
if not (ROOT/'xgo-runtime/python/talkingduck/native/aarch64/libatomic.so.1').is_file():
    raise RuntimeError('Bundled ARM64 libatomic is missing; do not ship an incomplete voice app.')
# Add the voice panel to the vendor's own App Lab web interface.
voice_client = (ROOT/'viewer/client.js').read_text(encoding='utf8')
voice_client = voice_client[voice_client.index('let ready ='):]
voice_client = voice_client[:voice_client.index('el("reset").onclick')]
voice_client = voice_client.replace('"/duck/audio"', '"/api/speech/audio"').replace('"/duck/command"', '"/api/speech/command"')
voice_client = voice_client.replace('const state = await request("/duck/state");', 'const state = {backend:"XGO UNO Q", controller_state:await request("/api/status")};')
(ROOT/'xgo-runtime/assets/talk-client.js').write_text(voice_client, encoding='utf8')
page = (ROOT/'viewer/index.html').read_text(encoding='utf8')
before = page.index('<div class="layout"><section>')
voice = page.index('<section><h2>Talk to your duck')
page = page[:before]+page[voice:]
page = page.replace('</section></div></main>', '<p id="state"></p><small id="physics"></small></section></main>')
page = page.replace('src="/client.js"', 'src="/talk-client.js"')
page = page.replace('Your XGO controller and offline speech application, connected to its simulated body.',
                    'Offline speech commands processed on this UNO Q. Your browser microphone supplies the audio.')
page = page.replace('Speech and policy run in the onboard role. MuJoCo and emulated motor/sensor feedback run in separate test equipment. This browser draws measured poses using WebGL.',
                    'Use the supplied controller page for hardware commissioning before enabling motion. Speech is an additional control input.')
page = page.replace('The 14-joint physics model does not animate the separate mouth motor.', 'The mouth motor is controlled separately from the walking policy.')
(ROOT/'xgo-runtime/assets/talk.html').write_text(page, encoding='utf8')
index = ROOT/'xgo-runtime/assets/index.html'
vendor_page = index.read_text(encoding='utf8')
if 'talk.html' not in vendor_page:
    vendor_page = vendor_page.replace('<main>', '<main><p style="padding:12px"><a href="talk.html">Open Talking XGO voice commands</a></p>', 1)
    index.write_text(vendor_page, encoding='utf8')
files = {}
def revision(folder):
    return subprocess.check_output(['git', '-C', str(ROOT / folder), 'rev-parse', 'HEAD'], text=True).strip()
manifest = dict(name='talking-xgo', version='0.2.0', target='Arduino UNO Q / Arduino App Lab',
    runtime_revision=revision('xgo-runtime'), rl_revision=revision('xgo-rl'),
    model='XGO-Duck with Feetech 1910 actuator parameters',
    spoken_prefix='Duck', contains_simulator=False, contains_firmware_source=True,
    paid_api_enabled=False, physical_hardware_validated=False,
    unsupported_commands={'sit': 'No supplied XGO sit/stand policy in deployed runtime'}, files=files)
package = OUT / 'talking-xgo-0.2.0.zip'
with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=3) as archive:
    roots = [(ROOT/'xgo-runtime', None),
             (ROOT/'models/vosk-model-small-en-us-0.15', 'python/talkingduck/model')]
    for folder, prefix in roots:
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or any(part in ('.git', '__pycache__') for part in path.relative_to(folder).parts):
                continue
            relative = path.relative_to(folder).as_posix()
            relative = f'{prefix}/{relative}' if prefix else relative
            content = path.read_bytes()
            files[relative] = hashlib.sha256(content).hexdigest()
            archive.writestr('talking-xgo/' + relative, content)
    archive.writestr('talking-xgo/manifest.json', json.dumps(manifest, indent=2))
manifest['package_sha256'] = hashlib.sha256(package.read_bytes()).hexdigest()
(OUT/'talking-xgo-0.2.0.manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
print(json.dumps({'package': str(package), 'files': len(files), 'size_mb': round(package.stat().st_size/1e6, 1),
                  'sha256': manifest['package_sha256']}, indent=2))
