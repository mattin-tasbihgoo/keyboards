#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build the Fingilish lexicon for Keyman.

Inputs:  words_raw.csv, sentences_raw.csv  (same folder as this script)
Outputs: fingilish.wordlist.tsv  — Persian word + freq, consumed by Keyman model
         lexicon.tsv             — Persian/Latin review file
         blocklist.txt
"""

from __future__ import annotations
import csv, re
from collections import Counter
from pathlib import Path

BASE_DIR      = Path(__file__).resolve().parent
WORDS_RAW     = BASE_DIR / "words_raw.csv"
SENTENCES_RAW = BASE_DIR / "sentences_raw.csv"
WORDLIST      = BASE_DIR / "fingilish.wordlist.tsv"
LEXICON       = BASE_DIR / "lexicon.tsv"
BLOCKLIST     = BASE_DIR / "blocklist.txt"

ARABIC_TO_PERSIAN = str.maketrans({
    "\u064a": "\u06cc", "\u0643": "\u06a9", "\u0629": "\u0647",
    "\u06c0": "\u0647", "\u0623": "\u0627", "\u0625": "\u0627",
    "\u0649": "\u06cc",
})
COMBINING_RE    = re.compile(r"[\u0640\u064B-\u065F\u0670\u06D6-\u06ED]")
SPACE_PUNCT_RE  = re.compile(r"\s+([؟!،\.,:;])")
MULTISPACE_RE   = re.compile(r"\s+")
PERSIAN_WORD_RE = re.compile(r"^[\u0600-\u06FF]+$")
TOKEN_RE        = re.compile(r"[\u0600-\u06FF]+")

def normalize(text):
    if not text: return ""
    text = text.strip().translate(ARABIC_TO_PERSIAN)
    text = COMBINING_RE.sub("", text)
    text = SPACE_PUNCT_RE.sub(r"\1", text)
    return MULTISPACE_RE.sub(" ", text).strip()

def is_persian(word):
    return bool(word and PERSIAN_WORD_RE.fullmatch(word))

def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write_tsv(path, headers, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(headers)
        w.writerows(rows)

MULTI = {"\u062e":"kh","\u0634":"sh","\u0686":"ch","\u0698":"zh","\u063a":"gh","\u0642":"gh"}
SINGLE = {
    "\u0627":"a","\u0622":"a","\u0628":"b","\u067e":"p","\u062a":"t","\u062b":"s",
    "\u062c":"j","\u062d":"h","\u062f":"d","\u0630":"z","\u0631":"r","\u0632":"z",
    "\u0633":"s","\u0635":"s","\u0636":"z","\u0637":"t","\u0638":"z","\u0639":"",
    "\u0641":"f","\u06a9":"k","\u06af":"g","\u0644":"l","\u0645":"m","\u0646":"n",
    "\u0648":"v","\u0647":"h","\u06cc":"y","\u0621":"",
}
MANUAL = {
    "\u06a9\u0647":"ke","\u0631\u0648":"ro","\u0628\u0647":"be","\u0645\u0646":"man",
    "\u0648":"o","\u0627\u0632":"az","\u062a\u0648":"to",
    "\u0627\u0648\u0646":"oon","\u0627\u06cc\u0646":"in","\u06cc\u0647":"ye",
    "\u0645\u06cc":"mi","\u0646\u0647":"na","\u0628\u0627":"ba","\u062f\u0631":"dar",
    "\u0645\u0627":"ma","\u0647\u0645":"ham","\u0628\u0648\u062f":"bood","\u062a\u0627":"ta",
    "\u0627\u06af\u0647":"age","\u0647\u0645\u0647":"hame","\u0647\u0631":"har",
    "\u0627\u0645\u0627":"ama","\u06cc\u0627":"ya","\u0686\u0648\u0646":"chon",
    "\u067e\u0633":"pas","\u062f\u06cc\u06af\u0647":"dige","\u0647\u0646\u0648\u0632":"hanooz",
    "\u062d\u0627\u0644\u0627":"hala","\u0641\u0642\u0637":"faghat","\u062e\u0628":"khob",
    "\u0627\u06cc\u0646\u062c\u0627":"inja","\u0627\u0648\u0646\u062c\u0627":"onja",
    "\u0627\u0644\u0627\u0646":"alan","\u0634\u0627\u06cc\u062f":"shayad",
    "\u0628\u0627\u06cc\u062f":"bayad","\u0628\u0627\u0634\u0647":"bashe",
    "\u06a9\u0646":"kon","\u06a9\u0646\u0645":"konam","\u06a9\u0646\u06cc":"koni",
    "\u06a9\u0646\u0647":"kone","\u06a9\u0646\u06cc\u0645":"konim",
    "\u0645\u06cc\u06a9\u0646\u0645":"mikonam","\u0645\u06cc\u06a9\u0646\u06cc":"mikoni",
    "\u0645\u06cc\u06a9\u0646\u0647":"mikone","\u0628\u062f\u0647":"bede",
    "\u0645\u06cc\u062f\u0647":"mide","\u062f\u0627\u062f":"dad",
    "\u062f\u0627\u0631\u06cc":"dari","\u062f\u0627\u0631\u0647":"dare",
    "\u062f\u0627\u0631\u0645":"daram","\u0628\u06cc\u0627":"bia",
    "\u0628\u0631\u06cc\u0645":"berim","\u0628\u0631\u0648":"boro",
    "\u0631\u0641\u062a\u0645":"raftam","\u0631\u0641\u062a":"raft",
    "\u0628\u06af\u0648":"bego","\u06af\u0641\u062a\u0645":"goftam",
    "\u06af\u0641\u062a":"goft","\u0628\u0628\u06cc\u0646":"bebin",
    "\u062f\u06cc\u062f\u0645":"didam","\u0628\u0632\u0646":"bezan",
    "\u0628\u0634\u06cc\u0646":"beshin",
    "\u0645\u06cc\u062e\u0648\u0627\u0645":"mikham","\u0645\u06cc\u062e\u0648\u0627\u062f":"mikhad",
    "\u0646\u0645\u06cc\u062e\u0648\u0627\u0645":"nemikham",
    "\u0645\u06cc\u0631\u0645":"miram","\u0645\u06cc\u0631\u06cc":"miri","\u0645\u06cc\u0631\u0647":"mire",
    "\u0628\u0645\u0648\u0646":"bemoon","\u0628\u06af\u06cc\u0631":"begir",
    "\u06af\u0631\u0641\u062a\u0645":"gereftam","\u06af\u0631\u0641\u062a":"gereft",
    "\u0628\u0630\u0627\u0631":"bezar",
    "\u0646\u0645\u06cc\u062f\u0648\u0646\u0645":"nemidoonam",
    "\u0645\u06cc\u062f\u0648\u0646\u0645":"midoonam","\u0645\u06cc\u062f\u0648\u0646\u06cc":"midooni",
    "\u0645\u06cc\u062a\u0648\u0646\u0645":"mitonam","\u0645\u06cc\u062a\u0648\u0646\u06cc":"mitooni",
    "\u0646\u0645\u06cc\u062a\u0648\u0646\u0645":"nemitonam",
    "\u0634\u062f\u0645":"shodam","\u0634\u062f":"shod",
    "\u0628\u0634\u0647":"beshe","\u0645\u06cc\u0634\u0647":"mishe","\u0646\u0645\u06cc\u0634\u0647":"nemishe",
    "\u0686\u06cc":"chi","\u0686\u0647":"che","\u0686\u0631\u0627":"chera",
    "\u0686\u0637\u0648\u0631":"chetoor","\u06a9\u062c\u0627":"koja","\u06a9\u06cc":"ki",
    "\u06a9\u062f\u0648\u0645":"kodoom","\u0686\u0646\u062f":"chand",
    "\u062e\u06cc\u0644\u06cc":"kheili","\u062e\u0648\u0628":"khob","\u062e\u0648\u0628\u0647":"khube",
    "\u0633\u0644\u0627\u0645":"salam","\u0645\u0645\u0646\u0648\u0646":"mamnoon",
    "\u062f\u0648\u0633\u062a":"doost","\u062e\u0648\u0646\u0647":"khune",
    "\u0645\u0627\u0634\u06cc\u0646":"mashin","\u0631\u0648\u0632":"rooz",
    "\u0634\u0628":"shab","\u0627\u0645\u0631\u0648\u0632":"emrooz","\u0641\u0631\u062f\u0627":"farda",
    "\u0622\u0631\u0647":"are","\u062e\u0648\u0634\u0628\u062e\u062a\u0645":"khoshbakhtam",
}

def transliterate(word):
    if word in MANUAL: return MANUAL[word]
    result = ""
    for ch in word:
        if ch in MULTI: result += MULTI[ch]
        elif ch in SINGLE: result += SINGLE[ch]
    result = re.sub(r"(.)\1{2,}", r"\1", result)
    return result.strip() or "?"

def load_counts():
    wc = Counter()
    for row in read_csv(WORDS_RAW):
        w = normalize(row.get("word",""))
        if not is_persian(w): continue
        try: wc[w] += int(row.get("count",0))
        except: pass
    sc = Counter()
    for row in read_csv(SENTENCES_RAW):
        s = normalize(row.get("sentence",""))
        try: freq = int(row.get("count",0))
        except: continue
        for tok in TOKEN_RE.findall(s):
            w = normalize(tok)
            if is_persian(w): sc[w] += freq
    all_words = set(wc)|set(sc)
    merged = [(w, wc.get(w,0)+sc.get(w,0)) for w in all_words]
    merged.sort(key=lambda x: (-x[1], x[0]))
    return merged

def main():
    merged = load_counts()
    print(f"  {len(merged):,} unique Persian words")

    # Persian wordlist — word is Persian, kmc embeds it, searchTermToKey converts to Latin
    rows = [(p, f) for p, f in merged if transliterate(p) != "?"]
    rows.sort(key=lambda x: -x[1])
    with WORDLIST.open("w", encoding="utf-8", newline="") as f:
        for persian, freq in rows:
            f.write(f"{persian}\t{freq}\n")
    print(f"  Wrote {len(rows):,} entries -> {WORDLIST.name}")

    # Human review lexicon
    lex = [[p, f, transliterate(p)] for p, f in merged]
    lex.sort(key=lambda x: -x[1])
    write_tsv(LEXICON, ["persian","freq","latin"], lex)
    print(f"  Wrote {len(lex):,} entries -> {LEXICON.name}")

    # Blocklist
    blocked = sorted(["in","to","man","dar","bar","be","on","no","as",
        "are","has","had","not","she","his","her","was","can","did","get",
        "got","him","how","its","may","our","out","set","say","use","way",
        "who","why","do","go","me","my","by","am","an","at","if","is",
        "it","of","or","so","up","us"])
    with BLOCKLIST.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(blocked)+"\n")
    print(f"  Wrote {len(blocked)} entries -> {BLOCKLIST.name}")

    # Verify key lookups
    print("\nVerification:")
    tests = ["salam","in","ye","oon","mitooni","kheili","bayad","koja","bebin","bego"]
    from collections import defaultdict
    lookup = defaultdict(list)
    for p,f in merged:
        l = transliterate(p)
        if l != "?": lookup[l].append((p,f))
    for t in tests:
        matches = sorted(lookup.get(t,[]), key=lambda x:-x[1])[:1]
        if matches: print(f"  {t:<14} -> {matches[0][0]}  ({matches[0][1]:,})")
        else: print(f"  {t:<14} -> (no match)")

if __name__ == "__main__":
    main()