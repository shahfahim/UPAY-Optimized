import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# 1. Update Fallback Intents
fb_file = 'backend/hishab/llm/fallback.py'
with open(fb_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Enhance transaction_route to catch "bank card", "npsb 300tk", "patabo", "kase", "tk"
def replace_intent_regex(text, intent_name, new_regex):
    pattern = r'\(\s*["\']' + intent_name + r'["\']\s*,\s*r["\'](.*?)["\']\s*\)'
    match = re.search(pattern, text)
    if match:
        old_full = match.group(0)
        new_full = f'("{intent_name}", r"{new_regex}")'
        return text.replace(old_full, new_full)
    return text

# Broaden transaction_route
old_route = r"(কীভাবে|কিভাবে|কিসে|kishe|kise).* (পাঠাব|পাঠাতে|ট্রান্সফার|সেন্ড)|(নগদ|বিকাশ|npsb|ব্যাংক|মা|বাবা|ভাই).* (কীভাবে|পাঠাব|কিসে)|পাঠাব.*কিসে"
new_route = r"(কীভাবে|কিভাবে|কিসে|kishe|kise|কোন ওয়েতে).* (পাঠাব|পাঠাতে|patabo|ট্রান্সফার|transfer|সেন্ড|send|দেয়া যায়)|(নগদ|বিকাশ|npsb|ব্যাংক|bank card|মাকে|maa ke|kakeo).* (কীভাবে|কিভাবে|পাঠাব|patabo|কিসে|kishe|করলে)|পাঠাব.*কিসে|bank card|npsb.*tk|npsb.*taka|npsb korba"
# Handle raw amount if we want, but better to just route "mayer kase patabo" properly.
# The user asked: "ami 500 taka npsb korba kivabe" -> has "npsb korba kivabe", should route to transaction_route
# "500 tk mayer kase patabo" -> has "patabo", so if we add patabo to normalizer, it works.

text = replace_intent_regex(text, "transaction_route", new_route)

# 2. Add to normalizer
norm_file = 'backend/hishab/llm/normalizer.py'
with open(norm_file, 'r', encoding='utf-8') as f:
    norm = f.read()

new_phrases = """    # ─── Recent Chat Fixes ──────────────────────────────
    ("patabo", "পাঠাব"),
    ("kase", "কাছে"),
    ("bank card", "ব্যাংক কার্ড"),
    ("npsb korba", "npsb করব"),
"""
if '"patabo"' not in norm:
    norm = norm.replace('    # ─── New Natural Vibes (Tour, Family, etc) ──────────────────────────────', new_phrases + '    # ─── New Natural Vibes (Tour, Family, etc) ──────────────────────────────')
    with open(norm_file, 'w', encoding='utf-8') as f:
        f.write(norm)

# Write fallback.py
with open(fb_file, 'w', encoding='utf-8') as f:
    f.write(text)

print("Chat intents expanded.")
