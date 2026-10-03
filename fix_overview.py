code = '''import { Link } from 'react-router-dom'
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

  if (loading && !home) return <Spinner label={L('????? ??? ?????…', 'Working it out…')} />
  if (error) return <ErrorNote message={error} onRetry={reload} />
  if (!home) return null

  const monthlyIncome = home.forecast?.monthly_income ?? 0
  const monthlyExpense = home.forecast?.monthly_expense ?? 0
  
  // Safe parsing for balance
  const currentBalance = typeof home.balance === 'number' ? home.balance : 0

  const chartData = [
    {
      name: L('???', 'Income'),
      value: monthlyIncome > 0 ? monthlyIncome : 12000,
      fill: '#22c55e'
    },
    {
      name: L('???', 'Expense'),
      value: monthlyExpense > 0 ? monthlyExpense : 4500,
      fill: '#f87171'
    }
  ]

  return (
    <div className="min-h-screen bg-slate-50 pb-20">
      {/* Simple Top Section */}
      <div className="bg-upay-blue px-4 pt-6 pb-12 rounded-b-3xl">
        <div className="flex flex-col items-center justify-center mt-2">
          <p className="text-blue-100 text-sm font-medium mb-1">{L('??????? ?????????', 'Current Balance')}</p>
          <h2 className="text-white text-4xl font-bold tracking-tight">
            ?{currentBalance.toLocaleString('bn-BD')}
          </h2>
        </div>
      </div>

      {/* Simple Bar Chart Card */}
      <div className="px-4 -mt-6">
        <Card className="bg-white shadow-sm border border-slate-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-800">{L('?? ????? ?????', 'This Month')}</h3>
            <AiBadge />
          </div>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }} barSize={50}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b', fontWeight: 600 }} />
                <YAxis tickFormatter={(v) => \?\k\} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <Tooltip cursor={{ fill: 'transparent' }} formatter={(val: number) => [\?\\, '??????']} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Grid Buttons */}
      <div className="px-4 mt-4 grid grid-cols-3 gap-3">
        <Link to="/app/hishab/ask" className="flex flex-col items-center justify-center bg-white rounded-xl p-3 shadow-sm border border-slate-100">
          <div className="h-10 w-10 rounded-full bg-blue-50 flex items-center justify-center mb-2">
            <Icon name="spark" size={20} className="text-upay-blue" />
          </div>
          <span className="text-xs font-bold text-slate-700 text-center">Hishab AI</span>
        </Link>
        <Link to="/app/savings" className="flex flex-col items-center justify-center bg-white rounded-xl p-3 shadow-sm border border-slate-100">
          <div className="h-10 w-10 rounded-full bg-green-50 flex items-center justify-center mb-2">
            <Icon name="chart" size={20} className="text-green-600" />
          </div>
          <span className="text-xs font-bold text-slate-700 text-center">Smart DPS</span>
        </Link>
        <Link to="/app/hishab/ask" className="flex flex-col items-center justify-center bg-white rounded-xl p-3 shadow-sm border border-slate-100">
          <div className="h-10 w-10 rounded-full bg-yellow-100 flex items-center justify-center mb-2">
            <Icon name="mic" size={20} className="text-yellow-700" />
          </div>
          <span className="text-xs font-bold text-slate-700 text-center">Ask Hishab</span>
        </Link>
      </div>

      <div className="px-4 mt-4">
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
    <Card className="border-slate-200 shadow-sm bg-white">
      <div className="mb-1 flex items-center gap-2">
        <Icon name="book" size={18} className="text-slate-500" />
        <AiBadge />
        <span className="text-xs text-slate-500">{L('????? ???? ??? ???', 'A short lesson for you')}</span>
      </div>
      <p className="font-semibold text-slate-800">{lesson.title_bn}</p>
      <p className="mt-1 text-sm leading-relaxed text-slate-600">{lesson.body_bn}</p>
      <div className="mt-3 flex gap-2">
        <Button variant="outline" className="flex-1 !min-h-9 text-sm text-slate-700 border-slate-300" onClick={() => void respond(true)}>{L('??????', 'Got it')}</Button>
        <Button variant="ghost" className="flex-1 !min-h-9 text-sm text-slate-500" onClick={() => void respond(false)}>{L('???? ????? ??', 'Not useful')}</Button>
      </div>
    </Card>
  )
}
'''
with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print('Overview.tsx reverted and simplified')
