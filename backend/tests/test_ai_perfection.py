"""Intent classifier robustness tests (typos, Banglish, Bangla script).

Run `python scripts/train_ai.py` first so artifacts/intent_model.pkl exists.
"""
import pytest

from hishab import ml_engine

pytestmark = pytest.mark.skipif(
    not ml_engine._classifier_instance.is_trained, reason="intent model not trained yet"
)

CASES = [
    # status
    ("amr obosta kmn", "status"),
    ("ami k vlo krchi", "status"),
    ("মাস শেষে কি টাকা থাকবে", "status"),
    # advice
    ("k krb ekhn", "advice"),
    ("tk bchate ki kora ucit", "advice"),
    # goal
    ("tk jomte ci", "goal"),
    ("5000 tk jomabo 3 mashe", "goal"),
    ("tour er jnno tk jomabo", "goal"),
    ("porer masher tour er jnno kivabe tk save krbo", "goal"),
    # send_money
    ("krim ke 500 tk ptha", "send_money"),
    ("taka patao", "send_money"),
    # cashout
    ("kash aut krbo", "cashout"),
    ("cashout fi koto", "cashout"),
    # route_planner
    ("kivbe tk pathle kom charge", "route_planner"),
    ("npsb na bkash", "route_planner"),
    ("maa ke tk pathabo kishe", "route_planner"),
    # emergency
    ("imargency dhar lagbe", "emergency"),
    ("ekhon e tk dorkar joruri", "emergency"),
    # savings
    ("amr sanchy dekhao", "savings"),
    ("totl svings koto", "savings"),
    # health
    ("amr health chck koro", "health"),
    ("financl halth kemon", "health"),
]


@pytest.mark.parametrize("text,expected", CASES)
def test_intent(text, expected):
    assert ml_engine.predict_intent(text)["intent"] == expected


def test_amount_extraction():
    assert ml_engine.predict_intent("karim ke 1,500 tk pathao")["extracted_entities"] == {"amount": 1500}
    assert ml_engine.predict_intent("৫০০ টাকা পাঠাও")["extracted_entities"] == {"amount": 500}
    assert ml_engine.predict_intent("2k jomabo")["extracted_entities"] == {"amount": 2000}
