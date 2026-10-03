import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("className={ bsolute right-3", "className={`absolute right-3")
code = code.replace("text-white }>", "text-white ${dot}`}>")
code = code.replace("L(${num(badge.days_left)} দিন, ${badge.days_left}d)", "L(`${num(badge.days_left)} দিন`, `${badge.days_left}d`)")

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

with open('web/src/pages/flows/Npsb.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("{ id: FAM-,", "{ id: `FAM-${uid}`,")

with open('web/src/pages/flows/Npsb.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed syntax errors!")
