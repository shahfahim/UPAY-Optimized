"""Nearby cash-out agents — DEMO DATA ONLY.

There is no agent-liquidity data or model behind this. The agents, their offsets
from the user and their cash hints are fixed sample values so the UI flow can be
shown. Output is deterministic (same location → same answer) and every row is
marked ``is_demo``. Replace with a upay agent-liquidity feed before any real use.
"""

from __future__ import annotations

import hashlib
import math

# name, metres north, metres east, cash hint (fixed sample value, not a prediction)
_DEMO_AGENTS: tuple[tuple[str, float, float, float], ...] = (
    ("Rahim Store", 90, 80, 0.85),
    ("Karim Telecom", -300, 340, 0.45),
    ("Bhai Bhai Traders", 520, -610, 0.15),
    ("Sumi Enterprise", -950, -730, 0.92),
    ("Molla Pharmacy", 1800, 1700, 0.60),
)

_EARTH_M = 6_371_000.0


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * _EARTH_M * math.asin(math.sqrt(a))


def cash_status(hint: float) -> str:
    return "green" if hint >= 0.8 else "amber" if hint >= 0.4 else "red"


def nearby_agents(lat: float, lng: float, limit: int = 5) -> list[dict]:
    """Demo agents placed at fixed offsets around (lat, lng), nearest first."""
    out = []
    for name, north, east, hint in _DEMO_AGENTS:
        a_lat = lat + north / 111_320.0
        a_lng = lng + east / (111_320.0 * max(math.cos(math.radians(lat)), 1e-6))
        out.append({
            "id": "demo-" + hashlib.sha1(name.encode()).hexdigest()[:8],
            "name": name,
            "lat": round(a_lat, 6),
            "lng": round(a_lng, 6),
            "distance_m": int(round(_haversine_m(lat, lng, a_lat, a_lng))),
            "cash_hint": hint,
            "cash_status": cash_status(hint),
            "is_demo": True,
        })
    out.sort(key=lambda a: a["distance_m"])
    return out[:limit]
