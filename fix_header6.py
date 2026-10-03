import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update BalanceButton
old_btn_pattern = re.compile(r'<button onClick=\{\(\) => setOpen\(\(o\) => !o\)\} aria-live="polite"\s*className="min-w-\[104px\] rounded-full bg-\[\#0b4ea2\].*?<\/button>', re.DOTALL)

new_btn = """<button onClick={() => setOpen((o) => !o)} aria-live="polite"
        className="min-w-[104px] rounded-full bg-[#ffd500] px-3 py-1.5 text-center text-[#083b7a] font-extrabold shadow-[0_4px_12px_rgba(255,213,0,0.3)] ring-2 ring-white/20 transition-transform active:scale-95">
        {open ? (
          <span className="text-[15px]">{taka(shell.balance)}</span>
        ) : (
          <span className="text-sm">ব্যালেন্স</span>
        )}
      </button>"""
      
# Wait, the previous button had {L('ব্যালেন্স', 'Balance')} inside. I should keep it.
new_btn = """<button onClick={() => setOpen((o) => !o)} aria-live="polite"
        className="min-w-[104px] rounded-full bg-[#ffd500] px-3 py-1.5 text-center text-[#083b7a] font-extrabold shadow-[0_4px_12px_rgba(255,213,0,0.4)] ring-[2px] ring-[#ffd500]/50 transition-transform active:scale-95">
        {open ? (
          <span className="text-[15px] tracking-tight">{taka(shell.balance)}</span>
        ) : (
          <span className="text-sm">{L('ব্যালেন্স', 'Balance')}</span>
        )}
      </button>"""

code = old_btn_pattern.sub(new_btn, code)

# 2. Replace Header geometric background
header_bg_pattern = re.compile(r'\{\/\* Abstract Geometric Background - Layer 1 .*?\}\}<\/div>', re.DOTALL)

# Let's replace the whole header inner structure to be precise
start_marker = "function Header({ shell }: { shell: Shell | null }) {"
end_marker = "  function BottomNav"
start_idx = code.find(start_marker)
end_idx = code.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_header = """function Header({ shell }: { shell: Shell | null }) {
    const { L } = useLang()
    return (
      <header className="relative overflow-hidden bg-[#ffd500] px-4 pb-5 pt-4 shadow-[0_4px_20px_-5px_rgba(0,0,0,0.15)] z-10">
        
        {/* Abstract Geometric Background - Main Deep Blue Split */}
        <div className="absolute -top-10 -bottom-20 left-[48%] right-0 -skew-x-[24deg] bg-gradient-to-br from-[#083b7a] to-[#0b4ea2] shadow-[-12px_0_25px_rgba(0,0,0,0.3)] z-0"></div>
        
        {/* Abstract Geometric Background - Accent Light Blue Split */}
        <div className="absolute -top-10 -bottom-20 left-[82%] right-0 -skew-x-[24deg] bg-[#1a64c4] shadow-[-6px_0_15px_rgba(0,0,0,0.2)] z-0"></div>

        {/* Subtle Halftone/Dot Pattern Overlay */}
        <div className="absolute inset-0 pointer-events-none mix-blend-overlay opacity-15 z-0" style={{
          backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
          backgroundSize: '16px 16px'
        }}></div>
        
        <div className="relative flex items-center justify-between gap-2 z-10">
          
          {/* Left Side: Avatar & Name (Safely on Yellow BG) */}
          <div className="flex items-center gap-3 max-w-[45%]">
            <div className="flex size-11 shrink-0 items-center justify-center rounded-full bg-white text-[#0b4ea2] ring-[3px] ring-white shadow-md overflow-hidden">
              {shell && (shell as any).profile_pic ? (
                <img src={(shell as any).profile_pic} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <img src="/upay-logo.png" alt="Upay Logo" className="w-full h-full object-contain p-1.5" />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[15.5px] font-extrabold text-slate-900 tracking-tight drop-shadow-[0_1px_1px_rgba(255,255,255,0.8)]">{shell?.name ?? ''}</p>
              <p className="font-[Inter] text-[12.5px] font-bold text-slate-800 drop-shadow-[0_1px_1px_rgba(255,255,255,0.8)]">{shell?.phone_masked ?? ''}</p>
            </div>
          </div>

          {/* Right Side: Balance & Icons (Safely on Blue BG) */}
          <div className="flex items-center justify-end gap-2.5 flex-1 pl-2">
            {shell && <BalanceButton shell={shell} />}
            
            <div className="flex items-center gap-1.5">
              <Link to="/app/notifications" className="relative flex size-9 items-center justify-center rounded-full bg-white/10 text-white backdrop-blur-md shadow-sm border border-white/20 transition-transform active:scale-95" aria-label={L('নোটিফিকেশন', 'Notifications')}>
                <Icon name="bell" size={20} strokeWidth={2.5} />
                {shell && shell.unread > 0 && (
                  <span className="absolute -right-1 -top-1 flex size-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white shadow-sm ring-2 ring-[#0b4ea2]">
                    {shell.unread}
                  </span>
                )}
              </Link>
              <Link to="/app/more" className="flex size-9 items-center justify-center rounded-full bg-white/10 text-white backdrop-blur-md shadow-sm border border-white/20 transition-transform active:scale-95" aria-label={L('আরও', 'More')}>
                <Icon name="menu" size={20} strokeWidth={2.5} />
              </Link>
            </div>
          </div>
          
        </div>
        
        <div className="relative mt-5 z-10">
          {shell && <MessageStrip shell={shell} />}
        </div>
      </header>
    )
  }

"""
    code = code[:start_idx] + new_header + code[end_idx:]
    with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Header fixed! Left=Yellow, Right=Blue, Button=Yellow")
else:
    print(f"Error: start={start_idx}, end={end_idx}")
