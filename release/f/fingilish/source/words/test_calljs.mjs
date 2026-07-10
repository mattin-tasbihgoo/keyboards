// test_calljs.mjs — end-to-end regression harness for ConvertWord.call_js
// Simulates the Keyman IMX target API and fires the generated function body.
// Run: node test_calljs.mjs
import { readFileSync } from 'fs';

const body = readFileSync(new URL('./ConvertWord.call_js', import.meta.url), 'utf-8');
const fn = new Function(body);

function makeTarget(text) {
  return {
    text,
    getTextBeforeCaret() { return this.text; },
    deleteCharsBeforeCaret(n) { this.text = this.text.slice(0, this.text.length - n); },
    insertTextBeforeCaret(s) { this.text += s; },
  };
}
const SPACE = { Lcode: 32, Lmodifiers: 0 };
function fire(text, keyEvt = SPACE) {
  const t = makeTarget(text);
  fn.call(null, t, keyEvt);
  return t.text;
}

let pass = 0, fail = 0;
function eq(got, want, label) {
  const ok = got === want;
  ok ? pass++ : fail++;
  console.log(`${ok ? '✓' : '✗'} ${label}: ${JSON.stringify(got)}${ok ? '' : ' (wanted ' + JSON.stringify(want) + ')'}`);
}

// --- Core conversion ---
eq(fire('salam'), 'سلام ', 'salam+space');
eq(fire('Salam'), 'سلام ', 'capitalized');
eq(fire('javab'), 'جواب ', 'javab (consonantal و)');
eq(fire('oomad'), 'اومد ', 'oomad (word-initial او)');
eq(fire('umad'), 'اومد ', 'umad');
eq(fire('aval'), 'اول ', 'aval');
eq(fire('ok'), 'اوکی ', 'ok → اوکی');
eq(fire('bad'), 'بد ', 'bad → بد');
eq(fire('baad'), 'بعد ', 'baad → بعد');
eq(fire('khab'), 'خواب ', 'khab → خواب');
eq(fire("sa'at"), 'ساعت ', "sa'at (apostrophe, whole word)");
eq(fire('mota2sefam'), 'متاسفم ', 'mota2sefam (Arabizi 2)');
eq(fire('miyam'), 'میام ', 'miyam (y→i)');
eq(fire('saye'), 'سایه ', 'saye');
eq(fire('masale'), 'مسئله ', 'masale');

// --- Prototype-safety ---
eq(fire('constructor').includes('function'), false, 'no constructor injection');
eq(fire('hasownproperty').includes('function'), false, 'no hasOwnProperty leak');

// --- Fallback ---
eq(fire('boro').endsWith('و '), true, 'final -o emits و');
eq(fire('filmo'), 'فیلمو ', 'filmo (object marker -o)');
eq(fire('mattin'), 'متین ', 'mattin (name)');

// --- Triggers ---
eq(fire('salam', { Lcode: 191, Lmodifiers: 0x10 }), 'سلام؟', '? → ؟');
eq(fire('salam', { Lcode: 188, Lmodifiers: 0 }), 'سلام،', ', → ،');
eq(fire('salam', { Lcode: 186, Lmodifiers: 0 }), 'سلام؛', '; → ؛');
eq(fire('salam', { Lcode: 186, Lmodifiers: 0x10 }), 'سلام:', 'shift+; → :');
eq(fire('salam', { Lcode: 190, Lmodifiers: 0 }), 'سلام.', '. trigger');

// --- Non-word paths ---
eq(fire('سلام '), 'سلام  ', 'space after Persian (slow: plain space)');
eq(fire('123'), '123 ', 'digits untouched');

// --- Double-space → period (quick taps) ---
{
  const t = makeTarget('salam');
  fn.call(null, t, SPACE);           // converts, arms window
  fn.call(null, t, SPACE);           // quick second tap
  eq(t.text, 'سلام. ', 'double-space period after conversion');
}
{
  const t = makeTarget('salam');
  fn.call(null, t, SPACE);
  await new Promise(r => setTimeout(r, 600));
  fn.call(null, t, SPACE);           // slow second tap
  eq(t.text, 'سلام  ', 'slow second space stays a space');
}
{
  const t = makeTarget('salam');
  fn.call(null, t, SPACE);
  fn.call(null, t, SPACE);           // → سلام.
  fn.call(null, t, SPACE);           // quick third space after '. '
  eq(t.text, 'سلام.  ', 'no period chain after period');
}

console.log(`\n${pass}/${pass + fail} passed`);
process.exit(fail ? 1 : 0);
