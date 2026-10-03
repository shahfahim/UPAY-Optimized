import re

with open('web/src/pages/Home.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_str = "{ icon: 'request', bn: 'রিকোয়েস্ট মানি', en: 'Request Money' },"
new_str = "{ icon: 'map-pin', bn: 'এজেন্ট খুঁজুন', en: 'Find Agent', to: '/app/agents', hishab: true },"

if old_str in code:
    print("Found exact string!")
else:
    # Try regex fallback
    code = re.sub(r"\{\s*icon:\s*'request',\s*bn:\s*'[^']+',\s*en:\s*'Request Money'.*?\},", new_str, code)
    print("Used regex!")

with open('web/src/pages/Home.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

