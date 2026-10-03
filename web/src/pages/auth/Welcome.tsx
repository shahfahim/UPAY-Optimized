import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Button, TextMark } from '../../components/ui'
import { useLang } from '../../i18n'

const SLIDES = [
  { bn: 'দ্রুত এবং নিরাপদে টাকা লেনদেন করুন', en: 'Fast and secure transactions', icon: '💸' },
  { bn: 'সবচেয়ে কম খরচে বাড়িতে টাকা পাঠান', en: 'Send money home the cheapest way', icon: '🏠' },
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
      <div className="relative overflow-hidden bg-[#ffd500] px-4 py-4 shadow-[0_4px_20px_-5px_rgba(0,0,0,0.15)] z-10 flex items-center justify-between">
        
        {/* Abstract Geometric Background - Main Deep Blue Split */}
        <div className="absolute -top-10 -bottom-20 left-[48%] right-0 -skew-x-[24deg] bg-gradient-to-br from-[#083b7a] to-[#0b4ea2] shadow-[-12px_0_25px_rgba(0,0,0,0.3)] z-0"></div>
        
        {/* Abstract Geometric Background - Accent Light Blue Split */}
        <div className="absolute -top-10 -bottom-20 left-[82%] right-0 -skew-x-[24deg] bg-[#1a64c4] shadow-[-6px_0_15px_rgba(0,0,0,0.2)] z-0"></div>

        {/* Subtle Halftone/Dot Pattern Overlay */}
        <div className="absolute inset-0 pointer-events-none mix-blend-overlay opacity-15 z-0" style={{
          backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
          backgroundSize: '16px 16px'
        }}></div>

        <div className="relative z-10 scale-[1.15] origin-left">
          <TextMark />
        </div>
        
        <button onClick={() => setLang(lang === 'bn' ? 'en' : 'bn')}
          className="relative z-10 rounded-full bg-white/10 text-white backdrop-blur-md shadow-sm border border-white/20 px-4 py-1.5 text-[13px] font-bold transition-transform active:scale-95">
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
