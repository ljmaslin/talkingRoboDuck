"""Auditable research data and standalone budget calculator; no purchases."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
items = []

def add(key, phase, name, supplier, sku, qty, price, url, evidence, notes='', selected=True):
    items.append(dict(id=key, phase=phase, product=name, supplier=supplier, sku=sku,
                      quantity=qty, unit_gbp=price, source=url, evidence=evidence,
                      notes=notes, selected=selected))

P = 'https://thepihut.com/products/'
add('printer', 'Core', 'Bambu Lab A1 (printer only)', 'Additive-X', 'BAMA1-U1', 1, 189,
    'https://www.additive-x.com/shop/bambu-lab-a1-3d-printer.html', 'Listed incl VAT; in stock; next-working-day option', 'User selected full A1. SO50 postage is unquoted; editable allowance below. A1 mini alternative is GBP139, saving GBP50.')
add('controller', 'Core', 'Arduino UNO Q 4GB / 32GB', 'CPC', 'ABX00173 / SC21880', 1, 54.42,
    'https://cpc.farnell.com/arduino/abx00173/arduino-uno-q-4gb/dp/SC21880', 'Listed incl VAT; 12 in stock at reviewed page', 'Free mainland standard shipping threshold is met by this line alone.')
add('white', 'Core', 'eSUN PLA+ White 1.75mm 1kg, spool', '3DJake', 'PLA+175W1P1', 1, 17.45,
    'https://www.3djake.uk/esun/pla-white-8', 'Listed incl VAT; in stock', 'Candidate material for fit tests, not an upstream-certified profile.')
add('yellow', 'Core', 'eSUN PLA+ Yellow 1.75mm 1kg, spool', '3DJake', 'Select 1kg spool', 1, 17.45,
    'https://www.3djake.uk/esun/pla-yellow-7', 'Listed incl VAT; in stock on indexed page', 'Optional colour: make rigid parts white to save this purchase.', False)
add('tpu', 'Core', 'eSUN TPU-95A Translucent Yellow 1.75mm 1kg', '3DJake', 'TPU-95A175T-Y1P1', 1, 27.50,
    'https://www.3djake.uk/esun/tpu-95a-translucent-yellow', 'Listed incl VAT; indexed in stock; delivery date stale', 'Upstream does not specify TPU hardness; confirm 95A suitability before purchase.')
add('dryer', 'Core', 'SUNLU Fila Dryer S2', '3DJake', 'Fila Dryer S2', 1, 58.63,
    'https://www.3djake.uk/sunlu/fila-dryer-s2', 'Listed incl VAT; in stock; displayed delivery 5 November', 'These selected 3DJake goods exceed GBP69.90: standard postage GBP0. No printer bought here, so no bulky-printer surcharge.')
add('meter', 'Core', 'Duratool digital multimeter', 'CPC', 'D03143A / IN10151', 1, 7.14,
    'https://cpc.farnell.com/duratool/d03143a/digital-multimeter/dp/IN10151', 'GBP5.95 ex VAT converted to GBP7.14; indexed in stock', 'Use for low-voltage robot continuity/polarity checks. Requires separate PP3 battery, now itemised.')
add('pp3', 'Core', 'Ansmann X-Power 9V PP3 battery for meter', 'The Pi Hut', '104896', 1, 4.50,
    P+'x-power-9v-6lr61-alkaline-battery', 'Live public variant: purchasable; incl VAT', 'For multimeter, not robot power. Replaces part of the previous GBP15 consumables allowance.')
add('ties', 'Core', '100mm black cable ties, pack', 'The Pi Hut', '103060', 1, 1.50,
    P+'100mm-black-cable-ties', 'Live public variant: purchasable; incl VAT', 'Replaces part of previous consumables allowance. Keep cables clear of moving joints.')
add('caliper', 'Core', '150mm composite digital calipers', 'The Pi Hut', '105194', 1, 9.50,
    P+'150mm-composite-electronic-digital-calipers', 'Live public variant: purchasable; incl VAT', 'Includes case, excludes LR44. Stated accuracy 0.1mm; suitable for coarse fit checks.')
add('lr44', 'Core', 'Ansmann LR44 battery', 'The Pi Hut', '105478', 1, 1.90,
    P+'lr44-1-5v-alkaline-coin-cell-battery', 'Live public variant: purchasable; incl VAT')
add('cable', 'Core', 'Arduino USB-C data cable', 'The Pi Hut', 'TPX00243', 1, 5.10,
    P+'arduino-usb-c-cable', 'Live public variant: purchasable; incl VAT', 'Remove if an existing USB data cable is suitable.')
add('psu', 'Core', 'Arduino 45W USB-C power supply, UK plug option', 'The Pi Hut', 'TPX00242', 1, 14.40,
    P+'arduino-usb-c-power-supply-45w', 'Live public variant: purchasable; incl VAT', 'For standalone UNO/bench use, not a servo supply or robot battery charger. Confirm compatible existing PSU before buying.')
add('station', 'Learning', 'Duratool 48W digital temperature-controlled station', 'CPC', 'D03327 / SD01120', 1, 57.30,
    'https://cpc.farnell.com/duratool/zd-931-89-3106/soldering-station-esd-bs-plug/dp/SD01120', 'GBP47.75 ex VAT converted to GBP57.30; 30 indexed in stock', 'UK plug, integral enclosed stand and sponge. No separate iron PSU/stand required.')
add('solder', 'Learning', 'Antex lead-free solder, 4m tube', 'The Pi Hut', '100327', 1, 4.40,
    P+'antex-lead-free-solder', 'Listed incl VAT; indexed in stock')
add('mat', 'Learning', 'Magnetic silicone soldering mat', 'The Pi Hut', '104755', 1, 11,
    P+'magnetic-silicone-soldering-mat', 'Listed incl VAT; indexed in stock')
add('glasses', 'Learning', 'iFixit basic safety glasses', 'The Pi Hut', 'IF145-556-1', 2, 4,
    P+'ifixit-safety-glasses-basic', 'Listed incl VAT; 14 indexed available', 'Two pairs: parent and son.')
add('practice', 'Learning', 'Blinky Light learn-to-solder kit, red', 'The Pi Hut', 'KIT-011-RED', 2, 4.50,
    P+'blinky-light-kit-learn-to-solder', 'Live public red variant: purchasable; incl VAT', 'One each. Requires two AA cells per kit.')
add('aa', 'Learning', 'Ansmann AA alkaline batteries, 2-pack', 'The Pi Hut', '104894', 2, 2.50,
    P+'x-power-1-5v-aa-alkaline-batteries-2-pack', 'Listed incl VAT; indexed in stock', 'Four cells total for the two practice kits, not robot power.')
add('audio', 'Audio', 'ReSpeaker Lite with pre-soldered XIAO ESP32S3', 'The Pi Hut', '106055 / 110061601', 1, 28.80,
    P+'respeaker-lite-with-xiao-esp32s3', 'Live public variant: purchasable; incl VAT', 'Candidate USB audio route: flash XMOS USB firmware, use XMOS port. Integration with UNO and final mounting remains untested.')
add('speaker', 'Audio', 'Seeed enclosed speaker for ReSpeaker Lite, 4 ohm 5W', 'The Pi Hut', '106075 / 114993346', 1, 2.40,
    P+'mono-enclosed-speaker-4r-5w', 'Live public variant: purchasable; incl VAT', '50x45x22mm; verify connector and fit. Five watts is its rating, not a measured running load.')
add('hub', 'Audio', 'Arduino USB-C hub, 8-in-1', 'The Pi Hut', 'TPX00241', 1, 14.40,
    P+'arduino-usb-c-hub-8-in-1', 'Live public variant: purchasable; incl VAT', 'Bench solution, 60g. Requires external USB-C PD per supplier; not a proven battery-mobile installation.')
add('audio-cable', 'Audio', 'Second Arduino USB data cable', 'The Pi Hut', 'TPX00243', 1, 5.10,
    P+'arduino-usb-c-cable', 'Live public variant: purchasable; incl VAT', 'Check host/device connector ends; remove if already owned.')
add('bits', 'Optional', 'iFixit Minnow precision bits', 'The Pi Hut', 'EU145474-1', 1, 14,
    P+'ifixit-minnow-precision-bit-set', 'Live public variant: purchasable; incl VAT', 'Only if existing drivers do not match supplied screw heads; not all hex sizes included.', False)
add('deburr', 'Optional', 'Deburring tool and 10 blades', 'The Pi Hut', '105012', 1, 7.90,
    P+'3d-print-deburring-tool-10x-blades', 'Live public variant: purchasable; incl VAT', 'Existing hand tools may cover this; do not enlarge precision bearing fits indiscriminately.', False)
add('ts101', 'Alternative', 'Miniware TS101 iron', 'The Pi Hut', '105410', 1, 57.50,
    P+'miniware-ts101-smart-soldering-iron', 'Listed incl VAT; indexed in stock', 'Alternative to station, not additional. USB-C cable and B2 tip included; needs PD PSU and a compatible stand.', False)
add('antex', 'Alternative', 'Antex XS25 engineers toolkit', 'The Pi Hut', '103534', 1, 69.90,
    P+'antex-xs25-engineers-toolkit-kc8jsz0', 'Live public variant: purchasable; incl VAT', 'Includes meter/hand tools/solder/stand; fixed-power iron. Duplicates existing tools and is not our selected upgrade.', False)

for item in items:
    if item['phase'] in ('Learning', 'Audio'):
        item['selected'] = False

data = dict(checked='2026-10-27', destination='SO50, mainland Great Britain; no complete delivery address used',
            upstream_commit='106186e1beda690c28f485a754538d6f41b5d025', items=items,
            purchase=dict(item='XGO electronics kit including shipping', paid_gbp=306.46,
                          quoted_total_usd=392, reported_date='2026-10-27',
                          source='User-reported card charge; no receipt/order ID supplied'),
            assumptions=dict(usd_to_gbp=306.46/392, kit_usd=352, kit_regular_usd=400,
                             import_shipping_gbp=40*306.46/392, import_vat=0.20, import_duty_rate=0,
                             import_handling_gbp=12, printer_shipping_gbp=15,
                             pihut_shipping_gbp=6, other_consumables_gbp=9, contingency_gbp=75),
            unresolved=['Kit and shipping have been purchased: user reports GBP306.46 charged against USD392. Exchange-rate input reproduces that actual payment, not a current FX quote.',
                        'Kit baseline uses USD352 plus USD40 shipping from the prior checkout figure. No invoice has been independently inspected.',
                        'User confirms UK VAT is excluded. Import VAT uses the effective card rate for budgeting; customs conversion can differ. Arrival remains unconfirmed.',
                        'Import duty rate 0 is an unset placeholder, not a tariff determination.',
                        'Additive-X and Pi Hut shipping inputs are allowances, not SO50 checkout quotes.',
                        'All chosen audio components are candidates, not an engineered untethered audio installation.'])
(ROOT/'costs.json').write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')

def calculate(selected=None):
    selected = [i for i in items if i['selected']] if selected is None else selected
    a = data['assumptions']
    goods = sum(i['quantity']*i['unit_gbp'] for i in selected)
    kit = a['kit_usd']*a['usd_to_gbp']
    duty = (kit+a['import_shipping_gbp'])*a['import_duty_rate']
    vat = (kit+a['import_shipping_gbp']+duty)*a['import_vat']
    total = goods+kit+a['import_shipping_gbp']+duty+vat+a['import_handling_gbp']+a['printer_shipping_gbp']+a['pihut_shipping_gbp']+a['other_consumables_gbp']
    return dict(uk_priced_goods=round(goods,2), import_kit=round(kit,2), import_vat=round(vat,2),
                paid_gbp=data['purchase']['paid_gbp'],
                remaining_budget_with_contingency=round(total+a['contingency_gbp']-data['purchase']['paid_gbp'],2),
                total_before_contingency=round(total,2), total_with_contingency=round(total+a['contingency_gbp'],2))

totals=calculate()
(ROOT/'budget-summary.json').write_text(json.dumps(totals,indent=2)+'\n',encoding='utf-8')
print(json.dumps(totals,indent=2))

rows='\n'.join(f"| {'Yes' if i['selected'] else 'No'} | {i['phase']} | [{i['product']}]({i['source']}) | {i['sku']} | {i['quantity']} | £{i['unit_gbp']:.2f} | £{i['quantity']*i['unit_gbp']:.2f} | {i['evidence']} |" for i in items)
(ROOT/'priced-listings.md').write_text('# Priced listings — 27 October 2026\n\nAll prices in this table are GBP including VAT. Postage is separate. Availability is seller-reported; a purchasable variant does not certify physical stock. Alternatives and optional rows are not in the selected total. SO50 destination.\n\n| Selected | Phase | Product and listing | SKU | Qty | Each inc VAT | Line | Evidence |\n|---|---|---|---|---:|---:|---:|---|\n'+rows+'\n\nThe imported robot kit and unquoted charges are in `build-plan.md`; they are not hidden inside these listed prices.\n',encoding='utf-8')

json_script=json.dumps(data, ensure_ascii=True).replace('</','<\\/')
template='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Duck build budget — SO50</title>
<style>body{font:16px/1.5 system-ui,sans-serif;color:#172b35;background:#f5f7f8;margin:0}main{max-width:1150px;margin:auto;padding:28px}h1{font-size:32px}h2{margin-top:32px}a{color:#076b75}section,.card{background:white;padding:20px;border-radius:12px;margin:16px 0}.notice{border-left:5px solid #bf7b13;background:#fff4df}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.big{font-size:32px;font-weight:700}label{display:block;margin:12px 0}input[type=number],select{display:block;width:170px;padding:8px;border:1px solid #8798a0;border-radius:5px;font:inherit}input[type=checkbox]{width:20px;height:20px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:12px;border-bottom:1px solid #dde4e8;vertical-align:top}.scroll{overflow:auto}small{display:block;color:#536872}.money{text-align:right;white-space:nowrap}button{padding:8px 14px;font:inherit;cursor:pointer}.status{color:#9a5700}footer{margin:30px 0}</style>
<main><h1>A robot duck you build together</h1><p>SO50 · checked 27 October 2026 · £800–£1,000 target</p>
<section class="notice"><strong>Budget model, not a checkout quote.</strong> UK goods use linked GBP listings. Luwu's kit is sold in USD; its freight, battery transport, duty and delivery date remain unconfirmed. Orange inputs are allowances. No purchases, supplier messages or AI requests have been made.</section>
<div class="grid"><section><small>Selected UK-priced goods, VAT included</small><div class="big" id="goods"></div></section><section><small>Estimated total before reserve</small><div class="big" id="total"></div></section><section><small>Including chosen reserve</small><div class="big" id="reserved"></div><small id="budget"></small></section></div>
<section><h2>Choose the build</h2><label>Printer<select id="printer"><option value="189">A1 — £189 listed</option><option value="139">A1 mini — £139 listed</option></select></label><p>Every individual audited STL fits a 180 mm cube; largest dimension 124.1 mm. This establishes size clearance, not a validated print profile.</p><div class="scroll"><table><thead><tr><th>Include</th><th>Phase / product</th><th>Quantity</th><th>Unit GBP</th><th>Line GBP</th></tr></thead><tbody id="items"></tbody></table></div></section>
<section><h2>Imported robot kit and allowances</h2><p>The kit already contains the 15 servos, expansion board, battery, charger, cables, bearings and screws. Do not add those parts a second time.</p><div class="grid" id="inputs"></div><p id="import"></p><p class="status">Duty defaults to zero because classification is unresolved. Enter a confirmed rate before treating this as a landed quote. VAT is calculated once on goods + freight + duty, assuming seller has not collected UK VAT.</p><p>3DJake standard delivery: £0 above £69.90; £8.90 otherwise. Selecting a printer bought elsewhere avoids their £30 bulky-printer surcharge. This model updates the standard threshold for selected 3DJake goods.</p></section>
<section><h2>What these choices prove</h2><p>The assembled electronics kit still leaves printing, servo configuration, wiring, assembly and calibration to you. The ReSpeaker/hub option is a bench audio experiment: final battery power, mounting and walking balance remain engineering work.</p><p>Use the full <a href="build-plan.md">build plan</a> for PCB manufacturing, sourcing alternatives, delivery gaps and the staged family build.</p><button id="reset">Reset selections and estimates</button></section><footer>No account, telemetry, cookies or network requests. Changes last until reload. Prices and stock can change.</footer></main>
<script id="data" type="application/json">__DATA__</script><script>
const plan=JSON.parse(document.getElementById('data').textContent), money=n=>new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP'}).format(n);
const fields=[['kit_usd','Kit price (USD; sale 352 unverified)'],['usd_to_gbp','GBP per USD (estimate)'],['import_shipping_gbp','Luwu freight GBP (unquoted)'],['import_vat','Import VAT fraction'],['import_duty_rate','Duty fraction (unset, not confirmed zero)'],['import_handling_gbp','Courier handling GBP (allowance)'],['printer_shipping_gbp','Printer shipping GBP (allowance)'],['pihut_shipping_gbp','Pi Hut shipping GBP (allowance)'],['other_consumables_gbp','Adhesive / ties / labels GBP (allowance)'],['contingency_gbp','Reserve GBP']];
for(const [key,label] of fields){const box=document.createElement('label');box.className='status';box.textContent=label;const input=document.createElement('input');input.type='number';input.min='0';input.step=key.includes('rate')||key==='usd_to_gbp'||key==='import_vat'?'0.001':'0.01';input.value=plan.assumptions[key];input.id=key;box.append(input);document.getElementById('inputs').append(box);input.oninput=update;}
for(const item of plan.items){if(item.id==='printer')continue;const tr=document.createElement('tr');const select=document.createElement('input');select.type='checkbox';select.checked=item.selected;select.id='sel-'+item.id;select.setAttribute('aria-label','Include '+item.product);select.onchange=update;const td=document.createElement('td');td.append(select);tr.append(td);const name=document.createElement('td');const a=document.createElement('a');a.href=item.source;a.target='_blank';a.rel='noopener';a.textContent=item.product;name.append(a);for(const text of [item.phase+' · '+item.supplier+' · '+item.sku,item.evidence,item.notes]){const small=document.createElement('small');small.textContent=text;name.append(small);}tr.append(name);for(const [prefix,value,step] of [['qty-',item.quantity,'1'],['unit-',item.unit_gbp,'0.01']]){const cell=document.createElement('td'),input=document.createElement('input');input.type='number';input.min='0';input.step=step;input.value=value;input.id=prefix+item.id;input.style.width='85px';input.setAttribute('aria-label',prefix+item.product);input.oninput=update;cell.append(input);tr.append(cell);}const line=document.createElement('td');line.className='money';line.id='line-'+item.id;tr.append(line);document.getElementById('items').append(tr);}
function number(id){return Math.max(0,Number(document.getElementById(id).value)||0);}
function compute(s){const kit=s.kit_usd*s.usd_to_gbp, duty=(kit+s.import_shipping_gbp)*s.import_duty_rate, vat=(kit+s.import_shipping_gbp+duty)*s.import_vat, shopShipping=s.jakeGoods>0&&s.jakeGoods<69.9?8.9:0;const total=s.goods+kit+s.import_shipping_gbp+duty+vat+s.import_handling_gbp+s.printer_shipping_gbp+s.pihut_shipping_gbp+s.other_consumables_gbp+shopShipping;return {kit,duty,vat,shopShipping,total,reserved:total+s.contingency_gbp};}
function update(){let goods=number('printer'),jakeGoods=0;for(const item of plan.items){if(item.id==='printer')continue;const line=number('qty-'+item.id)*number('unit-'+item.id);document.getElementById('line-'+item.id).textContent=money(line);if(document.getElementById('sel-'+item.id).checked){goods+=line;if(item.supplier==='3DJake')jakeGoods+=line;}}const state={goods,jakeGoods};for(const [key] of fields)state[key]=number(key);const out=compute(state);document.getElementById('goods').textContent=money(goods);document.getElementById('total').textContent=money(out.total);document.getElementById('reserved').textContent=money(out.reserved);document.getElementById('budget').textContent=out.reserved>1000?money(out.reserved-1000)+' above £1,000 target':money(1000-out.reserved)+' below £1,000 target';document.getElementById('import').textContent='Kit converted: '+money(out.kit)+' · duty placeholder: '+money(out.duty)+' · import VAT estimate: '+money(out.vat)+' · 3DJake standard shipping: '+money(out.shopShipping);}
document.getElementById('printer').onchange=update;document.getElementById('reset').onclick=()=>location.reload();update();
</script></html>'''
template = template.replace('Kit price (USD; sale 352 unverified)', 'Kit price (USD; advertised 352, confirm checkout)')
template = template.replace('Luwu freight GBP (unquoted)', 'Luwu freight GBP (USD40 converted at actual effective card rate)')
template = template.replace('GBP per USD (estimate)', 'GBP per USD (effective rate of reported card payment)')
template = template.replace('its freight, battery transport, duty and delivery date remain unconfirmed', 'the kit plus freight has been purchased for £306.46; UK VAT is excluded, duty and arrival remain unconfirmed')
template = template.replace('No purchases, supplier messages or AI requests have been made.', 'Kit purchase reported by user: £306.46 including shipping. All other goods remain planned. No supplier messages or paid AI requests made by this research tool.')
template = template.replace('Adhesive / ties / labels GBP (allowance)', 'Remaining glue / labels GBP (allowance; ties and meter battery itemised)')
template = template.replace('Use the full <a href="build-plan.md">build plan</a>', 'Use the current <a href="order-list.md">order list</a> and original <a href="build-plan.md">build plan</a>')
(ROOT/'cost-calculator.html').write_text(template.replace('__DATA__',json_script),encoding='utf-8')
