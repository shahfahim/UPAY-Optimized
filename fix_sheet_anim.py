import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    '--animate-rise: rise 800ms cubic-bezier(0.16, 1, 0.3, 1) both;',
    '--animate-rise: rise 400ms cubic-bezier(0.16, 1, 0.3, 1) both;\n  --animate-backdrop: fade-in 300ms ease-out both;'
)

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

with open('web/src/components/ui.tsx', 'r', encoding='utf-8') as f:
    ui = f.read()

ui = ui.replace(
    'className="fixed inset-0 z-50 flex items-end justify-center bg-black/40"',
    'className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 animate-backdrop"'
)

with open('web/src/components/ui.tsx', 'w', encoding='utf-8') as f:
    f.write(ui)

print("Sheet animations enhanced!")
