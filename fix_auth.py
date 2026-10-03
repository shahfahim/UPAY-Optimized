import re

def inject_auth_header(filepath, title_bn, title_en):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    old_header = r'<div className="flex items-center gap-3 bg-upay-yellow px-4 py-3">\s*<Link to="/welcome" aria-label=\{L\(\'পেছনে\', \'Back\'\)\} className="text-xl">←</Link>\s*<span className="font-semibold">\{L\(\'.*?\', \'.*?\'\)\}</span>\s*</div>'
    
    new_header = f"""<div className="relative flex items-center gap-3 overflow-hidden bg-[#ffd500] px-4 py-4 shadow-[0_4px_20px_-5px_rgba(0,0,0,0.15)] z-10">
        
        {{/* Abstract Geometric Background - Main Deep Blue Split */}}
        <div className="absolute -top-10 -bottom-20 left-[55%] right-0 -skew-x-[24deg] bg-gradient-to-br from-[#083b7a] to-[#0b4ea2] shadow-[-12px_0_25px_rgba(0,0,0,0.3)] z-0"></div>
        
        {{/* Abstract Geometric Background - Accent Light Blue Split */}}
        <div className="absolute -top-10 -bottom-20 left-[85%] right-0 -skew-x-[24deg] bg-[#1a64c4] shadow-[-6px_0_15px_rgba(0,0,0,0.2)] z-0"></div>

        {{/* Subtle Halftone/Dot Pattern Overlay */}}
        <div className="absolute inset-0 pointer-events-none mix-blend-overlay opacity-15 z-0" style={{{{
          backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
          backgroundSize: '16px 16px'
        }}}}></div>

        <Link to="/welcome" aria-label={{L('পেছনে', 'Back')}} className="relative z-10 text-2xl font-bold text-slate-900 drop-shadow-[0_1px_1px_rgba(255,255,255,0.8)] pb-1">←</Link>
        <span className="relative z-10 font-bold text-[17px] text-slate-900 drop-shadow-[0_1px_1px_rgba(255,255,255,0.8)]">{{L('{title_bn}', '{title_en}')}}</span>
      </div>"""
      
    code = re.sub(old_header, new_header, code)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)

inject_auth_header('web/src/pages/auth/Login.tsx', 'লগইন', 'Log in')
inject_auth_header('web/src/pages/auth/Register.tsx', 'রেজিস্ট্রেশন', 'Registration')
print("Auth headers upgraded.")
