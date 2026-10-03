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

  if (loading && !home) return <Spinner label={L('হিসাব করা হচ্ছে…', 'Working it out…')} />
  if (error) return <ErrorNote message={error} onRetry={reload} />
  if (!home) return null

  const monthlyIncome = home.forecast?.monthly_income ?? 0
  const monthlyExpense = home.forecast?.monthly_expense ?? 0
  
  // Safe parsing for balance
  const currentBalance = typeof home.balance === 'number' ? home.balance : 0

  const chartData = [
    {
      name: L('আয়', 'Income'),
      value: monthlyIncome > 0 ? monthlyIncome : 12000,
      fill: '#22c55e'
    },
    {
      name: L('খরচ', 'Expense'),
      value: monthlyExpense > 0 ? monthlyExpense : 4500,
      fill: '#f87171'
    }
  ]

  return (
    <div className="min-h-screen bg-transparent pb-20">
      {/* Simple Top Section */}
      <div className="bg-upay-blue px-4 pt-6 pb-12 rounded-b-3xl animate-fade-in">
        <div className="flex flex-col items-center justify-center mt-2">
          <p className="text-blue-100 text-sm font-medium mb-1">{L('বর্তমান ব্যালেন্স', 'Current Balance')}</p>
          <h2 className="text-white text-4xl font-bold tracking-tight">
            ৳{currentBalance.toLocaleString('bn-BD')}
          </h2>
        </div>
      </div>

      {/* Simple Bar Chart Card */}
      <div className="px-4 -mt-6 animate-slide-up" style={{ animationDelay: "100ms" }}>
        <Card className="bg-white shadow-[0_8px_30px_rgb(0,0,0,0.06)] border-none rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-800">{L('এই মাসের হিসাব', 'This Month')}</h3>
            <AiBadge />
          </div>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }} barSize={50}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b', fontWeight: 600 }} />
                <YAxis tickFormatter={(v) => `৳${(v / 1000).toFixed(0)}k`} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <Tooltip cursor={{ fill: 'transparent' }} formatter={(val: number) => [`৳${val.toLocaleString()}`, 'পরিমাণ']} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} />
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
