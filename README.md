# 🚀 হিসাব AI (Hishab AI) — An upay Cash-flow Copilot
**Prototype for AI DEV FEST 2026 · AI Hackathon (DIU CPC × upay)**

**Hishab AI** is an intelligent, voice-enabled financial copilot designed specifically for low-income Mobile Financial Service (MFS) users in Bangladesh. Built as a prototype for the **upay** ecosystem, it acts as a proactive guide to help users understand their spending, predict shortfalls, plan savings, and improve financial literacy—all in native Bangla.

---

## 🔴 Live Demo (Hackathon Prototype)
🔗 **[Test the Live App Here](https://hishab-ai-demo.loca.lt)**

> **⚠️ IMPORTANT FOR EVALUATORS:** 
> When accessing the live demo, please ensure you allow the following permissions:
> 1. 🎤 **Microphone (Voice) Permission:** Required to interact with the AI assistant using your voice in Bangla.
> 2. 📍 **Location Permission:** Required for the "Find Nearby Agent" (এজেন্ট খুঁজুন) feature to calculate distances and agent liquidity based on your real-time position.

---

## 🌟 Core Features Built for the Hackathon

* 🎙️ **Inclusive Financial Assistant:** Fully functional in Bangla with Voice-to-Text and Text-to-Speech capabilities. Designed with a highly simplified UX for maximum accessibility.
* 🧠 **AI Financial Health Coach & Spending Companion:** Uses LLM integration (Claude) to explain spending behaviors, cash dependency, and identify unusual spending patterns in plain Bangla.
* 📈 **Cash-Flow Forecasting:** Powered by **LightGBM & Scikit-learn**, it predicts short-term inflows, outflows, and liquidity pressure, visualizing them in intuitive, interactive charts.
* 🎯 **Personal Savings & Goal Copilot:** Turns user goals (e.g., Eid shopping, emergencies) into realistic, cash-flow-backed savings plans.
* 📍 **Smart Agent Locator:** Uses Geolocation to find nearby agents, displaying their "AI Liquidity Score" to ensure they have enough cash for withdrawals.
* 📚 **Financial Literacy Personalizer:** Adapts educational guidance based on a user’s demonstrated behavior and transaction history rather than generic content.
* 🛡️ **Responsible Credit Readiness:** Provides explainable signals to help customers understand how their financial behavior affects future eligibility—without making autonomous lending decisions (Strict Responsible AI compliance).

---

## 🛠️ Enterprise-Ready Technology Stack

### Frontend (`web/`)
* **Framework:** React 19, TypeScript, Vite
* **Styling:** Tailwind CSS v4 (Mobile-first, 375px optimized upay-wallet layout)
* **Data Visualization:** Recharts (Dynamic Bar/Area charts)

### Backend (`backend/`)
* **API Framework:** Python 3.11, FastAPI (Microservice Architecture)
* **Validation:** Pydantic v2 (Strict Input/Output validation & auto-generated Swagger UI)
* **Machine Learning:** LightGBM, Scikit-learn, Pandas, NumPy
* **LLM Integration:** Anthropic API (`claude-opus-5-5`) with robust tool-use and safety template fallbacks.

---

## 🚀 How to Run Locally

If the live tunnel is down, you can easily run this scalable architecture locally:

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # (On Windows: .venv\Scripts\activate)
pip install -r requirements.txt
python -m uvicorn hishab.api.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd web
npm install
npm run dev
```
Navigate to `http://localhost:5173` in your browser.

---
*Disclaimer: This is a hackathon prototype and not an official upay application. It uses exclusively synthetic data to comply with strict data privacy and Responsible AI policies.*
