import { useState } from 'react'
import { api, ApiError } from '../../api/client'
import type { GoalPlan, Savings } from '../../api/types'
import { useShell } from '../../components/AppShell'
import { Icon } from '../../components/Icon'
import { AiBadge, Button, Card, ErrorNote, ProgressBar, Sheet, Spinner } from '../../components/ui'
import { useLang } from '../../i18n'
import { bnPossessive, parseAmount } from '../../lib/format'
import { useApi } from '../../lib/useApi'
import { PageTitle } from '../common'

const ACTION_BN: Record<string, [string, string]> = {
  save_first: ['টাকা এলে আগে কিছু পকেটে রাখা', 'Set money aside when paid'],
  split_remittance: ['বাড়িতে টাকা দুই ভাগে পাঠানো', 'Split money sent home in two'],
  digital_pay_instead_of_cashout: ['cash-out কমিয়ে wallet দিয়ে পেমেন্ট', 'Pay by wallet instead of cash-out'],
  cheaper_route: ['কম খরচের পথে টাকা পাঠানো', 'Send through the cheaper route'],
  trim_discretionary: ['বাড়তি খরচ ১০% কমানো', 'Trim extra spending by 10%'],
  daily_limit: ['দিনের খরচের সীমা মেনে চলা', 'Keep to a daily spending limit'],
  eid_weekly_saving: ['সপ্তাহে ঈদের জন্য কিছু রাখা', 'Weekly Eid saving'],
}

const MONTHS = [1, 2, 3, 4, 6, 9, 12, 18, 24]
const POCKET_ICON: Record<string, string> = { emergency: 'shield', eid: 'gift', family: 'home', education: 'book', custom: 'pig' }

type Move = { pocket: string; name: string; dir: 'in' | 'out'; max: number }

function MoveSheet({ move, onClose, onDone }: { move: Move | null; onClose: () => void; onDone: (s: Savings) => void }) {
  const { L, taka } = useLang()
  const { uid, refresh } = useShell()
  const [text, setText] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  if (!move) return null
  const submit = async () => {
    const amount = parseAmount(text)
    if (!amount) return setErr(L('সঠিক পরিমাণ লিখুন', 'Enter a valid amount'))
    setBusy(true)
    setErr('')
    try {
      const s = await api.movePocket(uid, move.pocket, move.dir, amount)
      setText('')
      onDone(s)
      refresh()
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : L('কিছু একটা ভুল হয়েছে', 'Something went wrong'))
    } finally {
      setBusy(false)
    }
  }
  return (
    <Sheet open onClose={onClose}
      title={move.dir === 'in' ? L(`${move.name} পকেটে রাখুন`, `Add to ${move.name}`) : L(`${move.name} পকেট থেকে তুলুন`, `Take out of ${move.name}`)}>
      <p className="mb-2 text-sm text-muted">
        {move.dir === 'in' ? L(`ওয়ালেটে আছে ${taka(move.max)}`, `Wallet: ${taka(move.max)}`)
          : L(`পকেটে আছে ${taka(move.max, { paisa: true })} — যখন খুশি তুলতে পারেন`, `In pocket: ${taka(move.max, { paisa: true })} — withdraw any time`)}
      </p>
      <label className="block text-sm font-semibold" htmlFor="move-amount">{L('পরিমাণ', 'Amount')}</label>
      <div className="mt-1 flex items-center rounded-xl border border-line px-3 focus-within:border-upay-blue">
        <span className="text-lg font-bold text-muted">৳</span>
        <input id="move-amount" inputMode="decimal" autoFocus value={text} onChange={(e) => setText(e.target.value)}
          className="min-h-12 w-full bg-transparent px-2 text-lg font-semibold outline-none" placeholder="০" />
      </div>
      <div className="mt-2 flex gap-2">
        {[100, 500, 1000].map((v) => (
          <button key={v} onClick={() => setText(String(v))} className="rounded-full bg-transparent px-3 py-1 text-sm">{taka(v)}</button>
        ))}
      </div>
      {err && <p className="mt-2 text-sm text-bad" role="alert">{err}</p>}
      <Button full className="mt-4" disabled={busy} onClick={() => void submit()}>
        {busy ? L('হচ্ছে…', 'Working…') : L('নিশ্চিত করুন', 'Confirm')}
      </Button>
    </Sheet>
  )
}

function Toggle({ on, onChange, label }: { on: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <button role="switch" aria-checked={on} aria-label={label} onClick={() => onChange(!on)}
      className={`relative h-7 w-12 shrink-0 rounded-full transition ${on ? 'bg-ok' : 'bg-line'}`}>
      <span className={`absolute top-0.5 size-6 rounded-full bg-white shadow transition-all ${on ? 'left-[22px]' : 'left-0.5'}`} />
    </button>
  )
}

function GoalPlanner({ pockets, onSaved }: { pockets: Savings['pockets']; onSaved: () => void }) {
  const { L, taka, num } = useLang()
  const { uid } = useShell()
  const [target, setTarget] = useState('')
  const [months, setMonths] = useState(6)
  const [pocket, setPocket] = useState('custom')
  const [plan, setPlan] = useState<GoalPlan | null>(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const submit = async () => {
    const amount = parseAmount(target)
    if (!amount) return setErr(L('লক্ষ্যের সঠিক পরিমাণ লিখুন', 'Enter a valid goal amount'))
    setBusy(true)
    setErr('')
    try {
      setPlan(await api.planGoal(uid, amount, months, pocket))
      onSaved()
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : L('কিছু একটা ভুল হয়েছে', 'Something went wrong'))
    } finally {
      setBusy(false)
    }
  }
  const feas = plan ? Math.round(plan.feasibility * 100) : 0
  return (
    <Card>
      <div className="mb-2 flex items-center gap-2"><Icon name="spark" size={18} className="text-upay-blue" />
        <p className="font-semibold">{L('লক্ষ্য ঠিক করুন', 'Set a goal')}</p><AiBadge /></div>
      <div className="grid grid-cols-2 gap-2">
        <label className="col-span-2 text-sm">
          <span className="text-muted">{L('কত টাকা জমাতে চান', 'How much to save')}</span>
          <input inputMode="decimal" value={target} onChange={(e) => setTarget(e.target.value)} placeholder="৳৫,০০০"
            className="mt-1 min-h-11 w-full rounded-xl border border-line px-3 outline-none focus:border-upay-blue" />
        </label>
        <label className="text-sm">
          <span className="text-muted">{L('কত মাসে', 'In how many months')}</span>
          <select value={months} onChange={(e) => setMonths(Number(e.target.value))}
            className="mt-1 min-h-11 w-full rounded-xl border border-line bg-white px-2">
            {MONTHS.map((m) => <option key={m} value={m}>{L(`${num(m)} মাস`, `${m} months`)}</option>)}
          </select>
        </label>
        <label className="text-sm">
          <span className="text-muted">{L('কোন পকেটে', 'Which pocket')}</span>
          <select value={pocket} onChange={(e) => setPocket(e.target.value)}
            className="mt-1 min-h-11 w-full rounded-xl border border-line bg-white px-2">
            {pockets.map((p) => <option key={p.name} value={p.name}>{p.name_bn}</option>)}
          </select>
        </label>
      </div>
      {err && <p className="mt-2 text-sm text-bad" role="alert">{err}</p>}
      <Button full variant="outline" className="mt-3" disabled={busy} onClick={() => void submit()}>
        {busy ? L('হিসাব হচ্ছে…', 'Working…') : L('হিসাব করুন', 'Work it out')}
      </Button>
      {plan && !plan.insufficient_history && (
        <div className="mt-3 rounded-xl bg-transparent p-3 text-sm">
          <p className="font-semibold">{L(`মাসে ${taka(plan.monthly)} করে রাখতে হবে`, `Save ${taka(plan.monthly)} a month`)}</p>
          <p className={`mt-1 ${feas >= 60 ? 'text-ok' : feas >= 30 ? 'text-warn' : 'text-bad'}`}>
            {feas >= 60 ? L(`আপনার আগের মাসগুলোর হিসাবে এটি সম্ভব (${num(feas)}%)`, `Likely, based on past months (${feas}%)`)
              : feas >= 30 ? L(`একটু কঠিন হবে (${num(feas)}%)`, `A stretch (${feas}%)`)
                : L('এখনকার খরচে এটি কঠিন — সময় বাড়ান বা নিচের কাজগুলো করুন', 'Hard at current spending — add time or try these')}
          </p>
          {plan.enabling_actions.length > 0 && (
            <ul className="mt-2 list-disc pl-5 text-ink/80">
              {plan.enabling_actions.map((a) => <li key={a}>{L(...(ACTION_BN[a] ?? [a, a]))}</li>)}
            </ul>
          )}
          <p className="mt-2 text-xs text-muted">{L('লক্ষ্য পকেটে বসানো হয়েছে।', 'Goal saved on the pocket.')}</p>
        </div>
      )}
      {plan?.insufficient_history && (
        <p className="mt-3 text-sm text-muted">{L('আরও কিছু দিনের লেনদেন হলে হিসাব দেখাব।', 'Needs a few more days of activity.')}</p>
      )}
    </Card>
  )
}

export default function Pockets() {
  const { L, taka, num, date } = useLang()
  const { uid } = useShell()
  const { data, error, loading, reload, setData } = useApi(() => api.savings(uid), [uid])
  const [move, setMove] = useState<Move | null>(null)
  const [msg, setMsg] = useState('')

  if (loading && !data) return <><PageTitle bn="আমার পকেট" en="My pockets" /><Spinner /></>
  if (error) return <><PageTitle bn="আমার পকেট" en="My pockets" /><ErrorNote message={error} onRetry={reload} /></>
  if (!data) return null

  const displayPockets = data.pockets

  const togglePaisa = async (on: boolean) => {
    try {
      setData(await api.setPaisa(uid, on))
    } catch (e) {
      setMsg(e instanceof ApiError ? e.message : L('কিছু একটা ভুল হয়েছে', 'Something went wrong'))
    }
  }
  const eid = data.eid_plan
  const setEidGoal = async () => {
    try {
      await api.planGoal(uid, Math.max(eid.need, 1), Math.max(1, Math.min(60, Math.ceil(eid.days_left / 30))), 'eid')
      setMsg(L('ঈদ পকেটে লক্ষ্য বসানো হলো', 'Eid goal set'))
      void reload()
    } catch (e) {
      setMsg(e instanceof ApiError ? e.message : L('কিছু একটা ভুল হয়েছে', 'Something went wrong'))
    }
  }

  return (
    <div className="space-y-3 pb-6">
      <PageTitle bn="আমার পকেট" en="My pockets" />
      <div className="space-y-3 px-3">
        <Card className="flex items-center gap-3">
          <div className="flex-1">
            <p className="flex items-center gap-2 font-semibold">{L('পয়সা-সঞ্চয়', 'Paisa saving')}<AiBadge /></p>
            <p className="text-xs text-muted">
              {L('প্রতিটা লেনদেনের পয়সার ভগ্নাংশ (যেমন ৳১২০.৪০-এর ৪০ পয়সা) জমা হবে', 'The paisa fraction of each payment (e.g. 40 paisa of ৳120.40) is saved')}
            </p>
            <p className="mt-1 text-sm font-semibold">{L('জমেছে', 'Saved')} {taka(data.paisa.total, { paisa: true })}</p>
            {data.paisa.on && data.paisa.paused && (
              <p className="mt-1 text-xs font-semibold text-warn">{L('ঝুঁকির কারণে সাময়িক বন্ধ — পরের মাসে আবার চালু হবে', 'Paused for now due to risk — resumes next month')}</p>
            )}
          </div>
          <Toggle on={data.paisa.on} onChange={(v) => void togglePaisa(v)} label={L('পয়সা-সঞ্চয়', 'Paisa saving')} />
        </Card>
        {data.paisa.total > 0 && (
          <button className="text-sm font-semibold text-upay-blue underline"
            onClick={() => setMove({ pocket: 'paisa', name: L('পয়সা', 'Paisa'), dir: 'out', max: data.paisa.total })}>
            {L('পয়সা-সঞ্চয় থেকে তুলুন', 'Withdraw paisa savings')}
          </button>
        )}

        <div className="grid grid-cols-1 gap-3">
          {displayPockets.map((p) => (
            <Card key={p.name}>
              <div className="flex items-center gap-3">
                <span className="flex size-10 items-center justify-center rounded-xl bg-upay-yellow/30 text-upay-blue">
                  <Icon name={POCKET_ICON[p.name] ?? 'pig'} size={20} />
                </span>
                <div className="flex-1">
                  <p className="font-semibold">{p.name_bn}</p>
                  <p className="text-lg font-bold">{taka(p.balance, { paisa: p.balance % 1 !== 0 })}</p>
                </div>
                <div className="flex gap-1.5">
                  <Button variant="outline" className="!min-h-9 !px-3 text-sm"
                    onClick={() => setMove({ pocket: p.name, name: p.name_bn, dir: 'in', max: data.balance })}>{L('রাখুন', 'Add')}</Button>
                  <Button variant="ghost" className="!min-h-9 !px-3 text-sm" disabled={p.balance <= 0}
                    onClick={() => setMove({ pocket: p.name, name: p.name_bn, dir: 'out', max: p.balance })}>{L('তুলুন', 'Take out')}</Button>
                  <Button variant="ghost" className="!min-h-9 !px-2 text-sm text-slate-400 hover:text-red-500"
                    onClick={async () => { 
                      try {
                        setData(await api.deletePocket(uid, p.name)); 
                        setMsg(L('পকেট ডিলিট করা হয়েছে', 'Pocket deleted'))
                      } catch (e) {
                        setMsg('Error')
                      }
                    }} aria-label="Delete Pocket">
                    <Icon name="trash" size={18} />
                  </Button>

                </div>
              </div>
              {p.goal && (
                <div className="mt-3">
                  <div className="mb-1 flex justify-between text-xs text-muted">
                    <span>{L(`লক্ষ্য ${taka(p.goal.target)}`, `Goal ${taka(p.goal.target)}`)}{p.goal.date && L(` · ${bnPossessive(date(p.goal.date))} মধ্যে`, ` · by ${date(p.goal.date)}`)}</span>
                    <span>{num(Math.round((p.progress ?? 0) * 100))}%</span>
                  </div>
                  <ProgressBar value={p.progress ?? 0} tone={(p.progress ?? 0) >= 1 ? 'ok' : 'blue'} />
                </div>
              )}
            </Card>
          ))}
        </div>

        <Button variant="outline" className="w-full border-dashed border-2 border-slate-300 text-slate-500 hover:bg-slate-50 mb-4" onClick={async () => {
            const name = window.prompt(L('নতুন পকেটের নাম দিন:', 'Enter new pocket name:'))
            if (name) {
              try {
                setData(await api.addPocket(uid, 'custom_' + Date.now(), name))
                setMsg(L('নতুন পকেট তৈরি হয়েছে', 'New pocket created'))
              } catch (e) {
                setMsg('Error')
              }
            }
          }}>
          + {L('নতুন পকেট যোগ করুন', 'Add a new pocket')}
        </Button>
        <Card className="border-upay-yellow bg-upay-yellow/10">
          <div className="mb-1 flex items-center gap-2"><Icon name="gift" size={18} className="text-upay-blue" />
            <p className="font-semibold">{L(`${eid.eid_name_bn} আসছে · ${num(eid.days_left)} দিন বাকি`, `${eid.eid_name} in ${eid.days_left} days`)}</p><AiBadge /></div>
          <p className="text-sm text-ink/80">
            {L(`গত ঈদে খরচ হয়েছিল ${taka(eid.last_eid_spend)}, বোনাস আশা ${taka(eid.expected_bonus)}।`,
              `Last Eid you spent ${taka(eid.last_eid_spend)}; expected bonus ${taka(eid.expected_bonus)}.`)}
          </p>
          {eid.need > 0 ? (
            <>
              <p className="mt-1 text-sm font-semibold">
                {L(`বাকি ${taka(eid.need)} — সপ্তাহে ${taka(eid.weekly)} রাখলেই হবে`, `Short by ${taka(eid.need)} — save ${taka(eid.weekly)} a week`)}
              </p>
              <Button variant="yellow" full className="mt-3" onClick={() => void setEidGoal()}>{L('ঈদ পকেটে লক্ষ্য বসান', 'Set the Eid pocket goal')}</Button>
            </>
          ) : (
            <p className="mt-1 text-sm font-semibold text-ok">{L('বোনাসেই ঈদের খরচ চলে যাওয়ার কথা', 'Your bonus should cover Eid')}</p>
          )}
        </Card>

        <GoalPlanner pockets={displayPockets} onSaved={() => void reload()} />
      </div>
      <MoveSheet move={move} onClose={() => setMove(null)} onDone={(s) => { setData(s); setMove(null); setMsg(L('হয়ে গেছে', 'Done')) }} />
      {msg && (
        <div className="fixed bottom-24 left-1/2 z-50 -translate-x-1/2 rounded-full bg-ink px-4 py-2 text-sm text-white">
          {msg}
          <button className="ml-2 text-white/70" aria-label={L('বন্ধ', 'Close')} onClick={() => setMsg('')}>✕</button>
        </div>
      )}
    </div>
  )
}
