"""Save public Shopify variant prices/stock; no cart, account or checkout calls."""
import concurrent.futures
import json
import urllib.request
from pathlib import Path

targets = {
    'uno-q': 'https://thepihut.com/products/arduino-uno-q.js',
    'xgo-kit': 'https://shop.xgorobot.com/products/xgo-duck-biped-robot-electronics-kit-arduino-uno-q.js',
    'xgo-board': 'https://shop.xgorobot.com/products/robot-driver-board.js',
    'openelab-servo': 'https://openelab.com/products/feetech-hd1910-microduck-coreless-servo.js',
    'bambu-a1': 'https://uk.store.bambulab.com/products/a1.js',
    'bambu-mini': 'https://uk.store.bambulab.com/products/a1-mini.js',
    'antex-kit': 'https://thepihut.com/products/antex-xs25-engineers-toolkit-kc8jsz0.js',
    'minnow-bits': 'https://thepihut.com/products/ifixit-minnow-precision-bit-set.js',
    'calipers': 'https://thepihut.com/products/150mm-composite-electronic-digital-calipers.js',
    'lr44': 'https://thepihut.com/products/lr44-1-5v-alkaline-coin-cell-battery.js',
    'respeaker': 'https://thepihut.com/products/respeaker-lite-with-xiao-esp32s3.js',
    'respeaker-speaker': 'https://thepihut.com/products/mono-enclosed-speaker-4r-5w.js',
    'usb-hub': 'https://thepihut.com/products/arduino-usb-c-hub-8-in-1.js',
    'usb-psu': 'https://thepihut.com/products/arduino-usb-c-power-supply-45w.js',
    'usb-cable': 'https://thepihut.com/products/arduino-usb-c-cable.js',
    'deburring': 'https://thepihut.com/products/3d-print-deburring-tool-10x-blades.js',
    'practice-kit': 'https://thepihut.com/products/blinky-light-kit-learn-to-solder.js',
    'sunlu-s2': 'https://uk.store.sunlu.com/products/new-version-sunlu-filadryer-s2.js',
}

def fetch(item):
    label, url = item
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=35) as response:
            data = json.load(response)
        return label, dict(url=url, title=data.get('title'), variants=[
            {key: v.get(key) for key in ('id', 'title', 'price', 'available', 'sku')}
            for v in data.get('variants', [])])
    except Exception as error:
        return label, dict(url=url, error=str(error))

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = dict(pool.map(fetch, targets.items()))
    out = Path(__file__).resolve().parent / 'procurement' / 'public-product-variants.json'
    out.write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    for name, result in results.items():
        variants = result.get('variants', [])
        print(json.dumps(dict(name=name, error=result.get('error'), variants=variants[:5]), ensure_ascii=True))
