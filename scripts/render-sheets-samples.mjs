import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {renderReport} from '../assets/google-sheets/report-renderer.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const reports=JSON.parse(fs.readFileSync(path.join(root,'data/google-sheets-reports.json')));
fs.writeFileSync(path.join(root,'data/google-sheets-rendered.json'),JSON.stringify(Object.fromEntries(reports.map(r=>[r.id,renderReport(r.result,r.settings.currency)]))));
console.log('Rendered '+reports.length+' reports to crawlable sample HTML.');
