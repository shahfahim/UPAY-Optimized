"""E3 — shortfall-risk model: P(shortfall within 14 days), calibrated, with TreeSHAP drivers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

from hishab.engine.features import FEATURE_KEYS, PROTECTED, training_frame, user_features
from hishab.rules import load_rules, risk_level

PROJ_FEATURES = ["proj_min_14d", "proj_min_14d_stress"]
RISK_FEATURES = [k for k in FEATURE_KEYS if k not in PROTECTED and k != "persona_code"] + PROJ_FEATURES

_PARAMS = dict(objective="binary", learning_rate=0.05, num_leaves=31, min_data_in_leaf=40,
               feature_fraction=0.9, bagging_fraction=0.9, bagging_freq=1, verbose=-1, seed=42)


def projection_features(f: dict) -> dict[str, float]:
    """Cheap 14-day balance projection from the feature set (identical in training and serving)."""
    rent, fam = f.get("out_30d_rent", 0.0), f.get("out_30d_family_support", 0.0)
    bal, dti = f["balance"], f["days_to_income"]
    disc = max(0.0, (f["out_30d"] - rent - fam) / 30.0)
    out = {}
    for name, mult in (("proj_min_14d", 1.0), ("proj_min_14d_stress", 1.5)):
        vals = []
        for k in range(1, 15):
            if dti > 1:
                v = bal - k * disc * mult + (f["income_amount"] - rent - fam if k >= dti else 0.0)
            else:
                v = bal + k * (f["income_amount"] - f["out_30d"] * mult) / 30.0
            vals.append(v)
        out[name] = float(min(vals))
    return out


def risk_frame(data, obs_dates, user_ids=None) -> pd.DataFrame:
    fr = training_frame(data, obs_dates)
    if user_ids is not None:
        fr = fr[fr["user_id"].isin(set(user_ids))]
    proj = pd.DataFrame([projection_features(r) for r in fr.to_dict("records")], index=fr.index)
    return pd.concat([fr, proj], axis=1)


@dataclass
class Driver:
    feature: str
    text_bn: str
    text_en: str
    impact: float


@dataclass
class RiskResult:
    prob: float
    level: str
    drivers: list[Driver] = field(default_factory=list)
    shortfall_date: date | None = None
    shortfall_amount: float = 0.0


def _bn(n: float) -> str:
    from hishab.engine.text import bn_num
    return bn_num(n)


def _driver_text(feat: str, f: dict) -> tuple[str, str]:
    v = f.get(feat, 0.0)
    pct = round(100 * v)
    T = {
        "balance": (f"এখন ব্যালেন্স কম (৳{_bn(round(v))})", f"Your balance is low (৳{round(v):,})"),
        "days_to_income": (f"বেতন/আয় আসতে আরও {_bn(round(v))} দিন বাকি", f"Income is still {round(v)} days away"),
        "days_since_income": (f"শেষ আয়ের পর {_bn(round(v))} দিন পেরিয়েছে", f"{round(v)} days since your last income"),
        "out_7d": (f"গত ৭ দিনে খরচ বেশি (৳{_bn(round(v))})", f"High spending in the last 7 days (৳{round(v):,})"),
        "out_30d": (f"গত ৩০ দিনে খরচ বেশি (৳{_bn(round(v))})", f"High spending in the last 30 days (৳{round(v):,})"),
        "cashout_share_30d": (f"খরচের {_bn(pct)}% cash-out করে হয় — এতে fee লাগে",
                              f"{pct}% of spending goes through cash-out, which costs fees"),
        "remittance_share": (f"আয়ের {_bn(pct)}% বাড়িতে পাঠানো হয়", f"{pct}% of income is sent home"),
        "depletion_days": (f"আয়ের {_bn(round(v))} দিনের মধ্যেই অর্ধেক টাকা শেষ হয়ে যায়",
                           f"Half the income is gone within {round(v)} days"),
        "cashout_3d_after_income_share": (f"আয় আসার ৩ দিনের মধ্যে {_bn(pct)}% cash-out হয়",
                                          f"{pct}% is cashed out within 3 days of income"),
        "shortfall_days_90d": (f"গত ৩ মাসে {_bn(round(v))} দিন টাকা কম পড়েছে",
                               f"You ran short on {round(v)} days in the last 3 months"),
        "min_balance_30d": (f"গত মাসে ব্যালেন্স ৳{_bn(round(v))}-এ নেমেছিল",
                            f"Your balance fell to ৳{round(v):,} last month"),
        "proj_min_14d": ("সামনের দুই সপ্তাহে খরচ আয়ের চেয়ে বেশি হওয়ার সম্ভাবনা",
                         "Spending is likely to exceed income in the next two weeks"),
        "proj_min_14d_stress": ("খরচ একটু বাড়লেই সামনের দুই সপ্তাহে টাকা কম পড়তে পারে",
                                "A small rise in spending could leave you short in two weeks"),
        "pocket_total": ("জরুরি সঞ্চয় কম", "Little emergency savings"),
        "other_wallet_share": (f"খরচের {_bn(pct)}% অন্য wallet-এ যায়", f"{pct}% of spending goes to other wallets"),
        "income_regularity": ("আয় নিয়মিত নয়", "Income is irregular"),
        "income_amount": ("আয়ের তুলনায় খরচ বেশি", "Spending is high compared with income"),
        "month_end": ("মাসের শেষ সময়", "It's the end of the month"),
        "days_to_eid": ("সামনে উৎসবের খরচ", "Festival spending ahead"),
        "out_30d_festival": ("উৎসবের খরচ বেড়েছে", "Festival spending went up"),
        "out_30d_health": ("চিকিৎসার খরচ হয়েছে", "There were medical costs"),
    }
    if feat in T:
        return T[feat]
    if feat.startswith("out_30d_"):
        cat = feat.removeprefix("out_30d_")
        from hishab.engine.text import category_bn
        return (f"{category_bn(cat)} খরচ বেশি (৳{_bn(round(v))})", f"High {cat.replace('_', ' ')} spending (৳{round(v):,})")
    return ("খরচের ধরন ঝুঁকি বাড়াচ্ছে", "Your spending pattern is adding risk")


class RiskModel:
    def __init__(self, booster: lgb.Booster | None = None, iso_x: list | None = None, iso_y: list | None = None):
        self.booster = booster
        self.iso_x = iso_x
        self.iso_y = iso_y

    def fit(self, X: pd.DataFrame, y, X_val: pd.DataFrame, y_val, rounds: int = 300) -> "RiskModel":
        self.booster = lgb.train(_PARAMS, lgb.Dataset(X[RISK_FEATURES], np.asarray(y, dtype=float)),
                                 num_boost_round=rounds)
        raw = self.booster.predict(X_val[RISK_FEATURES])
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0).fit(raw, np.asarray(y_val, dtype=float))
        self.iso_x = [float(v) for v in iso.X_thresholds_]
        self.iso_y = [float(v) for v in iso.y_thresholds_]
        return self

    def raw(self, X: pd.DataFrame) -> np.ndarray:
        return self.booster.predict(X[RISK_FEATURES])

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        raw = self.raw(X)
        if not self.iso_x:
            return raw
        return np.clip(np.interp(raw, self.iso_x, self.iso_y), 0.0, 1.0)

    def contributions(self, X: pd.DataFrame) -> pd.DataFrame:
        c = self.booster.predict(X[RISK_FEATURES], pred_contrib=True)
        return pd.DataFrame(c[:, :-1], columns=RISK_FEATURES, index=X.index)

    def save(self, directory: Path) -> None:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.booster.save_model(str(directory / "risk.txt"))
        (directory / "risk_calibration.json").write_text(json.dumps({"x": self.iso_x, "y": self.iso_y}))

    @classmethod
    def load(cls, directory: Path) -> "RiskModel":
        directory = Path(directory)
        cal = json.loads((directory / "risk_calibration.json").read_text())
        return cls(lgb.Booster(model_file=str(directory / "risk.txt")), cal["x"], cal["y"])


def train_risk(data, val_from: date, until: date, user_ids=None) -> RiskModel:
    obs = sorted(o for o in data.labels["obs_date"].unique() if o < until)
    fr = risk_frame(data, obs, user_ids)
    tr, va = fr[fr["obs_date"] < val_from], fr[fr["obs_date"] >= val_from]
    return RiskModel().fit(tr, tr["shortfall_14d"], va, va["shortfall_14d"])


def risk_features(ctx, fc, base_fc=None) -> dict[str, float]:
    f = user_features(ctx)
    f.update(projection_features(f))
    if base_fc is not None and base_fc is not fc:
        delta = min(fc.p50[:14]) - min(base_fc.p50[:14])
        for k in PROJ_FEATURES:
            f[k] += delta
    return {k: float(f[k]) for k in RISK_FEATURES}


def rule_baseline(feats: dict) -> float:
    """Simple rule: balance / average daily spend < days until next income ⇒ shortfall."""
    daily = feats["out_30d"] / 30.0
    if daily <= 0:
        return 0.0
    return 1.0 if feats["balance"] / daily < feats["days_to_income"] else 0.0


def score(ctx, fc, models, base_fc=None, top_k: int = 3) -> RiskResult:
    feats = risk_features(ctx, fc, base_fc)
    X = pd.DataFrame([feats])
    prob = float(models.risk.predict_proba(X)[0])
    contrib = models.risk.contributions(X).iloc[0].sort_values(ascending=False)
    drivers = []
    for feat, val in contrib.items():
        if len(drivers) >= top_k:
            break
        if val <= 0 and drivers:
            break
        bn, en = _driver_text(feat, feats)
        drivers.append(Driver(feature=feat, text_bn=bn, text_en=en, impact=round(float(val), 4)))
    while len(drivers) < top_k:  # pad with the strongest remaining contributors
        feat = contrib.index[len(drivers)]
        bn, en = _driver_text(feat, feats)
        drivers.append(Driver(feature=feat, text_bn=bn, text_en=en, impact=round(float(contrib[feat]), 4)))
    return RiskResult(prob=round(prob, 4), level=risk_level(prob), drivers=drivers,
                      shortfall_date=fc.shortfall_date, shortfall_amount=fc.shortfall_amount)
