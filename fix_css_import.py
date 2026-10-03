import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("@import \"tailwindcss\";\n@import url", "@import url")
code = "@import \"tailwindcss\";\n" + code

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed CSS!")
