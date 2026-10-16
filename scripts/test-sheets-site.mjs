import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {transferCharge,addDelivery,accountTransfers} from '../assets/google-sheets/pricing.mjs';
import {renderReport,value} from '../assets/google-sheets/report-renderer.mjs';
import {computeDashboard} from '../assets/google-sheets/demo/engine.js';
import {createFixtures} from '../assets/google-sheets/demo/fixtures.js';
const root=fileURLToPath(new URL('../',import.meta.url));
const read=p=>JSON.parse(fs.readFileSync(root+p,'utf8'));
const p=read('data/product-facts.json')['google-sheets'].pricing;
const reports=read('data/google-sheets-reports.json');
test('Allowance, graduated tier edges, and exact accumulation',()=>{
 const cases=[[0,0],[250,0],[251,15000],[1249,14985000],[1250,15000000],[1251,15012000],[2249,26988000],[2250,27000000],[2251,27009000],[5249,53991000],[5250,54000000],[5251,54007500],[30249,241492500],[30250,241500000],[30251,241504500]];
 for(const [count,micro] of cases){const q=transferCharge(count,p);assert.equal(q.micro,micro,`usage ${count}`);assert.equal(q.breakdown.reduce((n,b)=>n+b.micro,0),micro);assert.equal(q.breakdown.reduce((n,b)=>n+b.count,0),Math.max(0,count-250));}
 assert.equal(transferCharge(251,p).cents,2);assert.equal(transferCharge(252,p).cents,3);
 assert.throws(()=>transferCharge(-1,p),RangeError);assert.throws(()=>transferCharge(1.2,p),RangeError);
});
test('New executions count again, retry receipts deduplicate, account/month scopes remain separate',()=>{
 let ledger={};const delivery={account:'a',month:'2026-10',execution:'run-1',primaryTransfers:100};
 ledger=addDelivery(ledger,delivery);ledger=addDelivery(ledger,delivery);assert.equal(accountTransfers(ledger,'a','2026-10'),100);
 ledger=addDelivery(ledger,{...delivery,execution:'run-2'});ledger=addDelivery(ledger,{...delivery,execution:'run-3'});
 assert.equal(accountTransfers(ledger,'a','2026-10'),300);assert.equal(transferCharge(300,p).micro,750000);
 ledger=addDelivery(ledger,{...delivery,account:'b'});ledger=addDelivery(ledger,{...delivery,month:'2026-11'});
 assert.equal(accountTransfers(ledger,'a','2026-10'),300);assert.equal(accountTransfers(ledger,'b','2026-10'),100);assert.equal(accountTransfers(ledger,'a','2026-11'),100);
});
test('Single public pricing definition feeds calculator and Markdown',()=>{
 assert.deepEqual(read('assets/google-sheets/pricing.json'),p);
 const md=fs.readFileSync(root+'google-sheets-integration/pricing.md','utf8');
 for(const band of p.bands)assert.ok(md.includes(String(band.rateMicrousd/1e6)));
 assert.match(md,/each execution/i);assert.match(md,/250/);
});
test('25 reports retain imported calculations and layout; all available filter combinations render',()=>{
 assert.equal(reports.length,25);assert.ok(!reports.some(r=>/workflow/i.test(r.name)));
 const rendered=read('data/google-sheets-rendered.json');
 let views=0;
 for(const r of reports){
  const base=computeDashboard(r.id,createFixtures(),r.settings,r.controls);
  assert.deepEqual(JSON.parse(JSON.stringify(base)),r.result,`${r.id} imported result`);
  assert.equal(renderReport(base,r.settings.currency),rendered[r.id]);
  assert.equal((rendered[r.id].match(/class="report-chart"/g)||[]).length,base.charts.length);
  assert.ok(!/data-action|javascript:|href=|onclick|<button/.test(rendered[r.id]),'No live actions or record navigation');
  for(const period of ['This month','Last month','Last 90 days'])for(const owner of ['Everyone','Alex Morgan','Jamie Chen','Sam Rivera']){
   const result=computeDashboard(r.id,createFixtures(),r.settings,{...r.controls,period,owner});
   const html=renderReport(result,r.settings.currency);assert.ok(!/NaN|Infinity|undefined/.test(html),`${r.id} ${period} ${owner}`);views++;
  }
 }
 assert.equal(views,300);
});
test('Selected business invariants do not conflate sales/cash/history',()=>{
 const get=id=>reports.find(r=>r.id===id).result;
 assert.equal(get('pipeline').metrics[0].value,9);assert.equal(get('pipeline').metrics[1].value,22050);
 assert.equal(get('receivables').charts.length,0,'Aging remains a register layout');
 assert.equal(get('receivables').metrics[0].value,1400);
 assert.equal(get('forecast').metrics.find(m=>m.label==='Forecast-versus-actual error').value,null);
 assert.equal(value(null),'Not enough data');assert.equal(value(0),'0');
 assert.equal(get('team').charts.length,4,'Team retains its 2 by 2 chart arrangement');
 assert.equal(get('subscriptions').metrics.find(m=>m.label==='Normalized active MRR').value,300);
 assert.equal(get('orders').metrics[0].value,2800);
});
