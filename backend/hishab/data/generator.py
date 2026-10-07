"""Seeded synthetic MFS data generator (spec §6).

Everything here is synthetic. Patterns injected (documented in docs/synthetic-data.md):
salary/allowance/daily income, remittance home, rent, utilities, recharge, weekly cash-outs,
digital merchant payments, health shocks, Eid bonus + festival spending, DPS installments
(some sized too high so they are missed), savers, and an inactivity mechanism.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from hishab.data.labels import daily_balances, income_mask, window_any
from hishab.rules import load_rules

PERSONAS_PATH = Path(__file__).with_name("personas.yaml")

TX_COLS = [
    "tx_id", "user_id", "ts", "type", "amount", "direction", "fee", "balance_after",
    "counterparty_id", "counterparty_name", "counterparty_type", "counterparty_channel",
    "category", "area",
]

FIRST_NAMES_F = ["রিনা", "সুমি", "মরিয়ম", "শাহনাজ", "নাজমা", "রুবিনা", "শিউলি", "পারভীন", "ফাতেমা", "জান্নাত",
                 "তানিয়া", "মিতু", "লাকি", "সালমা", "আসমা"]
FIRST_NAMES_M = ["রহিম", "করিম", "জসিম", "সোহেল", "রাকিব", "মামুন", "শাকিল", "হাসান", "আরিফ", "নাঈম",
                 "সাগর", "রুবেল", "ইমরান", "তানভীর", "বিল্লাল"]
LAST_NAMES = ["আক্তার", "বেগম", "খাতুন", "ইসলাম", "হোসেন", "উদ্দিন", "মিয়া", "রহমান", "আলী", "সরকার"]
MERCHANT_NAMES = ["মুদি দোকান", "সবজি বাজার", "ফার্মেসি", "চায়ের দোকান", "কাপড়ের দোকান", "রেস্টুরেন্ট",
                  "সুপারশপ", "মাছের বাজার", "বেকারি", "জুতার দোকান"]
BILLERS = [("BILL-electric", "বিদ্যুৎ বিল"), ("BILL-gas", "গ্যাস বিল"), ("BILL-internet", "ইন্টারনেট বিল")]
DPS_OPTIONS = [500, 1000, 1500, 2000, 3000, 5000]

# Showcase users with fixed persona and tuned behaviour (spec §6.1).
SHOWCASE = {
    "U0001": {"persona": "garment_worker", "name": "রিনা আক্তার", "gender": "female", "area": "Gazipur",
              "salary": 12500.0, "salary_day": 7, "remit_frac": 0.35, "family_wallet": "cash",
              "rent": 3000.0, "rent_day": 5, "spend_ratio": 1.08, "digital_share": 0.08,
              "saver": False, "dps": 0, "festival_frac": 1.25, "utilities": 450.0, "opening": 1500.0,
              "tightens": False, "noise": 0.12, "cash_k": 5, "shock_prob": 0.0},
    "U0002": {"persona": "daily_wage", "name": "জসিম উদ্দিন", "gender": "male", "area": "Mirpur"},
    "U0003": {"persona": "shop_owner", "name": "শাহনাজ পারভীন", "gender": "female", "area": "Uttara"},
    "U0004": {"persona": "student", "name": "তানভীর হাসান", "gender": "male", "area": "Dhanmondi"},
    "U0005": {"persona": "garment_worker", "name": "সুমি খাতুন", "gender": "female", "area": "Savar",
              "salary": 16000.0, "salary_day": 6, "remit_frac": 0.25, "family_wallet": "other_mfs",
              "rent": 2500.0, "rent_day": 3, "spend_ratio": 0.82, "digital_share": 0.35,
              "saver": True, "daily_saver": True, "dps": 0, "festival_frac": 0.4, "utilities": 400.0,
              "opening": 6000.0},
}


@dataclass
class SyntheticData:
    users: pd.DataFrame
    transactions: pd.DataFrame
    sessions: pd.DataFrame
    labels: pd.DataFrame
    acceptance_truth: pd.DataFrame


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def inactivity_hazard(feats: dict) -> float:
    """Monthly probability of going inactive (assumed causal story, spec §6.3)."""
    z = (-5.2
         + 1.6 * feats.get("cashout_share", 0.0)
         + 1.1 * feats.get("other_wallet_share", 0.0)
         + (0.7 if feats.get("depletion_days", 30) < 5 else 0.0)
         - (0.6 if feats.get("pocket_total", 0.0) > 0 else 0.0)
         - 1.0 * max(-1.0, min(1.0, feats.get("session_trend", 0.0))))
    return _sigmoid(z)


def _fee_rules() -> dict:
    edges = load_rules("fees")["edges"]
    return {(e["from"], e["to"]): e for e in edges}


def _edge_fee(edge: dict, amount: float) -> float:
    fee = edge["fixed"] + edge["pct"] / 100.0 * amount
    return round(min(max(fee, edge["min"]), edge["max"]), 2)


def _eids(start: date, end: date) -> list[date]:
    out = []
    for e in load_rules("eid_dates")["eids"]:
        d = e["date"] if isinstance(e["date"], date) else date.fromisoformat(str(e["date"]))
        if start <= d <= end + timedelta(days=30):
            out.append(d)
    return out


@dataclass
class _Profile:
    user_id: str
    persona: str
    p: dict
    name: str
    gender: str
    area: str
    income_amount: float
    income_day: int
    monthly_income: float
    remit_frac: float
    family_wallet: str
    rent: float
    rent_day: int
    spend_ratio: float
    digital_share: float
    utilities: float
    util_day: int
    recharge_per_month: int
    recharge_amount: float
    saver: bool
    daily_saver: bool
    dps: int
    dps_day: int
    festival_frac: float
    opening: float
    session_lam: float
    merchants: list
    never_inactive: bool
    tightens: bool = True
    noise: float = 0.35
    cash_k: int = 0
    shock_prob: float = 0.008


def _draw(rng, lo_hi):
    lo, hi = lo_hi
    return float(rng.uniform(lo, hi))


def _choice_weighted(rng, weights: dict) -> str:
    keys = list(weights)
    probs = np.array([weights[k] for k in keys], dtype=float)
    return str(rng.choice(keys, p=probs / probs.sum()))


def _make_profile(uid: str, persona: str, personas: dict, rng, merchant_pool: list, over: dict | None) -> _Profile:
    p = personas[persona]
    over = over or {}
    female = rng.random() < p["female_share"]
    gender = over.get("gender", "female" if female else "male")
    first = rng.choice(FIRST_NAMES_F if gender == "female" else FIRST_NAMES_M)
    name = over.get("name", f"{first} {rng.choice(LAST_NAMES)}")
    area = over.get("area", str(rng.choice(p["areas"])))
    inc = p["income"]
    kind = inc["kind"]
    if kind == "salary":
        income_amount = over.get("salary", round(_draw(rng, inc["amount"]), -2))
        income_day = over.get("salary_day", int(rng.integers(inc["day"][0], inc["day"][1] + 1)))
        monthly_income = income_amount
    elif kind == "allowance":
        income_amount = round(_draw(rng, inc["amount"]), -2)
        income_day = int(rng.integers(inc["day"][0], inc["day"][1] + 1))
        monthly_income = income_amount + inc["parttime_prob"] * 30 * np.mean(inc["parttime_amount"])
    elif kind == "daily":
        income_amount = round(_draw(rng, inc["amount"]), -1)
        income_day = 0
        monthly_income = income_amount * 30 * inc["work_prob"]
    else:  # shop
        income_amount = round(_draw(rng, inc["amount"]), -1)
        income_day = 0
        restock = _draw(rng, inc["restock_frac"])
        monthly_income = income_amount * 30 * inc["open_prob"] * (1 - restock)
    has_rent = rng.random() < p["rent"]["prob"]
    rent = over.get("rent", round(_draw(rng, p["rent"]["amount"]), -2) if has_rent else 0.0)
    has_remit = rng.random() < p["remittance"]["prob"]
    remit_frac = over.get("remit_frac", _draw(rng, p["remittance"]["frac"]) if has_remit else 0.0)
    has_util = rng.random() < p["utilities"]["prob"]
    saver = over.get("saver", bool(rng.random() < p["saver_prob"]))
    dps = over.get("dps", None)
    if dps is None:
        dps = 0
        if rng.random() < p["dps_prob"]:
            # Some DPS holders over-commit (sized well above 10% of income) and later miss installments.
            target = monthly_income * (rng.uniform(0.05, 0.12) if rng.random() < 0.6 else rng.uniform(0.18, 0.30))
            dps = int(min(DPS_OPTIONS, key=lambda o: abs(o - target)))
    return _Profile(
        user_id=uid, persona=persona, p=p, name=name, gender=gender, area=area,
        income_amount=float(income_amount), income_day=int(income_day), monthly_income=float(monthly_income),
        remit_frac=float(remit_frac),
        family_wallet=over.get("family_wallet", _choice_weighted(rng, p["family_wallet"])),
        rent=float(rent), rent_day=over.get("rent_day", int(rng.integers(p["rent"]["day"][0], p["rent"]["day"][1] + 1))),
        spend_ratio=over.get("spend_ratio", _draw(rng, p["spend_ratio"])),
        digital_share=over.get("digital_share", _draw(rng, p["digital_share"])),
        utilities=float(over.get("utilities", round(_draw(rng, p["utilities"]["amount"]), -1) if has_util else 0.0)),
        util_day=int(rng.integers(10, 21)),
        recharge_per_month=int(rng.integers(p["recharge"]["per_month"][0], p["recharge"]["per_month"][1] + 1)),
        recharge_amount=round(_draw(rng, p["recharge"]["amount"]), -1),
        saver=saver, daily_saver=over.get("daily_saver", False),
        dps=int(dps), dps_day=int(min(28, (income_day or 10) + int(rng.integers(1, 6)))),
        festival_frac=over.get("festival_frac", _draw(rng, p["festival_frac"])),
        opening=float(over.get("opening", round(monthly_income * rng.uniform(0.1, 0.4), -1))),
        session_lam=float(rng.uniform(0.6, 2.0)),
        merchants=[merchant_pool[i] for i in rng.choice(len(merchant_pool), size=4, replace=False)],
        never_inactive=uuid_is_showcase(uid),
        tightens=over.get("tightens", True),
        noise=over.get("noise", 0.35),
        cash_k=over.get("cash_k", 0),
        shock_prob=over.get("shock_prob", 0.008),
    )


def uuid_is_showcase(uid: str) -> bool:
    return uid in SHOWCASE


class _Sim:
    """Simulates one user's wallet day by day and appends rows to shared column lists."""

    def __init__(self, prof: _Profile, rng, cols: dict, sessions: list, start: date, end: date,
                 eids: list[date], fees: dict, seq: list):
        self.f = prof
        self.rng = rng
        self.cols = cols
        self.sessions = sessions
        self.start, self.end = start, end
        self.eids = eids
        self.fees = fees
        self.seq = seq
        self.balance = 0.0
        self.pocket = 0.0
        self.cash = 0.0
        self.active = True
        self.inactive_from: date | None = None
        self.pending: list[dict] = []
        self.recent_sessions: list[int] = []
        self.recharge_days: set[int] = set()
        self.income_balance = None
        self.depletion_days = 30
        self.days_since_income = 0
        self.session_drift = 1.0
        self.last_ts: datetime | None = None

    # --- emit -------------------------------------------------------------------------------------
    def emit(self, d: date, hour: int, typ: str, amount: float, direction: int, category: str,
             cp_id: str, cp_name: str, cp_type: str, channel: str = "upay", fee: float = 0.0) -> None:
        amount = round(float(amount), 2)
        fee = round(float(fee), 2)
        if direction == 1:
            self.balance = round(self.balance + amount, 2)
        elif direction == -1:
            self.balance = round(self.balance - amount - fee, 2)
        self.seq[0] += 1
        c = self.cols
        c["tx_id"].append(f"T{self.seq[0]:09d}")
        c["user_id"].append(self.f.user_id)
        minute = int(self.rng.integers(0, 60))
        ts = datetime(d.year, d.month, d.day, hour, minute)
        # balance_after follows emission order, so timestamps must never go backwards within the user's history
        if self.last_ts is not None and ts <= self.last_ts:
            ts = self.last_ts + timedelta(minutes=1)
        self.last_ts = ts
        c["ts"].append(ts)
        c["type"].append(typ)
        c["amount"].append(amount)
        c["direction"].append(direction)
        c["fee"].append(fee)
        c["balance_after"].append(self.balance)
        c["counterparty_id"].append(cp_id)
        c["counterparty_name"].append(cp_name)
        c["counterparty_type"].append(cp_type)
        c["counterparty_channel"].append(channel)
        c["category"].append(category)
        c["area"].append(self.f.area)

    def can_pay(self, amount: float, fee: float = 0.0) -> bool:
        return self.balance >= amount + fee - 1e-9

    def pay(self, d, hour, typ, amount, category, cp_id, cp_name, cp_type, channel="upay", fee=0.0,
            essential=False) -> bool:
        if amount <= 0:
            return True
        if self.can_pay(amount, fee):
            self.emit(d, hour, typ, amount, -1, category, cp_id, cp_name, cp_type, channel, fee)
            return True
        if essential:
            self.pending.append(dict(typ=typ, amount=amount, category=category, cp_id=cp_id, cp_name=cp_name,
                                     cp_type=cp_type, channel=channel, fee=fee))
        return False

    # --- helpers ----------------------------------------------------------------------------------
    def cashout_fee(self, amount: float) -> float:
        return _edge_fee(self.fees[("upay_wallet", "agent_cash")], amount)

    def send_fee(self, channel: str, amount: float) -> float:
        if channel in ("other_mfs", "bank"):
            return _edge_fee(self.fees[("upay_wallet", "npsb")], amount)
        return 0.0

    def eid_window(self, d: date) -> date | None:
        for e in self.eids:
            if e - timedelta(days=14) <= d < e:
                return e
        return None

    # --- day --------------------------------------------------------------------------------------
    def run(self) -> None:
        f = self.f
        self.emit(self.start, 9, "cash_in", f.opening, 1, "other", "AGENT", "এজেন্ট", "agent")
        base_disc = max(0.25 * f.monthly_income,
                        f.monthly_income * f.spend_ratio
                        - f.rent - f.remit_frac * f.monthly_income - f.utilities
                        - f.recharge_per_month * f.recharge_amount - f.dps) / 30.0
        d = self.start
        while d <= self.end:
            if d.day == 1 and d > self.start:
                self.month_check(d)
            if self.active:
                self.day(d, base_disc)
            d += timedelta(days=1)

    def month_check(self, d: date) -> None:
        if self.f.never_inactive or not self.active:
            return
        c = self.cols
        lo = datetime.combine(d - timedelta(days=30), datetime.min.time())
        # Only this user's rows are at the tail of the shared lists; scan backwards.
        out_total = cash = other = 0.0
        i = len(c["ts"]) - 1
        while i >= 0 and c["user_id"][i] == self.f.user_id and c["ts"][i] >= lo:
            if c["direction"][i] == -1:
                out_total += c["amount"][i]
                if c["type"][i] == "cash_out":
                    cash += c["amount"][i]
                if c["counterparty_channel"][i] == "other_mfs":
                    other += c["amount"][i]
            i -= 1
        rs = self.recent_sessions[-28:]
        trend = 0.0
        if len(rs) == 28:
            a, b = sum(rs[:14]), sum(rs[14:])
            trend = (b - a) / (a + 1)
        feats = dict(depletion_days=self.depletion_days,
                     cashout_share=cash / out_total if out_total else 0.0,
                     other_wallet_share=other / out_total if out_total else 0.0,
                     pocket_total=self.pocket, session_trend=trend)
        if self.rng.random() < inactivity_hazard(feats):
            self.active = False
            self.inactive_from = d

    def day(self, d: date, base_disc: float) -> None:
        f, rng = self.f, self.rng
        income_today = False
        # Session drift (slow random walk) feeds the inactivity mechanism.
        self.session_drift = float(np.clip(self.session_drift * math.exp(rng.normal(0, 0.05)), 0.2, 2.0))

        # 1) income -------------------------------------------------------------------------------
        kind = f.p["income"]["kind"]
        if kind == "salary":
            pay_day = f.income_day
            if d.day == pay_day:
                amt = f.income_amount * rng.uniform(0.98, 1.03)
                self.emit(d, 10, "salary_in", round(amt, 0), 1, "income", f"EMP-{f.user_id}",
                          "কারখানা (বেতন)", "employer")
                income_today = True
        elif kind == "allowance":
            if d.day == f.income_day:
                self.emit(d, 10, "receive_money", f.income_amount, 1, "income", f"FAM-{f.user_id}",
                          "পরিবার (হাতখরচ)", "person")
                income_today = True
            inc = f.p["income"]
            if rng.random() < inc["parttime_prob"]:
                self.emit(d, 18, "receive_money", round(_draw(rng, inc["parttime_amount"]), -1), 1, "income",
                          f"PT-{f.user_id}", "টিউশনি", "person")
                income_today = True
        elif kind == "daily":
            inc = f.p["income"]
            prob = inc["work_prob"] * (inc["monsoon_factor"] if d.month in (6, 7, 8) else 1.0)
            if rng.random() < prob:
                self.emit(d, 19, "receive_money", round(f.income_amount * rng.uniform(0.7, 1.3), -1), 1, "income",
                          f"CON-{f.user_id}", "ঠিকাদার (মজুরি)", "person")
                income_today = True
        else:  # shop
            inc = f.p["income"]
            if rng.random() < inc["open_prob"]:
                amt = f.income_amount * rng.uniform(0.6, 1.5) * (1.3 if self.eid_window(d) else 1.0)
                self.emit(d, 20, "receive_money", round(amt, 0), 1, "income", f"CUST-{f.user_id}",
                          "ক্রেতাদের পেমেন্ট", "person")
                income_today = True
            if d.weekday() == 5:  # weekly restock
                restock = f.income_amount * 7 * inc["open_prob"] * _draw(rng, inc["restock_frac"])
                self.pay(d, 9, "merchant_pay", round(restock, -1), "other", f"SUP-{f.user_id}", "পাইকারি সরবরাহকারী",
                         "merchant")
        # Eid bonus for garment workers, 7-10 days before Eid
        if f.p.get("bonus"):
            for e in self.eids:
                if d == e - timedelta(days=8):
                    frac = load_rules("eid_dates")["garment_bonus_fraction"]
                    self.emit(d, 11, "bonus_in", round(f.income_amount * frac, 0), 1, "income", f"EMP-{f.user_id}",
                              "কারখানা (ঈদ বোনাস)", "employer")
                    income_today = True

        if income_today:
            self.income_balance = self.balance
            self.days_since_income = 0
        else:
            self.days_since_income += 1
            if self.income_balance and self.balance < 0.5 * self.income_balance and self.depletion_days == 30:
                self.depletion_days = self.days_since_income
        if income_today:
            self.depletion_days = 30

        # 2) deferred essentials ---------------------------------------------------------------------
        still = []
        for item in self.pending:
            if self.can_pay(item["amount"], item["fee"]):
                self.emit(d, 11, item["typ"], item["amount"], -1, item["category"], item["cp_id"], item["cp_name"],
                          item["cp_type"], item["channel"], item["fee"])
            else:
                still.append(item)
        self.pending = still[-6:]

        # 3) scheduled outflows ----------------------------------------------------------------------
        if f.rent and d.day == f.rent_day:
            self.pay(d, 12, "send_money", f.rent, "rent", f"LL-{f.user_id}", "বাড়িওয়ালা", "person", essential=True)
        remit_day = (f.income_day + 2) if f.income_day else 0
        if f.remit_frac > 0:
            remit_base = f.remit_frac * f.monthly_income
            if (kind in ("salary", "allowance") and d.day == remit_day) or (kind in ("daily", "shop") and d.weekday() == 4):
                amt = remit_base if kind in ("salary", "allowance") else remit_base / 4.3
                self.remit(d, round(amt, -1))
            e = self.eid_window(d)
            if e and d == e - timedelta(days=5):
                self.remit(d, round(0.5 * remit_base, -1))
        if f.utilities and d.day == f.util_day:
            cp_id, cp_name = BILLERS[int(f.user_id[1:]) % len(BILLERS)]
            self.pay(d, 13, "bill_pay", round(f.utilities * rng.uniform(0.85, 1.15), 0), "utilities",
                     cp_id, cp_name, "biller", essential=True)
        if d.day == 1:
            days = rng.choice(np.arange(1, 29), size=f.recharge_per_month, replace=False)
            self.recharge_days = set(int(x) for x in days)
        if d.day in self.recharge_days:
            self.pay(d, 14, "mobile_recharge", f.recharge_amount, "mobile", "BILL-recharge", "মোবাইল রিচার্জ", "biller")
        if f.dps and d.day == f.dps_day:
            if self.can_pay(f.dps):
                self.emit(d, 12, "dps_installment", f.dps, -1, "other", "DPS-ISLAMIC", "ইসলামিক ডিপিএস", "biller")
            else:
                self.emit(d, 12, "dps_installment_missed", f.dps, 0, "other", "DPS-ISLAMIC", "ইসলামিক ডিপিএস",
                          "biller")
        if f.p["income"]["kind"] == "allowance" and "tuition" in f.p and d.day == 15 \
                and rng.random() < f.p["tuition"]["prob_month"]:
            self.pay(d, 11, "bill_pay", round(_draw(rng, f.p["tuition"]["amount"]), -2), "education",
                     "BILL-edu", "শিক্ষা প্রতিষ্ঠান", "biller", essential=True)
        # savings
        if f.saver and income_today and kind in ("salary", "allowance"):
            amt = round(f.monthly_income * rng.uniform(0.03, 0.08), -1)
            if self.can_pay(amt + 500):
                self.emit(d, 15, "pocket_in", amt, -1, "other", "pocket:emergency", "জরুরি পকেট", "pocket")
                self.pocket += amt
        if f.daily_saver and self.can_pay(520):
            self.emit(d, 21, "pocket_in", 20.0, -1, "other", "pocket:emergency", "জরুরি পকেট", "pocket")
            self.pocket += 20.0
        if self.pocket > 0 and self.balance < 300 and not income_today:
            amt = round(min(self.pocket, 1000.0), 2)
            self.emit(d, 16, "pocket_out", amt, 1, "other", "pocket:emergency", "জরুরি পকেট", "pocket")
            self.pocket = round(self.pocket - amt, 2)

        # 4) discretionary --------------------------------------------------------------------------
        need = base_disc * (1.2 if d.weekday() in (4, 5) else 1.0) * float(rng.lognormal(0, f.noise))
        if d.day >= 26:
            need *= 1.1  # month-end effect
        if self.balance < 1000 and f.tightens:
            need *= 0.7  # belt-tightening when money is low
        e = self.eid_window(d)
        festival = (f.festival_frac * f.monthly_income / 14.0) if e else 0.0
        # digital part: on average a `digital_share` of daily need is paid from the wallet
        if rng.random() < f.digital_share * 2:
            m_id, m_name = f.merchants[int(rng.integers(0, len(f.merchants)))]
            cat = _choice_weighted(rng, {"food_grocery": 0.6, "transport": 0.15, "shopping": 0.15, "other": 0.1})
            self.pay(d, int(rng.integers(8, 21)), "merchant_pay", round(need * 0.5, 0), cat, m_id, m_name, "merchant")
        if festival:
            m_id, m_name = f.merchants[0]
            half = round(festival * 0.5, 0)
            self.pay(d, 17, "merchant_pay", half, "festival", m_id, m_name, "merchant")
            self.cash -= festival * 0.5  # cash part of festival spending
        # cash part
        self.cash -= need * (1 - f.digital_share)
        if self.cash < 0:
            k = f.cash_k or int(rng.integers(4, 8))
            want = round(-self.cash + need * (1 - f.digital_share) * k, -1)
            fee = self.cashout_fee(want)
            if not self.can_pay(want, fee):
                want = math.floor(max(0.0, self.balance - 50) / (1 + 0.0185) / 10) * 10
                fee = self.cashout_fee(want)
            if want >= 100:
                self.emit(d, int(rng.integers(8, 20)), "cash_out", want, -1,
                          "festival" if festival else "food_grocery", "AGENT", "এজেন্ট", "agent", "upay", fee)
                self.cash += want
            else:
                self.cash = 0.0  # went without
        # rare health shock
        if rng.random() < f.shock_prob:
            m_id = "M-pharmacy"
            self.pay(d, 19, "merchant_pay", round(_draw(rng, (800, 4000)), -1), "health", m_id, "ফার্মেসি", "merchant",
                     essential=True)

        # sessions
        lam = f.session_lam * self.session_drift * (2.0 if income_today else 1.0)
        s = int(rng.poisson(lam))
        self.recent_sessions.append(s)
        if s:
            self.sessions.append((f.user_id, d, s))

    def remit(self, d: date, amount: float) -> None:
        f = self.f
        if amount <= 0:
            return
        if f.family_wallet == "cash":
            fee = self.cashout_fee(amount)
            self.pay(d, 11, "cash_out", amount, "family_support", "AGENT", "এজেন্ট", "agent", "upay", fee,
                     essential=True)
        else:
            channel = {"other_mfs": "other_mfs", "bank": "bank", "upay": "upay"}[f.family_wallet]
            fee = self.send_fee(channel, amount)
            self.pay(d, 11, "send_money", amount, "family_support", f"FAM-{f.user_id}", "মা", "person", channel, fee,
                     essential=True)


def _acceptance_truth(rng) -> pd.DataFrame:
    base = {"save_on_payday": 0.35, "split_remittance": 0.25, "digital_pay_instead_of_cashout": 0.45,
            "cheaper_route": 0.55, "pause_paisa_saving": 0.6, "trim_discretionary": 0.2, "dps_ready": 0.3,
            "eid_weekly_saving": 0.4, "cashout_cost": 0.5, "emergency_fund": 0.45, "eid_planning": 0.5,
            "npsb_basics": 0.4, "budget_why": 0.3, "paisa_saving": 0.35}
    mult = {"garment_worker": 1.0, "daily_wage": 0.85, "shop_owner": 0.9, "student": 1.1}
    rows = []
    for persona, m in mult.items():
        for item, p in base.items():
            rows.append((persona, item, float(np.clip(p * m * rng.uniform(0.8, 1.2), 0.05, 0.9))))
    return pd.DataFrame(rows, columns=["persona", "item_id", "p_accept"])


def generate(n_users: int = 2000, seed: int = 42, start: date = date(2025, 10, 1),
             end: date = date(2026, 9, 30)) -> SyntheticData:
    with open(PERSONAS_PATH, encoding="utf-8") as fh:
        personas = yaml.safe_load(fh)["personas"]
    rng = np.random.default_rng(seed)
    merchant_pool = [(f"M-{i:03d}", f"{MERCHANT_NAMES[i % len(MERCHANT_NAMES)]} {i}") for i in range(120)]
    names = list(personas)
    shares = np.array([personas[k]["share"] for k in names], dtype=float)
    shares /= shares.sum()
    eids = _eids(start, end)
    fees = _fee_rules()

    cols = {k: [] for k in TX_COLS}
    sessions: list = []
    seq = [0]
    user_rows = []
    inactive_from = {}
    for i in range(n_users):
        uid = f"U{i + 1:04d}"
        over = SHOWCASE.get(uid)
        persona = over["persona"] if over else str(rng.choice(names, p=shares))
        urng = np.random.default_rng([seed, i])
        prof = _make_profile(uid, persona, personas, urng, merchant_pool, over)
        sim = _Sim(prof, urng, cols, sessions, start, end, eids, fees, seq)
        sim.run()
        inactive_from[uid] = sim.inactive_from
        user_rows.append(dict(
            user_id=uid, synthetic_name=prof.name, persona=persona, gender=prof.gender,
            age_band=str(urng.choice(["18-24", "25-34", "35-44", "45+"], p=[0.3, 0.4, 0.2, 0.1])),
            area=prof.area, tenure_days=int(urng.integers(90, 1500)), family_wallet_type=prof.family_wallet,
            paisa_saving_default=False, dps_monthly=prof.dps, monthly_income=round(prof.monthly_income, 0),
            salary_day=prof.income_day, phone_masked=f"01XXXXXX{int(urng.integers(100, 1000))}",
            demo_pin="123456", inactive_from=sim.inactive_from,
        ))

    tx = pd.DataFrame(cols)
    tx["ts"] = pd.to_datetime(tx["ts"])
    users = pd.DataFrame(user_rows)
    sess = pd.DataFrame(sessions, columns=["user_id", "date", "session_count"])
    labels = _labels(tx, users, start, end, eids)
    return SyntheticData(users=users, transactions=tx, sessions=sess, labels=labels,
                         acceptance_truth=_acceptance_truth(rng))


def generate_one(user_id: str, name: str, persona: str = "garment_worker", seed: int = 0,
                 start: date = date(2025, 10, 1), end: date = date(2026, 9, 30)) -> tuple[dict, list[dict]]:
    """One extra synthetic user (used by demo registration). Never goes inactive."""
    with open(PERSONAS_PATH, encoding="utf-8") as fh:
        personas = yaml.safe_load(fh)["personas"]
    merchant_pool = [(f"M-{i:03d}", f"{MERCHANT_NAMES[i % len(MERCHANT_NAMES)]} {i}") for i in range(120)]
    urng = np.random.default_rng([seed, 999_999])
    prof = _make_profile(user_id, persona, personas, urng, merchant_pool, {"name": name})
    prof.never_inactive = True
    cols = {k: [] for k in TX_COLS}
    sim = _Sim(prof, urng, cols, [], start, end, _eids(start, end), _fee_rules(), [0])
    sim.run()
    tx = pd.DataFrame(cols)
    tx["tx_id"] = user_id + "-" + tx["tx_id"]
    user = dict(user_id=user_id, synthetic_name=name, persona=persona, gender=prof.gender, age_band="25-34",
                area=prof.area, tenure_days=0, family_wallet_type=prof.family_wallet, paisa_saving_default=False,
                dps_monthly=prof.dps, monthly_income=round(prof.monthly_income, 0), salary_day=prof.income_day,
                phone_masked="", demo_pin="", inactive_from=None)
    return user, tx.to_dict("records")


def _labels(tx: pd.DataFrame, users: pd.DataFrame, start: date, end: date, eids: list[date]) -> pd.DataFrame:
    threshold = load_rules("guardrails")["shortfall_threshold"]
    obs = [d.date() for d in pd.date_range(start + timedelta(days=35), end - timedelta(days=14), freq="W-SUN")]
    rows = []
    inactive = users.set_index("user_id")["inactive_from"].to_dict()
    for uid, t in tx.groupby("user_id", sort=False):
        bal = daily_balances(t, start, end)
        inc_days = set(pd.to_datetime(t.loc[income_mask(t), "ts"]).dt.date)
        flags = pd.Series([(pd.notna(b) and b < threshold and day not in inc_days) for day, b in bal.items()],
                          index=bal.index)
        stop = inactive.get(uid)
        if stop is not None and not pd.isna(stop):
            flags[flags.index >= stop] = False
        fest = t[t["category"] == "festival"]
        fest_dates = pd.to_datetime(fest["ts"]).dt.date
        for o in obs:
            if stop is not None and not pd.isna(stop) and o >= stop:
                continue
            pre = float("nan")
            for e in eids:
                if timedelta(days=0) < (e - o) <= timedelta(days=45):
                    pre = float(fest[(fest_dates >= e - timedelta(days=30)) & (fest_dates < e)]["amount"].sum())
                    break
            rows.append(dict(
                user_id=uid, obs_date=o,
                shortfall_14d=window_any(flags, o, 14),
                inactive_30d=bool(stop is not None and not pd.isna(stop) and o < stop <= o + timedelta(days=30)),
                pre_eid_spend=pre,
            ))
    return pd.DataFrame(rows)
