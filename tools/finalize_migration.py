"""Keep procurement records current and record the XGO migration provenance."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = ROOT/'research/procurement'
plan = (p/'build-plan.md').read_text(encoding='utf8').replace(
    'Our existing Vosk recognition logic is reusable, but the XGO motor-control\nadapter must target its UNO/Linux/STM32 runtime, not the Pollen robotd socket.',
    'The offline Vosk application has now been ported to the XGO UNO/Linux/STM32\nruntime. See the project README and DEPLOYMENT.md for the current implementation.')
(p/'build-plan.md').write_text(plan, encoding='utf8')
(p/'options-comparison.md').write_text('''# XGO build options

The electronics kit is purchased: £306.46 including shipping, user-reported.
No soldering equipment is required for the standard kit build. The current
selection is the full-size A1. Earlier alternative-robot research has been
retired with the old development stack.

| Option | Budget including £75 reserve | Trade-off |
|---|---:|---|
| A1 mini, matched kit, no audio yet | £825.79 | All audited individual duck parts fit; smallest budget |
| Full A1, matched kit, no audio yet | £875.79 | Selected; larger future prints and batches |
| A1 mini plus candidate bench audio | £876.49 | Microphone/speaker experiment; battery integration unverified |
| Full A1 plus candidate bench audio | £926.49 | Selected printer with optional later audio experiment |

VAT and remaining delivery/handling charges are estimates. These totals include
the kit payment already made; approximately £569.33 remains under the selected
no-audio budget, including reserve. No paid AI or custom PCB manufacture included.

Individually sourcing exact motors and mechanical parts was more expensive at
the audited listings and left an incomplete basket. The matched kit avoids that
procurement work while retaining printing, assembly, calibration and programming.

See [order-list.md](order-list.md), [all listings](priced-listings.md) and
[editable calculator](cost-calculator.html). Listing prices were checked on
27 October 2026 and are not new supplier quotations.
''', encoding='utf8')
manifest = json.loads((ROOT/'artifacts/talking-xgo-0.2.0.manifest.json').read_text())
removed = json.loads((ROOT/'artifacts/retired-pollen-paths.json').read_text(encoding='utf-8-sig'))
record = dict(target='XGO-Duck / Arduino UNO Q', runtime_revision=manifest['runtime_revision'],
    rl_revision=manifest['rl_revision'], package_sha256=manifest['package_sha256'],
    retired_paths=removed, retained=['offline recognition', 'Duck-prefix command checks',
    'synthetic voice fixtures', 'procurement and purchase records', 'Vosk model'],
    physical_hardware_validated=False, paid_api_calls=0,
    evidence=['xgo-integration.json', 'xgo-browser-check.json', 'xgo-arm64-check.json', 'talking-xgo-0.2.0.manifest.json'],
    limitations=['No deployed XGO sit/stand policy', 'No physical USB audio validation',
                 'MCU interface emulated, STM32 firmware not executed', 'No conversation or person following'])
(ROOT/'artifacts/migration.json').write_text(json.dumps(record, indent=2), encoding='utf8')
print('Recorded XGO migration; retained purchase history and retired old robot comparison.')
