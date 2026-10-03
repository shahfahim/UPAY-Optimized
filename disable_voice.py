import re

with open('web/src/pages/hub/Ask.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Remove speakBangla(a.text)
code = code.replace("        speakBangla(a.text)", "        // speakBangla(a.text) // Disabled by user request")

with open('web/src/pages/hub/Ask.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Voice reading disabled in Ask.tsx")
