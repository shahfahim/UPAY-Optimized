import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Button, TextMark } from '../../components/ui'
import { useLang } from '../../i18n'

const SLIDES = [
  { bn: 'টাকা আর কত দিন চলবে — আগেই জেনে নিন', en: 'Know how long your money will last — ahead of time', icon: '📅' },
  { bn: 'সবচেয়ে কম খরচে বাড়িতে টাকা পাঠান', en: 'Send money home the cheapest way', icon: '🧭' },
  { bn: 'পয়সা থেকে DPS — ধাপে ধাপে সঞ্চয়', en: 'From paisa to DPS — save step by step', icon: '🌱' },
]

export default function Welcome() {
  const { L, lang, setLang } = useLang()
  const [i, setI] = useState(0)
  useEffect(() => {
    const t = window.setInterval(() => setI((x) => (x + 1) % SLIDES.length), 3500)
    return () => window.clearInterval(t)
  }, [])
  const s = SLIDES[i]
  return (
    <div className="flex flex-1 flex-col">
      <div className="flex items-center justify-between p-4">
        <TextMark />
        <button onClick={() => setLang(lang === 'bn' ? 'en' : 'bn')}
          className="rounded-full bg-upay-blue/10 px-3 py-1 text-xs font-semibold text-upay-blue">
          {lang === 'bn' ? 'English' : 'বাংলা'}
        </button>
      </div>
      <div className="flex flex-1 flex-col items-center justify-center px-8 text-center">
        <div key={i} className="animate-rise">
          <div className="mb-6 text-6xl" aria-hidden="true">{s.icon}</div>
          <p className="text-xl font-semibold leading-snug">{L(s.bn, s.en)}</p>
        </div>
        <div className="mt-8 flex gap-1.5">
          {SLIDES.map((_, k) => (
            <button key={k} aria-label={`${k + 1}`} onClick={() => setI(k)}
              className={`h-2 rounded-full transition-all ${k === i ? 'w-6 bg-upay-blue' : 'w-2 bg-line'}`} />
          ))}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 pb-8">
        <Link to="/register"><Button full variant="blue">{L('রেজিস্ট্রেশন', 'Registration')}</Button></Link>
        <Link to="/login"><Button full variant="yellow">{L('লগইন', 'Login')}</Button></Link>
      </div>
    </div>
  )
}
