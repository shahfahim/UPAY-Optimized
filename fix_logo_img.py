import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the fallback SVG with the exact image
old_fallback = """<svg viewBox="0 0 100 100" className="w-full h-full" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="100" height="100" fill="#ffffff"/>
                <text x="50" y="60" fontSize="38" fontWeight="900" fontFamily="Arial, sans-serif" fill="#0b4ea2" textAnchor="middle" letterSpacing="-1.5">upay</text>
              </svg>"""

new_fallback = """<img src="/upay-logo.png" alt="Upay Logo" className="w-full h-full object-contain p-1" />"""

code = code.replace(old_fallback, new_fallback)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Replaced fallback SVG with the provided logo image!")
