Fingilish (Phonetic Persian) Change History
====================

1.1 (2026-04-18)
----------------
* Fixed RTL suggestion banner rendering: `isRTL: true` in the lexical model plus BiDi
  isolation characters (U+2067 RLI / U+2069 PDI) wrapped around every Persian wordlist
  entry via `wrap_bidi.py`; `searchTermToKey` strips them before lookup
* Improved lexical model: expanded MANUAL Persian→Latin override table for
  high-frequency function words and colloquial verb forms
* Expanded generated dictionary to ~28,000 entries (MANUAL + NAMES + auto-transliterated
  frequency wordlist)

1.0 (2026-03-30)
----------------
* First working hybrid IME build
* Replaced 500+ individual `.kmn` word rules with a Latin pass-through keyboard that
  triggers `call(ConvertWord)` on space/enter
* Added generated `ConvertWord.call_js` conversion engine: dictionary lookup with
  `norm()` variant collapse, plus character-level algorithmic transliteration fallback
  for unknown words
* Added `trie-1.0` lexical model (`mattin.fa.fingilish.model.ts`) driving the mobile
  suggestion banner from a ~22,500-entry Persian frequency wordlist
* Added data pipeline: `build_lexicon.py`, `build_dict.py`, `build_calljs.py`,
  `wrap_bidi.py`

0.1 (2026-01-04)
----------------
* Project scaffold created from the US Basic keyboard template
