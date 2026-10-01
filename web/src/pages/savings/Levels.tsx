import { Link } from 'react-router-dom'
import { api } from '../../api/client'
import { useShell } from '../../components/AppShell'
import { Icon } from '../../components/Icon'
import { LevelPath } from '../../components/LevelPath'
import { AiBadge, Card, ErrorNote, ProgressBar, Spinner } from '../../components/ui'
import { useLang } from '../../i18n'
import { useApi } from '../../lib/useApi'
import { PageTitle } from '../common'

export default function Levels() {
  const { L, num } = useLang()
  const { uid } = useShell()
  const { data: s, error, loading, reload } = useApi(() => api.levels(uid), [uid])

  return (
    <div className="pb-6">
      <PageTitle bn="সঞ্চয় লেভেল" en="Savings level" />
      {loading && !s && <Spinner />}
      {error && <ErrorNote message={error} onRetry={reload} />}
      {s && (
        <div className="space-y-3 px-3">
          <div className="rounded-2xl bg-upay-blue p-4 text-white">
            <div className="flex items-center gap-2">
              <span className="flex size-12 items-center justify-center rounded-full bg-upay-yellow text-xl font-bold text-upay-blue">{num(s.level)}</span>
              <div>
                <p className="text-lg font-bold">{L(`লেভেল ${num(s.level)} · ${s.name_bn}`, `Level ${s.level} · ${s.name_bn}`)}</p>
                <p className="text-sm text-white/80">{L(`টানা সঞ্চয় ${num(s.streak_days)} দিন`, `${s.streak_days}-day saving streak`)}</p>
              </div>
            </div>
            {s.next_level !== null && (
              <div className="mt-3">
                <div className="mb-1 flex justify-between text-xs text-white/80">
                  <span>{L(`লেভেল ${num(s.next_level)}-এর পথে`, `Towards level ${s.next_level}`)}</span>
                  <span>{num(Math.round(s.progress * 100))}%</span>
                </div>
                <div className="rounded-full bg-white/20"><ProgressBar value={s.progress} tone="ok" /></div>
              </div>
            )}
            {s.projection_days !== null && s.next_level !== null && (
              <p className="mt-2 flex items-center gap-1.5 text-sm"><AiBadge className="!bg-white !text-upay-blue" />
                {L(`এভাবে চললে প্রায় ${num(s.projection_days)} দিনে লেভেল ${num(s.next_level)}`,
                  `At this pace, level ${s.next_level} in about ${s.projection_days} days`)}
              </p>
            )}
          </div>

          {s.dps_ready && (
            <Link to="/app/savings/dps" className="flex items-center gap-3 rounded-2xl bg-ok-bg p-4 text-ok">
              <Icon name="check" />
              <span className="flex-1 font-semibold">{L('তুমি DPS-এর জন্য প্রস্তুত — Smart DPS দেখো', 'DPS-ready — see Smart DPS')}</span>
              <Icon name="chevron" size={16} />
            </Link>
          )}

          <Card>
            <p className="mb-3 font-semibold">{L('তোমার পথ', 'Your path')}</p>
            <LevelPath status={s} />
          </Card>

          <Card>
            <p className="mb-2 font-semibold">{L('এই লেভেলে যা পাচ্ছ', 'What this level gives you')}</p>
            <ul className="space-y-1.5 text-sm">
              {s.unlocks_bn.map((u) => (
                <li key={u} className="flex gap-2"><Icon name="check" size={16} className="mt-0.5 text-ok" />{u}</li>
              ))}
            </ul>
          </Card>

          <Card className="text-sm text-ink/80">
            <p className="mb-1 font-semibold">{L('কীভাবে লেভেল বাড়ে', 'How levels work')}</p>
            <ul className="list-disc space-y-1 pl-5">
              <li>{L('যে দিন পকেটে বা পয়সা-সঞ্চয়ে কিছু টাকা রাখো, সেদিন টানা সঞ্চয় চলতে থাকে — মাঝে ৩ দিন বাদ পড়লেও চলে, তবে পকেট পুরো খালি করলে আবার শুরু হয়।', 'Each day you put something into a pocket or paisa saving keeps the streak going — up to 3 missed days are fine, but emptying a pocket restarts it.')}</li>
              <li>{L('৩০ দিন টানা হলে লেভেল ১ — DPS-এর জন্য প্রস্তুত।', '30 days in a row: level 1 — DPS-ready.')}</li>
              <li>{L('৩ মাস টাকা কম না পড়লে আর ১৫ দিনের জরুরি তহবিল হলে লেভেল ২।', '3 shortfall-free months and a 15-day emergency fund: level 2.')}</li>
              <li>{L('DPS-এর ৩টা কিস্তি সময়মতো দিলে লেভেল ৩।', '3 on-time DPS installments: level 3.')}</li>
            </ul>
            <p className="mt-3 flex items-center gap-2 rounded-xl bg-surface p-2 text-xs font-semibold text-ink">
              <Icon name="info" size={16} className="text-upay-blue" />{s.note_bn}
            </p>
          </Card>
        </div>
      )}
    </div>
  )
}
