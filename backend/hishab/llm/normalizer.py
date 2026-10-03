"""Banglish → Bangla normalizer — run this BEFORE sending user text to the LLM or fallback engine.
Dramatically improves intent detection accuracy for Banglish-typing users.
"""

from __future__ import annotations

import re

# Core Banglish → Bangla word map (order matters: longer phrases first)
_PHRASE_MAP: list[tuple[str, str]] = [
    # ─── greetings ────────────────────────────────────────────────────────────
    ("assalamualaikum",  "আসসালামু আলাইকুম"),
    ("walaikum assalam", "ওয়ালাইকুম আস্সালাম"),
    ("ki khobor",        "কী খবর"),
    ("kemon acho",       "কেমন আছো"),
    ("kemn acho",        "কেমন আছো"),
    ("kem acho",         "কেমন আছো"),
    ("thik ache",        "ঠিক আছে"),
    ("thik achhi",       "ঠিক আছি"),
    ("dhonnobad",        "ধন্যবাদ"),
    ("shuvo",            "শুভ"),
    ("okay",             "ঠিক আছে"),
    ("salam",            "সালাম"),

    # ─── acknowledgment ───────────────────────────────────────────────────────
    ("bujhechi",  "বুঝেছি"),
    ("bujhlam",   "বুঝলাম"),


    # ─── routing queries ──────────────────────────────────────────────────────
    ("nagad", "নগদ"),
    ("bkash", "বিকাশ"),
    ("bkashe", "বিকাশে"),
    ("pathabo", "পাঠাব"),
    ("kivabe pathabo", "কীভাবে পাঠাব"),
    ("kemne pathabo", "কীভাবে পাঠাব"),
    ("npsb theke", "npsb থেকে"),
    ("send money", "সেন্ড মানি"),
    # ─── Recent Chat Fixes ──────────────────────────────
    ("patabo", "পাঠাব"),
    ("kase", "কাছে"),
    ("bank card", "ব্যাংক কার্ড"),
    ("npsb korba", "npsb করব"),
    # ─── New Natural Vibes (Tour, Family, etc) ──────────────────────────────
    ("kishe", "কীভাবে"),
    ("kise", "কীভাবে"),
    ("krbo", "করব"),
    ("korbo", "করব"),
    ("maa ke", "মাকে"),
    ("ma ke", "মাকে"),
    ("tour", "ট্যুর"),
    ("tk", "টাকা"),
    ("jomabo", "জমাব"),
    ("save", "সঞ্চয়"),
    ("save krbo", "সঞ্চয় করব"),
    # ─── extreme typos (low literacy) ──────────────────────────────────────
    ("csh out", "ক্যাশ আউট"), ("cash ot", "ক্যাশ আউট"), ("kesh out", "ক্যাশ আউট"),
    ("casout", "ক্যাশ আউট"), ("kashout", "ক্যাশ আউট"), ("kyashout", "ক্যাশ আউট"),
    ("cash auot", "ক্যাশ আউট"), ("kes aut", "ক্যাশ আউট"), ("cashut", "ক্যাশ আউট"),
    ("cshut", "ক্যাশ আউট"),
    ("snd money", "সেন্ড মানি"), ("sen money", "সেন্ড মানি"), ("send mony", "সেন্ড মানি"),
    ("snd mny", "সেন্ড মানি"), ("send mani", "সেন্ড মানি"), ("send maney", "সেন্ড মানি"),
    ("sen mani", "সেন্ড মানি"), ("send moni", "সেন্ড মানি"),
    ("balenc", "ব্যালেন্স"), ("balns", "ব্যালেন্স"), ("valoance", "ব্যালেন্স"),
    ("balanc", "ব্যালেন্স"), ("balans", "ব্যালেন্স"), ("valance", "ব্যালেন্স"),
    ("byalans", "ব্যালেন্স"), ("balnce", "ব্যালেন্স"),
    ("hawlat", "হাওলাত"), ("haolat", "হাওলাত"), ("howlat", "হাওলাত"),
    ("holat", "হাওলাত"), ("hulat", "হাওলাত"), ("udar", "উধার"), ("dhar", "ধার"),
    ("ngd", "নগদ"), ("nagd", "নগদ"), ("nogod", "নগদ"), ("nogd", "নগদ"), ("nogot", "নগদ"),
    ("bks", "বিকাশ"), ("bikas", "বিকাশ"), ("bikash", "বিকাশ"), ("bksh", "বিকাশ"), ("vicash", "বিকাশ"),
    ("kivb", "কীভাবে"), ("kibabe", "কীভাবে"), ("kibave", "কীভাবে"), ("kemne", "কীভাবে"), ("kmne", "কীভাবে"),

    # ─── cashout queries ────────────────────────────────────────────────────────
    ("cashout korsi",    "ক্যাশ আউট করেছি"),
    ("cashout korechi",  "ক্যাশ আউট করেছি"),
    ("cash out korsi",   "ক্যাশ আউট করেছি"),
    ("koto bar cashout", "কতবার ক্যাশ আউট"),
    ("kotbar",           "কতবার"),
    ("koto bar",         "কতবার"),
    ("last 30 dine",     "গত ৩০ দিনে"),
    ("last 30dine",      "গত ৩০ দিনে"),
    ("last 7 dine",      "গত ৭ দিনে"),
    ("last month e",     "গত মাসে"),

    # ─── goal / savings queries ───────────────────────────────────────────────
    ("save korte parbo", "সঞ্চয় করতে পারব"),
    ("koto joma hobe",   "কত জমা হবে"),
    ("ki ki korle",      "কী কী করলে"),
    ("cholte parbe",     "চলতে পারবে"),
    ("kichu pabe",       "কিছু পাবে"),

    # ─── money & balance ──────────────────────────────────────────────────────
    ("koto taka ache",   "কত টাকা আছে"),
    ("taka koto ache",   "টাকা কত আছে"),
    ("wallet e koto",    "ওয়ালেটে কত"),
    ("wallet er taka",   "ওয়ালেটের টাকা"),
    ("belence koto",     "ব্যালেন্স কত"),
    ("balence koto",     "ব্যালেন্স কত"),
    ("balance koto",     "ব্যালেন্স কত"),
    ("belence",          "ব্যালেন্স"),
    ("balence",          "ব্যালেন্স"),
    ("balance",          "ব্যালেন্স"),
    ("koto taka",        "কত টাকা"),
    ("taka ache",        "টাকা আছে"),

    # ─── spending ─────────────────────────────────────────────────────────────
    ("kharoch korte parbo",  "খরচ করতে পারব"),
    ("kharoch korte pari",   "খরচ করতে পারি"),
    ("kharoch kothay jay",   "খরচ কোথায় যায়"),
    ("kharoch kothay gelo",  "খরচ কোথায় গেলো"),
    ("kharoch komabo",       "খরচ কমাব"),
    ("kharoch er hisab",     "খরচের হিসাব"),
    ("aaj koto kharoch",     "আজ কত খরচ"),
    ("ajke koto kharoch",    "আজকে কত খরচ"),
    ("aaj koto",             "আজ কত"),
    ("kharoch",              "খরচ"),

    # ─── savings & goal ───────────────────────────────────────────────────────
    ("save korbo",          "সঞ্চয় করব"),
    ("save korte chai",     "সঞ্চয় করতে চাই"),
    ("save korte parchhi",  "সঞ্চয় করতে পারছি"),
    ("bachabo",             "বাঁচাব"),
    ("bachaibo",            "বাঁচাব"),
    ("joma dibo",           "জমা দেব"),
    ("joma ache",           "জমা আছে"),
    ("joma korbo",          "জমা করব"),
    ("jomate parbo",        "জমাতে পারব"),
    ("jomate pari",         "জমাতে পারি"),
    ("jomate chai",         "জমাতে চাই"),
    ("jomate parchhi",      "জমাতে পারছি"),
    ("joma",                "জমা"),
    ("saving",              "সঞ্চয়"),
    ("save",                "সঞ্চয়"),

    # ─── shortfall ────────────────────────────────────────────────────────────
    ("taka shesh hobe ki",  "টাকা শেষ হবে কি"),
    ("taka shesh hobe",     "টাকা শেষ হবে"),
    ("taka kobe shesh",     "টাকা কবে শেষ"),
    ("taka shesh",          "টাকা শেষ"),
    ("taka chalbe",         "টাকা চলবে"),
    ("taka nei",            "টাকা নেই"),
    ("koto din chalbe",     "কত দিন চলবে"),
    ("maser sheshe",        "মাসের শেষে"),
    ("mas er sheshe",       "মাসের শেষে"),
    ("tanatani",            "টানাটানি"),
    ("taka kome jacche",    "টাকা কমে যাচ্ছে"),
    ("taka thakbe",         "টাকা থাকবে"),
    ("taka",                "টাকা"),   # standalone (last resort)

    # ─── cash-out ─────────────────────────────────────────────────────────────
    ("cashout korsi",  "ক্যাশ আউট করেছি"),
    ("cashout korechi","ক্যাশ আউট করেছি"),
    ("last 30dine",    "গত ৩০ দিনে"),
    ("last 30 din",    "গত ৩০ দিন"),
    ("koto bar",       "কতবার"),
    ("ktobar",         "কতবার"),
    ("cashout",        "ক্যাশ আউট"),
    ("cash out",       "ক্যাশ আউট"),
    ("cash-out",       "ক্যাশ আউট"),
    ("agent theke",    "এজেন্ট থেকে"),
    ("agent fee",      "এজেন্ট ফি"),
    ("fee komabo",     "ফি কমাব"),
    ("fee koto",       "ফি কত"),

    # ─── DPS ─────────────────────────────────────────────────────────────────
    ("dps ki",        "DPS কী"),
    ("dps korbo",     "DPS করব"),
    ("monthly joma",  "মাসিক জমা"),
    ("kisti",         "কিস্তি"),

    # ─── identity / help ──────────────────────────────────────────────────────
    ("tumi ke",         "তুমি কে"),
    ("ki korte paro",   "কী করতে পারো"),
    ("ki koro",         "কী করো"),
    ("sahajjo koro",    "সাহায্য করো"),
    ("help lagbe",      "সাহায্য লাগবে"),
    ("kivabe kaj koro", "কীভাবে কাজ করো"),

    # ─── advice ("ki korbo?") ─────────────────────────────────────────────────
    ("ki korbo ekhon",     "কী করব এখন"),
    ("ki korbo",           "কী করব"),
    ("ki korle",           "কী করলে"),
    ("ki kora uchit",      "কী করা উচিত"),
    ("taka bachate ki",    "টাকা বাঁচাতে কী"),
    ("kharoch komabo",     "খরচ কমাব"),
    ("ki korle valo hobe", "কী করলে ভালো হবে"),
    ("pরামর্শ dao",        "পরামর্শ দাও"),

    # ─── status ("ami ki bhalo korchi?") ─────────────────────────────────────
    ("ami ki bhalo korchi",     "আমি কি ভালো করছি"),
    ("ami ki bhalo achi",       "আমি কি ভালো আছি"),
    ("amar obostha kemon",      "আমার অবস্থা কেমন"),
    ("amar financial condition","আমার আর্থিক অবস্থা"),
    ("hisab thik ache",         "হিসাব ঠিক আছে"),
    ("kemon cholche",           "কেমন চলছে"),
    ("ami ki save korte parchhi", "আমি কি সঞ্চয় করতে পারছি"),
    ("amar progress",           "আমার প্রগতি"),

    # ─── next income ("kobe taka ashbe?") ────────────────────────────────────
    ("kobe taka ashbe",    "কবে টাকা আসবে"),
    ("kobe income ashbe",  "কবে আয় আসবে"),
    ("next income kobe",   "পরের আয় কবে"),
    ("income kobe ashbe",  "আয় কবে আসবে"),
    ("kobe pabo",          "কবে পাব"),

    # ─── comparison ───────────────────────────────────────────────────────────
    ("age cheyey beshi",   "আগের চেয়ে বেশি"),
    ("age cheyey kom",     "আগের চেয়ে কম"),
    ("last month vs",      "গত মাসের তুলনায়"),
    ("age er tulonay",     "আগের তুলনায়"),

    # ─── complaint ────────────────────────────────────────────────────────────
    ("kaj hocche na",   "কাজ হচ্ছে না"),
    ("kaj hochhe na",   "কাজ হচ্ছে না"),
    ("kaje ashe na",    "কাজে আসে না"),
    ("andaze",          "আন্দাজে"),
    ("faltu",           "ফালতু"),
    ("pagol",           "পাগল"),
    ("vul",             "ভুল"),
    ("bekar",           "বেকার"),
    ("matha kharap",    "মাথা খারাপ"),

    # ─── emergency ────────────────────────────────────────────────────────────
    ("joruri taka lagbe", "জরুরি টাকা লাগবে"),
    ("joruri taka",       "জরুরি টাকা"),
    ("joruri",            "জরুরি"),
    ("ekhoni taka",       "এখনই টাকা"),
    ("ekhuni taka",       "এখনই টাকা"),
    ("udhar lagbe",       "উধার লাগবে"),
    ("udhar",             "উধার"),
    ("taka lagbe",        "টাকা লাগবে"),

    # ─── specific amount check ────────────────────────────────────────────────
    ("kinbo ki",   "কিনব কি"),
    ("kinbo",      "কিনব"),
    ("kinte parbo","কিনতে পারব"),

    # ─── general verbs ────────────────────────────────────────────────────────
    ("hisab",   "হিসাব"),
    ("income",  "আয়"),
    ("korbo",   "করব"),
    ("korle",   "করলে"),
    ("nibo",    "নেব"),
    ("dibo",    "দেব"),
    ("parbo",   "পারব"),
    ("parchhi", "পারছি"),
    ("jabo",    "যাব"),
    ("ashbe",   "আসবে"),
    ("thakbe",  "থাকবে"),
    ("hobe",    "হবে"),
    ("kemn",    "কেমন"),
    ("kmn",     "কেমন"),
    ("kobe",    "কবে"),
    ("keno",    "কেন"),
    ("kothay",  "কোথায়"),
    ("kivabe",  "কীভাবে"),
    ("koto",    "কত"),
    ("ki",      "কী"),
]

# Compile patterns for efficiency
_COMPILED: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r'\b' + re.escape(src) + r'\b', re.IGNORECASE), tgt)
    for src, tgt in _PHRASE_MAP
]


def normalize(text: str) -> str:
    """Normalize Banglish input to improve intent detection.

    Replaces known Banglish words/phrases with their Bangla equivalents.
    Preserves original case and structure for pure Bangla/English text.
    Numbers (500, 1000 etc.) are preserved as-is.
    """
    result = text
    for pattern, replacement in _COMPILED:
        result = pattern.sub(replacement, result)
    return result


def detect_language(text: str) -> str:
    """Detect whether input is primarily 'bangla', 'english', or 'banglish'."""
    bangla_chars = len(re.findall(r'[\u0980-\u09FF]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    total = bangla_chars + latin_chars
    if total == 0:
        return "unknown"
    if bangla_chars / total > 0.7:
        return "bangla"
    if latin_chars / total > 0.9:
        return "english"
    return "banglish"
