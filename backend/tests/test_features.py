import math

from hishab.engine.context import build_ctx
from hishab.engine.features import FEATURE_KEYS, PROTECTED, training_frame, user_features


def test_user_features_numeric_and_complete(repo, store, settings):
    for uid in ["U0001", "U0002", "U0003", "U0004", "U0005"]:
        f = user_features(build_ctx(uid, repo, store, settings))
        assert set(FEATURE_KEYS) <= set(f)
        for k, v in f.items():
            # days_to_income is NaN (a LightGBM "missing" value) for earners with no regular payday
            ok = math.isfinite(v) or (k == "days_to_income" and math.isnan(v))
            assert isinstance(v, float) and ok, (uid, k, v)


def test_features_do_not_include_protected_names():
    assert not (set(FEATURE_KEYS) & PROTECTED)


def test_rina_payday_features(repo, store, settings):
    f = user_features(build_ctx("U0001", repo, store, settings))
    assert f["days_since_income"] == 11.0  # salary on the 7th, today the 18th
    assert 18.0 <= f["days_to_income"] <= 21.0


def test_training_frame_has_labels(small_data):
    obs = sorted(small_data.labels.obs_date.unique())[:4]
    frame = training_frame(small_data, obs)
    assert len(frame) > 0
    assert {"user_id", "obs_date", "shortfall_14d"} <= set(frame.columns)
    assert set(FEATURE_KEYS) <= set(frame.columns)
