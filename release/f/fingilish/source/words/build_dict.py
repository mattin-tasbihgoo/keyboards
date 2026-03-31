#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_dict.py — Generate fingilish_dict.json for the Keyman keyboard

This script generates a Latin→Persian dictionary where keys are
how users ACTUALLY TYPE Fingilish (with vowels), not consonant skeletons.

Sources:
  1. MANUAL dict: hand-verified Fingilish for common words
  2. NAMES dict: common Persian proper names
  3. Algorithmic generation from wordlist (with variant expansion)

Output: fingilish_dict.json (consumed by build_calljs.py)

To add words: edit the MANUAL dict below, re-run this script.
"""

import json, re, csv
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent

# ============================================================
# MANUAL DICTIONARY — human-verified Fingilish spellings
# Add new words here! Format: "persian": ["primary", "variant1", "variant2", ...]
# The first entry is the canonical spelling.
# ============================================================
MANUAL = {
    # Function words
    "که": ["ke"], "رو": ["ro", "roo"], "به": ["be"], "من": ["man"],
    "و": ["va", "o"], "از": ["az"], "تو": ["to", "too"], "اون": ["oon", "un"],
    "این": ["in", "een"], "یه": ["ye"], "می": ["mi"], "نه": ["na", "nah"],
    "با": ["ba"], "در": ["dar"], "ما": ["ma"], "هم": ["ham"],
    "بود": ["bood", "bud"], "تا": ["ta"], "اگه": ["age", "ageh"],
    "همه": ["hame", "hameh"], "هر": ["har"], "اما": ["ama", "amma"],
    "یا": ["ya"], "چون": ["chon", "choon"], "پس": ["pas"],
    "دیگه": ["dige", "digeh", "dige"], "هنوز": ["hanooz", "hanuz"],
    "حالا": ["hala", "haala"], "فقط": ["faghat", "faqat"],
    "خب": ["khob", "khab"], "اینجا": ["inja", "injaa"],
    "اونجا": ["onja", "oonja"], "الان": ["alan", "alaan"],
    "شاید": ["shayad", "shaayad"], "حتی": ["hata", "hatta"],
    "بعد": ["bad", "baad"], "مثل": ["mesl", "mesle"],
    "همین": ["hamin", "hameen"], "پیدا": ["peyda", "peida"],
    "هیچ": ["hich", "heech"], "یکی": ["yeki"],
    "واقعا": ["vaghan", "vaqean"], "اصلا": ["aslan"],
    "البته": ["albate", "albatteh"], "لطفا": ["lotfan", "lotfa"],
    "یعنی": ["yani", "yaani"],

    # Common verbs — present
    "باید": ["bayad", "baayad"], "باشه": ["bashe", "baasheh"],
    "کن": ["kon"], "کنم": ["konam", "konem"], "کنی": ["koni"],
    "کنه": ["kone", "koneh"], "کنیم": ["konim"],
    "کنید": ["konid", "konin"], "کنند": ["konand", "konan"],
    "میکنم": ["mikonam", "mikonem"], "میکنی": ["mikoni"],
    "میکنه": ["mikone", "mikoneh"], "میکنیم": ["mikonim"],
    "بکن": ["bokon"], "نکن": ["nakon"],
    "بده": ["bede", "bedeh"], "میده": ["mide", "mideh"],
    "داد": ["dad", "daad"], "داری": ["dari", "daari"],
    "داره": ["dare", "daareh"], "دارم": ["daram", "daaram"],
    "دارن": ["daran", "daaran"], "داریم": ["darim", "daarim"],
    "دارید": ["darid", "darin"],

    # Common verbs — motion
    "بیا": ["bia", "biya"], "بریم": ["berim", "berem"],
    "برو": ["boro", "bero"], "بیاید": ["biaid", "biayin", "biain"],
    "رفتم": ["raftam"], "رفتی": ["rafti"], "رفت": ["raft"],
    "رفتیم": ["raftim"], "رفتن": ["raftan"],
    "میرم": ["miram", "mirm"], "میری": ["miri"],
    "میره": ["mire", "mireh"], "میریم": ["mirim"],
    "برم": ["beram", "berm"], "بری": ["beri"],
    "بره": ["bereh", "bareh"], "برن": ["beran"],
    "میام": ["miam", "miyam"], "میای": ["miai", "miyai"],
    "میاد": ["miad", "miyad"],
    "بیام": ["biam", "biyam"], "بیای": ["biai", "biyai"],

    # Common verbs — saying/seeing
    "بگو": ["bego", "begoo"], "گفتم": ["goftam"],
    "گفتی": ["gofti"], "گفت": ["goft"], "گفتن": ["goftan"],
    "میگم": ["migam", "migem"], "میگی": ["migi"],
    "میگه": ["mige", "migeh"], "میگن": ["migan"],
    "ببین": ["bebin", "bebeen"], "دیدم": ["didam"],
    "دیدی": ["didi"], "دید": ["did"],
    "میبینم": ["mibinam"], "میبینی": ["mibini"],

    # Common verbs — wanting/knowing/being able
    "میخوام": ["mikham", "mikhaam", "mikhwam"],
    "میخوای": ["mikhai", "mikhay", "mikhwai"],
    "میخواد": ["mikhad", "mikhwad"],
    "نمیخوام": ["nemikham", "nemikhaam"],
    "میدونم": ["midoonam", "midonam", "midunam"],
    "میدونی": ["midooni", "midoni", "miduni"],
    "میدونه": ["midooneh", "midoneh"],
    "نمیدونم": ["nemidoonam", "nemidonam"],
    "میتونم": ["mitonam", "mitoonam", "mitunam"],
    "میتونی": ["mitooni", "mitoni", "mituni"],
    "میتونه": ["mitooneh", "mitoneh"],
    "نمیتونم": ["nemitonam", "nemitoonam"],
    "نمیتونی": ["nemitooni", "nemitoni"],

    # Common verbs — being/becoming
    "شدم": ["shodam"], "شدی": ["shodi"], "شد": ["shod"],
    "بشه": ["beshe", "besheh"], "میشه": ["mishe", "misheh"],
    "نمیشه": ["nemishe", "nemisheh"],
    "هستم": ["hastam"], "هستی": ["hasti"], "هست": ["hast"],
    "بودم": ["boodam", "budam"], "بودی": ["boodi", "budi"],
    "بودیم": ["boodim", "budim"], "بودن": ["boodan", "budan"],
    "بودند": ["boodand", "budand"],

    # Common verbs — other
    "بمون": ["bemoon", "bemun"], "بگیر": ["begir", "begeer"],
    "گرفتم": ["gereftam"], "گرفت": ["gereft"],
    "بذار": ["bezar", "bezaar"], "بزن": ["bezan"],
    "بشین": ["beshin", "beshen"],
    "بخور": ["bekhor", "bokhur"], "خوردم": ["khordam"],
    "بخواب": ["bekhab", "bekhaab"], "خوابیدم": ["khabidam"],
    "بنویس": ["benevis"], "نوشتم": ["neveshtam"],
    "بپرس": ["bepors"], "پرسیدم": ["porsidam"],
    "بخون": ["bekhon", "bekhoon"], "خوندم": ["khondam"],

    # Questions
    "چی": ["chi", "chee"], "چه": ["che", "cheh"],
    "چرا": ["chera", "cheraa"], "چطور": ["chetor", "chetoor", "chetowr"],
    "چطوری": ["chetori", "chetoori"], "چطوره": ["chetoreh", "chetooreh"],
    "کجا": ["koja", "kojaa"], "کجایی": ["kojai", "kojayi"],
    "کی": ["ki", "key"], "کدوم": ["kodoom", "kodum"],
    "چند": ["chand"], "چیکار": ["chikar", "chikaar"],
    "چقدر": ["cheqadr", "cheghadr"], "چجوری": ["chejoori", "chejuri"],

    # Adjectives/adverbs
    "خیلی": ["kheili", "kheyli", "xeili", "xeyli"],
    "خوب": ["khob", "khoob", "xoob", "xob"],
    "خوبه": ["khobe", "khoobe", "khubeh"],
    "خوبی": ["khobi", "khoobi"],
    "بد": ["bad", "baad"], "بزرگ": ["bozorg", "bozorgh"],
    "کوچیک": ["kuchik", "koochik", "kuchek"],
    "زیاد": ["ziad", "ziyad", "ziyaad"],
    "کم": ["kam"], "زود": ["zood", "zud"],
    "دیر": ["dir", "deer"], "تند": ["tond"],
    "سخت": ["sakht"], "راحت": ["rahat", "raahat"],
    "درست": ["dorost", "doroste"],
    "بهتر": ["behtar"], "بهترین": ["behtarin"],
    "بدتر": ["badtar"],
    "خوشحال": ["khoshhal", "khoshhaal"],
    "ناراحت": ["narahat", "naarahat"],

    # Greetings/social
    "سلام": ["salam", "salaam"], "ممنون": ["mamnoon", "mamnun", "mersi"],
    "مرسی": ["mersi", "merci"], "خوشبختم": ["khoshbakhtam"],
    "خداحافظ": ["khodahafez", "khodaafez"],
    "ببخشید": ["bebakhshid", "bebakhshin"],
    "متاسفم": ["motasefam", "mota2sefam"],
    "تبریک": ["tabrik", "tabreek"],

    # Nouns — common
    "دوست": ["doost", "dust"], "خونه": ["khune", "khuneh", "khooneh"],
    "خانه": ["khaneh", "khaaneh"], "خانواده": ["khanevade", "khaanevadeh"],
    "ماشین": ["mashin", "maashin"], "روز": ["rooz", "ruz"],
    "شب": ["shab"], "امروز": ["emrooz", "emruz"],
    "فردا": ["farda", "fardaa"], "دیروز": ["dirooz", "diruz"],
    "دیشب": ["dishab", "dishab"],
    "آره": ["are", "aareh"], "آره": ["are"],
    "پول": ["pool", "pul"], "کار": ["kar", "kaar"],
    "سال": ["sal", "saal"], "ماه": ["mah", "maah"],
    "هفته": ["hafte", "hafteh"],
    "ساعت": ["saat", "sa'at"],
    "جا": ["ja", "jaa"], "راه": ["rah", "raah"],
    "آب": ["ab", "aab"], "غذا": ["ghaza", "qaza"],
    "خواب": ["khab", "khaab"], "دل": ["del"],
    "سر": ["sar"], "دست": ["dast"], "پا": ["pa", "paa"],
    "چشم": ["cheshm", "chashm"], "گوش": ["gush", "goosh"],
    "بچه": ["bache", "bacheh", "bachcheh"],
    "بابا": ["baba", "baabaa"], "مامان": ["maman", "maaman"],
    "پدر": ["pedar", "pedr"], "مادر": ["madar", "maadar"],
    "برادر": ["baradar", "baraadar"], "خواهر": ["khahar", "khaahar"],
    "پسر": ["pesar", "psar"], "دختر": ["dokhtar", "dokhtr"],
    "مرد": ["mard"], "زن": ["zan"],
    "خاله": ["khaleh", "khaaleh"], "عمو": ["amu", "amoo"],
    "دایی": ["dayi", "daayi"], "عمه": ["amme", "ammeh"],
    "دانشگاه": ["daneshgah", "daaneshgaah"],
    "مدرسه": ["madrese", "madreseh"],
    "بیمارستان": ["bimarestan", "bimaarestan"],
    "فرودگاه": ["forudgah", "foroodgaah"],
    "خیابان": ["khiaban", "khiyaabaan", "khiaboon"],
    "شهر": ["shahr", "shahr"], "کشور": ["keshvar"],
    "دنیا": ["donya", "donyaa"], "زندگی": ["zendegi", "zendegi"],

    # Verbs — more
    "خوش": ["khosh", "khoosh"], "گذشت": ["gozasht", "guzasht"],
    "گذاشت": ["gozasht", "guzaasht"],
    "گذاشتم": ["gozashtam"], "گذاشتن": ["gozashtan"],
    "فهمیدم": ["fahmidam", "fahmidem"],
    "فهمیدی": ["fahmidi"],
    "ترسیدم": ["tarsidam"],
    "رسیدم": ["residam"], "رسیدی": ["residi"],
    "کشتم": ["koshtam"], "کشت": ["kosht"],
    "شنیدم": ["shenidam", "shenidem"],
    "شنیدی": ["shenidi"],
    "نشستم": ["neshastam"], "نشسته": ["neshaste", "neshasteh"],
    "فرستادم": ["ferestadam"], "فرستاده": ["ferestadeh"],
    "برگشتم": ["bargashtam"], "برگشت": ["bargasht"],
    "برگرد": ["bargard"], "برگردم": ["bargardam"],
    "شروع": ["shoru", "shoroo"],
    "تموم": ["tamoom", "tamum"], "تمام": ["tamam", "tamaam"],
    "فراموش": ["faramush", "faraamoosh"],
    "انجام": ["anjam", "anjaam"],
    "استفاده": ["estefade", "estefaadeh"],

    # More common words people use
    "عاشق": ["ashegh", "aasheq"],
    "قلب": ["ghalb", "qalb"], "عشق": ["eshgh"],
    "همیشه": ["hamishe", "hamisheh"],
    "دوباره": ["dobare", "dobareh", "dubaareh"],
    "بیشتر": ["bishtar", "bishttar"],
    "قربان": ["ghorban", "qorbaan"],
    "احتمالا": ["ehtemaalan", "ehtemaala"],
    "مشکل": ["moshkel", "moshkul"],
    "مشکلی": ["moshkeli"],
    "لعنتی": ["lanati", "laanati"],
    "اشتباه": ["eshtebah", "eshtebaaah"],
    "اتفاق": ["etefagh", "etefaaq"],
    "اتفاقی": ["etefaghi"],
    "نگران": ["negaran", "negaraan"],
    "منتظر": ["montazer"],
    "مطمئن": ["motmaen", "motma2en"],
    "فکر": ["fekr", "feker"], "نظر": ["nazar"],
    "حق": ["hagh", "haq"], "حرف": ["harf"],
    "وقت": ["vaght", "vaqt"], "وقتی": ["vaghti", "vaqti"],

    # Adverbs/connectors
    "خیلی": ["kheili", "kheyli"],
    "الان": ["alan", "alaan"], "بعدا": ["badan", "ba'dan"],
    "قبلا": ["ghablan", "qablan"],
    "مثلا": ["masalan", "mesalan"],
    "اولین": ["avalin", "avvalin"],
    "آخرین": ["akharin"],
    "نزدیک": ["nazdik", "nazdeek"],
    "دور": ["door", "dur"],
}

# ============================================================
# PROPER NAMES — common Persian names
# ============================================================
NAMES = {
    "علی": ["ali"], "رضا": ["reza", "rezaa"],
    "محمد": ["mohammad", "mohamad", "muhammad"],
    "حسین": ["hossein", "hosein", "hoseyn"],
    "احمد": ["ahmad"],
    "مهدی": ["mahdi", "mehdi"],
    "فاطمه": ["fatemeh", "faatemeh"],
    "زهرا": ["zahra", "zahraa"],
    "مریم": ["maryam"],
    "سارا": ["sara", "saaraa"],
    "نرگس": ["narges"],
    "امیر": ["amir", "ameer"],
    "حسن": ["hasan", "hassan"],
    "جواد": ["javad", "javaad"],
    "مجید": ["majid", "majeed"],
    "سعید": ["saeed", "sa'eed"],
    "متین": ["matin", "mattin", "mateen"],
    "نیما": ["nima", "neema"],
    "پارسا": ["parsa", "paarsaa"],
    "آرش": ["arash", "aarash"],
    "کیان": ["kian", "kiyan"],
    "باران": ["baran", "baaraan"],
    "نازنین": ["nazanin", "naazaneen"],
    "الهام": ["elham"],
    "شیما": ["shima", "sheema"],
    "آرمین": ["armin", "armeen"],
    "دانیال": ["danial", "daaniyaal"],
    "پریسا": ["parisa", "pareesaa"],
    "ایران": ["iran", "eeraan"],
    "تهران": ["tehran", "tehraan"],
}

def build_dict():
    """Build the Latin→Persian dictionary."""
    result = {}  # latin_key → persian_word

    # 1. Add MANUAL entries (highest priority)
    for persian, variants in MANUAL.items():
        for latin in variants:
            latin_lower = latin.lower()
            if latin_lower not in result:
                result[latin_lower] = persian

    # 2. Add NAMES
    for persian, variants in NAMES.items():
        for latin in variants:
            latin_lower = latin.lower()
            if latin_lower not in result:
                result[latin_lower] = persian

    # 3. Load wordlist and add any MANUAL-keyed words from it
    wordlist_path = BASE_DIR / "fingilish.wordlist.tsv"
    if wordlist_path.exists():
        with wordlist_path.open("r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    persian = parts[0]
                    # Only add if the persian word is already in our dict
                    # (we don't add algorithmic keys anymore)
                    pass

    return result


def main():
    d = build_dict()

    # Sort by key for readability
    d_sorted = dict(sorted(d.items()))

    out_path = BASE_DIR / "fingilish_dict.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(d_sorted, f, ensure_ascii=False, separators=(',', ':'))

    print(f"Dictionary: {len(d_sorted)} entries → {out_path.name}")
    print(f"File size: {out_path.stat().st_size:,} bytes")

    # Verify key lookups
    print("\nVerification:")
    tests = [
        ("salam", "سلام"), ("salaam", "سلام"), ("kheili", "خیلی"),
        ("xeili", "خیلی"), ("beram", "برم"), ("daneshgah", "دانشگاه"),
        ("dishab", "دیشب"), ("khaleh", "خاله"), ("va", "و"),
        ("khosh", "خوش"), ("gozasht", "گذشت"), ("bache", "بچه"),
        ("boodand", "بودند"), ("ali", "علی"), ("reza", "رضا"),
        ("mohammad", "محمد"), ("mattin", "متین"), ("matin", "متین"),
        ("chetori", "چطوری"), ("mikham", "میخوام"),
    ]
    for latin, expected in tests:
        got = d.get(latin, "(missing)")
        status = "✓" if got == expected else "✗"
        print(f"  {status} {latin:<15} → {got:<10} (expected {expected})")


if __name__ == "__main__":
    main()
