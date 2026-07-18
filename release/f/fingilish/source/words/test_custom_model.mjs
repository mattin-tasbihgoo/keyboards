// test_custom_model.mjs — gate on the COMPILED custom-1.0 model artifact.
// Stubs LMLayerWorker, loads build/mattin.fa.fingilish.model.js, and runs a
// determinism + correctness battery through the real predict() entry point.
import { readFileSync } from 'fs';
const path = process.argv[2] || new URL('../../build/mattin.fa.fingilish.model.js', import.meta.url).pathname;
globalThis.LMLayerWorker = { loadModel(m) { globalThis.__m = m; } };
new Function(readFileSync(path, 'utf-8'))();
const m = globalThis.__m;
if (!m) { console.error('model did not load'); process.exit(1); }

const ctx = left => ({ left, startOfBuffer: true, endOfBuffer: true });
const T0 = { insert: '', deleteLeft: 0 };
const strip = s => s.replace(/[\u2066-\u2069]/g, '');
function tops(left) {
  return m.predict(T0, ctx(left)).map(x => strip(x.sample.displayAs));
}
let pass = 0, fail = 0;
function eq(cond, label, extra) {
  cond ? pass++ : fail++;
  console.log(`${cond ? '\u2713' : '\u2717'} ${label}${cond ? '' : '  [' + extra + ']'}`);
}
const U = a => a.map(s => [...s].map(c => c.codePointAt(0) > 127 ? '\\u' + c.codePointAt(0).toString(16) : c).join('')).join(' | ');

// correctness battery (top suggestion / membership)
const per = {
  salam: '\u0633\u0644\u0627\u0645', soraya: '\u062B\u0631\u06CC\u0627',
  farzad: '\u0641\u0631\u0632\u0627\u062F', abbasian: '\u0639\u0628\u0627\u0633\u06CC\u0627\u0646',
  asabani: '\u0639\u0635\u0628\u0627\u0646\u06CC', azar: '\u0622\u0632\u0627\u0631',
  azarName: '\u0622\u0630\u0631', bale: '\u0628\u0644\u0647',
  hastam: '\u0647\u0633\u062A\u0645', shamzad: '\u0634\u0645\u0632\u0627\u062F',
};
eq(tops('salam')[0] === per.salam, 'salam top = salam', U(tops('salam')));
eq(tops('soraya')[0] === per.soraya, 'soraya top = Soraya', U(tops('soraya')));
eq(tops('farzad')[0] === per.farzad, 'farzad top = Farzad', U(tops('farzad')));
eq(tops('abbasian')[0] === per.abbasian, 'abbasian top', U(tops('abbasian')));
eq(tops('asabani')[0] === per.asabani, 'asabani top = angry', U(tops('asabani')));
eq(tops('azar')[0] === per.azar, 'azar top = word (word-wins)', U(tops('azar')));
eq(tops('azar').includes(per.azarName), 'azar list includes the NAME (alternate)', U(tops('azar')));
eq(tops('bale')[0] === per.bale, 'bale top = yes', U(tops('bale')));
eq(tops('hastam')[0] === per.hastam, 'hastam top = hastam', U(tops('hastam')));
eq(tops('shamzad').includes(per.shamzad), 'unknown word offers literal translit', U(tops('shamzad')));
// literal == winner dedups to ONE clean chip (ideal case)
eq(tops('salam').length === 1, 'salam: literal==dict dedups to single chip', U(tops('salam')));
// literal != winner -> both offered
const kb = tops('khiaboon');
eq(kb.length >= 2 && kb[0] === '\u062E\u06CC\u0627\u0628\u0648\u0646', 'khiaboon: dict top + differing literal', U(kb));
// incremental preview: partial word still yields suggestions
eq(tops('sala').length > 0, 'partial "sala" yields live preview', U(tops('sala')));
// determinism: 5 identical calls, identical output
const a = JSON.stringify(m.predict(T0, ctx('asabani')));
let det = true;
for (let i = 0; i < 4; i++) if (JSON.stringify(m.predict(T0, ctx('asabani'))) !== a) det = false;
eq(det, 'predict() is deterministic across identical calls');
// transform mechanics: applies incoming transform before tokenizing
const viaTransform = m.predict({ insert: 'm', deleteLeft: 0 }, ctx('sala'));
eq(strip(viaTransform[0].sample.displayAs) === per.salam &&
   viaTransform[0].sample.transform.deleteLeft === 5,
   'transform applied: sala+m -> salam, deleteLeft=5',
   JSON.stringify(viaTransform[0] && viaTransform[0].sample.transform));
// empty / non-word context
eq(m.predict(T0, ctx('')).length === 0, 'empty context -> no suggestions');
eq(m.predict(T0, ctx('\u0633\u0644\u0627\u0645 ')).length === 0, 'after conversion+space -> no stale suggestions');
// wordbreak + configure exist and behave
eq(m.wordbreak(ctx('hey salam')) === 'salam', 'wordbreak returns trailing token');
eq(m.configure({ maxLeftContextCodePoints: 32 }).leftContextCodePoints === 32, 'configure mirrors capabilities');

console.log(`${pass}/${pass + fail} passed`);
process.exit(fail ? 1 : 0);
