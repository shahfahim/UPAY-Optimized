import re

with open('web/src/pages/hub/Overview.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add useState to imports
if 'useState' not in code:
    code = code.replace("import { Link } from 'react-router-dom'", "import { useState } from 'react'\nimport { Link } from 'react-router-dom'")

# 2. Add state and logic inside Overview component
state_logic = """
  const [view, setView] = useState<'all' | 'in_out' | 'savings_loan'>('all')
  const [monthOffset, setMonthOffset] = useState('0')

  const monthlyIncomeBase = home.forecast?.monthly_income ?? 12000
  const monthlyExpenseBase = home.forecast?.monthly_expense ?? 4500
  const dpsBase = 2000
  const loanBase = 1500

  // Mock historical data multiplier
  const multiplier = monthOffset === '0' ? 1 : monthOffset === '1' ? 0.85 : 0.92

  const income = monthlyIncomeBase * multiplier
  const expense = monthlyExpenseBase * multiplier
  const dps = dpsBase * multiplier
  const loan = loanBase * multiplier

  const chartData = []
  if (view === 'all' || view === 'in_out') {
    chartData.push({ name: L('আয়', 'Income'), value: income, fill: '#22c55e' })
    chartData.push({ name: L('খরচ', 'Expense'), value: expense, fill: '#f87171' })
  }
  if (view === 'all' || view === 'savings_loan') {
    chartData.push({ name: L('ডিপিএস', 'DPS'), value: dps, fill: '#0ea5e9' })
    chartData.push({ name: L('লোন', 'Loan'), value: loan, fill: '#f59e0b' })
  }
"""

# Replace existing logic
pattern_logic = r"const monthlyIncome = .*?fill: '#f87171'\n    }\n  ]"
code = re.sub(pattern_logic, state_logic.strip(), code, flags=re.DOTALL)

# 3. Update the Card header with Month Selector and View Pills
header_pattern = r'<div className="flex items-center justify-between mb-4">\s*<h3 className="font-bold text-slate-800">.*?</h3>\s*<AiBadge />\s*</div>'
header_replacement = """
          <div className="flex flex-col mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-slate-800">{L('ওভারভিউ', 'Overview')}</h3>
                <AiBadge />
              </div>
              <select 
                value={monthOffset} 
                onChange={e => setMonthOffset(e.target.value)}
                className="bg-transparent text-[13px] font-bold text-slate-700 outline-none cursor-pointer"
              >
                <option value="0">{L('চলতি মাস', 'This Month')}</option>
                <option value="1">{L('গত মাস', 'Last Month')}</option>
                <option value="2">{L('আগস্ট ২০২৬', 'August 2026')}</option>
              </select>
            </div>
            <div className="flex gap-2 overflow-x-auto no-scrollbar mt-3 pb-1">
              <button onClick={() => setView('all')} className={`px-3 py-1.5 rounded-full text-[11px] font-bold whitespace-nowrap transition-colors ${view === 'all' ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600'}`}>{L('সব ওভারভিউ', 'All')}</button>
              <button onClick={() => setView('in_out')} className={`px-3 py-1.5 rounded-full text-[11px] font-bold whitespace-nowrap transition-colors ${view === 'in_out' ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600'}`}>{L('আয়-ব্যয়', 'Income/Expense')}</button>
              <button onClick={() => setView('savings_loan')} className={`px-3 py-1.5 rounded-full text-[11px] font-bold whitespace-nowrap transition-colors ${view === 'savings_loan' ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600'}`}>{L('ডিপিএস ও লোন', 'DPS/Loan')}</button>
            </div>
          </div>
"""
code = re.sub(header_pattern, header_replacement.strip(), code)

# 4. Fix Bar styling (remove background)
bar_pattern = r'<Bar dataKey="value" radius=\[8, 8, 8, 8\] background={{ fill: \'#f8fafc\', radius: \[8, 8, 8, 8\] }} />'
bar_replacement = '<Bar dataKey="value" radius={[6, 6, 0, 0]} />'
code = code.replace(bar_pattern, bar_replacement)

with open('web/src/pages/hub/Overview.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Overview.tsx update applied")
