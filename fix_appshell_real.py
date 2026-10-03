import os

path_shell = 'web/src/components/AppShell.tsx'
with open(path_shell, 'r', encoding='utf-8') as f:
    code_shell = f.read()

code_shell = code_shell.replace("L('Upay Prototype', 'Upay Prototype')}", "L('হিসাব', 'Hishab')}")

with open(path_shell, 'w', encoding='utf-8') as f:
    f.write(code_shell)

print("Fixed AppShell.")
