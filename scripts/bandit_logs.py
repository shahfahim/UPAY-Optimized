"""Logged accept/dismiss responses for the bandit (E9), drawn on TRAIN users only.

The generator's acceptance table is the simulated *environment*: it decides whether a shown card is accepted.
The bandit never reads those probabilities. It only sees the binary outcomes logged here, under a uniform-random
logging policy (propensity 1/K), the same way it would learn from real app logs. Evaluation then runs on
held-out test users.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

UNKNOWN_P = 0.2  # environment's acceptance for an item the generator has no row for


def logged_responses(data, user_ids, items: list[str], days: int = 30, seed: int = 3) -> pd.DataFrame:
    truth = {(r.persona, r.item_id): r.p_accept for r in data.acceptance_truth.itertuples(index=False)}
    persona = dict(zip(data.users.user_id, data.users.persona))
    rng = np.random.default_rng(seed)
    rows = []
    for uid in user_ids:
        p = persona[uid]
        for _ in range(days):
            item = items[int(rng.integers(0, len(items)))]
            rows.append((uid, p, item, 1.0 / len(items), bool(rng.random() < truth.get((p, item), UNKNOWN_P))))
    return pd.DataFrame(rows, columns=["user_id", "persona", "item_id", "propensity", "accepted"])


def best_fixed_arm(logs: pd.DataFrame) -> dict[str, str]:
    """Per persona, the single item with the highest observed acceptance in the logs (fair static baseline)."""
    rate = logs.groupby(["persona", "item_id"]).accepted.mean().reset_index()
    return {p: g.sort_values("accepted", ascending=False).item_id.iloc[0] for p, g in rate.groupby("persona")}
