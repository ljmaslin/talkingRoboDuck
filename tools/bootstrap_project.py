"""Prepare pinned dependencies, apply our runtime overlay and fetch offline ASR.

Python 3.10+, Git and internet are needed for first setup. No paid service or
GitHub credential is required for public dependencies. Existing vendor edits
that conflict with the integration patch are preserved and reported.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from urllib.request import urlopen
import venv
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'vosk-model-small-en-us-0.15'
MODEL_SHA256 = '30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498'
MODEL_URL = f'https://alphacephei.com/vosk/models/{MODEL}.zip'


def run(*args, cwd=ROOT, check=True):
    return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-archive', type=Path, help='Use an existing, hash-verified Vosk ZIP instead of downloading.')
    parser.add_argument('--skip-model', action='store_true', help='Prepare source only; package builds still need the Vosk model.')
    args = parser.parse_args()
    if sys.version_info < (3, 10): raise RuntimeError('Python 3.10 or newer is required.')
    pins = json.loads((ROOT/'upstream-revisions.json').read_text())
    for folder, info in pins.items():
        target = ROOT/folder
        if not (target/'.git').exists():
            print(f'Initialising {folder}...', flush=True)
            run('git', 'submodule', 'update', '--init', '--recursive', '--', folder)
        head = run('git', 'rev-parse', 'HEAD', cwd=target).stdout.strip()
        if head != info['revision']:
            raise RuntimeError(f'{folder}: HEAD differs from upstream-revisions.json; review before updating.')
    vendor = ROOT/'xgo-runtime'
    patch = ROOT/'runtime-overlay/upstream.patch'
    already = run('git', 'apply', '--reverse', '--check', str(patch), cwd=vendor, check=False)
    if already.returncode:
        valid = run('git', 'apply', '--check', str(patch), cwd=vendor, check=False)
        if valid.returncode:
            raise RuntimeError('Existing runtime edits conflict with the saved patch. Export/review them before bootstrapping.')
        run('git', 'apply', str(patch), cwd=vendor)
    source = ROOT/'runtime-overlay/python/talkingduck'
    for path in source.rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts: continue
        target = vendor/'python/talkingduck'/path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    if not args.skip_model:
        archive = args.model_archive or ROOT/f'models/{MODEL}.zip'
        archive.parent.mkdir(parents=True, exist_ok=True)
        if not archive.is_file():
            if args.model_archive: raise RuntimeError(f'Model archive missing: {archive}')
            print('Downloading the 41 MB offline English model...', flush=True)
            partial = archive.with_suffix('.zip.part')
            with urlopen(MODEL_URL, timeout=60) as response, partial.open('wb') as output:
                shutil.copyfileobj(response, output)
            if hashlib.sha256(partial.read_bytes()).hexdigest() != MODEL_SHA256:
                raise RuntimeError('Downloaded model checksum mismatch; nothing extracted.')
            partial.replace(archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != MODEL_SHA256:
            raise RuntimeError('Model archive checksum mismatch; nothing extracted.')
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                relative = PurePosixPath(member.filename)
                if relative.is_absolute() or '..' in relative.parts or not relative.parts or relative.parts[0] != MODEL:
                    raise RuntimeError('Unexpected path in model archive.')
                if member.is_dir(): continue
                destination = ROOT/'models'/relative.as_posix()
                expected = bundle.read(member)
                if not destination.is_file() or destination.read_bytes() != expected:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(expected)
    python = ROOT/('.venv/Scripts/python.exe' if sys.platform == 'win32' else '.venv/bin/python')
    if not python.is_file(): venv.EnvBuilder(with_pip=True).create(ROOT/'.venv')
    print('Pinned sources and runtime overlay ready. No cloud APIs enabled.')
    print('Next: run Start-XgoDuck.cmd (Windows), or build the ZIP and use Docker Compose.')


if __name__ == '__main__':
    try: main()
    except (RuntimeError, subprocess.CalledProcessError, OSError, zipfile.BadZipFile) as error:
        print(f'Setup failed: {error}', file=sys.stderr)
        sys.exit(1)
