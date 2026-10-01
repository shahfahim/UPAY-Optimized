"""Bundle of trained artifacts used by the engine at serving time."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from hishab.engine.forecast import Forecaster, load_residuals
from hishab.engine.risk import RiskModel


@dataclass
class Models:
    forecaster: Forecaster
    risk: RiskModel
    residuals: dict
    bandit_priors: dict | None = None


def artifacts_present(directory: Path) -> bool:
    d = Path(directory)
    return all((d / n).exists() for n in ["forecaster_out.txt", "forecaster_in.txt", "risk.txt",
                                          "risk_calibration.json", "residuals.json"])


def load_from(directory: Path) -> Models:
    d = Path(directory)
    priors_path = d / "bandit_priors.json"
    priors = json.loads(priors_path.read_text(encoding="utf-8")) if priors_path.exists() else None
    return Models(forecaster=Forecaster.load(d), risk=RiskModel.load(d),
                  residuals=load_residuals(d / "residuals.json"), bandit_priors=priors)


@lru_cache
def load_models(directory: str) -> Models:
    return load_from(Path(directory))
