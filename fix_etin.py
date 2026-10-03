import re

with open('web/src/pages/savings/SavingsHome.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the text inside the e-TIN Sheet with a cool demo statement
old_sheet = """      <Sheet open={etin} onClose={() => setEtin(false)} title={L('ই-টিন ও সঞ্চয় বিবরণী', 'e-TIN & savings statement')}>
        <p className="text-sm text-muted">
          {L('এই অংশ upay-এর বর্তমান সেবার মতোই থাকবে — ডেমোতে চালু নেই।',
            'This stays as in the current upay app — not active in the demo.')}
        </p>
      </Sheet>"""

new_sheet = """      <Sheet open={etin} onClose={() => setEtin(false)} title={L('ই-টিন ও সঞ্চয় বিবরণী', 'e-TIN & savings statement')}>
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
          <p className="text-center font-bold text-slate-800 text-lg mb-2">উপায় সঞ্চয় বিবরণী (ডেমো)</p>
          <div className="text-sm text-slate-600 space-y-2">
            <div className="flex justify-between border-b pb-1"><span>ই-টিন (e-TIN):</span> <strong>987654321012</strong></div>
            <div className="flex justify-between border-b pb-1"><span>নাম:</span> <strong>রিণা আক্তার</strong></div>
            <div className="flex justify-between border-b pb-1"><span>সময়কাল:</span> <strong>২০২৫ - ২০২৬</strong></div>
            <div className="flex justify-between border-b pb-1"><span>সর্বমোট জমা:</span> <strong>৳ ১২,৪৫০.০০</strong></div>
            <div className="flex justify-between border-b pb-1"><span>উত্তোলন:</span> <strong>৳ ৩,০০০.০০</strong></div>
            <div className="flex justify-between pt-1"><span>বর্তমান ব্যালেন্স:</span> <strong className="text-upay-blue text-base">৳ ৯,৪৫০.০০</strong></div>
          </div>
          <button className="mt-4 w-full bg-upay-blue text-white py-2 rounded-lg font-semibold" onClick={() => setEtin(false)}>ডাউনলোড করুন (PDF)</button>
        </div>
      </Sheet>"""

code = code.replace(old_sheet, new_sheet)

with open('web/src/pages/savings/SavingsHome.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("e-TIN statement demo updated!")
