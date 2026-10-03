import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("className={ bsolute right-3", "className={`absolute right-3")
code = code.replace("text-white }", "text-white ${dot}`}")
code = code.replace("text-white ${dot}`}>", "text-white ${dot}`}")

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed syntax errors!")
