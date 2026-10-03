import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

old_css = """  background-color: #eef1f5;
  background-image: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M20 20.5V18H0v-2h20v-2H0v-2h20v-2H0V8h20V6H0V4h20V2H0V0h22v20h2V0h2v20h2V0h2v20h2V0h2v20h2V0h2v20h2v2H20v-1.5zM0 20h2v20H0V20zm4 0h2v20H4V20zm4 0h2v20H8V20zm4 0h2v20h-2V20zm4 0h2v20h-2V20zm4 4h20v2H20v-2zm0 4h20v2H20v-2zm0 4h20v2H20v-2zm0 4h20v2H20v-2z' fill='%230b4ea2' fill-opacity='0.03' fill-rule='evenodd'/%3E%3C/svg%3E");"""

new_css = """  background-color: #e2e8f0;
  background-image: 
    linear-gradient(rgba(11, 78, 162, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(11, 78, 162, 0.06) 1px, transparent 1px);
  background-size: 24px 24px;"""

code = code.replace(old_css, new_css)

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

print("Background updated to distinct CSS grid!")
