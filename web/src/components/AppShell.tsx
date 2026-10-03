import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { Link, NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom'
import { api } from '../api/client'
import type { Shell } from '../api/types'
import { useLang } from '../i18n'
import { getSession } from '../lib/session'
import { Icon } from './Icon'
import { PrototypeRibbon, Sheet } from './ui'

type ShellCtx = {
  uid: string
  shell: Shell | null
  refresh: () => Promise<void>
  demo: (name: string) => void
}

const Ctx = createContext<ShellCtx | null>(null)

export function useShell(): ShellCtx {
  const v = useContext(Ctx)
  if (!v) throw new Error('useShell outside AppShell')
  return v
}

function MessageStrip({ shell }: { shell: Shell }) {
  const { L } = useLang()
  const navigate = useNavigate()
  const [i, setI] = useState(0)
  const msgs = shell.strip
  useEffect(() => {
    setI(0)
    if (msgs.length < 2) return
    const t = window.setInterval(() => setI((x) => (x + 1) % msgs.length), 4000)
    return () => window.clearInterval(t)
  }, [msgs])
  if (!msgs.length) return null
  const m = msgs[i % msgs.length]
  const tone = m.priority === 1 ? 'bg-bad text-white' : 'bg-[#fff8cc] text-slate-900'
  return (
    <button onClick={() => navigate(m.link)}
      className={`mt-2 flex w-full items-center gap-2 rounded-xl px-3 py-1.5 text-left text-[13px] font-semibold ${tone}`}>
      <Icon name="spark" size={16} />
      <span key={i} className="flex-1 animate-rise truncate">{L(m.text_bn, m.text_en)}</span>
      <Icon name="chevron" size={14} />
    </button>
  )
}

function BalanceButton({ shell }: { shell: Shell }) {
  const { L, taka } = useLang()
  const [open, setOpen] = useState(false)
  useEffect(() => {
    if (!open) return
    const t = window.setTimeout(() => setOpen(false), 5000)
    return () => window.clearTimeout(t)
  }, [open])
  return (
    <button onClick={() => setOpen((o) => !o)} aria-live="polite"
        className="min-w-[104px] rounded-full bg-[#ffd500] px-3 py-1.5 text-center text-[#083b7a] font-extrabold shadow-[0_4px_12px_rgba(255,213,0,0.4)] ring-[2px] ring-[#ffd500]/50 transition-transform active:scale-95">
        {open ? (
          <span className="text-[15px] tracking-tight">{taka(shell.balance)}</span>
        ) : (
          <span className="text-sm">{L('ব্যালেন্স', 'Balance')}</span>
        )}
      </button>
  )
}

function Header({ shell }: { shell: Shell | null }) {
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

  function BottomNav({ shell, onQr }: { shell: Shell | null; onQr: () => void }) {
  const { L, num } = useLang()
  const badge = shell?.nav_badge
  const dot = badge ? { green: 'bg-ok', amber: 'bg-warn', red: 'bg-bad' }[badge.level] : ''
  const item = (to: string, icon: string, label: ReactNode, extra?: ReactNode) => (
    <NavLink to={to} className={({ isActive }) =>
      `relative flex flex-1 flex-col items-center gap-0.5 py-2 text-[11px] ${isActive ? 'font-bold text-upay-blue' : 'text-muted'}`}>
      <Icon name={icon} size={22} />
      {label}
      {extra}
    </NavLink>
  )
  return (
    <nav className="sticky bottom-0 z-40 flex items-end border-t border-line bg-white pb-[env(safe-area-inset-bottom)]">
      {item('/app/home', 'home', L('হোম', 'Home'))}
      {item('/app/account', 'wallet', L('অ্যাকাউন্ট', 'Account'))}
      <div className="flex flex-1 justify-center">
        <button onClick={onQr} aria-label="QR"
          className="-mt-6 flex size-16 items-center justify-center rounded-full border-4 border-white bg-upay-blue text-white shadow-lg">
          <Icon name="qr" size={28} />
        </button>
      </div>
      {item('/app/history', 'clock', L('হিস্টরি', 'History'))}
        {item('/app/hishab', 'spark', <span className="flex items-center gap-0.5">{L('হিসাব', 'Hishab')}<span className="rounded-[4px] bg-[#0b4ea2] px-1 py-[1px] text-[8px] font-bold text-white not-italic shadow-sm">AI</span></span>, (
          <>
            
            
          </>
        ))}
      </nav>
  )
}

export default function AppShell() {
  const { L } = useLang()
  const uid = getSession()?.userId ?? ''
  const [shell, setShell] = useState<Shell | null>(null)
  const [demoName, setDemoName] = useState<string | null>(null)
  const location = useLocation()
  const refresh = useCallback(async () => {
    if (!uid) return
    try {
      setShell(await api.shell(uid))
    } catch {
      /* the header keeps its last state; pages show their own errors */
    }
  }, [uid])
  useEffect(() => {
    void refresh()
  }, [refresh])
  const demo = useCallback((name: string) => setDemoName(name), [])
  return (
    <Ctx.Provider value={{ uid, shell, refresh, demo }}>
      <div className="app-frame">
        <PrototypeRibbon />
        <Header shell={shell} />
        <main className="flex-1 bg-surface pb-4 overflow-hidden relative">
          <div key={location.pathname} className="animate-page-enter w-full min-h-full">
            <Outlet />
          </div>
        </main>
        <BottomNav shell={shell} onQr={() => demo('QR')} />
      </div>
      <Sheet open={demoName !== null} onClose={() => setDemoName(null)} title={demoName ?? ''}>
        <p className="text-sm text-muted">
          {L('এই ফিচার demo-তে চালু নেই। Hishab শুধু টাকার হিসাব, সঞ্চয় আর পাঠানোর অংশগুলো দেখায়।',
            'This feature is not active in the demo. Hishab covers money planning, savings and transfers.')}
        </p>
      </Sheet>
    </Ctx.Provider>
  )
}
