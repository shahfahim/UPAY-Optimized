import re

with open('web/src/pages/Home.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Make sure useState is imported
if 'useState' not in code:
    code = code.replace("import { useEffect } from 'react'", "import { useEffect, useState } from 'react'")
else:
    # it might be imported, let's just make sure
    pass

# Inside Home component:
code = code.replace("export default function Home() {", "export default function Home() {\n  const [expanded, setExpanded] = useState(false)")

old_section = """      <section className="mx-3 grid grid-cols-4 gap-y-4 rounded-2xl bg-white px-1 py-4">
        {TILES.map((t) => (
          <button key={t.bn} onClick={() => (t.to ? navigate(t.to) : demo(L(t.bn, t.en)))}
            className="relative flex flex-col items-center gap-1.5 px-1 text-center">
            <span className="flex size-12 items-center justify-center rounded-2xl bg-upay-blue/8 text-upay-blue">
              <Icon name={t.icon} size={26} />
            </span>
            <span className="text-[12px] font-semibold leading-tight">{L(t.bn, t.en)}</span>
            {t.hishab && <span className="absolute right-2 top-0"><AiBadge className="!px-1 !text-[9px]" /></span>}
          </button>
        ))}
      </section>"""

new_section = """      <section className="relative mx-3 rounded-2xl bg-white px-1 py-4">
        <div className={`grid grid-cols-4 gap-y-4 ${expanded ? '' : 'overflow-hidden max-h-[170px]'}`}>
          {TILES.map((t, i) => {
            const isHidden = !expanded && i >= 8;
            return (
              <button key={t.bn} onClick={() => (t.to ? navigate(t.to) : demo(L(t.bn, t.en)))}
                className={`relative flex flex-col items-center gap-1.5 px-1 text-center transition-all duration-300 ${isHidden ? 'opacity-20 blur-[2px] pointer-events-none' : ''}`}>
                <span className="flex size-12 items-center justify-center rounded-2xl bg-upay-blue/8 text-upay-blue">
                  <Icon name={t.icon} size={26} />
                </span>
                <span className="text-[12px] font-semibold leading-tight">{L(t.bn, t.en)}</span>
                {t.hishab && <span className="absolute right-2 top-0"><AiBadge className="!px-1 !text-[9px]" /></span>}
              </button>
            )
          })}
        </div>
        
        {!expanded && (
          <div className="absolute inset-x-0 bottom-0 flex justify-center pb-0 bg-gradient-to-t from-white via-white/80 to-transparent pt-10 pointer-events-none">
            <button onClick={() => setExpanded(true)} className="flex items-center gap-1 rounded-full bg-white px-4 py-1.5 text-xs font-semibold text-upay-blue shadow-[0_2px_10px_rgba(0,0,0,0.1)] border border-slate-100 pointer-events-auto transform translate-y-2">
              {L('আরো দেখুন', 'See More')} <Icon name="chevron" size={14} className="rotate-90 mt-0.5" strokeWidth={3} />
            </button>
          </div>
        )}
        {expanded && (
          <div className="flex justify-center mt-3 border-t border-slate-50 pt-2">
            <button onClick={() => setExpanded(false)} className="flex items-center gap-1 rounded-full bg-transparent px-4 py-1 text-xs font-semibold text-upay-blue">
              {L('গুটিয়ে নিন', 'See Less')} <Icon name="chevron" size={14} className="-rotate-90 mt-0.5" strokeWidth={3} />
            </button>
          </div>
        )}
      </section>"""

code = code.replace(old_section, new_section)

with open('web/src/pages/Home.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Home.tsx updated with See More logic!")
