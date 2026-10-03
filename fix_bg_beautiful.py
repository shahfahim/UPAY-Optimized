import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

old_css = """  background: linear-gradient(145deg, #eaeff5 0%, #dce4ee 100%);"""

new_css = """  background-color: #f4f7fb;
  background-image: 
    radial-gradient(circle at 10% 0%, rgba(255, 182, 0, 0.08) 0%, transparent 60%),
    radial-gradient(circle at 90% 100%, rgba(11, 78, 162, 0.08) 0%, transparent 60%),
    repeating-linear-gradient(45deg, rgba(11, 78, 162, 0.035) 0, rgba(11, 78, 162, 0.035) 1px, transparent 1px, transparent 16px);"""

if old_css in code:
    code = code.replace(old_css, new_css)
else:
    print("Fallback to regex...")
    code = re.sub(r'  background: linear-gradient\(145deg, #eaeff5 0%, #dce4ee 100%\);', new_css, code)

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

print("Applied gorgeous Ambient Pinstripe background!")
