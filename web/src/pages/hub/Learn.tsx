import { api } from '../../api/client'
import { useShell } from '../../components/AppShell'
import { ErrorNote, Spinner } from '../../components/ui'
import { useLang } from '../../i18n'
import { useApi } from '../../lib/useApi'
import { LessonCard } from './Overview'

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
