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
 * Normalization rules (must match norm() in build_dict.py and
 * ConvertWord.call_js):
 *   strip '/2/3, c→s before e/i/y else c→k ('ch' protected),
 *   [consonant]y$→i, eh$→e
 *   x→kh, q→gh, w→v, ph→f
 *   aa→a, oo→o, ee→i, ou→o
 *   u→o  (khub → khob)
 *   ey→i, ei→i  (kheyli → khili), y→i everywhere
 *   collapse doubled letters
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
    // These bypass the algorithmic conversion for high-frequency words
    // where the algorithm would produce a poor key.
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
      "الان": "alan",  "شاید": "shayad", "حتی": "hata",
      "بعد": "bad",    "مثل": "mesl",    "همین": "hamin",
      "هیچ": "hich",   "یکی": "yeki",
      "برای": "baraye","حتما": "hatman", "هیچی": "hichi",
      "مگه": "mage",   "ولی": "vali",    "اگر": "agar",

      // Common verbs
      "باید": "bayad",      "باشه": "bashe",     "کن": "kon",
      "کنم": "konam",       "کنی": "koni",       "کنه": "kone",
      "کنیم": "konim",      "کنید": "konid",
      "میکنم": "mikonam",   "میکنی": "mikoni",   "میکنه": "mikone",
      "میکنیم": "mikonim",
      "بکن": "bokon",       "نکن": "nakon",      "بده": "bede",
      "میده": "mide",       "داد": "dad",        "داری": "dari",
      "داره": "dare",       "دارم": "daram",     "دارن": "daran",
      "داریم": "darim",     "دارید": "darid",
      "بیا": "bia",
      "میام": "miam",       "میای": "miai",      "میاد": "miad",
      "بیام": "biam",       "بیای": "biai",
      "بریم": "berim",      "برو": "boro",       "برم": "beram",
      "بری": "beri",        "بره": "bereh",      "برن": "beran",
      "رفتم": "raftam",     "رفتی": "rafti",     "رفت": "raft",
      "رفتن": "raftan",     "رفتیم": "raftim",
      "میرم": "miram",      "میری": "miri",      "میره": "mire",
      "میریم": "mirim",
      "بگو": "bego",        "گفتم": "goftam",    "گفتی": "gofti",
      "گفت": "goft",        "گفتن": "goftan",    "میگم": "migam",
      "میگی": "migi",       "میگه": "mige",      "میگن": "migan",
      "ببین": "bebin",      "دیدم": "didam",     "دید": "did",
      "دیدی": "didi",       "میبینم": "mibinam",  "میبینی": "mibini",
      "بزن": "bezan",       "زدم": "zadam",      "زد": "zad",
      "بشین": "beshin",     "نشین": "nashin",
      "میخوام": "mikham",   "نمیخوام": "nemikham",
      "میخوای": "mikhai",   "میخواد": "mikhad",
      "بمون": "bemoon",     "موندم": "moondam",
      "بگیر": "begir",      "گرفتم": "gereftam", "گرفت": "gereft",
      "بذار": "bezar",      "گذاشتم": "gozashtam",
      "نمیدونم": "nemidoonam","میدونم": "midoonam","میدونی": "midooni",
      "میدونه": "midooneh",
      "میتونم": "mitonam",  "میتونی": "mitooni", "میتونه": "mitooneh",
      "نمیتونم": "nemitonam","نمیتونی": "nemitooni",
      "شدم": "shodam",      "شدی": "shodi",      "شد": "shod",
      "بشه": "beshe",       "میشه": "mishe",     "نمیشه": "nemishe",
      "هستم": "hastam",     "هستی": "hasti",     "هست": "hast",
      "بودم": "boodam",     "بودی": "boodi",
      "بودیم": "boodim",    "بودن": "boodan",    "بودند": "boodand",
      "بخور": "bekhor",     "خوردم": "khordam",
      "بخون": "bekhon",     "خوندم": "khondam",
      "بنویس": "benevis",   "نوشتم": "neveshtam",
      "شنیدم": "shenidam",  "شنیدی": "shenidi",
      "فهمیدم": "fahmidam", "فهمیدی": "fahmidi",

      // Question words
      "چی": "chi",      "چه": "che",      "چرا": "chera",
      "چطور": "chetoor", "چطوری": "chetori","چطوره": "chetoreh",
      "کجا": "koja",    "کجایی": "kojai",  "کی": "ki",
      "کدوم": "kodoom",  "چند": "chand",   "چیکار": "chikar",
      "چقدر": "cheqadr",

      // Adjectives / adverbs
      "خیلی": "kheili",  "خوب": "khoob",   "خوبه": "khobe",
      "خوبی": "khobi",
      "بد": "bad",        "زیاد": "ziad",   "کم": "kam",
      "بزرگ": "bozorg",   "کوچیک": "kuchik",
      "بهتر": "behtar",   "بهترین": "behtarin","بدتر": "badtar",
      "سخت": "sakht",     "راحت": "rahat",
      "درست": "dorost",   "زود": "zood",    "دیر": "dir",
      "تند": "tond",      "نزدیک": "nazdik", "دور": "door",
      "بیشتر": "bishtar",

      // Greetings / social
      "سلام": "salam",       "ممنون": "mamnoon",
      "مرسی": "mersi",       "خداحافظ": "khodahafez",
      "خوشبختم": "khoshbakhtam",
      "ببخشید": "bebakhshid", "ببخش": "bebakhsh",
      "متاسفم": "motasefam",  "تبریک": "tabrik",
      "لطفا": "lotfan",

      // Nouns
      "دوست": "doost",   "دوستت": "doostet", "خونه": "khune",
      "خانه": "khaneh",  "خانواده": "khanevade",
      "ماشین": "mashin", "روز": "rooz",     "شب": "shab",
      "امروز": "emrooz", "فردا": "farda",   "دیروز": "diruz",
      "دیشب": "dishab",
      "هفته": "hafte",   "ماه": "mah",      "سال": "sal",
      "ساعت": "saat",
      "اسم": "esm",      "چشم": "cheshm",   "دست": "dast",
      "قلب": "ghalb",    "دل": "del",       "سر": "sar",
      "پا": "pa",        "گوش": "gush",
      "بچه": "bache",    "بابا": "baba",    "مامان": "maman",
      "پدر": "pedar",    "مادر": "madar",
      "پسر": "pesar",    "دختر": "dokhtar",
      "برادر": "baradar", "خواهر": "khahar",
      "مرد": "mard",     "زن": "zan",
      "خاله": "khaleh",  "عمو": "amu",      "دایی": "dayi",
      "دانشگاه": "daneshgah","مدرسه": "madrese",
      "خیابان": "khiaban","شهر": "shahr",   "کشور": "keshvar",
      "دنیا": "donya",   "زندگی": "zendegi",
      "پول": "pool",     "کار": "kar",      "جا": "ja",
      "راه": "rah",      "آب": "ab",        "غذا": "ghaza",
      "خواب": "khab",

      // Colloquial / chat
      "آره": "are",      "آخه": "akhe",     "وای": "vay",
      "هی": "hey",       "کنار": "kenar",   "لحظه": "lahze",
      "وایسا": "veysa",
      "خودش": "khodesh",  "خودم": "khodam",  "خودت": "khodet",
      "بهش": "behesh",    "بهم": "behem",    "بهت": "behet",
      "ازش": "azash",     "باهاش": "bahash", "براش": "barash",
      "خوشحالم": "khoshalam",   "ناراحتم": "narahatam",
      "عاشقتم": "asheghetam",
      "مراقب": "morageb",       "بیخیال": "bikheyal",
      "ولش": "velesh",   "ولم": "velam",
      "اصلاً": "aslan",  "اصلا": "aslan",
      "مثلاً": "masalan", "مثلا": "masalan",
      "واقعاً": "vaghean","واقعا": "vaghan",
      "یعنی": "yani",
      "جدی": "jeddi",    "دروغ": "doroogh",  "راست": "rast",
      "همیشه": "hamishe", "دوباره": "dobare",
      "فکر": "fekr",     "نظر": "nazar",    "حرف": "harf",
      "وقت": "vaght",    "وقتی": "vaghti",
      "شروع": "shoru",   "تموم": "tamoom",  "تمام": "tamam",
      "انجام": "anjam",  "مشکل": "moshkel",
      "نگران": "negaran","منتظر": "montazer",
      "خوشحال": "khoshhal","ناراحت": "narahat",
      "عاشق": "ashegh",  "عشق": "eshgh",

      // Consonantal و / hamze words
      "جواب": "javab",  "دیوار": "divar",  "آواز": "avaz",
      "مسئله": "masale", "او": "oo",        "نو": "no",

      // Names
      "علی": "ali",      "رضا": "reza",     "محمد": "mohammad",
      "متین": "matin",   "سارا": "sara",    "مریم": "maryam",
      "حسین": "hosein",  "زهرا": "zahra",
      "امیر": "amir",    "مهدی": "mahdi",
      "ایران": "iran",   "تهران": "tehran",
    };

    // Multi-character Persian → Latin (checked first in sequence)
    const MULTI: Record<string, string> = {
      "خو":"kho",  // خوب→khob, خونه→khone (NOT khvb/khvne)
      "خ":"kh","ش":"sh","چ":"ch","ژ":"zh","غ":"gh","ق":"gh",
    };

    // Single-character Persian → Latin
    const SINGLE: Record<string, string> = {
      "ا":"a","آ":"a","ب":"b","پ":"p","ت":"t","ث":"s",
      "ج":"j","ح":"h","د":"d","ذ":"z","ر":"r","ز":"z",
      "س":"s","ص":"s","ض":"z","ط":"t","ظ":"z","ع":"",
      "ف":"f","ک":"k","گ":"g","ل":"l","م":"m","ن":"n",
      "ه":"h","ی":"i","ء":"","ئ":"",
    };

    // Step 1: if Persian, convert to raw Latin
    const hasPersian = /[\u0600-\u06FF]/.test(term);
    let raw: string;
    if (hasPersian) {
      if (MANUAL[term] !== undefined) {
        raw = MANUAL[term];
      } else {
        raw = "";
        const chars = Array.from(term);
        let i = 0;
        while (i < chars.length) {
          // Try multi-char mappings (خو before خ)
          if (i + 1 < chars.length) {
            const pair = chars[i] + chars[i+1];
            if (MULTI[pair] !== undefined) {
              raw += MULTI[pair];
              i += 2;
              continue;
            }
          }
          const ch = chars[i];
          // و — context-dependent (must match build_dict.py):
          // word-initial → "va"; between consonants or final after a
          // consonant → long vowel "oo"; adjacent to a vowel → "v"
          if (ch === "\u0648") {
            const CONS = "بپتثجچحخدذرزسشصضطظعغفقکگلمنهی";
            const prevCons = i > 0 && CONS.indexOf(chars[i-1]) >= 0;
            const nextCons = i + 1 < chars.length && CONS.indexOf(chars[i+1]) >= 0;
            const atEnd = i + 1 >= chars.length;
            if (i === 0) { raw += "va"; }
            else if (prevCons && (nextCons || atEnd)) { raw += "oo"; }
            else { raw += "v"; }
            i++;
            continue;
          }
          // Word-final ه → "e" (not "h")
          if (ch === "\u0647" && i === chars.length - 1) {
            raw += "e";
          } else if (MULTI[ch] !== undefined) {
            raw += MULTI[ch];
          } else if (SINGLE[ch] !== undefined) {
            raw += SINGLE[ch];
          }
          i++;
        }
        // Collapse triple+ repeats but keep doubles (e.g. "oo")
        raw = raw.replace(/(.)\1{2,}/g, "$1$1");
      }
    } else {
      raw = term;
    }

    // Step 2: normalize variant Latin spellings → canonical key
    // MUST match norm() in build_dict.py and ConvertWord.call_js
    let key = raw.toLowerCase();
    // Strip apostrophes and Arabizi digits (2=ء, 3=ع) — keys are bare
    key = key.replace(/['\u201923]/g, "");
    // c → s before e/i/y, else c → k ('ch' protected)
    key = key.replace(/c(?=[eiy])/g, "s");
    key = key.replace(/c(?!h)/g, "k");
    // Word-final consonant+y → i  (kardy → kardi)
    key = key.replace(/([^aeiou])y$/, "$1i");
    // Word-final 'eh' → 'e'  (kardeh → karde)
    key = key.replace(/eh$/, "e");
    key = key.replace(/x/g, "kh");
    key = key.replace(/q/g, "gh");
    key = key.replace(/w/g, "v");
    key = key.replace(/ph/g, "f");
    key = key.replace(/aa/g, "a");
    key = key.replace(/oo/g, "o");
    key = key.replace(/ee/g, "i");
    key = key.replace(/ou/g, "o");
    key = key.replace(/u/g, "o");
    key = key.replace(/ey/g, "i");
    key = key.replace(/ei/g, "i");
    // y → i everywhere (saye→saie, miyam→miiam→miam)
    key = key.replace(/y/g, "i");
    key = key.replace(/(.)\1+/g, "$1");
    key = key.replace(/[^a-z]/g, "");
    return key;
  },
};

export default source;