import re

with open('web/src/pages/savings/Emergency.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

loan_card = """
        <Card className="border-upay-blue bg-blue-50/50 mt-4">
          <div className="flex items-start gap-3">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-upay-blue/20 text-upay-blue">
              <Icon name="shield" size={20} />
            </span>
            <div>
              <p className="font-bold text-slate-800">{L('লোন পাওয়ার যোগ্যতা', 'Loan Eligibility')}</p>
              <p className="mt-1 text-sm text-slate-600">
                {L('আপনার নিয়মিত লেনদেন ও সঞ্চয়ের উপর ভিত্তি করে আপনি ', 'Based on your regular transactions and savings, you are eligible for up to ')}
                <span className="font-bold text-upay-blue">৳১০,০০০</span>
                {L(' পর্যন্ত ইমার্জেন্সি লোন পাওয়ার যোগ্য। (ডেমো)', ' emergency loan. (Demo)')}
              </p>
            </div>
          </div>
        </Card>
"""

# Insert it right after the first <Card> block in Emergency.tsx
code = re.sub(
    r'(</Card>)\s*(<Card className="text-sm">|<Card>|\{msg)', 
    r'\1\n' + loan_card + r'\n        \2', 
    code, 
    count=1
)

with open('web/src/pages/savings/Emergency.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Emergency loan card added!")
