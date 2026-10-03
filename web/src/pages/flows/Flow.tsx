import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { api, ApiError } from '../../api/client'
import type { RouteResult, SendResult, SendType } from '../../api/types'
import { useShell } from '../../components/AppShell'
import { AmountInput, CATEGORY_BN, CategoryChips, DemoBanner, NudgeCard, RoutePanel } from '../../components/flow'
import { Icon } from '../../components/Icon'
import { PinPad } from '../../components/PinPad'
import { AiBadge, Button, Card } from '../../components/ui'
import { useLang } from '../../i18n'
import { parseAmount } from '../../lib/format'
import { PageTitle } from '../common'

export type Contact = {
  id: string | null
  name: string
  sub?: string
  /** Where the money ends up; a non-upay destination turns a send into an NPSB/fund transfer. */
  destination?: string
}

export type FlowConfig = {
  type: SendType
  titleBn: string
  titleEn: string
  contacts: Contact[]
  /** Show the Smart Route panel (transfers). */
  routed?: boolean
  /** Cash-out: show one nudge towards NPSB before the form. */
  cashNudge?: boolean
  /** Allow a typed recipient name/number. */
  freeRecipient?: boolean
}

const CP_TYPE: Record<SendType, string> = {
  send_money: 'person', npsb: 'person', fund_transfer: 'person', cash_out: 'agent',
  merchant_pay: 'merchant', bill_pay: 'biller', mobile_recharge: 'biller',
}

function sendTypeFor(base: SendType, dest: string | undefined): SendType {
  if (base === 'send_money' && dest && dest !== 'upay_wallet') return dest === 'bank_account' ? 'fund_transfer' : 'npsb'
  return base
}

export default function Flow({ cfg }: { cfg: FlowConfig }) {
  const { L, taka } = useLang()
  const { uid, shell, refresh } = useShell()
  const navigate = useNavigate()
  const [params] = useSearchParams()

  const preset: Contact | null = params.get('cp')
    ? cfg.contacts.find((c) => c.id === params.get('cp')) ?? { id: params.get('cp'), name: params.get('name') ?? params.get('cp')! }
    : null
  const [contact, setContact] = useState<Contact | null>(preset ?? (cfg.type === 'cash_out' ? cfg.contacts[0] ?? null : null))
  const [custom, setCustom] = useState('')
  const [text, setText] = useState('')
  const [category, setCategory] = useState<string | null>(null)
  const [routes, setRoutes] = useState<RouteResult | null>(null)
  const [routeIdx, setRouteIdx] = useState(0)
  const [nudgeSeen, setNudgeSeen] = useState(false)
  const [step, setStep] = useState<'form' | 'pin' | 'done'>('form')
  const [pin, setPin] = useState('')
  const [err, setErr] = useState('')
  const [result, setResult] = useState<SendResult | null>(null)

  const amount = parseAmount(text)
  const dest = contact?.destination ?? (cfg.type === 'cash_out' ? 'agent_cash' : cfg.type === 'send_money' ? 'upay_wallet' : undefined)
  const type = sendTypeFor(cfg.type, contact?.destination)
  const needsRoute = (cfg.routed || cfg.type === 'cash_out') && !!dest

  useEffect(() => {
    if (!needsRoute || !dest) return
    let live = true
    const t = window.setTimeout(() => {
      api.route(uid, amount ?? 1000, dest)
        .then((r) => { if (live) { setRoutes(r); setRouteIdx(0) } })
        .catch(() => live && setRoutes(null))
    }, 300)
    return () => { live = false; window.clearTimeout(t) }
  }, [uid, amount, dest, needsRoute])

  const fee = routes?.routes[routeIdx]?.fee ?? 0
  const recipient = contact ?? (custom.trim() ? { id: null, name: custom.trim() } : null)
  const habit = cfg.cashNudge ? routes?.habits.find((h) => h.kind === 'cash_remittance') : undefined
  const showNudge = !!habit && !nudgeSeen && step === 'form'

  const next = () => {
    setErr('')
    if (!recipient) return setErr(L('কাকে পাঠাবেন বেছে নিন', 'Choose a recipient'))
    if (!amount) return setErr(L('সঠিক পরিমাণ লিখুন', 'Enter a valid amount'))
    if (shell && amount + fee > shell.balance) return setErr(L('পর্যাপ্ত ব্যালেন্স নেই', 'Not enough balance'))
    setStep('pin')
  }
  const send = async () => {
    if (!amount || !recipient) return
    try {
      const r = await api.send(uid, {
        type, amount, counterparty_id: recipient.id ?? undefined, counterparty_name: recipient.name,
        destination: dest, category: category ?? undefined,
        route: type === 'npsb' || type === 'fund_transfer' ? routes?.routes[routeIdx]?.nodes : undefined,
      })
      setResult(r)
      setStep('done')
      refresh()
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : L('কিছু একটা ভুল হয়েছে', 'Something went wrong'))
      setStep('form')
    }
  }

  if (step === 'done' && result && amount && recipient) {
    const nudge = nudgeSeen ? null : result.nudge
    return (
      <div className="pb-6">
        <div className="mx-3 mt-6 rounded-3xl bg-white p-6 text-center">
          <span className="mx-auto flex size-16 items-center justify-center rounded-full bg-ok text-white"><Icon name="check" size={34} strokeWidth={3} /></span>
          <p className="mt-3 text-lg font-bold">{L('সফল হয়েছে', 'Done')}</p>
          <p className="mt-1 text-2xl font-bold">{taka(amount, { paisa: amount % 1 !== 0 })}</p>
          <p className="text-sm text-muted">{recipient.name}</p>
          <div className="mt-4 space-y-1.5 rounded-2xl bg-transparent p-3 text-left text-sm">
            <p className="flex justify-between"><span className="text-muted">{L('খরচ (fee)', 'Fee')}</span><span>{taka(result.fee, { paisa: result.fee % 1 !== 0 })}</span></p>
            <p className="flex justify-between"><span className="text-muted">{L('খরচের ধরন', 'Category')}</span><span>{L(...(CATEGORY_BN[result.category] ?? [result.category, result.category]))}</span></p>
            {result.swept > 0 && (
              <p className="flex justify-between text-ok"><span>{L('পয়সা-সঞ্চয়ে গেল', 'Paisa saved')}</span><span>{taka(result.swept, { paisa: true })}</span></p>
            )}
            <p className="flex justify-between font-semibold"><span>{L('নতুন ব্যালেন্স', 'New balance')}</span><span>{taka(result.balance, { paisa: true })}</span></p>
          </div>
          <p className="mt-2 text-xs text-muted">{L('Demo — কোনো আসল টাকা যায়নি', 'Demo — no real money moved')}</p>
        </div>
        {nudge && (
          <Card className="mx-3 mt-3 border-upay-blue/30">
            <p className="flex gap-2 text-sm"><AiBadge className="mt-0.5" />{nudge.text_bn}</p>
            <button className="mt-2 text-sm font-semibold text-upay-blue underline" onClick={() => navigate(nudge.link)}>{L('দেখুন', 'Show me')}</button>
          </Card>
        )}
        <div className="mx-3 mt-4 grid grid-cols-2 gap-2">
          <Button variant="outline" onClick={() => navigate('/app/home')}>{L('হোম', 'Home')}</Button>
          <Button onClick={() => { setStep('form'); setText(''); setResult(null) }}>{L('আরেকটা', 'Another')}</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="pb-6">
      <PageTitle bn={cfg.titleBn} en={cfg.titleEn} />
      <DemoBanner />
      <div className="space-y-4 px-3">
        {showNudge && habit && (
          <NudgeCard habit={habit} onGo={() => { setNudgeSeen(true); navigate('/app/npsb?cp=FAM-' + uid) }} onContinue={() => setNudgeSeen(true)} />
        )}
        {cfg.contacts.length > 0 && cfg.type !== 'cash_out' && (
          <div>
            <p className="text-sm font-semibold">{cfg.type === 'merchant_pay' ? L('কোথায় পেমেন্ট', 'Pay to')
              : cfg.type === 'bill_pay' ? L('কোন বিল', 'Which bill') : cfg.type === 'mobile_recharge' ? L('কোন নম্বর', 'Which number')
                : L('কাকে পাঠাবেন', 'Send to')}</p>
            <div className="mt-1.5 grid grid-cols-1 gap-2">
              {cfg.contacts.map((c) => {
                const on = contact?.id === c.id && contact?.name === c.name
                return (
                  <button key={`${c.id}-${c.name}`} type="button" onClick={() => { setContact(c); setCustom('') }} aria-pressed={on}
                    className={`flex items-center gap-3 rounded-xl border bg-white px-3 py-2.5 text-left ${on ? 'border-upay-blue ring-1 ring-upay-blue' : 'border-line'}`}>
                    <span className="flex size-9 items-center justify-center rounded-full bg-upay-yellow/40 text-sm font-bold text-upay-blue">{c.name.slice(0, 1)}</span>
                    <span className="flex-1"><span className="block font-semibold">{c.name}</span>{c.sub && <span className="text-xs text-muted">{c.sub}</span>}</span>
                    {on && <Icon name="check" size={18} className="text-upay-blue" />}
                  </button>
                )
              })}
            </div>
          </div>
        )}
        {cfg.freeRecipient && (
          <label className="block text-sm">
            <span className="text-muted">{L('অথবা নাম/নম্বর লিখুন (demo — আসল নম্বর দেবেন না)', 'Or type a name/number (demo — no real numbers)')}</span>
            <input value={custom} onChange={(e) => { setCustom(e.target.value); setContact(null) }} maxLength={40}
              className="mt-1 min-h-11 w-full rounded-xl border border-line bg-white px-3 outline-none focus:border-upay-blue" />
          </label>
        )}
        <AmountInput text={text} onText={setText} balance={shell?.balance} />
        {needsRoute && routes && amount && (cfg.routed ? (
          <RoutePanel routes={routes.routes} selected={routeIdx} onSelect={setRouteIdx} placeholder={routes.fees_placeholder} />
        ) : (
          <p className="text-sm text-muted">{L(`cash-out খরচ ${taka(fee, { paisa: fee % 1 !== 0 })}`, `Cash-out fee ${taka(fee, { paisa: fee % 1 !== 0 })}`)}</p>
        ))}
        {(recipient || cfg.type === 'cash_out') && (
          <CategoryChips uid={uid} counterpartyId={recipient?.id ?? null} counterpartyType={CP_TYPE[type]} amount={amount}
            value={category} onChange={setCategory} />
        )}
        {err && <p className="rounded-xl bg-bad-bg p-3 text-sm text-bad" role="alert">{err}</p>}
        <Button full variant="yellow" onClick={next} disabled={showNudge}>
          {L('এগিয়ে যান', 'Proceed')}{amount ? ` · ${taka(amount + fee, { paisa: (amount + fee) % 1 !== 0 })}` : ''}
        </Button>
      </div>
      {step === 'pin' && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={() => setStep('form')}>
          <div role="dialog" aria-modal="true" className="w-full max-w-[430px] animate-rise rounded-t-3xl bg-white p-5 pb-8" onClick={(e) => e.stopPropagation()}>
            <p className="text-center text-lg font-semibold">{L('PIN দিয়ে নিশ্চিত করুন', 'Confirm with PIN')}</p>
            <p className="text-center text-sm text-muted">
              {recipient?.name} · {amount && taka(amount, { paisa: amount % 1 !== 0 })}{fee > 0 && L(` + fee ${taka(fee, { paisa: fee % 1 !== 0 })}`, ` + fee ${taka(fee)}`)}
            </p>
            <p className="mt-1 text-center text-xs font-semibold text-bad">{L('Demo — আসল PIN দেবেন না', 'Demo — do not use a real PIN')}</p>
            <PinPad value={pin} onChange={(v) => { setPin(v); if (v.length === 6) { setPin(''); void send() } }} />
          </div>
        </div>
      )}
    </div>
  )
}
