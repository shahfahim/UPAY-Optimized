import os

path = 'web/src/components/PinPad.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the keys.map button styling
old_key_btn = 'className="h-14 rounded-xl bg-surface text-xl font-semibold active:bg-line"'
new_key_btn = 'className="h-14 rounded-xl bg-slate-200 border border-slate-300 shadow-sm text-xl font-bold text-slate-800 active:bg-slate-300 active:scale-95 transition-all"'

code = code.replace(old_key_btn, new_key_btn)

# Replace the backspace button styling
old_bs_btn = 'className="h-14 rounded-xl text-lg text-muted active:bg-surface"'
new_bs_btn = 'className="flex items-center justify-center h-14 rounded-xl text-xl text-slate-600 bg-slate-200/60 border border-slate-300 active:bg-slate-300 active:scale-95 transition-all"'
code = code.replace(old_bs_btn, new_bs_btn)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated PinPad styles.")
