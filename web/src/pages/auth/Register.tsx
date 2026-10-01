import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, ApiError } from '../../api/client'
import { PinPad } from '../../components/PinPad'
import { Button } from '../../components/ui'
import { useLang } from '../../i18n'
import { toAsciiDigits, toBnDigits } from '../../lib/format'
import { setSession } from '../../lib/session'

export default function Register() {
  const { L, lang } = useLang()
  const navigate = useNavigate()
  const [step, setStep] = useState<1 | 2 | 3>(1)
  const [mobile, setMobile] = useState('')
  const [demoOtp, setDemoOtp] = useState('')
  const [otp, setOtp] = useState('')
  const [name, setName] = useState('')
  const [pin, setPin] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const m = toAsciiDigits(mobile)

  async function run(fn: () => Promise<void>) {
    setErr('')
    setBusy(true)
    try {
      await fn()
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : L('কিছু একটা ভুল হয়েছে', 'Something went wrong'))
    } finally {
      setBusy(false)
    }
  }

  const start = () => {
    if (!/^01[3-9]\d{8}$/.test(m)) return setErr(L('সঠিক মোবাইল নম্বর দিন', 'Enter a valid mobile number'))
    void run(async () => {
      const r = await api.registerStart(m)
      setDemoOtp(r.otp)
      setStep(2)
    })
  }
  const checkOtp = () => {
    if (toAsciiDigits(otp) !== demoOtp) return setErr(L('OTP সঠিক নয়', 'Wrong OTP'))
    setStep(3)
  }
  const finish = () => {
    if (name.trim().length < 2) return setErr(L('নাম লিখুন', 'Enter your name'))
    if (pin.length !== 6) return setErr(L('৬ সংখ্যার PIN দিন', 'Choose a 6-digit PIN'))
    void run(async () => {
      const r = await api.registerVerify(m, toAsciiDigits(otp), name.trim(), pin)
      setSession({ token: r.token, userId: r.user_id })
      navigate('/app/home', { replace: true })
    })
  }

  const steps = [L('নম্বর', 'Number'), 'OTP', L('নাম ও PIN', 'Name & PIN')]
  return (
    <div className="flex flex-1 flex-col">
      <div className="flex items-center gap-3 bg-upay-yellow px-4 py-3">
        <Link to="/welcome" aria-label={L('ফিরে যান', 'Back')} className="text-xl">←</Link>
        <span className="font-semibold">{L('রেজিস্ট্রেশন', 'Registration')}</span>
      </div>
      <div className="flex gap-2 px-5 pt-4">
        {steps.map((s, k) => (
          <div key={s} className="flex-1">
            <div className={`h-1.5 rounded-full ${k < step ? 'bg-upay-blue' : 'bg-line'}`} />
            <p className={`mt-1 text-[11px] ${k < step ? 'font-semibold text-upay-blue' : 'text-muted'}`}>{s}</p>
          </div>
        ))}
      </div>
      <div className="flex-1 px-5 py-5">
        <p className="mb-4 rounded-xl bg-warn-bg px-3 py-2 text-xs font-semibold text-warn">
          {L('Demo — আসল তথ্য দেবেন না। একটা নমুনা ইতিহাস তৈরি হবে।', 'Demo — do not enter real details. A sample history is created.')}
        </p>
        {step === 1 && (
          <>
            <label className="mb-1 block text-sm font-semibold" htmlFor="rmobile">{L('মোবাইল নম্বর', 'Mobile number')}</label>
            <input id="rmobile" inputMode="numeric" placeholder="01XXXXXXXXX" value={mobile}
              onChange={(e) => { setMobile(e.target.value); setErr('') }}
              className="h-12 w-full rounded-xl border border-line bg-surface px-3 font-[Inter] text-lg tracking-wider outline-none focus:border-upay-blue" />
            <Button full className="mt-5" onClick={start} disabled={busy}>{L('এগিয়ে যান', 'Continue')}</Button>
          </>
        )}
        {step === 2 && (
          <>
            <div className="mb-4 rounded-xl border border-dashed border-upay-blue p-3 text-center">
              <p className="text-xs text-muted">Demo OTP</p>
              <p className="font-[Inter] text-2xl font-bold tracking-[0.3em] text-upay-blue">
                {lang === 'bn' ? toBnDigits(demoOtp) : demoOtp}
              </p>
            </div>
            <label className="mb-1 block text-sm font-semibold" htmlFor="otp">OTP</label>
            <input id="otp" inputMode="numeric" value={otp} onChange={(e) => { setOtp(e.target.value); setErr('') }}
              className="h-12 w-full rounded-xl border border-line bg-surface px-3 text-center font-[Inter] text-xl tracking-[0.3em] outline-none focus:border-upay-blue" />
            <Button full className="mt-5" onClick={checkOtp}>{L('যাচাই করুন', 'Verify')}</Button>
          </>
        )}
        {step === 3 && (
          <>
            <label className="mb-1 block text-sm font-semibold" htmlFor="rname">{L('আপনার নাম', 'Your name')}</label>
            <input id="rname" value={name} maxLength={40} onChange={(e) => { setName(e.target.value); setErr('') }}
              className="mb-4 h-12 w-full rounded-xl border border-line bg-surface px-3 outline-none focus:border-upay-blue" />
            <p className="mb-2 text-sm font-semibold">{L('৬ সংখ্যার PIN বেছে নিন', 'Choose a 6-digit PIN')}</p>
            <PinPad value={pin} onChange={(v) => { setPin(v); setErr('') }} />
            <Button full className="mt-5" onClick={finish} disabled={busy}>
              {busy ? L('অ্যাকাউন্ট তৈরি হচ্ছে…', 'Creating account…') : L('অ্যাকাউন্ট খুলুন', 'Create account')}
            </Button>
          </>
        )}
        {err && <p className="mt-3 text-center text-sm text-bad" role="alert">{err}</p>}
      </div>
    </div>
  )
}
