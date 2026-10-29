"""Read public product pages/variants only; never cart or checkout endpoints."""
import concurrent.futures
import json
import re
import urllib.request
from pathlib import Path

urls = {
    'mini': 'https://www.additive-x.com/shop/bambu-lab-a1-mini-3d-printer.html',
    'a1': 'https://www.additive-x.com/shop/bambu-lab-a1-3d-printer.html',
    'dryer': 'https://www.3djake.uk/sunlu/fila-dryer-s2',
    'battery': 'https://thepihut.com/products/x-power-9v-6lr61-alkaline-battery.js',
    'ties': 'https://thepihut.com/products/100mm-black-cable-ties.js',
    'psu': 'https://thepihut.com/products/arduino-usb-c-power-supply-45w.js',
    'calipers': 'https://thepihut.com/products/150mm-composite-electronic-digital-calipers.js',
}

def fetch(item):
    name, url = item
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode('utf8')
        if url.endswith('.js'):
            data = json.loads(body)
            info = [{k: v.get(k) for k in ('title', 'price', 'available', 'sku')} for v in data['variants']]
        else:
            info = []
            for match in re.finditer(r'.{0,100}(?:"price"\s*:|data-price-amount=|priceCurrency|58\.63|59\.82|availability).{0,150}', body, re.I):
                snippet = match.group(0)
                if snippet not in info:
                    info.append(snippet)
            info = info[:18]
        return name, {'url': url, 'evidence': info}
    except Exception as exc:
        return name, {'url': url, 'error': str(exc)}

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    result = dict(pool.map(fetch, urls.items()))
Path(__file__).with_name('order-list-checks.json').write_text(json.dumps(result, indent=2), encoding='utf8')
print(json.dumps(result, indent=2))
