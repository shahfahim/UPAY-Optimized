import sys
import re

with open('backend/hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Update transaction_route
old_route = r'(কীভাবে|কিভাবে).* (পাঠাব|পাঠাতে|ট্রান্সফার|transfer|সেন্ড|send)|(নগদ|বিকাশ|npsb|ব্যাংক).* (কীভাবে|কিভাবে|পাঠাব)'
new_route = r'(কীভাবে|কিভাবে|কিসে|kishe|kise|কোন ওয়েতে).* (পাঠাব|পাঠাতে|ট্রান্সফার|transfer|সেন্ড|send|দেয়া যায়)|(নগদ|বিকাশ|npsb|ব্যাংক|maa ke|kakeo).* (কীভাবে|কিভাবে|পাঠাব|কিসে|kishe)'
text = text.replace(old_route, new_route)

# Wait, the string might not be exactly that. Let's just use regex substitution for the intents.
# Actually, replacing the whole INTENTS block is safer.
