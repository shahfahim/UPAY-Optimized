import re

with open('hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'npsb.*????|npsb ???',
    'npsb'
)

with open('hishab/llm/fallback.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed fallback regex!")
