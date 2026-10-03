import re

path = 'backend/hishab/llm/fallback.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('নীચે', 'নিচে')

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed spelling error in fallback.py")
