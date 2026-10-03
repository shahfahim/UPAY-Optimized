import re

with open('web/src/api/client.ts', 'r', encoding='utf-8') as f:
    code = f.read()

new_methods = """  savings: (uid: string) => req<Savings>('GET', `${u(uid)}/savings`),
  addPocket: (uid: string, pocket: string, name_bn: string) => req<Savings>('POST', `${u(uid)}/savings/pockets/${pocket}`, { name_bn }),
  deletePocket: (uid: string, pocket: string) => req<Savings>('DELETE', `${u(uid)}/savings/pockets/${pocket}`),"""

code = code.replace("  savings: (uid: string) => req<Savings>('GET', `${u(uid)}/savings`),", new_methods)

with open('web/src/api/client.ts', 'w', encoding='utf-8') as f:
    f.write(code)

print("Added API methods to frontend client!")
