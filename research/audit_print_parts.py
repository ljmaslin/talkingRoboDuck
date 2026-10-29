"""Measure upstream STL bounds without installing or executing vendor code."""
import csv
import json
import re
import struct
from pathlib import Path

root = Path(__file__).resolve().parent
rows = []
for part in sorted((root / 'xgoduck_hardware' / 'structure').iterdir()):
    if part.suffix.lower() != '.stl':
        continue
    data = part.read_bytes()
    count = struct.unpack_from('<I', data, 80)[0] if len(data) >= 84 else 0
    if len(data) == 84 + count * 50:
        vertices = (struct.unpack_from('<3f', data, 84 + face * 50 + 12 + vertex * 12)
                    for face in range(count) for vertex in range(3))
    else:
        points = re.findall(rb'vertex\s+([-+\d.eE]+)\s+([-+\d.eE]+)\s+([-+\d.eE]+)', data)
        if not points:
            raise ValueError(f'Unrecognised STL: {part}')
        vertices = (tuple(float(v) for v in point) for point in points)
        count = len(points) // 3
    lows, highs = [float('inf')] * 3, [float('-inf')] * 3
    for vertex in vertices:
        for axis, value in enumerate(vertex):
            lows[axis] = min(lows[axis], value)
            highs[axis] = max(highs[axis], value)
    sizes = [round(hi - lo, 3) for hi, lo in zip(highs, lows)]
    copies = int(re.match(r'(\d+)x_', part.name).group(1)) if re.match(r'(\d+)x_', part.name) else 1
    rows.append(dict(file=part.name, copies=copies, x_mm=sizes[0], y_mm=sizes[1], z_mm=sizes[2],
                     triangles=count, material='TPU' if 'tpu' in part.name.lower() else 'confirm',
                     optional_rollers='tire' in part.name.lower(),
                     within_180_cube=all(v <= 180 for v in sizes)))
out = root / 'procurement'
out.mkdir(exist_ok=True)
(out / 'print-dimensions.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
with (out / 'print-dimensions.csv').open('w', newline='', encoding='utf-8-sig') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(json.dumps(dict(files=len(rows), copies=sum(r['copies'] for r in rows),
                     exceed_180=[r for r in rows if not r['within_180_cube']],
                     largest=sorted(rows, key=lambda r: max(r['x_mm'], r['y_mm'], r['z_mm']), reverse=True)[:5]), indent=2))
