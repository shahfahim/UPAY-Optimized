import { Area, ComposedChart, Line, ReferenceDot, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { Forecast } from '../api/types'
import { useLang } from '../i18n'

/** 30-day balance forecast: P10–P90 band, P50 line, ৳200 threshold, shortfall marker, optional what-if line. */
export function ForecastChart({ forecast, whatIf }: { forecast: Forecast; whatIf?: Forecast | null }) {
  const { L, taka, date, num } = useLang()
  const data = forecast.dates.map((d, i) => ({
    d,
    label: date(d),
    band: [Math.round(forecast.p10[i]), Math.round(forecast.p90[i])] as [number, number],
    p50: Math.round(forecast.p50[i]),
    whatIf: whatIf ? Math.round(whatIf.p50[i]) : undefined,
  }))
  const sf = forecast.shortfall_date
  const sfPoint = sf ? data.find((x) => x.d === sf) : undefined
  return (
    <div className="h-52 w-full" role="img"
      aria-label={L('সামনের ৩০ দিনের ব্যালেন্সের পূর্বাভাস', 'Balance forecast for the next 30 days')}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
          <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#6b7280' }} interval={6} tickLine={false} axisLine={false} />
          <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} tickLine={false} axisLine={false} width={48}
            tickFormatter={(v: number) => num(Math.round(v / 1000)) + L('হা', 'k')} />
          <Tooltip
            formatter={(value, name) => {
              const v = Array.isArray(value) ? `${taka(Number(value[0]))} – ${taka(Number(value[1]))}` : taka(Number(value))
              const label = name === 'band' ? L('সম্ভাব্য সীমা', 'Likely range') : name === 'whatIf' ? L('পরামর্শ মানলে', 'If you follow it') : L('সম্ভাব্য ব্যালেন্স', 'Expected balance')
              return [v, label]
            }}
            labelStyle={{ fontSize: 12 }} contentStyle={{ borderRadius: 12, fontSize: 12 }} />
          <Area dataKey="band" stroke="none" fill="#0b4ea2" fillOpacity={0.12} isAnimationActive={false} />
          <ReferenceLine y={200} stroke="#c81e1e" strokeDasharray="4 4" strokeWidth={1} />
          <ReferenceLine y={0} stroke="#9ca3af" strokeWidth={0.5} />
          <Line dataKey="p50" stroke="#0b4ea2" strokeWidth={2.5} dot={false} isAnimationActive={false} />
          {whatIf && <Line dataKey="whatIf" stroke="#15803d" strokeWidth={2.5} strokeDasharray="6 4" dot={false} isAnimationActive={false} />}
          {sfPoint && <ReferenceDot x={sfPoint.label} y={sfPoint.p50} r={5} fill="#c81e1e" stroke="#fff" strokeWidth={2} />}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
