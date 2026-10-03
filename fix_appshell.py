import re
with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace main
code = code.replace('<main className="flex-1 bg-surface pb-4 overflow-hidden relative">', 
                    '<main className="flex flex-col flex-1 bg-surface overflow-hidden relative">')

# Replace the animate-page-enter div
code = code.replace('<div key={location.pathname} className="animate-page-enter w-full min-h-full">',
                    '<div key={location.pathname} className="animate-page-enter flex flex-col flex-1 w-full">')

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated AppShell.tsx")
