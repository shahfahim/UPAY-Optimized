import type { RouteResult } from '../api/types'
import { useLang } from '../i18n'
import { Icon } from './Icon'

export function RouteWidget({ result, destinationName }: { result: RouteResult; destinationName?: string }) {
  const { L } = useLang()
  
  // Find the cheapest/best route and the fallback (cashout) route
  const bestHabit = result.habits?.[0]
  const npsbRoute = result.routes.find((r) => r.nodes.includes('npsb'))
  const agentRoute = result.routes.find((r) => r.nodes.includes('agent'))

  const hasNpsb = !!npsbRoute
  const bestFee = bestHabit?.best_fee ?? npsbRoute?.fee ?? 15
  const cashOutFee = bestHabit?.current_fee ?? agentRoute?.fee ?? 90
  const annualSave = bestHabit?.annual_saving ?? (cashOutFee - bestFee) * 12

  const destText = destinationName ?? L('অন্য wallet', 'Other wallet')

  return (
    <div className="mt-3 rounded-xl bg-[#1c1c1c] p-4 text-white font-sans overflow-hidden">
      <h3 className="text-sm font-semibold text-white/90 mb-4">{L('সবচেয়ে ভালো পথ', 'Best Route')}</h3>

      {/* Tree Visualization */}
      <div className="relative flex flex-col items-center gap-6 z-10 my-6 text-sm">
        {/* SVG Lines - Absolute positioned behind the nodes */}
        <svg className="absolute inset-0 w-full h-full -z-10 pointer-events-none" style={{ minHeight: '200px' }}>
          {/* Default gray dashed lines */}
          <line x1="50%" y1="15%" x2="50%" y2="30%" stroke="#444" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="50%" y1="40%" x2="25%" y2="60%" stroke="#444" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="50%" y1="40%" x2="50%" y2="60%" stroke="#444" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="50%" y1="40%" x2="75%" y2="60%" stroke="#444" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="25%" y1="70%" x2="50%" y2="90%" stroke="#444" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="50%" y1="70%" x2="50%" y2="90%" stroke="#444" strokeWidth="2" strokeDasharray="4 4" />
          <line x1="75%" y1="70%" x2="50%" y2="90%" stroke="#444" strokeWidth="2" strokeDasharray="4 4" />

          {/* Highlighted Green solid lines */}
          {hasNpsb && (
            <>
              <line x1="50%" y1="15%" x2="50%" y2="30%" stroke="#00A98F" strokeWidth="3" />
              <line x1="50%" y1="40%" x2="25%" y2="60%" stroke="#00A98F" strokeWidth="3" />
              <line x1="25%" y1="70%" x2="50%" y2="90%" stroke="#00A98F" strokeWidth="3" />
            </>
          )}
        </svg>

        {/* Sender */}
        <div className="rounded border border-[#444] bg-[#2a2a2a] px-5 py-1.5 shadow-md">
          {L('আপনি', 'You')}
        </div>

        {/* Source */}
        <div className={`rounded bg-[#1a3831] border border-[#00A98F] px-5 py-1.5 font-medium shadow-md ${hasNpsb ? 'text-[#00A98F]' : 'text-white'}`}>
          upay wallet
        </div>

        {/* Options Row */}
        <div className="flex w-full justify-around px-2">
          <div className={`rounded border px-4 py-1.5 shadow-md ${hasNpsb ? 'bg-[#1a3831] border-[#00A98F] text-[#00A98F] font-bold' : 'bg-[#2a2a2a] border-[#444]'}`}>
            NPSB
          </div>
          <div className="rounded border border-[#444] bg-[#2a2a2a] px-4 py-1.5 shadow-md">
            এজেন্ট
          </div>
          <div className="rounded border border-[#444] bg-[#2a2a2a] px-4 py-1.5 shadow-md">
            ব্যাংক কার্ড
          </div>
        </div>

        {/* Target */}
        <div className={`rounded bg-[#1a3831] border border-[#00A98F] px-5 py-1.5 font-medium shadow-md ${hasNpsb ? 'text-[#00A98F]' : 'text-white'}`}>
          {destText}
        </div>
      </div>

      {/* Fee Comparison */}
      <div className="mt-4 flex gap-3 text-sm">
        <div className="flex-1 rounded-lg bg-[#112a23] p-3 border border-[#1a3831]">
          <div className="text-[#00A98F] font-medium mb-1">NPSB দিয়ে</div>
          <div className="text-[#00A98F] font-bold text-lg">fee ~৳{Math.round(bestFee)}</div>
        </div>
        <div className="flex-1 rounded-lg bg-[#222] p-3 border border-[#333]">
          <div className="text-[#aaa] font-medium mb-1">Cash-out করে</div>
          <div className="text-white font-bold text-lg">fee ~৳{Math.round(cashOutFee)}</div>
        </div>
      </div>

      {/* Savings highlight */}
      {annualSave > 0 && (
        <div className="mt-4 flex items-center gap-2 text-[13px] text-[#e0e0e0]">
          <span className="text-[#ffb800] text-lg leading-none">✨</span>
          <span>{L(`প্রতি মাসে এভাবে পাঠালে বছরে ~৳${Math.round(annualSave)} বাঁচবে`, `Sending this way saves ~৳${Math.round(annualSave)}/year`)}</span>
        </div>
      )}
    </div>
  )
}
