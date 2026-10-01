import { useLang } from '../../i18n'
import Flow from './Flow'

export default function CashOut() {
  const { L } = useLang()
  const contacts = [{ id: 'AGENT', name: L('এজেন্ট', 'Agent') }]
  return <Flow cfg={{ type: 'cash_out', titleBn: 'ক্যাশ আউট', titleEn: 'Cash out', contacts, cashNudge: true }} />
}
