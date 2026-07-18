Fingilish (Phonetic Persian) Change History
====================

2.0 (2026-07-17)
----------------
* BANNER REBUILT on custom-1.0 (Stage 4): predict() performs direct
  dictionary lookup using the converter's OWN generated functions and data
  (fng_model_fns.js extracted verbatim from ConvertWord.call_js;
  fng_model_data.js = the converter dictionary + ranked alternates) — one
  brain for banner and conversion, deterministic, all 22k names included
* The literal transliteration is always offered when it differs from the
  dictionary answer, so the banner shows exactly what you are spelling
* Ranked alternates: surname-frequency collisions + curated MANUAL_ALTS
  (azar shows the word first, the name one tap away)
* New gate: test_custom_model.mjs runs the predict() battery (19 cases:
  correctness, determinism, transform mechanics, live partial-word preview,
  empty/Persian-context guards) against the COMPILED model artifact

1.9 (2026-07-17)
----------------
* REVERT the 1.8 banner/model changes (searchTermToKey + wordlist names):
  skeleton keys violate trie-1.0 prefix-monotonicity (doc-04 L6) — incremental
  search corrupted, banner showed correction noise / dropped targets / went
  empty. Banner returns to 1.7 behavior; converter (names, H8, aa-intent,
  regex) fully retained. custom-1.0 migration is the successor.

1.8 (2026-07-17)
----------------
* Banner/model interim fix (doc-04 L3/L4): searchTermToKey regenerated from
  build_dict source by new gen_model_key.py — Persian-index and typed-query
  paths now both produce converter-tier-3 skeleton keys (104,800-case
  differential proof gates the build; 36-key hand mirror removed)
* Name lexicon appended to the banner wordlist (+19,619 entries, 42,123
  total) at sub-word frequencies so shared keys keep word-first ranking
* New build gates: gen_model_key.py differential proof + test_model_keys.mjs
  typed<->Persian key-equality battery (16 pairs incl. all reported names)

1.7 (2026-07-17)
----------------
* Names overhaul: bulk name lexicon (22,153 entries) generated from two
  Apache-2.0 datasets (persian-gender-by-name, iranian-surname-frequencies)
  via new build_names.py; word-wins collision policy (names never displace
  existing word keys); curated fixes for user-reported names (Abbasian,
  Soraya, Ameneh, Ava, Farzad, Azar-the-name via aazar)
* Token regex accepts leading apostrophe / Arabizi 2/3, so 'abbas and 3ali
  convert with correct initial ayn/hamza
* Explicit "aa" start is treated as long-A letterform intent: aa-variant
  dictionary keys emitted for ALEF-MADDA and AYN+ALEF words (aali, aadi,
  aashegh, aameneh...), and runtime skips norm/skel collapse for aa- words
* transliterate_for_dict: word-initial ayn now emits 'a' (abasi not basi);
  fixes unreachable words (aali) and improves all ayn-initial name keys
* Fallback transliteration upgraded to the H8 heuristic (chosen by new
  eval_translit.mjs harness over 33k human-romanized pairs: 29.5% vs 25.2%
  exact match): last-vowel alef, -an/-ani alef, surname suffix table
  (-ian/-zadeh/-pour/-nejad/-abadi/-vand/-lou/-khah/-far), other medial
  short 'a' unwritten
* Tests: dict verification 142 cases, e2e harness 72 cases (both gate build.sh)

1.6 (2026-07-15)
----------------
* Exact-tier shadowing fix (bale class): ~40 MANUAL entries + displacement
  guards; model.ts mirrors 36 keys; tests 75->128 (dict) and 29->47 (e2e)

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
