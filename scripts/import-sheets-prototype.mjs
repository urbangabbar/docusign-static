// Import owned, synthetic report calculations. Never reads the production repository.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=process.argv[2];
if(!source || !source.endsWith('sheets-sync-prototype')) throw Error('Pass the reviewed sheets-sync-prototype directory.');
const base=path.join(source,'src/dashboards');
const {templates,defaultSettings,defaultControls}=await import(pathToFileURL(path.join(base,'catalog.js')));
const {createFixtures}=await import(pathToFileURL(path.join(base,'fixtures.js')));
const {computeDashboard}=await import(pathToFileURL(path.join(base,'engine.js')));
const dest=path.join(root,'assets/google-sheets/demo');fs.mkdirSync(dest,{recursive:true});
for(const name of ['engine.js','fixtures.js','library-engine.js','library-fixtures.js','library-catalog.js','chart-model.js','table-model.js']) fs.copyFileSync(path.join(base,name),path.join(dest,name));
fs.writeFileSync(path.join(dest,'package.json'),JSON.stringify({private:true,type:'module'}));
const reportData=templates.filter(t=>!t.blocked).map(t=>{
 const settings=defaultSettings(t.id);if(t.id==='custom-records')settings.customMappingValidated=true;
 const controls=defaultControls(),result=computeDashboard(t.id,createFixtures(),settings,controls);
 if(result.unsupported)throw Error('Unsupported sample '+t.id);
 return {id:t.id,name:t.name,slug:t.name.toLowerCase().replace(/&/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''),description:t.description,category:t.category,dependencies:t.dependencies,snapshot:!!t.snapshot,settings,controls,result};
});
if(reportData.length!==25)throw Error('Expected 25 supported reports');
fs.writeFileSync(path.join(root,'data/google-sheets-reports.json'),JSON.stringify(reportData,null,2)+'\n');
console.log(`Imported ${reportData.length} synthetic reports and seven pure calculation modules.`);
