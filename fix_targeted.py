import re

def targeted_replace():
    # 1. Fix ui.tsx (TextMark)
    path_ui = 'web/src/components/ui.tsx'
    with open(path_ui, 'r', encoding='utf-8') as f:
        code_ui = f.read()
    
    # We want to replace the whole TextMark component to be clean.
    old_textmark = r"""export function TextMark\(\{ size = 'md' \}: \{ size\?: 'md' \| 'lg' \}\) \{
  const big = size === 'lg'
  return \(
    <div className="flex flex-col items-center leading-none">
      <span className=\{`font-bold text-upay-blue \$\{big \? 'text-5xl' : 'text-2xl'\}`\}>.*?</span>
      <span className=\{`mt-1 font-\[Inter\] font-semibold tracking-wide text-ink/60 \$\{big \? 'text-sm' : 'text-\[10px\]'\}`\}>
        .*?
      </span>
    </div>
  \)
\}"""
    
    new_textmark = """export function TextMark({ size = 'md' }: { size?: 'md' | 'lg' }) {
  const big = size === 'lg'
  return (
    <div className="flex flex-col items-center leading-none">
      <span className={`font-bold text-upay-blue ${big ? 'text-4xl' : 'text-xl'}`}>Upay Prototype</span>
    </div>
  )
}"""
    code_ui = re.sub(old_textmark, new_textmark, code_ui, flags=re.DOTALL)
    with open(path_ui, 'w', encoding='utf-8') as f:
        f.write(code_ui)


    # 2. Fix HubLayout.tsx (Top Header)
    path_hub = 'web/src/pages/hub/HubLayout.tsx'
    with open(path_hub, 'r', encoding='utf-8') as f:
        code_hub = f.read()
    code_hub = re.sub(r'<h1 className="text-lg font-bold">L\([^\)]+\)</h1>', '<h1 className="text-lg font-bold">Upay Prototype</h1>', code_hub)
    code_hub = re.sub(r'<h1 className="text-lg font-bold">.*?</h1>', '<h1 className="text-lg font-bold">Upay Prototype</h1>', code_hub)
    with open(path_hub, 'w', encoding='utf-8') as f:
        f.write(code_hub)


    # 3. Fix AppShell.tsx (Bottom Nav)
    path_shell = 'web/src/components/AppShell.tsx'
    with open(path_shell, 'r', encoding='utf-8') as f:
        code_shell = f.read()
    # Find the nav item for hishab
    code_shell = code_shell.replace("L('হিসাব', 'Hishab')", "L('Upay Prototype', 'Upay Prototype')")
    with open(path_shell, 'w', encoding='utf-8') as f:
        f.write(code_shell)


    # 4. Fix index.html
    path_html = 'web/index.html'
    with open(path_html, 'r', encoding='utf-8') as f:
        code_html = f.read()
    code_html = re.sub(r'<title>.*?</title>', '<title>Upay Prototype</title>', code_html)
    with open(path_html, 'w', encoding='utf-8') as f:
        f.write(code_html)

targeted_replace()
print("Targeted branding completed.")
