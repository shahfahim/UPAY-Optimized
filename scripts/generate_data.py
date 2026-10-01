"""Generate the synthetic dataset (spec §6).

Writes all users to backend/data/full/ (gitignored) and a 300-user serving subset to
backend/data/serving/ (committed; used by the live app).

Usage: python scripts/generate_data.py [--users 2000] [--seed 42]
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from hishab.config import BACKEND_DIR
from hishab.data.generator import SHOWCASE, generate

SERVING_USERS = 300


def write(data, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    data.users.to_parquet(out / "users.parquet", index=False)
    data.transactions.to_parquet(out / "transactions.parquet", index=False)
    data.sessions.to_parquet(out / "sessions.parquet", index=False)
    data.labels.to_parquet(out / "labels.parquet", index=False)
    data.acceptance_truth.to_parquet(out / "acceptance_truth.parquet", index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    t0 = time.time()
    data = generate(n_users=args.users, seed=args.seed)
    write(data, BACKEND_DIR / "data" / "full")

    rng = np.random.default_rng(args.seed)
    others = [u for u in data.users.user_id if u not in SHOWCASE]
    keep = list(SHOWCASE) + list(rng.choice(others, size=SERVING_USERS - len(SHOWCASE), replace=False))
    keep_set = set(keep)
    serving = type(data)(
        users=data.users[data.users.user_id.isin(keep_set)].reset_index(drop=True),
        transactions=data.transactions[data.transactions.user_id.isin(keep_set)].reset_index(drop=True),
        sessions=data.sessions[data.sessions.user_id.isin(keep_set)].reset_index(drop=True),
        labels=data.labels[data.labels.user_id.isin(keep_set)].reset_index(drop=True),
        acceptance_truth=data.acceptance_truth,
    )
    write(serving, BACKEND_DIR / "data" / "serving")
    size_mb = (BACKEND_DIR / "data" / "serving" / "transactions.parquet").stat().st_size / 1e6
    print(f"users={len(data.users)} tx={len(data.transactions)} serving_tx_mb={size_mb:.1f} "
          f"secs={time.time() - t0:.0f}")


if __name__ == "__main__":
    main()
