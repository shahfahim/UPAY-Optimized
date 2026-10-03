import re

with open('web/src/pages/Home.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# I will re-write the TILES array properly
old_pattern = r"\{ icon: 'request', bn: 'রিকোয়েস্ট মানি', en: 'Request Money' \},"

new_tiles_insertion = """{ icon: 'map-pin', bn: 'এজেন্ট খুঁজুন', en: 'Find Agent', to: '/app/agents', hishab: true },
  { icon: 'pay', bn: 'মেক পেমেন্ট', en: 'Make Payment', to: '/app/pay?type=merchant_pay' },
  { icon: 'gift', bn: 'রেফার & আর্ন', en: 'Refer & Earn' },
  { icon: 'npsb', bn: 'এনপিএসবি', en: 'NPSB', to: '/app/npsb', hishab: true },
  { icon: 'grid', bn: 'উপায় পেমেন্ট', en: 'upay Payment', to: '/app/payments' },
  { icon: 'add', bn: 'অ্যাড মানি', en: 'Add Money' },
  { icon: 'request', bn: 'রিকোয়েস্ট মানি', en: 'Request Money' },"""

# Let's just use regex to replace from 'request' down to 'add'
regex_pattern = r"\{\s*icon:\s*'request'[\s\S]*?\{\s*icon:\s*'add'[^}]+\},"

code = re.sub(regex_pattern, new_tiles_insertion, code)

with open('web/src/pages/Home.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Tiles updated!")
