"""One-time conversion of synthetic fixtures to the app's 16 kHz PCM boundary."""
from array import array
from pathlib import Path
import wave

folder = Path(__file__).resolve().parents[1]/'xgo-sim/fixtures'
for path in folder.glob('*.wav'):
    with wave.open(str(path), 'rb') as source:
        if source.getnchannels()!=1 or source.getsampwidth()!=2: raise ValueError(path)
        rate = source.getframerate()
        if rate==16000: continue
        samples = array('h', source.readframes(source.getnframes()))
    output = array('h')
    for i in range(int(len(samples)*16000/rate)):
        at = i*rate/16000
        lo = int(at); hi = min(lo+1, len(samples)-1)
        output.append(round(samples[lo]+(samples[hi]-samples[lo])*(at-lo)))
    with wave.open(str(path), 'wb') as target:
        target.setparams((1,2,16000,0,'NONE','not compressed'))
        target.writeframes(output.tobytes())
print('Synthetic fixtures are 16 kHz mono PCM.')
