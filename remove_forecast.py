import re

with open('web/src/pages/hub/Calendar.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update cellTone to ignore risk colors for predicted days
old_cellTone = """  const cellTone = (d: CalendarDay) => {
    if (d.predicted) {
      return d.risk === 'red' ? 'bg-bad-bg text-bad' : d.risk === 'amber' ? 'bg-warn-bg text-warn' : d.risk === 'green' ? 'bg-ok-bg text-ok' : 'bg-white text-muted'
    }
    const a = d.out_total / maxOut
    return a > 0.6 ? 'bg-upay-blue/35' : a > 0.3 ? 'bg-upay-blue/20' : a > 0 ? 'bg-upay-blue/8' : 'bg-white'
  }"""
new_cellTone = """  const cellTone = (d: CalendarDay) => {
    if (d.predicted) {
      return 'bg-white text-slate-400 opacity-50'
    }
    const a = d.out_total / maxOut
    return a > 0.6 ? 'bg-upay-blue/35' : a > 0.3 ? 'bg-upay-blue/20' : a > 0 ? 'bg-upay-blue/8' : 'bg-white'
  }"""
code = code.replace(old_cellTone, new_cellTone)

# 2. Remove "Risk (forecast)" from legend
old_legend = """            <span><span className="mr-1 inline-block size-3 rounded bg-upay-blue/30 align-middle" />{L('খরচ (অতীত)', 'Spending (past)')}</span>
            <span><span className="mr-1 inline-block size-3 rounded bg-bad-bg align-middle" />{L('ঝুঁকি (পূর্বাভাস)', 'Risk (forecast)')}</span>
            <span><span className="mr-1 inline-block size-1.5 rounded-full bg-upay-yellow-dark align-middle" />{L('ভাড়া/বিল', 'Rent/bills')}</span>"""
new_legend = """            <span><span className="mr-1 inline-block size-3 rounded bg-upay-blue/30 align-middle" />{L('খরচ (অতীত)', 'Spending (past)')}</span>
            <span><span className="mr-1 inline-block size-1.5 rounded-full bg-upay-yellow-dark align-middle" />{L('ভাড়া/বিল', 'Rent/bills')}</span>"""
code = code.replace(old_legend, new_legend)

# 3. Update the modal to hide forecast data
old_modal = """        {pick && (
          <div className="space-y-2 text-sm">
            <p className="text-muted">{pick.predicted ? L('পূর্বাভাস (AI)', 'Forecast (AI)') : L('যা হয়েছে', 'What happened')}</p>
            <p>{L('আয়', 'In')}: <b>{taka(pick.in_total)}</b> · {L('খরচ', 'Out')}: <b>{taka(pick.out_total)}</b></p>
            {pick.events.length > 0 && <p>{pick.events.join(' · ')}</p>}
            {pick.risk && pick.risk !== 'green' && (
              <p className={pick.risk === 'red' ? 'text-bad' : 'text-warn'}>
                {pick.risk === 'red' ? L('এই দিনে ব্যালেন্স ৳২০০-এর নিচে থাকার কথা', 'Balance expected below ৳200') : L('এই দিনে টাকা কম পড়ার ঝুঁকি আছে', 'Some risk of running short')}
              </p>
            )}
          </div>
        )}"""
new_modal = """        {pick && (
          <div className="space-y-2 text-sm">
            {pick.predicted ? (
               <div className="text-center py-4">
                 <p className="text-muted italic">{L('ভবিষ্যতের কোনো পূর্বাভাস নেই', 'No forecast available')}</p>
               </div>
            ) : (
               <>
                 <p className="text-muted">{L('যা হয়েছে', 'What happened')}</p>
                 <p>{L('আয়', 'In')}: <b>{taka(pick.in_total)}</b> · {L('খরচ', 'Out')}: <b>{taka(pick.out_total)}</b></p>
                 {pick.events.length > 0 && <p>{pick.events.join(' · ')}</p>}
               </>
            )}
          </div>
        )}"""
code = code.replace(old_modal, new_modal)

with open('web/src/pages/hub/Calendar.tsx', 'w', encoding='utf-8') as f:
    f.write(code)
print("Calendar updated to remove forecast logic.")
