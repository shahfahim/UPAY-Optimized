import re

with open('web/src/pages/savings/Pockets.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add trash icon to existing pockets
trash_button = """                  <Button variant="ghost" className="!min-h-9 !px-2 text-sm text-slate-400 hover:text-red-500"
                    onClick={() => setMsg(L('পকেট ডিলিট করা হয়েছে (ডেমো)', 'Pocket deleted (Demo)'))} aria-label="Delete Pocket">
                    <Icon name="trash" size={18} />
                  </Button>
"""
# Find where the other buttons are rendered and inject the trash button
code = code.replace(
    "<Button variant=\"ghost\" className=\"!min-h-9 !px-3 text-sm\" disabled={p.balance <= 0}\n                    onClick={() => setMove({ pocket: p.name, name: p.name_bn, dir: 'out', max: p.balance })}>{L('তুলুন', 'Take out')}</Button>",
    "<Button variant=\"ghost\" className=\"!min-h-9 !px-3 text-sm\" disabled={p.balance <= 0}\n                    onClick={() => setMove({ pocket: p.name, name: p.name_bn, dir: 'out', max: p.balance })}>{L('তুলুন', 'Take out')}</Button>\n" + trash_button
)

# 2. Add an "Add Pocket" button at the end of the pockets list
add_pocket_btn = """        <Button variant="outline" className="w-full border-dashed border-2 border-slate-300 text-slate-500 hover:bg-slate-50 mb-4" onClick={() => setMsg(L('নতুন পকেট তৈরির ফিচার শীঘ্রই আসছে (ডেমো)', 'New pocket feature coming soon (Demo)'))}>
          + {L('নতুন পকেট যোগ করুন', 'Add a new pocket')}
        </Button>
"""

code = code.replace(
    '        <Card className="border-upay-yellow bg-upay-yellow/10">',
    add_pocket_btn + '        <Card className="border-upay-yellow bg-upay-yellow/10">'
)

with open('web/src/pages/savings/Pockets.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Pockets updated!")
