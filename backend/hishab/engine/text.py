"""Small Bangla text helpers shared by engine modules."""

from __future__ import annotations

_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

CATEGORY_BN = {
    "food_grocery": "বাজার", "rent": "বাড়ি ভাড়া", "family_support": "পরিবারে পাঠানো", "transport": "যাতায়াত",
    "mobile": "মোবাইল", "health": "চিকিৎসা", "education": "শিক্ষা", "utilities": "বিল", "shopping": "কেনাকাটা",
    "festival": "উৎসব", "other": "অন্যান্য", "income": "আয়",
}

POCKET_BN = {"emergency": "জরুরি", "eid": "ঈদ", "family": "বাড়ি", "education": "শিক্ষা", "paisa": "পয়সা",
             "custom": "নিজের"}


def bn_digits(s: str) -> str:
    return str(s).translate(_BN_DIGITS)


def bn_num(n: float) -> str:
    """Indian-grouped integer with Bangla digits: 150000 -> ১,৫০,০০০."""
    n = int(round(n))
    neg = n < 0
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if neg else "") + bn_digits(s)


def category_bn(cat: str) -> str:
    return CATEGORY_BN.get(cat, cat)
