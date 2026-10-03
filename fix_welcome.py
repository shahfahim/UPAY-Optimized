# -*- coding: utf-8 -*-
with open('web/src/pages/auth/Welcome.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_slides = '''const SLIDES = [
  { bn: 'দ্রুত এবং নিরাপদে টাকা লেনদেন করুন', en: 'Fast and secure transactions', icon: '💸' },
  { bn: 'সবচেয়ে কম খরচে বাড়িতে টাকা পাঠান', en: 'Send money home the cheapest way', icon: '🏠' },
  { bn: 'পয়সা থেকে DPS — ধাপে ধাপে সঞ্চয়', en: 'From paisa to DPS — save step by step', icon: '🌱' },
]
'''
start = -1
end = -1
for i, l in enumerate(lines):
    if l.startswith('const SLIDES'):
        start = i
    if start != -1 and l.strip() == ']':
        end = i
        break

if start != -1 and end != -1:
    lines[start:end+1] = [new_slides]

with open('web/src/pages/auth/Welcome.tsx', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Welcome.tsx updated')
