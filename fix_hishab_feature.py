import re

# 1. Fix AppShell.tsx (Bottom Nav)
path_shell = 'web/src/components/AppShell.tsx'
with open(path_shell, 'r', encoding='utf-8') as f:
    code_shell = f.read()
code_shell = code_shell.replace("L('Upay Prototype', 'Upay Prototype')<span", "L('হিসাব', 'Hishab')<span")
with open(path_shell, 'w', encoding='utf-8') as f:
    f.write(code_shell)

# 2. Fix HubLayout.tsx (Top Header)
path_hub = 'web/src/pages/hub/HubLayout.tsx'
with open(path_hub, 'r', encoding='utf-8') as f:
    code_hub = f.read()
code_hub = code_hub.replace('<h1 className="text-lg font-bold">Upay Prototype</h1>', '<h1 className="text-lg font-bold">হিসাব</h1>')
with open(path_hub, 'w', encoding='utf-8') as f:
    f.write(code_hub)

print("Restored feature name back to Hishab.")
