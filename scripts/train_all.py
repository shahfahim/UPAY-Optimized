"""Train all models on backend/data/full/ and write artifacts to backend/artifacts/ (spec §6.4).

Splits: 15% of users held out; months 1–9 train, month 10 validation, months 11–12 test (evaluate.py).
Usage: python scripts/train_all.py
"""

from __future__ import annotations

import time
from datetime import timedelta

import pandas as pd

from hishab.config import BACKEND_DIR
from hishab.data.generator import SyntheticData
from hishab.data.splits import TRAIN_START, VAL_START, TEST_START, split_users
from hishab.engine import forecast as F
from hishab.engine.forecast import save_residuals
from hishab.engine.risk import train_risk

ART = BACKEND_DIR / "artifacts"


def load_full() -> SyntheticData:
    d = BACKEND_DIR / "data" / "full"
    return SyntheticData(
        users=pd.read_parquet(d / "users.parquet"),
        transactions=pd.read_parquet(d / "transactions.parquet"),
        sessions=pd.read_parquet(d / "sessions.parquet"),
        labels=pd.read_parquet(d / "labels.parquet"),
        acceptance_truth=pd.read_parquet(d / "acceptance_truth.parquet"),
    )


def main() -> None:
    t0 = time.time()
    data = load_full()
    train_ids, test_ids = split_users(list(data.users.user_id))
    train_set = set(train_ids)
    print(f"users train={len(train_ids)} test={len(test_ids)}")

    daily = F.training_daily(data, TRAIN_START, VAL_START - timedelta(days=1), user_ids=train_set)
    fc = F.Forecaster().fit(daily)
    val_daily = F.training_daily(data, VAL_START, TEST_START - timedelta(days=1), user_ids=train_set)
    fc.save(ART)
    save_residuals(fc.residuals(val_daily), ART / "residuals.json")
    print(f"forecaster: {len(daily)} train days, {len(val_daily)} val days ({time.time() - t0:.0f}s)")

    risk = train_risk(data, val_from=VAL_START, until=TEST_START, user_ids=train_set)
    risk.save(ART)
    print(f"risk model saved ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
