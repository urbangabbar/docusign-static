export const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function value(v,unit='count',currency='USD'){
 if(v===null||v===undefined||!Number.isFinite(v))return 'Not enough data';
 if(unit==='money')return new Intl.NumberFormat('en-US',{style:'currency',currency,maximumFractionDigits:2}).format(v);
 return new Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(v)+(unit==='percent'?'%':unit==='days'?' days':unit==='minutes'?' min':'');
}
const palette=['#106F43','#235EA8','#8C5200','#7255A2','#497E77','#64748B'];
const short=s=>s.length>21?s.slice(0,20)+'…':s;
function chart(c,currency){
 const groups=c.groups||[],all=groups.flatMap(g=>[g.value,g.target,...(g.segments||g.series||[]).map(s=>s.value)]).concat(c.comparison||[],(c.multiSeries||[]).flatMap(s=>s.values||[])).filter(Number.isFinite);
 if(c.type==='waterfall'){let running=0;for(const g of groups){running=g.total?g.value:running+(g.value||0);all.push(running);}}
 const max=c.unit==='percent'?Math.max(100,...all):Math.max(1,...all.map(Math.abs)),w=600,h=260,left=55,right=18,top=22,bottom=52,iw=w-left-right,ih=h-top-bottom;
 const xx=i=>left+(groups.length<=1?iw/2:i*iw/(groups.length-1)),yy=v=>top+ih-(v/max)*ih;
 let shapes='',legend=[];
 const label=(x,y,s,anchor='middle')=>`<text x="${x}" y="${y}" text-anchor="${anchor}" fill="#586A60" font-size="11">${esc(s)}</text>`;
 const title=t=>`<title>${esc(t)}</title>`;
 if(c.type==='bars'||c.type==='target'){
  const row=Math.max(32,220/Math.max(1,groups.length)),height=groups.length*row+18;
  const bars=groups.map((g,i)=>{const v=g.value;return `${label(0,i*row+12,short(g.label),'start')}<rect x="190" y="${i*row}" width="${Math.max(0,Number.isFinite(v)?v/max*275:0)}" height="17" rx="2" fill="${palette[0]}">${title(g.label+': '+value(v,c.unit,currency))}</rect>${Number.isFinite(g.target)?`<line x1="${190+g.target/max*275}" x2="${190+g.target/max*275}" y1="${i*row-2}" y2="${i*row+20}" stroke="#235EA8" stroke-width="3"/>`:''}${label(590,i*row+13,value(v,c.unit,currency),'end')}`;}).join('');
   return `<svg class="chart-svg bars" viewBox="0 0 600 ${Math.max(height,95)}" role="img" aria-label="${esc(c.title)}">${title(c.title)}${bars}</svg>${c.type==='target'?`<p class="chart-note">Bar: median · Blue marker: ${esc(c.markerLabel||'target')}</p>`:''}`;
 }
 for(let i=0;i<4;i++){const v=max*i/3,y=yy(v);shapes+=`<line x1="${left}" x2="${w-right}" y1="${y}" y2="${y}" stroke="#E1EAE5"/>${label(left-8,y+4,value(v,c.unit,currency),'end')}`;}
 if(c.type==='line'){
  const series=c.multiSeries?.length?c.multiSeries.map(s=>({label:s.label,values:s.values})): [{label:'Actual',values:groups.map(g=>g.value)}];
  if(c.comparison?.length)series.push({label:c.comparisonLabel||'Previous period',values:c.comparison});
  for(const [sidx,s] of series.entries()){
   const color=palette[sidx%palette.length];legend.push(`<span><i style="background:${color}"></i>${esc(s.label)}</span>`);
   let segment=[];const flush=()=>{if(segment.length)shapes+=`<polyline fill="none" stroke="${color}" stroke-width="2.5" points="${segment.join(' ')}"/>`;segment=[];};
   s.values.forEach((v,i)=>{if(!Number.isFinite(v)){flush();return;}segment.push(`${xx(i)},${yy(v)}`);shapes+=`<circle cx="${xx(i)}" cy="${yy(v)}" r="3" fill="${color}">${title((groups[i]?.label||'')+': '+value(v,c.unit,currency))}</circle>`;});flush();
  }
 }else{
  const slot=iw/Math.max(1,groups.length),bw=Math.min(48,slot*.6);let running=0;
  if(groups.some(g=>g.series?.length))legend=(groups.find(g=>g.series?.length)?.series||[]).map((s,j)=>`<span><i style="background:${palette[j%palette.length]}"></i>${esc(s.label)}</span>`);
  groups.forEach((g,i)=>{
   const x=left+i*slot+slot/2,segments=g.segments||g.series;
   if((c.type==='stacked'||c.type==='grouped-columns')&&Array.isArray(segments)){
    let accum=0;segments.forEach((s,j)=>{const n=Number.isFinite(s.value)?s.value:0,sx=c.type==='grouped-columns'?x-bw/2+j*bw/segments.length:x-bw/2,sw=c.type==='grouped-columns'?bw/segments.length:bw,y=yy(n+(c.type==='stacked'?accum:0));shapes+=`<rect x="${sx}" y="${y}" width="${sw}" height="${Math.abs(n)/max*ih}" fill="${palette[j%palette.length]}">${title(g.label+' · '+s.label+': '+value(s.value,c.unit,currency))}</rect>`;accum+=n;});
   }else if(c.type==='grouped-columns'&&Number.isFinite(g.target)){
    for(const [j,n] of [g.value,g.target].entries())if(Number.isFinite(n))shapes+=`<rect x="${x-bw/2+j*bw/2}" y="${yy(n)}" width="${bw/2-2}" height="${Math.abs(n)/max*ih}" fill="${palette[j]}">${title(g.label+(j?' target':' actual')+': '+value(n,c.unit,currency))}</rect>`;
   }else if(c.type==='waterfall'){
    const n=Number.isFinite(g.value)?g.value:0,start=g.total?0:running,end=g.total?n:running+n;running=end;
    shapes+=`<rect x="${x-bw/2}" y="${yy(Math.max(start,end))}" width="${bw}" height="${Math.max(1,Math.abs(n)/max*ih)}" fill="${n<0?'#B42318':palette[0]}">${title(g.label+': '+value(n,c.unit,currency))}</rect>`;
   }else if(Number.isFinite(g.value))shapes+=`<rect x="${x-bw/2}" y="${yy(g.value)}" width="${bw}" height="${Math.max(0,g.value)/max*ih}" rx="2" fill="${palette[0]}">${title(g.label+': '+value(g.value,c.unit,currency))}</rect>`;
  });
 }
 const stride=Math.max(1,Math.ceil(groups.length/5));groups.forEach((g,i)=>{if(i%stride===0||i===groups.length-1)shapes+=label(c.type==='line'?xx(i):left+(i+.5)*iw/Math.max(1,groups.length),h-29,short(g.label));});
 return `<svg class="chart-svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(c.title)}">${title(c.title)}${shapes}</svg>${legend.length?`<div class="chart-legend">${legend.join('')}</div>`:''}`;
}
function dataTable(table){
 if(!table?.columns)return '';
 // Actions belong to the actual app, never to an open synthetic preview.
 const cols=table.columns.map((name,index)=>({name,index})).filter(c=>!/action|records\s*\//i.test(c.name));
 return `<div class="table-scroll" tabindex="0" role="region" aria-label="${esc(table.title)}"><table><caption>${esc(table.title)}</caption><thead><tr>${cols.map(c=>`<th scope="col">${esc(c.name)}</th>`).join('')}</tr></thead><tbody>${table.rows?.length?table.rows.map(r=>`<tr>${cols.map(c=>`<td>${esc(r.cells?.[c.index]??'Not recorded')}</td>`).join('')}</tr>`).join(''):`<tr><td colspan="${cols.length}">No sample records match these filters.</td></tr>`}</tbody></table></div>`;
}
export function renderReport(r,currency='USD'){
 const metrics=`<div class="report-kpis">${r.metrics.map(m=>`<div class="report-kpi"><span>${esc(m.label)}</span><strong>${esc(value(m.value,m.unit,currency))}</strong><small>${esc(m.context||m.definition?.basis)}</small></div>`).join('')}</div>`;
 const charts=`<div class="report-charts">${r.charts.map(c=>{const series=c.groups?.find(g=>g.series?.length)?.series||[];return `<section class="report-chart"><h3>${esc(c.title)}</h3>${c.groups?.length?`<div class="chart-scroll" tabindex="0" role="region" aria-label="${esc(c.title)} chart; scroll horizontally on small screens">${chart(c,currency)}</div>`:'<p class="muted">Not enough data for this view.</p>'}<p class="chart-note">${esc(c.note)}</p><details><summary>View chart data</summary><div class="table-scroll"><table><caption>${esc(c.title)} values</caption><thead><tr><th scope="col">Group</th><th scope="col">Value</th>${series.map(s=>`<th scope="col">${esc(s.label)}</th>`).join('')}${c.type==='target'?`<th scope="col">${esc(c.markerLabel||'Target')}</th>`:''}${c.comparison?`<th scope="col">${esc(c.comparisonLabel||'Previous period')}</th>`:''}${c.multiSeries?.map(s=>`<th scope="col">${esc(s.label)}</th>`).join('')||''}</tr></thead><tbody>${c.groups.map((g,i)=>`<tr><th scope="row">${esc(g.label)}</th><td>${esc(value(g.value,c.unit,currency))}</td>${series.map(s=>`<td>${esc(value(g.series?.find(x=>x.label===s.label)?.value,c.unit,currency))}</td>`).join('')}${c.type==='target'?`<td>${esc(value(g.target,c.unit,currency))}</td>`:''}${c.comparison?`<td>${esc(value(c.comparison[i],c.unit,currency))}</td>`:''}${c.multiSeries?.map(s=>`<td>${esc(value(s.values[i],c.unit,currency))}</td>`).join('')||''}</tr>`).join('')}</tbody></table></div></details></section>`;}).join('')}</div>`;
 return `${r.unsupported?'<p class="notice">This selection needs source history that is unavailable in the sample.</p>':''}${r.coverage?.partial?'<p class="notice">Partial history: missing periods are unavailable, not zero.</p>':''}${metrics}${charts}${r.summaryTable?dataTable(r.summaryTable):''}${dataTable(r.table)}`;
}
