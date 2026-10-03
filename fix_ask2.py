import re
with open('web/src/pages/hub/Ask.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('className="flex min-h-[85dvh] flex-col', 'className="flex flex-1 min-h-[85dvh] flex-col')

with open('web/src/pages/hub/Ask.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated Ask.tsx to be flex-1")
