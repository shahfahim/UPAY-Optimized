import { useState } from 'react'
import { Link } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
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

  const [view, setView] = useState<'all' | 'in_out' | 'savings_loan'>('all')
  const [monthOffset, setMonthOffset] = useState('0')

  if (loading && !home) return <Spinner label={L('হিসাব করা হচ্ছে…', 'Working it out…')} />
  if (error) return <ErrorNote message={error} onRetry={reload} />
  if (!home) return null



  const monthlyIncomeBase = home.forecast?.monthly_income ?? 12000
  const monthlyExpenseBase = home.forecast?.monthly_expense ?? 4500
  const dpsBase = 2000
  const loanBase = 1500

  // Mock historical data multiplier
  const multiplier = monthOffset === '0' ? 1 : monthOffset === '1' ? 0.85 : 0.92

  const income = monthlyIncomeBase * multiplier
  const expense = monthlyExpenseBase * multiplier
  const dps = dpsBase * multiplier
  const loan = loanBase * multiplier

  const chartData = []
  if (view === 'all' || view === 'in_out') {
    chartData.push({ name: L('আয়', 'Income'), value: income, fill: '#22c55e' })
    chartData.push({ name: L('খরচ', 'Expense'), value: expense, fill: '#f87171' })
  }
  if (view === 'all' || view === 'savings_loan') {
    chartData.push({ name: L('ডিপিএস', 'DPS'), value: dps, fill: '#0ea5e9' })
    chartData.push({ name: L('লোন', 'Loan'), value: loan, fill: '#f59e0b' })
  }

  return (
    <div className="min-h-screen bg-transparent pb-20">
      {/* Simple Top Section */}
      <div className="bg-upay-blue px-4 pt-6 pb-12 rounded-b-3xl animate-fade-in">
        <div className="flex flex-col items-center justify-center mt-2">
          <p className="text-blue-100 text-sm font-medium mb-1">{L('বর্তমান ব্যালেন্স', 'Current Balance')}</p>
          <h2 className="text-white text-4xl font-bold tracking-tight">
            ৳{currentBalance.toLocaleString('en-US')}
          </h2>
        </div>
      </div>

      {/* Simple Bar Chart Card */}
      <div className="px-4 -mt-6 animate-slide-up" style={{ animationDelay: "100ms" }}>
        <Card className="bg-white shadow-[0_8px_30px_rgb(0,0,0,0.06)] border-none rounded-2xl">
          <div className="flex flex-col mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-slate-800">{L('ওভারভিউ', 'Overview')}</h3>
                <AiBadge />
              </div>
              <select 
                value={monthOffset} 
                onChange={e => setMonthOffset(e.target.value)}
                className="bg-transparent text-[13px] font-bold text-slate-700 outline-none cursor-pointer"
              >
                <option value="0">{L('চলতি মাস', 'This Month')}</option>
                <option value="1">{L('গত মাস', 'Last Month')}</option>
                <option value="2">{L('আগস্ট ২০২৬', 'August 2026')}</option>
              </select>
            </div>
            <div className="flex gap-2 overflow-x-auto no-scrollbar mt-3 pb-1">
              <button onClick={() => setView('all')} className={`px-3 py-1.5 rounded-full text-[11px] font-bold whitespace-nowrap transition-colors ${view === 'all' ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600'}`}>{L('সব ওভারভিউ', 'All')}</button>
              <button onClick={() => setView('in_out')} className={`px-3 py-1.5 rounded-full text-[11px] font-bold whitespace-nowrap transition-colors ${view === 'in_out' ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600'}`}>{L('আয়-ব্যয়', 'Income/Expense')}</button>
              <button onClick={() => setView('savings_loan')} className={`px-3 py-1.5 rounded-full text-[11px] font-bold whitespace-nowrap transition-colors ${view === 'savings_loan' ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600'}`}>{L('ডিপিএস ও লোন', 'DPS/Loan')}</button>
            </div>
          </div>
          <div className="h-48 w-full [&_svg]:outline-none select-none">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 15, right: 10, left: -20, bottom: 0 }} barSize={40}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 13, fill: '#64748b', fontWeight: 600 }} />
                <YAxis tickFormatter={(v) => `৳ ${(v / 1000).toFixed(0)}k`} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                <Tooltip 
                  cursor={{ fill: '#f1f5f9', opacity: 0.5 }} 
                  content={({ active, payload, label }: any) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="bg-slate-800/95 backdrop-blur-md text-white text-[13px] rounded-xl py-2 px-3 shadow-xl border border-slate-700/50">
                          <p className="font-medium text-slate-300">{label}</p>
                          <p className="text-white font-bold mt-0.5 tracking-wide">
                            ৳ {payload[0].value.toLocaleString('en-US')}
                          </p>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Bar dataKey="value" radius={[8, 8, 8, 8]} background={{ fill: '#f8fafc', radius: [8, 8, 8, 8] }} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Quick Actions Grid */}
      <div className="px-4 mt-4 animate-slide-up" style={{ animationDelay: "200ms" }}>
        <div className="grid grid-cols-2 gap-3">
          <Link to="/app/agents" className="block">
            <Card className="bg-white shadow-[0_4px_20px_rgb(0,0,0,0.04)] border-none rounded-2xl p-4 flex flex-col items-center justify-center gap-2 h-full active:scale-95 transition-transform">
              <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-upay-blue mb-1">
                <Icon name="map-pin" size={20} />
              </div>
              <span className="font-semibold text-slate-800">{L('এজেন্ট খুঁজুন', 'Find Agent')}</span>
              <span className="text-xs text-slate-500 text-center">{L('নিকটস্থ এজেন্ট ও তারল্য', 'Nearby agents & liquidity')}</span>
            </Card>
          </Link>
          <div className="opacity-50">
            <Card className="bg-white shadow-[0_4px_20px_rgb(0,0,0,0.04)] border-none rounded-2xl p-4 flex flex-col items-center justify-center gap-2 h-full">
              <div className="w-10 h-10 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 mb-1">
                <Icon name="help-circle" size={20} />
              </div>
              <span className="font-semibold text-slate-600">{L('সাহায্য', 'Support')}</span>
            </Card>
          </div>
        </div>
      </div>

      <div className="px-4 mt-4 animate-slide-up" style={{ animationDelay: "300ms" }}>
        {home.lesson && <LessonCard lesson={home.lesson} onDone={() => reload()} />}
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
    <Card className="border-none bg-white shadow-[0_8px_30px_rgb(0,0,0,0.06)] rounded-2xl">
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
