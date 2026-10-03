import re
with open('web/src/pages/auth/Splash.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace "হিসাব" and "hishab" with the logo and "upay prototype"
old_block = """<div className="flex animate-fade-in flex-col items-center leading-none">
            <span className="text-5xl font-bold text-upay-blue">হিসাব</span>
            <span className="mt-2 font-[Inter] text-sm font-semibold tracking-wide text-ink/60">hishab</span>
          </div>"""
new_block = """<div className="flex animate-fade-in flex-col items-center leading-none">
            <img src="/upay-logo.png" alt="upay logo" className="h-16 w-auto object-contain" />
            <span className="mt-2 font-[Inter] text-sm font-semibold tracking-wide text-ink/60">upay prototype</span>
          </div>"""
code = code.replace(old_block, new_block)

with open('web/src/pages/auth/Splash.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Splash.tsx updated with logo")
