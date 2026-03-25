#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build the Fingilish lexicon for Keyman.

Input files (in the same folder as this script):
  words_raw.csv       columns: word,count
  sentences_raw.csv   columns: sentence,count

Output files (in the same folder):
  fingilish.wordlist.tsv   → consumed by fingilish.model.ts (Keyman)
  lexicon.tsv              → human-readable Persian→Latin mapping for review
  blocklist.txt            → Latin tokens to never auto-convert

Intermediate data (words.tsv, sentences.tsv, normalized files, etc.) is
kept in memory only and not written to disk.

Usage:
  python build_lexicon.py

Run from any directory; paths are resolved relative to this script file.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR.parent

WORDS_RAW      = BASE_DIR / "words_raw.csv"
SENTENCES_RAW  = BASE_DIR / "sentences_raw.csv"

WORDLIST       = SOURCE_DIR / "fingilish.wordlist.tsv"
LEXICON        = BASE_DIR / "lexicon.tsv"
BLOCKLIST      = BASE_DIR / "blocklist.txt"


# ---------------------------------------------------------------------------
# Persian text normalization
# ---------------------------------------------------------------------------

ARABIC_TO_PERSIAN = str.maketrans({
    "ي": "ی",
    "ك": "ک",
    "ة": "ه",
    "ۀ": "ه",
    "أ": "ا",
    "إ": "ا",
    "ى": "ی",
})

COMBINING_RE     = re.compile(r"[\u0640\u064B-\u065F\u0670\u06D6-\u06ED]")
SPACE_PUNCT_RE   = re.compile(r"\s+([؟!،\.,:;])")
MULTISPACE_RE    = re.compile(r"\s+")
PERSIAN_WORD_RE  = re.compile(r"^[\u0600-\u06FF]+$")
TOKEN_RE         = re.compile(r"[\u0600-\u06FF]+")


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
# CSV reading
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# TSV writing
# ---------------------------------------------------------------------------

def write_tsv(path: Path, headers: list[str], rows: list) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(headers)
        w.writerows(rows)


# ---------------------------------------------------------------------------
# Build frequency tables (in memory)
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


def merge_counts(word_counts: Counter, sentence_counts: Counter) -> list[tuple[str, int]]:
    all_words = set(word_counts) | set(sentence_counts)
    merged = [
        (w, word_counts.get(w, 0) + sentence_counts.get(w, 0))
        for w in all_words
    ]
    merged.sort(key=lambda x: (-x[1], x[0]))
    return merged


# ---------------------------------------------------------------------------
# Transliteration
# ---------------------------------------------------------------------------

# Multi-character mappings are checked first (order matters).
MULTI_CHAR_MAP: dict[str, str] = {
    "خ": "kh",
    "ش": "sh",
    "چ": "ch",
    "ژ": "zh",
    "غ": "gh",
    "ق": "gh",
}

# Single-character fallback mappings.
# Note: و / ه / ی have context-dependent pronunciations; these are defaults.
SINGLE_CHAR_MAP: dict[str, str] = {
    "ا": "a",
    "آ": "a",
    "ب": "b",
    "پ": "p",
    "ت": "t",
    "ث": "s",
    "ج": "j",
    "ح": "h",
    "د": "d",
    "ذ": "z",
    "ر": "r",
    "ز": "z",
    "س": "s",
    "ص": "s",
    "ض": "z",
    "ط": "t",
    "ظ": "z",
    "ع": "",
    "ف": "f",
    "ک": "k",
    "گ": "g",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "و": "v",   # consonant default; handled as "o/oo/u" vowel in MANUAL
    "ه": "h",
    "ی": "y",
    "ء": "",
}

# Manual overrides — these are the ground truth for common words.
# The automated transliterator cannot reliably recover short vowels that
# Persian orthography omits, so we enumerate the top vocabulary here.
#
# Convention used: match how Iranians actually type in Fingilish.
#   - "aa" / "oo" / "ee" for long vowels (user can also type "a"/"o"/"i")
#   - "kh", "sh", "ch", "gh", "zh" for digraphs
#   - silent/helper vowels added where needed for readability
MANUAL_LATIN: dict[str, str] = {
    # ─── Top function words ──────────────────────────────────────────────
    "که":       "ke",
    "رو":       "ro",
    "به":       "be",
    "من":       "man",
    "و":        "o",
    "از":       "az",
    "تو":       "to",
    "اون":      "oon",
    "این":      "in",
    "یه":       "ye",
    "می":       "mi",
    "نه":       "na",
    "با":       "ba",
    "در":       "dar",
    "ما":       "ma",
    "هم":       "ham",
    "بود":      "bood",
    "تا":       "ta",
    "اگه":      "age",
    "همه":      "hame",
    "هر":       "har",
    "اما":      "ama",
    "یا":       "ya",
    "چون":      "chon",
    "پس":       "pas",
    "دیگه":     "dige",
    "هنوز":     "hanooz",
    "حالا":     "hala",
    "قبلاً":    "ghaban",
    "فقط":      "faghat",
    "خب":       "khob",
    "اینجا":    "inja",
    "اونجا":    "onja",
    "الان":     "alan",
    "دیگه":     "dige",
    "شاید":     "shayad",

    # ─── Common verbs / verb forms ───────────────────────────────────────
    "باید":     "bayad",
    "باشه":     "bashe",
    "کن":       "kon",
    "کنم":      "konam",
    "کنی":      "koni",
    "کنه":      "kone",
    "کنیم":     "konim",
    "کنید":     "konid",
    "میکنم":    "mikonam",
    "میکنی":    "mikoni",
    "میکنه":    "mikone",
    "میکنیم":   "mikonim",
    "میکنید":   "mikonid",
    "بکن":      "bokon",
    "نکن":      "nakon",
    "بده":      "bede",
    "میده":     "mide",
    "داد":      "dad",
    "داری":     "dari",
    "داره":     "dare",
    "دارم":     "daram",
    "دارن":     "daran",
    "داریم":    "darim",
    "بیا":      "bia",
    "میام":     "miam",
    "میای":     "miai",
    "میاد":     "miad",
    "بریم":     "berim",
    "برو":      "boro",
    "رفتم":     "raftam",
    "رفتی":     "rafti",
    "رفت":      "raft",
    "رفتیم":    "raftim",
    "بگو":      "bego",
    "گفتم":     "goftam",
    "گفتی":     "gofti",
    "گفت":      "goft",
    "گفتن":     "goftan",
    "ببین":     "bebin",
    "دیدم":     "didam",
    "دیدی":     "didi",
    "دید":      "did",
    "بزن":      "bezan",
    "زدم":      "zadam",
    "بشین":     "beshin",
    "نشستم":    "neshastam",
    "بیا":      "bia",
    "بخور":     "bokhor",
    "خوردم":    "khordam",
    "میخورم":   "mikhooram",
    "میخوام":   "mikham",
    "میخوای":   "mikhai",
    "میخواد":   "mikhad",
    "میخوان":   "mikhan",
    "بخواد":    "bekhad",
    "بخوای":    "bekhai",
    "نمیخوام":  "nemikham",
    "میرم":     "miram",
    "میری":     "miri",
    "میره":     "mire",
    "میریم":    "mirim",
    "بمون":     "bemoon",
    "موندم":    "moondam",
    "بپوش":     "bepush",
    "بخواب":    "bekhab",
    "خوابیدم":  "khabeedam",
    "بخند":     "bekhond",
    "خندیدم":   "khandeedam",
    "بگیر":     "begir",
    "گرفتم":    "gereftam",
    "گرفتی":    "gerefti",
    "گرفت":     "gereft",
    "بذار":     "bezar",
    "گذاشتم":   "gozashtam",
    "بپرس":     "bepors",
    "پرسیدم":   "porseedam",
    "نمیدونم":  "nemidoonam",
    "نمیدونی":  "nemidooni",
    "میدونم":   "midoonam",
    "میدونی":   "midooni",
    "میدونه":   "midoone",
    "بدونم":    "bedoonam",
    "فهمیدم":   "fahmeedam",
    "فهمیدی":   "fahmeedi",
    "نفهمیدم":  "nafahmeedam",
    "میفهمم":   "mifahmam",
    "میتونم":   "mitonam",
    "میتونی":   "mitooni",
    "میتونه":   "mitoone",
    "نمیتونم":  "nemitonam",
    "نمیتونی":  "nemitooni",
    "شدم":      "shodam",
    "شدی":      "shodi",
    "شد":       "shod",
    "بشه":      "beshe",
    "میشه":     "mishe",
    "نمیشه":    "nemishe",
    "بشم":      "besham",

    # ─── Common nouns / adjectives ───────────────────────────────────────
    "چی":       "chi",
    "چه":       "che",
    "چرا":      "chera",
    "چطور":     "chetoor",
    "کجا":      "koja",
    "کی":       "ki",
    "کدوم":     "kodoom",
    "چند":      "chand",
    "چقدر":     "cheghadr",
    "خیلی":     "kheili",
    "خوب":      "khob",
    "خوبه":     "khube",
    "بد":       "bad",
    "بده":      "bade",
    "قشنگ":     "ghashang",
    "زیبا":     "ziba",
    "بزرگ":     "bozorg",
    "کوچیک":    "koochik",
    "سریع":     "sari",
    "آروم":     "aroom",
    "درست":     "dorost",
    "غلط":      "ghalat",
    "مهم":      "mohem",
    "راحت":     "rahat",
    "سخت":      "sakht",
    "آسون":     "asoon",
    "گرون":     "geroon",
    "ارزون":    "arzoon",
    "سلام":     "salam",
    "ممنون":    "mamnoon",
    "خواهش":    "khahesh",
    "ببخشید":   "bebakhshid",
    "متشکرم":   "mотаshakeram",
    "فکر":      "fekr",
    "کار":      "kar",
    "وقت":      "vaght",
    "جا":       "ja",
    "اسم":      "esm",
    "آدم":      "adam",
    "دوست":     "doost",
    "خانه":     "khune",
    "خونه":     "khune",
    "مدرسه":    "madrese",
    "ماشین":    "mashin",
    "راه":      "rah",
    "در":       "dar",
    "پول":      "pool",
    "روز":      "rooz",
    "شب":       "shab",
    "صبح":      "sobh",
    "ظهر":      "zohr",
    "امشب":     "emshab",
    "امروز":    "emrooz",
    "فردا":     "farda",
    "دیروز":    "diruz",
    "هفته":     "hafte",
    "ماه":      "mah",
    "سال":      "sal",
    "اسم":      "esm",
    "چشم":      "cheshm",
    "دست":      "dast",
    "قلب":      "ghalb",
    "دل":       "del",
    "سر":       "sar",
    "پا":       "pa",

    # ─── Colloquial / chat ────────────────────────────────────────────────
    "آره":      "are",
    "باشه":     "bashe",
    "اوکی":     "okay",
    "آخه":      "akhe",
    "عه":       "e",
    "وای":      "vay",
    "اِ":       "e",
    "هی":       "hey",
    "خوشبختم":  "khoshbakhtam",
    "کنار":     "kenar",
    "لحظه":     "lahze",
    "وایسا":    "veysa",
    "امتحان":   "emtehan",
    "غلطی":     "ghalati",
    "زیباست":   "zibast",
    "بلندشو":   "bolandsho",
    "متشکرم":   "motashakeram",
    "ببخش":     "bebakhsh",
    "خوشحالم":  "khoshalam",
    "ناراحتم":  "narahatam",
    "عاشقتم":   "asheghetam",
    "دوستت":    "doostet",
    "دوستت دارم": "doostet daram",
    "مراقب":    "morageb",
    "حواست":    "havaset",
    "بیخیال":   "bikheyal",
    "ولش":      "velesh",
    "ولم":      "velam",
    "اصلاً":    "aslan",
    "مثلاً":    "masalan",
    "واقعاً":   "vaghean",
    "جدی":      "jeddi",
    "دروغ":     "doroogh",
    "راست":     "rast",
}


def rough_transliterate(word: str) -> str:
    if word in MANUAL_LATIN:
        return MANUAL_LATIN[word]

    pieces = []
    for ch in word:
        if ch in MULTI_CHAR_MAP:
            pieces.append(MULTI_CHAR_MAP[ch])
        elif ch in SINGLE_CHAR_MAP:
            pieces.append(SINGLE_CHAR_MAP[ch])
        # else: skip unknown chars (punctuation etc. shouldn't reach here)

    latin = "".join(pieces)

    # Collapse triple+ repeats (e.g. "rrr" → "r")
    latin = re.sub(r"(.)\1{2,}", r"\1", latin)
    latin = latin.strip()

    return latin or "?"


# ---------------------------------------------------------------------------
# Build Keyman wordlist
# ---------------------------------------------------------------------------

def build_wordlist(merged: list[tuple[str, int]]) -> None:
    """
    Write fingilish.wordlist.tsv in the format Keyman expects:
      word <TAB> frequency
    No header row.

    The Persian word is the surface form that gets inserted.
    The Keyman model's searchTermToKey converts typed Latin to a lookup key,
    and also converts the Persian word to the same key space for indexing.
    """
    rows = []
    for word, freq in merged:
        latin = rough_transliterate(word)
        if latin == "?":
            continue  # skip untranslatable entries (isolated punctuation etc.)
        rows.append((word, freq))

    # Sort by frequency descending.
    rows.sort(key=lambda x: -x[1])

    with WORDLIST.open("w", encoding="utf-8", newline="") as f:
        for word, freq in rows:
            f.write(f"{word}\t{freq}\n")

    print(f"  Wrote {len(rows):,} entries → {WORDLIST.name}")


def build_human_readable_lexicon(merged: list[tuple[str, int]]) -> None:
    """
    Write lexicon.tsv for human inspection:
      word <TAB> freq <TAB> latin
    """
    rows = []
    for word, freq in merged:
        latin = rough_transliterate(word)
        rows.append([word, freq, latin])

    rows.sort(key=lambda x: -x[1])

    write_tsv(LEXICON, ["word", "freq", "latin"], rows)
    print(f"  Wrote {len(rows):,} entries → {LEXICON.name}")


# ---------------------------------------------------------------------------
# Blocklist
# ---------------------------------------------------------------------------

def write_blocklist() -> None:
    """
    Latin tokens that should never trigger auto-conversion because they are
    common English words, which would cause false fires for bilingual users.
    Extend this list as you discover false positives.
    """
    blocked = sorted([
        # English words that collide with valid Fingilish tokens
        "in", "to", "man", "dar", "bar", "be", "on", "no", "as",
        "are", "has", "had", "not", "she", "his", "her", "was",
        "can", "did", "get", "got", "him", "how", "its", "may",
        "our", "out", "set", "say", "use", "way", "who", "why",
        "do",  "go",  "me",  "my",  "by",  "am",  "an",  "at",
        "if",  "is",  "it",  "of",  "or",  "so",  "up",  "us",
    ])
    with BLOCKLIST.open("w", encoding="utf-8", newline="\n") as f:
        for item in blocked:
            f.write(item + "\n")
    print(f"  Wrote {len(blocked)} entries → {BLOCKLIST.name}")


# ---------------------------------------------------------------------------
# Demo lookup (uses the in-memory transliteration, not disk files)
# ---------------------------------------------------------------------------

def demo_lookup(merged: list[tuple[str, int]]) -> None:
    lookup: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for word, freq in merged:
        latin = rough_transliterate(word)
        if latin != "?":
            lookup[latin].append((word, freq))

    print("\nSample lookups (top 3 matches per token):")
    tests = ["salam", "in", "ye", "oon", "mitooni", "kheili",
             "bayad", "koja", "bebin", "bego", "chera", "chetoor"]

    for token in tests:
        matches = sorted(lookup.get(token, []), key=lambda x: -x[1])[:3]
        if matches:
            top = ", ".join(f"{w} ({f:,})" for w, f in matches)
            print(f"  {token:<14} → {top}")
        else:
            print(f"  {token:<14} → (no match)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not WORDS_RAW.exists():
        raise FileNotFoundError(f"Missing: {WORDS_RAW}")
    if not SENTENCES_RAW.exists():
        raise FileNotFoundError(f"Missing: {SENTENCES_RAW}")

    print("Loading word frequencies …")
    word_counts = load_word_counts()
    print(f"  {len(word_counts):,} unique words from words_raw.csv")

    print("Loading sentence-derived word frequencies …")
    sentence_counts = load_sentence_word_counts()
    print(f"  {len(sentence_counts):,} unique words from sentences_raw.csv")

    print("Merging …")
    merged = merge_counts(word_counts, sentence_counts)
    print(f"  {len(merged):,} unique words total")

    print("\nWriting output files …")
    build_wordlist(merged)
    build_human_readable_lexicon(merged)
    write_blocklist()

    demo_lookup(merged)

    print(f"\nDone. Files in {BASE_DIR}:")
    for p in [WORDLIST, LEXICON, BLOCKLIST]:
        size_kb = p.stat().st_size // 1024
        print(f"  {p.name:<35} {size_kb:>5} KB")


if __name__ == "__main__":
    main()
