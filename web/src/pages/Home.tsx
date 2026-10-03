import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useShell } from '../components/AppShell'
import { Icon } from '../components/Icon'
import { AiBadge } from '../components/ui'
import { useLang } from '../i18n'

type Tile = { icon: string; bn: string; en: string; to?: string; hishab?: boolean }

const TILES: Tile[] = [
  { icon: 'send', bn: 'সেন্ড মানি', en: 'Send Money', to: '/app/send' },
  { icon: 'phone', bn: 'মোবাইল রিচার্জ', en: 'Recharge', to: '/app/pay?type=mobile_recharge' },
  { icon: 'cashout', bn: 'ক্যাশ আউট', en: 'Cash Out', to: '/app/cashout' },
  { icon: 'bill', bn: 'পে বিল', en: 'Pay Bill', to: '/app/pay?type=bill_pay' },
  { icon: 'add', bn: 'অ্যাড মানি', en: 'Add Money' },
  { icon: 'pig', bn: 'সঞ্চয়', en: 'Savings', to: '/app/savings', hishab: true },
  { icon: 'bank', bn: 'ফান্ড ট্রান্সফার', en: 'Fund Transfer', to: '/app/transfer' },
  { icon: 'request', bn: 'রিকোয়েস্ট মানি', en: 'Request Money' },
  { icon: 'pay', bn: 'মেক পেমেন্ট', en: 'Make Payment', to: '/app/pay?type=merchant_pay' },
  { icon: 'gift', bn: 'রেফার & আর্ন', en: 'Refer & Earn' },
  { icon: 'npsb', bn: 'এনপিএসবি', en: 'NPSB', to: '/app/npsb', hishab: true },
  { icon: 'grid', bn: 'উপায় পেমেন্ট', en: 'upay Payment', to: '/app/payments' },
]

const OTHER = [
  { bn: 'পেওনিয়ার', en: 'Payoneer', icon: 'card' },
  { bn: 'উপায় চাকা', en: 'upay Wheel', icon: 'spark' },
  { bn: 'মিউজিক', en: 'Music', icon: 'heart' },
  { bn: 'ই-লার্নিং', en: 'e-Learning', icon: 'book' },
  { bn: 'গেমস', en: 'Games', icon: 'grid' },
]

const BANNERS = [
  { bn: 'টাকা আর কত দিন চলবে? হিসাব দেখো', en: 'How long will your money last? Open Hishab', to: '/app/hishab' },
  { bn: 'অন্য wallet-এ পাঠাও NPSB দিয়ে — কম খরচে', en: 'Send to other wallets via NPSB — for less', to: '/app/npsb' },
]

function payRoute(type: string): string {
  if (type === 'send_money') return '/app/send'
  return `/app/pay?type=${type}`
}

export default function Home() {
  const [expanded, setExpanded] = useState(false)
  const { L, taka, num } = useLang()
  const { shell, demo } = useShell()
  const navigate = useNavigate()
  const [b, setB] = useState(0)
  useEffect(() => {
    const t = window.setInterval(() => setB((x) => (x + 1) % BANNERS.length), 4500)
    return () => window.clearInterval(t)
  }, [])

  return (
    <div className="space-y-3 pt-3">
      <section className="relative mx-3 rounded-2xl bg-white px-1 py-4">
        <div className={`grid grid-cols-4 gap-y-4 transition-all duration-500 ease-in-out ${expanded ? 'max-h-[500px]' : 'overflow-hidden max-h-[170px]'}`}>
          {TILES.map((t, i) => {
            const isHidden = !expanded && i >= 8;
            return (
              <button key={t.bn} onClick={() => (t.to ? navigate(t.to) : demo(L(t.bn, t.en)))}
                className={`relative flex flex-col items-center gap-1.5 px-1 text-center transition-all duration-300 ${isHidden ? 'opacity-20 blur-[2px] pointer-events-none' : ''}`}>
                <span className="flex size-12 items-center justify-center rounded-2xl bg-upay-blue/8 text-upay-blue">
                  <Icon name={t.icon} size={26} />
                </span>
                <span className="text-[12px] font-semibold leading-tight">{L(t.bn, t.en)}</span>
                {t.hishab && <span className="absolute right-2 top-0"><AiBadge className="!px-1 !text-[9px]" /></span>}
              </button>
            )
          })}
        </div>
        
        {!expanded && (
          <div className="absolute inset-x-0 bottom-0 flex justify-center pb-0 bg-gradient-to-t from-white via-white/80 to-transparent pt-10 pointer-events-none">
            <button onClick={() => setExpanded(true)} className="flex items-center gap-1 rounded-full bg-white px-4 py-1.5 text-xs font-semibold text-upay-blue shadow-[0_2px_10px_rgba(0,0,0,0.1)] border border-slate-100 pointer-events-auto transform translate-y-2">
              {L('আরো দেখুন', 'See More')} <Icon name="chevron" size={14} className="rotate-90 mt-0.5" strokeWidth={3} />
            </button>
          </div>
        )}
        {expanded && (
          <div className="flex justify-center mt-3 border-t border-slate-50 pt-2">
            <button onClick={() => setExpanded(false)} className="flex items-center gap-1 rounded-full bg-transparent px-4 py-1 text-xs font-semibold text-upay-blue">
              {L('গুটিয়ে নিন', 'See Less')} <Icon name="chevron" size={14} className="-rotate-90 mt-0.5" strokeWidth={3} />
            </button>
          </div>
        )}
      </section>

      {shell && shell.recent.length > 0 && (
        <section className="mx-3 rounded-2xl bg-white p-3">
          <h2 className="mb-2 text-[14px] font-semibold text-upay-blue">{L('সাম্প্রতিক পেমেন্ট', 'Recent payments')}</h2>
          <div className="grid grid-cols-4 gap-2">
            {shell.recent.map((r) => (
              <button key={r.counterparty_id}
                onClick={() => navigate(`${payRoute(r.type)}${payRoute(r.type).includes('?') ? '&' : '?'}cp=${encodeURIComponent(r.counterparty_id)}&name=${encodeURIComponent(r.name)}`)}
                className="flex flex-col items-center gap-1 rounded-xl p-1 text-center hover:bg-transparent">
                <span className="flex size-10 items-center justify-center rounded-full bg-upay-yellow/40 text-sm font-bold">
                  {r.name.slice(0, 1)}
                </span>
                <span className="line-clamp-1 text-[11px] font-semibold">{r.name}</span>
                <span className="text-[10px] text-muted">{taka(r.last_amount)}</span>
                {r.due_in_days !== null && (
                  <span className="rounded-full bg-warn-bg px-1.5 text-[9px] font-bold text-warn">
                    {L(`${num(r.due_in_days)} দিনে দিতে হবে`, `due in ${r.due_in_days}d`)}
                  </span>
                )}
              </button>
            ))}
          </div>
        </section>
      )}

      <section className="mx-3">
        <button onClick={() => navigate(BANNERS[b].to)}
          className="flex h-24 w-full items-center justify-between rounded-2xl bg-upay-blue px-5 text-left text-white">
          <span key={b} className="animate-rise text-[15px] font-semibold leading-snug">{L(BANNERS[b].bn, BANNERS[b].en)}</span>
          <Icon name="chevron" />
        </button>
        <div className="mt-2 flex justify-center gap-1.5">
          {BANNERS.map((_, k) => <span key={k} className={`h-1.5 rounded-full ${k === b ? 'w-5 bg-upay-blue' : 'w-1.5 bg-line'}`} />)}
        </div>
      </section>

      <section className="mx-3 rounded-2xl bg-white p-3">
        <h2 className="mb-3 text-[14px] font-semibold text-upay-blue">{L('অন্যান্য সার্ভিস', 'Other services')}</h2>
        <div className="grid grid-cols-4 gap-y-3">
          {OTHER.map((o) => (
            <button key={o.bn} onClick={() => demo(L(o.bn, o.en))} className="flex flex-col items-center gap-1">
              <span className="flex size-11 items-center justify-center rounded-2xl bg-transparent text-upay-blue"><Icon name={o.icon} /></span>
              <span className="text-[12px]">{L(o.bn, o.en)}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="mx-3 grid grid-cols-2 gap-3">
        <button onClick={() => demo(L('উপায় কার্ড', 'upay Card'))} className="rounded-full bg-upay-yellow/30 py-3 text-sm font-semibold">
          {L('উপায় কার্ড', 'upay Card')}
        </button>
        <button onClick={() => demo(L('উপায় অফার', 'upay Offers'))} className="rounded-full bg-upay-yellow/30 py-3 text-sm font-semibold">
          {L('উপায় অফার', 'upay Offers')}
        </button>
      </section>
    </div>
  )
}
