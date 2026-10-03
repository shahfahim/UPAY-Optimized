import re
with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('<main className="flex flex-col flex-1 bg-surface overflow-hidden relative">', 
                    '<main className="flex flex-col flex-1 bg-surface overflow-y-auto relative">')

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

with open('web/src/pages/hub/Ask.tsx', 'r', encoding='utf-8') as f:
    ask = f.read()

ask = ask.replace('<div className="flex h-full flex-col', '<div className="flex flex-1 flex-col')

with open('web/src/pages/hub/Ask.tsx', 'w', encoding='utf-8') as f:
    f.write(ask)

print("Updated flex layout")
