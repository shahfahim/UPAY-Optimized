import re

with open('web/src/pages/savings/Pockets.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add state
if 'const [deletedPockets' not in code:
    code = code.replace("const [msg, setMsg] = useState('')", 
                        "const [msg, setMsg] = useState('')\n  const [deletedPockets, setDeletedPockets] = useState<string[]>([])\n  const [addedPockets, setAddedPockets] = useState<any[]>([])")

# Replace data.pockets.map with active pockets
if 'const displayPockets =' not in code:
    code = code.replace("if (!data) return null", 
                        "if (!data) return null\n\n  const displayPockets = [...data.pockets.filter(p => !deletedPockets.includes(p.name)), ...addedPockets]")
    code = code.replace("{data.pockets.map((p) => (", "{displayPockets.map((p) => (")
    code = code.replace("pockets={data.pockets}", "pockets={displayPockets}")

# Fix Delete button
code = re.sub(
    r"onClick=\{\(\) => setMsg\(L\('.*ডিলিট.*'.*\}\)",
    "onClick={() => { setDeletedPockets([...deletedPockets, p.name]); setMsg(L('পকেট ডিলিট করা হয়েছে', 'Pocket deleted')) }}",
    code
)

# Fix Add button
new_add = """onClick={() => {
            const name = window.prompt(L('নতুন পকেটের নাম দিন:', 'Enter new pocket name:'))
            if (name) {
              setAddedPockets([...addedPockets, { name: 'custom_' + Date.now(), name_bn: name, balance: 0, goal: null, progress: null }])
              setMsg(L('নতুন পকেট তৈরি হয়েছে', 'New pocket created'))
            }
          }}"""

code = re.sub(
    r"onClick=\{\(\) => setMsg\(L\('নতুন পকেট তৈরির ফিচার.*\}\)",
    new_add,
    code
)

with open('web/src/pages/savings/Pockets.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated Pockets.tsx with local state logic for Add and Delete!")
