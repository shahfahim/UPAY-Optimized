import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../../api/client'
import type { EmergencyOption, EmergencyResult } from '../../api/types'
import { useShell } from '../../components/AppShell'
import { Icon } from '../../components/Icon'
import { AiBadge, Button, Card } from '../../components/ui'
import { useLang } from '../../i18n'
import { parseAmount } from '../../lib/format'
import { PageTitle } from '../common'

const POCKET_NAME: Record<string, [string, string]> = {
  emergency: ['জরুরি পকেট', 'Emergency pocket'], eid: ['ঈদ পকেট', 'Eid pocket'], family: ['বাড়ি পকেট', 'Home pocket'],
  education: ['শিক্ষা পকেট', 'Education pocket'], custom: ['নিজের পকেট', 'Own pocket'], paisa: ['পয়সা-সঞ্চয়', 'Paisa saving'],
}

function OptionCard({ o, i, amount, onTake, requested, onRequest }: {
  o: EmergencyOption; i: number; amount: number; onTake: (o: EmergencyOption) => void; requested: boolean; onRequest: () => void
}) {
  const { L, taka, num } = useLang()
  const loan = o.kind === 'dps_loan'
  const title = loan ? L('DPS-এর বিপরীতে ব্যাংক ঋণের অনুরোধ', 'Bank loan request against your DPS')
    : L(...(POCKET_NAME[o.pocket ?? ''] ?? [o.pocket ?? '', o.pocket ?? '']))
  return (
    <Card className={i === 0 ? 'border-ok ring-1 ring-ok' : ''}>
      <div className="flex items-start gap-3">
        <span className={`flex size-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${i === 0 ? 'bg-ok text-white' : 'bg-transparent text-ink'}`}>{num(i + 1)}</span>
        <div className="flex-1">
          <p className="font-semibold">{title}</p>
          <p className="text-sm text-muted">
            {loan ? L(`সর্বোচ্চ ${taka(o.available)} (ব্যাংকের নিয়ম)`, `Up to ${taka(o.available)} (bank rule)`)
              : L(`আছে ${taka(o.available, { paisa: o.available % 1 !== 0 })}`, `Available ${taka(o.available, { paisa: o.available % 1 !== 0 })}`)}
          </p>
          <p className="mt-1 text-sm text-ink/80">{o.tradeoff_bn}</p>
          {o.affordability_bn && (
            <p className="mt-1 flex gap-1.5 text-sm"><AiBadge className="mt-0.5" /><span>{o.affordability_bn}</span></p>
          )}
          {loan ? (
            <>
              <p className="mt-2 rounded-lg bg-warn-bg px-2 py-1 text-xs font-semibold text-warn">{L('চূড়ান্ত সিদ্ধান্ত ব্যাংক নেবে', 'The bank makes the final decision')}</p>
              <Button variant="outline" full className="mt-2" disabled={requested} onClick={onRequest}>
                {requested ? L('অনুরোধ তৈরি হয়েছে (ডেমো)', 'Request drafted (demo)') : L('ব্যাংকে অনুরোধ পাঠান (ডেমো)', 'Send request to bank (demo)')}
              </Button>
            </>
          ) : (
            <Button variant={i === 0 ? 'blue' : 'outline'} full className="mt-2" onClick={() => onTake(o)}>
              {L(`${taka(Math.min(o.available, amount), { paisa: Math.min(o.available, amount) % 1 !== 0 })} তুলে ওয়ালেটে নিন`,
                `Move ${taka(Math.min(o.available, amount))} to wallet`)}
            </Button>
          )}
        </div>
      </div>
    </Card>
  )
}

export default function Emergency() {
  const { L, taka } = useLang()
  const { uid, refresh } = useShell()
  const [text, setText] = useState('')
  const [res, setRes] = useState<EmergencyResult | null>(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const [requested, setRequested] = useState(false)
  const [msg, setMsg] = useState('')

  const check = async (raw = text) => {
    const amount = parseAmount(raw)
    if (!amount) return setErr(L('কত টাকা লাগবে লিখুন', 'Enter how much you need'))
    setBusy(true)
    setErr('')
    setMsg('')
    setRequested(false)
    try {
      setRes(await api.emergency(uid, amount))
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : L('কিছু একটা ভুল হয়েছে', 'Something went wrong'))
    } finally {
      setBusy(false)
    }
  }
  const take = async (o: EmergencyOption) => {
    if (!res || !o.pocket) return
    try {
      await api.movePocket(uid, o.pocket, 'out', Math.min(o.available, res.amount))
      setMsg(L('টাকা ওয়ালেটে চলে এসেছে', 'Money moved to your wallet'))
      refresh()
      await check(String(res.amount))
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : L('কিছু একটা ভুল হয়েছে', 'Something went wrong'))
    }
  }
  const covered = res ? res.options.filter((o) => o.kind !== 'dps_loan').reduce((a, o) => a + o.available, 0) : 0

  return (
    <div className="pb-6">
      <PageTitle bn="জরুরি টাকা" en="Emergency money" />
      <div className="space-y-3 px-3">
        <Card>
          <p className="flex items-center gap-2 font-semibold">{L('হঠাৎ কত টাকা লাগবে?', 'How much do you need?')}<AiBadge /></p>
          <p className="mt-1 text-sm text-muted">
            {L('হিসাব দেখাবে আগে কোথা থেকে নেওয়া ভালো — নিজের জমানো টাকা আগে, ঋণ শেষে।',
              'Hishab shows where to take it from first — your own savings before any loan.')}
          </p>
          <div className="mt-3 flex gap-2">
            <div className="flex flex-1 items-center rounded-xl border border-line px-3 focus-within:border-upay-blue">
              <span className="font-bold text-muted">৳</span>
              <input inputMode="decimal" aria-label={L('পরিমাণ', 'Amount')} value={text} onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && void check()} placeholder="৩,০০০"
                className="min-h-11 w-full bg-transparent px-2 font-semibold outline-none" />
            </div>
            <Button disabled={busy} onClick={() => void check()}>{busy ? '…' : L('দেখান', 'Show')}</Button>
          </div>
          {err && <p className="mt-2 text-sm text-bad" role="alert">{err}</p>}
        </Card>

        <Card className="border-upay-blue bg-blue-50/50 mt-4">
          <div className="flex items-start gap-3">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-upay-blue/20 text-upay-blue">
              <Icon name="shield" size={20} />
            </span>
            <div>
              <p className="font-bold text-slate-800">{L('লোন পাওয়ার যোগ্যতা', 'Loan Eligibility')}</p>
              <p className="mt-1 text-sm text-slate-600">
                {L('আপনার নিয়মিত লেনদেন ও সঞ্চয়ের উপর ভিত্তি করে আপনি ', 'Based on your regular transactions and savings, you are eligible for up to ')}
                <span className="font-bold text-upay-blue">৳১০,০০০</span>
                {L(' পর্যন্ত ইমার্জেন্সি লোন পাওয়ার যোগ্য। (ডেমো)', ' emergency loan. (Demo)')}
              </p>
            </div>
          </div>
        </Card>

        {msg && <p className="rounded-xl bg-ok-bg p-3 text-sm font-semibold text-ok" role="status">{msg}</p>}

        {res && res.options.length === 0 && (
          <Card className="text-sm">
            <p className="font-semibold">{L('এখন পকেটে বা DPS-এ কোনো জমা নেই', 'No pocket or DPS savings yet')}</p>
            <p className="mt-1 text-muted">
              {L('পরের বার এমন সময়ের জন্য জরুরি পকেটে অল্প অল্প করে রাখা শুরু করুন — সপ্তাহে ৳১০০ হলেও চলবে।',
                'Start putting a little into the emergency pocket for next time — even ৳100 a week helps.')}
            </p>
            <Link to="/app/savings/pockets" className="mt-2 inline-block font-semibold text-upay-blue underline">{L('পকেটে যান', 'Go to pockets')}</Link>
          </Card>
        )}

        {res && res.options.length > 0 && (
          <>
            <p className="px-1 text-sm text-muted">
              {covered >= res.amount
                ? L(`আপনার জমানো টাকাতেই ${taka(res.amount)} হয়ে যাবে।`, `Your savings cover ${taka(res.amount)}.`)
                : L(`জমানো টাকায় ${taka(covered)} হবে; বাকিটার জন্য নিচের বিকল্প দেখুন।`, `Savings cover ${taka(covered)}; see below for the rest.`)}
            </p>
            {res.options.map((o, i) => (
              <OptionCard key={`${o.kind}-${o.pocket}`} o={o} i={i} amount={res.amount} onTake={(x) => void take(x)}
                requested={requested} onRequest={() => setRequested(true)} />
            ))}
            {requested && (
              <p className="rounded-xl bg-transparent p-3 text-xs text-muted">
                {L('এটি ডেমো — কোনো ব্যাংকে অনুরোধ পাঠানো হয়নি। আসল সেবায় ব্যাংক নিজস্ব নিয়মে যাচাই করবে।',
                  'Demo only — nothing was sent. In the real service the bank reviews it under its own rules.')}
              </p>
            )}
          </>
        )}

        <p className="flex items-start gap-2 px-1 text-xs text-muted">
          <Icon name="info" size={14} className="mt-0.5 shrink-0" />
          {L('হিসাব কোনো ঋণ দেয় না, ঋণের সিদ্ধান্তও নেয় না; DPS-ভিত্তিক সীমা ব্যাংকের নির্ধারিত নিয়ম।',
            'Hishab does not give or decide on loans; the DPS-based limit is a fixed bank rule.')}
        </p>
      </div>
    </div>
  )
}
