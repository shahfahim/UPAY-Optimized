import re

with open('web/src/pages/hub/Ask.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace import
code = code.replace('listenBn', 'listenVoice')

# Insert state
if 'const [micLang' not in code:
    code = code.replace('const [listening, setListening] = useState(false)', "const [listening, setListening] = useState(false)\n  const [micLang, setMicLang] = useState<'bn-BD' | 'en-US'>('bn-BD')")

# Update mic function
code = code.replace('await listenVoice()', 'await listenVoice(micLang)')

# Add toggle button next to mic
old_ui = """          </div>
          {voice ? (
            <button type="button" onClick={() => void mic()}"""

new_ui = """          </div>
          {voice && (
            <button type="button" onClick={() => setMicLang(prev => prev === 'bn-BD' ? 'en-US' : 'bn-BD')} className="flex h-11 px-3 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-500 text-sm font-semibold hover:bg-slate-200 transition-colors">
              {micLang === 'bn-BD' ? 'BN' : 'EN'}
            </button>
          )}
          {voice ? (
            <button type="button" onClick={() => void mic()}"""

if old_ui in code:
    code = code.replace(old_ui, new_ui)

with open('web/src/pages/hub/Ask.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated Ask.tsx with BN/EN toggle!")
