"""Per-user demo state in SQLite: pockets, toggles, responses, notifications, clock, sessions."""

from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
import threading
import time
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
CREATE TABLE IF NOT EXISTS auth_sessions (token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL,
    created_at REAL NOT NULL, last_seen REAL NOT NULL, expires_at REAL NOT NULL, revoked_at REAL);
CREATE TABLE IF NOT EXISTS auth_failures (key TEXT PRIMARY KEY, count INTEGER NOT NULL, locked_until REAL);
CREATE TABLE IF NOT EXISTS extra_users (user_id TEXT PRIMARY KEY, body TEXT);
CREATE TABLE IF NOT EXISTS extra_tx (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, body TEXT);
"""


@dataclass
class UserState:
    pockets: dict = field(default_factory=lambda: {p: 0.0 for p in POCKETS})
    pocket_goals: dict = field(default_factory=dict)
    custom_names: dict = field(default_factory=dict)
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
        d["pockets"] = d.get("pockets") or {}
        d["custom_names"] = d.get("custom_names") or {}
        return cls(**d)


def _default(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    raise TypeError(type(o))


SESSION_TTL_S = 12 * 3600   # absolute lifetime of a login
SESSION_IDLE_S = 30 * 60    # sign out after 30 minutes without a request
MAX_FAILURES = 5            # wrong PINs before a lockout
LOCKOUT_S = 15 * 60


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class Store:
    def __init__(self, path: Path, clock: Callable[[], float] = time.time):
        self.clock = clock  # wall clock for sessions and lockouts (not the demo calendar)
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

    def reset(self, keep_sessions: bool = False) -> None:
        """Clear demo state. With keep_sessions, logins of seeded users survive; registered users are
        removed, so their sessions go too (their ids are handed out again)."""
        with self._lock:
            if keep_sessions:
                self._conn.execute("DELETE FROM auth_sessions WHERE user_id IN (SELECT user_id FROM extra_users)")
            tables = ["state", "sim_tx", "responses", "categories", "notifications", "meta", "extra_users", "extra_tx",
                      "auth_failures"]
            for t in tables + ([] if keep_sessions else ["auth_sessions"]):
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
    # Only a SHA-256 of each bearer token is stored, so a copied database cannot be replayed as logins.
    def create_session(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        now = self.clock()
        self._exec("INSERT INTO auth_sessions (token_hash, user_id, created_at, last_seen, expires_at) "
                   "VALUES (?, ?, ?, ?, ?)", (_token_hash(token), user_id, now, now, now + SESSION_TTL_S))
        return token

    def session_user(self, token: str) -> str | None:
        """The user behind a live token; touches last_seen. Expired, idle or revoked tokens return None."""
        if not token:
            return None
        h, now = _token_hash(token), self.clock()
        rows = self._exec("SELECT user_id, last_seen, expires_at, revoked_at FROM auth_sessions WHERE token_hash=?",
                          (h,))
        if not rows:
            return None
        uid, last_seen, expires_at, revoked_at = rows[0]
        if revoked_at is not None or now >= expires_at or now - last_seen >= SESSION_IDLE_S:
            return None
        self._exec("UPDATE auth_sessions SET last_seen=? WHERE token_hash=?", (now, h))
        return uid

    def revoke_session(self, token: str) -> None:
        self._exec("UPDATE auth_sessions SET revoked_at=? WHERE token_hash=? AND revoked_at IS NULL",
                   (self.clock(), _token_hash(token)))

    def revoke_user_sessions(self, user_id: str) -> int:
        with self._lock:
            cur = self._conn.execute("UPDATE auth_sessions SET revoked_at=? WHERE user_id=? AND revoked_at IS NULL",
                                     (self.clock(), user_id))
            self._conn.commit()
            return cur.rowcount

    # login lockout ----------------------------------------------------------------------------------
    def locked_until(self, key: str) -> float | None:
        rows = self._exec("SELECT locked_until FROM auth_failures WHERE key=?", (key,))
        until = rows[0][0] if rows else None
        return until if until is not None and until > self.clock() else None

    def record_failure(self, key: str) -> None:
        with self._lock:
            row = self._conn.execute("SELECT count FROM auth_failures WHERE key=?", (key,)).fetchone()
            count = (row[0] if row else 0) + 1
            until = self.clock() + LOCKOUT_S if count >= MAX_FAILURES else None
            self._conn.execute("INSERT OR REPLACE INTO auth_failures (key, count, locked_until) VALUES (?, ?, ?)",
                               (key, 0 if until else count, until))
            self._conn.commit()

    def clear_failures(self, key: str) -> None:
        self._exec("DELETE FROM auth_failures WHERE key=?", (key,))

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
