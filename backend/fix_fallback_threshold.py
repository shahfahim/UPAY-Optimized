import re

with open('hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Lower ML threshold
code = code.replace('_ML_THRESHOLD = 0.6', '_ML_THRESHOLD = 0.35')

# 2. Add 'overview' and 'hisab dao' to status intent regex
code = code.replace(
    r'|kemon cholche|',
    r'|kemon cholche|hisab dao|overview|amar overview|total hisab|'
)

code = code.replace(
    r'|taka nai|',
    r'|taka nai|keno|'
)

with open('hishab/llm/fallback.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("fallback.py updated!")
