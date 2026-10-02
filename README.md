---
title: Hishab upay prototype
emoji: 💰
colorFrom: yellow
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Hishab (হিসাব) — AI cash-flow copilot for upay

> **Prototype — not the official upay app.** All data is synthetic. No real customer data, no real money, no real PINs.

AI DEV FEST 2026 · AI Hackathon (DIU CPC × upay) · **Track 03: AI-driven financial management for low-income customers.**

---

## 1. Project overview

Many upay customers are garment workers, daily-wage earners, small shop owners and students. Their income is irregular, and money often runs out before the next payday. They then cash out at a fee, borrow informally, or go without.

**Hishab** is an **AI feature + API that lives inside the existing upay app**. It:

- forecasts the next 30 days of balance,
- warns early when money is likely to run short ("২৯ তারিখের দিকে প্রায় ৳১,১৪৫ কম পড়তে পারে"),
- explains why,
- recommends concrete actions (and shows the what-if), then learns which nudges each customer actually accepts,
- helps them save (pockets, paisa saving, Eid planner, a levelled path to DPS, Smart DPS sizing),
- routes transfers through the cheapest path,
- answers questions in Bangla by text or voice.

The prototype is a mobile-first web app that recreates a refined **upay-style wallet shell** and shows exactly where Hishab plugs in. The lead persona is **Rina**, a garment worker in Gazipur.

## 2. Features and how AI is used

| # | Feature (where in upay) | AI / logic behind it |
|---|---|---|
| E1 | Recurring income and bill detection | Interval and amount clustering over 12 months of transactions |
| E2 | **30-day balance forecast** with a P10–P90 band (Hishab hub) | LightGBM in/out-flow models + bootstrap residual band |
| E3 | **Shortfall risk** green/amber/red, with "কেন?" drivers | Calibrated LightGBM classifier (isotonic) + TreeSHAP reasons in Bangla |
| E5 | **Action cards** with what-if redraw of the forecast | Rule catalogue × model re-scoring of risk and fees per action |
| E6 | **AI category chips** at send/pay | Counterparty history + amount model (top-3) |
| E7 | **Smart Route** (universal-wallet money map) | Cheapest-path search over a fee graph (fees are placeholders) |
| E8 | **Eid planner** | Last-Eid excess spend estimate vs expected bonus → weekly saving |
| E9 | **Learning nudges** | Thompson-sampling contextual bandit over actions and lessons |
| E11 | **আজ নিরাপদ খরচ** under the balance + daily budget | Forecast P10 minus committed outflows before next income |
| E12 | **Health coach**: emergency days, cash dependency, shortfall-free months, habits, monthly report | Indicators + habit mining |
| E13 | **Literacy lessons** (Bangla, 60 s) | Bandit-ranked lessons tied to the user's situation |
| E14 | **Readiness signals** (educational, not a credit score) | Five consistency signals with a disclaimer |
| E15 | **সাম্প্রতিক পেমেন্ট** one-tap repeat row | Recency × frequency × due-date ranking |
| E16 | **সঞ্চয় লেভেল** (5/10/15/30 days → Level 1 "DPS-এর জন্য প্রস্তুত") + **Smart DPS** on upay's DPS screen | Streak rules + forecast-checked safe installment (≤ 25% of income) |
| E17 | **জরুরি টাকা** helper | Own pockets first; the DPS-backed loan cap is a fixed bank rule. The AI never approves, sizes or promises a loan |
| F6 | **Ask Hishab** chat in Bangla, with voice | Claude (`claude-opus-5-5`) with strict tool use over the engine; template fallback when offline. Numbers come only from tools |
| F9 | **Notifications + daily message strip**, incl. re-engagement after inactivity | Priority rules over engine outputs |
| F7 | **Impact page** (judges) | Month-by-month replay of held-out users, with and without Hishab |

Guardrails are separate from ML (`backend/hishab/rules/*.yaml`):

- risk thresholds,
- action limits,
- the 25% DPS income cap,
- forbidden phrases (for example "loan offer", "credit score", "ঋণ পাবেন"), post-filtered on every LLM answer.

## 3. How upay integrates Hishab

Hishab is designed to be adopted by upay with almost no change to its app:

| # | Location in upay | What Hishab adds |
|---|---|---|
| I1 | Bottom nav (replaces "আরো", which moves to the header) | **হিসাব** tab with a live status badge (e.g. red "১১ দিন") |
| I2 | Yellow header | One-line daily message strip (risk, bill due, safe-to-spend, level progress) |
| I3 | ব্যালেন্স reveal | "আজ নিরাপদ খরচ ৳…" under the balance |
| I4 | Home | **সাম্প্রতিক পেমেন্ট** row; the long উপায় পেমেন্ট section collapses into one icon next to এনপিএসবি |
| I5 | সেন্ড মানি / এনপিএসবি / ফান্ড ট্রান্সফার | Smart Route + AI category |
| I6 | ক্যাশ আউট | One fee-saving nudge with "তবুও cash-out" |
| I7 | মেক পেমেন্ট / পে বিল / মোবাইল রিচার্জ | AI category chip (automatic budget tracking) |
| I8 | সঞ্চয় | আমার পকেট, সঞ্চয় লেভেল, জরুরি টাকা above upay's DPS; Smart DPS on the DPS-opening screen |
| I9 | Bell | Personalised notification centre, incl. re-engagement |

**API:** everything the UI shows comes from a JSON API under `/api`. Interactive docs are at **`/docs`** (OpenAPI), e.g. `GET /api/users/{id}/home`, `POST /api/users/{id}/route`, `POST /api/users/{id}/chat`. Every `/api/users/{id}/…` call needs the session token from `/api/auth/login` (or `/register/verify`) as `Authorization: Bearer <token>`, and a token only opens its own user. upay's app can call these endpoints, or embed the engine as a service.

## 4. Tech stack

- **Backend:** Python 3.11, FastAPI, Pydantic v2, pandas, NumPy, LightGBM, scikit-learn, PyYAML, Anthropic Python SDK, SQLite (demo state).
- **Frontend:** React 19 + TypeScript, Vite, Tailwind CSS v4, Recharts, React Router. Hind Siliguri + Inter fonts.
- **LLM:** Claude `claude-opus-5-5` via the Anthropic API, with strict tool use, a 25 s budget, rate limiting, and a template fallback.
- **Deploy:** one Docker container (Node build stage → Python runtime) on Hugging Face Spaces.
- **CI:** GitHub Actions (backend pytest; web typecheck, Vitest and build).

## 5. Requirements

- Python **3.11** (and [uv](https://docs.astral.sh/uv/), or pip)
- Node.js **22** + npm
- Optional: an Anthropic API key. Without one, chat uses grounded template answers.
- Optional: Docker

## 6. Installation and setup

```bash
git clone https://github.com/shahfahim/UPAY-Optimized.git
cd UPAY-Optimized

# Python environment (from the repo root)
uv venv backend/.venv --python 3.11
source backend/.venv/bin/activate        # Windows: backend\.venv\Scripts\activate
uv pip install -e "backend[dev]"         # or: pip install -e "backend[dev]"

# Optional: regenerate data, retrain and evaluate (the trained artifacts and the serving subset are already committed)
python scripts/generate_data.py          # 2,000 synthetic users × 12 months, seed 42
python scripts/train_all.py              # forecaster, risk model, calibration, bandit priors
python scripts/evaluate.py               # writes reports/metrics.md and reports/metrics.json
python scripts/evaluate_impact.py        # writes backend/artifacts/impact_snapshot.json

# Frontend
cd web && npm ci && cd ..
```

## 7. Environment variables

Copy `.env.example` to `.env`. Never commit `.env`.

| Variable | Default | Meaning |
|---|---|---|
| `ANTHROPIC_API_KEY` | *(empty)* | Enables Claude for chat. Leave empty to use template answers |
| `LLM_ENABLED` | `auto` | `auto` = on only when a key is set; `true`/`false` to force |
| `LLM_MODEL` | `claude-opus-5-5` | Claude model ID |
| `DEMO_TODAY` | `2026-09-18` | The demo's "today" (Rina's mid-month moment) |
| `SEED` | `42` | Data generator seed |
| `HISHAB_DB_PATH` | system temp `hishab.db` | SQLite file for demo state |
| `HISHAB_WEB_DIST` | `web/dist` | Built frontend served by FastAPI |

## 8. Run and build

```bash
# Backend API on http://localhost:8000 (API docs at /docs)
uvicorn hishab.api.main:create_app --factory --reload --port 8000

# Frontend dev server on http://localhost:5173 (proxies /api to :8000)
cd web && npm run dev

# Production build: FastAPI serves web/dist at http://localhost:8000
cd web && npm run build

# Docker (same image as the live deployment)
docker build -t hishab .
docker run -p 7860:7860 -e ANTHROPIC_API_KEY=... hishab   # http://localhost:7860
```

**Demo access:** on the login screen, tap a user under "Demo user হিসেবে ঢুকুন". The demo PIN for seeded users is **123456**; it is not a real credential.

| User | Persona | Story |
|---|---|---|
| U0001 রিনা আক্তার | Garment worker, Gazipur | Red risk: short around 29 Sep; cash-out remittance habit |
| U0002 জসিম উদ্দিন | Daily-wage earner | Irregular income |
| U0003 শাহনাজ পারভীন | Shop owner | Mixed personal and business money |
| U0004 তানভীর হাসান | Student | Allowance-based |
| U0005 সুমি খাতুন | Garment worker (saver) | Green, savings level 2, Smart DPS safe amount |

In **আরো** (header menu), you can:

- jump time forward 7/14/30 days (60 days in total at most),
- reset the demo,
- switch users,
- open the Impact page.

## 9. Live deployment

**Live URL:** `https://huggingface.co/spaces/<HF_SPACE>`. This is pending: the Space is created by the team (see below). Once the GitHub secret is set, every push to `main` deploys automatically.

To enable deployment:

1. Create a Hugging Face Space with SDK **Docker**.
2. In the Space settings, add the secret `ANTHROPIC_API_KEY`.
3. In this GitHub repo, add the secret `HF_TOKEN` (a write token) and the variable `HF_SPACE` (e.g. `username/hishab`).
4. Push to `main`. `.github/workflows/deploy-hf.yml` pushes the repo to the Space, which builds the `Dockerfile`.

## 10. Testing

```bash
pytest backend/tests -q            # ~190 backend tests: engine, guardrails, API, LLM fallback, safety
cd web && npm run typecheck && npm test -- --run && npm run build
```

CI runs the same commands on every push. The tests pin the safety rules:

- no forbidden loan or credit phrasing,
- tools never take a user ID from the model,
- prompt-injection attempts stay scoped,
- invalid amounts return 422 (never 500).

## 11. Other configuration and assumptions

- **Fees** (`backend/hishab/rules/fees.yaml`): every number is a placeholder assumption for the demo, not a real upay tariff. The UI says so.
- **Eid dates** (`rules/eid_dates.yaml`): approximate, for planning only.
- **DPS options and caps** (`rules/dps.yaml`, `rules/emergency.yaml`): demo values. The loan cap is a bank rule, never computed by AI. The bank makes every decision.
- **Synthetic data:** 2,000 users × 12 months (Oct 2025 – Sep 2026), seed 42. The 300-user serving subset is committed. Personas, injected patterns, labels and limitations are in [`docs/synthetic-data.md`](docs/synthetic-data.md).
- **Metrics:** [`reports/metrics.md`](reports/metrics.md). Impact simulation: the **Impact** page (`/impact`) and [`docs/report.md`](docs/report.md).
- **Regenerating data:** run the four scripts in §6 in order; artifacts land in `backend/artifacts/`.

## Documents

- [Project report](docs/report.md)
- [Demo video script](docs/video-script.md)
- [Demo checklist](docs/demo-checklist.md)
- [Design spec](docs/superpowers/specs/2026-10-01-hishab-design.md)
- [Implementation plan](docs/superpowers/plans/2026-10-02-hishab.md)

## Responsible AI (summary)

- The AI never approves, denies, sizes or promises loans. Readiness signals are educational, not a credit score.
- Every number in a chat answer comes from engine tools. If the LLM is slow, failing or unsafe, a grounded template answer is used.
- No real personal data; the real upay logo is not used; login warns "Demo — আসল PIN দেবেন না". Demo PINs are stored only as salted hashes and never logged.
- Fairness gaps across personas and areas are measured and shown on the Impact page.
