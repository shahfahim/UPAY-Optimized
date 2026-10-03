import re

with open('web/src/pages/savings/Dps.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace PageTitle
code = code.replace('PageTitle bn="ইসলামিক ডিপিএস" en="Islamic DPS"', 'PageTitle bn="Smart DPS" en="Smart DPS"')

# Inject a toggle right after <div className="space-y-3 px-3">
# But first we need a state for it
state_injection = "  const [pin, setPin] = useState('')\n  const [dpsType, setDpsType] = useState<'normal'|'islamic'>('islamic')\n"
code = code.replace("  const [pin, setPin] = useState('')", state_injection)

toggle_html = """        <div className="space-y-3 px-3">
          <div className="flex bg-white rounded-lg p-1 border border-slate-200">
            <button className={`flex-1 text-sm font-semibold py-2 rounded-md ${dpsType === 'normal' ? 'bg-upay-blue text-white' : 'text-slate-500'}`} onClick={() => setDpsType('normal')}>Normal DPS</button>
            <button className={`flex-1 text-sm font-semibold py-2 rounded-md ${dpsType === 'islamic' ? 'bg-upay-blue text-white' : 'text-slate-500'}`} onClick={() => setDpsType('islamic')}>Islamic DPS</button>
          </div>
"""
code = code.replace('        <div className="space-y-3 px-3">', toggle_html)

with open('web/src/pages/savings/Dps.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Smart DPS updated!")
