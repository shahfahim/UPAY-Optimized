"""E9 — learning nudges: Thompson sampling with Beta(α, β) per (persona, item).

Global priors are learned offline from logged train-user responses (scripts/bandit_logs.py); each user's own accept/dismiss responses update their posterior.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


class Bandit:
    def __init__(self, priors: dict[tuple[str, str], tuple[float, float]]):
        self.priors = dict(priors)

    @classmethod
    def from_logs(cls, logs: pd.DataFrame, max_n: float = 20.0) -> "Bandit":
        """Beta priors from logged binary responses (columns persona, item_id, accepted).

        Counts are shrunk to at most `max_n` pseudo-observations per (persona, item) so each user's own
        responses still move their posterior."""
        pri = {}
        for (persona, item), g in logs.groupby(["persona", "item_id"]):
            n, acc = float(len(g)), float(g.accepted.sum())
            scale = min(1.0, max_n / n) if n else 1.0
            pri[(persona, item)] = (round(1 + acc * scale, 4), round(1 + (n - acc) * scale, 4))
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
