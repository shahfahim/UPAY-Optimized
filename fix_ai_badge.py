import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_ai_span = '<span className="text-[9px] font-extrabold text-upay-blue italic">AI</span>'
new_ai_span = '<span className="rounded-[4px] bg-[#0b4ea2] px-1 py-[1px] text-[8px] font-bold text-white not-italic shadow-sm">AI</span>'

code = code.replace(old_ai_span, new_ai_span)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("AI badge updated to match user design!")
