# Hishab (হিসাব) — Design Spec

**Event:** AI DEV FEST 2026 · AI Hackathon (DIU CPC × upay)
**Track:** 03 — Customer Innovation & Financial Independence
**Team:** Solo builder (full-stack + Python), built with AI coding tools
**Spec date:** 2026-10-01 (72-hour clock already running)
**Status:** Draft for review

---

## 0. সংক্ষেপে (Bangla overview)

**Hishab** হলো upay wallet-এর ভেতরে একটা AI cash-flow copilot। মূল user রিনা, গাজীপুরের একজন garment কর্মী। তার বেতন আসে upay-এ, সে বাড়িতে টাকা পাঠায়, প্রচুর cash-out করে, আর মাসের শেষে টাকা কম পড়ে।

Hishab যা করে:
1. **আগামী ৩০ দিনের balance-এর পূর্বাভাস দেয়।** কবে আর কত টাকা কম পড়বে, কেন, আর কী করলে এড়ানো যাবে, তা বলে।
2. **"আজ নিরাপদে কত খরচ করা যায়"** তার একটা সংখ্যা দেয়, budget আর calendar-এ অতীত ও ভবিষ্যৎ একসাথে দেখায়।
3. **সঞ্চয়:** savings pocket, লক্ষ্য, পয়সা-সঞ্চয়, আর ঈদ পরিকল্পনাকারী।
4. **Smart Route (universal wallet):** যেকোনো wallet বা ব্যাংকে টাকা পাঠানোর সবচেয়ে সস্তা পথ দেখায়, আর cash-out fee বাঁচায়।
5. **বাংলায় লিখে বা মুখে প্রশ্ন করা যায়।** উত্তর আসে AI engine-এর আসল সংখ্যা থেকে।
6. **আর্থিক স্বাস্থ্য coach:** জরুরি তহবিল কত দিনের, cash-নির্ভরতা কত, ঘাটতিমুক্ত মাস কয়টা; অভ্যাস চিহ্নিত করা; মাসিক হিসাব রিপোর্ট।
7. **ব্যক্তিগত শেখা:** user-এর নিজের আচরণ আর সংখ্যা দিয়ে ছোট বাংলা পাঠ, যা শেখে কোন পাঠ কাজে দেয়।
8. **নিয়মিততার signal (দায়িত্বশীল credit readiness):** কোনো score বা loan সিদ্ধান্ত নয়। শুধু user নিজে দেখে কোন অভ্যাস ভবিষ্যৎ যোগ্যতায় প্রভাব ফেলতে পারে, আর কী করলে উন্নতি হবে।
9. **upay Analyst tab:** ঘাটতির ঝুঁকি, churn-এর ঝুঁকি, এজেন্টদের cash-out চাহিদার পূর্বাভাস, model-এর মান, আর fairness।

Track 03-এর ৮টা project opportunity-ই cover হয়: health coach, savings planner, spending companion, cash-flow forecasting, goal copilot, inclusive assistant, literacy personalizer, credit readiness।

AI-এর মূল কাজ করে ML model (LightGBM, SHAP, bandit, graph optimization)। LLM (Claude) শুধু ব্যাখ্যা দেয়। কোনো সংখ্যা বানায় না, কোনো সিদ্ধান্ত নেয় না।

---

## 1. Context and constraints

### 1.1 Competition rules that shape the design

| Rule | Design consequence |
|---|---|
| 72 h initial build from T+0; on-site update round on 7 Oct; final 90 min second evaluation | Ship a working deploy by H30; keep code modular (registries/config) so on-site changes are small |
| Public GitHub repo, continuous commit history (single final upload not accepted) | Small, frequent commits per feature; push often |
| README.md must contain 10 specific sections incl. **live deployment URL** | README checklist in §14.3; always-on host |
| Submit video demo + project report | Scripts/outlines in §14.4–14.5 |
| No substantially pre-built challenge-specific solution | All challenge code written after T+0 (this spec is the first artifact) |
| Synthetic / public data only; no production data | Synthetic generator (§6) with documented assumptions |
| Team must explain design and AI components | Spec + clear module boundaries + metrics report |

### 1.2 Judging rubric → where we score

| Criterion (weight) | What earns it in Hishab |
|---|---|
| Problem relevance (20%) | Covers all 8 Track 03 project opportunities (§3.3) and directly answers the guideline's own examples ("Why do I always run short before month-end?", "save ৳30,000 in six months"); Bangladesh-specific (garment payroll, Eid, remittance home, cash-out habit) |
| AI/ML depth (20%) | Forecasting with uncertainty, calibrated risk classifier + SHAP, churn model, category classifier, counterfactual action optimizer, Thompson-sampling bandit, graph route optimizer; all beat stated baselines |
| Business/customer impact (20%) | Customer: shortfall days avoided, fees saved. upay: money retained in wallet, churn risk reduced, agent liquidity planning. Simulated impact in Analyst tab + post-hackathon A/B design |
| Prototype quality (15%) | Live end-to-end app, mobile-first, Bangla UI, voice input, always-on deployment |
| Innovation (10%) | Learning nudges, Smart Route/universal wallet, Eid planner, one engine serving customer + agent + upay |
| Scalability & integration (10%) | Clean API boundary, config-driven rules, model registry, "what changes with real data" plan |
| Responsible AI & security (5%) | Guardrails, explainability, fairness slices, labelled AI text, no autonomous money movement, prompt-injection-safe tools |

### 1.3 Problem statement (guideline template)

> For **garment workers and other low-income upay users in Bangladesh**, **salary leaving the wallet within days (cash-out, remittance, rent) with no visibility of what is coming** causes **month-end cash shortfalls, avoidable cash-out fees, and low wallet retention**. We will build **Hishab, an AI cash-flow copilot** that uses **wallet transaction history** to **forecast balance, warn of shortfalls early, and recommend and learn the most effective actions (saving, cheaper transfer routes, Eid planning)**, with success measured by **shortfall days per user-month, cash-out fees saved, share of salary retained in wallet, and 30/90-day active rate**.

---

## 2. Users and journey

### 2.1 Personas (all synthetic)

| Persona | Share of synthetic users | Income pattern | Role in demo |
|---|---|---|---|
| **Garment worker** (lead: "Rina", Gazipur) | 45% | Monthly salary ~day 7, festival bonus before Eid | Hero persona |
| Daily-wage / gig earner | 20% | Irregular daily inflows | Shows forecasting on noisy income |
| Small shop owner | 20% | Daily merchant receipts, mixed personal and business money | Shows variety |
| University student | 15% | Monthly family allowance and some part-time income | Shows variety |

Every persona's names, places and amounts are synthetic and clearly marked as such.

### 2.2 Rina's month (demo narrative)

1. **Onboarding (≤3 steps):** the app reads her history and shows a first insight: *"তোমার বেতন সাধারণত ৭ তারিখে আসে; ২০ তারিখের পর টাকা কমে যায়।"* She picks a budget mode (auto by default), turns on paisa saving, and sees the pre-made pockets.
2. **Payday (7th):** a plan card appears: emergency pocket ৳500, send home via NPSB (saves ৳X), Eid pocket weekly amount. Each item is one tap to accept or dismiss.
3. **Mid-month:** when she sends or pays, the category is pre-suggested. Budget bars and the "আজ নিরাপদ খরচ" number update.
4. **Risk (18th):** Home turns amber: *"২৪ তারিখে প্রায় ৳১,৮০০ কম পড়তে পারে।"* "কেন?" shows the drivers. Tapping an action redraws the forecast (what-if). Paisa saving auto-pauses.
5. **Anytime:** she asks by voice in Bangla: *"ঈদের জন্য ৳৫,০০০ জমাতে পারব?"*
6. **Month end:** a summary of fees saved and whether the shortfall was avoided.

---

## 3. Product scope

### 3.1 Screens (mobile-first web app, Bangla primary, English toggle)

Bottom navigation: **হোম · পাঠাও/পে · সঞ্চয় · জিজ্ঞেস**. The analyst tab is a separate route (`/analyst`) for upay staff, linked from a header menu.

**F1. Home**
- Balance; greeting; demo-user switcher (header menu).
- **Forecast chart:** 30-day projected balance with P10–P90 band, zero/threshold line, predicted shortfall marker.
- **Risk card:** green, amber or red; headline *"{date}-এ প্রায় ৳{amount} কম পড়তে পারে"* plus likelihood in words and %; a **"কেন?"** expander lists the top 3 drivers in plain Bangla.
- **আজ নিরাপদ খরচ** (safe-to-spend today) number.
- **আর্থিক স্বাস্থ্য snapshot** (E12): three indicators, each with last month's value and an up/down arrow.
  - **জরুরি তহবিল:** "জমানো টাকায় ৯ দিনের খরচ চলবে".
  - **Cash-নির্ভরতা:** "বেতনের ৬২% cash-out হয়".
  - **ঘাটতিমুক্ত মাস:** "গত ৩ মাসে ২ মাস".

  Tapping it opens the **Health Coach** page (F8).
- **শেখার card** (E13): at most one personalised micro-lesson, dismissible.
- **Action cards** (max 3), each with: text, expected effect ("ঝুঁকি ৭২% → ৩১%", "৳৯৫ বাঁচবে"), **রাজি / বাদ / কেন?**. Tapping a card previews the what-if line on the chart.
- Links to Calendar and Budget.

**F2. Calendar** (history plus future)
- Month grid. Past days are shaded by outflow intensity and carry icons for salary, rent, remittance and Eid. Future days show predicted recurring events and are risk-coloured by P50 projected balance.
- Tapping a day shows that day's transactions (past) or predicted events (future).

**F3. Budget**
- Period selector (দৈনিক / সাপ্তাহিক / মাসিক); mode **Auto** (AI-set per category) or **Manual** (user-entered).
- Per-category bars: spent vs budget, with an alert at 80% and 100%.
- In Auto mode each budget shows the reason it was set ("গত ৩ মাসের হিসাব আর সামনের পূর্বাভাস থেকে").

**F4. Savings**
- **Pockets:** জরুরি (emergency), ঈদ, বাড়ি (family), শিক্ষা (education), and custom. Each pocket has a balance, optional target and date, and progress. Money moves in and out freely; withdrawals are **never blocked**.
- **Goal planner:** target plus date gives the recommended monthly amount, a feasibility likelihood, and which actions would make it feasible.
- **Paisa saving (পয়সা-সঞ্চয়)** toggle; see the rule in §5.3. Shows the total saved and an "auto-paused due to risk" state.
- **Eid planner card:** days to the next Eid, last Eid's spend, expected bonus, recommended weekly saving, and a one-tap "ঈদ pocket-এ লক্ষ্য বসাও".

**F5. Send / Pay** (simulated money movement; banner "Demo — কোনো আসল টাকা যাবে না")
- Recipient (from synthetic contacts or a merchant), amount, and **category chip pre-filled by AI** (top-3 alternatives selectable). The user's confirmation is stored.
- **Smart Route panel:** the best route is highlighted with its fee and time versus the alternatives. "সব পথ দেখো" opens the **Money Map**: a node graph (User → upay wallet → NPSB → other MFS wallet / bank account; wallet → bank card; wallet → merchant; wallet → agent cash-out). Tapping any path opens that path's simulated send flow.
- **Contextual nudge on cash-out:** if the cash-out looks like it will be spent at a merchant or forwarded to another wallet, suggest the digital alternative and the fee saved, with a "তবুও cash-out" option.

**F6. Ask (জিজ্ঞেস)**
- Chat in Bangla or English with a **mic button** (Bangla speech recognition in the browser).
- Answers come from engine tools (§8). LLM text is labelled with ✨. An expandable "যে তথ্য দেখে উত্তর" section shows which tool results were used.
- Suggested question chips: "মাসের শেষে টাকা কম পড়ে কেন?", "৬ মাসে ৳৩০,০০০ জমাতে পারব?", "cash-out কীভাবে কমাব?", "এই লেনদেনগুলো বুঝিয়ে বলো"।

**F8. Health Coach (আর্থিক স্বাস্থ্য)** — opened from the Home snapshot
- The three indicators with a 6-month mini trend each.
- **তোমার অভ্যাস** (E12): 3–5 detected habits in plain Bangla, each with its ৳ effect. Examples:
  - "বেতনের ৩ দিনের মধ্যে ৬০% টাকা বেরিয়ে যায়"
  - "মাসে ৪ বার cash-out — fee ৳৩১০"
  - "শুক্রবারে বাজার খরচ বেশি"
- **মাসিক হিসাব রিপোর্ট:** what went well, one thing to change, fees saved, and shortfall avoided or not. Numbers come from the engine; wording comes from a template, or the LLM when available (✨).
- **শেখো (Learn) section** (E13): personalised lesson list. Each lesson embeds the user's own numbers, has a **বুঝেছি / কাজে লাগবে না** response, and links to a related action.
- **নিয়মিততার signal (Credit readiness)** (E14) — a separate card at the bottom, with a fixed disclaimer: *"এটা শুধু তোমার নিজের বোঝার জন্য। এটা কোনো ঋণের সিদ্ধান্ত বা score নয়, upay এটা দিয়ে কোনো সিদ্ধান্ত নেয় না।"*
  - Five transparent signals, each green, amber or red, with a one-line reason:
    1. Income regularity.
    2. Emergency buffer.
    3. On-time bills and recharges.
    4. Shortfall frequency.
    5. Saving consistency.
  - **কী করলে উন্নতি হবে:** for each non-green signal, the specific habit and an E2-based projection, e.g. "প্রতি মাসে ৳৫০০ রাখলে ৩ মাসে 'জরুরি তহবিল' সবুজ হবে".
  - No numeric score, no ranking, no loan offers or links.

**F7. upay Analyst** (`/analyst`, English UI)
- KPI tiles: % users at shortfall risk (14 d), avg predicted shortfall, avoidable cash-out fees / month, money retained if actions accepted (simulated).
- **Impact simulation:** baseline vs with-Hishab for shortfall days, fees and salary retained in wallet. Labelled "simulated; assumptions in docs".
- **Churn risk:** distribution, top global drivers (SHAP), table of at-risk users with drivers and the recommended next-best action.
- **Agent cash-out forecast:** by area for the next 14 days (table and bar chart), with peak day and ratio vs normal.
- **Learning nudges:** acceptance-rate learning curve (bandit vs static ranking) from offline replay, for actions and for lessons.
- **Financial independence:** cohort distribution of the three health indicators, plus simulated change with Hishab. This is the headline Track 03 outcome metric.
- **Lesson effectiveness:** simulated behaviour change after lessons (e.g. cash-out share next month, treated vs not shown).
- **Readiness-signal fairness:** signal distribution by persona, gender and area, with a note that signals never use these attributes as inputs.
- **Model quality:** metrics vs baselines (from `reports/metrics.json`).
- **Fairness:** key metrics sliced by persona, gender and area.
- **"What changes with real upay data"** panel (§11.4).

### 3.2 Out of scope (72 h)
Real money movement or integration with real MFS or NPSB; push notifications; lending or credit **decisions**, credit scores or loan offers (E14 is educational signals only); scam detection (kept as an on-site candidate); user accounts and authentication (a demo-user switcher instead); native mobile app.

### 3.3 Track 03 coverage
| Track 03 opportunity | Where in Hishab |
|---|---|
| AI Financial Health Coach | F8 health snapshot, habits, monthly report (E12) + "কেন?" drivers + chat |
| Personal Savings Planner | F4 goal planner (E8) |
| Smart Spending Companion | E5 actions (`trim_discretionary`, `digital_pay_instead_of_cashout`), cash-out nudge, E12 unusual-spend habits |
| Cash-Flow Forecasting | E2 + E3, Home chart, Calendar |
| Financial Goal Copilot | Pockets (emergency, Eid, family, education, custom) + Eid planner |
| Inclusive Financial Assistant | Bangla-first UI, Bangla voice, simple language |
| Financial Literacy Personalizer | E13 behaviour-triggered lessons with the user's own numbers, bandit-adapted |
| Responsible Credit Readiness | E14 transparent consistency signals + improvement projections, no decisions |

---

## 4. AI engine

All engine modules are plain Python in `backend/hishab/engine/`, are stateless (inputs → outputs), and are unit-tested. ML models are trained offline by scripts and loaded from `backend/artifacts/`.

| ID | Module | Method | Output | Baseline to beat | Metric |
|---|---|---|---|---|---|
| E1 | Recurring detector | Statistical: group by counterparty/type; day-of-month clustering and amount stability (CV) | List of recurring events {type, counterparty, expected day, expected amount, confidence} | n/a (precision/recall vs injected ground truth) | P/R of injected recurring events |
| E2 | Cash-flow forecaster | LightGBM regressor on daily non-recurring outflow (and inflow for irregular earners) + E1 recurring events; 200 bootstrap residual paths → P10/P50/P90 balance | 30-day balance band, expected events | (a) same-as-last-month, (b) trailing-30-day average | MAE of day-14 and day-30 balance; band coverage (P10–P90 ≈ 80%) |
| E3 | Shortfall-risk model | LightGBM binary classifier, isotonic calibration; SHAP drivers | P(shortfall within 14 d), top drivers, predicted date and amount (from E2 P50) | Rule: balance ÷ avg daily spend < days to next income | PR-AUC, ROC-AUC, precision@alert, median warning lead time, calibration (Brier) |
| E4 | Churn-risk model | LightGBM binary classifier + SHAP | P(inactive next 30 d), drivers, mapped next-best action | Rule: days since last transaction > 14 | PR-AUC, ROC-AUC, recall@top-10% |
| E5 | Action optimizer | Candidate actions from `actions.yaml` → apply transform to future flows → re-run E2/E3 → score | Ranked actions with Δrisk, ৳ saved | Static fixed ordering | Avg Δshortfall-prob of top action; see E9 for acceptance |
| E6 | Category suggester | Per-user counterparty memory (confirmed labels) → else LightGBM multiclass (counterparty type, amount bucket, hour, weekday, persona) | Top-3 categories with confidence | Majority-class per counterparty type | Top-1 / top-3 accuracy |
| E7 | Route optimizer | Weighted graph from `fees.yaml`; Dijkstra on fee (tie-break: time); habit detection of recurring post-salary cash-outs | Ranked routes with fee and time; detected costly habits with annual saving | User's habitual path | ৳ saved per transfer (deterministic) |
| E8 | Goal and Eid planner | Monthly-surplus distribution (bootstrap last 6 months, adjusted by E2) → feasibility; Eid need from last Eid's 30-day pre-Eid spend minus expected bonus | Monthly/weekly amount, feasibility %, enabling actions | n/a | Backtest: predicted vs actual pre-Eid spend MAE |
| E9 | Learning nudges | Thompson sampling, Beta(α, β) per (persona, action type), updated per user on accept/dismiss; priors from synthetic acceptance | Acceptance probability used in E5 ranking | Static ranking; random | Offline replay: cumulative acceptance rate vs static/random |
| E10 | Agent cash-out forecast | Aggregate per-user predicted cash-outs (E2 flows × cash-out share, salary-day pattern) by area and day | 14-day cash-out volume per area, peak day, ratio vs normal | Same weekday last month | Area-level MAPE on holdout |
| E11 | Safe-to-spend | Deterministic formula on E1 + E2 (§5.2) | ৳ per day | n/a | n/a |
| E12 | Health indicators and habit miner | Indicators: emergency days = pocket total ÷ avg daily essential spend; cash dependency = cash-out ÷ income (30 d); shortfall-free months (last 3). Habits: rule templates over features (post-salary depletion speed, cash-out count/fees, weekday spikes, category z-score > 2 vs own 3-month history) ranked by ৳ impact | 3 indicators + month-over-month delta; top 3–5 habits; monthly report facts | n/a | Habit detector P/R vs injected habits |
| E13 | Literacy personalizer | Lesson library (`rules/lessons.yaml`, 10–12 Bangla micro-lessons with `{placeholders}`) + trigger rules on E12 features; selection via E9 Thompson sampling per (persona, lesson) | ≤1 lesson card on Home, ranked list in F8, filled with the user's numbers | Random or generic lesson | Offline replay: simulated behaviour change after lesson vs generic/random |
| E14 | Readiness signals | Five transparent rule-based signals (thresholds in `rules/readiness.yaml`) computed from E1/E12 features; improvement path via E2 projection of the recommended habit. **Never uses** persona, gender, area or age as inputs | Signal states + reasons + improvement projection | n/a | Fairness: signal-state distribution by group; unit tests on thresholds |

### 4.1 Feature set (shared; `engine/features.py`)
Per user and observation date:
- **Pay cycle:** days since and until the last/next income, income amount, income regularity.
- **Balance:** current balance; trailing 7/30-day outflow by category; cash-out share of outflow.
- **Post-salary speed:** days from salary to 50% depletion; share of salary cashed out within 3 days.
- **Transfers and savings:** remittance share; other-wallet send share; pocket balances.
- **Calendar:** days to next Eid; month-end flag.
- **Profile:** persona, area, tenure.
- **Engagement:** sessions in the last 7/30 days and their trend (churn only).
- **Forecast-derived** (E3 only): min P50 projected balance over 14 d, P10 min.

### 4.2 Action catalogue (`rules/actions.yaml`)
Each action has `id`, `applies_if` (rule on features), `params` (computed), `transform` (how it modifies future flows), Bangla and English templates, and `sensitive: false|true`.

| id | Applies if | Transform |
|---|---|---|
| `save_on_payday` | regular salary, and risk ≥ amber or a shortfall occurred in any of the last 3 months | Move ৳X to the emergency pocket on salary day (X = min(10% salary, shortfall amount)) |
| `split_remittance` | remittance ≥ 25% of salary in one transfer | Send in two parts (payday + day 15); smooths balance |
| `digital_pay_instead_of_cashout` | recurring cash-out followed by merchant-type spend | Replace cash-out with merchant pay; removes the cash-out fee |
| `cheaper_route` | E7 finds a habit with a cheaper path | Swap the route; fee difference saved |
| `pause_paisa_saving` | paisa saving on and risk ≥ amber | Stop sweeps until the next income |
| `trim_discretionary` | discretionary category above its 3-month median by > 20% | Reduce that category by 10% (never essentials) |
| `eid_weekly_saving` | Eid within 120 days and Eid pocket below need | Weekly transfer to the Eid pocket |

**Risk levels** (from E3 probability, configurable in `guardrails.yaml`): green < 0.30 ≤ amber < 0.60 ≤ red.

**Ranking score** = `benefit × p_accept`. Here `benefit` = Δshortfall-probability × 1000 + fees saved (৳, 30 d), normalised, and `p_accept` is sampled from E9. Show the top 3 after guardrails (§5.1).

---

## 5. Business rules and guardrails (kept separate from ML)

### 5.1 Guardrails (`rules/guardrails.yaml`, enforced in `engine/actions.py` and the LLM tool layer)
- Never recommend borrowing, loans or credit products.
- Never recommend increasing spending, and never promote paid products.
- Never suggest cutting essential or sensitive categories: family support amount, health, education, rent. Timing changes (split) are allowed; reductions are not.
- Never block or discourage withdrawals from pockets. "তবুও cash-out" is always available.
- No autonomous money movement. Every action requires an explicit user tap, and the demo only simulates it.
- **Readiness signals (E14):**
  - No numeric score.
  - No loan offers, links or "you qualify" language.
  - Never used by any upay-facing decision path, in code or in the API. The analyst API exposes only aggregate distributions for fairness checking.
  - The disclaimer is always shown.
  - Inputs exclude protected or proxy attributes (persona, gender, area, age).
- **Lessons (E13):** educational only, never promote paid products; at most 1 lesson card on Home at a time.
- At most 3 action cards at once, and at most 1 contextual nudge per send/pay flow.

### 5.2 Safe-to-spend (E11)
```
horizon     = days until next expected income (regular earners) | 7 (irregular earners)
committed   = Σ recurring outflows expected before horizon (E1)
cushion     = P50 − P10 of E2 projected balance at horizon   # uncertainty buffer
safe_today  = max(0, (balance − committed − cushion − essential_buffer) / horizon)
```
`essential_buffer` defaults to ৳200 (config).

### 5.3 Paisa saving (পয়সা-সঞ্চয়)
- After every transaction, if the main balance has a fractional part (৳0.01–৳0.99), that fraction is swept into the **পয়সা pocket**. Example: the balance becomes ৳6,240.35, so ৳0.35 moves and the balance is ৳6,240.00.
- This never adds a charge to a payment and never makes a payment fail.
- It is auto-paused while E3 risk is amber or red, resumes on the next income, and shows its state in the UI.
- Pitch framing: habit-building; amounts are small and we say so honestly.

### 5.4 Fees and routes (`rules/fees.yaml`)
- All fee values are **placeholder assumptions** for the demo, documented in the README. Each edge has `{fixed, pct, min, max, minutes}`.
- Nodes: `upay_wallet, npsb, other_mfs_wallet, bank_account, bank_card, merchant, agent_cash`.
- Other MFS providers are referred to generically ("অন্য MFS wallet"), with no third-party logos.

### 5.5 Eid calendar (`rules/eid_dates.yaml`)
- Approximate Eid-ul-Fitr and Eid-ul-Adha dates for 2025–2027, marked approximate.
- Festival bonus assumption for the garment persona (configurable).

---

## 6. Synthetic data

### 6.1 Generator (`backend/hishab/data/generator.py`)
- Seeded (`SEED=42`) and fully reproducible: `python -m scripts.generate_data`.
- **Scale:** 2,000 users × 12 months (2025-10-01 → 2026-09-30). The serving subset is 300 users, including handcrafted **Rina** (`user_id=U0001`) and one showcase user per persona.
- **Demo "today":** `DEMO_TODAY=2026-09-18` (config). Serving uses history ≤ DEMO_TODAY and forecasts after it, so Rina is mid-cycle and heading to a shortfall.

### 6.2 Tables (parquet in `backend/data/`, gitignored except the small serving subset)
- `users`: user_id, synthetic_name, persona, gender, age_band, area, tenure_days, family_wallet_type (`upay|other_mfs|bank|cash`), paisa_saving_default.
- `transactions`: tx_id, user_id, ts, type (`salary_in, bonus_in, cash_in, cash_out, send_money, receive_money, merchant_pay, bill_pay, mobile_recharge, pocket_in, pocket_out`), amount (2 dp), fee, counterparty_id, counterparty_type (`employer, person, merchant, agent, biller`), counterparty_channel (`upay, other_mfs, bank`), category (`food_grocery, rent, family_support, transport, mobile, health, education, utilities, shopping, festival, other`), area.
- `sessions`: user_id, date, session_count (for churn).
- `labels`: per (user, observation_date): `shortfall_14d`, `churn_30d`, `pre_eid_spend`.
- `action_acceptance_truth`: latent acceptance propensity per (persona, action type), used to simulate bandit feedback.
- `agents`: agent_id, area.

### 6.3 Injected patterns (each documented in `docs/synthetic-data.md`)
- **Salary:** garment day 5–9 (assumption: wages paid in the first working days); persona-specific amount ranges (synthetic).
- **Remittance:** 25–45% of salary sent home within 1–3 days of salary; the channel depends on `family_wallet_type` (cash ⇒ cash-out habit).
- **Other outflows:**
  - Rent between day 1 and day 10.
  - Weekly grocery spending.
  - Mobile recharge.
  - Random health shocks (rare, large).
  - Weekend and month-end effects.
- **Eid:**
  - Bonus about 7–10 days before Eid for the garment persona.
  - Festival spending spike in the 14 days before Eid.
  - Higher remittance before Eid.
- **Irregular earners:** daily income with weather or seasonal dips.
- **Shortfall:** arises naturally when the balance falls below ৳200 before the next income. Essential spends that would fail are deferred and flagged.
- **Churn mechanism (assumed causal story):** higher churn probability with
  - fast post-salary depletion,
  - a high cash-out share,
  - a high other-wallet send share,
  - zero pocket balance,
  - declining sessions.

  Churned users stop transacting.
- **Noise:** amount jitter, missed or late events, and 5% random category noise, so models are not trivially perfect.

### 6.4 Splits (leakage-safe)
- **Users:** 85% train/validation, 15% held out entirely for test.
- **Time:** observation dates in months 1–9 for training, month 10 for validation, months 11–12 for testing.
- The test set is never used for training or tuning. Metrics are reported on the test set only.

---

## 7. Learning nudges (E9) detail
- **State:** `Beta(α, β)` per (persona, action_type) as a global prior, plus per-user counts in SQLite.
- **On show:** sample θ ~ Beta per candidate and use it as `p_accept` in the ranking.
- **On response:** accept → α += 1, dismiss → β += 1 (user level). Global priors are refreshed by the offline script.
- **Offline replay** (`scripts/evaluate.py`): simulate 60 days of nudges against `action_acceptance_truth` for test users. Compare cumulative acceptance and Δshortfall for bandit vs static vs random, and plot the curve in Analyst.

---

## 8. LLM layer (`backend/hishab/llm/`)
- **Model:** Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) via the Anthropic Python SDK. Confirm the exact model ID and SDK usage at implementation time.
- **Tool use.** Tools are read-only and scoped server-side to the current demo user. The model never chooses `user_id`. Tools:
  - `get_home_summary`
  - `get_shortfall_drivers`
  - `list_actions`
  - `simulate_action`
  - `plan_goal`
  - `plan_eid`
  - `get_budget_status`
  - `find_route`
  - `get_transactions_summary(period)`
  - `get_health`
  - `get_readiness`
  - `get_lessons`
- **System prompt rules:**
  - Answer only from tool results.
  - Never invent numbers.
  - Mirror the user's language (Bangla or English) in simple words, short sentences, rounded amounts.
  - Follow the guardrails in §5.1.
  - If asked something out of scope, say so briefly.
- **Response contract:** `{text, used_tools: [...], numbers_source: "engine"}`. The UI shows the ✨ label and a collapsible list of tool results.
- **Safety and robustness:**
  - Input limit of 500 characters.
  - 10 requests per minute per session.
  - 8 s timeout.
  - If the API key is missing, errors or times out, a **template fallback** answers the suggested questions from engine outputs. The demo never breaks.
- **Voice (F6):** Web Speech API `SpeechRecognition` with `lang='bn-BD'`, feature-detected. Only recognised text is sent to the server. If unsupported, the mic is hidden and a tooltip explains. Optional `speechSynthesis` reads answers if a Bangla voice exists.

---

## 9. Architecture

### 9.1 Repository layout
```
/
├─ backend/
│  ├─ hishab/
│  │  ├─ config.py            # env + paths + DEMO_TODAY
│  │  ├─ data/                # generator.py, personas.yaml, loader.py
│  │  ├─ engine/              # features, recurring, forecast, risk, churn, category,
│  │  │                       # actions, bandit, route, goals, eid, safe_spend, agents,
│  │  │                       # health, lessons, readiness
│  │  ├─ rules/               # actions.yaml, guardrails.yaml, fees.yaml, eid_dates.yaml,
│  │  │                       # lessons.yaml, readiness.yaml
│  │  ├─ llm/                 # client.py, tools.py, prompts.py, fallback.py
│  │  ├─ store/               # sqlite.py (user state: pockets, toggles, responses, labels)
│  │  └─ api/                 # main.py, routes/*.py, schemas.py
│  ├─ artifacts/              # trained models + analyst_snapshot.json (committed, small)
│  ├─ data/                   # serving parquet subset (committed), full data gitignored
│  ├─ tests/
│  └─ requirements.txt
├─ scripts/                   # generate_data.py, train_all.py, evaluate.py
├─ web/                       # React + Vite + TS + Tailwind + Recharts
├─ reports/                   # metrics.json, metrics.md (generated)
├─ docs/                      # this spec, synthetic-data.md, report, video script
├─ Dockerfile
├─ .github/workflows/ci.yml   # pytest + web build on push
└─ README.md
```

### 9.2 Data flow
Synthetic data → features → models (E1–E10) → business rules and guardrails → API → UI and LLM explanation → user accept/dismiss → SQLite → bandit update (feedback loop).

### 9.3 API (FastAPI, JSON, `/api` prefix)
| Method | Path | Returns |
|---|---|---|
| GET | `/health` | status, model versions, LLM availability |
| GET | `/users` | demo users (id, name, persona, area) |
| GET | `/users/{id}/home` | balance, forecast band, risk + drivers, safe_today, actions (top 3) |
| POST | `/users/{id}/actions/simulate` | forecast + risk with an action applied (no persistence) |
| POST | `/users/{id}/actions/{action_id}/respond` | records accept/dismiss → bandit update |
| GET | `/users/{id}/health` | 3 indicators + deltas + 6-month trends, habits, monthly report |
| GET | `/users/{id}/lessons` | ranked personalised lessons (top 1 also in `/home`) |
| POST | `/users/{id}/lessons/{lesson_id}/respond` | records বুঝেছি / কাজে লাগবে না → bandit update |
| GET | `/users/{id}/readiness` | 5 signals + reasons + improvement projections + disclaimer |
| GET | `/users/{id}/calendar?month=YYYY-MM` | per-day past totals/events + future predictions and risk colour |
| GET | `/users/{id}/budget?period=day\|week\|month` | per-category budget (auto/manual) vs spent |
| PUT | `/users/{id}/budget` | set mode / manual amounts |
| GET | `/users/{id}/savings` | pockets, paisa saving state and total, Eid plan |
| POST | `/users/{id}/savings/pockets/{pocket}/move` | simulated in/out |
| PUT | `/users/{id}/savings/paisa` | toggle paisa saving |
| POST | `/users/{id}/goals/plan` | goal feasibility plan |
| POST | `/users/{id}/category/suggest` | top-3 categories for a draft transaction |
| POST | `/users/{id}/category/confirm` | store confirmed label |
| POST | `/users/{id}/route` | ranked routes for {amount, destination_type} + habit insight |
| POST | `/users/{id}/send` | simulated send/pay (applies paisa sweep, records category) |
| POST | `/users/{id}/chat` | LLM answer (or fallback) + used tools |
| POST | `/demo/reset` | reset SQLite state to seed |
| GET | `/analyst/overview` | KPIs, impact sim, churn, agents, bandit curve, metrics, fairness |

Pydantic schemas live in `api/schemas.py`, and the frontend types mirror them.

### 9.4 State and performance
- Engine data (serving parquet + models) is loaded once at startup into memory.
- User state lives in SQLite at `/tmp/hishab.db` (ephemeral on the host). It is seeded on startup and resettable via `/demo/reset`.
- `/analyst/overview` serves the precomputed `artifacts/analyst_snapshot.json` built by `scripts/evaluate.py`.
- Target is < 400 ms p50 for `/home` on the host.

### 9.5 Frontend
- React 18 + Vite + TypeScript + Tailwind + Recharts + React Router.
- i18n via a simple dictionary (`bn` default, `en`), with Bangla numerals in the `bn` locale.
- **Visual style:** clean wallet-app look. Risk colours are green, amber and red, with large tap targets. The rich Home (forecast chart and action cards) is the approved direction.
- Built to static files and served by FastAPI (`/` → SPA, `/api` → API).

### 9.6 Deployment
- Single multi-stage Docker image: Node build of `web/`, then a Python 3.11 slim image running uvicorn on port 7860.
- **Primary host:** Hugging Face Spaces (Docker SDK; stays awake through judging). **Backup:** Render.
- Secrets: `ANTHROPIC_API_KEY`. Config env: `DEMO_TODAY`, `LLM_ENABLED`, `LLM_MODEL`.
- **First deploy by H30**, then redeploy on each milestone.

---

## 10. Responsible AI and security

| Principle | Implementation |
|---|---|
| Privacy | Synthetic data only; voice processed in the browser; no PII; no real accounts |
| Explainability | SHAP drivers for risk and churn; every action shows its expected effect; "কেন?" everywhere; tool trace in chat |
| Fairness | Metrics sliced by persona, gender and area in the Analyst tab; flag gaps > 10 pp |
| Security | API key server-side only; read-only, user-scoped LLM tools; input limits; rate limiting; no secrets in the repo (`.env.example` only) |
| Human oversight | All actions are user-initiated; analyst outputs are recommendations for staff, never automated account changes |
| Transparency | ✨ label on AI-generated text; predictions vs assumptions vs generated text visibly separated; fee and Eid assumptions labelled |
| No harmful automation | No lending decisions, no blocked withdrawals, no manipulative nudges (§5.1) |

---

## 11. Evaluation and impact

### 11.1 Offline model evaluation (`scripts/evaluate.py` → `reports/metrics.json` + `metrics.md`)
- Each model has its metrics vs baselines (see §4 table) on the leakage-safe test split.
- **Success bar:**
  - E2 beats both baselines on MAE.
  - E3 PR-AUC beats the rule baseline, with median lead time ≥ 5 days.
  - E4 beats the recency rule.
  - E6 top-3 accuracy is ≥ 90%.
  - The E9 bandit beats static ranking in the replay.

  If a model doesn't beat its baseline, we report that honestly and keep the baseline in the product.

### 11.2 Impact simulation (Analyst)
On test users over the test months:
1. **Baseline:** actual synthetic outcomes.
2. **With Hishab:** apply top actions with acceptance drawn from `action_acceptance_truth`, then recompute shortfall days, fees paid, salary share retained in wallet at day +10, and churn probability (E4 on modified features).

Results are reported per user-month and extrapolated to "per 100,000 users", **clearly labelled as model-based simulation on synthetic data.**

### 11.3 Post-hackathon validation plan
- **Offline:** backtest on governed, anonymised upay data.
- **Pilot:** randomised A/B with garment-payroll users.
  - **Primary metrics:** shortfall incidence; cash-out share; 30/90-day active rate.
  - **Secondary metrics:** pocket balances; nudge acceptance.
  - **Guardrail metrics:** complaints; opt-outs.
- **Usability:** a small usability study with real users (task completion without help, taps per task).

### 11.4 What changes with real data
- Retrain E2–E6 on real distributions and recalibrate E3 and E4.
- Replace placeholder fees with real tariffs.
- Plug E7 into real NPSB and bank routing.
- Use real payroll schedules from employer disbursement data.
- Move the bandit to a production feature store.
- Governance: model monitoring (drift, calibration), a fairness audit, and a privacy review.

---

## 12. Testing strategy
- **Engine unit tests (pytest).** Each test runs on a tiny generated fixture:
  - E1 finds the injected salary day (±1) and the rent.
  - E2 output shape and monotonic quantiles (P10 ≤ P50 ≤ P90).
  - E3/E4 probabilities lie in [0, 1].
  - E5 never returns guardrail-violating actions.
  - E5 `pause_paisa_saving` appears when risk is high.
  - E7 picks the cheapest path on a hand-built fee table.
  - E8 Eid weekly amount arithmetic.
  - E9 Beta updates.
  - E11 is never negative.
  - Paisa sweep arithmetic.
  - E12 indicators on a hand-built fixture, and habit detection of injected habits.
  - E13 lesson triggers fire only on their conditions, and placeholders are always filled.
  - E14 thresholds; E14 output never contains a numeric score or loan language; E14 inputs exclude protected attributes (asserted on the feature list).
- **API tests:** FastAPI `TestClient` for every route (happy path + 404 user + validation error). The chat route is tested with the LLM disabled (fallback path).
- **Generator tests:** reproducible with a seed; no negative balances; label prevalence within expected ranges.
- **Frontend:** `npm run build` and a type-check in CI, plus a manual demo checklist (`docs/demo-checklist.md`).
- **CI:** GitHub Actions runs pytest and the web build on every push.

---

## 13. On-site readiness (7 Oct update round)
- Extension points are registries/config:
  - New action → add a `actions.yaml` entry plus a transform function.
  - New route or fee → `fees.yaml`.
  - New persona → `personas.yaml` plus regenerate.
  - New chat capability → add a tool in `llm/tools.py`.
- **Likely asks, pre-thought:**
  - Scam/suspicious-recipient warning (Isolation Forest on recipient novelty + amount + time).
  - Notification simulation.
  - Agent-facing view.
  - English/Bangla parity.
  - Accessibility tweaks.
  - A new persona.
  - Explainability depth.
- Keep `main` always deployable; on-site work in short commits.

---

## 14. Delivery plan

### 14.1 72-hour schedule (from T+0; includes sleep)
| Hours | Work | Exit criterion |
|---|---|---|
| 0–5 | Repo, CI skeleton, config, synthetic generator (incl. Eid, areas, churn, acceptance truth, injected habits, bill timeliness) | `generate_data` produces tables; generator tests pass |
| 5–13 | Features, E1, E2, E3 + baselines + evaluate script | metrics.md shows E2/E3 vs baselines |
| 13–19 | E5 actions + guardrails, E11 safe-to-spend, E7 route, E8 goals + Eid | Engine tests pass |
| 19–23 | E4 churn, E6 category, E9 bandit + replay, E10 agents | metrics.md complete |
| 23–26 | E12 health + habits, E13 lessons (library + triggers), E14 readiness signals | Engine tests pass; analyst_snapshot.json |
| 26–31 | FastAPI routes + SQLite + API tests, Dockerfile, **first deploy** | Live URL serves `/api/health` and a stub UI |
| 31–46 | React UI: Home (incl. health snapshot + lesson card), Health Coach, Calendar, Budget, Savings, Send/Pay + Smart Route + Money Map, Analyst | Full flow clickable on the live URL |
| 46–51 | Chat + tools + fallback + Bangla voice | Chat answers suggested questions; fallback verified |
| 51–56 | Polish, bug fixes, fairness views, final deploy | Demo checklist passes on the live URL |
| 56–65 | README (10 sections), project report, demo video | All submission files ready |
| 65–72 | Buffer (~4 h usable after rest), final verification, submit | Submitted before deadline |

**Time warning:** with all features in, the buffer is thin for a solo builder. The cut order in §14.2 is mandatory to follow if any phase overruns by more than 2 hours.

### 14.2 Cut order if behind schedule
1. E10 agent forecast reduced to a table only.
2. E14 "কী করলে উন্নতি হবে" projection reduced to static habit text (signals and disclaimer stay).
3. Churn UI reduced to KPI + top drivers.
4. E13 lesson library reduced to 6 lessons; lesson-effectiveness view dropped.
5. E6 ML replaced by counterparty-memory + rules.
6. Chat reduced to template fallback; voice Chrome-only.

**Never cut:** E2 forecast, E3 risk, E5 actions, E7 Smart Route, E8 Eid planner, E9 learning nudges, E12 health snapshot, E14 signals + disclaimer, live deployment.

### 14.3 README checklist (rulebook §6.2)
1. Project overview
2. Features + how AI is used
3. Tech stack
4. Requirements
5. Installation and setup
6. Environment variables (placeholders)
7. Run and build commands
8. Live deployment URL
9. Testing instructions
10. Other configuration (DEMO_TODAY, fees/Eid assumptions, data regeneration)

### 14.4 Project report outline (rulebook §7.3)
1. Problem
2. Proposed idea
3. Implemented solution
4. Key features
5. AI approach (engine table + metrics vs baselines)
6. Real-life impact (simulation + validation plan)
7. Responsible AI
8. Limitations and next steps

### 14.5 Demo video (3–5 min) outline
1. Rina's problem (20 s).
2. Home: forecast, risk, "কেন?", tap an action to see the what-if (50 s).
2b. Health Coach: indicators, habits, a personalised lesson, readiness signals with disclaimer (30 s).
3. Send home with Smart Route and the cash-out nudge (40 s).
4. Savings: Eid planner and paisa saving (30 s).
5. Bangla voice question (30 s).
6. Analyst: impact, churn, agent forecast, metrics vs baselines, fairness (50 s).
7. Responsible AI + what's next (20 s).

### 14.6 Commit policy
- One commit per meaningful step (feature, test, fix), with a conventional message (`feat:`, `fix:`, `test:`, `docs:`).
- Push at least every 1–2 hours. Never squash the history.

---

## 15. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Synthetic circularity ("model learns what you injected") | Say it openly. Add noise, use held-out users, compare against baselines, and frame results as a pipeline demonstration ready for real data |
| Solo time overrun | Strict schedule, early deploy, cut order (§14.2) |
| LLM outage, cost or rate limits | Haiku model, rate limiting, template fallback |
| Bangla speech recognition unsupported in a judge's browser | Feature-detect, typed fallback, demo video shows voice in Chrome |
| Host downtime | Render backup deploy; README lists both |
| Readiness signals read as a credit score | No number, fixed disclaimer, no loan language, protected attributes excluded, fairness view; say "educational signals" in the pitch |
| Placeholder fees challenged by judges | Labelled assumptions in config; show how real tariffs plug in |

## 16. Decisions recorded
- **Track:** 03. **Lead persona:** garment worker. **Stack:** FastAPI + React in one container. **LLM:** Claude.
- The rich Home design (forecast chart + action cards) is approved; the simplified variant was rejected.
- **Added unique features:** learning nudges (bandit), Bangla voice, Eid planner, agent cash-out forecast.
- **Added for retention:** churn model, safe-to-spend, and Smart Route framed as a universal wallet. Retention is a supporting business argument, not the headline.
- **Paisa saving** = sweep of the balance's fractional part after each transaction (§5.3).
- **Full Track 03 coverage:** Health Coach (E12), Literacy Personalizer (E13), and Responsible Credit Readiness as transparent, non-scored, user-only signals (E14) — all three in full scope.
