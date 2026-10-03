import re

path = 'web/src/pages/Home.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

old_render = r'<button onClick=\{\(\) => navigate\(BANNERS\[b\]\.to\)\}.*?</button>'

new_render = """<button onClick={() => navigate(BANNERS[b].to)}
          className="relative flex h-24 w-full items-center justify-center rounded-2xl overflow-hidden shadow-[0_3px_10px_-3px_rgba(0,0,0,0.15)] active:scale-[0.98] transition-all bg-upay-blue">
          <img key={b} src={BANNERS[b].img} className="animate-fade-in h-full w-full object-cover" alt="Offer Banner" />
        </button>"""

code = re.sub(old_render, new_render, code, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Reverted to the exact original shape (h-24 wide card) with object-cover.")
