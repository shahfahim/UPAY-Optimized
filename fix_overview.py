import re

with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Enhance shadows for cards to make them pop
code = code.replace(
    'className="border-slate-100 bg-white p-4 shadow-sm"',
    'className="border-white bg-white p-4 shadow-[0_8px_30px_rgb(0,0,0,0.06)] rounded-2xl"'
)

code = code.replace(
    'shadow-[0_8px_20px_-4px_rgba(0,0,0,0.05)] border-slate-100/50',
    'shadow-[0_8px_30px_rgb(0,0,0,0.06)] border-white'
)

code = code.replace(
    'className="border-slate-200 bg-white shadow-sm"',
    'className="border-white bg-white shadow-[0_8px_30px_rgb(0,0,0,0.06)]"'
)

with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Overview card shadows fixed!")
