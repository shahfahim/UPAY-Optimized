import re

path = 'web/src/pages/Home.tsx'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# Update BANNERS array
old_banners = """const BANNERS = [
  { bn: 'কতদিন চলবে আপনার টাকা? হিসাব খুলুন', en: 'How long will your money last? Open Hishab', to: '/app/hishab' },
  { bn: 'অন্য wallet-এ পাঠাও NPSB দিয়ে — কম খরচে', en: 'Send to other wallets via NPSB — for less', to: '/app/npsb' },
]"""

new_banners = """const BANNERS = [
  { img: '/assets/banners/offer1.png', to: '/app/npsb' },
  { img: '/assets/banners/offer2.png', to: '/app/npsb' },
  { img: '/assets/banners/offer3.png', to: '/app/npsb' },
]"""

if old_banners in code:
    code = code.replace(old_banners, new_banners)
else:
    # try a regex if encoding or exact match fails
    code = re.sub(r'const BANNERS = \[.*?\]', new_banners, code, flags=re.DOTALL)

# Update Banner Rendering Section
old_render = """<section className="mx-3">
        <button onClick={() => navigate(BANNERS[b].to)}
          className="flex h-24 w-full items-center justify-between rounded-2xl bg-upay-blue px-5 text-left text-white">
          <span key={b} className="animate-rise text-[15px] font-semibold leading-snug">{L(BANNERS[b].bn, BANNERS[b].en)}</span>
          <Icon name="chevron" />
        </button>
        <div className="mt-2 flex justify-center gap-1.5">
          {BANNERS.map((_, k) => <span key={k} className={`h-1.5 rounded-full ${k === b ? 'w-5 bg-upay-blue' : 'w-1.5 bg-line'}`} />)}
        </div>
      </section>"""

new_render = """<section className="mx-3">
        <button onClick={() => navigate(BANNERS[b].to)}
          className="relative flex h-[120px] w-full items-center justify-center rounded-2xl bg-slate-100 overflow-hidden shadow-[0_4px_15px_-3px_rgba(0,0,0,0.1)] active:scale-[0.98] transition-all">
          <img key={b} src={BANNERS[b].img} className="animate-fade-in h-full w-full object-cover" alt="Offer Banner" />
        </button>
        <div className="mt-3 flex justify-center gap-1.5">
          {BANNERS.map((_, k) => <span key={k} className={`h-1.5 rounded-full transition-all duration-300 ${k === b ? 'w-5 bg-upay-blue' : 'w-1.5 bg-line'}`} />)}
        </div>
      </section>"""

if old_render in code:
    code = code.replace(old_render, new_render)
else:
    # use regex
    code = re.sub(r'<section className="mx-3">\s*<button onClick=\{\(\) => navigate\(BANNERS\[b\]\.to\)\}.*?</section>', new_render, code, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated Home.tsx with image banners.")
