import re

with open('web/src/pages/savings/SavingsHome.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace specifically the title for the 'bank' icon item
old_pattern = r"\{ icon: 'bank', bn: 'সঞ্চয়', en: 'Savings', ai: true, to: '/app/savings/dps',"
new_pattern = r"{ icon: 'bank', bn: 'Smart DPS', en: 'Smart DPS', ai: true, to: '/app/savings/dps',"

code = re.sub(old_pattern, new_pattern, code)

with open('web/src/pages/savings/SavingsHome.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated SavingsHome.tsx!")
