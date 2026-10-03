import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# 1. Update Normalizer
norm_file = 'backend/hishab/llm/normalizer.py'
with open(norm_file, 'r', encoding='utf-8') as f:
    norm = f.read()

new_phrases = """    # ─── New Natural Vibes (Tour, Family, etc) ──────────────────────────────
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
"""
if '"kishe"' not in norm:
    norm = norm.replace('    # ─── extreme typos (low literacy) ──────────────────────────────────────', new_phrases + '    # ─── extreme typos (low literacy) ──────────────────────────────────────')
    with open(norm_file, 'w', encoding='utf-8') as f:
        f.write(norm)
    print("Normalizer expanded with natural vibe phrases.")

# 2. Update Fallback Intents
fb_file = 'backend/hishab/llm/fallback.py'
with open(fb_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Make transaction_route much broader:
# old: r"(কীভাবে|কিভাবে).* (পাঠাব|পাঠাতে|ট্রান্সফার|transfer|সেন্ড|send)|(নগদ|বিকাশ|npsb|ব্যাংক).* (কীভাবে|কিভাবে|পাঠাব)"
# new: r"(কীভাবে|কিভাবে|কিসে|kishe|kise|কোন ওয়েতে).* (পাঠাব|পাঠাতে|ট্রান্সফার|transfer|সেন্ড|send)|(নগদ|বিকাশ|npsb|ব্যাংক|মাকে|maa ke|kakeo).* (কীভাবে|কিভাবে|পাঠাব|কিসে|kishe)"
import ast

def replace_intent_regex(text, intent_name, new_regex):
    # Find the line like `("intent_name", r"...")`
    pattern = r'\(\s*["\']' + intent_name + r'["\']\s*,\s*r["\'](.*?)["\']\s*\)'
    match = re.search(pattern, text)
    if match:
        old_full = match.group(0)
        new_full = f'("{intent_name}", r"{new_regex}")'
        return text.replace(old_full, new_full)
    return text

text = replace_intent_regex(text, "transaction_route", r"(কীভাবে|কিভাবে|কিসে|kishe|kise).* (পাঠাব|পাঠাতে|ট্রান্সফার|সেন্ড)|(নগদ|বিকাশ|npsb|ব্যাংক|মা|বাবা|ভাই).* (কীভাবে|পাঠাব|কিসে)|পাঠাব.*কিসে")

text = replace_intent_regex(text, "goal", r"target|save korbo|jomabo|jomate|dps khulbo|sanchoy|save|ট্যুর|tour|trip|কিনব|kinbo")

with open(fb_file, 'w', encoding='utf-8') as f:
    f.write(text)
print("Fallback intents updated with expert natural rules.")
