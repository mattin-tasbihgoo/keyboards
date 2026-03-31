# Architecting a Fingilish keyboard on Keyman

**The best architecture for a Keyman Fingilish keyboard is a hybrid: a pass-through `.kmn` keyboard using `call()` with embedded JavaScript (`.call_js`) for spacebar-triggered dictionary lookup and conversion, paired with a `custom-1.0` lexical model that provides ranked Persian suggestions on mobile.** This mirrors how Keyman's existing Chinese, Japanese, and Korean keyboards already handle dictionary-based IME conversion. The three problems — scaling beyond hundreds of rules, RTL banner rendering, and unknown-word fallback — each have viable solutions within Keyman's current architecture, though some require workarounds for platform gaps.

## The `custom-1.0` model unlocks dictionary-based transliteration

Keyman's `custom-1.0` lexical model format is the key architectural enabler. Unlike `trie-1.0` (which only does prefix matching on a static wordlist), `custom-1.0` lets you write **arbitrary TypeScript/JavaScript** in a `predict()` function. This function receives the user's current context and keystroke, and returns a ranked list of suggestions — each with a `transform` that can delete the Latin input and insert Persian output:

```typescript
predict(transform, context): Distribution<Suggestion> {
  // Extract current Latin word from context.left
  // Look up in dictionary → return Persian candidates
  // Fall back to algorithmic transliteration for unknown words
  return [{
    p: 0.9,
    sample: {
      displayAs: 'سلام',
      transform: { deleteLeft: 5, insert: 'سلام' }
    }
  }];
}
```

The model runs in a Web Worker and can contain an embedded dictionary, character mapping tables, and any transliteration logic you need. **One critical caveat**: `custom-1.0` compilation was broken in Keyman Developer until version **18.0.249** (bug #15778, fixed March 2026). Earlier versions had the format defined but the compiler failed to produce working models. Confirm you're using 18.0.249 or later.

The `trie-1.0` model's `searchTermToKey` function was suggested by Keyman developer Joshua Horton as a partial workaround — you could write a function mapping both Persian wordlist entries and Latin input to a common normalized key. But this is brittle for cross-script use. The `custom-1.0` approach is architecturally superior because your `predict()` function has full control over the lookup logic.

## Why `call()` with JavaScript solves the auto-accept gap

The biggest limitation of relying solely on the lexical model is that **Keyman has no auto-accept mechanism** — users must manually tap a suggestion from the banner. The Keyman roadmap (March 2026) lists "autocorrect: Automatically accept high-probability suggestions" as a planned future feature, confirming this gap exists today. The suggestion banner itself is **mobile/touch only**; desktop Keyman does not display lexical model predictions at all.

The solution is Keyman's `call()` statement with `.call_js` files. On web and mobile platforms, a `.kmn` rule can invoke JavaScript on spacebar:

```
store(ConvertWord) "fingilish.dll:ConvertWord"
' ' + [K_SPACE] > call(ConvertWord)
```

The compiler ignores the DLL name on web/mobile and instead looks for `ConvertWord.call_js` — a JavaScript file embedded into the compiled keyboard. This JavaScript function **can read the current context and modify the text buffer**, exactly like the DLL's `KMSetOutput()` and `KMQueueAction()`. Chinese (`chinese-1.0.js`), Japanese (`japanese-1.0.js`), and Korean (`korean_rr-1.1.js`) keyboards already use this IMX mechanism in production for dictionary-based conversion.

Your `.call_js` function would:

- Read the preceding Latin characters from the context buffer
- Look up the word in an embedded Fingilish→Persian dictionary (a JSON object mapping normalized Latin forms to Persian, with variant handling)
- If found, delete the Latin text and insert the Persian equivalent
- If not found, apply character-level transliteration rules as fallback
- Insert a space after the converted word

This eliminates the need for hundreds of `.kmn` rules. The dictionary lives in JavaScript, is easily maintainable, and can handle **thousands of words** plus spelling variants through normalization (stripping double vowels, mapping `x`→`kh`, `ou`→`u`, etc.) before lookup.

**Important limitation**: the `.call_js` approach works on web, Android, and iOS — but on **desktop Windows**, `call()` invokes an actual DLL. For desktop, you would need either a compiled DLL implementing the same logic, or a fallback set of `.kmn` rules for the most common words. Cross-platform IMX support is planned for Keyman v19 but is not yet available.

## The RTL banner problem is a configuration mismatch, likely a bug

The reversed Persian text in the suggestion banner stems from a fundamental architectural mismatch: **the banner inherits its text direction from the keyboard's `&kmw_rtl` flag, not from the lexical model's content**. A Fingilish keyboard naturally sets `&kmw_rtl` to false (since its key layout is Latin/LTR), but its lexical model outputs RTL Persian text. The banner renders the Persian suggestions in an LTR container, visually reversing the character order.

Keyman has two separate RTL flags that should theoretically address this. The keyboard-level `store(&kmw_rtl) '1'` controls the on-screen keyboard direction. The lexical model's `isRTL` property (added in PR #4559, March 2021) marks the model as right-to-left. However, **no existing Keyman keyboard matches this exact scenario** — Latin input with RTL output — so the interaction between these flags in the suggestion banner has likely never been tested.

Try these fixes in order:

- **Set `isRTL: true`** in your `.model.ts` lexical model definition (via the Lexical Model Editor checkbox or the source file directly). This is the architecturally correct setting.
- **If that fails, set `store(&kmw_rtl) '1'`** in the `.kmn` file. This may fix the banner but will also make the on-screen keyboard layout RTL, which is undesirable for Latin input keys.
- **If both fail, wrap suggestion text** in Unicode BiDi isolation characters — use **U+2067** (Right-to-Left Isolate) at the start and **U+2069** (Pop Directional Isolate) at the end of each `displayAs` string in your custom model's suggestions. These are stronger than RLM (U+200F) and explicitly isolate the directional context.
- **File a bug** at github.com/keymanapp/keyman with title: "Suggestion banner does not respect lexical model isRTL when keyboard is LTR." This appears to be an unreported edge case. No existing GitHub issue matches this specific scenario.

## Dictionary-plus-fallback handles unknown words

The standard IME architecture pattern — used by Google Input Tools, ibus-typing-booster, and every major Fingilish converter — is **dictionary lookup as primary, character-level transliteration as fallback**. Your `custom-1.0` model's `predict()` function (and your `.call_js` conversion function) should implement both tiers.

For the dictionary tier, build a comprehensive Fingilish→Persian mapping with **normalized keys**. Strip double vowels, collapse common variants, and map to a canonical form before lookup. For example, "salam", "salaam", and "salâm" all normalize to "slm" → سلام. The IROpen/fingilish project demonstrates this pattern effectively in JavaScript. Multiple open-source Fingilish dictionaries exist (elektito/finglish with confidence scores, masihyeganeh/ConvertFinglishToFarsi with extensive variant mappings) that can seed your wordlist.

For the algorithmic fallback tier, implement a character/digraph mapping table that handles any arbitrary input. The standard Fingilish mappings are well-established:

- **Unambiguous digraphs** (handle first, longest-match): `sh`→ش, `ch`→چ, `zh`→ژ, `kh`→خ, `gh`→غ
- **Ambiguous consonants** (default to most common): `s`→س, `z`→ز, `t`→ت, `h`→ه, `q`→ق
- **Vowels**: `a`→َ (or ا in word-initial), `e`→ِ, `o`→ُ, `i`/`y`→ی, `u`/`oo`→و, `aa`/`â`→آ

Persian's inherent ambiguity (e.g., `s` could be س, ث, or ص) means the fallback will sometimes produce incorrect spellings for unknown words. This is acceptable — the dictionary tier handles common words correctly, and the fallback provides a reasonable approximation for names and novel words. The `custom-1.0` model can return **multiple candidates** ranked by probability, letting users select alternatives from the suggestion banner.

## Recommended architecture: the three-layer approach

Evaluating the four options from the original question:

**Option A (current approach — hundreds of .kmn rules)** is unsustainable. It cannot handle variants, unknown words, or scale beyond a few hundred common words. Reject.

**Option B (everything in custom-1.0 lexical model)** is architecturally clean but has a fatal UX flaw: no auto-accept on space, and the suggestion banner doesn't exist on desktop. Users must tap each suggestion manually. Insufficient as the sole mechanism.

**Option D (existing Keyman patterns)** shows that CJK keyboards use `call()` with IMX for exactly this conversion pattern. This validates the hybrid approach.

**The best architecture is a refined version of Option C** — a three-layer hybrid:

**Layer 1 — The `.kmn` keyboard** does minimal work. It passes through Latin keystrokes as-is (the user sees Latin text while typing). On spacebar or enter, it triggers `call(ConvertWord)` which invokes the `.call_js` JavaScript engine. For desktop fallback where `.call_js` doesn't work, include a small set of `.kmn` rules for the **50–100 most common words** (سلام، خوبی، چطوری, etc.).

**Layer 2 — The `.call_js` conversion engine** (JavaScript, embedded in the keyboard) contains the full Fingilish→Persian dictionary plus the algorithmic fallback. On spacebar, it reads the Latin word from context, runs dictionary lookup with normalization, falls back to character-level mapping for unknown words, deletes the Latin text, and inserts Persian. This gives the seamless "type salam + space → سلام" experience on web and mobile platforms.

**Layer 3 — The `custom-1.0` lexical model** provides the suggestion banner on mobile with ranked alternatives. Its `predict()` function implements the same dictionary + fallback logic as the `.call_js` engine (ideally sharing the same dictionary data). This lets users see and select alternative transliterations when the auto-conversion picks the wrong candidate.

This three-layer architecture cleanly separates concerns: the keyboard handles input and triggers conversion, the JavaScript engine handles the core transliteration logic, and the lexical model provides the suggestion UI. It mirrors how mature IME systems (Google Input Tools, ibus-typing-booster, Windows Pinyin) separate their candidate engines from their UI layers.

## Practical implementation path

Start with the `custom-1.0` lexical model, since it provides immediate value on mobile and validates your dictionary/transliteration logic in TypeScript. Ensure you're using **Keyman Developer 18.0.249+** for working `custom-1.0` compilation. Structure the model's `predict()` function with the two-tier lookup (dictionary → algorithmic fallback) and test it against your existing wordlist.

Next, extract the core transliteration logic into a standalone `.call_js` file and wire it into the `.kmn` keyboard via `call()` on spacebar. Test on KeymanWeb first (easiest debugging), then Android and iOS. For the dictionary data, convert your existing `fingilish.wordlist.tsv` into a JavaScript object keyed by normalized Latin forms, and embed it in both the `.call_js` file and the custom model sources.

For the RTL banner, test the `isRTL` model flag first. If it doesn't work, use BiDi isolation characters in `displayAs`. File the GitHub issue regardless — this is a gap the Keyman team should address for any future Latin-input/RTL-output keyboards.

Keep a minimal set of `.kmn` rules (50–100 top words) as a desktop fallback until Keyman v19 delivers cross-platform IMX support. This hybrid ensures the keyboard works everywhere, even if the full JavaScript engine isn't available on all platforms.

## Conclusion

The Keyman platform was not originally designed for IME-style transliteration keyboards, but its existing infrastructure — `custom-1.0` models for suggestion generation and `call()` with `.call_js` for programmatic text manipulation — provides the building blocks needed. The **key architectural insight** is that CJK keyboards on Keyman already solve the same fundamental problem (accumulate phonetic input, convert to target script via dictionary lookup on commit). Your Fingilish keyboard should follow this proven pattern rather than scaling up `.kmn` rules.

Three specific gaps remain in Keyman: no auto-accept for high-confidence suggestions (on the roadmap), no suggestion banner on desktop (feature request #2005, still unresolved), and no documented handling of mixed LTR-keyboard/RTL-output scenarios for the banner. The `call()` + `.call_js` approach works around the first two gaps today, and BiDi isolation characters or a bug fix should resolve the third. Watch for Keyman v19's cross-platform IMX support, which would eventually let you consolidate the JavaScript and DLL codepaths into a single engine.