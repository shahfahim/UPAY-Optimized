import re

with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add currentBalance back
missing_code = """
  // Safe parsing for balance
  const currentBalance = typeof home.balance === 'number' ? home.balance : 0

  const monthlyIncomeBase = home.forecast?.monthly_income ?? 12000
"""

code = code.replace("  const monthlyIncomeBase = home.forecast?.monthly_income ?? 12000", missing_code.lstrip('\n'))

with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Restored currentBalance")
