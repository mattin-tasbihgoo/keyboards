#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_dict.py — Generate fingilish_dict.json for the Keyman keyboard

This script generates a Latin→Persian dictionary where keys are
how users ACTUALLY TYPE Fingilish (with vowels), not consonant skeletons.

Sources:
  1. MANUAL dict: hand-verified Fingilish for common words (highest priority)
  2. NAMES dict: common Persian proper names (highest priority)
  3. Auto-generated from wordlist via improved transliteration (lower priority)

Output: fingilish_dict.json (consumed by build_calljs.py)

Lookup at runtime:  exact key → norm(key) → algorithmic fallback
Norm collapses:     u↔oo↔o, ei↔ey↔i, aa→a, ee→i, x→kh, q→gh, w→v, ph→f

To add words: edit the MANUAL dict below, re-run this script.
"""

import json, re, csv
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent

# ============================================================
# SHARED NORMALIZATION — must match norm() in ConvertWord.call_js
# and searchTermToKey in the lexical model
# ============================================================
def norm(s):
    """Collapse spelling variants to a canonical Latin key."""
    s = s.lower()
    # Strip apostrophes and Arabizi digits (2=ء, 3=ع) — dict keys are bare
    s = re.sub(r"['\u201923]", '', s)
    # c → s before e/i/y (cinema→sinema), else c → k; 'ch' protected
    s = re.sub(r'c(?=[eiy])', 's', s)
    s = re.sub(r'c(?!h)', 'k', s)
    # Word-final consonant+y → i  (kardy → kardi)
    s = re.sub(r'([^aeiou])y$', r'\1i', s)
    # Word-final 'eh' → 'e'  (kardeh → karde, ageh → age)
    s = re.sub(r'eh$', 'e', s)
    # Consonant equivalences
    s = s.replace('x', 'kh')
    s = s.replace('q', 'gh')
    s = s.replace('w', 'v')
    s = s.replace('ph', 'f')
    # Long vowels → short
    s = s.replace('aa', 'a')
    s = s.replace('oo', 'o')
    s = s.replace('ee', 'i')
    s = s.replace('ou', 'o')
    # u/oo equivalence: u → o  (khub → khob, shuru → shoro)
    s = s.replace('u', 'o')
    # ei/ey → i  (kheili → khili, kheyli → khili)
    s = s.replace('ey', 'i')
    s = s.replace('ei', 'i')
    # y → i everywhere (saye→saie, miyam→miiam→miam, khyaboon→khiabon)
    s = s.replace('y', 'i')
    # Collapse doubled letters
    s = re.sub(r'(.)\1+', r'\1', s)
    return s


def skeleton(s):
    """Vowel-skeleton key (tier-3 lookup): Persian doesn't write short
    vowels, so the auto Persian→Latin generator drops them (کردی→'krdi')
    while typists write them ('kardi'). Both collapse to the same skeleton:
    initial vowel → 'a' (written alef), final char kept (written letter),
    middle a/e/o stripped (unwritten short vowels)."""
    if len(s) < 2:
        return s
    head = s[0]
    if head in 'aeou':
        head = 'a'
    body = s[1:]
    if len(body) > 1:
        body = re.sub(r'[aeo]', '', body[:-1]) + body[-1]
    return head + body


# ============================================================
# MANUAL DICTIONARY — human-verified Fingilish spellings
# Add new words here! Format: "persian": ["primary", "variant1", "variant2", ...]
# The first entry is the canonical spelling.
# ============================================================
MANUAL = {
    "عالی": ["aali"],  # fix: was unreachable ("ali" belongs to the name)
    # Function words
    "که": ["ke"], "رو": ["ro", "roo"], "به": ["be"], "من": ["man"],
    "و": ["va", "o"], "از": ["az"], "تو": ["to", "too"], "اون": ["oon", "un"],
    "این": ["in", "een"], "یه": ["ye"], "می": ["mi"], "نه": ["na", "nah", "noh"],
    "با": ["ba"], "در": ["dar"], "ما": ["ma"], "هم": ["ham"],
    "بود": ["bood", "bud"], "تا": ["ta"], "اگه": ["age", "ageh"],
    "همه": ["hame", "hameh"], "هر": ["har"], "اما": ["ama", "amma"],
    "یا": ["ya"], "چون": ["chon", "choon"], "پس": ["pas"],
    "دیگه": ["dige", "digeh"], "هنوز": ["hanooz", "hanuz"],
    "حالا": ["hala", "haala"], "فقط": ["faghat", "faqat"],
    "خب": ["khob"], "اینجا": ["inja", "injaa"],
    "اونجا": ["onja", "oonja"], "الان": ["alan", "alaan", "aalan"],
    "شاید": ["shayad", "shaayad"], "حتی": ["hata", "hatta"],
    "بعد": ["baad"], "مثل": ["mesl", "mesle"],
    "همین": ["hamin", "hameen"], "پیدا": ["peyda", "peida"],
    "هیچ": ["hich", "heech"], "یکی": ["yeki"],
    "واقعا": ["vaghan", "vaqean"], "اصلا": ["aslan"],
    "البته": ["albate", "albatteh"], "لطفا": ["lotfan", "lotfa"],
    "یعنی": ["yani", "yaani"],
    # --- NEWLY ADDED common words ---
    "برای": ["baraye", "baraaye"],
    "حتما": ["hatman", "hatmen"],
    "هیچی": ["hichi", "heechi"],
    "مگه": ["mage", "mageh"],
    "ای": ["ey", "ei"],
    "بعضی": ["bazi", "ba'zi"],
    "چیزی": ["chizi"],
    "چیز": ["chiz"],
    "کسی": ["kasi"],
    "اگر": ["agar"],
    "ولی": ["vali"],
    "خودش": ["khodesh"],
    "خودم": ["khodam"],
    "خودت": ["khodet"],
    "بهش": ["behesh"],
    "بهم": ["behem"],
    "بهت": ["behet"],
    "ازش": ["azash"],
    "باهاش": ["bahash"],
    "براش": ["barash"],

    # Common verbs — present
    "باید": ["bayad", "baayad"], "باشه": ["bashe", "baasheh"],
    "کن": ["kon"], "کنم": ["konam", "konem"], "کنی": ["koni"],
    "کنه": ["kone", "koneh"], "کنیم": ["konim"],
    "کنید": ["konid", "konin"], "کنند": ["konand", "konan"],
    "میکنم": ["mikonam", "mikonem", "mikunam"],
    "میکنی": ["mikoni", "mikuni"],
    "میکنه": ["mikone", "mikoneh", "mikune"],
    "میکنیم": ["mikonim"],
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
    "چرا": ["chera", "cheraa"], "چطور": ["chetor", "chetoor", "chetowr", "chetour"],
    "چطوری": ["chetori", "chetoori", "cheturi"],
    "چطوره": ["chetoreh", "chetooreh"],
    "کجا": ["koja", "kojaa"], "کجایی": ["kojai", "kojayi"],
    "کی": ["ki", "key"], "کدوم": ["kodoom", "kodum"],
    "چند": ["chand", "chan"], "چیکار": ["chikar", "chikaar"],
    "چقدر": ["cheqadr", "cheghadr"], "چجوری": ["chejoori", "chejuri"],

    # Adjectives/adverbs
    "خیلی": ["kheili", "kheyli", "xeili", "xeyli", "khili"],
    "خوب": ["khoob", "khub", "xoob", "xob"],
    "خوبه": ["khobe", "khoobe", "khubeh", "khube"],
    "خوبی": ["khobi", "khoobi", "khubi"],
    "بد": ["bad"], "بزرگ": ["bozorg", "bozorgh"],
    "کوچیک": ["kuchik", "koochik", "kuchek", "kochik"],
    "زیاد": ["ziad", "ziyad", "ziyaad"],
    "کم": ["kam"], "زود": ["zood", "zud"],
    "دیر": ["dir", "deer"], "تند": ["tond"],
    "سخت": ["sakht"], "راحت": ["rahat", "raahat"],
    "درست": ["dorost", "dorust"],
    "بهتر": ["behtar"], "بهترین": ["behtarin"],
    "بدتر": ["badtar"],
    "خوشحال": ["khoshhal", "khoshhaal"],
    "ناراحت": ["narahat", "naarahat"],

    # Greetings/social
    "سلام": ["salam", "salaam"], "ممنون": ["mamnoon", "mamnun"],
    "مرسی": ["mersi", "merci"], "خوشبختم": ["khoshbakhtam"],
    "خداحافظ": ["khodahafez", "khodaafez"],
    "ببخشید": ["bebakhshid", "bebakhshin", "bebakhsid"],
    "متاسفم": ["motasefam", "mota2sefam"],
    "تبریک": ["tabrik", "tabreek"],

    # Nouns — common
    "دوست": ["doost", "dust", "doust"],
    "خونه": ["khune", "khuneh", "khooneh"],
    "خانه": ["khaneh", "khaaneh"], "خانواده": ["khanevade", "khaanevadeh"],
    "ماشین": ["mashin", "maashin"], "روز": ["rooz", "ruz"],
    "شب": ["shab"], "امروز": ["emrooz", "emruz"],
    "فردا": ["farda", "fardaa"], "دیروز": ["dirooz", "diruz"],
    "دیشب": ["dishab"],
    "آره": ["are", "aareh"],
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
    "دایی": ["dayi", "daayi", "daei", "daii"], "عمه": ["amme", "ammeh", "ame", "ameh"],
    "دانشگاه": ["daneshgah", "daaneshgaah"],
    "مدرسه": ["madrese", "madreseh"],
    "بیمارستان": ["bimarestan", "bimaarestan"],
    "فرودگاه": ["forudgah", "foroodgaah"],
    "خیابان": ["khiaban", "khiyaabaan"],
    "شهر": ["shahr"], "کشور": ["keshvar"],
    "دنیا": ["donya", "donyaa", "dunya"], "زندگی": ["zendegi"],

    # Verbs — more
    "خوش": ["khosh", "khoosh"], "گذشت": ["gozasht", "guzasht"],
    "گذاشت": ["gozaasht", "guzaasht"],
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
    "شروع": ["shoru", "shoroo", "shuru"],
    "تموم": ["tamoom", "tamum"], "تمام": ["tamam", "tamaam"],
    "فراموش": ["faramush", "faraamoosh", "faramoosh"],
    "انجام": ["anjam", "anjaam"],
    "استفاده": ["estefade", "estefaadeh"],

    # More common words people use
    "عاشق": ["ashegh", "aasheq"],
    "قلب": ["ghalb", "qalb"], "عشق": ["eshgh"],
    "همیشه": ["hamishe", "hamisheh"],
    "دوباره": ["dobare", "dobareh", "dubaareh", "doobare"],
    "بیشتر": ["bishtar", "bishttar"],
    "قربان": ["ghorban", "qorbaan"],
    "احتمالا": ["ehtemaalan", "ehtemaala"],
    "مشکل": ["moshkel", "moshkul", "mushkel"],
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
    "بعدا": ["badan", "ba'dan"],
    "قبلا": ["ghablan", "qablan"],
    "مثلا": ["masalan", "mesalan"],
    "اولین": ["avalin", "avvalin"],
    "آخرین": ["akharin"],
    "نزدیک": ["nazdik", "nazdeek"],
    "دور": ["door", "dur"],
    # --- Words with consonantal و / hamze the auto-generator can't key ---
    "جواب": ["javab", "javaab"], "دیوار": ["divar", "deevar"],
    "آواز": ["avaz", "aavaaz"], "مسئله": ["masale", "masaleh", "mas'ale"],
    "او": ["oo", "u"], "نو": ["no"],
    "اول": ["aval", "avval"], "اوکی": ["ok", "okey", "oki"],
    # G-sound collision fixes (2026-07-10): high-frequency words that lost
    # their natural keys to auto/skel neighbors (گول, قزل, fallback junk)
    "گل": ["gol"], "غزل": ["ghazal", "qazal"],
    "قهوه": ["ghahve", "qahve", "ghahveh", "qahveh"],
    "قورمه": ["ghorme", "qorme", "ghormeh", "qormeh"],

    # --- کرد verb family: auto-generator drops the short 'a' (کردی→krdi) ---
    "کرد": ["kard"], "کردم": ["kardam"], "کردی": ["kardi", "kardy"],
    "کرده": ["karde", "kardeh"], "کردن": ["kardan"], "کردیم": ["kardim"],
    "کردید": ["kardid"], "کردین": ["kardin"], "کردند": ["kardand"],

    # --- Exact-tier shadowing fixes (2026-07-14): natural typed spellings
    # of high-frequency words were claimed by low-frequency homographs'
    # auto keys (bale→باله shadowed بله) or lost skel collisions. Found by
    # the frequency-inversion audit + conversational battery. ---
    "بله": ["bale", "baleh"],
    "درسته": ["doroste", "dorosteh"],
    "ظهر": ["zohr"],
    "ظاهر": ["zaher", "zaaher"],  # keeps zaher reachable after ظهر takes skel 'zhr'
    "عزیزم": ["azizam"], "عزیز": ["aziz"],
    "عشقم": ["eshgham", "eshgam"],
    "ممنونم": ["mamnoonam", "mamnunam"],
    "فدات": ["fadat"],
    "تعارف": ["taarof", "tarof"],
    "طرف": ["taraf"],
    # Displacement protection (2026-07-14): words whose skel slots were
    # taken by the shadowing fixes above get their natural raw keys back.
    "ظاهرا": ["zaheran", "zaaheran"], "عکاس": ["akkas", "akas"], "فلان": ["folan", "folaan"],  # protect taraf: taarof/tarof claim skel trf
    "خونم": ["khoonam", "khunam"], "خونت": ["khoonet", "khunet"],
    "دوستت": ["dooset", "doostet", "dustet", "duset"],
    "تشنم": ["teshnam"],
    "چهار": ["chahar", "chaar"],
    "ده": ["dah"], "صد": ["sad"],
    "فعلا": ["felan"],
    "تقریبا": ["taghriban"], "دقیقا": ["daghighan"], "کاملا": ["kamelan"],
    "عکس": ["aks", "ax"],
    "پلو": ["polo", "polow"],
    "خیابون": ["khiaboon", "khiabun", "khiyaboon"],
    "پایین": ["payin", "paiin", "paeen"],
    "هوای": ["havaye", "havaaye"], "هواتو": ["havato", "havaato"],
    "جای": ["jaye", "jaaye"],
    "بای": ["bye"],
    "تنگ": ["tang"],
    "کس": ["kas"],
    "صبح": ["sobh", "sob"],
    "همه\u200cچیز": ["hamechiz"],
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
    "ØªÙØ±Ø§Ù": ["tehran", "tehraan"],
    # --- user-reported name fixes (2026-07-17) ---
    "عباسیان": ["abbasian", "abasian"],
    "ثریا": ["soraya", "sorayya", "sorayeh"],
    "آمنه": ["ameneh", "amene"],
    "آوا": ["ava", "aava"],
    "فرزاد": ["farzad", "farzaad"],
    "تهرانی": ["tehrani"],  # modern form beats archaic طهرانی in bulk
    # aazar only: plain "azar" stays with the common word (word-wins policy)
    "آذر": ["aazar"],
}


# ============================================================
# IMPROVED PERSIAN→LATIN TRANSLITERATION for auto-generation
# Produces keys closer to what people actually type in Fingilish
# ============================================================
CONSONANTS = set('بپتثجچحخدذرزسشصضطظعغفقکگلمنهی')

# Multi-char Persian → Latin (checked first)
TRANSLIT_MULTI = {
    "خو": "kho",   # خوب→khob, خونه→khune (NOT khvo)
}

# Single-char mappings
TRANSLIT_SINGLE = {
    'ا': 'a', 'آ': 'a', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ث': 's',
    'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'z',
    'ر': 'r', 'ز': 'z', 'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's',
    'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': '', 'غ': 'gh', 'ف': 'f',
    'ق': 'gh', 'ک': 'k', 'گ': 'g', 'ل': 'l', 'م': 'm', 'ن': 'n',
    'ه': 'h', 'ی': 'i', 'ء': '', 'ئ': '',
    # و gets special handling below
}

def transliterate_for_dict(word):
    """
    Convert a Persian word to a reasonable Fingilish spelling.

    Key improvements over the old transliterate():
    - و between consonants → "oo" (not "v")
    - و after خ → handled by خو→"kho" multi-map
    - و word-final → "oo"
    - ه word-final → "e" (not "h")
    """
    if not word:
        return "?"

    chars = list(word)
    n = len(chars)
    result = ""
    i = 0

    while i < n:
        ch = chars[i]

        # Try multi-char mappings first
        if i + 1 < n:
            pair = chars[i] + chars[i + 1]
            if pair in TRANSLIT_MULTI:
                result += TRANSLIT_MULTI[pair]
                i += 2
                continue

        # و — context-dependent
        if ch == 'و':
            prev_is_consonant = (i > 0 and chars[i-1] in CONSONANTS)
            next_is_consonant = (i + 1 < n and chars[i+1] in CONSONANTS)
            next_is_end = (i + 1 >= n)

            if i == 0:
                # Word-initial و → "va"
                result += "va"
            elif i == 1 and chars[0] == 'ا':
                # Word-initial او = long vowel (اومد→oomad, اوکی→ooki);
                # NOT آ (آواز keeps consonantal v via the else branch)
                result += "oo"
            elif prev_is_consonant and (next_is_consonant or next_is_end):
                # و between consonants or at end = long vowel "oo"
                result += "oo"
            else:
                # و adjacent to a vowel letter = consonantal v
                # (جواب→javab, دیوار→divar, آواز→avaz)
                result += "v"
            i += 1
            continue

        # ه — word-final is usually "e" or "eh" (not "h")
        if ch == 'ه' and i == n - 1:
            result += "e"
            i += 1
            continue

        # Word-initial \u0639 (ayn) carries its vowel: emit 'a' so
        # \u0639\u0628\u0627\u0633 -> 'abas...' not 'bas...'. Mid-word stays ''.
        if ch == '\u0639' and i == 0:
            result += "a"
            i += 1
            continue

        # Standard single-char lookup
        if ch in TRANSLIT_SINGLE:
            result += TRANSLIT_SINGLE[ch]
        i += 1

    # Collapse triple+ repeated letters (but keep doubles like "oo")
    result = re.sub(r'(.)\1{2,}', r'\1\1', result)

    return result.strip() or "?"


# ============================================================
# BLOCKLIST — Latin words that should NOT trigger conversion
# (unless overridden by MANUAL for known Persian words)
# ============================================================
BLOCKLIST = {
    "am", "an", "as", "at", "by", "can",
    "did", "do", "get", "go", "got", "had", "has", "her", "him", "his",
    "how", "if", "is", "it", "its", "may", "me", "my",
    "not", "of", "on", "or", "our", "out", "say", "set", "she",
    "so", "up", "us", "use", "the", "was", "way", "who", "why",
}


def build_dict():
    """Build the Latin→Persian dictionary."""
    result = {}       # latin_key → persian_word  (final output)
    norm_bank = {}    # norm(key) → (persian, freq) for collision resolution
    manual_persian = set()

    # -----------------------------------------------------------
    # Tier 1: MANUAL entries (highest priority — exact keys)
    # -----------------------------------------------------------
    for persian, variants in MANUAL.items():
        manual_persian.add(persian)
        for latin in variants:
            lat = re.sub(r"['\u201923]", "", latin.lower())
            if lat not in result:
                result[lat] = persian
            elif result[lat] != persian:
                print(f"  WARNING: MANUAL key '{lat}' for {persian} already claimed by {result[lat]}")

    # -----------------------------------------------------------
    # Tier 2: NAMES (highest priority — exact keys)
    # -----------------------------------------------------------
    for persian, variants in NAMES.items():
        manual_persian.add(persian)
        for latin in variants:
            lat = re.sub(r"['\u201923]", "", latin.lower())
            if lat not in result:
                result[lat] = persian
            elif result[lat] != persian:
                print(f"  WARNING: NAMES key '{lat}' for {persian} already claimed by {result[lat]}")

    # Mark all MANUAL/NAMES norm keys as untouchable
    for persian, variants in {**MANUAL, **NAMES}.items():
        for latin in variants:
            nk = norm(latin.lower().replace("'", ""))
            norm_bank[nk] = (persian, float('inf'))

    # -----------------------------------------------------------
    # Tier 3: Auto-generate from wordlist
    # -----------------------------------------------------------
    wordlist_path = BASE_DIR / "fingilish.wordlist.tsv"
    if not wordlist_path.exists():
        print(f"  WARNING: {wordlist_path} not found, skipping auto-generation")
        return result, {}

    wordlist = []
    with wordlist_path.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                # Strip BiDi isolates (wrap_bidi.py wraps the wordlist in
                # place; build order must not matter)
                persian = re.sub('[\u2066-\u2069]', '', parts[0].strip())
                try:
                    freq = int(parts[1])
                except ValueError:
                    continue
                if not persian or not re.match(r'^[\u0600-\u06FF\u200c]+$', persian):
                    continue
                if re.match(r'^(.)\1+$', persian):
                    continue  # junk like آآآ / ههه
                wordlist.append((persian, freq))

    print(f"  Wordlist: {len(wordlist):,} Persian words loaded")

    auto_exact = 0
    auto_norm = 0
    for persian, freq in wordlist:
        if persian in manual_persian:
            continue

        latin = transliterate_for_dict(persian)
        if latin == "?" or len(latin) < 2:
            continue

        lat = latin.lower()

        # Store exact key if not taken and not blocklisted
        if lat not in result and lat not in BLOCKLIST:
            result[lat] = persian
            auto_exact += 1

        # Store under normalized key (highest freq wins)
        nk = norm(lat)
        if nk not in norm_bank or freq > norm_bank[nk][1]:
            norm_bank[nk] = (persian, freq)
            auto_norm += 1

    # Add norm_bank entries to result where exact key is missing
    norm_added = 0
    for nk, (persian, freq) in norm_bank.items():
        if nk not in result and nk not in BLOCKLIST:
            result[nk] = persian
            norm_added += 1

    print(f"  Auto-generated: {auto_exact:,} exact + {norm_added:,} norm-only entries")

    # -----------------------------------------------------------
    # Tier-4 skeleton bank: vowel-stripped keys, highest freq wins.
    # Rescues words whose auto key lost its short vowels (krdi/kardi).
    # -----------------------------------------------------------
    # -----------------------------------------------------------
    # Tier 3.5: BULK NAMES from names.tsv (build_names.py output).
    # WORD-WINS POLICY: only fills keys not already claimed. Never touches
    # norm_bank or the skeleton bank (zero displacement of word lookups).
    # Collisions are logged for review, not resolved.
    # -----------------------------------------------------------
    names_path = BASE_DIR / "names.tsv"
    bulk_added = 0
    collisions = []
    if names_path.exists():
        with names_path.open("r", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) != 4:
                    continue
                persian, variants, kind, rank = parts
                if persian in manual_persian:
                    continue
                for lat in variants.split(","):
                    for key in (lat, norm(lat)):
                        if len(key) < 2 or key in BLOCKLIST:
                            continue
                        if key not in result:
                            result[key] = persian
                            bulk_added += 1
                        elif result[key] != persian:
                            collisions.append((key, persian, result[key], kind, rank))
        print(f"  Bulk names: {bulk_added:,} keys added, {len(collisions):,} collisions -> existing kept")
        report = Path.home() / "Documents" / "Fingilish" / "namedata" / "collision_report.txt"
        try:
            with report.open("w", encoding="utf-8") as rf:
                rf.write("key\tname_wanted\tkept_existing\tkind\trank\n")
                for c in sorted(collisions, key=lambda x: (x[3] != "S", int(x[4]) if x[4].isdigit() and int(x[4]) > 0 else 10**9)):
                    rf.write("\t".join(c) + "\n")
        except OSError:
            pass
        # Alternates for the custom-1.0 banner model: for keys where a name
        # lost to an existing entry, record up to 3 ranked alternates.
        # Manual alternates: curated names that deliberately ceded their
        # plain key to a common word (word-wins) but must stay one tap away.
        MANUAL_ALTS = {
            "azar": ["آذر"],   # Azar the name/month behind the word
        }
        alts = {k: list(v) for k, v in MANUAL_ALTS.items()}
        # Bulk alternates: SURNAMES ONLY (frequency-ranked, real signal);
        # first-name dataset rows carry no frequency and include junk
        # spellings, so they are excluded from the banner's alternates.
        for key, wanted, kept, kind, rank in sorted(
                collisions, key=lambda x: (x[3] != "S",
                    int(x[4]) if x[4].isdigit() and int(x[4]) > 0 else 10**9)):
            if kind != "S":
                continue
            lst = alts.setdefault(key, [])
            if wanted not in lst and len(lst) < 3:
                lst.append(wanted)
        import json as _json
        with (BASE_DIR / "fng_model_alts.json").open("w", encoding="utf-8") as af:
            _json.dump(alts, af, ensure_ascii=False)
        print(f"  Alternates: {len(alts):,} keys -> fng_model_alts.json")

    # -----------------------------------------------------------
    # aa-variant post-pass: words/names starting with ALEF-MADDA (U+0622)
    # or AYN+ALEF whose key starts with single 'a' also get an 'aa' key,
    # so explicit "aa" typing (long-A letterform intent) hits the dict
    # before norm() can collapse it.
    # -----------------------------------------------------------
    aa_added = 0
    for lat, persian in list(result.items()):
        if not lat.startswith("a") or lat.startswith("aa"):
            continue
        if persian.startswith("\u0622") or persian.startswith("\u0639\u0627"):
            aa_key = "a" + lat
            if aa_key not in result:
                result[aa_key] = persian
                aa_added += 1
    print(f"  aa-variants: {aa_added:,} keys added")

    skel_bank = {}
    for nk, (persian, freq) in norm_bank.items():
        sk = skeleton(nk)
        if len(sk) >= 3 and sk not in BLOCKLIST:
            if sk not in skel_bank or freq > skel_bank[sk][1]:
                skel_bank[sk] = (persian, freq)
    skel = {sk: p for sk, (p, _) in skel_bank.items()}
    print(f"  Skeleton bank: {len(skel):,} entries")

    return result, skel


def main():
    d, skel = build_dict()

    d_sorted = dict(sorted(d.items()))
    skel_sorted = dict(sorted(skel.items()))

    out_path = BASE_DIR / "fingilish_dict.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump({"exact": d_sorted, "skel": skel_sorted}, f,
                  ensure_ascii=False, separators=(',', ':'))

    print(f"\nDictionary: {len(d_sorted)} exact + {len(skel_sorted)} skeleton → {out_path.name}")
    print(f"File size: {out_path.stat().st_size:,} bytes")

    # Verify key lookups (simulating runtime: exact → norm → skeleton → miss)
    def lookup(key):
        key = key.lower()
        if key in d: return d[key]
        bare = re.sub(r"['\u201923]", "", key)
        if bare != key and bare in d: return d[bare]
        nk = norm(key)
        if nk in d: return d[nk]
        sk = skeleton(nk)
        if sk in skel: return skel[sk]
        return "(miss)"

    print("\nVerification (exact → norm → miss):")
    tests = [
        # Core words
        ("salam", "سلام"), ("salaam", "سلام"), ("kheili", "خیلی"),
        ("xeili", "خیلی"), ("beram", "برم"), ("daneshgah", "دانشگاه"),
        ("dishab", "دیشب"), ("khaleh", "خاله"), ("va", "و"),
        ("khosh", "خوش"), ("bache", "بچه"),
        ("ali", "علی"), ("reza", "رضا"),
        ("mohammad", "محمد"), ("mattin", "متین"), ("matin", "متین"),
        ("chetori", "چطوری"), ("mikham", "میخوام"),
        # Expanded norm tests
        ("khub", "خوب"), ("khili", "خیلی"), ("mikunam", "میکنم"),
        ("cheturi", "چطوری"), ("shuru", "شروع"),
        # Missing word tests
        ("baraye", "برای"), ("hatman", "حتما"), ("hichi", "هیچی"),
        ("mage", "مگه"),
        # u↔oo variants
        ("dust", "دوست"), ("doost", "دوست"), ("doust", "دوست"),
        ("zud", "زود"), ("zood", "زود"),
        ("pul", "پول"), ("pool", "پول"),
        # c / y$ / eh$ / skeleton flexibility
        ("kardi", "کردی"), ("kardy", "کردی"), ("karde", "کرده"),
        ("kardeh", "کرده"), ("kardam", "کردم"), ("cheghadr", "چقدر"),
        ("kuchik", "کوچیک"), ("comak", "کمک"), ("cinema", "سینما"),
        # Collision fixes: each word must have its own reachable key
        ("bad", "بد"), ("baad", "بعد"), ("khab", "خواب"), ("khob", "خب"),
        ("gozasht", "گذشت"), ("gozaasht", "گذاشت"),
        # Consonantal و + hamze words
        ("javab", "جواب"), ("divar", "دیوار"), ("avaz", "آواز"),
        ("masale", "مسئله"), ("oo", "او"), ("u", "او"), ("no", "نو"),
        ("varzesh", "ورزش"),
        # Word-initial او = long vowel; اول stays reachable via MANUAL
        ("oomad", "اومد"), ("umad", "اومد"), ("oomadam", "اومدم"),
        ("aval", "اول"), ("ok", "اوکی"), ("oki", "اوکی"),
        # G-sound fixes; gool must still reach گول via its auto key
        ("gol", "گل"), ("gool", "گول"), ("ghazal", "غزل"),
        ("qahve", "قهوه"), ("ghahve", "قهوه"), ("ghorme", "قورمه"),
        # y→i normalization
        ("saye", "سایه"), ("miyam", "میام"), ("khyaboon", "خیابون"),
        # Apostrophe / Arabizi digit stripping in norm
        ("sa'at", "ساعت"), ("mota2sefam", "متاسفم"), ("mas'ale", "مسئله"),
 # Shadowing fixes (2026-07-14) - expectations from MANUAL to avoid RTL typos
 ("bale", "بله"),
 ("baleh", "بله"),
 ("doroste", "درسته"),
 ("dorosteh", "درسته"),
 ("zohr", "ظهر"),
 ("zaher", "ظاهر"),
 ("azizam", "عزیزم"),
 ("eshgham", "عشقم"),
 ("mamnoonam", "ممنونم"),
 ("fadat", "فدات"),
 ("taarof", "تعارف"),
 ("khoonam", "خونم"),
 ("khoonet", "خونت"),
 ("dooset", "دوستت"),
 ("doostet", "دوستت"),
 ("teshnam", "تشنم"),
 ("chahar", "چهار"),
 ("dah", "ده"),
 ("sad", "صد"),
 ("felan", "فعلا"),
 ("taghriban", "تقریبا"),
 ("daghighan", "دقیقا"),
 ("kamelan", "کاملا"),
 ("aks", "عکس"),
 ("ax", "عکس"),
 ("polo", "پلو"),
 ("khiaboon", "خیابون"),
 ("payin", "پایین"),
 ("paeen", "پایین"),
 ("havaye", "هوای"),
 ("havato", "هواتو"),
 ("jaye", "جای"),
 ("bye", "بای"),
 ("tang", "تنگ"),
 ("kas", "کس"),
 ("sob", "صبح"),
 ("daei", "دایی"),
 ("ame", "عمه"),
 ("ameh", "عمه"),
 ("bebakhsid", "ببخشید"),
 ("noh", "نه"),
 ("chan", "چند"),
 ("hamechiz", "همه\u200cچیز"),
 # Regression guards adjacent to the fixes
 ("akh", "آخ"),
 ("khob", "خب"),
 ("khoob", "خوب"),
 ("khub", "خوب"),
 ("taraf", "طرف"),
 ("dorost", "درست"),
 ("khanoom", "خانوم"),
 ("doost", "دوست"),
 ("dust", "دوست"),
 ("khiaban", "خیابان"),
    ]
    along = [
        # Names battery (2026-07-17, keyboard 1.7)
        ("abbasian", "\u0639\u0628\u0627\u0633\u06cc\u0627\u0646"),
        ("soraya", "\u062b\u0631\u06cc\u0627"),
        ("ameneh", "\u0622\u0645\u0646\u0647"),
        ("ava", "\u0622\u0648\u0627"),
        ("farzad", "\u0641\u0631\u0632\u0627\u062f"),
        ("azar", "\u0622\u0632\u0627\u0631"),
        ("aazar", "\u0622\u0630\u0631"),
        ("aali", "\u0639\u0627\u0644\u06cc"),
        ("aadi", "\u0639\u0627\u062f\u06cc"),
        ("aashegh", "\u0639\u0627\u0634\u0642"),
        ("aalan", "\u0627\u0644\u0627\u0646"),
        ("mohammadi", "\u0645\u062d\u0645\u062f\u06cc"),
        ("hosseini", "\u062d\u0633\u06cc\u0646\u06cc"),
        ("tehrani", "\u062a\u0647\u0631\u0627\u0646\u06cc"),
    ]
    tests.extend([(a, b) for a, b in along])
    
    ok = 0
    for latin, expected in tests:
        got = lookup(latin)
        status = "✓" if got == expected else "✗"
        if got == expected: ok += 1
        nk = norm(latin.lower())
        bare2 = re.sub(r"['\u201923]", "", latin.lower())
        via = "exact" if latin.lower() in d else ("bare" if bare2 in d else ("norm" if nk in d else ("skel" if skeleton(nk) in skel else "miss")))
        print(f"  {status} {latin:<15} → {got:<10} (expected {expected}) [{via}]")
    print(f"\n  {ok}/{len(tests)} passed")


if __name__ == "__main__":
    main()