import re

with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the Bar component line
code = re.sub(r"<Bar dataKey=\"value\" radius=\[.*?\] background=\{\{.*?\}\} />",
              r"<Bar dataKey=\"value\" radius={[6, 6, 0, 0]} />", code)

# Ensure tap highlight is transparent on the wrapper
code = code.replace('className="h-48 w-full [&_svg]:outline-none select-none"',
                    'className="h-48 w-full select-none" style={{ WebkitTapHighlightColor: \'transparent\' }}')

with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Overview updated successfully")
