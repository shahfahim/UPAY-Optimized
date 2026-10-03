import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

# Using regex to replace the background-color and background-image properties in .app-frame
old_css = """  background-color: #e3e9f0;
  background-image: 
    repeating-linear-gradient(120deg, rgba(11, 78, 162, 0.12) 0px, rgba(11, 78, 162, 0.12) 1.5px, transparent 1.5px, transparent 30px),
    repeating-linear-gradient(60deg, rgba(11, 78, 162, 0.12) 0px, rgba(11, 78, 162, 0.12) 1.5px, transparent 1.5px, transparent 30px),
    repeating-linear-gradient(0deg, rgba(11, 78, 162, 0.1) 0px, rgba(11, 78, 162, 0.1) 1.5px, transparent 1.5px, transparent 17.32px);"""

new_css = """  background-color: #f4f7fb;
  background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
  background-size: 20px 20px;"""

if old_css in code:
    code = code.replace(old_css, new_css)
else:
    print("Could not find the exact old CSS string. Using regex fallback...")
    code = re.sub(r'  background-color: #e3e9f0;.*?transparent 17\.32px\);', new_css, code, flags=re.DOTALL)

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

print("Reverted to clean dot grid!")
