import sys
sys.path.append('backend')
from hishab.store.sqlite import UserState
import json

body = '{"pockets": {"emergency": 20040.0, "eid": 0.0, "family": 0.0, "education": 0.0, "paisa": 0.0, "custom": 0.0, "custom_1791048869033": 0.0}, "pocket_goals": {}, "custom_names": {"custom_1791048851491": "tour", "custom_1791048869033": "Tour"}, "paisa_on": false, "paisa_paused": false, "budget_mode": "auto", "manual_budget": {}, "dps": null, "notif_optout": [], "last_active": "2026-09-18"}'
st = UserState.from_json(body)

print("custom_names from st:", st.custom_names)
p = "custom_1791048869033"
print("p is:", p)
res = getattr(st, 'custom_names', {}).get(p)
print("get(p) returns:", res)
