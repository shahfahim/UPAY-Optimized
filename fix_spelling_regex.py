import re
with open('backend/hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    code = f.read()

# I will replace any incorrect version of "niche" before "পুরো হিসাব দেখানো হলো:"
pattern = r'সবচেয়ে ভালো পথ হলো NPSB বা সরাসরি পেমেন্ট।.*?পুরো হিসাব দেখানো হলো:'
replacement = 'সবচেয়ে ভালো পথ হলো NPSB বা সরাসরি পেমেন্ট। নিচে পুরো হিসাব দেখানো হলো:'

new_code = re.sub(pattern, replacement, code)
if new_code != code:
    print("Replaced successfully")
else:
    print("Pattern not found!")

with open('backend/hishab/llm/fallback.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
