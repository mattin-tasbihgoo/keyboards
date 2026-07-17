#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append names.tsv entries to fingilish.wordlist.tsv (BiDi-wrapped) so the
banner model can suggest them. Idempotent (membership-checked). Frequencies
sit BELOW common corpus words so shared skeleton keys keep word-first
ranking (banner mirror of the converter's word-wins policy):
surnames 60, first names 40, user-reported fixes 80."""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
WL = BASE / "fingilish.wordlist.tsv"
NAMES = BASE / "names.tsv"
RLI, PDI = "\u2067", "\u2069"
BOOST = {"\u0639\u0628\u0627\u0633\u06CC\u0627\u0646", "\u062B\u0631\u06CC\u0627",
         "\u0622\u0645\u0646\u0647", "\u0622\u0648\u0627",
         "\u0641\u0631\u0632\u0627\u062F", "\u0622\u0630\u0631"}

def main():
    have = set()
    for line in WL.open(encoding="utf-8"):
        w = re.sub(r"[\u2066-\u2069]", "", line.split("\t")[0]).strip()
        if w:
            have.add(w)
    added = 0
    with WL.open("a", encoding="utf-8") as out:
        for line in NAMES.open(encoding="utf-8"):
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 4:
                continue
            persian, _variants, kind, _rank = parts
            if persian in have:
                continue
            freq = 80 if persian in BOOST else (60 if kind == "S" else 40)
            out.write(f"{RLI}{persian}{PDI}\t{freq}\n")
            have.add(persian)
            added += 1
    print(f"  wordlist: +{added:,} names appended (now {len(have):,} words)")

if __name__ == "__main__":
    main()
