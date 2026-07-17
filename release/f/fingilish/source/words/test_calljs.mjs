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

// --- Double-space → period: implementation kept, DISABLED (2026-07-10) ---
// If DOUBLE_SPACE_PERIOD is ever flipped back on in build_calljs.py, these
// expectations must change back to 'سلام. ' behavior.
{
  const t = makeTarget('salam');
  fn.call(null, t, SPACE);           // converts
  fn.call(null, t, SPACE);           // quick second tap
  eq(t.text, 'سلام  ', 'double-space DISABLED: quick second space stays a space');
}
{
  const t = makeTarget('salam');
  fn.call(null, t, SPACE);
  fn.call(null, t, SPACE);
  fn.call(null, t, SPACE);
  eq(t.text, 'سلام   ', 'double-space DISABLED: triple space stays spaces');
}


// --- Shadowing-fix regression battery (2026-07-14, keyboard 1.6) ---
// bale->baleh class: natural typed spellings of high-freq words must not be
// shadowed by low-freq homographs' auto exact keys or lost skel slots.
eq(fire('bale'), 'بله ', 'bale -> yes (not ballet)');
eq(fire('baleh'), 'بله ', 'baleh -> yes');
eq(fire('doroste'), 'درسته ', 'doroste keeps its -e');
eq(fire('zohr'), 'ظهر ', 'zohr -> noon');
eq(fire('zaher'), 'ظاهر ', 'zaher still reachable (displacement guard)');
eq(fire('azizam'), 'عزیزم ', 'azizam');
eq(fire('dooset'), 'دوستت ', 'dooset -> doostet (love you)');
eq(fire('aks'), 'عکس ', 'aks -> photo');
eq(fire('ax'), 'عکس ', 'ax -> photo');
eq(fire('akh'), 'آخ ', 'akh unharmed by ax fix (norm-tier guard)');
eq(fire('felan'), 'فعلا ', 'felan -> for-now');
eq(fire('folan'), 'فلان ', 'folan still so-and-so (displacement guard)');
eq(fire('taarof'), 'تعارف ', 'taarof -> the cultural institution');
eq(fire('taraf'), 'طرف ', 'taraf unharmed (displacement guard)');
eq(fire('khiaboon'), 'خیابون ', 'khiaboon -> colloquial register');
eq(fire('mamnoonam'), 'ممنونم ', 'mamnoonam');
eq(fire('chahar'), 'چهار ', 'chahar -> four');
eq(fire('kas'), 'کس ', 'kas -> person (not photographer)');


// --- Names + first-letter-forms battery (2026-07-17, keyboard 1.7) ---
// User-reported name failures: dict/NAMES fixes
eq(fire('abbasian'), '\u0639\u0628\u0627\u0633\u06cc\u0627\u0646 ', 'abbasian -> Abbasian (ayn)');
eq(fire('abasian'), '\u0639\u0628\u0627\u0633\u06cc\u0627\u0646 ', 'abasian variant');
eq(fire('soraya'), '\u062b\u0631\u06cc\u0627 ', 'soraya -> Soraya (not quickly)');
eq(fire('sorayya'), '\u062b\u0631\u06cc\u0627 ', 'sorayya variant');
eq(fire('ameneh'), '\u0622\u0645\u0646\u0647 ', 'ameneh -> madda');
eq(fire('ava'), '\u0622\u0648\u0627 ', 'ava -> madda');
eq(fire('farzad'), '\u0641\u0631\u0632\u0627\u062f ', 'farzad -> no first alef');
eq(fire('azar'), '\u0622\u0632\u0627\u0631 ', 'azar stays the common word (word-wins)');
eq(fire('aazar'), '\u0622\u0630\u0631 ', 'aazar -> the name (curated aa-key)');
// Leading apostrophe / Arabizi digit (token regex fix)
eq(fire("'abbasian"), '\u0639\u0628\u0627\u0633\u06cc\u0627\u0646 ', 'leading apostrophe joins token');
eq(fire('3abbasian'), '\u0639\u0628\u0627\u0633\u06cc\u0627\u0646 ', 'leading 3 joins token');
eq(fire("'"), "' ", 'lone apostrophe does not convert');
eq(fire('3'), '3 ', 'lone digit does not convert');
// aa-intent: explicit aa never collapsed into a different word
eq(fire('aameneh'), '\u0622\u0645\u0646\u0647 ', 'aameneh not hijacked by skel');
eq(fire('aava'), '\u0622\u0648\u0627 ', 'aava');
eq(fire('aali'), '\u0639\u0627\u0644\u06cc ', 'aali -> excellent (was unreachable)');
eq(fire('aadi'), '\u0639\u0627\u062f\u06cc ', 'aadi -> normal');
eq(fire('aashegh'), '\u0639\u0627\u0634\u0642 ', 'aashegh (ayn+alef aa-variant)');
eq(fire('aalan'), '\u0627\u0644\u0627\u0646 ', 'aalan protected (MANUAL variant)');
// H8 fallback heuristic on out-of-dict words
eq(fire('shamzad'), '\u0634\u0645\u0632\u0627\u062f ', 'H8: last-vowel alef only');
eq(fire('golshanifar'), '\u06af\u0644\u0634\u0627\u0646\u06cc\u0641\u0631 ', 'H8: -ani + -far suffix');
eq(fire('zarbanipour'), '\u0632\u0631\u0628\u0627\u0646\u06cc\u067e\u0648\u0631 ', 'H8: -ani + -pour suffix');
eq(fire('vetkarian'), '\u0648\u062a\u06a9\u0627\u0631\u06cc\u0627\u0646 ', 'H8: -ian suffix');
// Bulk-names spot checks (dataset ingest)
eq(fire('mohammadi'), '\u0645\u062d\u0645\u062f\u06cc ', 'mohammadi (surname #1)');
eq(fire('hosseini'), '\u062d\u0633\u06cc\u0646\u06cc ', 'hosseini (surname #2)');

console.log(`\n${pass}/${pass + fail} passed`);
process.exit(fail ? 1 : 0);
