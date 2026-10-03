import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, ApiError } from '../../api/client'
import type { RouteResult, SendResult, CategoryOption } from '../../api/types'
import { useShell } from '../../components/AppShell'
import { AmountInput, CATEGORY_BN, DemoBanner, RoutePanel } from '../../components/flow'
import { Icon } from '../../components/Icon'
import { PinPad } from '../../components/PinPad'
import { Button } from '../../components/ui'
import { useLang } from '../../i18n'
import { parseAmount } from '../../lib/format'
import { PageTitle } from '../common'

const SUB_CATEGORIES = [
  'food_grocery', 'transport', 'mobile', 'health', 'education', 'utilities', 'shopping', 'festival'
]

export default function SendMoney() {
  const { L, taka } = useLang()
  const { uid, shell, refresh } = useShell()
  const navigate = useNavigate()

  const [custom, setCustom] = useState('')
  const [text, setText] = useState('')
  const [category, setCategory] = useState<string | null>(null)
  const [customCategoryInput, setCustomCategoryInput] = useState('')
  const [reference, setReference] = useState('')
  
  const [opts, setOpts] = useState<CategoryOption[]>([])
  
  const [routes, setRoutes] = useState<RouteResult | null>(null)
  const [routeIdx, setRouteIdx] = useState(0)

  const [step, setStep] = useState<'form' | 'pin' | 'done'>('form')
  const [pin, setPin] = useState('')
  const [err, setErr] = useState('')
  const [result, setResult] = useState<SendResult | null>(null)
  
  const amount = parseAmount(text)
  const dest = 'upay_wallet'
  const type = 'send_money'
  const recipient = custom.trim() ? { id: null, name: custom.trim() } : null

  useEffect(() => {
    let live = true
    const t = window.setTimeout(() => {
      api.categorySuggest(uid, null, 'person', amount ?? 0)
        .then((o) => {
          if (!live) return
          setOpts(o.slice(0, 3))
        })
        .catch(() => live && setOpts([]))
    }, 250)
    return () => { live = false; window.clearTimeout(t) }
  }, [uid, amount])

  useEffect(() => {
    if (!dest) return
    let live = true
    const t = window.setTimeout(() => {
      api.route(uid, amount ?? 1000, dest)
        .then((r) => { if (live) { setRoutes(r); setRouteIdx(0) } })
        .catch(() => live && setRoutes(null))
    }, 300)
    return () => { live = false; window.clearTimeout(t) }
  }, [uid, amount, dest])

  const fee = routes?.routes[routeIdx]?.fee ?? 0

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
      const finalCategory = category ?? 'other'
      const r = await api.send(uid, {
        type, 
        amount, 
        counterparty_id: recipient.id ?? undefined, 
        counterparty_name: recipient.name,
        destination: dest, 
        category: finalCategory,
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
        <div className="mx-3 mt-4 grid grid-cols-2 gap-2">
          <Button variant="outline" onClick={() => navigate('/app/home')}>{L('হোম', 'Home')}</Button>
          <Button onClick={() => { setStep('form'); setText(''); setResult(null) }}>{L('আরেকটা', 'Another')}</Button>
        </div>
      </div>
    )
  }

  const suggestedKeys = opts.map((o) => o.category)

  return (
    <div className="pb-6">
      <PageTitle bn="সেন্ড মানি" en="Send money" />
      <DemoBanner />
      <div className="space-y-4 px-3">
        <label className="block text-sm">
          <span className="text-muted font-semibold block mb-1">{L('নাম বা মোবাইল নম্বর দিন', 'Enter name or mobile number')}</span>
          <input value={custom} onChange={(e) => setCustom(e.target.value)} maxLength={40} placeholder={L('নাম/নম্বর', 'Name/Number')}
            className="min-h-11 w-full rounded-xl border border-line bg-white px-3 outline-none focus:border-upay-blue" />
        </label>
        
        <AmountInput text={text} onText={setText} balance={shell?.balance} />
        
        {routes && amount && (
          <RoutePanel routes={routes.routes} selected={routeIdx} onSelect={setRouteIdx} placeholder={routes.fees_placeholder} />
        )}

        <div>
          <p className="flex items-center gap-2 text-sm font-semibold">{L('খরচের ধরন (অপশনাল)', 'Category (Optional)')}</p>
          <div className="mt-1.5 flex flex-wrap gap-2">
            {opts.map((o, i) => (
              <button key={o.category} type="button" onClick={() => setCategory(o.category)}
                className={`rounded-full border px-3 py-1.5 text-sm ${category === o.category ? 'border-upay-blue bg-upay-blue text-white' : 'border-line bg-white'}`}>
                {L(...(CATEGORY_BN[o.category] ?? [o.category_bn, o.category]))}
                {i === 0 && <span className="ml-1 text-[10px] opacity-80">{L('সম্ভাব্য', 'likely')}</span>}
              </button>
            ))}
            {!suggestedKeys.includes('other') && (
              <button type="button" onClick={() => setCategory('other')}
                className={`rounded-full border px-3 py-1.5 text-sm ${category === 'other' ? 'border-upay-blue bg-upay-blue text-white' : 'border-line bg-white'}`}>
                {L(...(CATEGORY_BN['other'] ?? ['অন্যান্য', 'Other']))}
              </button>
            )}
          </div>
          
          {(category === 'other' || (category && SUB_CATEGORIES.includes(category) && !suggestedKeys.includes(category))) && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {SUB_CATEGORIES.filter((c) => !suggestedKeys.includes(c)).map((c) => (
                <button key={c} type="button" onClick={() => setCategory(c)}
                  className={`rounded-full px-2.5 py-1 text-xs ${category === c ? 'bg-upay-blue text-white' : 'bg-surface text-ink'}`}>
                  {L(...(CATEGORY_BN[c] ?? [c, c]))}
                </button>
              ))}
            </div>
          )}

          <div className="mt-2 flex items-center gap-2">
            <input 
              type="text" 
              placeholder={L('নতুন ধরন যোগ করুন...', 'Add custom type...')}
              value={customCategoryInput}
              onChange={(e) => setCustomCategoryInput(e.target.value)}
              className="flex-1 rounded-xl border border-line px-3 py-1.5 text-sm outline-none focus:border-upay-blue"
            />
            <button 
              type="button" 
              onClick={() => {
                if(customCategoryInput.trim()) {
                  setCategory(customCategoryInput.trim());
                  setCustomCategoryInput('');
                }
              }}
              className="flex items-center justify-center rounded-xl bg-upay-blue px-3 py-1.5 text-sm font-semibold text-white">
              <Icon name="plus" size={16} /> {L('Add', 'Add')}
            </button>
          </div>
          {category && !suggestedKeys.includes(category) && category !== 'other' && !SUB_CATEGORIES.includes(category) && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              <button type="button" onClick={() => setCategory(category)} className="rounded-full bg-upay-blue px-2.5 py-1 text-xs text-white">
                {category}
              </button>
            </div>
          )}
        </div>

        <div>
          <p className="flex items-center gap-2 text-sm font-semibold">{L('রেফারেন্স (অপশনাল)', 'Reference (Optional)')}</p>
          <input 
            type="text"
            placeholder={L('Note or Reference', 'Note or Reference')}
            value={reference}
            onChange={(e) => setReference(e.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-line bg-white px-3 outline-none focus:border-upay-blue"
          />
        </div>

        {err && <p className="rounded-xl bg-bad-bg p-3 text-sm text-bad" role="alert">{err}</p>}
        <Button full variant="yellow" onClick={next}>
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
