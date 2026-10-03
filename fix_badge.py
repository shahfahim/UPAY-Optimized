import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Change label: string to label: ReactNode
code = code.replace("label: string", "label: ReactNode")

# Remove the ugly absolute AI badge
bad_ai_badge = '<span className="absolute right-1 top-0 text-[10px] font-extrabold text-upay-blue italic drop-shadow-sm">AI</span>'
code = code.replace(bad_ai_badge, "")

# Now update the item call for hishab to pass the styled label
old_item_call = "        {item('/app/hishab', 'spark', L('হিসাব', 'Hishab'), ("
new_item_call = "        {item('/app/hishab', 'spark', <span className=\"flex items-center gap-0.5\">{L('হিসাব', 'Hishab')}<span className=\"text-[9px] font-extrabold text-upay-blue italic\">AI</span></span>, ("
code = code.replace(old_item_call, new_item_call)

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed AI badge position!")
