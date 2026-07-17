// test_model_keys.mjs — gate: banner key function must map typed Latin and
// its Persian target to the SAME key (doc-04 L4). Extracts searchTermToKey
// from model.ts source and asserts pair equality.
import { readFileSync } from 'fs';
const src = readFileSync(new URL('../mattin.fa.fingilish.model.ts', import.meta.url), 'utf-8');
const m = src.match(/searchTermToKey: (function\(term: string\): string \{[\s\S]*?\n  \})/);
if (!m) { console.error('searchTermToKey not found'); process.exit(1); }
let body = m[1].replace('term: string', 'term').replace('): string {', ') {')
  .replace(/: Record<string, string>/g, '').replace(/: string\b/g, '');
const stk = new Function('return ' + body)();

const pairs = [
  // typed latin              persian (\u-escaped)
  ['asabani',  '\u0639\u0635\u0628\u0627\u0646\u06CC'],   // عصبانی
  ['soraya',   '\u062B\u0631\u06CC\u0627'],
  ['sorayya',  '\u062B\u0631\u06CC\u0627'],
  ['farzad',   '\u0641\u0631\u0632\u0627\u062F'],
  ['abbasian', '\u0639\u0628\u0627\u0633\u06CC\u0627\u0646'],
  ['abasian',  '\u0639\u0628\u0627\u0633\u06CC\u0627\u0646'],
  ['ameneh',   '\u0622\u0645\u0646\u0647'],
  ['ava',      '\u0622\u0648\u0627'],
  ['salam',    '\u0633\u0644\u0627\u0645'],
  ['bale',     '\u0628\u0644\u0647'],
  ['khiaboon', '\u062E\u06CC\u0627\u0628\u0648\u0646'],
  ['aks',      '\u0639\u06A9\u0633'],
  ['aali',     '\u0639\u0627\u0644\u06CC'],
  ['kardi',    '\u06A9\u0631\u062F\u06CC'],
  ['mohammadi','\u0645\u062D\u0645\u062F\u06CC'],
  ['hosseini', '\u062D\u0633\u06CC\u0646\u06CC'],
];
let fail = 0;
for (const [lat, per] of pairs) {
  const kl = stk(lat), kp = stk(per);
  const ok = kl === kp && kl.length > 0;
  if (!ok) { fail++; console.log(`\u2717 ${lat}: typed-key=${kl} persian-key=${kp}`); }
  else { console.log(`\u2713 ${lat} \u2194 key "${kl}"`); }
}
console.log(`${pairs.length - fail}/${pairs.length} key pairs match`);
process.exit(fail ? 1 : 0);
