import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

old_css = """  background-color: #f4f7fb;
  background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
  background-size: 20px 20px;"""

new_css = """  background: linear-gradient(145deg, #eaeff5 0%, #dce4ee 100%);"""

if old_css in code:
    code = code.replace(old_css, new_css)
else:
    print("Could not find the exact old CSS string. Using regex fallback...")
    code = re.sub(r'  background-color: #f4f7fb;.*?background-size: 20px 20px;', new_css, code, flags=re.DOTALL)

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

print("Reverted to a clean, pattern-free gradient background!")
