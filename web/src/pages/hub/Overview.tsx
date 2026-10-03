import { Link } from 'react-router-dom'
import { AreaChart, Area, Tooltip, ResponsiveContainer } from 'recharts'
import { api } from '../../api/client'
import { useShell } from '../../components/AppShell'
import { Icon } from '../../components/Icon'
import { ErrorNote, Spinner, Card, Button, AiBadge } from '../../components/ui'
import { useLang } from '../../i18n'
import { useApi } from '../../lib/useApi'
import type { Lesson } from '../../api/types'

export default function Overview() {
  const { L } = useLang()
  const { uid } = useShell()
  const { data: home, error, loading, reload } = useApi(() => api.home(uid), [uid])

  if (loading && !home) return <Spinner label={L('হিসাব করা হচ্ছে…', 'Working it out…')} />
  if (error) return <ErrorNote message={error} onRetry={reload} />
  if (!home) return null

  // Mock 30-Day Forecast Data for the AreaChart
  const forecastData = home.forecast?.p50.map((v, i) => ({ day: i + 1, balance: v })) || []

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top Blue Section */}
      <div className="bg-gradient-to-b from-[#083b7a] to-[#0b4ea2] px-4 pt-6 pb-24 rounded-b-[40px]">
        <div className="flex items-center justify-center gap-2 mb-6 text-white bg-white/20 w-fit mx-auto px-4 py-1.5 rounded-full shadow-sm backdrop-blur-md">
          <Icon name="shield" size={16} className="text-yellow-400" />
          <span className="text-sm font-medium">আজ আপনার নিরাপদ খরচ ৳{home.safe_spend}</span>
        </div>
      </div>

      {/* Massive Stunning Card - overlaps blue and surface */}
      <div className="px-4 -mt-20 animate-slide-up">
        <div className="bg-[#0f172a] rounded-3xl p-6 shadow-2xl ring-4 ring-yellow-400/50 shadow-yellow-400/20 relative overflow-hidden">
          {/* Inner Glow / Gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-upay-blue/30 to-transparent pointer-events-none" />
          
          <div className="relative z-10 flex flex-col items-center">
            <h2 className="text-white text-5xl font-extrabold tracking-tight">{home.forecast ? `৳${(home.forecast.monthly_income - home.forecast.monthly_expense).toLocaleString('bn-BD')}` : '৳০'}</h2>
            <p className="text-blue-200 text-sm font-medium mt-1 uppercase tracking-widest">{L('বর্তমান ব্যালেন্স', 'Current Balance')}</p>
          </div>

          <div className="mt-8 h-32 w-full relative z-10">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={forecastData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                  formatter={(val: number) => [`৳${Math.round(val)}`, 'Forecast']}
                  labelStyle={{ display: 'none' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="balance" 
                  stroke="#60a5fa" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorBalance)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 3-column Grid Buttons */}
      <div className="px-4 mt-8 grid grid-cols-3 gap-4">
        {/* Button 1: Hishab AI */}
          <Link to="/app/hishab/ask" className="flex flex-col items-center justify-center bg-white rounded-2xl p-4 shadow-[0_20px_50px_-12px_rgba(11,78,162,0.15)] hover:scale-105 transition-all duration-300 ease-out border border-gray-100 animate-slide-up">
          <div className="h-12 w-12 rounded-full bg-blue-50 flex items-center justify-center mb-3">
            <Icon name="spark" size={24} className="text-upay-blue" />
          </div>
          <span className="text-sm font-bold text-ink text-center">Hishab AI</span>
        </Link>

        {/* Button 2: Smart DPS */}
        <Link to="/app/savings" className="flex flex-col items-center justify-center bg-white rounded-2xl p-4 shadow-[0_20px_50px_-12px_rgba(11,78,162,0.15)] hover:scale-105 transition-all duration-300 ease-out border border-gray-100 animate-slide-up">
          <div className="h-12 w-12 rounded-full bg-green-50 flex items-center justify-center mb-3">
            <Icon name="chart" size={24} className="text-green-600" />
          </div>
          <span className="text-sm font-bold text-ink text-center">Smart DPS</span>
        </Link>

        {/* Button 3: Ask Hishab (Yellow Mic) */}
        <Link to="/app/hishab/ask" className="flex flex-col items-center justify-center bg-white rounded-2xl p-4 shadow-[0_20px_50px_-12px_rgba(11,78,162,0.15)] hover:scale-105 transition-all duration-300 ease-out border border-gray-100 animate-slide-up">
          <div className="h-12 w-12 rounded-full bg-[#FFD700] flex items-center justify-center mb-3 shadow-inner animate-pulse-mic">
            <Icon name="mic" size={24} className="text-ink" />
          </div>
          <span className="text-sm font-bold text-ink text-center">Ask Hishab</span>
        </Link>
      </div>

    </div>
  )
}

export function LessonCard({ lesson, onDone }: { lesson: Lesson; onDone: () => void }) {
  const { L } = useLang()
  const { uid } = useShell()
  const respond = async (ok: boolean) => {
    await api.lessonRespond(uid, lesson.id, ok).catch(() => undefined)
    onDone()
  }
  return (
    <Card className="border-slate-200 shadow-[0_10px_40px_-10px_rgba(0,0,0,0.08)] bg-white">
      <div className="mb-1 flex items-center gap-2">
        <Icon name="book" size={18} className="text-slate-500" />
        <AiBadge />
        <span className="text-xs text-slate-500">{L('তোমার জন্য ছোট পাঠ', 'A short lesson for you')}</span>
      </div>
      <p className="font-semibold text-slate-800">{lesson.title_bn}</p>
      <p className="mt-1 text-sm leading-relaxed text-slate-600">{lesson.body_bn}</p>
      <div className="mt-3 flex gap-2">
        <Button variant="outline" className="flex-1 !min-h-9 text-sm text-slate-700 border-slate-300" onClick={() => void respond(true)}>{L('বুঝেছি', 'Got it')}</Button>
        <Button variant="ghost" className="flex-1 !min-h-9 text-sm text-slate-500" onClick={() => void respond(false)}>{L('কাজে লাগবে না', 'Not useful')}</Button>
      </div>
    </Card>
  )
}
