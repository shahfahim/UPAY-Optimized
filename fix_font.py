import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

# Remove Noto Sans Bengali import
code = re.sub(r"@import url\('https://fonts\.googleapis\.com/css2\?family=Noto\+Sans\+Bengali.*?swap'\);\n?", "", code)

# Change font-family rule to generic system-ui to perfectly match OS native Bengali (like bKash does)
code = re.sub(
    r"font-family:\s*'Noto Sans Bengali',\s*sans-serif;",
    r"font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';",
    code
)
# Also check if it's applied to body or .app-frame
# Usually tailwind's sans is used.
with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

print("Font updated to native system font!")
