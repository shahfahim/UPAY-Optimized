import re

with open('web/src/lib/format.ts', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the specific function implementation
old_func = """export function toBnDigits(s: string | number): string {
  return String(s).replace(/[0-9]/g, (d) => BN[Number(d)])
}"""
new_func = """export function toBnDigits(s: string | number): string {
  // User requested all digits remain in English globally
  return String(s)
}"""

code = code.replace(old_func, new_func)

with open('web/src/lib/format.ts', 'w', encoding='utf-8') as f:
    f.write(code)

print("format.ts updated to enforce English digits everywhere.")
