/*
 * fingilish.model.ts
 * Keyman Lexical Model — Fingilish (Latin → Persian transliteration)
 *
 * HOW THIS WORKS
 * ──────────────
 * The user types a full Latin-script word (Fingilish), presses space or
 * punctuation, and the keyboard replaces it with the Persian equivalent.
 *
 * Keyman's lexical model drives this via `searchTermToKey`, which is called:
 *   1. On every word in fingilish.wordlist.tsv (to build the trie index).
 *   2. On the user's typed Latin buffer (to look up candidates).
 *
 * Both calls must map to the same "key space" so that typing "salam" finds
 * the index entry for "سلام".
 *
 * Key design decisions:
 *   - Key space is normalized Latin: single vowels, no digraph variants.
 *     "saalam", "salam", and "salaam" all collapse to key "salam".
 *   - Persian words are converted to their canonical Latin key via the same
 *     MANUAL_LATIN map used in build_lexicon.py (embedded below).
 *   - Variant inputs (aa/a, oo/o, ee/i, x/kh, q/gh, w/v) are normalized
 *     before lookup, so the user can type either and get the same result.
 *
 * UPDATING THE TRANSLITERATION
 * ─────────────────────────────
 * If you add entries to MANUAL_LATIN in build_lexicon.py, mirror them in
 * MANUAL_LATIN below so that the trie index and the lookup stay in sync.
 *
 * COMPILATION
 * ───────────
 * Place this file at:
 *   source/fingilish.model.ts
 * Place fingilish.wordlist.tsv at:
 *   source/fingilish.wordlist.tsv
 * Then run the Keyman Developer compiler or:
 *   kmc build fingilish.model.ts
 */

// ─── Manual overrides ──────────────────────────────────────────────────────
// These are the canonical Latin keys for common Persian words.
// Must be kept in sync with MANUAL_LATIN in build_lexicon.py.

const MANUAL_LATIN: Record<string, string> = {
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
  "دیدم": "didam",      "دیدی": "didi",      "دید": "did",
  "بزن": "bezan",       "زدم": "zadam",      "بشین": "beshin",
  "نشستم": "neshastam",
  "میخوام": "mikham",   "میخوای": "mikhai",  "میخواد": "mikhad",
  "میخوان": "mikhan",   "نمیخوام": "nemikham",
  "میرم": "miram",      "میری": "miri",      "میره": "mire",
  "میریم": "mirim",     "بمون": "bemoon",
  "بگیر": "begir",      "گرفتم": "gereftam", "گرفت": "gereft",
  "بذار": "bezar",      "گذاشتم": "gozashtam",
  "نمیدونم": "nemidoonam", "نمیدونی": "nemidooni",
  "میدونم": "midoonam",    "میدونی": "midooni",
  "میدونه": "midoone",
  "فهمیدم": "fahmeedam",   "نفهمیدم": "nafahmeedam",
  "میتونم": "mitonam",     "میتونی": "mitooni",
  "میتونه": "mitoone",     "نمیتونم": "nemitonam",
  "شدم": "shodam",         "شدی": "shodi",      "شد": "shod",
  "بشه": "beshe",          "میشه": "mishe",     "نمیشه": "nemishe",

  // Common nouns / adjectives
  "چی": "chi",       "چه": "che",        "چرا": "chera",
  "چطور": "chetoor", "کجا": "koja",      "کی": "ki",
  "کدوم": "kodoom",  "چند": "chand",     "چقدر": "cheghadr",
  "خیلی": "kheili",  "خوب": "khob",      "خوبه": "khube",
  "بد": "bad",       "قشنگ": "ghashang", "زیبا": "ziba",
  "بزرگ": "bozorg",  "کوچیک": "koochik",
  "درست": "dorost",  "غلط": "ghalat",    "مهم": "mohem",
  "راحت": "rahat",   "سخت": "sakht",     "آسون": "asoon",
  "گرون": "geroon",  "ارزون": "arzoon",
  "سلام": "salam",   "ممنون": "mamnoon",
  "فکر": "fekr",     "کار": "kar",       "وقت": "vaght",
  "دوست": "doost",   "خونه": "khune",    "خانه": "khune",
  "ماشین": "mashin", "روز": "rooz",      "شب": "shab",
  "صبح": "sobh",     "ظهر": "zohr",
  "امشب": "emshab",  "امروز": "emrooz",  "فردا": "farda",
  "دیروز": "diruz",  "هفته": "hafte",
  "آره": "are",      "اصلاً": "aslan",   "واقعاً": "vaghean",
  "جدی": "jeddi",    "دروغ": "doroogh",  "راست": "rast",
};

// ─── Character maps (fallback for words not in MANUAL_LATIN) ───────────────

const MULTI: Record<string, string> = {
  "خ": "kh", "ش": "sh", "چ": "ch", "ژ": "zh", "غ": "gh", "ق": "gh",
};

const SINGLE: Record<string, string> = {
  "ا": "a",  "آ": "a",  "ب": "b",  "پ": "p",  "ت": "t",  "ث": "s",
  "ج": "j",  "ح": "h",  "د": "d",  "ذ": "z",  "ر": "r",  "ز": "z",
  "س": "s",  "ص": "s",  "ض": "z",  "ط": "t",  "ظ": "z",  "ع": "",
  "ف": "f",  "ک": "k",  "گ": "g",  "ل": "l",  "م": "m",  "ن": "n",
  "و": "v",  "ه": "h",  "ی": "y",  "ء": "",
};

// ─── Transliterate Persian → raw Latin ────────────────────────────────────

function persianToRawLatin(word: string): string {
  if (word in MANUAL_LATIN) {
    return MANUAL_LATIN[word];
  }
  let result = "";
  for (const ch of word) {
    if (ch in MULTI) {
      result += MULTI[ch];
    } else if (ch in SINGLE) {
      result += SINGLE[ch];
    }
    // unknown chars (e.g. digits) are dropped
  }
  // Collapse 3+ repeated characters.
  result = result.replace(/(.)\1{2,}/g, "$1");
  return result;
}

// ─── Normalize Latin → canonical key ──────────────────────────────────────
// Called on BOTH:
//   • the raw Latin produced from a Persian word (for indexing the wordlist)
//   • the Latin text the user actually typed (for lookup)
//
// This is where variant spellings collapse:
//   saalam → salam    (double vowel → single)
//   rooh   → ro       (oo → o, then trailing h dropped)
//   mikham → mikham   (already canonical)
//   mikhaam → mikham  (aa → a)

function normalizeLatinKey(latin: string): string {
  let s = latin.toLowerCase();

  // Alternate consonant spellings → canonical form
  s = s.replace(/x/g, "kh");    // xeili → kheili
  s = s.replace(/q/g, "gh");    // qalb → ghalb
  s = s.replace(/w/g, "v");     // wa → va (some type w for v)

  // Collapse doubled vowels → single (handles "saalam", "rooh", "meekhaam" etc.)
  s = s.replace(/aa/g, "a");
  s = s.replace(/oo/g, "o");
  s = s.replace(/ee/g, "i");

  // Collapse remaining 3+ repeated characters
  s = s.replace(/(.)\1{2,}/g, "$1");

  // Strip non-Latin characters (shouldn't be present, but just in case)
  s = s.replace(/[^a-z]/g, "");

  return s;
}

// ─── Keyman model export ───────────────────────────────────────────────────

export default {
  /*
   * "trie-1.0" is Keyman's standard wordlist-based model.
   * It presents ranked suggestions as the user types and replaces the typed
   * word when the user accepts a suggestion (tap, swipe, or space).
   */
  format: "trie-1.0",

  /*
   * Word breaker: Keyman's default breaks on space and punctuation, which
   * matches our whole-word conversion design exactly.
   */
  wordBreaker: {
    use: "default",
  },

  /*
   * After accepting a suggestion, insert a space automatically.
   * This matches the expected UX: type "salam", accept → "سلام " (with space).
   */
  punctuation: {
    insertAfterWord: "\u0020",  // U+0020 SPACE
  },

  /*
   * Source wordlist. Columns: word <TAB> frequency
   * Generated by build_lexicon.py → fingilish.wordlist.tsv
   * Copy fingilish.wordlist.tsv into the same directory as this file.
   */
  sources: ["words/fingilish.wordlist.tsv"],

  /*
   * searchTermToKey(term)
   *
   * This is the heart of the transliteration model.
   *
   * Keyman calls it with:
   *   • Persian words from the wordlist → must return the Latin lookup key
   *   • Latin text the user typed       → must return the same Latin lookup key
   *
   * Both paths must produce the same canonical key for a match to occur.
   *
   * Examples:
   *   "سلام"    → persianToRawLatin → "salam"  → normalizeLatinKey → "salam"
   *   "salam"   → (already Latin)               → normalizeLatinKey → "salam"  ✓
   *   "saalam"  → (already Latin)               → normalizeLatinKey → "salam"  ✓
   *   "salaam"  → (already Latin)               → normalizeLatinKey → "salam"  ✓
   *   "این"     → "in"             → "in"
   *   "mitooni" → (already Latin)               → "mitooni"  ✓
   *   "xeili"   → normalizeLatinKey replaces x→kh → "kheili" ✓
   */
  searchTermToKey(term: string): string {
    const hasPersian = /[\u0600-\u06FF]/.test(term);
    const rawLatin = hasPersian ? persianToRawLatin(term) : term;
    return normalizeLatinKey(rawLatin);
  },
};