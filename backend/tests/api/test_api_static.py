from fastapi.testclient import TestClient

from hishab.api.main import create_app


def test_spa_fallback(svc, tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><title>Hishab</title>", encoding="utf-8")
    (dist / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    client = TestClient(create_app(svc=svc, web_dist=dist))
    page = client.get("/app/savings")
    assert page.status_code == 200 and "<title>Hishab</title>" in page.text
    assert client.get("/assets/app.js").text == "console.log(1)"
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/nope").status_code == 404
