"""Shared fixtures: a small generated dataset written to a temp dir, and a temp SQLite store."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from hishab.config import get_settings
from hishab.data.generator import generate
from hishab.data.loader import DataRepo
from hishab.store.sqlite import Store


def _write(data, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    data.users.to_parquet(out / "users.parquet", index=False)
    data.transactions.to_parquet(out / "transactions.parquet", index=False)
    data.sessions.to_parquet(out / "sessions.parquet", index=False)
    data.labels.to_parquet(out / "labels.parquet", index=False)
    data.acceptance_truth.to_parquet(out / "acceptance_truth.parquet", index=False)


@pytest.fixture(scope="session")
def small_data():
    return generate(n_users=20, seed=42)


@pytest.fixture(scope="session")
def data_dir(small_data, tmp_path_factory):
    d = tmp_path_factory.mktemp("data") / "serving"
    _write(small_data, d)
    return d


@pytest.fixture(scope="session")
def repo(data_dir):
    return DataRepo.from_dir(data_dir)


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "test.db")
    s.reset()
    yield s
    s.close()


@pytest.fixture
def settings():
    get_settings.cache_clear()
    return replace(get_settings(), llm_enabled=False)
