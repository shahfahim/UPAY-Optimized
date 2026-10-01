import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { CategoryOption, CostlyHabit, Route } from '../api/types'
import { useLang } from '../i18n'
import { chooseCategory } from '../lib/category'
import { parseAmount } from '../lib/format'
import { Icon } from './Icon'
import { AiBadge, Sheet } from './ui'

export const CATEGORY_BN: Record<string, [string, string]> = {
  food_grocery: ['বাজার', 'Groceries'], rent: ['বাড়ি ভাড়া', 'Rent'], family_support: ['পরিবারে পাঠানো', 'Family'],
  transport: ['যাতায়াত', 'Transport'], mobile: ['মোবাইল', 'Mobile'], health: ['চিকিৎসা', 'Health'],
  education: ['শিক্ষা', 'Education'], utilities: ['বিল', 'Bills'], shopping: ['কেনাকাটা', 'Shopping'],
  festival: ['উৎসব', 'Festival'], other: ['অন্যান্য', 'Other'],
}

export function DemoBanner() {
  const { L } = useLang()
  return (
    <p className="mx-3 mb-3 flex items-center gap-2 rounded-xl bg-upay-yellow/30 px-3 py-2 text-xs font-semibold text-ink">
      <Icon name="info" size={16} className="text-upay-blue" />
      {L('Demo — কোনো আসল টাকা যাবে না', 'Demo — no real money moves')}
    </p>
  )
}

/** Amount field that accepts Bangla or ASCII digits; reports the parsed value (or null) upward. */
export function AmountInput({ text, onText, error, balance }: {
  text: string; onText: (t: string) => void; error?: string; balance?: number
}) {
  const { L, taka } = useLang()
  const parsed = parseAmount(text)
  const invalid = text.trim() !== '' && parsed === null
  return (
    <div>
      <label className="block text-sm font-semibold" htmlFor="flow-amount">{L('পরিমাণ', 'Amount')}</label>
      <div className={`mt-1 flex items-center rounded-xl border bg-white px-3 focus-within:border-upay-blue ${invalid || error ? 'border-bad' : 'border-line'}`}>
        <span className="text-xl font-bold text-muted">৳</span>
        <input id="flow-amount" inputMode="decimal" value={text} onChange={(e) => onText(e.target.value)} placeholder="০"
          aria-invalid={invalid || !!error} className="min-h-14 w-full bg-transparent px-2 text-2xl font-bold outline-none" />
      </div>
      {balance !== undefined && <p className="mt-1 text-xs text-muted">{L(`ব্যালেন্স ${taka(balance, { paisa: true })}`, `Balance ${taka(balance, { paisa: true })}`)}</p>}
      {(invalid || error) && (
        <p className="mt-1 text-sm text-bad" role="alert">{error || L('সঠিক পরিমাণ লিখুন (যেমন ৫০০ বা 500)', 'Enter a valid amount (e.g. 500)')}</p>
      )}
    </div>
  )
}

/** Top-3 AI category suggestions for this payee and amount; the user can pick any other. */
export function CategoryChips({ uid, counterpartyId, counterpartyType, amount, value, onChange }: {
  uid: string; counterpartyId: string | null; counterpartyType: string; amount: number | null
  value: string | null; onChange: (c: string) => void
}) {
  const { L } = useLang()
  const [opts, setOpts] = useState<CategoryOption[]>([])
  const [more, setMore] = useState(false)
  const [userChose, setUserChose] = useState(false)
  useEffect(() => setUserChose(false), [counterpartyId])
  const pick = (c: string) => { setUserChose(true); onChange(c) }
  useEffect(() => {
    let live = true
    const t = window.setTimeout(() => {
      api.categorySuggest(uid, counterpartyId, counterpartyType, amount ?? 0)
        .then((o) => {
          if (!live) return
          setOpts(o.slice(0, 3))
          const next = chooseCategory(value, userChose, o.map((x) => x.category))
          if (next && next !== value) onChange(next)
        })
        .catch(() => live && setOpts([]))
    }, 250)
    return () => { live = false; window.clearTimeout(t) }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uid, counterpartyId, counterpartyType, amount])
  const shown = opts.map((o) => o.category)
  return (
    <div>
      <p className="flex items-center gap-2 text-sm font-semibold">{L('খরচের ধরন', 'Category')}<AiBadge /></p>
      <div className="mt-1.5 flex flex-wrap gap-2">
        {opts.map((o, i) => (
          <button key={o.category} type="button" onClick={() => pick(o.category)} aria-pressed={value === o.category}
            className={`rounded-full border px-3 py-1.5 text-sm ${value === o.category ? 'border-upay-blue bg-upay-blue text-white' : 'border-line bg-white'}`}>
            {L(...(CATEGORY_BN[o.category] ?? [o.category_bn, o.category]))}
            {i === 0 && <span className="ml-1 text-[10px] opacity-80">{L('সম্ভাব্য', 'likely')}</span>}
          </button>
        ))}
        <button type="button" onClick={() => setMore((m) => !m)} className="rounded-full border border-dashed border-line px-3 py-1.5 text-sm text-muted">
          {value && !shown.includes(value) ? L(...(CATEGORY_BN[value] ?? [value, value])) : L('অন্য…', 'Other…')}
        </button>
      </div>
      {more && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {Object.keys(CATEGORY_BN).filter((c) => !shown.includes(c)).map((c) => (
            <button key={c} type="button" onClick={() => { pick(c); setMore(false) }}
              className="rounded-full bg-surface px-2.5 py-1 text-xs">{L(...CATEGORY_BN[c])}</button>
          ))}
        </div>
      )}
    </div>
  )
}

const NODE_ICON: Record<string, string> = {
  upay_wallet: 'wallet', npsb: 'npsb', other_mfs_wallet: 'phone', bank_account: 'bank', bank_card: 'card',
  merchant: 'pay', agent_cash: 'cashout',
}
const NODE_BN: Record<string, [string, string]> = {
  upay_wallet: ['upay', 'upay'], npsb: ['NPSB', 'NPSB'], other_mfs_wallet: ['অন্য wallet', 'Other wallet'],
  bank_account: ['ব্যাংক', 'Bank'], bank_card: ['কার্ড', 'Card'], merchant: ['দোকান', 'Merchant'], agent_cash: ['এজেন্ট', 'Agent'],
}

function RoutePath({ nodes }: { nodes: string[] }) {
  const { L } = useLang()
  return (
    <div className="flex flex-wrap items-center gap-1">
      {nodes.map((n, i) => (
        <span key={`${n}-${i}`} className="flex items-center gap-1">
          {i > 0 && <span className="text-muted">→</span>}
          <span className="inline-flex items-center gap-1 rounded-full bg-surface px-2 py-0.5 text-xs">
            <Icon name={NODE_ICON[n] ?? 'wallet'} size={13} />{L(...(NODE_BN[n] ?? [n, n]))}
          </span>
        </span>
      ))}
    </div>
  )
}

/** Every route to the destination, cheapest first; tapping a row picks it. */
export function MoneyMap({ routes, selected, onSelect }: { routes: Route[]; selected: number; onSelect: (i: number) => void }) {
  const { L, taka, num } = useLang()
  return (
    <ol className="space-y-2">
      {routes.map((r, i) => (
        <li key={r.nodes.join('>')}>
          <button type="button" onClick={() => onSelect(i)} aria-pressed={selected === i}
            className={`w-full rounded-xl border p-3 text-left ${selected === i ? 'border-upay-blue ring-1 ring-upay-blue' : 'border-line'}`}>
            <div className="mb-1.5 flex items-center justify-between text-sm">
              <span className="font-semibold">{num(i + 1)}. {i === 0 ? L('সবচেয়ে কম খরচ', 'Cheapest') : L('বিকল্প পথ', 'Alternative')}</span>
              <span className="font-semibold">{taka(r.fee, { paisa: r.fee % 1 !== 0 })} · {L(`${num(r.minutes)} মিনিট`, `${r.minutes} min`)}</span>
            </div>
            <RoutePath nodes={r.nodes} />
          </button>
        </li>
      ))}
    </ol>
  )
}

export function RoutePanel({ routes, selected, onSelect, placeholder }: {
  routes: Route[]; selected: number; onSelect: (i: number) => void; placeholder: boolean
}) {
  const { L, taka } = useLang()
  const [open, setOpen] = useState(false)
  if (!routes.length) return null
  const r = routes[selected] ?? routes[0]
  const worst = Math.max(...routes.map((x) => x.fee))
  const saving = worst - r.fee
  return (
    <div className={`rounded-2xl border p-3 ${selected === 0 ? 'border-ok bg-ok-bg/50' : 'border-warn bg-warn-bg/50'}`}>
      <div className="mb-1.5 flex items-center justify-between">
        <p className="flex items-center gap-2 text-sm font-semibold"><AiBadge />{L('Smart Route', 'Smart Route')}</p>
        <span className={`text-xs font-semibold ${selected === 0 ? 'text-ok' : 'text-warn'}`}>
          {selected === 0 ? L('সবচেয়ে কম খরচ', 'Cheapest') : L('বেশি খরচের পথ', 'Costlier path')}
        </span>
      </div>
      <RoutePath nodes={r.nodes} />
      <p className="mt-2 text-sm">
        {L(`খরচ ${taka(r.fee, { paisa: r.fee % 1 !== 0 })}`, `Fee ${taka(r.fee, { paisa: r.fee % 1 !== 0 })}`)}
        {saving > 0 && <span className="ml-1 font-semibold text-ok">{L(`· cash-out পথের চেয়ে ${taka(saving, { paisa: saving % 1 !== 0 })} কম`, `· ${taka(saving)} less than via cash-out`)}</span>}
      </p>
      {routes.length > 1 && (
        <button type="button" onClick={() => setOpen(true)} className="mt-1 text-sm font-semibold text-upay-blue underline">{L('সব পথ দেখো', 'See all routes')}</button>
      )}
      {placeholder && <p className="mt-1 text-[11px] text-muted">{L('fee-গুলো demo অনুমান, আসল tariff নয়', 'Fees are demo assumptions, not real tariffs')}</p>}
      <Sheet open={open} onClose={() => setOpen(false)} title={L('টাকা যাওয়ার সব পথ', 'All money routes')}>
        <MoneyMap routes={routes} selected={selected} onSelect={(i) => { onSelect(i); setOpen(false) }} />
      </Sheet>
    </div>
  )
}

export function NudgeCard({ habit, onGo, onContinue }: { habit: CostlyHabit; onGo: () => void; onContinue: () => void }) {
  const { L, taka } = useLang()
  return (
    <div className="rounded-2xl border border-upay-blue/30 bg-upay-blue/5 p-4">
      <p className="flex items-center gap-2 font-semibold"><AiBadge />{L('একটু থামো', 'One moment')}</p>
      <p className="mt-1 text-sm">
        {L(`বাড়িতে টাকা পাঠাতে cash-out করলে প্রতিবার fee লাগে। NPSB দিয়ে সরাসরি পাঠালে বছরে প্রায় ${taka(habit.annual_saving)} বাঁচবে।`,
          `Cashing out to send money home costs a fee each time. Sending through NPSB saves about ${taka(habit.annual_saving)} a year.`)}
      </p>
      <div className="mt-3 grid grid-cols-2 gap-2">
        <button type="button" onClick={onGo} className="min-h-10 rounded-xl bg-upay-blue text-sm font-semibold text-white">{L('NPSB দিয়ে পাঠাও', 'Send via NPSB')}</button>
        <button type="button" onClick={onContinue} className="min-h-10 rounded-xl border border-line bg-white text-sm font-semibold">{L('তবুও cash-out', 'Cash out anyway')}</button>
      </div>
    </div>
  )
}
