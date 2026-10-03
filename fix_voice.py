import re

with open('web/src/lib/voice.ts', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('export function listenBn(): Promise<string> {', 'export function listenVoice(lang: string = \'bn-BD\'): Promise<string> {')
code = code.replace("r.lang = 'bn-BD'", "r.lang = lang")

with open('web/src/lib/voice.ts', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated voice.ts to accept lang param!")
