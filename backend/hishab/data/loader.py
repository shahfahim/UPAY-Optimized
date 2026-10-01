"""Read-only access to the synthetic dataset (parquet)."""

from __future__ import annotations

from datetime import date
from functools import lru_cache
from pathlib import Path

import pandas as pd

from hishab.config import get_settings


class DataRepo:
    def __init__(self, users: pd.DataFrame, tx: pd.DataFrame, acceptance_truth: pd.DataFrame | None = None):
        self.users = users.reset_index(drop=True)
        tx = tx.copy()
        tx["ts"] = pd.to_datetime(tx["ts"])
        self.tx = tx.sort_values(["user_id", "ts"], kind="stable").reset_index(drop=True)
        self.acceptance_truth = acceptance_truth
        self._by_user = {uid: g for uid, g in self.tx.groupby("user_id", sort=False)}
        self._users = {r["user_id"]: r for r in self.users.to_dict("records")}

    @classmethod
    def from_dir(cls, path: Path) -> "DataRepo":
        path = Path(path)
        acc = path / "acceptance_truth.parquet"
        return cls(
            users=pd.read_parquet(path / "users.parquet"),
            tx=pd.read_parquet(path / "transactions.parquet"),
            acceptance_truth=pd.read_parquet(acc) if acc.exists() else None,
        )

    def user(self, user_id: str) -> dict | None:
        row = self._users.get(user_id)
        return dict(row) if row is not None else None

    def history(self, user_id: str, until: date) -> pd.DataFrame:
        t = self._by_user.get(user_id)
        if t is None:
            return self.tx.iloc[0:0].copy()
        return t[t["ts"].dt.date <= until].copy()

    def list_users(self) -> list[dict]:
        cols = ["user_id", "synthetic_name", "persona", "area", "phone_masked"]
        return self.users[cols].to_dict("records")


@lru_cache
def get_repo() -> DataRepo:
    return DataRepo.from_dir(get_settings().data_dir / "serving")
