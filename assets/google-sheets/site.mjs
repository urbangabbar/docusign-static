import {transferCharge} from './pricing.mjs';
import {renderReport} from './report-renderer.mjs';
function event(name,fields={}){window.LCBridgeAnalytics?.recordSheetsEvent?.(name,fields);}
const search=document.querySelector('#template-search'),category=document.querySelector('#template-category');
if(search&&category){const cards=[...document.querySelectorAll('[data-template-card]')],counter=document.querySelector('#template-count');const filter=()=>{let count=0;const q=search.value.trim().toLowerCase();for(const card of cards){const visible=(!q||card.textContent.toLowerCase().includes(q))&&(category.value==='All'||card.dataset.category===category.value);card.hidden=!visible;if(visible)count++;}counter.textContent=`${count} of ${cards.length} sample reports`;document.querySelector('#template-empty').hidden=count!==0;};search.addEventListener('input',filter);category.addEventListener('change',filter);}
const configNode=document.querySelector('#report-config');
if(configNode){
 const config=JSON.parse(configNode.textContent),controls={...config.controls},content=document.querySelector('#report-content'),status=document.querySelector('#report-status');
 const inputs=[...document.querySelectorAll('[data-report-control]')];let modules;
 async function render(){
  try{modules??=Promise.all([import('./demo/engine.js'),import('./demo/fixtures.js')]);const [{computeDashboard},{createFixtures}]=await modules;for(const input of inputs)controls[input.dataset.reportControl]=input.value;const result=computeDashboard(config.id,createFixtures(),config.settings,controls);content.innerHTML=renderReport(result,config.settings.currency);status.textContent=`Sample updated · ${controls.owner} · ${controls.period} · Frozen October 2026 data`;event('template_filter_changed',{template_id:config.id});}
  catch{status.textContent='The interactive preview could not update. Your original sample remains below. Reload to try again.';}
 }
 for(const input of inputs)input.addEventListener('change',render);
 event('template_preview_opened',{template_id:config.id});
}
const calculator=document.querySelector('#transfer-calculator');
if(calculator){const config=JSON.parse(document.querySelector('#pricing-config').textContent),records=calculator.querySelector('#records-per-run'),runs=calculator.querySelector('#runs-per-month'),result=calculator.querySelector('#calculator-result'),error=calculator.querySelector('#calculator-error');
 calculator.addEventListener('submit',e=>{e.preventDefault();error.textContent='';
  try{const a=Number(records.value),b=Number(runs.value);if(records.value===''||runs.value===''||![a,b].every(x=>Number.isSafeInteger(x)&&x>=0)||!Number.isSafeInteger(a*b)||a*b>1e10)throw Error('Use whole numbers between zero and a total of 10 billion transfers.');
   const quote=transferCharge(a*b,config),fmt=n=>new Intl.NumberFormat('en-US',{maximumFractionDigits:2}).format(n);result.innerHTML=`<span>Estimated monthly base usage</span><strong>$${(quote.cents/100).toFixed(2)} USD</strong><p>${fmt(quote.transfers)} record transfers · ${fmt(quote.included)} included · ${fmt(quote.billable)} billable</p><div class="table-scroll"><table><caption>Graduated transfer estimate</caption><thead><tr><th>Transfers in band</th><th>Rate per transfer</th><th>Band amount</th></tr></thead><tbody>${quote.breakdown.filter(b=>b.count).map(b=>`<tr><td>${fmt(b.count)}</td><td>$${b.rate}</td><td>$${(b.micro/1e6).toFixed(4)}</td></tr>`).join('')||'<tr><td colspan="3">All transfers in this estimate are covered by the monthly allowance.</td></tr>'}</tbody></table></div><p class="small">Estimate only. Bands apply progressively per connected account per calendar month (UTC). Applicable markup and tax can change the final charge. Repeat executions create additional usage.</p>`;result.hidden=false;event('pricing_calculator_used');
  }catch(ex){result.hidden=true;error.textContent=ex.message;}
 });
}
const filmButton=document.querySelector('[data-film-play]');
if(filmButton){const film=document.getElementById(filmButton.getAttribute('aria-controls'));filmButton.addEventListener('click',()=>film.play());film.addEventListener('play',()=>{filmButton.hidden=true;event('product_film_played');},{once:true});}
const frame=document.querySelector('#sheets-waitlist, iframe.hl-form');
if(frame){let started=false;frame.addEventListener('focus',()=>{if(!started){started=true;event('early_access_form_started');}});}
// A frame load/click is never reported as an accepted request. Provider-confirmed
// completion must be wired by its actual trusted success flow, not inferred here.
