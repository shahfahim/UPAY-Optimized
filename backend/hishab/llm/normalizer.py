"""Banglish → Bangla normalizer — run this BEFORE sending user text to the LLM or fallback engine.
Dramatically improves intent detection accuracy for Banglish-typing users.
"""

from __future__ import annotations

import re

# Core Banglish → Bangla word map (order matters: longer phrases first)
_PHRASE_MAP: list[tuple[str, str]] = [
    # --- greetings ---
    ("assalamualaikum", "আসসালামু আলাইকুম"),
    ("walaikum assalam", "ওয়ালাইকুম আস্সালাম"),
    ("ki khobor", "কী খবর"),
    ("kemon acho", "কেমন আছো"),
    ("kemn acho", "কেমন আছো"),
    ("kem acho", "কেমন আছো"),
    ("thik ache", "ঠিক আছে"),
    ("thik achhi", "ঠিক আছি"),
    ("dhonnobad", "ধন্যবাদ"),
    ("shuvo", "শুভ"),
    # --- acknowledgment ---
    ("okay", "ঠিক আছে"),
    ("salam", "সালাম"),
    # --- money & balance ---
    ("koto taka ache", "কত টাকা আছে"),
    ("taka koto ache", "টাকা কত আছে"),
    ("wallet e koto", "ওয়ালেটে কত"),
    ("belence koto", "ব্যালেন্স কত"),
    ("balence koto", "ব্যালেন্স কত"),
    ("balance koto", "ব্যালেন্স কত"),
    ("belence", "ব্যালেন্স"),
    ("balence", "ব্যালেন্স"),
    ("balance", "ব্যালেন্স"),
    ("koto taka", "কত টাকা"),
    ("taka ache", "টাকা আছে"),
    ("taka nei", "টাকা নেই"),
    ("taka shesh", "টাকা শেষ"),
    ("taka kobe shesh hobe", "টাকা কবে শেষ হবে"),
    # --- spending ---
    ("kharoch korte parbo", "খরচ করতে পারব"),
    ("kharoch kothay jay", "খরচ কোথায় যায়"),
    ("kharoch kothay gelo", "খরচ কোথায় গেলো"),
    ("aaj koto kharoch", "আজ কত খরচ"),
    ("ajke koto kharoch", "আজকে কত খরচ"),
    ("aaj koto", "আজ কত"),
    ("kharoch", "খরচ"),
    # --- savings ---
    ("save korbo", "সঞ্চয় করব"),
    ("save korte chai", "সঞ্চয় করতে চাই"),
    ("bachabo", "বাঁচাব"),
    ("bachaibo", "বাঁচাব"),
    ("joma dibo", "জমা দেব"),
    ("joma ache", "জমা আছে"),
    ("joma korbo", "জমা করব"),
    ("joma", "জমা"),
    ("saving", "সঞ্চয়"),
    ("save", "সঞ্চয়"),
    # --- shortfall ---
    ("taka shesh hobe", "টাকা শেষ হবে"),
    ("taka kobe shesh", "টাকা কবে শেষ"),
    ("taka shesh", "টাকা শেষ"),
    ("taka chalbe", "টাকা চলবে"),
    ("taka nei", "টাকা নেই"),
    ("koto din chalbe", "কত দিন চলবে"),
    ("maser sheshe", "মাসের শেষে"),
    ("mas er sheshe", "মাসের শেষে"),
    ("tanatani", "টানাটানি"),
    # standalone taka → টাকা (for "wallet e koto taka" etc.)
    ("taka", "টাকা"),
    # --- cash-out ---
    ("cashout", "ক্যাশ আউট"),
    ("cash out", "ক্যাশ আউট"),
    ("cash-out", "ক্যাশ আউট"),
    ("agent theke", "এজেন্ট থেকে"),
    # --- DPS ---
    ("dps korbo", "DPS করব"),
    ("dps ki", "DPS কী"),
    ("monthly joma", "মাসিক জমা"),
    ("kisti", "কিস্তি"),
    # --- identity / help ---
    ("tumi ke", "তুমি কে"),
    ("ki korte paro", "কী করতে পারো"),
    ("ki koro", "কী করো"),
    ("sahajjo koro", "সাহায্য করো"),
    ("help lagbe", "সাহায্য লাগবে"),
    ("kivabe kaj koro", "কীভাবে কাজ করো"),
    # --- complaint ---
    ("kaj hocche na", "কাজ হচ্ছে না"),
    ("kaj hochhe na", "কাজ হচ্ছে না"),
    ("andaze", "আন্দাজে"),
    ("faltu", "ফালতু"),
    ("pagol", "পাগল"),
    ("vul", "ভুল"),
    # --- general ---
    ("hisab", "হিসাব"),
    ("income", "আয়"),
    ("korbo", "করব"),
    ("nibo", "নেব"),
    ("dibo", "দেব"),
    ("parbo", "পারব"),
    ("jabo", "যাব"),
    ("kemn", "কেমন"),
    ("kmn", "কেমন"),
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
