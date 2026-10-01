"""E6 — category suggestion for a draft send/payment: the user's confirmed label → their history → rules."""

from __future__ import annotations

from hishab.engine.features import CATEGORIES

_RULES: dict[str, list[tuple[str, float]]] = {
    "merchant": [("food_grocery", 0.5), ("shopping", 0.25), ("transport", 0.1), ("health", 0.1), ("other", 0.05)],
    "person": [("family_support", 0.5), ("rent", 0.2), ("other", 0.2), ("education", 0.1)],
    "agent": [("food_grocery", 0.5), ("family_support", 0.3), ("other", 0.2)],
    "biller": [("utilities", 0.6), ("education", 0.2), ("mobile", 0.1), ("other", 0.1)],
}
_BILLERS = {"BILL-recharge": "mobile", "BILL-electric": "utilities", "BILL-gas": "utilities",
            "BILL-internet": "utilities", "BILL-edu": "education", "DPS-ISLAMIC": "other"}


def _rules(counterparty_id: str | None, counterparty_type: str, amount: float) -> list[tuple[str, float]]:
    if counterparty_id in _BILLERS:
        return [(_BILLERS[counterparty_id], 0.9), ("utilities", 0.05), ("other", 0.05)]
    base = list(_RULES.get(counterparty_type, [("other", 0.5), ("food_grocery", 0.3), ("shopping", 0.2)]))
    if counterparty_type == "person" and amount >= 1500:
        base = [("family_support", 0.5), ("rent", 0.3), ("other", 0.2)]
    return base


def suggest_category(ctx, counterparty_id: str | None, counterparty_type: str, amount: float,
                     confirmed: dict[str, str]) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    if counterparty_id and counterparty_id in confirmed:
        scores[confirmed[counterparty_id]] = 0.95
    budget = 1.0 - sum(scores.values())
    if counterparty_id and not ctx.tx.empty:
        hist = ctx.tx[(ctx.tx["counterparty_id"] == counterparty_id) & (ctx.tx["direction"] == -1)]
        if not hist.empty:
            shares = hist["category"].value_counts(normalize=True)
            for cat, share in shares.items():
                if cat not in scores:
                    scores[str(cat)] = round(budget * 0.9 * float(share), 4)
    remaining = 1.0 - sum(scores.values())
    for cat, p in _rules(counterparty_id, counterparty_type, amount):
        if len(scores) >= 3 or remaining <= 0:
            break
        if cat not in scores:
            scores[cat] = round(remaining * p, 4)
    for cat in CATEGORIES:  # always return exactly three distinct options
        if len(scores) >= 3:
            break
        scores.setdefault(cat, 0.0)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:3]
