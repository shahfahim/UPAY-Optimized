# Hishab AI: what we changed after Phase 1 feedback

Short notes for the judges, one block per criterion. **Done** means the change is merged and tested. **Open** means it has not been done yet; we list it rather than claim it.

---

## Problem relevance (feedback: diluted, advisory layer, no real evidence)

**Done**
- The app is now built around one problem: predicting and preventing month-end cash shortfalls. The Hishab tab opens on a **Forecast** page with four parts:
  - Risk card: "you may run short by ৳X around date Y".
  - "কেন?" (why) reasons.
  - 30-day balance chart with an uncertainty band.
  - What-if action cards the user can accept or dismiss.
- Restored the shortfall signals on the calendar (red and amber days), the "N দিন" countdown on the nav bar, and the shortfall message in the header.
- Removed a mock Overview page and the Learn tab from the main navigation.
- Rewrote the README around a one-sentence problem statement.
- `docs/evidence.md` lists the public sources we are extracting figures from: Bangladesh Bank MFS statistics, World Bank Findex, BIGD, CGAP, and *Portfolios of the Poor*. No figure is quoted until it is checked at the source.
- `docs/validation/` holds a ready survey (n ≥ 60), diary study, usability test, and consent text in Bangla.

**Open**
- Fieldwork: the survey and diary have not been run yet.

## AI/ML depth (feedback: robustness, baselines, calibration; some "AI" is rules)

**Done**
- **Honest labelling.** The README has a table of what is learned and what is rules:
  - Learned: the LightGBM forecaster, the calibrated LightGBM risk model, and the intent classifier.
  - Rules: the action catalogue, what-if transforms, and fees.
  - Demo data, not AI: the agent locator. Its "AI liquidity score" was random sample data; we removed the claim, and the AI badge is gone from the agent and NPSB tiles.
- **Intent model leakage fixed.** Typo variants of the same phrase were in both train and test. Evaluation is now grouped by phrase: accuracy is **0.60**, not the earlier near-1.0.
- **Bandit made fair.**
  - Its priors used to come from the simulator's own answer key. They now come only from logged responses of training users.
  - The baseline is now the best fixed card per persona.
  - Result: **no lift yet** (0.58 vs 0.60). We report this and no longer claim the bandit adds value.
- **Fairness reporting.**
  - One alert threshold for every group (before, groups had hand-picked thresholds).
  - Per-group AUC, base rate vs mean prediction, and 95% CIs.
  - Recall and precision gaps are judged only for groups with ≥ 30 positive cases.
  - Real gap found: daily-wage workers (risk AUC 0.71 vs 0.93–0.95 for the other personas).

**In progress**
- Income-rhythm features for daily earners, who have no payday, to close the daily-wage gap. The model is being retrained now.

**Open**
- Rolling-origin backtest, leave-one-persona-out test, ablations, and a reliability diagram.

## Business / customer impact (feedback: all simulated, single extrapolated number)

**Done**
- Every impact figure is labelled **Simulated** on the Impact page and in the README.
- The bandit priors no longer come from the same table the impact replay draws from.
- `docs/validation/survey-and-pilot-kit.md` has a pre-registered pilot design:
  - 30–40 users, randomised 1:1.
  - Four hypotheses: acceptance, forecast error, short/borrow days, usability.

**In progress**
- 95% bootstrap CIs, plus a sensitivity curve at 25%, 50% and 100% of the assumed acceptance rates. This replaces the single "per 100k" number with a range.

**Open**
- Running the pilot, a unit-economics model, and the production A/B protocol.

## Prototype quality (feedback: CI only printed "Tests passed!", demo-grade parts)

**Done**
- Real CI on every push and pull request:
  - Backend: ruff, then pytest with coverage (must stay ≥ 85%; currently **92%**, 286 tests).
  - Web: strict TypeScript, lint, unit tests, build.
  - Docker build plus a smoke test.
  - Deploys run only after CI passes.
- Fixed 14 failing backend tests, 3 failing web tests and 21 TypeScript errors that the old CI hid.
- Real bugs fixed:
  - Missing safe-to-spend chat intent.
  - Crash on irregular earners' payday feature.
  - Unknown savings pocket returned 500.
  - "500tk bkash e pathabo" returned "invalid amount".
- Removed a fake "overnight trainer" that never trained a model.

**Open**
- Budgeting is still switched off.

## Innovation (feedback: learning component not shown to add value)

**Done**
- We measured the learning component honestly: today's bandit does **not** beat a fixed best card. The claim is withdrawn.

**Open**
- A contextual bandit with off-policy evaluation.
- An action-bundle optimiser that minimises the forecast probability of a shortfall.
- Conformal safe-to-spend.

## Scalability & integration (feedback: SQLite, reset on start, no upay integration)

**Done**
- State is no longer wiped on every start, unless the server runs in demo mode.
- Demo-only features (seeded user list, time travel, global reset, OTP shown on screen) need `HISHAB_DEMO_MODE=1`.

**Open**
- Postgres and Redis.
- A signed, idempotent transaction-ingestion webhook and upay adapter.
- Model registry, retraining, and drift monitoring.
- Load test.

## Responsible AI & security (feedback: CORS `*`, tokens never expire, open routes)

**Done**
- **CORS and headers.** CORS is an allowlist instead of `*`. Security headers and a Content-Security-Policy are on every response.
- **Sessions.**
  - Tokens are stored only as hashes.
  - A login expires after 12 hours, or after 30 minutes idle.
  - Logout and "log out everywhere" revoke tokens on the server.
- **PINs.**
  - Stored as scrypt hashes with a per-user salt and a server secret.
  - 5 wrong PINs lock the number for 15 minutes.
  - The shared demo PIN works only in demo mode.
- **OTP.** Stored as a hash, expires after 5 minutes, allows 3 tries, and is checked only on the server.
- **Open routes closed.**
  - The agent route and the intent-prediction route now require login.
  - The user list never shows registered numbers.
  - Error messages no longer leak internals.
- **Personal data.** The PII filter now really redacts phone numbers; before, it never matched them and it deleted money amounts by mistake.
- **Authorization test.** An automated test calls every API route with no token, a fake token, and another user's token. Adding a new unprotected route fails CI.

**Open**
- Shared rate limiting (Redis), an audit log, a model card and data card, and an LLM red-team set.
