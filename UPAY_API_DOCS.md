# Hishab AI: UPAY Integration API

> Prototype using **synthetic data only**. The model classifies what the user wants. It never approves, sizes or promises a loan.

## Endpoint

`POST /api/upay/ai/predict`  ·  `Content-Type: application/json`  ·  no auth (demo only; add an API key before any real deployment)

### Request
```json
{ "query": "maa ke tk pathabo kishe" }
```

### Response (200)
```json
{ "intent": "route_planner", "confidence": 0.849, "extracted_entities": {} }
```

| Field | Meaning |
|---|---|
| `intent` | One of: `status`, `advice`, `goal`, `send_money`, `cashout`, `route_planner`, `emergency`, `savings`, `health`, `balance` |
| `confidence` | 0–1 calibrated probability. Treat **< 0.5** as "not sure" and ask the user to rephrase |
| `extracted_entities` | `{"amount": <int>}` when a taka amount is present (supports `1,500`, `2k`, Bangla digits `৫০০`) |

Errors: `503` if the model file is missing (run `python scripts/train_ai.py`), `422` if `query` is missing.

## Verified examples (actual output)

| Query | intent | confidence | entities |
|---|---|---|---|
| `maa ke tk pathabo kishe` | route_planner | 0.849 | – |
| `tour er jnno 5000 tk jomabo` | goal | 0.934 | amount 5000 |
| `করিমকে ৫০০ টাকা পাঠাও` | send_money | 0.615 | amount 500 |
| `imargency dhar lagbe` | emergency | 0.919 | – |

## cURL
```bash
curl -X POST "http://<HOST>:8000/api/upay/ai/predict" \
     -H "Content-Type: application/json" \
     -d '{"query": "tour er jnno 5000 tk jomabo"}'
```
On the same Wi-Fi as the demo laptop, `<HOST>` is `10.183.97.33`. For UPAY to reach it from outside, deploy with the included `Dockerfile` / `docker-compose.yml`.

## Postman
Method `POST` → URL `http://<HOST>:8000/api/upay/ai/predict` → Body → raw → JSON → `{"query": "cashout fi koto"}`.

## Retraining
```bash
cd backend
python scripts/train_ai.py              # prints held-out report, saves artifacts/intent_model.pkl
python -m pytest tests/test_ai_perfection.py
```
