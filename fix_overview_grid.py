import re

with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# I need to completely remove the Grid Buttons section
# Let's find the start and end.
start_str = "{/* Grid Buttons */}"
end_str = "{/* Safe Spending (if you want to keep a small version of it) or just Lesson Card */}"
end_str_alt = "{/* Lesson */}"
end_str_alt_2 = "      <div className=\"px-4 mt-4 animate-slide-up\" style={{ animationDelay: \"300ms\" }}>"

start_idx = code.find(start_str)

# Look for the beginning of the next section
end_idx = code.find("      <div className=\"px-4 mt-4 animate-slide-up\"", start_idx)

if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + code[end_idx:]
    with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Grid Buttons removed successfully!")
else:
    print(f"Could not find exact block to remove. start_idx={start_idx}, end_idx={end_idx}")

