"""Every /users/{uid}/… route must reject missing, garbage and foreign tokens; the public route list is fixed,
so a new unprotected route fails CI."""
import re

from hishab.api.main import create_app

PUBLIC = {
    ("GET", "/api/health"), ("GET", "/api/impact"), ("GET", "/api/users"),  # /users is demo-mode only
    ("POST", "/api/auth/login"), ("POST", "/api/auth/register/start"), ("POST", "/api/auth/register/verify"),
}


def _routes(svc):
    """All documented API routes (FastAPI nests included routers, so read the OpenAPI schema)."""
    paths = create_app(svc=svc).openapi()["paths"]
    return [(m.upper(), p) for p, ops in paths.items() for m in ops]


def _url(path):
    return re.sub(r"\{[^}]+\}", lambda m: "U0001" if m.group(0) == "{uid}" else "x", path)


def _bearer(t):
    return {"Authorization": f"Bearer {t}"}


def test_public_routes_are_exactly_the_allowlist(svc, anon):
    open_routes = set()
    for method, path in _routes(svc):
        r = anon.request(method, _url(path) + ("?lat=23.8&lng=90.4" if "agents" in path else ""), json={})
        if r.status_code not in (401, 403):
            open_routes.add((method, path))
    assert open_routes == PUBLIC


def test_every_user_route_rejects_bad_tokens(svc, anon, store):
    other = store.create_session("U0002")
    user_routes = [(m, p) for m, p in _routes(svc) if "{uid}" in p]
    assert len(user_routes) > 20
    for method, path in user_routes:
        url = _url(path)
        assert anon.request(method, url, json={}).status_code == 401, (method, path)
        assert anon.request(method, url, json={}, headers=_bearer("garbage")).status_code == 401, (method, path)
        assert anon.request(method, url, json={}, headers=_bearer(other)).status_code == 403, (method, path)
