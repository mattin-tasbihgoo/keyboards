#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_names.py — Generate names.tsv (bulk Persian name lexicon) from external
datasets. The RAW datasets live OUTSIDE the repo (~/Documents/Fingilish/namedata);
only the generated names.tsv is committed, so builds are reproducible without
redistributing the sources.

Sources & licenses (attribution also in README):
  - persian-gender-by-name.csv   (HuggingFace farbodbij/..., Apache-2.0)
      26,680 rows: persian,gender,english  — PAIRED human romanizations
  - iranian-surname-frequencies.csv (GitHub farbodbj/..., Apache-2.0)
      101,000 rows: persian,frequency,english — english col PARTIALLY DIRTY
      (mixed-script rows); every english value is ASCII-validated, with
      fallback to our own transliterator.

Output: names.tsv   columns: persian \t comma-joined-latin-variants \t kind \t rank
  kind: F (first name) | S (surname)
  rank: surname frequency rank (1-based) or 0 for first names

Policy decisions (2026-07-17, confirmed by Mattin):
  - Surname cutoff: top 10,000 by frequency (73.1% coverage; knee analysis)
  - Bulk names NEVER displace existing word keys (word-wins). Enforced in
    build_dict.py at merge time, not here.
"""
import csv
import re
import unicodedata
from pathlib import Path

from build_dict import transliterate_for_dict, norm

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path.home() / "Documents" / "Fingilish" / "namedata"
OUT = BASE_DIR / "names.tsv"

SURNAME_TOP_N = 10000

PERSIAN_RE = re.compile(r'^[\u0600-\u06FF\u200c]+$')
LATIN_RE = re.compile(r"^[a-z']+$")


def clean_persian(p):
    p = unicodedata.normalize("NFC", p.strip())
    # Arabic -> Persian codepoint normalization (match pipeline conventions)
    p = p.replace('\u064A', '\u06CC').replace('\u0643', '\u06A9')
    if ' ' in p or not PERSIAN_RE.match(p):
        return None
    if len(p) < 2 or len(p) > 14:
        return None
    return p


def clean_latin(l):
    l = l.strip().lower().replace('\u2019', "'").replace('-', '')
    if not LATIN_RE.match(l):
        return None
    if len(l) < 2 or len(l) > 20:
        return None
    return l


def main():
    entries = []   # (persian, [variants], kind, rank)

    # ---------- Surnames (freq-ranked; processed first = higher priority) ----------
    sur_path = DATA_DIR / "iranian-surname-frequencies.csv"
    n_dirty_eng = 0
    with sur_path.open(encoding="utf-8") as f:
        for rank, row in enumerate(csv.DictReader(f), 1):
            if rank > SURNAME_TOP_N:
                break
            persian = clean_persian(row["name"])
            if not persian:
                continue
            variants = []
            eng = clean_latin(row.get("name_english", ""))
            if eng:
                variants.append(eng)
            else:
                n_dirty_eng += 1
            gen = transliterate_for_dict(persian)
            if gen and gen != "?" and LATIN_RE.match(gen) and gen not in variants:
                variants.append(gen)
            if variants:
                entries.append((persian, variants, "S", rank))

    # ---------- First names (paired romanizations; dataset order) ----------
    fn_path = DATA_DIR / "persian-gender-by-name.csv"
    with fn_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            persian = clean_persian(row["name"])
            latin = clean_latin(row["english_name"])
            if not persian or not latin:
                continue
            entries.append((persian, [latin], "F", 0))

    # ---------- Merge variants per Persian word, preserve first-seen order ----------
    merged = {}
    order = []
    for persian, variants, kind, rank in entries:
        if persian not in merged:
            merged[persian] = {"variants": [], "kind": kind, "rank": rank}
            order.append(persian)
        m = merged[persian]
        for v in variants:
            if v not in m["variants"]:
                m["variants"].append(v)

    with OUT.open("w", encoding="utf-8") as f:
        for persian in order:
            m = merged[persian]
            f.write(f"{persian}\t{','.join(m['variants'])}\t{m['kind']}\t{m['rank']}\n")

    n_s = sum(1 for p in order if merged[p]["kind"] == "S")
    n_f = len(order) - n_s
    print(f"names.tsv: {len(order):,} entries ({n_s:,} surnames + {n_f:,} first names)")
    print(f"  dirty english fields replaced by generated keys: {n_dirty_eng:,}")
    print(f"  size: {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
