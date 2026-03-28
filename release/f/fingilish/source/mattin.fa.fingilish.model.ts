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

    // Manual overrides: common Persian words → canonical Latin key
    const MANUAL: Record<string, string> = {
      "که":"ke",
      "رو":"ro",
      "به":"be",
      "من":"man",
      "و":"o",
      "از":"az",
      "تو":"to",
      "اون":"oon",
      "این":"in",
      "یه":"ye",
      "می":"mi",
      "نه":"na",
      "با":"ba",
      "در":"dar",
      "ما":"ma",
      "هم":"ham",
      "بود":"bood",
      "تا":"ta",
      "اگه":"age",
      "همه":"hame",
      "هر":"har",
      "اما":"ama",
      "یا":"ya",
      "چون":"chon",
      "پس":"pas",
      "دیگه":"dige",
      "فقط":"faghat",
      "خب":"khob",
      "اینجا":"inja",
      "الان":"alan",
      "شاید":"shayad",
      "باید":"bayad",
      "باشه":"bashe",
      "کن":"kon",
      "کنم":"konam",
      "کنی":"koni",
      "کنه":"kone",
      "کنیم":"konim",
      "میکنم":"mikonam",
      "میکنی":"mikoni",
      "میکنه":"mikone",
      "بده":"bede",
      "داری":"dari",
      "داره":"dare",
      "دارم":"daram",
      "بیا":"bia",
      "بریم":"berim",
      "برو":"boro",
      "رفتم":"raftam",
      "رفت":"raft",
      "بگو":"bego",
      "گفتم":"goftam",
      "گفت":"goft",
      "ببین":"bebin",
      "دیدم":"didam",
      "بزن":"bezan",
      "بشین":"beshin",
      "میخوام":"mikham",
      "نمیخوام":"nemikham",
      "میرم":"miram",
      "میری":"miri",
      "میره":"mire",
      "بمون":"bemoon",
      "بگیر":"begir",
      "گرفتم":"gereftam",
      "گرفت":"gereft",
      "بذار":"bezar",
      "نمیدونم":"nemidoonam",
      "میدونم":"midoonam",
      "میدونی":"midooni",
      "میتونم":"mitonam",
      "میتونی":"mitooni",
      "نمیتونم":"nemitonam",
      "شدم":"shodam",
      "شد":"shod",
      "بشه":"beshe",
      "میشه":"mishe",
      "نمیشه":"nemishe",
      "چی":"chi",
      "چه":"che",
      "چرا":"chera",
      "چطور":"chetoor",
      "کجا":"koja",
      "کی":"ki",
      "کدوم":"kodoom",
      "چند":"chand",
      "خیلی":"kheili",
      "خوب":"khob",
      "خوبه":"khube",
      "سلام":"salam",
      "ممنون":"mamnoon",
      "دوست":"doost",
      "خونه":"khune",
      "ماشین":"mashin",
      "روز":"rooz",
      "شب":"shab",
      "امروز":"emrooz",
      "فردا":"farda",
      "آره":"are",
      "خوشبختم":"khoshbakhtam"
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
    const hasPersian = /[؀-ۿ]/.test(term);
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
        raw = raw.replace(/(.){2,}/g, "$1");
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
    key = key.replace(/(.){2,}/g, "$1");
    key = key.replace(/[^a-z]/g, "");
    return key;
  },
};

export default source;