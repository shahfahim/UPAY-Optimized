import re
with open('web/src/pages/hub/Ask.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('min-h-[60dvh]', 'min-h-[85dvh]')

with open('web/src/pages/hub/Ask.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated Ask.tsx to min-h-[85dvh]")
