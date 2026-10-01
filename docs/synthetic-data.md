# Synthetic data — assumptions and injected patterns

All data in Hishab is **synthetic**. No real upay or personal data is used. Names, phone numbers,
places, amounts and behaviours are generated. Source: `backend/hishab/data/generator.py`,
parameters: `backend/hishab/data/personas.yaml`.

- **Reproducible:** `python scripts/generate_data.py --users 2000 --seed 42`.
- **Period:** 2025-10-01 → 2026-09-30 (12 months).
- **Demo "today":** `DEMO_TODAY=2026-09-18`.
- **Output:**
  - `backend/data/full/`: 2,000 users, gitignored.
  - `backend/data/serving/`: 300-user subset, committed and used by the live app.

## Personas

| Persona | Share | Income (assumption) |
|---|---|---|
| Garment worker | 45% | Monthly salary ৳10,000–18,000, paid on day 5–9 (assumes wages are paid in the first working days) |
| Daily-wage earner | 20% | ৳400–900 on ~80% of days; ×0.75 work probability in Jun–Aug (monsoon) |
| Small shop owner | 20% | Customer receipts ৳800–3,000 on ~85% of days; weekly restock = 35–55% of receipts |
| University student | 15% | Monthly family allowance ৳4,000–9,000 on day 1–5; occasional tuition income |

### Showcase users

| User | Who | Behaviour |
|---|---|---|
| **U0001 — রিনা আক্তার** | Garment worker, Gazipur | Salary ৳12,500 on the 7th. 35% sent home by cash-out (family has no wallet). Rent ৳3,000 on the 5th. Spends slightly more than she earns, spends heavily at Eid (festival spending 1.25 × monthly income, more than her bonus covers), and doesn't cut back when money runs low. Low noise and no random health shocks, so her story is stable: about ৳2,000–2,500 left on 18 Sep, shortfall from about the 25th |
| U0002 | Daily-wage earner | Irregular income |
| U0003 | Shop owner | Mixed personal/business money |
| U0004 | Student | Allowance-based |
| **U0005 — সুমি খাতুন** | Garment worker, "saver" | Saves ৳20 every day plus 3–8% of salary, spends below income, sends home via another wallet. Green risk, so it shows savings levels and Smart DPS |

## Injected patterns

| Pattern | Assumption |
|---|---|
| Opening balance | Cash-in of 10–40% of monthly income on day 1 |
| Rent | ৳1,500–9,000 (by persona) on day 1–10, paid to a landlord (send money) |
| Remittance home | 25–45% of salary (garment), 2 days after salary. Weekly for daily-wage/shop. Channel by family wallet: **cash ⇒ cash-out (fee)**, other wallet / bank ⇒ NPSB-style send (fee), upay ⇒ free send |
| Utilities | ৳200–2,000 bill on day 10–20 for a share of users |
| Mobile recharge | 2–6 times a month, ৳30–400 |
| Daily spending | Base need = (income × spend ratio − fixed costs) / 30, lognormal noise, +20% on Fri/Sat, +10% after the 25th. ×0.7 when balance < ৳1,000 (belt-tightening; not for Rina) |
| Cash vs digital | A per-user digital share (5–70%) is paid by merchant payments. The rest is withdrawn by cash-out every 4–7 days |
| Health shocks | 0.8% chance per day of a ৳800–4,000 pharmacy payment (essential) |
| Eid | Garment workers get a bonus of 0.5 × salary 8 days before Eid. Festival spending of 0.2–0.8 × monthly income over the 14 days before Eid (half shop payments, half cash). Extra remittance of 0.5 × usual 5 days before Eid. Eid dates are approximate (`rules/eid_dates.yaml`) |
| Savings | "Savers" (10–30% by persona) move 3–8% of income to an emergency pocket on payday, and take up to ৳1,000 back when the balance is below ৳300 |
| DPS | 5–18% of users (by persona) hold an Islamic DPS. 60% sized at 5–12% of income, 40% over-committed at 18–30%. If the balance is short on the installment day, the installment is recorded as **missed** |
| Shortfall | A day whose end-of-day main balance is below ৳200 and that is not an income day. Essential payments (rent, remittance, bills, health, tuition) that can't be paid are deferred and retried |
| Inactivity | Monthly probability `sigmoid(−5.2 + 1.6·cash-out share + 1.1·other-wallet share + 0.7·[fast depletion] − 0.6·[has pocket] − 1.0·session trend)`. Inactive users stop transacting. Used **only** for the simulated active-rate metric; showcase users never go inactive |
| Sessions | Poisson app opens per day with a slow random drift; doubled on income days |
| Fees | From `rules/fees.yaml`. Cash-out 1.85%, NPSB send 0.5% (min ৳5, max ৳50). **All fee values are placeholders** |
| Acceptance truth | Latent probability that each persona accepts each action/lesson (base value × persona multiplier × noise). Used only to simulate feedback for the learning bandit |

## Labels

- `shortfall_14d`: any shortfall day in the 14 days after a weekly (Sunday) observation date. Only counted while the user is active.
- `inactive_30d`: the user goes inactive within 30 days after the observation date.
- `pre_eid_spend`: festival spending in the 30 days before the next Eid, for observation dates up to 45 days before it.

## Honest limitations

Models trained on this data learn the patterns we injected. Results show that the pipeline works end to end, not real-world accuracy. To counter this we use noise, held-out users, a time-based split and simple baselines. With governed upay data the same pipeline would be retrained and recalibrated (see the spec, §11.4).
