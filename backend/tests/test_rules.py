from hishab.rules import forbidden_phrases, load_rules, risk_level

RULE_FILES = [
    "guardrails", "actions", "fees", "eid_dates", "lessons", "readiness",
    "levels", "dps", "emergency", "notifications",
]


def test_all_rule_files_load():
    for name in RULE_FILES:
        assert isinstance(load_rules(name), dict), name


def test_risk_level_boundaries():
    assert risk_level(0.29) == "green"
    assert risk_level(0.30) == "amber"
    assert risk_level(0.59) == "amber"
    assert risk_level(0.60) == "red"


def test_actions_catalog_ids():
    ids = [a["id"] for a in load_rules("actions")["actions"]]
    assert ids == [
        "save_on_payday", "split_remittance", "digital_pay_instead_of_cashout",
        "cheaper_route", "pause_paisa_saving", "trim_discretionary",
        "dps_ready", "eid_weekly_saving", "daily_limit",
    ]


def test_fees_marked_placeholder():
    assert load_rules("fees")["placeholder"] is True


def test_readiness_disclaimer_verbatim():
    assert load_rules("readiness")["disclaimer_bn"] == (
        "এটা শুধু তোমার নিজের বোঝার জন্য। এটা কোনো ঋণের সিদ্ধান্ত বা score নয়, "
        "upay এটা দিয়ে কোনো সিদ্ধান্ত নেয় না।"
    )


def test_forbidden_phrases_present():
    phrases = forbidden_phrases()
    for p in ["অনুমোদিত", "ঋণ পাবেন", "ঋণ পাবে", "তুমি যোগ্য",
              "approved", "you qualify", "loan offer", "credit score"]:
        assert p in phrases
