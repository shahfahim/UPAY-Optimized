import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('backend/hishab/llm/fallback.py', encoding='utf-8') as f:
    lines = f.readlines()

# Show around line 199
for i, l in enumerate(lines[195:205], 196):
    print(i, repr(l))
