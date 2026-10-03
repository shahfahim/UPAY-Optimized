import re

# 1. Update index.css
with open('web/src/index.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Insert variable
css = css.replace('--animate-glow: glow 2s ease-in-out infinite alternate;', 
                  '--animate-glow: glow 2s ease-in-out infinite alternate;\n    --animate-page-enter: page-enter 300ms cubic-bezier(0.25, 0.46, 0.45, 0.94) both;')

# Insert keyframes
keyframes = """@keyframes page-enter {
  0% { opacity: 0; transform: translateX(12px) scale(0.99); }
  100% { opacity: 1; transform: translateX(0) scale(1); }
}
@keyframes glow {"""
css = css.replace('@keyframes glow {', keyframes)

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(css)

# 2. Update AppShell.tsx
with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    tsx = f.read()

# Fix import
tsx = tsx.replace("import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'", 
                  "import { Link, NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom'")

# Use location hook
tsx = tsx.replace("const [demoName, setDemoName] = useState<string | null>(null)", 
                  "const [demoName, setDemoName] = useState<string | null>(null)\n  const location = useLocation()")

# Wrap Outlet
old_outlet = """        <main className="flex-1 bg-surface pb-4">
          <Outlet />
        </main>"""

new_outlet = """        <main className="flex-1 bg-surface pb-4 overflow-hidden relative">
          <div key={location.pathname} className="animate-page-enter w-full min-h-full">
            <Outlet />
          </div>
        </main>"""

tsx = tsx.replace(old_outlet, new_outlet)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(tsx)

print("CSS and AppShell updated with page transition animations!")
