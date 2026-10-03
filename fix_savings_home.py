import re

with open('web/src/pages/savings/SavingsHome.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("bn: 'ডিপিএস', en: 'DPS', ai: false", "bn: 'Smart DPS', en: 'Smart DPS', ai: true")

with open('web/src/pages/savings/SavingsHome.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("SavingsHome DPS name updated!")
