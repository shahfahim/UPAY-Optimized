import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_avatar = """<div className="flex size-11 items-center justify-center rounded-full bg-white text-base font-bold text-[#0b4ea2] ring-2 ring-white/70 shadow-sm">
            {shell?.avatar_initials ?? '👤'}
          </div>"""

new_avatar = """<div className="flex size-11 items-center justify-center rounded-full bg-white text-[#0b4ea2] ring-2 ring-white/70 shadow-sm overflow-hidden">
            {shell && (shell as any).profile_pic ? (
              <img src={(shell as any).profile_pic} alt="Profile" className="w-full h-full object-cover" />
            ) : (
              <svg viewBox="0 0 100 100" className="w-full h-full" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="100" height="100" fill="#ffffff"/>
                <text x="50" y="60" fontSize="38" fontWeight="900" fontFamily="Arial, sans-serif" fill="#0b4ea2" textAnchor="middle" letterSpacing="-1.5">upay</text>
              </svg>
            )}
          </div>"""

code = code.replace(old_avatar, new_avatar)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Avatar replaced with Upay logo!")
