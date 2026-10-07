import { api } from '../../api/client'
import type { Lesson } from '../../api/types'
import { useShell } from '../../components/AppShell'
import { Icon } from '../../components/Icon'
import { AiBadge, Button, Card, ErrorNote, Spinner } from '../../components/ui'
import { useLang } from '../../i18n'
import { useApi } from '../../lib/useApi'

export function LessonCard({ lesson, onDone }: { lesson: Lesson; onDone: () => void }) {
  const { L } = useLang()
  const { uid } = useShell()
  const respond = async (ok: boolean) => {
    await api.lessonRespond(uid, lesson.id, ok).catch(() => undefined)
    onDone()
  }
  return (
    <Card className="border-upay-blue/30">
      <div className="mb-1 flex items-center gap-2"><Icon name="book" size={18} className="text-upay-blue" /><AiBadge />
        <span className="text-xs text-muted">{L('তোমার জন্য ছোট পাঠ', 'A short lesson for you')}</span></div>
      <p className="font-semibold">{lesson.title_bn}</p>
      <p className="mt-1 text-sm leading-relaxed text-ink/80">{lesson.body_bn}</p>
      <div className="mt-3 flex gap-2">
        <Button variant="outline" className="flex-1 !min-h-9 text-sm" onClick={() => void respond(true)}>{L('বুঝেছি', 'Got it')}</Button>
        <Button variant="ghost" className="flex-1 !min-h-9 text-sm" onClick={() => void respond(false)}>{L('কাজে লাগবে না', 'Not useful')}</Button>
      </div>
    </Card>
  )
}

export default function Learn() {
  const { L } = useLang()
  const { uid } = useShell()
  const { data, error, loading, reload, setData } = useApi(() => api.lessons(uid), [uid])
  return (
    <div className="space-y-3 px-3 pb-6">
      <p className="px-1 text-sm text-muted">{L('আপনার নিজের লেনদেন দেখে বাছাই করা ছোট পাঠ।', 'Short lessons picked from your own activity.')}</p>
      {loading && <Spinner />}
      {error && <ErrorNote message={error} onRetry={reload} />}
      {data?.length === 0 && <p className="rounded-2xl bg-white p-6 text-center text-sm text-muted">{L('এখন নতুন কোনো পাঠ নেই।', 'No new lessons right now.')}</p>}
      {data?.map((l) => <LessonCard key={l.id} lesson={l} onDone={() => setData(prev => prev?.filter((x) => x.id !== l.id) || [])} />)}
    </div>
  )
}
