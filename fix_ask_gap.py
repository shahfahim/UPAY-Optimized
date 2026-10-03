import re

path = 'web/src/pages/hub/Ask.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update suggestions margin
code = code.replace('<div className="mt-3 flex gap-2 overflow-x-auto pb-1">', '<div className="mt-1 flex gap-2 overflow-x-auto pb-0">')

# 2. Update form margin
code = code.replace('className="sticky bottom-2 z-10 mt-3 flex items-end gap-2 rounded-3xl', 'className="sticky bottom-2 z-10 mt-1.5 flex items-end gap-2 rounded-3xl')

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Reduced gaps between suggestions and the chat form.")
