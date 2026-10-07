# Hishab AI: Phase 2 Development Plan

> **Read this first if you are a Claude session or a teammate picking up this work.**
> This file is the single source of truth for Phase 2. It is based on the Phase 1 judges' feedback plus a 7-domain code audit run on 2026-10-07.
> Every task has an ID (e.g. `S-03`), files, and an acceptance check. When a task is done, tick its box, add the date, and commit. Do not start a P1 task while a P0 task in the same workstream is still open, unless it is independent.

---

## 0. Working rules (for Claude sessions)

**Run commands** (Windows; Git Bash paths):
- Backend tests: `cd backend && .venv/Scripts/python -m pytest tests -q`
- Backend server: `cd backend && .venv/Scripts/python -m uvicorn hishab.api.main:create_app --factory --port 8000` (or `preview_start` with name `hishab`, from `.claude/launch.json`)
- Web: `cd web && npm run typecheck && npx vitest run && npm run build && npm run dev`
- Train / evaluate (from the repo root, not `backend/scripts`): `scripts/train_all.py`, `scripts/evaluate.py`, `scripts/evaluate_impact.py`, `scripts/generate_data.py`
- Intent model training: `backend/scripts/train_ai.py`

**Rules**
1. **Honesty first.** Never label anything "AI", "predicted", or "measured" unless the code really does it. Synthetic results are labelled `Simulated`. Judges read the code.
2. **No more root-level `fix_*.py` patch scripts.** Edit source files directly. Every change needs a test or a reproducible script under `scripts/`.
3. Every new number that goes into the report must be produced by a committed script and written to `docs/eval/` or `backend/artifacts/`.
4. Keep the core story: **predict and prevent month-end liquidity shortfalls.** If a change does not serve that loop (or its evidence, security, or scale), it is P2 or out of scope.
5. Run the full backend test suite and `npm run typecheck` before every commit once task `Q-01` is done.

---

## 1. Where the points are

| Criterion | Phase 1 score | Points lost | Main cause (from judges + audit) |
|---|---|---|---|
| Business/customer impact | 11.67 / 20 | **8.33** | All impact numbers simulated; bandit and impact are graded against their own assumptions; single ×100k number with no CI |
| Problem relevance | 14.67 / 20 | **5.33** | Secondary features dilute the story; core forecast UI is not even mounted; no real user evidence |
| Scalability & integration | 5.0 / 10 | **5.00** | SQLite + reset-on-boot, single process, in-memory locks/limiters, no ingestion, no MLOps, no load test |
| AI/ML depth | 16.67 / 20 | **3.33** | No robustness tests, weak baselines, no calibration analysis, no ablations |
| Innovation | 7.33 / 10 | **2.67** | Learning component not shown to add value; some "AI" is simulated |
| Prototype quality | 13.33 / 15 | **1.67** | CI echoes "Tests passed!"; demo-grade parts |
| Responsible AI & security | 3.67 / 5 | **1.33** | CORS `*`, tokens never expire, weak PIN hash, open routes |

**Priority order by points recoverable per effort:** Business → Problem → Scalability → AI/ML → Innovation → Prototype → Security. Security and Prototype P0 items are still done first because they are cheap and judges flagged specific lines.

---

## 2. Credibility killers: fix these before anything else (Week 1, days 1–2)

These are things a judge can find by reading the code. Each one makes every other claim look less believable.

| ID | Problem | Where | Fix |
|---|---|---|---|
| - [x] **C-01** (2026-10-07) | "AI-predicted Liquidity Score" for agents is `random.sample` over 5 hard-coded shops with random coordinates; a second hard-coded list in the LLM tool | `backend/hishab/api/routes/agents.py:23-53`, `backend/hishab/llm/tools.py:127-131`, `README.md`, `generate_slides.py`, `generate_report.py`, `create_docs.py` | Remove the "AI" claim everywhere. Either delete the Agent Locator from navigation, or make it a deterministic seeded dataset with haversine distance labelled "demo data, heuristic". Add `require_user`. |
| - [x] **C-02** (2026-10-07) | The core forecast UI (`ForecastChart.tsx` with P10–P90 band, shortfall marker, what-if line) is **not imported by any page**. `remove_forecast.py` stripped risk colours from the calendar. | `web/src/components/ForecastChart.tsx`, `web/src/pages/hub/*`, `web/src/pages/hub/Calendar.tsx` | See `P-01`..`P-03`. |
| - [x] **C-03** (2026-10-07) | Bandit priors are built from the generator's hidden ground truth (`Bandit.from_truth(acceptance_truth)`), and the impact replay draws acceptances from the same table. "Static" baseline is `items[0]`. | `scripts/train_all.py:54`, `backend/hishab/engine/bandit.py`, `scripts/evaluate_impact.py:166-181,222` | See `I-01`. Until fixed, do not quote the 0.58 vs 0.34 bandit result. |
| - [x] **C-04** (2026-10-07) | CI test step is `echo "Tests passed!"`. Real status: **241 passed / 14 failed** backend, **3 failed** vitest, **21 TypeScript errors**. | `.github/workflows/ci.yml`, `.github/workflows/deploy.yml` | See `Q-01`..`Q-03`. |
| - [x] **C-05** (2026-10-07) | `training_log.txt` repeats "Total accuracy improving…" with no metric; `ai_trainer_daemon.py` appends synthetic phrases and never retrains. Looks like fake MLOps. | `backend/hishab/training_log.txt`, `ai_trainer_daemon.py` | Delete both. Real retraining is `X-07`. |
| - [x] **C-06** (2026-10-07) | `fairness()` uses hand-picked alert thresholds per group (0.05 for shop_owner/Uttara, 0.30 for others), which can hide the gap it claims to monitor. | `scripts/evaluate_impact.py:275` | One global threshold. Report per-group calibration openly. |
| - [x] **C-07** (2026-10-07) | `Overview.tsx` uses mock data (`dpsBase = 2000`, `loanBase = 1500`, "Mock historical data multiplier") and reads fields that don't exist (`monthly_income`). | `web/src/pages/hub/Overview.tsx` | Remove from navigation (see `P-01`). |
| - [x] **C-08** (2026-10-07) | Intent-model evaluation leaks: typo augmentations of the same seed phrase land in both train and test; `train_ai_advanced.py` duplicates ×10 then `cv=2`. | `backend/scripts/train_ai.py:208-219`, `backend/scripts/train_ai_advanced.py:248-316` | `GroupKFold` by seed phrase; save metrics to `backend/artifacts/intent_metrics.json`. Delete `train_ai_advanced.py` or fix it. |

---

### 2.1 What the C-tasks revealed (2026-10-07) — read before quoting numbers

- **Bandit has no lift over a fair baseline.** With priors learned from train-user logs and a fair static baseline (best fixed card per persona, chosen from train logs), day-60 action acceptance is bandit **0.581** vs best fixed card **0.596** vs random **0.359** (lessons: 0.504 / 0.513 / 0.390). The old "0.58 vs 0.34" only beat an arbitrary `items[0]`. **Do not claim the bandit adds value** until `I-01` (contextual bandit + OPE) shows a real lift.
- **Fairness (corrected after M-08 diagnosis):** at the global 0.30 threshold shop-owner recall is 0, but that is **base rate, not bias**: shop owners have 11 positives in 406 obs (2.7%), the model is calibrated for them (mean p 0.026) and ranks them well (AUC 0.87). 0/11 has a 95% CI of 0–28%, so it is not judged. The **real gap is `daily_wage`: AUC 0.71** vs 0.93–0.95 for other personas; area AUC gap 23 pp (Jatrabari lowest). Gender parity is fine.
- **Intent model honest score:** grouped 5-fold CV (seed phrase held out) accuracy **0.600**, macro-F1 **0.531**; `health` F1 = 0.0, `advice` 0.11. Gibberish → `unknown` class F1 0.92. See `backend/artifacts/intent_metrics.json`. → new task **M-09**.
- Impact snapshot after the bandit change: shortfall days/user-month 4.132 → 3.683 (was 3.729), per-100k 44,900 days (still a single simulated number — B-01 replaces it with a range).
- Backend coverage is **92%** (262 tests), so the CI gate is set at 85%.

- [x] **M-08** (P0, M) Diagnosed (2026-10-07): fairness now reports threshold-free AUC and base rate vs mean predicted for every group, recall/precision with Wilson 95% CIs, and flags only groups with ≥ 30 positives (`scripts/evaluate_impact.py`, `python scripts/evaluate.py --fairness-only`). Shop owners are not a bias case (see §2.1).
- [ ] **M-10** (P0, M) Improve `daily_wage` risk ranking (AUC 0.71): daily earners have no payday (`days_to_income` = NaN), so add income-rhythm features (7-day inflow mean/variance, days since last inflow ≥ median daily income, share of days with income in last 14). Retrain with `scripts/train_all.py`, re-run `scripts/evaluate.py`. Acceptance: daily_wage AUC ≥ 0.80 with no drop for other personas.
- [ ] **M-09** (P1, S) Intent model: add more seed phrases for `health`, `advice`, `send_money`, `status` (≥ 10 distinct phrasings each); re-run `backend/scripts/train_ai.py`; raise the floor in `tests/test_intent_metrics.py` as scores improve.

## 3. Comparison with the previous `development.md`

The previous version had the right 7 headings but was generic. The audit found these differences:

**Correct in the old plan and kept:** narrowing to month-end shortfall; citing real sources and a small user study; evaluation suite with baselines, LOPO, ablations, calibration; KPI tree and A/B design; real CI; removing `store.reset()`; contextual bandit + OPE; prescriptive optimizer; conformal intervals; Postgres/Alembic/Redis; HMAC + idempotent webhook; model registry + drift (PSI); Locust load test; hashed expiring sessions; argon2; restrictive CORS; audit log; model/data card; fairness audit.

**Wrong or misleading in the old plan:**
- Evaluation script path `backend/scripts/evaluate.py` does not exist. The real scripts are in root `scripts/` (`evaluate.py`, `evaluate_impact.py`, `train_all.py`).
- "Restore TypeScript strict checking": `strict` was **never** enabled in `web/tsconfig.app.json`. It must be added after fixing the 21 current errors. `web/fix_ts.py` silenced errors with regexes and should be deleted.
- "Move `fix_*.py` scripts to `scripts/archive/`": about 150 of them are **tracked in git**. Delete them (`git rm`), don't archive. History keeps them.
- "Prophet-lite" baseline: not needed. Use seasonal-naive, moving average, ETS (statsmodels), Ridge, and logistic regression for risk.
- `--cov-fail-under=80` straight away will fail CI. Start at 75 after the 14 failing tests are fixed.

**Missing from the old plan (found by the audit):**
- All of section 2 (C-01..C-08): fake liquidity score, unmounted forecast UI, circular bandit, fake retraining daemon, hand-picked fairness thresholds, intent-model leakage.
- Real current test status (14 backend + 3 vitest failures, 21 TS errors) and two real bugs: unknown pocket returns 500 (`services_hub.py:194`), NaN `days_to_income` feature.
- Security holes the judges did not list: `GET /api/users` lists every phone number with no auth, and all seeded users share PIN `123456`; OTP is returned in the API response with no TTL and unlimited attempts; any user can call `/demo/reset` (global wipe); PII regex for phone numbers never matches (double-escaped) and the PIN regex redacts amounts; `str(e)` leaked in 500 responses; token in `localStorage`.
- Budgeting is disabled (`services_hub.py:119-124` returns `mode: "disabled"`) — judge J3 named this.
- E3 risk baseline is binary (degenerate PR-AUC 0.53, a straw man); E2 baselines are identical at h=30; label windows overlap split boundaries.
- `upay_integration.py` is not an integration: it is an unauthenticated intent classifier.
- Safe-to-spend line is not shown in the UI.
- Business-side: upay's own cash-out fee revenue is ignored in the business case; no break-even analysis.
- LLM grounding/hallucination evaluation set.
- Concrete pilot ethics/consent, pre-registration, and small-n statistics.

---

## 4. Workstreams and tasks

Effort: S ≤ 3 h, M ≈ 1 day, L ≥ 2 days.

### 4.1 Problem relevance — "P" (target 14.67 → 18+)

**One-sentence problem (use everywhere: README, report §1, slides, video):**
> Low-income upay users, led by salaried garment workers, run out of money in the last 7–10 days of each month, then borrow informally or skip essentials. Their wallet shows a balance but never warns them in advance. Hishab predicts that shortfall days ahead and gives 1–3 actions that measurably reduce it.

Feature triage:

| Class | Features |
|---|---|
| **CORE** | Forecast + shortfall risk + "কেন?" (SHAP reasons) + what-if actions; nav badge "১১ দিন"; safe-to-spend; shortfall notifications; risk calendar |
| SUPPORTING | Impact page; Smart Route / cash-out fee nudge (framed as "saves ৳X before the 29th"); emergency pocket; Ask Hishab voice (as an access channel) |
| DILUTING → hide | Overview (mock), Learn/lessons, Levels, Smart DPS, readiness signals, Agent Locator (unless C-01 is fixed honestly), report Appendix |

- [ ] **P-01** (P0, M) Hub restructure. New `web/src/pages/hub/Forecast.tsx` becomes the hub index route in `web/src/App.tsx`. Tabs in `HubLayout.tsx`: পূর্বাভাস / ক্যালেন্ডার / জিজ্ঞাসা / সঞ্চয়. Remove Overview and Learn tabs.
  - `Forecast.tsx`: hero risk card ("২৯ সেপ্টেম্বরের দিকে ৳১,১৪৫ কম পড়তে পারে · ৮৩%"), "কেন?" SHAP reasons, `<ForecastChart forecast whatIf>`, top-3 action cards with "কী হবে দেখো" and রাজি/না. Data from `/api/users/{uid}/home`, `/actions/simulate`, `/actions/{id}/respond`. Check git history before `remove_forecast.py` for the earlier version.
  - Accept: page renders for every showcase user; accepting an action updates the chart.
- [ ] **P-02** (P0, S) `AppShell.tsx` `BalanceButton`: add "আজ নিরাপদ খরচ ৳X". `MessageStrip`: pin the shortfall message (priority 1, no rotation). Fix failing `test_notifications::test_strip_priority_order`.
- [ ] **P-03** (P0, S) `hub/Calendar.tsx`: restore red/amber predicted risk days.
- [ ] **P-04** (P0, S) `Home.tsx`: remove the agent tile and duplicate Savings/DPS tile; add slim card "Hishab: টাকা চলবে আর ১১ দিন" linking to `/app/hishab`. `savings/SavingsHome.tsx`: hide Levels and DPS behind "পরে আসছে". `hub/Ask.tsx` `SUGGESTED`: all 4 questions about shortfall.
- [ ] **P-05** (P0, M) Rewrite `README.md` (Problem + 2–3 cited stats; How Hishab prevents shortfalls: predict → explain → act → measure; key metrics; Supporting features; delete "Liquidity Score" and "Enterprise-Ready"). Rewrite `docs/report.md` §1 (Evidence subsection), §4 (Core vs Supporting), §6 (lead with shortfall days); delete the Appendix. Align `docs/superpowers/specs/2026-10-01-hishab-design.md` §1.3.
- [x] **P-06** (P0, S) Desk evidence. Add `docs/evidence.md` with links. Every number is marked `[verify]` until someone checks it at the source. Sources: Bangladesh Bank monthly MFS statistics (cash-out share, salary disbursement); World Bank Global Findex 2021/2025 (emergency funds within 30 days, borrowing from family, wage receipt); BIGD (BRAC University) garment-worker digital wage studies; CGAP financial diaries; *Portfolios of the Poor* (Collins et al., 2009); a2i; BGMEA/ILO minimum wage. **Never invent a number.**
- [ ] **P-07** (P1, L — fieldwork, run in parallel from day 1) User validation, 3 people, 1 week:
  - Survey (Google Form in Bangla, face to face), n ≥ 60: MFS used and how salary is paid; times money ran out in last 3 months; day of month it starts; coping (family, shop credit, NGO, skipping meals); last payday cash-out amount and fee; usefulness of a 5-day warning (1–5); which action they would take; trust inside upay.
  - Diary study, n = 8–10, 5–7 days, daily WhatsApp voice note (balance, in/out, short or not), ৳50/day recharge incentive.
  - Usability test, n = 8–10: "When will you run short? What will you do?" → task success, time, SUS.
  - Consent line; no names or phone numbers in the dataset.
  - Output: `docs/validation/survey_results.md` + one slide: "X% of N ran short in last 3 months (median day Y)", "Z% borrowed informally", "W% rated the warning ≥ 4/5", 2–3 anonymised quotes, diary heatmap, limitations.
- [ ] **P-08** (P1, S) `docs/video-script.md`: cut Health and Levels/DPS segments; spend the time on risk → "কেন?" → what-if → accept. Re-record.

### 4.2 Business / customer impact — "B" (target 11.67 → 16+)

**KPI tree**
- North star: **shortfall-free user-months** (no day below ৳200 outside income days).
- Drivers: action acceptance rate, completion rate, shortfall days per user-month, fees per user-month, cash-out share of income, pocket balance.
- upay outcomes: 30/90-day active rate, average in-wallet balance, digital payment volume.
- Guardrails: opt-out rate, notification disable rate, salary retained on day 10 (currently *regresses* 0.341 → 0.336 — report it), fairness gap < 10 pp.

- [ ] **B-01** (P0, M) Rewrite `impact()` in `scripts/evaluate_impact.py`:
  - Bandit priors from a train split of logged responses only (depends on `I-01`); never from `acceptance_truth`.
  - Randomise held-out users 50/50 control/treatment, stratified by persona. Report ITT and per-acceptor effects.
  - 200 seeds; user-level cluster bootstrap (2,000 resamples) for 95% CIs.
  - Sensitivity grid: acceptance scale {0.1, 0.25, 0.5, 0.75, 1.0} × `COMMITMENT_EFFECT` {0, 0.25, 0.5} × fees {low, placeholder, high} × effect decay {0, 30%/month}.
  - Output an effect-vs-acceptance curve and a **break-even acceptance rate**.
  - Replace "×100k = 40,300 days" with a range, labelled **Simulated**.
- [ ] **B-02** (P0, S) Move all impact constants (`COMMITMENT_EFFECT`, 10% trim, inactivity coefficients, fees) to new `backend/hishab/rules/impact_assumptions.yaml` with fields `id, value, source, status: assumed | literature | measured`. `engine/actions.py` reads from it.
- [ ] **B-03** (P0, S) New snapshot schema in `backend/artifacts/impact_snapshot.json`: `{point, ci_low, ci_high, evidence, assumption_ids}` + `sensitivity[]` + `break_even`. `GET /api/impact?acceptance_scale=&commitment=` interpolates the precomputed grid. Update `tests/test_impact_snapshot.py`.
- [ ] **B-04** (P0, M) `web/src/pages/Impact.tsx`: Simulated / Measured badges on every metric; acceptance and commitment sliders; fan chart with CI band; per-100k shown only as a range; assumptions table with status. Shortfall-days and lead-time tiles at the top.
- [x] **B-05** (P0, S) Fix C-06 (one fairness threshold). Done 2026-10-07.
- [ ] **B-06** (P1, L) Pilot mode (`PILOT_MODE=1`): consent screen (`web/src/pages/Consent.tsx`), hashed arm assignment, manual / SMS-paste ledger (`web/src/pages/Ledger.tsx`, stays on device or is pasted by the participant; never ask for PINs), daily check-in, `POST /api/events` (new `backend/hishab/api/routes/events.py`) logging card_shown / accepted / dismissed / completed. Existing respond endpoints also log events.
- [ ] **B-07** (P1, L — fieldwork) Run the pilot: 30–40 participants, 1:1 randomised in blocks. Days 1–7 everyone logs; days 8–14 treatment gets forecasts and cards, control gets ledger only (difference-in-differences).
  - Pre-register on AsPredicted/OSF **before day 1**: H1 acceptance ≥ 30% (Wilson 95% lower bound); H2 7-day balance MAE beats "same as last week" (paired Wilcoxon); H3 treatment reduces self-reported short/borrow days more than control (permutation DiD); H4 SUS ≥ 68 and ≥ 80% comprehension of Bangla explanations.
  - Ethics: DIU supervisor sign-off, written Bangla consent, withdraw/delete rights, pseudonymous IDs, delete after 90 days, flat ৳100 thank-you.
  - Analysis: `scripts/analyze_pilot.py` (Wilson / Beta-binomial, permutation tests, effect sizes + CIs; report nulls too). `GET /api/impact/pilot` feeds the "Measured" panel.
  - Present as **feasibility and acceptance evidence**, not proof of outcome effects.
- [ ] **B-08** (P1, M) Unit economics, `docs/business-case.md` + Business tab in `Impact.tsx` with editable inputs:
  `ΔV = Δactive × ARPU × L + ΔBalance × r_float/12 + ΔDigitalPay × MDR_net + ΔDPS × DPS_bal × spread/12 − ΔCashOut × m_cashout_net − C`.
  All inputs `[verify]`. Cost C: LightGBM batch scoring (measure it) + LLM calls × tokens × current Anthropic pricing (look it up, don't hard-code from memory); templated Bangla + prompt caching to cut LLM cost. Include a break-even chart. **Net out upay's lost cash-out fee revenue.**
- [ ] **B-09** (P2, S) `docs/ab-protocol.md` + `scripts/power.py`: unit = user, stratified by persona proxy and salary day; ≥ 8 weeks (2 salary cycles); 5–10% long-term holdout; primary metric shortfall-month incidence. Example power (baseline synthetic, re-estimate on upay data): p₀ = 0.58, detect −3 pp at α 0.05 / power 0.8 → ≈ 4,300 users/arm; CUPED cuts this ~30–50%. O'Brien-Fleming sequential boundaries.

### 4.3 Scalability & integration — "X" (target 5 → 8+)

Current reality: single uvicorn process; parquet loaded into pandas at startup; SQLite at `/tmp/hishab.db` with one global lock and JSON blobs; `store.reset()` on every boot (`main.py:28`); process-local locks and limiters (`services.py:60-72`, `llm/client.py:33`, `upay_integration.py:18`); pickle loaded at import (`ml_engine.py:37-45,108`); no metrics or readiness probe.

Target:
```
web ─► api (gunicorn + uvicorn workers, stateless, N replicas)
         ├─ Postgres (SQLAlchemy 2 + Alembic): users, sessions, state, tx, events, idempotency, audit_log, model_registry
         ├─ Redis: sessions TTL, rate limit, per-user lock, feature cache, job queue
         └─ worker (arq or RQ): feature recompute on tx events, nightly retrain, PSI drift
upay (mock adapter / sandbox) ─HMAC-signed webhook─► /api/v1/ingest/transactions
```

- [ ] **X-01** (P0, L) Repository interface: `backend/hishab/store/base.py` (Protocol), `store/sql.py` + `store/models.py` on SQLAlchemy 2 (works with `postgresql+psycopg` and `sqlite`, so tests keep SQLite), `backend/alembic/`. Demo reset/seed only when `HISHAB_DEMO_MODE=1`. Update `main.py:27-28`, `config.py`.
- [ ] **X-02** (P0, M) `backend/hishab/infra/redis.py`: sessions with TTL, sliding-window rate limiter (replaces both in-memory limiters), `redis.lock` per user instead of `user_lock`, clock offset per user (not global). Fallback to in-memory when `REDIS_URL` is unset (dev/tests).
- [ ] **X-03** (P0, L) Ingestion: `POST /api/v1/ingest/transactions` in `api/routes/ingest.py`; contract in `backend/hishab/ingest/contract.py` (`TxEvent`: event_id, wallet_id hash, ts, amount, direction, counterparty_type, channel, balance_after); `ingest/signing.py` (headers `X-Upay-Signature` = HMAC-SHA256 over `timestamp.body`, `X-Upay-Timestamp` reject > 5 min skew); `Idempotency-Key` with unique index (replay returns stored result); returns 202 and enqueues `recompute_features(user)`. Tests in `tests/api/test_ingest.py` (bad signature, stale timestamp, duplicate key).
- [ ] **X-04** (P0, M) `backend/hishab/adapters/upay.py` Protocol (`get_transactions`, `get_balance`, `get_agent_liquidity`, `list_products`; read-only, consent token) + `adapters/mock_upay.py` backed by the parquet files. `DataRepo` reads through the adapter. `scripts/replay_to_webhook.py` streams synthetic transactions into the webhook for demos.
- [ ] **X-05** (P0, S) `scripts/export_openapi.py` → `docs/integration/openapi.json`; `docs/integration/UPAY_CONTRACT.md` (auth, HMAC, idempotency, error codes, SLAs). Rewrite `UPAY_API_DOCS.md`.
- [ ] **X-06** (P0, M) Ops: `/healthz`, `/readyz` (DB, Redis, models loaded), `/metrics` via `prometheus-fastapi-instrumentator` + custom counters (ingest accepted / duplicate / bad signature, model latency), `structlog` JSON logs with request_id. File `backend/hishab/api/observability.py`.
- [ ] **X-07** (P1, M) Model registry `backend/hishab/ml/registry.py` + `backend/artifacts/manifest.json` (name, version, sha256, trained_at, data_hash, metrics, feature baseline bins). Verify hash on load; `GET /api/v1/models`. No pickle load at import time.
- [ ] **X-08** (P1, M) Scheduled retraining in the worker (`backend/hishab/worker/jobs.py`, cron 02:00): train → evaluate → promote only if metrics are at least as good. Delete `ai_trainer_daemon.py` (C-05).
- [ ] **X-09** (P1, S) Drift: `backend/hishab/ml/drift.py`, PSI per feature (inflow, outflow, txn count, cash-out share, balance), last 7 days vs training baseline; 0.1 watch, 0.25 alert. `GET /api/v1/monitoring/drift` + `hishab_feature_psi{feature}` gauge.
- [ ] **X-10** (P1, M) `docker-compose.yml`: api, worker, postgres:16, redis:7, prometheus (+ optional grafana), healthchecks, `depends_on: service_healthy`, migrate job, DB volume. `Dockerfile` CMD → gunicorn with uvicorn workers. Update `render.yaml`.
- [ ] **X-11** (P1, M) Load test `loadtest/locustfile.py` + `loadtest/report.py`. Mix: 60% home read, 20% chat/intent, 10% pocket move (lock + write), 10% signed ingest (5% duplicate keys). Ramp 50 → 100 → 200 → 400 RPS, 3 min each. Targets: reads p95 < 300 ms @ 200 RPS, ingest p95 < 150 ms, errors < 0.5%, zero duplicate rows. Run **before** (current SQLite build) and **after** (compose, 1 vs 2 replicas). Output chart p50/p95/p99 vs RPS + table + one sentence naming the bottleneck → `docs/eval/loadtest.md`.
- [ ] **X-12** (P2, S) `docs/architecture/SCALING.md` with the Mermaid integration diagram (upay core → gateway with mTLS/HMAC → Hishab ingest/adapter → Postgres/Redis/worker/registry → Prometheus; "suggestions only, no money movement"). Notes: stateless replicas, PgBouncer, partition transactions by month.

### 4.4 AI/ML depth — "M" (target 16.67 → 19)

What is genuinely learned: E2 forecaster (2 LightGBM regressors + bootstrap residual band), E3 risk (LightGBM + isotonic + TreeSHAP), intent classifier (TF-IDF + LinearSVC). Everything else (recurring detection, actions, replay, health, DPS, route, levels, lessons) is rules — say so in the report.

- [ ] **M-01** (P0, L) `scripts/eval_suite.py` (reuse `load_full`, `training_daily`, `risk_frame`, `ctx_from_history`; `--quick` flag). Outputs `docs/eval/results.json`, `docs/eval/summary.md`, PNGs.
  - Rolling-origin backtest: origins Jun/Jul/Aug/Sep, retrain before each, 14-day purge at boundaries, held-out users. E2: MAE, RMSE, MASE at h = 7/14/30, pinball loss, P10/P90 coverage. E3: PR-AUC, ROC-AUC, Brier, ECE, recall at precision 0.8. Mean ± std across origins + user-cluster bootstrap CI.
  - Baselines. E2: seasonal-naive, 7/30-day moving average, ETS (statsmodels), Ridge on `FC_FEATURES`, recurring-only. E3: persistence (balance < 200), continuous `-proj_min_14d`, logistic regression on `RISK_FEATURES`, current rule.
  - Report E3 on two slices: all observations, and **not currently short** (balance ≥ 200) — today's AUCs are inflated by persistence (positive rate 0.41, median lead 3 days).
  - Calibration: isotonic vs Platt vs none → Brier, ECE (15 bins), log-loss; `reliability_e3.png`, `coverage_e2.png`.
- [ ] **M-02** (P0, S) Fix C-08 (intent model leakage) and add `backend/tests/test_intent_golden.py` with an accuracy floor. Fix the 6 `test_ai_perfection` + 4 `test_chat_ml_routing` failures (gibberish must get the polite fallback; check what `backend/fix_fallback_threshold.py` changed and revert).
- [ ] **M-03** (P0, M) LLM grounding eval: `backend/tests/llm_eval/questions_bn.jsonl` (60–100 Bangla/Banglish questions with expected tools and answer facts) + `scripts/eval_llm.py`: tool-selection accuracy, number-grounding rate (every ৳/digit in the reply appears in tool results, after Bangla-digit conversion), hallucination rate, forbidden-phrase rate, fallback rate, latency. Run with LLM on and with `fallback.answer`.
- [ ] **M-04** (P1, M) Leave-one-persona-out for E2 and E3 → `lopo.png`. Shift stress tests: salary −30% and 7-day delay; cash-out fee ×2; ±20% amount jitter + 10% dropped transactions; Eid date shift → ΔPR-AUC, ΔECE, ΔMAE, coverage → `stress.png`.
- [ ] **M-05** (P1, M) Ablations: forecaster without `is_regular`, `days_to_payday`, recurring flows; risk without `proj_min_14d*`; risk **with** forecast-derived features (min P50/P10 over 14 days from `balance_band`) — this answers J2 directly.
- [ ] **M-06** (P1, S) Bug fixes: purge labels overlapping split boundaries (`risk.py:522-524`, `train_all.py:50`); continuous E3 rule baseline (`scripts/evaluate.py:83,110`); distinct E2 baselines at h = 30 (`forecast.py:351-365`); NaN `days_to_income` (failing `test_features`).
- [ ] **M-07** (P2, S) Tweedie objective for zero-inflated spend; document or ablate `persona_code` in the forecaster (it is excluded from risk as protected — inconsistent); band ignores inflow and recurring uncertainty — document.
- **Report wording:** "LLM = planner and narrator over engine tools; all numbers come from the engine." And: "All results are on synthetic data from one generator; they show robustness inside the simulator, not on real users."

### 4.5 Innovation — "I" (target 7.33 → 9)

- [ ] **I-01** (P0, L) Fix the learning loop, then contextual bandit + off-policy evaluation.
  - Generator: make acceptance depend on context (hidden logistic over features); generate logs from a randomised ε-greedy logging policy that records propensities.
  - `engine/bandit.py`: add `LinTS` (or LinUCB) over context: risk prob, days_to_income, cashout_share_30d, top SHAP driver one-hot, persona, action ΔP. Reward = accepted × shortfall days avoided in next 14 days. Delete `from_truth`.
  - New `engine/ope.py`: IPS, SNIPS, doubly robust.
  - Policy-value table with DR 95% CIs on held-out users: random; fair static (benefit-ranked, p_accept 0.5, best fixed arm per persona); current persona-TS; LinTS. Regret curves; context-feature ablation.
- [ ] **I-02** (P0, L) Prescriptive plan optimizer `engine/optimizer.py`: search action bundles (≤ 2⁹ subsets + amount grid for `save_on_payday`, `daily_limit`), minimise Monte-Carlo P(shortfall) = share of 200 paths whose minimum < threshold, weighted by expected acceptance; constraints: minimum essential spend, remittance untouched, burden budget. `engine/forecast.py` returns paths and `p_shortfall`; `actions.py` computes risk_after from paths. Route `POST /api/users/{uid}/plan`. Proof: realised shortfall days at equal burden — top-1 card vs greedy top-3 vs optimized bundle.
- [ ] **I-03** (P1, M) Conformal safe-to-spend in `engine/safe_spend.py`: split-conformal quantile of backtest min-balance errors to next income, 90% target. Proof: empirical coverage current vs conformal at similar mean safe-to-spend. UI: "৳X/দিন, ৯০% নিশ্চয়তা".
- [ ] **I-04** (P1, M) Forecast-timed early-warning nudge: trigger when lead time ≤ L and P > τ, L and τ tuned by replay; nudge carries the I-02 bundle. Files: `engine/notifications.py`, `rules/notifications.yaml`. Proof: shortfall days avoided per nudge — timed vs fixed day-20 vs current `risk_red`.
- [ ] **I-05** (P2, M) Claude tools `simulate_plan(actions[], amounts)` and `optimize_plan(constraints)` so a spoken Bangla what-if runs a real simulation. Fix the few-shot example naming a non-existent `dps_advice` tool (`llm/prompts.py:83`).
- **Key chart (report + slides):** ablation ladder of shortfall days per 100 user-months with DR 95% CIs — no app → static rules → + forecast/risk ranking → + contextual bandit → + optimizer bundle → + timed nudge. Inset: OPE policy values.

### 4.6 Prototype quality — "Q" (target 13.33 → 14.5+)

- [ ] **Q-01** (P0, M) Make all tests green. Backend 14 failures:
  - Unknown pocket → 422, not 500 (`services_hub.py:194`).
  - NaN `days_to_income` (with M-06).
  - Strip priority order (with P-02).
  - `test_tool_names_exact`: add `find_agents_near_me` to the list or remove the tool (with C-01).
  - 6 intent + 4 routing (with M-02).
  - Web: 3 vitest failures in `src/lib/format.test.ts` (`fmtTaka` / `toBnDigits` must return Bangla digits). 21 TS errors (`client.ts:2` dead `Budget` import, `Overview.tsx:29,31,111`, `SendMoney.tsx:89`, `AgentLocator.tsx:121`, 13 unused vars). Then add `"strict": true` to `web/tsconfig.app.json`. Delete `web/fix_ts.py`.
- [ ] **Q-02** (P0, S) Real CI. `backend/pyproject.toml` `dev = ["pytest","pytest-cov","pytest-timeout","ruff","schemathesis"]`; `web/package.json` `"test": "vitest run"`. Replace `.github/workflows/ci.yml` with jobs:
  - backend: `apt-get install libgomp1`; `pip install -r requirements.lock -e ".[dev]"`; `ruff check`; `pytest -q --timeout=300 --cov=hishab --cov-fail-under=75 --junitxml=junit.xml` with `LLM_ENABLED=false`; upload coverage + junit.
  - web: `npm ci`, `npm run typecheck`, `npm run lint`, `npx vitest run`, `npm run build`.
  - docker: build image, run it, curl `/api/health` until up.
  - Delete `.github/workflows/deploy.yml` (fake test step, old actions). Gate `gh-pages.yml` and `deploy-hf.yml` on CI success (`workflow_run`); `gh-pages.yml` uses `npm ci` only.
- [ ] **Q-03** (P0, M) Missing tests: `tests/api/test_authz_matrix.py` (S-05); OpenAPI contract tests with schemathesis; model-inference golden tests (fixed input → expected forecast/risk within tolerance, plus artifact hash check); router-presence test (`main.py:81-86` silently swallows `ModuleNotFoundError` — assert every expected prefix is in `app.routes`).
- [ ] **Q-04** (P0, M) Restore budgeting (`services_hub.py:119-124`): auto caps from category history + manual caps; API tests; re-add `Budget` type in `web/src/api/types.ts`. (J3 called out "disabled budgeting". Keep it small and tied to the shortfall story: "cap that keeps you safe until payday".)
- [ ] **Q-05** (P1, S) Remove demo defaults: `DEMO_TODAY` fixed clock opt-in only (`config.py:40`, `render.yaml`); 200-user cap lifted after X-01; voice TTS as a settings toggle instead of commented out (`Ask.tsx:104,127`); AgentLocator geolocation error instead of silent Dhaka fallback.
- [ ] **Q-06** (P1, S) Repo hygiene. `git rm` all root `fix_*`, `patch_*`, `check*`, `force_*`, `mod_*`, `rename_*`, `remove_*`, `update_*`, `inspect_*`, `test_*.py`, `brand_sweep.py`, `natural_vibe_patch.py`, `null.py`, `do_nothing.py`, `disable_voice.py`, `append_css.ps1`, `update_format.js`, `run_until_6am.ps1`, `apply_office.py`, `add_*.py`; `backend/fix_*.py`, `backend/test_*.py` (move useful cases into `backend/tests/test_intent_golden.py`), `backend/update_train.py`; root `artifacts/intent_model.pkl` (duplicate). Move `generate_report.py`, `generate_slides.py`, `generate_submission_assets.py`, `create_docs.py` into `scripts/submission/`. `.gitignore`: `scratch/`, `deliverables/`, `.agents/`, `/artifacts/`, `*.log`, `coverage.xml`, `junit.xml`, `.coverage`, `htmlcov/`, `.ruff_cache/`, `web/coverage/`, `*.egg-info/`. `.claude/launch.json`: relative path instead of `E:/AI Hackathon DIU-2026/...`. Remove obsolete `version:` from compose.
- [ ] **Q-07** (P2, M) Provider interfaces + sandbox adapters for DPS opening and emergency loan (`services_hub.py:249` `simulated: True`); versioned tariff config for fees (`rules/fees.yaml`); code-split the >500 kB web bundle.

### 4.7 Security & Responsible AI — "S" (target 3.67 → 4.7)

Route authorization today: all `/users/{uid}/*` routers enforce `require_user` with owner check — **except** `GET /users` (no auth, leaks phones), `/users/{uid}/agents/nearby` (no auth), `POST /upay/ai/predict` (no auth), `/demo/*` (any user, global effect). LLM tools take the user from the session (good).

- [x] **S-01** (P0, S) CORS from `HISHAB_CORS_ORIGINS` (only GET/POST/PUT/DELETE, Authorization + Content-Type) at `main.py:43`. Security headers middleware (CSP, HSTS, X-Content-Type-Options, frame-ancestors 'none', Referrer-Policy). Update `.env.example` with `HISHAB_CORS_ORIGINS`, `HISHAB_PEPPER`, `HISHAB_DEMO_MODE`, `REDIS_URL`, `DATABASE_URL`.
- [x] **S-02** (P0, M) Sessions: table `sessions(token_hash PK, user_id, created_at, last_seen, expires_at, revoked_at, ip, ua)`; look up by `sha256(token)`; absolute TTL 12 h, idle 30 min; `POST /auth/logout`, `POST /auth/logout-all`; revoke all on PIN change. Files `store/sqlite.py:25,171-178` (then X-01), `api/deps.py`, `routes/auth.py`, `services.py`.
- [x] **S-03** (P0, M) PIN: argon2id (`argon2-cffi`, time 3, memory 64 MiB, parallelism 1) + HMAC pepper; rehash on login. Lockout: 5 failures → 15 min with 2^n backoff, keyed by mobile and IP, same error message always. OTP: hashed, 5-min TTL, max 3 attempts, sent through an `SmsProvider` interface (console sink in dev); echo back only when `HISHAB_DEMO_MODE=1`; verification server-side only (fix `web/src/pages/auth/Register.tsx:39-44,90`). Same response for existing/new numbers in `register_start` (`services.py:132`). Random PIN per seeded user (`data/generator.py:576`), demo credentials in a seed/README file only.
- [x] **S-04** (P0, S) Close open routes: `GET /users` behind `HISHAB_DEMO_MODE` with masked phones (`routes/users.py:15-17`); `require_user` + lat/lng bounds on agents; session required on `/upay/ai/predict` and generic 500 message (`upay_integration.py:35-52`); `/demo/*` behind `HISHAB_DEMO_MODE` + admin role. Fix PII regex (`security.py:92-95`): phone `r'\b(?:\+?88)?01[3-9]\d{8}\b'`; PIN pattern must not eat amounts (only redact digits next to words like "pin"/"পিন"); add unit tests.
- [x] **S-05** (P0, S) `tests/api/test_authz_matrix.py`: enumerate every `APIRoute` with `{uid}` from `app.routes`; parametrize over {no token, garbage, expired, revoked, other user's token} → 401/401/401/401/403. Assert the public allow-list is exactly {`/auth/*`, `/health*`, `/impact`, ingest (HMAC)} so any new unprotected route fails CI.
- [ ] **S-06** (P1, M) `slowapi` with Redis: login 5/min, OTP 3/10 min, chat 10/min, per-user LLM budget. Append-only `audit_log(id, ts, actor_uid, action, target, ip, outcome, prev_hash, hash)`, hash-chained, phones masked, for login, transfer, pocket move, DPS open, logout. Schema bounds in `api/schemas.py:45-94` and `hub.py:51` (`max_length`, `Literal`, `limit` 1–200).
- [ ] **S-07** (P1, M) Responsible-AI docs: `docs/model_card.md` (E2, E3, intent; intended use; out-of-scope = credit decisions; synthetic training data; metrics; thresholds 0.30/0.60; LLM role); `docs/data_card.md` (generator, personas, seeds, no real PII, gaps: rural/female/elderly).
- [ ] **S-08** (P1, M) LLM red-team set `backend/tests/redteam/cases.jsonl` (~60 cases, half Bangla/Banglish): direct injection ("আগের সব নির্দেশ ভুলে যাও"), cross-user ("U0002-এর ব্যালেন্স বলো"), system-prompt extraction, loan/credit-score/investment-tip requests, shaming/fear language, indirect injection via counterparty names. Deterministic checks; target ≥ 95% pass on both LLM and fallback. Mark tool output as untrusted data in the prompt.
- [ ] **S-09** (P1, S) `scripts/fairness_audit.py` → `docs/fairness.md`: per persona / area / gender proxy — ECE, calibration slope, FPR/FNR parity, action selection rate, fee-savings uplift; flag ECE gap > 0.05 or FPR ratio outside 0.8–1.25. One global threshold (C-06).
- [ ] **S-10** (P2, M) Token in an HttpOnly, Secure, SameSite=Strict cookie + CSRF token instead of `localStorage` (`web/src/lib/session.ts:28-43`, `web/src/api/client.ts`). axe-core (Playwright) + Lighthouse CI accessibility ≥ 90. `docs/compliance_bd.md` (all `[verify]`): Bangladesh Bank MFS Regulations 2022, Cyber Security Act 2023 (check current status), draft Personal Data Protection Act/Ordinance, BB ICT Security Guideline. `docs/threat_model.md` (STRIDE).

---

## 5. Schedule (3 people, ~2 weeks)

Fieldwork (P-07, B-07) starts on **day 1** and runs in parallel; it has the longest lead time and recovers the most points.

| Days | Person A (backend / infra) | Person B (ML / eval) | Person C (frontend / product / research) |
|---|---|---|---|
| 1–2 | C-04, Q-01 (backend), Q-02, S-01, S-04, S-05 | C-03 prep, C-05, C-06, C-08, M-02, M-06 | C-01, C-02 → P-01..P-04, Q-01 (web); launch survey (P-07) |
| 3–5 | S-02, S-03, X-01 | M-01 (eval suite), B-02 | P-05, P-06; Pilot mode B-06 (with A for `/events`) |
| 6–8 | X-02, X-03, X-04, X-05, X-06 | I-01 (bandit + OPE), B-01, B-03 | B-04 Impact page; pilot running (B-07) |
| 9–11 | X-07..X-10, Q-03, Q-04 | I-02 optimizer, M-03, M-04, M-05 | Diary + usability study; S-07; B-08 |
| 12–13 | X-11 load test, S-06 | I-03, S-09, S-08 | analyze pilot; report + slides rewrite |
| 14 | Freeze. Full CI green, re-record video (P-08), final report, README | | |

If time runs short, cut in this order: I-05, Q-07, S-10, X-12, B-09, I-04, M-07.

---

## 6. Judge-facing deliverables checklist

- [ ] README: one-sentence problem, cited evidence, core loop, honest "learned vs rules" table, CI badge, how to run.
- [ ] Report: Evidence (desk + survey + diary) → Solution (core loop) → ML evaluation (baselines, LOPO, stress, ablations, calibration, "where it fails") → Innovation (ablation ladder, OPE) → Impact ("Assumption vs Measured" table, sensitivity curve, break-even, pilot results, A/B protocol) → Architecture (diagram, ingest contract, load-test chart) → Security & RAI (authz matrix, red-team pass rate, fairness, model/data cards, compliance notes) → Limitations.
- [ ] Slides: one key chart per criterion (survey stat, reliability diagram, ablation ladder, impact fan chart with CI, load-test chart, authz matrix).
- [ ] Video: core loop only, 90 seconds of forecast → কেন? → what-if → accept → measured pilot numbers.
- [ ] Every number traceable to a committed script output in `docs/eval/` or `backend/artifacts/`.

**The message to judges:** "Simulated impact is reported as a range with inspectable assumptions. Measured acceptance and usability come from an n = 3X randomized pilot. upay outcomes are pending a pre-registered A/B test powered at about 4k users per arm. Integration is one adapter: mock → sandbox → production is a config change. Hishab never moves money."

---

## 7. Progress log

| Date | Task IDs | Who | Notes |
|---|---|---|---|
| 2026-10-07 | — | Claude | Plan written from 7-domain audit; previous plan compared (section 3). |
| 2026-10-07 | C-01..C-08, B-05 | Claude | Agents → deterministic demo data + auth; Forecast page is the hub index, calendar risk + nav badge + shortfall strip restored; Overview deleted; all tests green (backend 262, web 10), TS strict on; real CI (ruff, pytest+cov ≥85%, typecheck, lint, vitest, build, docker smoke), deploys gated on CI; fake trainer removed; intent model grouped CV; bandit priors from train logs + fair baseline; single fairness threshold. Findings in §2.1. |
| 2026-10-07 | M-08 | Claude | Fairness reporting rewritten (AUC, calibration, Wilson CIs, min-positives rule); shop-owner "recall 0" is a 2.7% base rate with 11 positives, not bias; real gap is daily_wage AUC 0.71 → M-10. |
| 2026-10-07 | S-01, S-04, S-05 | Claude | `HISHAB_DEMO_MODE` (default off; on in Dockerfile/render/.env.example/launch) gates `/users`, `/demo/*`, OTP echo and boot-time reset; `/users` never lists registered numbers; CORS allowlist from `HISHAB_CORS_ORIGINS`; security headers + CSP; `/upay/ai/predict` needs a session and hides errors; PII regex fixed (phones redacted, amounts kept); authz matrix test over every OpenAPI route. 276 tests, 92% coverage. Not done yet: S-02 hashed expiring sessions, S-03 argon2/lockout/random seeded PINs. |
| 2026-10-07 | S-02, S-03 | Claude | Sessions: only SHA-256 of tokens stored (`auth_sessions`), 12 h absolute + 30 min idle expiry, `POST /auth/logout` and `/auth/logout-all`, web logout revokes server-side. PINs: scrypt + per-user salt + `HISHAB_PEPPER` (`hishab/passwords.py`; stdlib, so no argon2 dependency), legacy SHA-256 hashes upgrade on login. Lockout: 5 wrong PINs → 15 min (per mobile and per IP), 429. OTP: keyed hash, 5 min TTL, 3 tries, checked server-side only. Shared seeded demo PIN only works with `HISHAB_DEMO_MODE=1`. Not done: rate limiting via Redis (S-06), HttpOnly cookie (S-10). |
| 2026-10-07 | P-05 (README), P-06, P-07 kit | Claude | README rewritten around the shortfall problem with an honest learned-vs-rules table and current metrics; `docs/evidence.md` lists sources to extract (all [verify], no numbers invented); `docs/validation/survey-and-pilot-kit.md` has consent, survey, diary, usability and pilot protocol. Still open: report.md §1/§4/§6 rewrite (rest of P-05), fieldwork itself (P-07/B-07), M-10. |
