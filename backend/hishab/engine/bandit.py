"""E9 — learning nudges: Thompson sampling with Beta(α, β) per (persona, item).

Global priors come from the offline script; each user's own accept/dismiss responses update their posterior.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


class Bandit:
    def __init__(self, priors: dict[tuple[str, str], tuple[float, float]]):
        self.priors = dict(priors)

    @classmethod
    def from_truth(cls, acceptance_truth: pd.DataFrame, strength: float = 10.0) -> "Bandit":
        pri = {}
        for r in acceptance_truth.itertuples(index=False):
            pri[(r.persona, r.item_id)] = (round(r.p_accept * strength + 1, 4), round((1 - r.p_accept) * strength + 1, 4))
        return cls(pri)

    def posterior(self, persona: str, item_id: str, responses: list[tuple[str, bool]]) -> tuple[float, float]:
        a, b = self.priors.get((persona, item_id), (1.0, 1.0))
        for item, accepted in responses:
            if item == item_id:
                if accepted:
                    a += 1
                else:
                    b += 1
        return float(a), float(b)

    def sample(self, persona: str, item_id: str, responses: list[tuple[str, bool]], rng) -> float:
        a, b = self.posterior(persona, item_id, responses)
        return float(rng.beta(a, b))

    def mean(self, persona: str, item_id: str, responses: list[tuple[str, bool]]) -> float:
        a, b = self.posterior(persona, item_id, responses)
        return a / (a + b)

    def save(self, path: Path) -> None:
        data = {f"{p}|{i}": list(v) for (p, i), v in self.priors.items()}
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Bandit":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "Bandit":
        pri = {}
        for k, v in data.items():
            p, i = k.split("|", 1)
            pri[(p, i)] = (float(v[0]), float(v[1]))
        return cls(pri)
