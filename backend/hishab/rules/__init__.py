"""Business rules (YAML) — kept separate from ML predictions."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml

RULES_DIR = Path(__file__).resolve().parent

RiskLevel = Literal["green", "amber", "red"]


@lru_cache
def load_rules(name: str) -> dict:
    with open(RULES_DIR / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def risk_level(p: float) -> RiskLevel:
    levels = load_rules("guardrails")["risk_levels"]
    if p >= levels["red"]:
        return "red"
    if p >= levels["amber"]:
        return "amber"
    return "green"


def forbidden_phrases() -> list[str]:
    return list(load_rules("guardrails")["forbidden_phrases"])


def contains_forbidden(text: str) -> bool:
    low = text.lower()
    return any(p.lower() in low for p in forbidden_phrases())
