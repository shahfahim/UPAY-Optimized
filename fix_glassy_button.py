import os

path_shell = 'web/src/components/AppShell.tsx'
with open(path_shell, 'r', encoding='utf-8') as f:
    code = f.read()

old_classes = "bg-[#ffd500] text-[#083b7a] font-extrabold shadow-[0_4px_12px_rgba(255,213,0,0.4)] ring-[2px] ring-[#ffd500]/50"
new_classes = "bg-white/15 backdrop-blur-md border border-white/20 text-white font-extrabold shadow-[0_4px_12px_rgba(0,0,0,0.15)] ring-[1px] ring-white/30"

if old_classes in code:
    code = code.replace(old_classes, new_classes)
    with open(path_shell, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully updated classes to glassy!")
else:
    print("Could not find the exact class string.")
