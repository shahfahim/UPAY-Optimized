import re

path = 'web/src/pages/hub/Ask.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'className="flex min-h-[60dvh] flex-col px-4 pb-6 bg-slate-100"',
    'className="flex min-h-[60dvh] flex-col px-4 pt-5 pb-6 bg-slate-100"'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Added top padding to the chat container.")
