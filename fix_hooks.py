import re

with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Pattern to capture the hooks
hooks_pattern = r"(  const \[view, setView\] = useState\w*<.*?>\('all'\)\n  const \[monthOffset, setMonthOffset\] = useState\('0'\))"

# Find the hooks
hooks_match = re.search(hooks_pattern, code)
if hooks_match:
    hooks_str = hooks_match.group(1)
    
    # Remove them from the old location
    code = code.replace(hooks_str, "")
    
    # Place them immediately after useApi
    use_api_pattern = r"(const \{ data: home, error, loading, reload \} = useApi\(\(\) => api\.home\(uid\), \[uid\]\))"
    replacement = f"\\1\n\n{hooks_str}"
    
    code = re.sub(use_api_pattern, replacement, code)
    
    with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Fixed React Hook order")
else:
    print("Could not find hooks to move")
