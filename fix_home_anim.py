import re

with open('web/src/pages/Home.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add transition to max-height for smooth expand/collapse
code = code.replace(
    '<div className={`grid grid-cols-4 gap-y-4 ${expanded ? \'\' : \'overflow-hidden max-h-[170px]\'}`}>',
    '<div className={`grid grid-cols-4 gap-y-4 transition-all duration-500 ease-in-out ${expanded ? \'max-h-[500px]\' : \'overflow-hidden max-h-[170px]\'}`}>'
)

with open('web/src/pages/Home.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Home.tsx Grid animation enhanced!")
