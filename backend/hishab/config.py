"""Runtime settings, read from environment variables."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    demo_today: date
    seed: int
    data_dir: Path
    artifacts_dir: Path
    db_path: Path
    llm_enabled: bool
    llm_model: str
    anthropic_api_key: str | None
    # Demo-only routes (user list, time travel, global reset, OTP echo). Off unless HISHAB_DEMO_MODE=1.
    demo_mode: bool = False
    cors_origins: tuple[str, ...] = ("http://localhost:5173", "http://127.0.0.1:5173")


def _flag(raw: str | None) -> bool:
    return (raw or "").strip().lower() in ("1", "true", "yes", "on")


def _origins(raw: str | None) -> tuple[str, ...]:
    items = tuple(o.strip() for o in (raw or "").split(",") if o.strip())
    return items or Settings.cors_origins


def _llm_enabled(raw: str, key: str | None) -> bool:
    raw = raw.strip().lower()
    if raw in ("1", "true", "yes", "on"):
        return bool(key)
    if raw in ("0", "false", "no", "off"):
        return False
    return bool(key)  # "auto"


@lru_cache
def get_settings() -> Settings:
    key = os.environ.get("ANTHROPIC_API_KEY") or None
    return Settings(
        demo_today=date.fromisoformat(os.environ.get("DEMO_TODAY", "2026-09-18")),
        seed=int(os.environ.get("SEED", "42")),
        data_dir=Path(os.environ.get("HISHAB_DATA_DIR", BACKEND_DIR / "data")),
        artifacts_dir=Path(os.environ.get("HISHAB_ARTIFACTS_DIR", BACKEND_DIR / "artifacts")),
        db_path=Path(os.environ.get("HISHAB_DB_PATH", Path(tempfile.gettempdir()) / "hishab.db")),
        llm_enabled=_llm_enabled(os.environ.get("LLM_ENABLED", "auto"), key),
        llm_model=os.environ.get("LLM_MODEL", "claude-opus-5-5"),
        anthropic_api_key=key,
        demo_mode=_flag(os.environ.get("HISHAB_DEMO_MODE")),
        cors_origins=_origins(os.environ.get("HISHAB_CORS_ORIGINS")),
    )
