"""PIN and OTP hashing.

PINs: scrypt (memory-hard, Python stdlib) with a random per-user salt, keyed with a server-side pepper
(HISHAB_PEPPER) so a stolen database alone cannot be brute-forced. Hashes made by the old prototype
(one SHA-256 pass with a static salt) still verify once and are upgraded on the next successful login.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

_N, _R, _P = 2**14, 8, 1  # ~16 MiB, tens of ms per check
_PREFIX = "scrypt"
_LEGACY_SALT = "hishab-demo:"


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _derive(pin: str, salt: bytes, pepper: str, n: int, r: int, p: int) -> bytes:
    keyed = hmac.new(pepper.encode(), pin.encode(), hashlib.sha256).digest()
    return hashlib.scrypt(keyed, salt=salt, n=n, r=r, p=p, dklen=32, maxmem=64 * 1024 * 1024)


def hash_pin(pin: str, pepper: str) -> str:
    salt = secrets.token_bytes(16)
    return f"{_PREFIX}${_N}${_R}${_P}${_b64(salt)}${_b64(_derive(pin, salt, pepper, _N, _R, _P))}"


def is_legacy(stored: str) -> bool:
    return not stored.startswith(_PREFIX + "$")


def verify_pin(stored: str | None, pin: str, pepper: str) -> bool:
    if not stored:
        return False
    if is_legacy(stored):
        legacy = hashlib.sha256((_LEGACY_SALT + pin).encode()).hexdigest()
        return hmac.compare_digest(stored, legacy)
    try:
        _, n, r, p, salt, digest = stored.split("$")
        got = _derive(pin, _unb64(salt), pepper, int(n), int(r), int(p))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(got, _unb64(digest))


def hash_otp(mobile: str, otp: str, pepper: str) -> str:
    """OTPs live for minutes, so a keyed SHA-256 is enough; it keeps the code out of the database."""
    return hmac.new(pepper.encode(), f"{mobile}:{otp}".encode(), hashlib.sha256).hexdigest()
