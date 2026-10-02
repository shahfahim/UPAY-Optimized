"""Only messages written for the user reach the client; anything else stays in the log."""


def test_user_errors_keep_their_bangla_message(client):
    r = client.get("/api/users/U0001/calendar?month=2026-13")
    assert r.status_code == 422 and r.json()["detail"] == "মাস সঠিক নয় (YYYY-MM)"


def test_unexpected_value_error_is_hidden(client, svc, monkeypatch):
    def boom():
        raise ValueError("could not convert string to float: '/srv/secret/path'")
    monkeypatch.setattr(svc, "users", boom)
    r = client.get("/api/users")
    assert r.status_code == 500
    assert r.json() == {"detail": "কিছু একটা ভুল হয়েছে"}
