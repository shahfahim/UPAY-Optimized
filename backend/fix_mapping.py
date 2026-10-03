import re

with open('hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    '"balance": "balance",',
    '"balance": "balance",\n    "shortfall": "shortfall",'
)

with open('hishab/llm/fallback.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Added shortfall mapping!")
