import re

with open('web/src/pages/auth/Welcome.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_header = r'<div className="flex items-center justify-between p-4">\s*<TextMark />\s*<button onClick=\{\(\) => setLang\(lang === \'bn\' \? \'en\' : \'bn\'\)\}\s*className="rounded-full bg-upay-blue/10 px-3 py-1 text-xs font-semibold text-upay-blue">\s*\{lang === \'bn\' \? \'English\' : \'বাংলা\'\}\s*</button>\s*</div>'

new_header = """<div className="relative overflow-hidden bg-[#ffd500] px-4 py-4 shadow-[0_4px_20px_-5px_rgba(0,0,0,0.15)] z-10 flex items-center justify-between">
        
        {/* Abstract Geometric Background - Main Deep Blue Split */}
        <div className="absolute -top-10 -bottom-20 left-[48%] right-0 -skew-x-[24deg] bg-gradient-to-br from-[#083b7a] to-[#0b4ea2] shadow-[-12px_0_25px_rgba(0,0,0,0.3)] z-0"></div>
        
        {/* Abstract Geometric Background - Accent Light Blue Split */}
        <div className="absolute -top-10 -bottom-20 left-[82%] right-0 -skew-x-[24deg] bg-[#1a64c4] shadow-[-6px_0_15px_rgba(0,0,0,0.2)] z-0"></div>

        {/* Subtle Halftone/Dot Pattern Overlay */}
        <div className="absolute inset-0 pointer-events-none mix-blend-overlay opacity-15 z-0" style={{
          backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
          backgroundSize: '16px 16px'
        }}></div>

        <div className="relative z-10 scale-[1.15] origin-left">
          <TextMark />
        </div>
        
        <button onClick={() => setLang(lang === 'bn' ? 'en' : 'bn')}
          className="relative z-10 rounded-full bg-white/10 text-white backdrop-blur-md shadow-sm border border-white/20 px-4 py-1.5 text-[13px] font-bold transition-transform active:scale-95">
          {lang === 'bn' ? 'English' : 'বাংলা'}
        </button>
      </div>"""

if re.search(old_header, code):
    code = re.sub(old_header, new_header, code)
    with open('web/src/pages/auth/Welcome.tsx', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Welcome.tsx header upgraded.")
else:
    print("Welcome.tsx header not found! Using fallback.")
