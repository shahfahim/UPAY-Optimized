import { useState } from 'react'
import { api, ApiError } from '../../api/client'
import type { DpsAdvice, Savings } from '../../api/types'
import { useShell } from '../../components/AppShell'
import { Icon } from '../../components/Icon'
import { PinPad } from '../../components/PinPad'
import { AiBadge, Button, Card, ErrorNote, Sheet, Spinner } from '../../components/ui'
import { useLang } from '../../i18n'
import { useApi } from '../../lib/useApi'
import { PageTitle } from '../common'

// Mirrors the options of a DPS opening screen (backend rules/dps.yaml).
const MONTHLY = [500, 1000, 1500, 2000, 3000, 5000]
const TENURE = [12, 24, 36, 60]

function SmartDpsCard({ a, onPick }: { a: DpsAdvice; onPick: (monthly: number, tenure: number) => void }) {
  const { L, taka, num } = useLang()
  if (a.status === 'not_now') {
    return (
      <Card className="border-warn/40 bg-warn-bg">
        <p className="flex items-center gap-2 font-semibold text-warn"><AiBadge />{L('Smart DPS: এখন না', 'Smart DPS: not now')}</p>
        <p className="mt-1 text-sm text-ink/80">{a.reason_bn}</p>
        {a.naive_monthly ? (
          <p className="mt-2 text-xs text-muted">
            {L(`সাধারণ নিয়মে (আয়ের ১০%) ${taka(a.naive_monthly)} বলা হতো — Upay Prototype আপনার মাসের শেষের খরচের কথাও ভাবে।`,
              `A flat 10%-of-income rule would say ${taka(a.naive_monthly)} — Upay Prototype also checks your month-end squeeze.`)}
          </p>
        ) : null}
      </Card>
    )
  }
  return (
    <Card className="border-ok/40 bg-ok-bg">
      <p className="flex items-center gap-2 font-semibold text-ok"><AiBadge />{L('Smart DPS পরামর্শ', 'Smart DPS advice')}</p>
      <p className="mt-2 text-2xl font-bold text-ink">{L(`মাসে ${taka(a.safe_monthly ?? 0)}`, `${taka(a.safe_monthly ?? 0)} a month`)}</p>
      <div className="mt-1 grid grid-cols-2 gap-2 text-sm text-ink/80">
        {a.day && <p>{L(`কিস্তির দিন: প্রতি মাসের ${num(a.day)} তারিখ`, `Installment day: ${a.day} of each month`)}</p>}
        {a.tenure_months && <p>{L(`সময়কাল: ${num(a.tenure_months)} মাস`, `Tenure: ${a.tenure_months} months`)}</p>}
      </div>
      {a.maturity_estimate && (
        <p className="mt-1 text-sm">
          {L(`মেয়াদ শেষে প্রায় ${taka(a.maturity_estimate)}`, `About ${taka(a.maturity_estimate)} at maturity`)}
          <span className="ml-1 text-xs text-muted">({L('আনুমানিক, মুনাফা ছাড়া', 'estimate, excluding profit')})</span>
        </p>
      )}
      <p className="mt-2 text-sm text-ink/80">{a.reason_bn}</p>
      {a.naive_monthly ? (
        <p className="mt-1 text-xs text-muted">
          {L(`সাধারণ নিয়মে (আয়ের ১০%) ${taka(a.naive_monthly)} বলা হতো।`, `A flat 10%-of-income rule would say ${taka(a.naive_monthly)}.`)}
        </p>
      ) : null}
      <Button full className="mt-3" onClick={() => onPick(a.safe_monthly ?? 500, a.tenure_months ?? 12)}>
        {L('এই পরিমাণ বেছে নিন', 'Use this amount')}
      </Button>
    </Card>
  )
}

function ActiveDps({ dps }: { dps: NonNullable<Savings['dps']> }) {
  const { L, taka, num, date } = useLang()
  return (
    <Card className="border-ok/40">
      <p className="flex items-center gap-2 font-semibold"><Icon name="check" className="text-ok" />{L('আপনার DPS চালু আছে', 'Your DPS is active')}</p>
      <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
        <p>{L('মাসিক জমা', 'Monthly')}: <b>{taka(dps.monthly)}</b></p>
        <p>{L('সময়কাল', 'Tenure')}: <b>{L(`${num(dps.tenure_months)} মাস`, `${dps.tenure_months} months`)}</b></p>
        <p>{L('কিস্তির দিন', 'Day')}: <b>{L(`${num(dps.day)} তারিখ`, `${dps.day}th`)}</b></p>
        <p>{L('শুরু', 'Opened')}: <b>{date(dps.opened)}</b></p>
      </div>
      {dps.simulated && <p className="mt-2 text-xs text-muted">{L('ডেমো — আসল DPS খোলা হয়নি', 'demo — no real DPS was opened')}</p>}
    </Card>
  )
}

export default function Dps() {
  const { L, taka, num } = useLang()
  const { uid, refresh } = useShell()
  const { data, error, loading, reload } = useApi(() => Promise.all([api.dpsAdvice(uid), api.savings(uid)]), [uid])
  const [monthly, setMonthly] = useState<number | null>(null)
  const [tenure, setTenure] = useState<number | null>(null)
  const [confirm, setConfirm] = useState(false)
  const [err, setErr] = useState('')
  const [done, setDone] = useState(false)
  const [pin, setPin] = useState('')
  const [dpsType, setDpsType] = useState<'normal'|'islamic'>('islamic')


  if (loading && !data) return <><PageTitle bn="সঞ্চয় (DPS)" en="Savings (DPS)" /><Spinner /></>
  if (error) return <><PageTitle bn="সঞ্চয় (DPS)" en="Savings (DPS)" /><ErrorNote message={error} onRetry={reload} /></>
  if (!data) return null
  const [advice, savings] = data
  const safe = advice.status === 'ok' ? advice.safe_monthly : null
  const m = monthly ?? safe ?? null
  const t = tenure ?? advice.tenure_months ?? null
  const overSafe = m !== null && (advice.status === 'not_now' || (safe !== null && m > safe))

  const open = async (code: string) => {
    if (code.length < 6 || m === null || t === null) return
    setErr('')
    try {
      await api.dpsOpen(uid, m, t)
      setConfirm(false)
      setDone(true)
      refresh()
      void reload()
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : L('কিছু একটা ভুল হয়েছে', 'Something went wrong'))
    }
  }

  return (
    <div className="pb-6">
      <PageTitle bn="সঞ্চয় (DPS)" en="Savings (DPS)" />
      <div className="space-y-3 px-3">
        {done && <p className="rounded-xl bg-ok-bg p-3 text-sm font-semibold text-ok" role="status">{L('DPS চালু হয়েছে (ডেমো)', 'DPS opened (demo)')}</p>}
        {savings.dps ? <ActiveDps dps={savings.dps} /> : (
          <>
            <SmartDpsCard a={advice} onPick={(mm, tt) => { setMonthly(mm); setTenure(tt) }} />
            <Card>
              <label className="block text-sm font-semibold" htmlFor="dps-monthly">{L('মাসিক জমার পরিমাণ', 'Monthly deposit')}</label>
              <select id="dps-monthly" value={m ?? ''} onChange={(e) => setMonthly(Number(e.target.value))}
                className={`mt-1 min-h-12 w-full rounded-xl border bg-white px-3 text-[15px] ${m !== null && m === safe ? 'border-ok ring-1 ring-ok' : 'border-line'}`}>
                <option value="" disabled>{L('বেছে নিন', 'Select')}</option>
                {MONTHLY.map((v) => (
                  <option key={v} value={v}>{taka(v)}{v === safe ? L(' — AI পরামর্শ', ' — AI pick') : ''}</option>
                ))}
              </select>
              <label className="mt-3 block text-sm font-semibold" htmlFor="dps-tenure">{L('সময়কাল', 'Tenure')}</label>
              <select id="dps-tenure" value={t ?? ''} onChange={(e) => setTenure(Number(e.target.value))}
                className="mt-1 min-h-12 w-full rounded-xl border border-line bg-white px-3 text-[15px]">
                <option value="" disabled>{L('বেছে নিন', 'Select')}</option>
                {TENURE.map((v) => <option key={v} value={v}>{L(`${num(v)} মাস`, `${v} months`)}</option>)}
              </select>
              {overSafe && (
                <p className="mt-2 rounded-lg bg-warn-bg px-2 py-1.5 text-xs text-warn">
                  {L('এটি নিরাপদ সীমার বেশি — মাসের শেষে টাকা কম পড়তে পারে। চাইলে তবুও বেছে নিতে পারেন।',
                    'Above the safe amount — you may run short at month end. You can still choose it.')}
                </p>
              )}
              {m !== null && t !== null && (
                <p className="mt-2 text-sm text-muted">
                  {L(`মেয়াদ শেষে জমা ${taka(m * t)} (আনুমানিক, মুনাফা ছাড়া)`, `Deposits total ${taka(m * t)} (estimate, excluding profit)`)}
                </p>
              )}
              <div className="mt-3 flex items-center justify-between rounded-xl bg-transparent px-3 py-2 text-sm">
                <span className="text-muted">{L('বর্তমান ব্যালেন্স', 'Current balance')}</span>
                <span className="font-semibold">{taka(savings.balance, { paisa: true })}</span>
              </div>
              <Button variant="yellow" full className="mt-4" disabled={m === null || t === null} onClick={() => setConfirm(true)}>
                {L('এগিয়ে যান', 'Proceed')}
              </Button>
            </Card>
          </>
        )}
      </div>
      <Sheet open={confirm} onClose={() => setConfirm(false)} title={L('DPS নিশ্চিত করুন', 'Confirm DPS')}>
        <p className="text-sm">{m !== null && t !== null && L(`মাসে ${taka(m)} · ${num(t)} মাস`, `${taka(m)} a month · ${t} months`)}</p>
        <p className="mt-1 text-xs font-semibold text-bad">{L('ডেমো — আসল পিন দেবেন না', 'Demo — do not use a real PIN')}</p>
        <PinPad value={pin} onChange={(v) => { setPin(v); if (v.length === 6) { setPin(''); void open(v) } }} />
        {err && <p className="mt-2 text-sm text-bad" role="alert">{err}</p>}
      </Sheet>
    </div>
  )
}

