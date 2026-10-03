import re

path = 'web/src/pages/Account.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the Profile Card
pattern = r'\s*\{/\* Profile Card \*/\}.*?(?=\{/\* Balances Grid \*/\})'

new_code = re.sub(pattern, '\n\n      {loading && <div className="mt-6"><Spinner /></div>}\n      {error && <div className="mt-4"><ErrorNote message={error} onRetry={reload} /></div>}\n      \n      ', code, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_code)
print("Removed Profile Card from Account.tsx")
