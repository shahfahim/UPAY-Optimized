import re
with open('backend/hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "পুরো হিসাব দেখানো হলো" in line or "সবচেয়ে ভালো পথ" in line:
        print(f"Line {i+1}: {line.strip()}")
