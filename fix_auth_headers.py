import re

def update_file(path, label_en, label_bn):
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Find the plain header
    pattern = r'<div className="flex items-center gap-3 bg-upay-yellow px-4 py-3">.*?</div>'
    
    # We construct the new geometric header for Login and Register
    new_header = f"""<div className="relative flex items-center gap-3 bg-[#ffd500] px-4 py-3 overflow-hidden shadow-[0_2px_10px_-2px_rgba(0,0,0,0.15)] z-10">
        <div className="absolute -top-10 -bottom-20 left-[48%] right-0 -skew-x-[24deg] bg-gradient-to-br from-[#083b7a] to-[#0b4ea2] shadow-[-12px_0_25px_rgba(0,0,0,0.3)] z-0 pointer-events-none"></div>
        <div className="absolute -top-10 -bottom-20 left-[82%] right-0 -skew-x-[24deg] bg-[#1a64c4] shadow-[-6px_0_15px_rgba(0,0,0,0.2)] z-0 pointer-events-none"></div>
        <Link to="/welcome" aria-label={{L('Back', 'Back')}} className="relative z-10 text-xl font-bold text-[#083b7a]">←</Link>
        <span className="relative z-10 font-bold text-[#083b7a]">{{L('{label_bn}', '{label_en}')}}</span>
      </div>"""
      
    if '<div className="flex items-center gap-3 bg-upay-yellow px-4 py-3">' in code:
        new_code = re.sub(pattern, new_header, code, flags=re.DOTALL)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f"Updated {path}")
    else:
        print(f"Header not found in {path}")

update_file('web/src/pages/auth/Login.tsx', 'Log in', 'লগইন')
update_file('web/src/pages/auth/Register.tsx', 'Registration', 'রেজিস্ট্রেশন')
