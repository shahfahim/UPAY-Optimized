import re

path = 'web/src/pages/hub/Ask.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('bg-slate-100/80', 'bg-slate-100')

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Made background solid slate-100.")
