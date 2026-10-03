import re

with open('web/src/pages/savings/Pockets.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's fix the add/delete onClick to call the API!
# Find the delete button
delete_pattern = r"onClick=\{\(\) => \{ setDeletedPockets\(\[\.\.\.deletedPockets, p\.name\]\); setMsg\(L\('পকেট ডিলিট করা হয়েছে', 'Pocket deleted'\)\) \}\}"
new_delete = """onClick={async () => { 
                      try {
                        setData(await api.deletePocket(uid, p.name)); 
                        setMsg(L('পকেট ডিলিট করা হয়েছে', 'Pocket deleted'))
                      } catch (e) {
                        setMsg('Error')
                      }
                    }}"""
code = re.sub(delete_pattern, new_delete, code)

# Find the add button
add_pattern = r"onClick=\{\(\) => \{\s*const name = window\.prompt\(L\('নতুন পকেটের নাম দিন:', 'Enter new pocket name:'\)\)\s*if \(name\) \{\s*setAddedPockets\(\[\.\.\.addedPockets, \{ name: 'custom_' \+ Date\.now\(\), name_bn: name, balance: 0, goal: null, progress: null \}\]\)\s*setMsg\(L\('নতুন পকেট তৈরি হয়েছে', 'New pocket created'\)\)\s*\}\s*\}\}"
new_add = """onClick={async () => {
            const name = window.prompt(L('নতুন পকেটের নাম দিন:', 'Enter new pocket name:'))
            if (name) {
              try {
                setData(await api.addPocket(uid, 'custom_' + Date.now(), name))
                setMsg(L('নতুন পকেট তৈরি হয়েছে', 'New pocket created'))
              } catch (e) {
                setMsg('Error')
              }
            }
          }}"""
code = re.sub(add_pattern, new_add, code)

with open('web/src/pages/savings/Pockets.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated Pockets.tsx to call real API!")
