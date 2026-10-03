import { useEffect, useRef, useState } from 'react'
import { api, ApiError } from '../../api/client'
import type { ChatAnswer } from '../../api/types'
import { useShell } from '../../components/AppShell'
import { Icon } from '../../components/Icon'
import { AiBadge } from '../../components/ui'
import { useLang } from '../../i18n'
import { isVoiceSupported, listenVoice } from '../../lib/voice'
import { speakBangla } from '../../lib/accessibility'
import { RouteWidget } from '../../components/RouteWidget'
import type { RouteResult } from '../../api/types'

const SUGGESTED = [
  'মাসের শেষে টাকা কম পড়ে কেন?',
  '৬ মাসে ৳৩০,০০০ জমাতে পারব?',
  'cash-out কীভাবে কমাব?',
  'এই লেনদেনগুলো বুঝিয়ে বলো',
]
const MAX = 500

const TOOL_BN: Record<string, string> = {
  get_home_summary: 'ব্যালেন্স আর সামনের ৩০ দিনের হিসাব', get_shortfall_drivers: 'টাকা কম পড়ার কারণ',
  list_actions: 'তোমার জন্য পরামর্শ', simulate_action: 'পরামর্শ মানলে কী হবে', plan_goal: 'লক্ষ্যের হিসাব',
  plan_eid: 'ঈদের হিসাব', find_route: 'টাকা পাঠানোর পথ ও fee',
  get_transactions_summary: 'লেনদেনের সারাংশ', get_health: 'আর্থিক স্বাস্থ্য', get_readiness: 'নিয়মিততার সংকেত',
  get_lessons: 'ছোট পাঠ', get_levels: 'সঞ্চয় লেভেল', emergency_options: 'জরুরি টাকার উপায়',
}

type Msg = { role: 'user' | 'bot'; text: string; answer?: ChatAnswer }

function Sources({ a }: { a: ChatAnswer }) {
  const { L } = useLang()
  const [open, setOpen] = useState(false)
  if (!a.used_tools.length) return null
  return (
    <div className="mt-2 border-t border-line pt-1.5">
      <button onClick={() => setOpen((o) => !o)} aria-expanded={open} className="flex items-center gap-1 text-xs font-semibold text-upay-blue">
        {L('যে তথ্য দেখে উত্তর', 'What this answer used')}
        <Icon name="chevron" size={12} className={`transition ${open ? 'rotate-90' : ''}`} />
      </button>
      {open && (
        <ul className="mt-1 list-disc pl-4 text-xs text-muted">
          {a.used_tools.map((t, i) => <li key={`${t.name}-${i}`}>{TOOL_BN[t.name] ?? t.name}</li>)}
        </ul>
      )}
    </div>
  )
}

export default function Ask() {
  const { L } = useLang()
  const { uid, shell } = useShell()
  const [msgs, setMsgs] = useState<Msg[]>([])
  const [text, setText] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const [listening, setListening] = useState(false)
  const [micLang, setMicLang] = useState<'bn-BD' | 'en-US'>('bn-BD')
  const voice = isVoiceSupported()
  const end = useRef<HTMLDivElement>(null)

  useEffect(() => { 
    if (end.current) {
      setTimeout(() => {
        end.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
      }, 100)
    }
  }, [msgs, busy])

  const ask = async (q: string) => {
    const message = q.trim()
    if (!message) return setErr(L('প্রশ্ন লিখুন', 'Type a question'))
    if (message.length > MAX) return setErr(L(`প্রশ্ন ${MAX} অক্ষরের মধ্যে রাখুন`, `Keep it under ${MAX} characters`))
    setErr('')
    setText('')
    setMsgs((m) => [...m, { role: 'user', text: message }])
    setBusy(true)
    try {
      const a = await api.chat(uid, message)
      setMsgs((m) => [...m, { role: 'bot', text: a.text, answer: a }])
        // speakBangla(a.text) // Disabled by user request
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : L('উত্তর আনা যায়নি — আবার চেষ্টা করুন', 'Could not get an answer — try again'))
    } finally {
      setBusy(false)
    }
  }
  const mic = async () => {
    setErr('')
    setListening(true)
    try {
      const said = await listenVoice(micLang)
      if (said) {
        setText(said)
        await ask(said)
      }
    } catch (e) {
      const code = e instanceof Error ? e.message : ''
      setErr(code === 'not-allowed' ? L('মাইক্রোফোনের অনুমতি দিন', 'Allow microphone access')
        : L('কথা বোঝা যায়নি — আবার বলুন বা লিখুন', 'Didn\'t catch that — try again or type'))
    } finally {
      setListening(false)
    }
  }

  return (
    <div className="flex min-h-[60dvh] flex-col px-4 pb-6 bg-slate-100">
      <div className="flex-1 space-y-3">
        {msgs.length === 0 && (
          <div className="rounded-2xl bg-white p-3 shadow-sm border border-slate-100 flex flex-col gap-1 mx-1 mt-1">
            <p className="flex items-center gap-1.5 text-[14px] font-semibold text-slate-800"><AiBadge />{L(`${shell?.name.split(' ')[0] ?? ''}, টাকা নিয়ে যা খুশি জিজ্ঞেস করুন`, 'Ask anything about your money')}</p>
            <p className="mt-1 text-sm text-muted">{L('বাংলায় লিখে বা বলে জিজ্ঞেস করতে পারেন। উত্তর আপনার নিজের লেনদেনের হিসাব থেকে।', 'Type or speak in Bangla. Answers come from your own transactions.')}</p>
          </div>
        )}
        {msgs.map((m, i) => m.role === 'user' ? (
          <div key={i} className="ml-auto max-w-[85%] rounded-2xl rounded-tr-sm bg-upay-blue px-3.5 py-2 text-[14px] text-white shadow-md shadow-upay-blue/20 animate-slide-up">{m.text}</div>
        ) : (
          <div key={i} className="mr-auto max-w-[85%] rounded-2xl rounded-tl-sm border border-slate-100 bg-white px-3.5 py-2.5 text-[14px] text-slate-800 shadow-sm animate-slide-up">
            {m.answer?.ai && <AiBadge className="mb-1" />}
            <p className="whitespace-pre-line leading-relaxed">{m.text}</p>
            {m.answer?.used_tools.map(t => t.name === 'find_route' && t.result ? (
              <RouteWidget key="route" result={t.result as RouteResult} />
            ) : null)}
            {m.answer && <Sources a={m.answer} />}
          </div>
        ))}
        {busy && (
          <div className="mr-auto max-w-[85%] flex items-center gap-2 rounded-2xl rounded-tl-sm border border-slate-100 bg-white px-3.5 py-2.5 text-[13px] text-muted shadow-sm" role="status">
            <span className="size-4 animate-spin rounded-full border-2 border-upay-blue border-t-transparent" />{L('হিসাব দেখছি…', 'Checking your numbers…')}
          </div>
        )}
        <div ref={end} />
      </div>
      <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
        {SUGGESTED.map((q) => (
          <button key={q} disabled={busy} onClick={() => void ask(q)}
            className="shrink-0 rounded-full border border-upay-blue/30 bg-white px-3 py-1.5 text-[12.5px] text-upay-blue disabled:opacity-50">{q}</button>
        ))}
      </div>
      {err && <p className="mt-2 text-sm text-bad" role="alert">{err}</p>}
      <form className="sticky bottom-2 z-10 mt-3 flex items-end gap-2 rounded-3xl bg-white/70 backdrop-blur-lg border border-white/50 p-1.5 shadow-[0_4px_20px_rgb(0,0,0,0.04)]" onSubmit={(e) => { e.preventDefault(); void ask(text) }}>
        <div className="flex-1 rounded-2xl bg-white/60 px-3.5 py-1.5 focus-within:bg-white focus-within:ring-1 focus-within:ring-upay-blue/50 transition-all border border-transparent">
          <textarea rows={1} value={text} onChange={(e) => setText(e.target.value)} aria-label={L('প্রশ্ন', 'Question')}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void ask(text) } }}
            placeholder={L('যেমন: ঈদের জন্য ৳৫,০০০ জমাতে পারব?', 'e.g. Can I save ৳5,000 for Eid?')}
            className="max-h-28 min-h-9 w-full resize-none bg-transparent py-1 outline-none text-[14px]" />
          {text.length > MAX - 50 && <p className={`text-right text-[11px] ${text.length > MAX ? 'text-bad' : 'text-muted'}`}>{text.length}/{MAX}</p>}
        </div>
        {voice ? (
          <button type="button" onClick={() => void mic()} disabled={busy || listening} aria-label={L('বলে জিজ্ঞেস করুন', 'Ask by voice')}
            className={`flex size-10 shrink-0 items-center justify-center rounded-full ${listening ? 'animate-pulse bg-bad text-white' : 'bg-upay-yellow text-upay-blue'}`}>
            <Icon name="mic" size={18} />
          </button>
        ) : (
          <span title={L('এই ব্রাউজারে ভয়েস চলে না — Chrome ব্যবহার করুন', 'Voice needs Chrome')}
            className="flex size-10 shrink-0 cursor-help items-center justify-center rounded-full bg-transparent text-muted" aria-label={L('ভয়েস নেই', 'Voice unavailable')}>
            <Icon name="mic" size={18} />
          </span>
        )}
        <button type="submit" disabled={busy} aria-label={L('পাঠান', 'Send')} className="flex size-10 shrink-0 items-center justify-center rounded-full bg-upay-blue text-white disabled:opacity-50">
          <Icon name="send" size={16} />
        </button>
      </form>
    </div>
  )
}
