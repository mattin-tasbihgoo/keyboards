/*
 * mattin.fa.fingilish.model.ts
 *
 * Keyman Lexical Model — Fingilish (Latin input → Persian output)
 *
 * The wordlist contains Persian words. searchTermToKey converts them to
 * Latin keys for trie indexing, and also normalizes the user's typed Latin
 * before lookup. Both paths must produce the same key for a match.
 *
 * All helpers are defined INSIDE searchTermToKey because kmc compiles the
 * model in a sandboxed scope where top-level module functions are not
 * accessible at runtime.
 *
 * RTL FIX: isRTL is set to true so the suggestion banner renders Persian
 * correctly. Persian words in the wordlist are wrapped with BiDi isolation
 * characters (U+2067 RLI / U+2069 PDI) as a belt-and-suspenders fix for
 * platforms where isRTL alone doesn't drive banner direction.
 * searchTermToKey strips these before processing.
 *
 * Variants collapsed before lookup:
 *   saalam/salaam → salam   (aa→a)
 *   roo/rooh → ro           (oo→o)
 *   xeili → kheili          (x→kh)
 *   qalb → ghalb            (q→gh)
 */

const source: LexicalModelSource = {
  format: "trie-1.0",
  wordBreaker: { use: "default" },
  punctuation: { insertAfterWord: " " },
  languageUsesCasing: false,
  isRTL: true,
  sources: ["words/fingilish.wordlist.tsv"],

  searchTermToKey: function(term: string): string {

    // ── Strip BiDi isolation characters (RLI, LRI, FSI, PDI) ──
    // The wordlist wraps Persian words in U+2067...U+2069 for RTL banner fix.
    // Strip them before any processing so lookups and indexing work cleanly.
    term = term.replace(/[\u2066-\u2069]/g, '');

    // Manual overrides: common Persian words → canonical Latin key
    const MANUAL: Record<string, string> = {
      // Top function words
      "که": "ke",      "رو": "ro",       "به": "be",      "من": "man",
      "و": "o",        "از": "az",       "تو": "to",      "اون": "oon",
      "این": "in",     "یه": "ye",       "می": "mi",      "نه": "na",
      "با": "ba",      "در": "dar",      "ما": "ma",      "هم": "ham",
      "بود": "bood",   "تا": "ta",       "اگه": "age",    "همه": "hame",
      "هر": "har",     "اما": "ama",     "یا": "ya",      "چون": "chon",
      "پس": "pas",     "دیگه": "dige",   "هنوز": "hanooz","حالا": "hala",
      "فقط": "faghat", "خب": "khob",     "اینجا": "inja", "اونجا": "onja",
      "الان": "alan",  "شاید": "shayad",

      // Common verbs
      "باید": "bayad",      "باشه": "bashe",     "کن": "kon",
      "کنم": "konam",       "کنی": "koni",       "کنه": "kone",
      "کنیم": "konim",      "کنید": "konid",
      "میکنم": "mikonam",   "میکنی": "mikoni",   "میکنه": "mikone",
      "بکن": "bokon",       "نکن": "nakon",      "بده": "bede",
      "میده": "mide",       "داد": "dad",        "داری": "dari",
      "داره": "dare",       "دارم": "daram",     "دارن": "daran",
      "داریم": "darim",     "بیا": "bia",
      "میام": "miam",       "میای": "miai",      "میاد": "miad",
      "بریم": "berim",      "برو": "boro",
      "رفتم": "raftam",     "رفتی": "rafti",     "رفت": "raft",
      "بگو": "bego",        "گفتم": "goftam",    "گفتی": "gofti",
      "گفت": "goft",        "گفتن": "goftan",    "ببین": "bebin",
      "دیدم": "didam",      "دید": "did",
      "بزن": "bezan",       "زدم": "zadam",      "زد": "zad",
      "بشین": "beshin",     "نشین": "nashin",
      "میخوام": "mikham",   "نمیخوام": "nemikham",
      "میخوای": "mikhai",   "میخواد": "mikhad",
      "میرم": "miram",      "میری": "miri",      "میره": "mire",
      "بمون": "bemoon",     "موندم": "moondam",
      "بگیر": "begir",      "گرفتم": "gereftam", "گرفت": "gereft",
      "بذار": "bezar",      "گذاشتم": "gozashtam",
      "نمیدونم": "nemidoonam","میدونم": "midoonam","میدونی": "midooni",
      "میتونم": "mitonam",  "میتونی": "mitooni", "نمیتونم": "nemitonam",
      "شدم": "shodam",      "شد": "shod",        "بشه": "beshe",
      "میشه": "mishe",      "نمیشه": "nemishe",

      // Question words
      "چی": "chi",      "چه": "che",      "چرا": "chera",
      "چطور": "chetoor", "کجا": "koja",    "کی": "ki",
      "کدوم": "kodoom",  "چند": "chand",

      // Adjectives / adverbs
      "خیلی": "kheili",  "خوب": "khob",    "خوبه": "khube",
      "بد": "bad",        "زیاد": "ziad",   "کم": "kam",
      "بزرگ": "bozorg",   "کوچیک": "kuchik",

      // Greetings / social
      "سلام": "salam",       "ممنون": "mamnoon",
      "مرسی": "mersi",       "خداحافظ": "khodahafez",
      "خوشبختم": "khoshbakhtam",

      // Nouns
      "دوست": "doost",   "خونه": "khune",   "ماشین": "mashin",
      "روز": "rooz",     "شب": "shab",      "امروز": "emrooz",
      "فردا": "farda",   "دیروز": "diruz",
      "هفته": "hafte",   "ماه": "mah",      "سال": "sal",
      "اسم": "esm",      "چشم": "cheshm",   "دست": "dast",
      "قلب": "ghalb",    "دل": "del",       "سر": "sar",
      "پا": "pa",

      // Colloquial / chat
      "آره": "are",      "آخه": "akhe",     "وای": "vay",
      "هی": "hey",       "کنار": "kenar",   "لحظه": "lahze",
      "وایسا": "veysa",  "ببخش": "bebakhsh",
      "خوشحالم": "khoshalam",   "ناراحتم": "narahatam",
      "عاشقتم": "asheghetam",   "دوستت": "doostet",
      "مراقب": "morageb",       "بیخیال": "bikheyal",
      "ولش": "velesh",   "ولم": "velam",
      "اصلاً": "aslan",  "مثلاً": "masalan", "واقعاً": "vaghean",
      "جدی": "jeddi",    "دروغ": "doroogh",  "راست": "rast",

      // Names
      "علی": "ali",      "رضا": "reza",     "محمد": "mohammad",
      "متین": "matin",   "سارا": "sara",    "مریم": "maryam",
      "حسین": "hosein",  "زهرا": "zahra",
    };

    // Multi-character Persian → Latin
    const MULTI: Record<string, string> = {
      "خ":"kh","ش":"sh","چ":"ch","ژ":"zh","غ":"gh","ق":"gh",
    };

    // Single-character Persian → Latin
    const SINGLE: Record<string, string> = {
      "ا":"a","آ":"a","ب":"b","پ":"p","ت":"t","ث":"s",
      "ج":"j","ح":"h","د":"d","ذ":"z","ر":"r","ز":"z",
      "س":"s","ص":"s","ض":"z","ط":"t","ظ":"z","ع":"",
      "ف":"f","ک":"k","گ":"g","ل":"l","م":"m","ن":"n",
      "و":"v","ه":"h","ی":"y","ء":"",
    };

    // Step 1: if Persian, convert to raw Latin
    const hasPersian = /[\u0600-\u06FF]/.test(term);
    let raw: string;
    if (hasPersian) {
      if (MANUAL[term] !== undefined) {
        raw = MANUAL[term];
      } else {
        raw = "";
        for (const ch of term) {
          if (MULTI[ch] !== undefined) raw += MULTI[ch];
          else if (SINGLE[ch] !== undefined) raw += SINGLE[ch];
        }
        raw = raw.replace(/(.)\1{2,}/g, "$1");
      }
    } else {
      raw = term;
    }

    // Step 2: normalize variant Latin spellings → canonical key
    let key = raw.toLowerCase();
    key = key.replace(/x/g, "kh");
    key = key.replace(/q/g, "gh");
    key = key.replace(/w/g, "v");
    key = key.replace(/aa/g, "a");
    key = key.replace(/oo/g, "o");
    key = key.replace(/ee/g, "i");
    key = key.replace(/ou/g, "o");
    key = key.replace(/(.)\1+/g, "$1");

    return key;
  },
};

export default source;
