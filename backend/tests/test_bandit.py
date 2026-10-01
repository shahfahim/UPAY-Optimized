import numpy as np
import pandas as pd

from hishab.engine.bandit import Bandit


def test_posterior_updates():
    b = Bandit({("garment_worker", "A"): (1.0, 1.0)})
    resp = [("A", True), ("A", True), ("A", False), ("B", True)]
    assert b.posterior("garment_worker", "A", resp) == (3.0, 2.0)


def test_unknown_item_uses_uniform_prior():
    assert Bandit({}).posterior("student", "X", []) == (1.0, 1.0)


def test_sample_in_unit_interval():
    b = Bandit({})
    rng = np.random.default_rng(0)
    assert all(0.0 <= b.sample("student", "X", [], rng) <= 1.0 for _ in range(50))


def test_learns_preference():
    b = Bandit({})
    resp = [("A", True)] * 20 + [("B", False)] * 20
    rng = np.random.default_rng(1)
    a = np.mean([b.sample("p", "A", resp, rng) for _ in range(200)])
    bb = np.mean([b.sample("p", "B", resp, rng) for _ in range(200)])
    assert a > bb


def test_from_truth_and_roundtrip(tmp_path):
    truth = pd.DataFrame([{"persona": "garment_worker", "item_id": "A", "p_accept": 0.8}])
    b = Bandit.from_truth(truth, strength=10)
    assert b.posterior("garment_worker", "A", []) == (9.0, 3.0)
    b.save(tmp_path / "p.json")
    assert Bandit.load(tmp_path / "p.json").posterior("garment_worker", "A", []) == (9.0, 3.0)
