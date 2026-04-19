#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wrap_bidi.py — Add RTL BiDi isolation to Persian words in the wordlist

This post-processes fingilish.wordlist.tsv to wrap each Persian word with:
  U+2067 (Right-to-Left Isolate) ... U+2069 (Pop Directional Isolate)

This ensures the suggestion banner renders Persian text correctly even when
the banner container inherits LTR direction from the keyboard's &kmw_rtl flag.

Run AFTER build_lexicon.py:
  python build_lexicon.py       # generates fingilish.wordlist.tsv
  python wrap_bidi.py           # wraps Persian words with BiDi chars

The model.ts searchTermToKey strips these characters before processing,
so trie indexing and lookup are unaffected.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

WORDLIST = BASE_DIR / "fingilish.wordlist.tsv"

RLI = "\u2067"  # Right-to-Left Isolate
PDI = "\u2069"  # Pop Directional Isolate


def has_persian(s: str) -> bool:
    """Check if string contains Persian/Arabic script characters."""
    return any("\u0600" <= ch <= "\u06FF" for ch in s)


def already_wrapped(s: str) -> bool:
    """Check if string is already wrapped with BiDi isolation chars."""
    return s.startswith(RLI) and s.endswith(PDI)


def main():
    if not WORDLIST.exists():
        print(f"ERROR: {WORDLIST} not found. Run build_lexicon.py first.")
        return

    lines = WORDLIST.read_text(encoding="utf-8").splitlines()
    out_lines = []
    wrapped_count = 0
    skipped_count = 0

    for line in lines:
        if not line.strip():
            out_lines.append(line)
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            out_lines.append(line)
            continue

        word = parts[0]

        if has_persian(word) and not already_wrapped(word):
            parts[0] = RLI + word + PDI
            wrapped_count += 1
        else:
            skipped_count += 1

        out_lines.append("\t".join(parts))

    WORDLIST.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    print(f"BiDi wrap complete:")
    print(f"  Wrapped: {wrapped_count} Persian entries")
    print(f"  Skipped: {skipped_count} (already wrapped or non-Persian)")
    print(f"  Output:  {WORDLIST}")


if __name__ == "__main__":
    main()
