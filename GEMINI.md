# Hishab (হিসাব) - AI Agent Rules & Guidelines

## 1. Project Context
* **Event:** AI DEV FEST 2026 · AI Hackathon (DIU CPC × upay)
* **Goal:** AI cash-flow copilot prototype for low-income MFS users.
* **Strict Rule:** **DO NOT** use real customer data. Only use synthetic data.
* **Responsible AI:** The AI must never autonomously approve, size, or promise a loan. Always provide explainability (e.g., TreeSHAP reasons).

## 2. Tech Stack Requirements

### Frontend (`web/`)
* **Stack:** React 19, TypeScript, Vite, Tailwind CSS v4.
* **Styling:** Strictly use Tailwind utility classes.
* **Components:** Use React Functional Components and Hooks.
* **Language:** UI text and interactions MUST support Bangla (and English fallback).

### Backend (`backend/`)
* **Stack:** Python 3.11, FastAPI, Pydantic v2.
* **Machine Learning:** LightGBM, Scikit-learn, Pandas, NumPy.
* **LLM Integration:** Claude (`claude-opus-5-5`) via Anthropic SDK with strict tool use and template fallbacks.
* **Validation:** Rely on Pydantic v2 schemas for all API input/output validation.

## 3. Workflow Protocol (Superpowers Integration)
* **Planning:** Always use `writing-plans` before touching complex code.
* **Testing:** Use `test-driven-development` and run `pytest backend/tests` for backend changes.
* **Debugging:** Use `systematic-debugging` for any errors or failing tests.
* **Validation before completion:** Always verify functionality (API responses or frontend builds) before assuming a task is complete.

## 4. UI/UX Guidelines
* Replicate the upay-style wallet shell faithfully.
* Keep the design mobile-first (optimized for 375px width).
* Ensure the "Prototype — upay-এর অফিসিয়াল app নয়" ribbon remains visible.
