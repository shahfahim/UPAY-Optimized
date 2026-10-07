# How to test the Phase 2 changes

Do the automated checks first, then the manual ones. Use demo user Rina: mobile `01700000001`, PIN `123456`. Start the backend with `HISHAB_DEMO_MODE=1`.

## A. Automated (one command each)

| # | What | Command | Pass if |
|---|---|---|---|
| A1 | Backend tests + coverage | `cd backend && .venv/Scripts/python -m pytest -q --cov=hishab` | All pass, total ≥ 85% |
| A2 | Backend lint | `cd backend && .venv/Scripts/python -m ruff check hishab tests` | "All checks passed" |
| A3 | Web types (strict) | `cd web && npm run typecheck` | No errors |
| A4 | Web unit tests | `cd web && npm test` | 10/10 pass |
| A5 | Web lint + build | `cd web && npm run lint && npm run build` | Both exit 0 |
| A6 | CI on GitHub | Open the repo's **Actions** tab after a push | "CI" run is green; Pages/HF deploy start only after it |
| A7 | Intent metrics are honest | Open `backend/artifacts/intent_metrics.json` | `method` mentions GroupKFold; accuracy ≈ 0.60 |

## B. Core shortfall flow (phone or browser)

| # | Steps | Expected |
|---|---|---|
| B1 | Log in as Rina, tap **হিসাব** in the bottom bar | Opens on **পূর্বাভাস**; risk card says when and how much she may run short |
| B2 | Tap **কেন?** | 2–3 Bangla reasons appear |
| B3 | Tap **কী হবে দেখো** on an action | A green dashed "if you follow it" line appears on the chart |
| B4 | Tap **রাজি** | Card disappears, "Added to your plan" toast |
| B5 | Open the **ক্যালেন্ডার** tab | Future days are coloured red/amber where risk is high |
| B6 | Look at the bottom bar and header | "N দিন" badge on হিসাব; red shortfall message in the header |
| B7 | Home screen tiles | First shield tile says **ডিপিএস**; **এজেন্ট খুঁজুন** and **এনপিএসবি** have no AI badge |
| B8 | Open এজেন্ট খুঁজুন | Amber "ডেমো" banner; label says "ক্যাশ থাকার নমুনা মান (ডেমো)"; same list every reload |

## C. Chat

| # | Ask | Expected |
|---|---|---|
| C1 | `500tk bkash e pathabo` | Route answer, **no** "টাকার পরিমাণ সঠিক নয়" |
| C2 | `aaj koto kharoch korte parbo` | Safe-to-spend answer with a ৳ amount |
| C3 | `asdkjh qwe zzz` | Polite "I don't know" reply, no tools used |
| C4 | `কাছাকাছি এজেন্ট` | Answer says it is demo data |

## D. Security and accounts

| # | Steps | Expected |
|---|---|---|
| D1 | Register a new number; enter the on-screen demo OTP; set name and PIN | Lands on home |
| D2 | Register again, type a wrong OTP 3 times, then the right one | Still rejected (OTP used up) |
| D3 | Log out from **More → লগ আউট**, then reuse the old token (browser devtools or the test) | 401 |
| D4 | Enter a wrong PIN 5 times for one number | 6th try, even with the right PIN, says to wait 15 minutes |
| D5 | Start the backend **without** `HISHAB_DEMO_MODE=1` and open `/api/users` | 404; demo PIN `123456` no longer logs in |
| D6 | `curl -I http://localhost:8000/api/health` | Shows `X-Frame-Options: DENY` and a `Content-Security-Policy` header |
| D7 | `curl -X POST http://localhost:8000/api/upay/ai/predict -H "Content-Type: application/json" -d "{\"query\":\"balance\"}"` | 401 without a login token |

## E. Impact page (http://localhost:5173/impact)

| # | Check | Expected |
|---|---|---|
| E1 | Bandit chart | Baseline is called "Best fixed card (train logs)"; bandit is **not** above it |
| E2 | Fairness section | Flags name the lowest group (daily wage); groups with < 30 cases are listed as "not judged"; CIs in brackets |
| E3 | All impact numbers | Marked as simulated |
