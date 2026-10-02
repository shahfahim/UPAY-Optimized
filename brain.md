# brain.md — Hishab (হিসাব) project brain

What this project is, how it fits together, the rules it must never break, and where to look before changing
something. It's for anyone (or any AI session) picking the project up cold. For setup and run commands the
README is the source of truth. This file explains *why* the code looks the way it does.

---

## 1. One-paragraph summary

**Hishab is an AI cash-flow copilot prototype for the upay mobile wallet (Bangladesh)**, built for AI DEV FEST
2026 (DIU CPC × upay), Track 03: AI-driven financial management for low-income customers. It forecasts the next
30 days of a user's balance and warns early when money will run short ("২৯ তারিখের দিকে প্রায় ৳১,১৪৫ কম পড়তে পারে").
It explains why, suggests concrete actions with a what-if redraw, and helps the user save (pockets, paisa
saving, Eid planner, savings levels, Smart DPS). It also picks the cheapest money route and answers questions in
Bangla by text or voice. It is shown inside a recreated **upay-style wallet shell**, because the pitch is "a
feature + API that plugs into the existing upay app", not a new app. **All data is synthetic.** The lead
persona is **Rina (U0001)**, a garment worker in Gazipur on ৳12,500/month who sends money home by cash-out
and runs short in the last week of the month.

## 2. Mental model

```
 synthetic data (parquet, 300 users)      demo state (SQLite)
  backend/data/serving/*.parquet          state, sim_tx, sessions, notifications, …
            │                                        │
            └──────────── build_ctx(uid) ────────────┘
                              │   UserCtx = user + merged transactions + today + balance + UserState
                              ▼
              engine/ (pure-ish functions over UserCtx + trained Models)
              recurring → forecast → risk → actions / safe_spend / levels / …
                              │
                 rules/*.yaml (guardrails, fees, copy) — kept separate from ML
                              │
              services.py + services_hub.py  (Hishab facade: one method per API resource → JSON dicts)
                     │                                   │
          api/routes/* (FastAPI, /api)          llm/ (Claude tool loop; tools call the same facade)
                     │
          web/ (React SPA, upay-style shell) — served by FastAPI from web/dist in production
```

Things to keep in mind:
- **There is no real ledger.** A user's history is the committed parquet (seeded users) or `extra_tx`
  (registered users), plus `sim_tx` rows the demo writes when the user sends, pays or moves money.
  **Balance = `balance_after` of the latest transaction.** Every money move writes a row with a new
  `balance_after`.
- **"Today" is a demo clock:** `DEMO_TODAY` (default `2026-09-18`) + `clock_offset` (time travel of 7/14/30 days,
  at most 60 days in total). Each history is cut off at today.
- **The demo state is thrown away on purpose.** `store.reset()` runs on every server start, and `POST /api/demo/reset`
  clears everything except seeded users' sessions.
- **The engine computes, the LLM explains.** Every number the chat shows comes from a tool that calls the
  engine. The model never decides money matters.

## 3. Repository map

| Path | What lives there |
|---|---|
| `backend/hishab/api/main.py` | `create_app()` factory, exception handlers, router mounting, SPA file serving |
| `backend/hishab/api/deps.py` | Auth dependencies: `require_session` (any logged-in user), `require_user` (token must own `{uid}`) |
| `backend/hishab/api/routes/` | `auth`, `users`, `hub`, `savings`, `flows`, `chat`, `demo`, `impact`: thin wrappers over the facade |
| `backend/hishab/api/schemas.py` | Pydantic request bodies (amounts accept `float \| str`; the engine re-validates) |
| `backend/hishab/services.py` | `Hishab` facade: auth, home, shell, notifications, actions, chat, demo controls, locks |
| `backend/hishab/services_hub.py` | `HubMixin`: health, lessons, calendar, budget, savings, pockets, DPS, emergency, send, route, history, impact; `@locked` decorator |
| `backend/hishab/engine/` | The AI and logic modules (§5) |
| `backend/hishab/rules/*.yaml` | Guardrails, fees, actions copy, DPS/emergency caps, levels, lessons, notifications, Eid dates, readiness |
| `backend/hishab/llm/` | `client.py` (tool loop, limits, fallback), `tools.py` (14 read-only tools), `prompts.py`, `fallback.py` (template answers) |
| `backend/hishab/store/sqlite.py` | `Store`: demo state in SQLite (`state`, `sim_tx`, `responses`, `categories`, `notifications`, `meta`, `sessions`, `extra_users`, `extra_tx`) |
| `backend/hishab/data/` | Synthetic data generator, persona params, labels, leakage-safe splits, parquet loader |
| `backend/hishab/errors.py` | `UserError`: a `ValueError` whose (Bangla) message may be shown to the user |
| `backend/artifacts/` | Trained models (LightGBM text dumps, calibration, residuals, bandit priors), `impact_snapshot.json` |
| `backend/data/serving/` | Committed 300-user parquet subset the live app reads (`backend/data/full/` is gitignored) |
| `backend/tests/` | ~209 pytest tests; `tests/api/` has the HTTP-level tests (see §10) |
| `backend/requirements.lock` | Pinned runtime dependencies (uv, universal), used by Docker, CI and the README |
| `scripts/` | `generate_data.py` → `train_all.py` → `evaluate.py` (+ `evaluate_impact.py`) |
| `web/src/` | React 19 + TS + Vite + Tailwind v4 app (§8) |
| `docs/` | `report.md` (project report), `synthetic-data.md`, `video-script.md`, `demo-checklist.md`, design spec and implementation plan under `docs/superpowers/` |
| `reports/metrics.{md,json}` | Model metrics on the held-out split |
| `Dockerfile` | Node build stage → Python 3.11 runtime, one uvicorn process on port 7860 |
| `.github/workflows/` | `ci.yml` (pytest; web typecheck, Vitest, build), `deploy-hf.yml` (push `main` to a Hugging Face Space) |

## 4. Request lifecycle (example: `POST /api/users/U0001/send`)

1. `routes/flows.py` router has `Depends(require_user)`: the `Authorization: Bearer <token>` header is looked up
   in `sessions`. No/invalid token → **401**; token of another user → **403**.
2. The Pydantic `SendIn` body is parsed.
3. `Hishab.send()` is decorated with `@locked` → takes the per-user `RLock`, so read-balance → check → write
   cannot interleave with another request for the same user.
4. `validate.amount()` (finite, > 0, ≤ ৳10,00,000) → `build_ctx()` → fee from Smart Route (`engine/route.py`) →
   balance check (`InsufficientFunds` → 400) → category (user's choice, or `suggest_category`) → at most one nudge
   → `_sim()` writes a `sim_tx` row with the new `balance_after` → paisa sweep (`apply_paisa`) may write a
   `pocket_in` row → `save_state`.
5. Exceptions map to HTTP in `api/main.py`: `UserNotFound` 404, `UserError` 422 (message shown),
   `InsufficientFunds` 400, `RateLimited` 429, `PermissionError` 401 (bad PIN), any other `ValueError` → logged + generic
   500, Pydantic errors 422 "তথ্য সঠিক নয়".

## 5. Engine modules (`backend/hishab/engine/`)

IDs (E1, E2, …, F6, I1–I9) come from the design spec and are used across code, docs and tests.

| ID | Module | What it does | Method |
|---|---|---|---|
| E1 | `recurring.py` | Detect salary, rent, remittance, bills, DPS; `next_income` | Interval + amount clustering |
| E2 | `forecast.py` | 30-day balance forecast with a P10–P90 band | LightGBM daily in/out-flow models + recurring events; 200 bootstrap residual paths. Training and serving share `_DayState` |
| E3 | `risk.py` | P(shortfall within 14 days) → green/amber/red, with "কেন?" drivers | LightGBM + isotonic calibration + TreeSHAP; `rule_baseline` for comparison |
| E5 | `actions.py` | Ranked action cards with a what-if | Rule catalogue (`rules/actions.yaml`) × re-scored forecast and risk; guardrail check; bandit ranking |
| E6 | `category.py` | Top-3 category for a draft payment | User's confirmed label → history → rules/amount |
| E7 | `route.py` | Cheapest path to send money; costly-habit detection | Path search over the `rules/fees.yaml` fee graph (**fees are placeholders**) |
| E8 | `eid.py`, `goals.py` | Eid weekly saving plan; goal feasibility | Last-Eid excess spend vs bonus; bootstrapped monthly surpluses |
| E9 | `bandit.py` | Learns which nudges and lessons each persona accepts | Thompson sampling, Beta(α, β) per (persona, item), priors from training |
| E11 | `safe_spend.py` | "আজ নিরাপদ খরচ" and the break-even daily budget | Forecast P10 minus committed outflows before next income |
| E12 | `health.py` | Emergency days, cash dependency, shortfall-free months, habits, monthly report | Indicators + habit mining |
| E13 | `lessons.py` | 60-second Bangla lessons filled with the user's own numbers | Behaviour triggers + bandit ranking |
| E14 | `readiness.py` | Five educational consistency signals | **Not a credit score.** Inputs never include persona, gender, area or age |
| E15 | `shortcuts.py` | "সাম্প্রতিক পেমেন্ট" row | Recency × frequency × due date |
| E16 | `levels.py`, `dps.py` | Savings levels 0–3 (5/10/15/30-day streaks); Smart DPS safe installment | Streak rules; forecast-checked installment ≤ 25% of income |
| E17 | `emergency.py` | Emergency money options | Own pockets first; DPS-backed loan cap is a fixed bank rule; AI only checks repayment affordability |
| F9 | `notifications.py` | Notification triggers (caps, opt-out, re-engagement) + header message strip (I2) | Priority rules over engine outputs |
| — | `savings.py` | Paisa saving: sweep the 0.xx fraction into a pocket; pauses at amber/red | Deterministic |
| — | `replay.py` | Month replay with/without Hishab for the Impact page | Re-runs actual flows with action transforms |
| — | `features.py` | Shared feature set; the **same code** builds training rows and live features | Prevents train/serve skew |
| — | `context.py` | `UserCtx`, `build_ctx`, default state (pockets/DPS inferred from history) | — |
| — | `models.py` | Loads `backend/artifacts/` into a `Models` bundle | — |
| — | `text.py` | Bangla digits and Indian grouping (`১,৫০,০০০`), category names | — |

## 6. Rules and guardrails (`backend/hishab/rules/`)

Business rules live in YAML, **separate from ML**. Change behaviour there before touching code.

- `guardrails.yaml`: risk thresholds (amber ≥ 0.30, red ≥ 0.60), shortfall threshold ৳200, essential buffer ৳200,
  essentials (rent, family support, health, education: **never** suggested for cutting), trimmable categories,
  `max_action_cards: 3`, `max_nudges_per_flow: 1`, `max_amount: 1000000`, **forbidden phrases**
  ("loan offer", "credit score", "approved", "you qualify", "ঋণ পাবেন", "অনুমোদিত", …).
- `actions.yaml`: `save_on_payday`, `split_remittance`, `digital_pay_instead_of_cashout`, `cheaper_route`,
  `pause_paisa_saving`, `trim_discretionary`, `dps_ready`, `eid_weekly_saving`, `daily_limit`.
- `fees.yaml`: cash-out 1.85%, NPSB 0.5% (min ৳5, max ৳50), all **placeholders, not real upay tariffs**.
- `dps.yaml` / `emergency.yaml`: DPS monthly options and tenures, 25% income cap, loan rule (demo values).
- `levels.yaml`: milestones 5/10/15, Level 1 at 30 days (3 missed days allowed), Level 2 (3 shortfall-free months +
  15 emergency days), Level 3 (3 on-time installments). **Levels never block any upay service.**
- `lessons.yaml`, `notifications.yaml`, `readiness.yaml`, `eid_dates.yaml` (approximate dates).

## 7. LLM layer (`backend/hishab/llm/`)

- **Model:** `LLM_MODEL` (default `claude-opus-5-5`) via the Anthropic Python SDK, `client.beta.messages.create`,
  `output_config={"effort": "low"}`, server-side refusal fallback (`betas=["server-side-fallback-2026-07-01"]`,
  `fallbacks="default"`), `tool_choice: auto`, `max_tokens` 4000.
- **Tools:** 14 strict, read-only tools (`tools.py`). `run_tool` always uses the **session user's** `uid` and drops any
  `user_id` the model sends. Tool results are capped at 8,000 characters.
- **Limits:** message ≤ 500 characters; 25 s total budget; ≤ 4 rounds; **10 chats/min per user**; **30 Claude
  calls/min across all users** (`LLM_CALLS_PER_MINUTE`). Past the global cap, chat answers from templates instead of
  erroring.
- **Safety:** if the answer contains a forbidden phrase, or the model refuses, times out or errors, the reply is
  replaced by `fallback.answer()` (grounded templates). `stop_reason == "refusal"` → fallback. Responses report
  `ai: true/false` and `used_tools`.
- **Off switch:** `LLM_ENABLED=auto` means on only when `ANTHROPIC_API_KEY` is set. Without a key the app works fully on
  templates.

## 8. Frontend (`web/src/`)

- **Stack:** React 19, TypeScript, Vite 8, Tailwind v4, Recharts, React Router 7, Vitest, oxlint. Fonts: Hind Siliguri + Inter.
- **API client:** `api/client.ts`. Every call goes to `/api…` and sends `Authorization: Bearer <token>` from
  `lib/session.ts` (localStorage key `hishab.session`). On 401/403 for a non-`/auth/` call it clears the session and
  sends the user to `/login`.
- **Routes** (`App.tsx`): `/` splash, `/welcome`, `/login`, `/register`, `/impact` (for judges, public), and under
  `/app` (needs a session): `home`, `account`, `history`, `notifications`, `more`, `payments`,
  `hishab` (overview, `budget`, `calendar`, `learn`, `ask`), `hishab/health`, `savings` (+ `pockets`, `levels`,
  `emergency`, `dps`), flows `send`, `cashout`, `npsb`, `transfer`, `pay`.
- **Shell:** `components/AppShell.tsx` (yellow header, message strip, bottom nav with the হিসাব badge). `ForecastChart`,
  `LevelPath`, `PinPad`, `flow.tsx` (shared send/pay flow pieces), `ui.tsx`.
- **i18n:** `i18n.tsx` gives `L(bn, en)`; Bangla is the default, with an English toggle. Voice input uses browser
  speech recognition (`lib/voice.ts`, `bn-BD`).
- **Demo access:** the login page lists demo users; seeded users' PIN is **123456** (public, demo only). "Switch demo
  user" in **আরো** logs in for real with that PIN.
- **Dev:** `npm run dev` proxies `/api` to `localhost:8000` (`vite.config.ts`).

## 9. Data and ML pipeline

- `scripts/generate_data.py`: 2,000 users × 12 months (2025-10-01 → 2026-09-30), seed 42, five personas
  (garment 45%, daily-wage 20%, shop owner 20%, student 15%). Injected patterns (rent, remittance channel, Eid bonus
  and festival spending, health shocks, DPS over-commitment, savers, inactivity hazard) are documented in
  `docs/synthetic-data.md`. Writes `data/full/` (gitignored) and a 300-user `data/serving/` subset (committed).
- `scripts/train_all.py`: forecaster, risk model + calibration, residuals, bandit priors → `backend/artifacts/`.
  Splits (`data/splits.py`): 15% of users held out; months 1–9 train, 10 validation, 11–12 test; showcase users stay
  in train.
- `scripts/evaluate.py` (+ `evaluate_impact.py`): writes `reports/metrics.*` and `artifacts/impact_snapshot.json`.

**Headline metrics** (held-out, synthetic; `reports/metrics.md`):
- E2 MAE: ৳1,640 at day 14 and ৳2,569 at day 30 (baselines ৳2,084 / ৳3,056); band coverage 0.77 / 0.81.
- E3: PR-AUC 0.912 (rule baseline 0.53); precision 0.81, recall 0.89 at amber+; median lead time 6 days for new
  shortfalls.
- E6: top-3 accuracy 0.912. E8: Eid MAE ৳1,846 vs ৳4,309 baseline.
- E9: action acceptance 0.58 with the bandit vs 0.34 static.
- **Impact simulation** (per user-month, baseline → with Hishab):
  - shortfall days 4.13 → 3.73
  - fees ৳132.9 → ৳127.3
  - cash dependency 0.391 → 0.355
  - shortfall-free months 0.42 → 0.45
  - salary kept on day 10: 0.341 → 0.336 (no gain; report it honestly)

These numbers show the pipeline works on data whose patterns we injected; they don't show real-world accuracy.
Always say so.

## 10. Invariants: do not break these

1. **No loan or credit language or decisions.** The AI never approves, denies, sizes or promises a loan. Readiness is
   educational, not a score. Forbidden phrases are post-filtered on every LLM answer, and tests pin this.
2. **Numbers in chat come only from tools.** Tools are scoped server-side to the session user; never take a
   `user_id` from the model.
3. **Never suggest cutting essentials** (rent, family support, health, education), never push paid products, never
   discourage withdrawing one's own savings. Pocket withdrawals are limited only by the pocket balance.
4. **Every `/api/users/{uid}/…` route needs `Depends(require_user)`**, and new demo or global mutations need
   `require_session`. Public routes: `/api/users`, `/api/health`, `/api/impact`, `/api/auth/*`.
5. **Anything that reads a balance or state, checks it, then writes must run under `self.user_lock(uid)`**
   (use `@locked`). The locks are in-process: keep **one uvicorn worker** or move to DB-level locking.
6. **User-facing errors raise `UserError("<Bangla message>")`.** A plain `ValueError` is treated as a bug: it is
   logged and returns a generic 500. Bad input must give 422, never 500.
7. **Amounts go through `engine/validate.amount`** (finite, > 0, ≤ max). Pydantic bodies accept strings on purpose.
8. **Training and serving share feature code** (`features.py`, forecast `_DayState`). Don't fork them.
9. **Rules stay in YAML; fees are placeholders.** The UI labels fees as assumptions.
10. **Synthetic data only.** No real upay data, logo or PINs. The login screen warns "Demo — আসল PIN দেবেন না".
    Registered PINs are stored as SHA-256 with one fixed app-wide prefix (`hishab-demo:`). That's demo-grade, not a
    real password hash: use a per-user salted KDF before any real use.

## 11. Testing and CI

- `pytest backend/tests -q` (about 209 tests). Fixtures in `tests/conftest.py` generate a 20-user dataset and train
  tiny models once per session.
- `tests/api/conftest.py`: `client` is an **`AuthedClient`** that creates a session for the `{uid}` in the path (U0001
  for `/api/demo/…`) unless the test sends its own `Authorization`. `anon` sends no token; use it for auth tests.
- Notable suites: `test_api_auth.py` (401/403, demo controls, registration cap, parallel verify),
  `test_api_concurrency.py` (parallel sends and withdrawals; these fail without the locks), `test_api_errors.py`,
  `test_llm.py` (tool loop, injection scoping, refusal and timeout fallback, global LLM cap), guardrail/rules tests.
- Web: `npm run typecheck && npm test -- --run && npm run build`; `npm run lint` (oxlint; CI doesn't run it).
- CI (`.github/workflows/ci.yml`) installs from `backend/requirements.lock`. To update pins:
  `uv pip compile backend/pyproject.toml --universal --python-version 3.11 -o backend/requirements.lock`.

## 12. Run, deploy, configure

- Dev: `uvicorn hishab.api.main:create_app --factory --reload --port 8000` (from `backend/`) + `cd web && npm run dev`.
- Production: `docker build -t hishab . && docker run -p 7860:7860 -e ANTHROPIC_API_KEY=… hishab`.
- Deploy: every push to `main` → `deploy-hf.yml` force-pushes to the Hugging Face Space in `HF_SPACE` (needs the repo
  secret `HF_TOKEN`; skipped otherwise). The Space needs its own `ANTHROPIC_API_KEY` secret.
- Environment variables: `ANTHROPIC_API_KEY`, `LLM_ENABLED` (auto/true/false), `LLM_MODEL`, `DEMO_TODAY`, `SEED`,
  `HISHAB_DB_PATH`, `HISHAB_WEB_DIST`, `HISHAB_DATA_DIR`, `HISHAB_ARTIFACTS_DIR`.

## 13. Demo cast

| User | Persona | Story |
|---|---|---|
| U0001 রিনা আক্তার | Garment worker, Gazipur | Red risk, short around 25–29 Sep; sends money home by cash-out (fee habit); Eid overspender |
| U0002 জসিম উদ্দিন | Daily-wage earner | Irregular income |
| U0003 শাহনাজ পারভীন | Shop owner | Personal and business money mixed |
| U0004 তানভীর হাসান | Student | Allowance-based |
| U0005 সুমি খাতুন | Garment worker (saver) | Green, savings level 2, Smart DPS suggests a safe amount |

Phones for seeded users are `017` + 8-digit user number (U0001 → `01700000001`). Registered users get IDs
`N0001…` (at most 200), with a year of generated history, and are wiped by demo reset.

## 14. Gotchas and known limits

- **Shared demo clock:** time travel and reset affect every visitor. They now need a login, but any logged-in user
  can still move the clock for everyone.
- **Restarting the server clears all state** (`/tmp/hishab.db` in Docker), including sessions. The web client handles
  this by sending users back to login.
- **The OTP is returned in the register response** (`demo: true`); there is no SMS. Fine for a demo, not for production.
- **The forecast is the expensive call.** `home`, `shell` and `calendar` each run the core models; LLM tools reuse one
  `cache` per chat answer, so `home` is computed at most once per question.
- **`load_rules` is `lru_cache`d** and returns shared dicts. Never mutate the result.
- **The JS bundle is about 800 kB** (one chunk); route-level code splitting would help.
- **`.claude/launch.json`** points at a local Windows venv path. It's personal and unused in CI or Docker.
- **Impact is model-based simulation**, not measured outcomes. Salary kept on day 10 doesn't improve; say so.

## 15. Where to look first

| If you want to… | Start at |
|---|---|
| change what a screen shows | the page in `web/src/pages/…` → `api/client.ts` → the matching route in `backend/hishab/api/routes/` → the facade method |
| change advice or wording | `backend/hishab/rules/*.yaml` |
| change a number the engine produces | the engine module in §5, and its test in `backend/tests/test_<module>.py` |
| add an endpoint | route (with `require_user`) → facade method (with `@locked` if it writes) → `web/src/api/client.ts` + `types.ts` → test in `backend/tests/api/` |
| add a chat capability | new tool in `llm/tools.py` (`strict`, no `user_id`) + `run_tool` branch + fallback template + `test_llm.py` |
| retrain or re-evaluate | `scripts/` in order; artifacts land in `backend/artifacts/` |
| understand design intent | `docs/superpowers/specs/2026-10-01-hishab-design.md` (feature IDs, guardrails, §11 limitations) |
