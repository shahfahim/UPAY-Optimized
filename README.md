<div align="center">
  <br/>
  <h1>হিসাব AI (Hishab AI) — an upay cash-flow copilot</h1>
  <p><b>Predict and prevent month-end liquidity shortfalls for low-income MFS users (AI DEV FEST 2026 • Track 3)</b></p>

  [![CI](https://github.com/shahfahim/UPAY-Optimized/actions/workflows/ci.yml/badge.svg)](https://github.com/shahfahim/UPAY-Optimized/actions/workflows/ci.yml)

  <a href="https://youtu.be/EUe-zCwZJgk?si=CNCy9P8Kg2qeqbGK">
    <img src="https://img.shields.io/badge/▶_WATCH_THE_DEMO-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch on YouTube" />
  </a>
</div>

---

## The problem

Low-income upay users, led by salaried garment workers, run out of money in the last 7–10 days of the month, then borrow informally or skip essentials. Their wallet shows a balance but never warns them in advance.

Evidence we cite and are validating is listed in [docs/evidence.md](docs/evidence.md). Our own user survey and pilot kit is in [docs/validation/](docs/validation/).

## How Hishab prevents shortfalls

1. **Predict.** A LightGBM forecaster projects the next 30 days of balance with a P10–P90 band. A calibrated LightGBM risk model gives the probability of falling below ৳200 in the next 14 days.
2. **Explain.** "কেন?" shows the top TreeSHAP drivers in plain Bangla.
3. **Act.** Up to three actions (save on payday, daily limit, pay by wallet instead of cash-out, send home by NPSB), each with a what-if line on the forecast chart. The user accepts or dismisses; nothing moves money automatically.
4. **Measure.** Shortfall days, fees, and acceptance are tracked on the Impact page, labelled as simulated until pilot data exists.

## What is learned and what is rules

| Component | How it works | Held-out result (synthetic test users) |
|---|---|---|
| 30-day balance forecast | LightGBM (daily in/out flows) + bootstrap residual band | MAE day 14: ৳1,640 vs ৳2,084 for "same as last month"; P10–P90 coverage 0.77 |
| 14-day shortfall risk | LightGBM + isotonic calibration, TreeSHAP reasons | PR-AUC 0.914, ROC-AUC 0.944, Brier 0.092 |
| Bangla/Banglish intent (offline chat fallback) | TF-IDF char n-grams + LinearSVC | Grouped CV accuracy 0.60 (phrasings never seen in training) |
| Action ranking | Thompson-sampling bandit over a fixed action catalogue | No lift yet over the best fixed card (0.58 vs 0.60); contextual bandit is planned |
| Actions, what-if transforms, fees, recurring bills | Deterministic rules (`backend/hishab/rules/*.yaml`) | — |
| Chat with Claude | Claude calls read-only, user-scoped tools; every number comes from the engine | — |
| Agent locator | **Demo sample data**, no liquidity model | — |

All numbers come from `scripts/evaluate.py` on synthetic data from one generator ([docs/synthetic-data.md](docs/synthetic-data.md)). They show the models work inside the simulator, not on real users. Fairness by persona, gender and area is on the Impact page; the known gap is daily-wage workers (risk AUC 0.71 vs 0.93–0.95 for others).

## Responsible AI and security

- Suggestions only; no lending or credit decisions, no money movement.
- Hashed, expiring sessions; scrypt-hashed PINs with lockout; OTP limits; CORS allowlist and security headers; an authorization test covers every API route.
- Demo-only features (seeded users, time travel, on-screen OTP) need `HISHAB_DEMO_MODE=1`.

## Tech stack

React 19 + TypeScript (strict) + Vite + Tailwind, FastAPI + Pydantic v2, LightGBM, scikit-learn, Anthropic Claude API. CI runs ruff, pytest (coverage ≥ 85%), typecheck, lint, vitest, build and a Docker smoke test.

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.lock -e ".[dev]"
HISHAB_DEMO_MODE=1 python -m uvicorn hishab.api.main:create_app --factory --port 8000 --reload
```

```bash
cd web
npm install
npm run dev
```

Open `http://localhost:5173`. Plan and status for Phase 2: [development.md](development.md).

---
Team RageBait: Fahim Shahryar, Hasibul Hasib, Abu Nabil Md. Masrur.
*Hackathon prototype, not an official upay app. Uses synthetic data only.*
