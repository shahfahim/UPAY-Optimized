import re

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


class AuthedClient(TestClient):
    """Logs in as the user a /api/users/{uid}/… path names, unless the test sends its own Authorization.

    Keeps route tests about behaviour; test_api_auth.py covers the token checks themselves."""

    def __init__(self, app, store):
        super().__init__(app)
        self._store = store

    def request(self, method, url, **kwargs):
        m = re.match(r"/api/users/([^/?]+)/", str(url))
        headers = dict(kwargs.pop("headers", None) or {})
        if m and not any(k.lower() == "authorization" for k in headers):
            headers["Authorization"] = f"Bearer {self._store.create_session(m.group(1))}"
        return super().request(method, url, headers=headers, **kwargs)


@pytest.fixture
def client(svc):
    return AuthedClient(create_app(svc=svc), svc.store)


@pytest.fixture
def anon(svc):
    """A client that sends no token."""
    return TestClient(create_app(svc=svc))
