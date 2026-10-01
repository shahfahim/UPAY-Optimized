import pytest
from fastapi.testclient import TestClient

from hishab.api.main import create_app
from hishab.services import Hishab


@pytest.fixture
def svc(repo, store, tiny_models, settings):
    from hishab.data.generator import SyntheticData  # noqa: F401  (keeps fixture imports explicit)
    priors = {f"{p}|{i}": [1.0, 1.0] for p in ["garment_worker", "daily_wage", "shop_owner", "student"]
              for i in ["save_on_payday"]}
    tiny_models.bandit_priors = priors
    return Hishab(repo, store, tiny_models, settings)


@pytest.fixture
def client(svc):
    return TestClient(create_app(svc=svc))
