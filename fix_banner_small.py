import re

path = 'web/src/pages/Home.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the previous render logic
old_render = r'<button onClick=\{\(\) => navigate\(BANNERS\[b\]\.to\)\}\s*className="relative flex w-full items-center justify-center rounded-2xl bg-white overflow-hidden shadow-\[0_4px_15px_-3px_rgba\(0,0,0,0\.1\)\] active:scale-\[0\.98\] transition-all">\s*<img key=\{b\} src=\{BANNERS\[b\]\.img\} className="animate-fade-in w-full h-auto object-contain" alt="Offer Banner" />\s*</button>'

new_render = """<button onClick={() => navigate(BANNERS[b].to)}
          className="relative flex h-[110px] w-full items-center justify-center rounded-2xl bg-white overflow-hidden shadow-sm border border-slate-100 active:scale-[0.98] transition-all">
          <img key={b} src={BANNERS[b].img} className="animate-fade-in h-full w-full object-contain p-0.5" alt="Offer Banner" />
        </button>"""

if re.search(old_render, code):
    code = re.sub(old_render, new_render, code, flags=re.DOTALL)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Updated Home.tsx successfully.")
else:
    print("Could not find the exact pattern. Let me try a broader regex.")
    old_render_broad = r'<button onClick=\{\(\) => navigate\(BANNERS\[b\]\.to\)\}.*?</button>'
    code = re.sub(old_render_broad, new_render, code, flags=re.DOTALL)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Updated Home.tsx with broader regex.")
