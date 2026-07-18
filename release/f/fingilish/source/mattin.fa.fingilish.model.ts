/*
  Fingilish lexical model — custom-1.0 (Stage 4, 2026-07-17).

  The trie-1.0 era is over: its incremental search requires a
  prefix-monotonic searchTermToKey, and bridging Persian's unwritten short
  vowels requires a non-monotonic key (doc-04 L6) — structurally
  incompatible. This model instead performs direct dictionary lookup in
  predict() using the CONVERTER'S OWN generated functions and data:

    fng_model_data.js — FNG_DICT (exact+skel) + FNG_ALTS (ranked alternates)
    fng_model_fns.js  — norm/skel/translit, verbatim from ConvertWord.call_js
    fng_model_impl.ts — the FingilishModel class (predict/configure/wordbreak)

  All three are generated/owned by the words/ pipeline (model_emit.py);
  the compiled artifact is gated by test_custom_model.mjs in build.sh.
*/
const source: LexicalModelSource = {
  format: "custom-1.0",
  isRTL: true,
  rootClass: "FingilishModel",
  sources: ["fng_model_data.js", "fng_model_fns.js", "fng_model_impl.ts"],
};
export default source;
