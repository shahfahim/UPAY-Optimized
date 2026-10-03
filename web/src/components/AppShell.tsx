import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
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
  const tone = m.priority === 1 ? 'bg-bad text-white' : m.priority === 3 ? 'bg-white/80 text-warn' : 'bg-white/70 text-ink'
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
      className="min-w-[104px] rounded-full bg-upay-blue px-3 py-1 text-center text-white shadow-sm">
      {open ? (
        <span className="block leading-tight">
          <span className="block text-[15px] font-bold">{taka(shell.balance)}</span>
          <span className="block text-[10px] opacity-90">
            {shell.safe_today > 0
              ? L(`আজ নিরাপদ খরচ ${taka(shell.safe_today)}`, `Safe today ${taka(shell.safe_today)}`)
              : L(`সাবধানে খরচ করুন`, `Spend carefully`)}
          </span>
        </span>
      ) : (
        <span className="text-sm font-semibold">{L('ব্যালেন্স', 'Balance')}</span>
      )}
    </button>
  )
}

function Header({ shell }: { shell: Shell | null }) {
  const { L } = useLang()
  return (
    <header className="header-pattern px-4 pb-3 pt-3">
      <div className="flex items-center gap-3">
        <div className="flex size-11 items-center justify-center rounded-full bg-white text-base font-bold text-upay-blue ring-2 ring-white/70">
          {shell?.avatar_initials ?? '…'}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-[15px] font-bold">{shell?.name ?? ''}</p>
          <p className="font-[Inter] text-xs text-ink/60">{shell?.phone_masked ?? ''}</p>
        </div>
        {shell && <BalanceButton shell={shell} />}
        <Link to="/app/notifications" className="relative p-1" aria-label={L('নোটিফিকেশন', 'Notifications')}>
          <Icon name="bell" size={22} />
          {shell && shell.unread > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex size-4 items-center justify-center rounded-full bg-bad text-[10px] font-bold text-white">
              {shell.unread}
            </span>
          )}
        </Link>
        <Link to="/app/more" className="p-1" aria-label={L('আরো', 'More')}>
          <Icon name="menu" size={22} />
        </Link>
      </div>
      {shell && <MessageStrip shell={shell} />}
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
        <main className="flex-1 bg-surface pb-4">
          <Outlet />
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
