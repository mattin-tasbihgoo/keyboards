Fingilish (Phonetic Persian) Change History
====================

1.5 (2026-07-13)
----------------
* Emoji key replaces the in-keyboard globe on the bottom row of every layer
  (matching native iOS on Face ID devices); long-press reveals a globe subkey
* Three curated emoji layers (72 emoji, 3 pages x 24), single-codepoint
  Apple-emoji-safe set plus the U+2764 U+FE0F red heart; page nav + ABC return
* Special keys use literal Unicode glyphs (⇧ ⌫ ↵) instead of the SpecialOSK
  symbol font, so they render in SF like native key caps
* No engine changes - conversion behavior identical to 1.3

1.4 (2026-07-12)
----------------
* Touch layout matched to native iOS keyboard geometry (phone platform, both
  `fingilish` and `fingilishlatin`), derived from pixel measurements of device
  screenshots:
  - Letters row 3: shift/backspace w=130 with 25-unit flanking gaps
  - A-row: symmetric half-key spacers (was visually lopsided)
  - Numeric/symbol row 3: ends w=135, punctuation w=145, flanking gaps; fixes
    oversized backspace (row previously summed under the normalization
    threshold, dumping leftover width into the last key)
  - Symbol-switch key labeled `#+=` (was a garbled special glyph); `abc`→`ABC`
  - Bottom row: space 560 / return 270 (native 2.06:1 ratio), uniform gaps
* No engine changes — conversion behavior identical to 1.3

Unreleased (2026-07-07)
----------------
* Repo resynced as single source of truth (shipping `.kmn`s, touch layout, and
  `.kps` were previously Desktop-only and uncommitted)
* Added punctuation conversion triggers (`. , ! ? ; :`; `?` inserts Persian `؟`)
* Added `fingilishlatin.kmn` — pass-through twin keyboard backing the iOS fa/EN toggle
* Conversion engine: new tier-3 vowel-skeleton lookup (16,529 entries) rescuing
  words whose auto-generated keys dropped unwritten short vowels (kardi/kardy/karde)
* `norm()`: `c`→`s`/`k` handling, word-final consonant+`y`→`i`, `eh$`→`e`;
  fallback vowel rules refined (single `a`→ا, initial `aa`→آ, mid `oo`→و, `ee`→ی)
* Pipeline hardening: `build_dict.py` strips BiDi isolates on read (order trap
  dead); dict format now `{exact, skel}`; canonical `build.sh` incl. kvk-collision
  workaround; compiled artifacts removed from `source/`

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
