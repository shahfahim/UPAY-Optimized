# Hishab (হিসাব) — Project report

AI DEV FEST 2026 · AI Hackathon · Track 03: AI-driven financial management for low-income upay customers.
Repository: https://github.com/shahfahim/UPAY-Optimized · All data is synthetic.

---

## 1. Problem

For **garment workers and other low-income upay users in Bangladesh**, salary leaves the wallet within days (cash-out, remittance home, rent), and they cannot see what is coming. The result is:

- **month-end cash shortfalls**: days with almost nothing left, followed by informal borrowing;
- **avoidable cash-out fees**: money is cashed out at an agent and then sent home or spent in cash;
- **low wallet retention**: the wallet is used as a pass-through, then forgotten.

Today's wallet shows a balance and a history. It does not say *"you will run short around the 29th, and here is what would prevent it"*.

## 2. Proposed idea

**Hishab is an AI cash-flow copilot delivered as a feature + API inside the existing upay app.** It does not replace upay's screens. It adds a status tab, a one-line daily message, advice at the moment of a transfer, and a smarter savings section. Its success measures are:

- shortfall days per user-month,
- cash-out fees paid,
- share of salary still in the wallet on day 10,
- active rate.

The lead persona is **Rina**, a garment worker in Gazipur earning ৳12,500 a month. She sends money to her mother by cash-out and usually runs short in the last week of the month.

## 3. Implemented solution

A working end-to-end prototype in one Docker container:

- **Synthetic data generator**:
  - 2,000 users × 12 months, five personas, seed 42.
  - Injected patterns: paydays, rent, remittance, festival spending, shocks, cash dependency, inactivity.
  - Documented in `docs/synthetic-data.md`.
- **AI engine** (`backend/hishab/engine/`): forecasting, risk, explanations, actions, bandit, savings logic, routes and more (§5).
- **Rules layer** (`backend/hishab/rules/*.yaml`): guardrails, fees, Eid dates, DPS/emergency caps and lessons, kept separate from ML.
- **LLM layer**:
  - Claude (`claude-opus-5-5`) with strict, read-only, user-scoped tools.
  - Every number in an answer comes from a tool.
  - Falls back to grounded templates when the LLM is slow, failing or unsafe.
  - A forbidden-phrase post-filter is applied.
- **FastAPI JSON API** (`/api`, OpenAPI at `/docs`), plus a **React + TypeScript** upay-style shell in Bangla with an English toggle.
- **191 backend tests and frontend unit tests**, CI on every push, and auto-deploy to Hugging Face Spaces.

## 4. Key features

Each feature maps to the upay integration points I1–I9:

1. **হিসাব tab with a live badge** (I1) and a **daily message strip** in the header (I2), e.g. "সাবধান: টাকা আর প্রায় ১১ দিন চলবে".
2. **আজ নিরাপদ খরচ** under the balance (I3). When even ৳0 is risky, it shows a daily limit instead ("বেতন পর্যন্ত দিনে ৳৬৪").
3. **Hishab hub:**
   - 30-day forecast with an uncertainty band.
   - Risk card with "কেন?" reasons.
   - Action cards with a **what-if** redraw of the forecast.
   - Budget (auto/manual), calendar (past + predicted), health coach, lessons, and Ask.
4. **সাম্প্রতিক পেমেন্ট** row (I4) with due-soon chips; the long payment section collapses into one **উপায় পেমেন্ট** icon.
5. **Smart Route + AI category** in send/NPSB/fund-transfer (I5). For example, ৳5,000 to "মা (অন্য wallet)" via NPSB costs ৳25 instead of ৳92.50 via cash-out. Picking any route on the money map charges that route.
6. **Cash-out nudge**, shown at most once, with "তবুও cash-out" (I6). AI category chips in pay/bill/recharge (I7).
7. **সঞ্চয়** (I8):
   - Pockets with goals.
   - **Paisa saving**: only the 0.xx fraction, with an on/off switch; it auto-pauses under risk.
   - Eid planner.
   - **সঞ্চয় লেভেল**: 5/10/15/30 days → Level 1 "DPS-এর জন্য প্রস্তুত", then Levels 2–3. Levels never block any service.
   - **জরুরি টাকা**: own pockets first, then a bank DPS-backed request where the bank decides.
   - **Smart DPS** on upay's existing DPS screen. It says "এখন না" for Rina, and suggests ৳3,000/month for a steady saver.
8. **Notifications** (I9), including re-engagement after inactivity, grounded in the user's own numbers.
9. **Ask Hishab** in Bangla by text or **voice** (browser speech recognition, `bn-BD`), showing which data each answer used.
10. **Impact page** for judges: simulation, models vs baselines, bandit learning curves, fairness and readiness distributions.

## 5. AI approach

| Engine | Method | Why |
|---|---|---|
| E1 Recurring detection | Interval + amount clustering | Paydays and bills drive everything else |
| E2 Forecaster | LightGBM daily in/out-flow models; bootstrap residuals for P10–P90 | Fast, explainable, strong on tabular data |
| E3 Shortfall risk | LightGBM classifier with projection features; isotonic calibration; TreeSHAP reasons | Calibrated probabilities and per-user "why" |
| E5 Actions | Rule catalogue; each action re-scored by E2/E3 (what-if) | Advice is concrete and its effect is measurable |
| E6 Category | Counterparty memory + amount model, top-3 | One tap instead of manual budgeting |
| E7 Smart Route | Cheapest path over a fee graph | Universal-wallet routing |
| E8 Eid | Last-Eid excess spend vs expected bonus | Festival shocks are predictable |
| E9 Learning nudges | Thompson-sampling bandit | Learns which nudges each person accepts |
| E11–E17 | Safe-to-spend, health, lessons, readiness, recent payments, levels/Smart DPS, emergency | Rules on top of model outputs |

### Metrics vs baselines

These are from the held-out test split (15% of users, Aug–Sep 2026). Source: `reports/metrics.md`.

| Model | Metric | Hishab | Baseline |
|---|---|---|---|
| E2 | Balance MAE, day 14 | **৳1,640** | ৳2,084 (same as last month) · ৳3,577 (trailing average) |
| E2 | Balance MAE, day 30 | **৳2,569** | ৳3,056 |
| E2 | P10–P90 coverage, day 14 / 30 | 76.7% / 80.9% | target ≈ 80% |
| E3 | PR-AUC | **0.912** | 0.53 (balance rule) |
| E3 | Precision / recall at alert | **81% / 89%** | 57% / 76% |
| E3 | Median warning lead, new shortfalls | **6 days** | bar: ≥ 5 days |
| E6 | Top-1 / top-3 accuracy | **72.8% / 91.2%** | 66.6% (majority class) |
| E15 | Next-payee hit rate | **64.5%** | 57.2% (most recent) |
| E8 | Eid spend MAE | **৳1,846** | ৳4,309 (global mean) |
| E9 | Action acceptance, day 60 | **58.1%** | 34.1% static · 35.9% random |
| E9 | Lesson acceptance, day 60 | **50.4%** | 46.4% static · 39.0% random |
| E16 | Smart DPS missed-installment rate | 14.0% | 12.7% (flat 10% of income) |
| E16 | Average monthly installment | ৳4,367 | ৳2,474 |

**Honest reading:**

- Every predictive model beats its baseline.
- E2's day-14 band is a little narrow (76.7% vs the 80% target).
- **Smart DPS does not beat the flat 10% rule on missed installments.** It recommends larger installments for steady savers and says "not now" to 51% of users. The product therefore shows the flat-rule amount next to its own advice, never exceeds 25% of income, and the user always chooses freely.

## 6. Real-life impact

**Simulation, clearly labelled as model-based on synthetic data.** Setup:

- 517 held-out user-months are replayed month by month.
- "With Hishab" applies the top-3 actions with each persona's assumed acceptance probability.
- Source: `backend/artifacts/impact_snapshot.json`, also shown on `/impact`.

| Indicator (per user-month) | Baseline | With Hishab |
|---|---|---|
| Shortfall days | 4.13 | **3.73** (−9.8%) |
| Transfer fees | ৳132.9 | **৳127.3** (−4.2%) |
| Cash dependency (cash-out ÷ income) | 39.1% | **35.5%** |
| Shortfall-free months | 42.0% | **45.3%** |
| Emergency buffer (days of living cost) | 0.49 | 0.50 |
| Salary left on day 10 | 34.1% | 33.6% (slightly worse) |
| Monthly active rate | 98.1% | 98.2% |

Linear extrapolation per **100,000 users per month**:

- about **40,300 shortfall days avoided**,
- about **৳5.6 lakh in fees saved**.

Salary-on-day-10 does not improve (34.1% → 33.6%). We have not isolated why. One plausible reason is that accepted actions, such as moving money into pockets on payday, take it out of the main wallet early.

**Benefit to upay:**

- More money stays and moves inside the wallet: NPSB instead of agent cash-out, pockets instead of cash.
- Re-engagement notifications.
- A levelled pipeline into upay's own **DPS** product.
- Everything ships as an API behind existing screens.

**Validation plan after the hackathon:**

1. Offline backtest on governed, anonymised upay data.
2. Randomised A/B pilot with garment-payroll users:
   - **Primary:** shortfall incidence, cash-out share, 30/90-day active rate.
   - **Secondary:** pocket balances, nudge acceptance.
   - **Guardrails:** complaints, opt-outs.
3. A small usability study with real users (task completion without help, taps per task).

## 7. Responsible AI

| Principle | Implementation |
|---|---|
| No harmful automation | The AI never approves, denies, sizes or promises a loan. The DPS-backed cap is a fixed bank rule and "চূড়ান্ত সিদ্ধান্ত ব্যাংক নেবে" is always shown. Withdrawals are never blocked; levels never gate a service |
| Safe language | Forbidden phrases ("approved", "loan offer", "credit score", "ঋণ পাবেন", "তুমি যোগ্য", …) are post-filtered on every LLM answer and tested |
| Grounding | Chat numbers come only from engine tools. Tools are read-only, scoped to the logged-in user, and never take a user ID from the model. Template fallback on timeout, error or refusal. Rate limit 10/min |
| Explainability | TreeSHAP reasons ("কেন?"); every action shows its effect on risk and fees; chat lists the data used; readiness signals show reasons |
| Transparency | "AI" badge on AI-generated content; fees and Eid dates labelled as assumptions; a permanent "Prototype — upay-এর অফিসিয়াল app নয়" ribbon |
| Fairness | Outcomes and alert quality are sliced by persona and area. Gaps above 10 pp are flagged on the Impact page (§8) |
| Privacy and security | Synthetic data only; voice is processed by the browser; the API key is server-side; no secrets in the repo; demo PINs are salted hashes and never logged; the real upay logo is not used |
| Readiness ≠ credit | Readiness signals are educational consistency signals with a disclaimer. No lending decision uses them |

## 8. Limitations and next steps

- **Synthetic data.** The models learn the patterns we injected. The metrics show that the pipeline works end to end; they do not show real-world accuracy.
- **Fairness flags — shop owners.** Alert recall is **9%** for shop owners, against 85–97% for the other personas (precision 50% vs 79–83%). Their income is lumpy and mixed with business money, which the features do not capture, so the risk model misses most of their shortfalls. A per-persona model or business-cash-flow features are needed, and real-data fairness auditing must happen before any use. Until then, shop owners should not read a green signal as an all-clear.
- **Placeholder fees and caps.** Fees, the DPS options and the 80% DPS-loan cap are demo assumptions.
- **Smart DPS** needs real installment data to tune the trade-off between installment size and missed payments.

**With real data:**

- Retrain and recalibrate E2/E3/E6, and re-derive the E12–E14 thresholds.
- Plug E7 into real NPSB and bank routing, and use employer payroll schedules.
- Move the bandit to a feature store.
- Add drift, calibration and fairness monitoring, plus a privacy review.

---

## Appendix — Additional UX suggestions for upay

These are suggestions with rationale, not requirements on upay. The prototype shows each one working.

1. **Move "আরো" to the header** and give the freed bottom-nav slot to **হিসাব**. A live status badge in the nav is noticed every session; a static "more" icon is not.
2. **Collapse the long উপায় পেমেন্ট tile section into one icon** in the empty slot next to এনপিএসবি. Home gets shorter, and **অন্যান্য সার্ভিস** comes into view without scrolling.
3. **Add a সাম্প্রতিক পেমেন্ট row**: four one-tap repeat payments, with bills due within 5 days moved first. Most payments are repeats.
4. **A subtle geometric pattern in the yellow header** with AA-contrast text. It gives a more premium feel with no extra clutter.
5. **Show the customer's avatar** (initials) in the header instead of the logo. It is more personal, and the app already shows the brand everywhere else.
6. **One daily message line in the header** instead of extra cards. The most important thing today is seen first, with no clutter.
