import fs from 'node:fs';
import assert from 'node:assert/strict';

const root = new URL('./', import.meta.url);
const page = fs.readFileSync(new URL('cost-calculator.html', root), 'utf8');
const script = page.match(/<script>([\s\S]*?)<\/script>/)[1];
new Function(script); // Compile the complete UI script without executing DOM code.
const fn = script.slice(script.indexOf('function compute(s)'), script.indexOf('function update()'));
const compute = new Function(fn + ';return compute;')();
const plan = JSON.parse(fs.readFileSync(new URL('costs.json', root), 'utf8'));
const selected = plan.items.filter(x => x.selected);
const goods = selected.reduce((sum, x) => sum + x.quantity * x.unit_gbp, 0);
const jakeGoods = selected.filter(x => x.supplier === '3DJake').reduce((sum, x) => sum + x.quantity * x.unit_gbp, 0);
const state = {...plan.assumptions, goods, jakeGoods};
const near = (actual, expected) => assert.ok(Math.abs(actual - expected) < 0.00001, `${actual} != ${expected}`);
near(compute(state).kit + state.import_shipping_gbp, plan.purchase.paid_gbp);
near(compute(state).total, 800.792);
near(compute(state).reserved, 875.792);
near(compute({...state, goods: goods - 50}).total, 750.792);
near(compute({...state, kit_usd: 400}).total, 800.792 + 48 * state.usd_to_gbp * 1.2);
near(compute({...state, import_duty_rate: 0.04}).total, 815.50208);
near(compute({...state, jakeGoods: 40}).shopShipping, 8.9);
near(compute({...state, jakeGoods: 69.9}).shopShipping, 0);
near(compute({...state, goods: goods + 50.7}).total, 851.492);
assert.ok(!page.includes('\uFFFD'));
console.log('Calculator syntax, actual payment reconciliation and budget/import/shipping scenarios passed.');
