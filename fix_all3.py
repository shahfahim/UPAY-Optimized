import re

with open('web/src/components/AppShell.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's completely wipe everything from "item('/app/hishab'" until "      </nav>"
start = code.find("{item('/app/hishab'")
end = code.find("</nav>", start)

if start != -1 and end != -1:
    good_block = """{item('/app/hishab', 'spark', L('হিসাব', 'Hishab'), (
          <>
            {badge ? (
              <span className={`absolute right-3 top-1 flex items-center gap-0.5 rounded-full px-1 text-[9px] font-bold text-white ${dot}`}>
                {badge.days_left !== null ? L(`${num(badge.days_left)} দিন`, `${badge.days_left}d`) : '•'}
              </span>
            ) : null}
            <span className="absolute right-1 top-0 text-[10px] font-extrabold text-upay-blue italic drop-shadow-sm">AI</span>
          </>
        ))}
      """
    code = code[:start] + good_block + code[end:]

with open('web/src/components/AppShell.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed syntax errors properly!")
