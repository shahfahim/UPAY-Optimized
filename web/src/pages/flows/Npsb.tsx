import { useLang } from '../../i18n'
import Flow from './Flow'

export default function Npsb() {
  const { L } = useLang()
  const contacts = [
    { id: 'NPSB-BKASH', name: L('বিকাশ-এ ট্রান্সফার', 'Transfer to bKash'), sub: L('bKash (demo)', 'bKash (demo)'), destination: 'other_mfs_wallet' },
    { id: 'NPSB-NAGAD', name: L('নগদ-এ ট্রান্সফার', 'Transfer to Nagad'), sub: L('Nagad (demo)', 'Nagad (demo)'), destination: 'other_mfs_wallet' },
    { id: 'NPSB-ROCKET', name: L('রকেট-এ ট্রান্সফার', 'Transfer to Rocket'), sub: L('Rocket (demo)', 'Rocket (demo)'), destination: 'other_mfs_wallet' },
    { id: 'NPSB-BANK', name: L('ব্যাংক অ্যাকাউন্টে ট্রান্সফার', 'Transfer to Bank Account'), sub: L('Bank (demo)', 'Bank (demo)'), destination: 'bank_account' },
  ]
  return <Flow cfg={{ type: 'npsb', titleBn: 'এনপিএসবি', titleEn: 'NPSB transfer', contacts, routed: true }} />
}
