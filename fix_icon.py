import re

with open('web/src/components/Icon.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

trash_path = "  trash: 'M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6',\n"

# Insert trash path after close
code = code.replace("  close: 'M18 6 6 18M6 6l12 12',", "  close: 'M18 6 6 18M6 6l12 12',\n" + trash_path)

with open('web/src/components/Icon.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Trash icon added to Icon.tsx!")
