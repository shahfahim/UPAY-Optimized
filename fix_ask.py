import re

with open('web/src/pages/hub/Ask.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Container
code = code.replace('<div className="flex min-h-[60dvh] flex-col px-3 pb-4">',
                    '<div className="flex min-h-[60dvh] flex-col px-4 pb-6 bg-slate-50/70">')

# 2. Top Info Box (AI badge + Welcome text)
old_info = '<div className="rounded-2xl bg-white p-4">'
new_info = '<div className="rounded-3xl bg-white p-5 shadow-sm border border-slate-100">'
code = code.replace(old_info, new_info)

# 3. User Bubble
code = code.replace('className="ml-10 rounded-2xl rounded-br-md bg-upay-blue px-3.5 py-2.5 text-white animate-slide-up"',
                    'className="ml-auto max-w-[85%] rounded-3xl rounded-tr-sm bg-upay-blue px-4 py-3 text-white shadow-md shadow-upay-blue/20 animate-slide-up"')

# 4. Bot Bubble
code = code.replace('className="mr-6 rounded-2xl rounded-bl-md border border-line bg-white px-3.5 py-2.5 animate-slide-up"',
                    'className="mr-auto max-w-[85%] rounded-3xl rounded-tl-sm border border-slate-100 bg-white px-4 py-3 text-slate-800 shadow-sm animate-slide-up"')

# 5. Form Input Container
old_form = '<form className="mt-2 flex items-end gap-2"'
new_form = '<form className="sticky bottom-2 z-10 mt-3 flex items-end gap-2 rounded-3xl bg-white/70 backdrop-blur-lg border border-white/50 p-2 shadow-[0_8px_30px_rgb(0,0,0,0.04)]"'
code = code.replace(old_form, new_form)

# 6. Textarea container
old_textarea_container = '<div className="flex-1 rounded-2xl border border-line bg-white px-3 py-1 focus-within:border-upay-blue">'
new_textarea_container = '<div className="flex-1 rounded-2xl bg-white/50 px-4 py-2 focus-within:bg-white focus-within:ring-1 focus-within:ring-upay-blue/50 transition-all border border-transparent">'
code = code.replace(old_textarea_container, new_textarea_container)

# 7. Loading bubble
code = code.replace('className="mr-6 flex items-center gap-2 rounded-2xl border border-line bg-white px-3.5 py-3 text-sm text-muted"',
                    'className="mr-auto max-w-[85%] flex items-center gap-2 rounded-3xl rounded-tl-sm border border-slate-100 bg-white px-4 py-3 text-sm text-muted shadow-sm"')

with open('web/src/pages/hub/Ask.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Ask.tsx UI upgraded with professional glassmorphism and rounded bubbles.")
