"""E7 — Smart Route: cheapest way to move money (graph over rules/fees.yaml) + costly-habit detection."""

from __future__ import annotations

from dataclasses import dataclass

from hishab.engine.recurring import detect_recurring
from hishab.rules import load_rules

START = "upay_wallet"


@dataclass
class Route:
    nodes: list[str]
    fee: float
    minutes: int
    label_bn: str


@dataclass
class CostlyHabit:
    kind: str
    monthly_count: int
    avg_amount: float
    current_fee: float
    best_fee: float
    annual_saving: float
    best_route: list[str]


def edge_fee(edge: dict, amount: float) -> float:
    fee = edge["fixed"] + edge["pct"] / 100.0 * amount
    return round(min(max(fee, edge["min"]), edge["max"]), 2)


def routes(amount: float, destination: str, fees: dict | None = None) -> list[Route]:
    """All simple paths from the upay wallet to `destination`, cheapest first (tie-break: faster)."""
    if amount is None or amount <= 0:
        raise ValueError("টাকার পরিমাণ সঠিক নয়")
    fees = fees or load_rules("fees")
    labels = fees.get("labels_bn", {})
    adj: dict[str, list[dict]] = {}
    for e in fees["edges"]:
        adj.setdefault(e["from"], []).append(e)
    found: list[Route] = []

    def walk(node: str, path: list[str], fee: float, minutes: int) -> None:
        for e in adj.get(node, []):
            nxt = e["to"]
            f = fee + edge_fee(e, amount)
            m = minutes + int(e["minutes"])
            if nxt == destination and (nxt != node or destination == START):
                p = path + [nxt]
                found.append(Route(nodes=p, fee=round(f, 2), minutes=m,
                                   label_bn=" → ".join(labels.get(n, n) for n in p)))
            elif nxt not in path:
                walk(nxt, path + [nxt], f, m)

    walk(START, [START], 0.0, 0)
    found.sort(key=lambda r: (r.fee, r.minutes, len(r.nodes)))
    return found


def detect_costly_habits(ctx) -> list[CostlyHabit]:
    """Recurring remittance sent by cash-out (cash carried to family) where a digital route is cheaper."""
    out = []
    for e in detect_recurring(ctx.tx, ctx.today):
        if e.kind != "remittance" or e.tx_type != "cash_out":
            continue
        rs = routes(e.amount, "other_mfs_wallet")
        cash = [r for r in rs if "agent_cash" in r.nodes]
        best = rs[0] if rs else None
        if not cash or best is None or best.fee >= cash[0].fee:
            continue
        out.append(CostlyHabit(kind="cash_remittance", monthly_count=1, avg_amount=e.amount,
                               current_fee=cash[0].fee, best_fee=best.fee,
                               annual_saving=round(12 * (cash[0].fee - best.fee), 0), best_route=best.nodes))
    out.sort(key=lambda h: h.annual_saving, reverse=True)
    return out
