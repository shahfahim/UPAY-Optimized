"""Leakage-safe splits (spec §6.4): 15% of users held out; months 1–9 train, 10 validation, 11–12 test."""

from __future__ import annotations

from datetime import date

import numpy as np

from hishab.data.generator import SHOWCASE

TRAIN_START = date(2025, 11, 1)   # first month skipped so trailing features have history
VAL_START = date(2026, 7, 1)      # month 10
TEST_START = date(2026, 8, 1)     # months 11–12
DATA_END = date(2026, 9, 30)
TEST_SHARE = 0.15


def split_users(user_ids: list[str], seed: int = 42) -> tuple[list[str], list[str]]:
    """Returns (train_ids, test_ids). Showcase users always stay in train (they are demo users)."""
    pool = sorted(u for u in user_ids if u not in SHOWCASE)
    rng = np.random.default_rng(seed)
    n_test = int(round(TEST_SHARE * len(user_ids)))
    test = set(rng.choice(pool, size=min(n_test, len(pool)), replace=False).tolist())
    train = [u for u in user_ids if u not in test]
    return train, sorted(test)
