import { useLang } from '../../i18n'
import Flow from './Flow'

export default function FundTransfer() {
  const { L } = useLang()
  const contacts = [
    { id: 'BANK-OWN', name: L('নিজের ব্যাংক অ্যাকাউন্ট', 'My bank account'), sub: L('ব্যাংক (demo)', 'Bank (demo)'), destination: 'bank_account' },
    { id: 'BANK-FAM', name: L('পরিবারের ব্যাংক অ্যাকাউন্ট', 'Family bank account'), sub: L('ব্যাংক (demo)', 'Bank (demo)'), destination: 'bank_account' },
  ]
  return <Flow cfg={{ type: 'fund_transfer', titleBn: 'ফান্ড ট্রান্সফার', titleEn: 'Fund transfer', contacts, routed: true }} />
}
