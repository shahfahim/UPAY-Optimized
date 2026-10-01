import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, ApiError } from '../../api/client'
import type { DemoUser } from '../../api/types'
import { PinPad } from '../../components/PinPad'
import { Button, Sheet, TextMark } from '../../components/ui'
import { useLang } from '../../i18n'
import { toAsciiDigits } from '../../lib/format'
import { setSession } from '../../lib/session'

const PERSONA_BN: Record<string, string> = {
  garment_worker: 'গার্মেন্টস কর্মী', daily_wage: 'দিনমজুর', shop_owner: 'দোকানদার', student: 'ছাত্র/ছাত্রী',
}

export default function Login() {
  const { L } = useLang()
  const navigate = useNavigate()
  const [mobile, setMobile] = useState('')
  const [pin, setPin] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const [users, setUsers] = useState<DemoUser[]>([])
  const [forgot, setForgot] = useState(false)

  useEffect(() => {
    api.users().then(setUsers).catch(() => setUsers([]))
  }, [])

  const mobileOk = /^01[3-9]\d{8}$/.test(toAsciiDigits(mobile))

  async function doLogin(m: string, p: string) {
    setErr('')
    setBusy(true)
    try {
      const r = await api.login(m, p)
      setSession({ token: r.token, userId: r.user_id })
      navigate('/app/home', { replace: true })
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : L('লগইন হয়নি', 'Login failed'))
      setPin('')
    } finally {
      setBusy(false)
    }
  }

  function submit() {
    if (!mobileOk) return setErr(L('সঠিক মোবাইল নম্বর দিন', 'Enter a valid mobile number'))
    if (pin.length !== 6) return setErr(L('৬ সংখ্যার PIN দিন', 'Enter your 6-digit PIN'))
    void doLogin(toAsciiDigits(mobile), pin)
  }

  return (
    <div className="flex flex-1 flex-col">
      <div className="flex items-center gap-3 bg-upay-yellow px-4 py-3">
        <Link to="/welcome" aria-label={L('ফিরে যান', 'Back')} className="text-xl">←</Link>
        <span className="font-semibold">{L('লগইন', 'Log in')}</span>
      </div>
      <div className="flex-1 overflow-y-auto px-5 py-5">
        <div className="mb-5 flex items-center gap-3">
          <TextMark />
          <div>
            <p className="font-semibold">{L('অ্যাকাউন্টে লগইন', 'Account login')}</p>
            <p className="text-xs text-muted">{L('মোবাইল নম্বর আর PIN দিন', 'Enter your mobile number and PIN')}</p>
          </div>
        </div>
        <p className="mb-4 rounded-xl bg-warn-bg px-3 py-2 text-xs font-semibold text-warn">
          {L('Demo — আসল PIN দেবেন না', 'Demo — do not enter a real PIN')}
        </p>
        <label className="mb-1 block text-sm font-semibold" htmlFor="mobile">{L('মোবাইল নম্বর', 'Mobile number')}</label>
        <input id="mobile" inputMode="numeric" autoComplete="off" placeholder="01XXXXXXXXX" value={mobile}
          onChange={(e) => { setMobile(e.target.value); setErr('') }}
          className="mb-1 h-12 w-full rounded-xl border border-line bg-surface px-3 font-[Inter] text-lg tracking-wider outline-none focus:border-upay-blue" />
        {mobile && !mobileOk && <p className="mb-2 text-xs text-bad">{L('সঠিক মোবাইল নম্বর দিন', 'Enter a valid mobile number')}</p>}
        <p className="mb-2 mt-4 text-sm font-semibold">{L('PIN দিন', 'Enter PIN')}</p>
        <PinPad value={pin} onChange={(v) => { setPin(v); setErr('') }} />
        {err && <p className="mt-3 text-center text-sm text-bad" role="alert">{err}</p>}
        <Button full className="mt-4" onClick={submit} disabled={busy}>{busy ? '…' : L('লগইন', 'Log in')}</Button>
        <button className="mt-3 w-full text-center text-sm text-upay-blue" onClick={() => setForgot(true)}>
          {L('PIN ভুলে গেছেন?', 'Forgot your PIN?')}
        </button>

        <div className="mt-6 border-t border-line pt-4">
          <p className="mb-2 text-sm font-semibold">{L('Demo user হিসেবে ঢুকুন', 'Enter as a demo user')}</p>
          <div className="space-y-2">
            {users.slice(0, 5).map((d) => (
              <button key={d.user_id} disabled={busy} onClick={() => void doLogin(d.phone, '123456')}
                className="flex w-full items-center gap-3 rounded-xl border border-line px-3 py-2 text-left hover:bg-surface">
                <span className="flex size-9 items-center justify-center rounded-full bg-upay-yellow text-sm font-bold">
                  {d.name.slice(0, 1)}
                </span>
                <span className="flex-1">
                  <span className="block text-sm font-semibold">{d.name}</span>
                  <span className="block text-xs text-muted">{L(PERSONA_BN[d.persona] ?? d.persona, d.persona.replace('_', ' '))} · {d.area}</span>
                </span>
                <span className="text-upay-blue">→</span>
              </button>
            ))}
          </div>
        </div>
      </div>
      <Sheet open={forgot} onClose={() => setForgot(false)} title={L('PIN ভুলে গেছেন?', 'Forgot your PIN?')}>
        <p className="text-sm text-muted">{L('এটা demo। সব demo user-এর PIN ১২৩৪৫৬, অথবা উপরের তালিকা থেকে ঢুকুন।',
          'This is a demo. Every demo user\'s PIN is 123456, or pick a user from the list.')}</p>
      </Sheet>
    </div>
  )
}
