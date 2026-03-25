#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build the Fingilish lexicon for Keyman.

Input files (same folder as this script):
  words_raw.csv       columns: word,count
  sentences_raw.csv   columns: sentence,count

Output files:
  fingilish.wordlist.tsv   Latin keys -> consumed by Keyman trie model
  persian_map.tsv          Latin key -> Persian word map (for kmn rules later)
  lexicon.tsv              Human-readable Persian->Latin review file
  blocklist.txt            Latin tokens to never auto-convert

How the wordlist works:
  The Keyman trie-1.0 model does prefix matching on the stored words.
  The user types Latin (e.g. "sal"), the trie finds all entries starting
  with "sal", and shows them as suggestions. The entry text is what gets
  inserted when the user accepts.

  Option B (current): wordlist stores Latin keys so the trie matches
  naturally. The suggestion shown and inserted is Latin (e.g. "salam").
  This confirms the pipeline works end-to-end.

  Option A (next step): .kmn rules will intercept the accepted Latin
  suggestion and replace it with Persian. persian_map.tsv has that data.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

WORDS_RAW     = BASE_DIR / "words_raw.csv"
SENTENCES_RAW = BASE_DIR / "sentences_raw.csv"

WORDLIST    = BASE_DIR / "fingilish.wordlist.tsv"
PERSIAN_MAP = BASE_DIR / "persian_map.tsv"
LEXICON     = BASE_DIR / "lexicon.tsv"
BLOCKLIST   = BASE_DIR / "blocklist.txt"


# ---------------------------------------------------------------------------
# Persian normalization
# ---------------------------------------------------------------------------

ARABIC_TO_PERSIAN = str.maketrans({
    "\u064a": "\u06cc",  # ي -> ی
    "\u0643": "\u06a9",  # ك -> ک
    "\u0629": "\u0647",  # ة -> ه
    "\u06c0": "\u0647",  # ۀ -> ه
    "\u0623": "\u0627",  # أ -> ا
    "\u0625": "\u0627",  # إ -> ا
    "\u0649": "\u06cc",  # ى -> ی
})
COMBINING_RE    = re.compile(r"[\u0640\u064B-\u065F\u0670\u06D6-\u06ED]")
SPACE_PUNCT_RE  = re.compile(r"\s+([؟!،\.,:;])")
MULTISPACE_RE   = re.compile(r"\s+")
PERSIAN_WORD_RE = re.compile(r"^[\u0600-\u06FF]+$")
TOKEN_RE        = re.compile(r"[\u0600-\u06FF]+")


def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = text.translate(ARABIC_TO_PERSIAN)
    text = COMBINING_RE.sub("", text)
    text = SPACE_PUNCT_RE.sub(r"\1", text)
    text = MULTISPACE_RE.sub(" ", text).strip()
    return text


def is_persian_word(word: str) -> bool:
    return bool(word and PERSIAN_WORD_RE.fullmatch(word))


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_tsv(path: Path, headers: list[str], rows: list) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(headers)
        w.writerows(rows)


# ---------------------------------------------------------------------------
# Frequency tables
# ---------------------------------------------------------------------------

def load_word_counts() -> Counter:
    counts: Counter = Counter()
    for row in read_csv(WORDS_RAW):
        word = normalize(row.get("word", ""))
        if not is_persian_word(word):
            continue
        try:
            counts[word] += int(row.get("count", 0))
        except ValueError:
            pass
    return counts


def load_sentence_word_counts() -> Counter:
    counts: Counter = Counter()
    for row in read_csv(SENTENCES_RAW):
        sentence = normalize(row.get("sentence", ""))
        try:
            freq = int(row.get("count", 0))
        except ValueError:
            continue
        for token in TOKEN_RE.findall(sentence):
            word = normalize(token)
            if is_persian_word(word):
                counts[word] += freq
    return counts


def merge_counts(wc: Counter, sc: Counter) -> list[tuple[str, int]]:
    all_words = set(wc) | set(sc)
    merged = [(w, wc.get(w, 0) + sc.get(w, 0)) for w in all_words]
    merged.sort(key=lambda x: (-x[1], x[0]))
    return merged


# ---------------------------------------------------------------------------
# Transliteration
# ---------------------------------------------------------------------------

MULTI_CHAR_MAP: dict[str, str] = {
    "\u062e": "kh",  # خ
    "\u0634": "sh",  # ش
    "\u0686": "ch",  # چ
    "\u0698": "zh",  # ژ
    "\u063a": "gh",  # غ
    "\u0642": "gh",  # ق
}

SINGLE_CHAR_MAP: dict[str, str] = {
    "\u0627": "a",   # ا
    "\u0622": "a",   # آ
    "\u0628": "b",   # ب
    "\u067e": "p",   # پ
    "\u062a": "t",   # ت
    "\u062b": "s",   # ث
    "\u062c": "j",   # ج
    "\u062d": "h",   # ح
    "\u062f": "d",   # د
    "\u0630": "z",   # ذ
    "\u0631": "r",   # ر
    "\u0632": "z",   # ز
    "\u0633": "s",   # س
    "\u0635": "s",   # ص
    "\u0636": "z",   # ض
    "\u0637": "t",   # ط
    "\u0638": "z",   # ظ
    "\u0639": "",    # ع
    "\u0641": "f",   # ف
    "\u06a9": "k",   # ک
    "\u06af": "g",   # گ
    "\u0644": "l",   # ل
    "\u0645": "m",   # م
    "\u0646": "n",   # ن
    "\u0648": "v",   # و
    "\u0647": "h",   # ه
    "\u06cc": "y",   # ی
    "\u0621": "",    # ء
}

MANUAL_LATIN: dict[str, str] = {
    # Top function words
    "\u06a9\u0647":    "ke",
    "\u0631\u0648":    "ro",
    "\u0628\u0647":    "be",
    "\u0645\u0646":    "man",
    "\u0648":          "o",
    "\u0627\u0632":    "az",
    "\u062a\u0648":    "to",
    "\u0627\u0648\u0646": "oon",
    "\u0627\u06cc\u0646": "in",
    "\u06cc\u0647":    "ye",
    "\u0645\u06cc":    "mi",
    "\u0646\u0647":    "na",
    "\u0628\u0627":    "ba",
    "\u062f\u0631":    "dar",
    "\u0645\u0627":    "ma",
    "\u0647\u0645":    "ham",
    "\u0628\u0648\u062f": "bood",
    "\u062a\u0627":    "ta",
    "\u0627\u06af\u0647": "age",
    "\u0647\u0645\u0647": "hame",
    "\u0647\u0631":    "har",
    "\u0627\u0645\u0627": "ama",
    "\u06cc\u0627":    "ya",
    "\u0686\u0648\u0646": "chon",
    "\u067e\u0633":    "pas",
    "\u062f\u06cc\u06af\u0647": "dige",
    "\u0647\u0646\u0648\u0632": "hanooz",
    "\u062d\u0627\u0644\u0627": "hala",
    "\u0641\u0642\u0637": "faghat",
    "\u062e\u0628":    "khob",
    "\u0627\u06cc\u0646\u062c\u0627": "inja",
    "\u0627\u0648\u0646\u062c\u0627": "onja",
    "\u0627\u0644\u0627\u0646": "alan",
    "\u0634\u0627\u06cc\u062f": "shayad",
    # Common verbs
    "\u0628\u0627\u06cc\u062f":    "bayad",
    "\u0628\u0627\u0634\u0647":    "bashe",
    "\u06a9\u0646":               "kon",
    "\u06a9\u0646\u0645":          "konam",
    "\u06a9\u0646\u06cc":          "koni",
    "\u06a9\u0646\u0647":          "kone",
    "\u06a9\u0646\u06cc\u0645":    "konim",
    "\u06a9\u0646\u06cc\u062f":    "konid",
    "\u0645\u06cc\u06a9\u0646\u0645": "mikonam",
    "\u0645\u06cc\u06a9\u0646\u06cc": "mikoni",
    "\u0645\u06cc\u06a9\u0646\u0647": "mikone",
    "\u0628\u0643\u0646":          "bokon",
    "\u0646\u06a9\u0646":          "nakon",
    "\u0628\u062f\u0647":          "bede",
    "\u0645\u06cc\u062f\u0647":    "mide",
    "\u062f\u0627\u062f":          "dad",
    "\u062f\u0627\u0631\u06cc":    "dari",
    "\u062f\u0627\u0631\u0647":    "dare",
    "\u062f\u0627\u0631\u0645":    "daram",
    "\u062f\u0627\u0631\u0646":    "daran",
    "\u062f\u0627\u0631\u06cc\u0645": "darim",
    "\u0628\u06cc\u0627":          "bia",
    "\u0645\u06cc\u0627\u0645":    "miam",
    "\u0645\u06cc\u0627\u06cc":    "miai",
    "\u0645\u06cc\u0627\u062f":    "miad",
    "\u0628\u0631\u06cc\u0645":    "berim",
    "\u0628\u0631\u0648":          "boro",
    "\u0631\u0641\u062a\u0645":    "raftam",
    "\u0631\u0641\u062a\u06cc":    "rafti",
    "\u0631\u0641\u062a":          "raft",
    "\u0628\u06af\u0648":          "bego",
    "\u06af\u0641\u062a\u0645":    "goftam",
    "\u06af\u0641\u062a\u06cc":    "gofti",
    "\u06af\u0641\u062a":          "goft",
    "\u06af\u0641\u062a\u0646":    "goftan",
    "\u0628\u0628\u06cc\u0646":    "bebin",
    "\u062f\u06cc\u062f\u0645":    "didam",
    "\u062f\u06cc\u062f\u06cc":    "didi",
    "\u062f\u06cc\u062f":          "did",
    "\u0628\u0632\u0646":          "bezan",
    "\u0632\u062f\u0645":          "zadam",
    "\u0628\u0634\u06cc\u0646":    "beshin",
    "\u0645\u06cc\u062e\u0648\u0627\u0645": "mikham",
    "\u0645\u06cc\u062e\u0648\u0627\u06cc": "mikhai",
    "\u0645\u06cc\u062e\u0648\u0627\u062f": "mikhad",
    "\u0645\u06cc\u062e\u0648\u0627\u0646": "mikhan",
    "\u0646\u0645\u06cc\u062e\u0648\u0627\u0645": "nemikham",
    "\u0645\u06cc\u0631\u0645":    "miram",
    "\u0645\u06cc\u0631\u06cc":    "miri",
    "\u0645\u06cc\u0631\u0647":    "mire",
    "\u0645\u06cc\u0631\u06cc\u0645": "mirim",
    "\u0628\u0645\u0648\u0646":    "bemoon",
    "\u0628\u06af\u06cc\u0631":    "begir",
    "\u06af\u0631\u0641\u062a\u0645": "gereftam",
    "\u06af\u0631\u0641\u062a":    "gereft",
    "\u0628\u0630\u0627\u0631":    "bezar",
    "\u0646\u0645\u06cc\u062f\u0648\u0646\u0645": "nemidoonam",
    "\u0646\u0645\u06cc\u062f\u0648\u0646\u06cc": "nemidooni",
    "\u0645\u06cc\u062f\u0648\u0646\u0645": "midoonam",
    "\u0645\u06cc\u062f\u0648\u0646\u06cc": "midooni",
    "\u0645\u06cc\u062f\u0648\u0646\u0647": "midoone",
    "\u0645\u06cc\u062a\u0648\u0646\u0645": "mitonam",
    "\u0645\u06cc\u062a\u0648\u0646\u06cc": "mitooni",
    "\u0645\u06cc\u062a\u0648\u0646\u0647": "mitoone",
    "\u0646\u0645\u06cc\u062a\u0648\u0646\u0645": "nemitonam",
    "\u0646\u0645\u06cc\u062a\u0648\u0646\u06cc": "nemitooni",
    "\u0634\u062f\u0645":          "shodam",
    "\u0634\u062f\u06cc":          "shodi",
    "\u0634\u062f":                "shod",
    "\u0628\u0634\u0647":          "beshe",
    "\u0645\u06cc\u0634\u0647":    "mishe",
    "\u0646\u0645\u06cc\u0634\u0647": "nemishe",
    # Nouns / adjectives
    "\u0686\u06cc":    "chi",
    "\u0686\u0647":    "che",
    "\u0686\u0631\u0627": "chera",
    "\u0686\u0637\u0648\u0631": "chetoor",
    "\u06a9\u062c\u0627": "koja",
    "\u06a9\u06cc":    "ki",
    "\u06a9\u062f\u0648\u0645": "kodoom",
    "\u0686\u0646\u062f": "chand",
    "\u0686\u0642\u062f\u0631": "cheghadr",
    "\u062e\u06cc\u0644\u06cc": "kheili",
    "\u062e\u0648\u0628": "khob",
    "\u062e\u0648\u0628\u0647": "khube",
    "\u0628\u062f":    "bad",
    "\u0642\u0634\u0646\u06af": "ghashang",
    "\u0632\u06cc\u0628\u0627": "ziba",
    "\u0628\u0632\u0631\u06af": "bozorg",
    "\u06a9\u0648\u0686\u06cc\u06a9": "koochik",
    "\u062f\u0631\u0633\u062a": "dorost",
    "\u063a\u0644\u0637": "ghalat",
    "\u0645\u0647\u0645": "mohem",
    "\u0631\u0627\u062d\u062a": "rahat",
    "\u0633\u062e\u062a": "sakht",
    "\u0622\u0633\u0648\u0646": "asoon",
    "\u06af\u0631\u0648\u0646": "geroon",
    "\u0627\u0631\u0632\u0648\u0646": "arzoon",
    "\u0633\u0644\u0627\u0645": "salam",
    "\u0645\u0645\u0646\u0648\u0646": "mamnoon",
    "\u0641\u06a9\u0631": "fekr",
    "\u06a9\u0627\u0631": "kar",
    "\u0648\u0642\u062a": "vaght",
    "\u062f\u0648\u0633\u062a": "doost",
    "\u062e\u0648\u0646\u0647": "khune",
    "\u062e\u0627\u0646\u0647": "khune",
    "\u0645\u0627\u0634\u06cc\u0646": "mashin",
    "\u0631\u0648\u0632": "rooz",
    "\u0634\u0628":    "shab",
    "\u0635\u0628\u062d": "sobh",
    "\u0638\u0647\u0631": "zohr",
    "\u0627\u0645\u0634\u0628": "emshab",
    "\u0627\u0645\u0631\u0648\u0632": "emrooz",
    "\u0641\u0631\u062f\u0627": "farda",
    "\u062f\u06cc\u0631\u0648\u0632": "diruz",
    "\u0647\u0641\u062a\u0647": "hafte",
    # Chat / colloquial
    "\u0622\u0631\u0647":  "are",
    "\u0627\u0635\u0644\u0627\u064b": "aslan",
    "\u0648\u0627\u0642\u0639\u0627\u064b": "vaghean",
    "\u062c\u062f\u06cc": "jeddi",
    "\u062f\u0631\u0648\u063a": "doroogh",
    "\u0631\u0627\u0633\u062a": "rast",
    "\u062e\u0648\u0634\u0628\u062e\u062a\u0645": "khoshbakhtam",
    "\u06a9\u0646\u0627\u0631": "kenar",
    "\u0644\u062d\u0638\u0647": "lahze",
    "\u0648\u0627\u06cc\u0633\u0627": "veysa",
    "\u0627\u0645\u062a\u062d\u0627\u0646": "emtehan",
}


def rough_transliterate(word: str) -> str:
    if word in MANUAL_LATIN:
        return MANUAL_LATIN[word]
    result = ""
    for ch in word:
        if ch in MULTI_CHAR_MAP:
            result += MULTI_CHAR_MAP[ch]
        elif ch in SINGLE_CHAR_MAP:
            result += SINGLE_CHAR_MAP[ch]
    result = re.sub(r"(.)\1{2,}", r"\1", result)
    return result.strip() or "?"


def normalize_latin_key(latin: str) -> str:
    s = latin.lower()
    s = s.replace("x", "kh")
    s = s.replace("q", "gh")
    s = s.replace("w", "v")
    s = s.replace("aa", "a")
    s = s.replace("oo", "o")
    s = s.replace("ee", "i")
    s = re.sub(r"(.)\1{2,}", r"\1", s)
    s = re.sub(r"[^a-z]", "", s)
    return s


# ---------------------------------------------------------------------------
# Output builders
# ---------------------------------------------------------------------------

def build_outputs(merged: list[tuple[str, int]]) -> None:
    latin_to_persian: dict[str, tuple[str, int]] = {}
    lexicon_rows = []

    for persian, freq in merged:
        latin = rough_transliterate(persian)
        if latin == "?":
            continue
        key = normalize_latin_key(latin)
        if not key:
            continue
        lexicon_rows.append([persian, freq, latin])
        if key not in latin_to_persian or freq > latin_to_persian[key][1]:
            latin_to_persian[key] = (persian, freq)

    # fingilish.wordlist.tsv — Latin key TAB freq, no header
    wordlist_rows = sorted(latin_to_persian.items(), key=lambda x: -x[1][1])
    with WORDLIST.open("w", encoding="utf-8", newline="") as f:
        for key, (_, freq) in wordlist_rows:
            f.write(f"{key}\t{freq}\n")
    print(f"  Wrote {len(wordlist_rows):,} entries -> {WORDLIST.name}")

    # persian_map.tsv — for generating kmn rules later
    map_rows = sorted(
        [(k, p, f) for k, (p, f) in latin_to_persian.items()],
        key=lambda x: -x[2]
    )
    write_tsv(PERSIAN_MAP, ["latin_key", "persian", "freq"], map_rows)
    print(f"  Wrote {len(map_rows):,} entries -> {PERSIAN_MAP.name}")

    # lexicon.tsv — human review
    lexicon_rows.sort(key=lambda x: -x[1])
    write_tsv(LEXICON, ["persian", "freq", "latin"], lexicon_rows)
    print(f"  Wrote {len(lexicon_rows):,} entries -> {LEXICON.name}")


def write_blocklist() -> None:
    blocked = sorted([
        "in", "to", "man", "dar", "bar", "be", "on", "no", "as",
        "are", "has", "had", "not", "she", "his", "her", "was",
        "can", "did", "get", "got", "him", "how", "its", "may",
        "our", "out", "set", "say", "use", "way", "who", "why",
        "do", "go", "me", "my", "by", "am", "an", "at",
        "if", "is", "it", "of", "or", "so", "up", "us",
    ])
    with BLOCKLIST.open("w", encoding="utf-8", newline="\n") as f:
        for item in blocked:
            f.write(item + "\n")
    print(f"  Wrote {len(blocked)} entries -> {BLOCKLIST.name}")


def demo_lookup(merged: list[tuple[str, int]]) -> None:
    lookup: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for persian, freq in merged:
        latin = rough_transliterate(persian)
        if latin != "?":
            key = normalize_latin_key(latin)
            if key:
                lookup[key].append((persian, freq))

    print("\nSample lookups (what trie will match):")
    tests = ["salam", "in", "ye", "oon", "mitooni", "kheili",
             "bayad", "koja", "bebin", "bego", "chera", "chetoor"]
    for token in tests:
        key = normalize_latin_key(token)
        matches = sorted(lookup.get(key, []), key=lambda x: -x[1])[:1]
        if matches:
            persian, freq = matches[0]
            print(f"  {token:<14} key={key:<14} -> {persian}  ({freq:,})")
        else:
            print(f"  {token:<14} key={key:<14} -> (no match)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not WORDS_RAW.exists():
        raise FileNotFoundError(f"Missing: {WORDS_RAW}")
    if not SENTENCES_RAW.exists():
        raise FileNotFoundError(f"Missing: {SENTENCES_RAW}")

    print("Loading frequencies ...")
    wc = load_word_counts()
    sc = load_sentence_word_counts()
    merged = merge_counts(wc, sc)
    print(f"  {len(merged):,} unique Persian words")

    print("\nWriting output files ...")
    build_outputs(merged)
    write_blocklist()

    demo_lookup(merged)

    print(f"\nDone. Files in {BASE_DIR}:")
    for p in [WORDLIST, PERSIAN_MAP, LEXICON, BLOCKLIST]:
        print(f"  {p.name:<40} {p.stat().st_size // 1024:>4} KB")


if __name__ == "__main__":
    main()