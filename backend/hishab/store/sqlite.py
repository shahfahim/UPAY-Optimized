"""Per-user demo state in SQLite: pockets, toggles, responses, notifications, clock, sessions."""

from __future__ import annotations

import json
import secrets
import sqlite3
import threading
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Callable

POCKETS = ["emergency", "eid", "family", "education", "paisa", "custom"]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS state (user_id TEXT PRIMARY KEY, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sim_tx (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, body TEXT);
CREATE TABLE IF NOT EXISTS responses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, kind TEXT,
    item_id TEXT, accepted INTEGER, ts TEXT);
CREATE TABLE IF NOT EXISTS categories (user_id TEXT, counterparty_id TEXT, category TEXT,
    PRIMARY KEY (user_id, counterparty_id));
CREATE TABLE IF NOT EXISTS notifications (rowid_ INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, body TEXT);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id TEXT);
CREATE TABLE IF NOT EXISTS extra_users (user_id TEXT PRIMARY KEY, body TEXT);
CREATE TABLE IF NOT EXISTS extra_tx (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, body TEXT);
"""


@dataclass
class UserState:
    pockets: dict = field(default_factory=lambda: {p: 0.0 for p in POCKETS})
    pocket_goals: dict = field(default_factory=dict)
    paisa_on: bool = False
    paisa_paused: bool = False
    budget_mode: str = "auto"
    manual_budget: dict = field(default_factory=dict)
    dps: dict | None = None
    notif_optout: list = field(default_factory=list)
    last_active: date | None = None

    def to_json(self) -> str:
        d = asdict(self)
        d["last_active"] = self.last_active.isoformat() if self.last_active else None
        return json.dumps(d, ensure_ascii=False)

    @classmethod
    def from_json(cls, body: str) -> "UserState":
        d = json.loads(body)
        la = d.get("last_active")
        d["last_active"] = date.fromisoformat(la) if la else None
        pockets = {p: 0.0 for p in POCKETS}
        pockets.update(d.get("pockets") or {})
        d["pockets"] = pockets
        return cls(**d)


def _default(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    raise TypeError(type(o))


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def _exec(self, sql: str, args: tuple = ()) -> list:
        with self._lock:
            cur = self._conn.execute(sql, args)
            rows = cur.fetchall()
            self._conn.commit()
            return rows

    # lifecycle ---------------------------------------------------------------------------------
    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def reset(self) -> None:
        with self._lock:
            for t in ["state", "sim_tx", "responses", "categories", "notifications", "meta", "sessions",
                      "extra_users", "extra_tx"]:
                self._conn.execute(f"DELETE FROM {t}")
            self._conn.commit()

    # state -------------------------------------------------------------------------------------
    def get_state(self, user_id: str, default_factory: Callable[[], UserState] | None = None) -> UserState:
        rows = self._exec("SELECT body FROM state WHERE user_id=?", (user_id,))
        if rows:
            return UserState.from_json(rows[0][0])
        st = default_factory() if default_factory else UserState()
        self.save_state(user_id, st)
        return st

    def save_state(self, user_id: str, st: UserState) -> None:
        self._exec("INSERT OR REPLACE INTO state (user_id, body) VALUES (?, ?)", (user_id, st.to_json()))

    # simulated transactions ----------------------------------------------------------------------
    def add_sim_tx(self, user_id: str, row: dict) -> None:
        self._exec("INSERT INTO sim_tx (user_id, body) VALUES (?, ?)",
                   (user_id, json.dumps(row, default=_default, ensure_ascii=False)))

    def sim_tx(self, user_id: str) -> list[dict]:
        rows = self._exec("SELECT body FROM sim_tx WHERE user_id=? ORDER BY id", (user_id,))
        return [json.loads(r[0]) for r in rows]

    # responses and categories ---------------------------------------------------------------------
    def record_response(self, user_id: str, kind: str, item_id: str, accepted: bool) -> None:
        self._exec("INSERT INTO responses (user_id, kind, item_id, accepted, ts) VALUES (?, ?, ?, ?, ?)",
                   (user_id, kind, item_id, int(accepted), datetime.now().isoformat()))

    def responses(self, user_id: str, kind: str) -> list[tuple[str, bool]]:
        rows = self._exec("SELECT item_id, accepted FROM responses WHERE user_id=? AND kind=? ORDER BY id",
                          (user_id, kind))
        return [(r[0], bool(r[1])) for r in rows]

    def set_category(self, user_id: str, counterparty_id: str, category: str) -> None:
        self._exec("INSERT OR REPLACE INTO categories (user_id, counterparty_id, category) VALUES (?, ?, ?)",
                   (user_id, counterparty_id, category))

    def categories(self, user_id: str) -> dict[str, str]:
        rows = self._exec("SELECT counterparty_id, category FROM categories WHERE user_id=?", (user_id,))
        return {r[0]: r[1] for r in rows}

    # notifications ------------------------------------------------------------------------------
    def add_notification(self, user_id: str, n: dict) -> None:
        self._exec("INSERT INTO notifications (user_id, body) VALUES (?, ?)",
                   (user_id, json.dumps(n, default=_default, ensure_ascii=False)))

    def notifications(self, user_id: str) -> list[dict]:
        rows = self._exec("SELECT body FROM notifications WHERE user_id=? ORDER BY rowid_", (user_id,))
        return [json.loads(r[0]) for r in rows]

    def mark_notifications_read(self, user_id: str) -> None:
        rows = self._exec("SELECT rowid_, body FROM notifications WHERE user_id=?", (user_id,))
        with self._lock:
            for rid, body in rows:
                d = json.loads(body)
                d["read"] = True
                self._conn.execute("UPDATE notifications SET body=? WHERE rowid_=?", (json.dumps(d, ensure_ascii=False), rid))
            self._conn.commit()

    # meta ----------------------------------------------------------------------------------------
    def set_meta(self, key: str, value: str) -> None:
        self._exec("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (key, value))

    def get_meta(self, key: str) -> str | None:
        rows = self._exec("SELECT value FROM meta WHERE key=?", (key,))
        return rows[0][0] if rows else None

    # clock ---------------------------------------------------------------------------------------
    def clock_offset(self) -> int:
        rows = self._exec("SELECT value FROM meta WHERE key='clock_offset'")
        return int(rows[0][0]) if rows else 0

    def set_clock_offset(self, days: int) -> None:
        self._exec("INSERT OR REPLACE INTO meta (key, value) VALUES ('clock_offset', ?)", (str(int(days)),))

    # sessions and registered users ------------------------------------------------------------------
    def create_session(self, user_id: str) -> str:
        token = secrets.token_urlsafe(24)
        self._exec("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
        return token

    def session_user(self, token: str) -> str | None:
        rows = self._exec("SELECT user_id FROM sessions WHERE token=?", (token,))
        return rows[0][0] if rows else None

    def add_user(self, row: dict, tx: list[dict]) -> None:
        self._exec("INSERT OR REPLACE INTO extra_users (user_id, body) VALUES (?, ?)",
                   (row["user_id"], json.dumps(row, default=_default, ensure_ascii=False)))
        with self._lock:
            self._conn.executemany("INSERT INTO extra_tx (user_id, body) VALUES (?, ?)",
                                   [(row["user_id"], json.dumps(t, default=_default, ensure_ascii=False))
                                    for t in tx])
            self._conn.commit()

    def extra_users(self) -> list[dict]:
        return [json.loads(r[0]) for r in self._exec("SELECT body FROM extra_users")]

    def extra_user(self, user_id: str) -> dict | None:
        rows = self._exec("SELECT body FROM extra_users WHERE user_id=?", (user_id,))
        return json.loads(rows[0][0]) if rows else None

    def extra_tx(self, user_id: str) -> list[dict]:
        rows = self._exec("SELECT body FROM extra_tx WHERE user_id=? ORDER BY id", (user_id,))
        return [json.loads(r[0]) for r in rows]
