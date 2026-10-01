from datetime import date

import pandas as pd

from hishab.data.labels import shortfall_days
from hishab.engine.actions import TRANSFORMS
from hishab.engine.replay import month_flows, replay_month


def _month(small_data, uid="U0001", start=date(2026, 8, 1), end=date(2026, 8, 31)):
    tx = small_data.transactions[small_data.transactions.user_id == uid]
    d = pd.to_datetime(tx.ts).dt.date
    before = tx[d < start]
    start_balance = float(before.balance_after.iloc[-1])
    return tx, tx[(d >= start) & (d <= end)], start_balance


def test_replay_identity(small_data):
    tx, month, bal = _month(small_data)
    out = replay_month(month, bal, 0.0, [], date(2026, 8, 1), date(2026, 8, 31))
    assert out.shortfall_days == len(shortfall_days(tx, date(2026, 8, 1), date(2026, 8, 31)))
    assert out.fees == round(float(month.fee.sum()), 2)


def test_replay_save_on_payday_not_worse(small_data):
    _, month, bal = _month(small_data)
    base = replay_month(month, bal, 0.0, [], date(2026, 8, 1), date(2026, 8, 31))
    sal = month[month.type == "salary_in"]
    payday = pd.to_datetime(sal.ts).dt.date.iloc[0]
    tr = TRANSFORMS["save_on_payday"]({"amount": 1000.0, "payday": payday.isoformat()})
    after = replay_month(month, bal, 0.0, [tr], date(2026, 8, 1), date(2026, 8, 31))
    assert after.shortfall_days <= base.shortfall_days


def test_month_flows_kinds(small_data):
    _, month, _ = _month(small_data)
    f = month_flows(month)
    assert set(f.kind) <= {"recurring", "discretionary", "income", "internal"}
    assert (f[f.category == "family_support"].kind == "recurring").all()
