import re
with open('web/src/pages/hub/HubLayout.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('<div>', '<div className="flex flex-col h-full flex-1">')

with open('web/src/pages/hub/HubLayout.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated HubLayout.tsx")
