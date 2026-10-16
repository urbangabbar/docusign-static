// Public estimates only. Actual billing belongs to the authorized production service.
export function transferCharge(transfers, pricing) {
 if(!Number.isSafeInteger(transfers)||transfers<0)throw new RangeError('Enter a whole, non-negative number of record transfers.');
 let remaining=Math.max(0,transfers-pricing.includedTransfers),micro=0;
 const breakdown=[];
 for(const band of pricing.bands){const count=Math.min(remaining,band.transfers===null?remaining:band.transfers);const amount=count*band.rateMicrousd;micro+=amount;remaining-=count;breakdown.push({count,rate:band.rateMicrousd/1e6,micro:amount});}
 return {transfers,included:Math.min(transfers,pricing.includedTransfers),billable:Math.max(0,transfers-pricing.includedTransfers),micro,cents:Math.round(micro/10000),breakdown};
}
// The receipt key identifies a delivery operation, not a record for an entire month.
// A retry reuses its receipt; a fresh execution counts its successful transfers again.
export function addDelivery(ledger,{account,month,execution,primaryTransfers}) {
 if(!account||!/^\d{4}-\d{2}$/.test(month)||!execution||!Number.isSafeInteger(primaryTransfers)||primaryTransfers<0)throw new RangeError('Invalid delivery receipt');
 const key=JSON.stringify([account,month,execution]);if(Object.hasOwn(ledger,key))return ledger;
 return {...ledger,[key]:primaryTransfers};
}
export function accountTransfers(ledger,account,month){return Object.entries(ledger).reduce((n,[k,v])=>{const [a,m]=JSON.parse(k);return n+(a===account&&m===month?v:0);},0);}
