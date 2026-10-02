import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('backend/hishab/llm/fallback.py', encoding='utf-8') as f:
    lines = f.readlines()

# Line 199 is "    else:\n" and line 200 is the text we want to replace
# (0-indexed: lines[198] and lines[199])
# Verify
print("Line 199:", repr(lines[198]))
print("Line 200:", repr(lines[199]))

NOTIFICATION_BLOCK = [
    '    elif intent == "notification":\n',
    '        h = tool("get_home_summary")\n',
    '        if h["insufficient_history"]:\n',
    '            text = "\u09b9\u09bf\u09b8\u09be\u09ac \u09a6\u09c7\u0996\u09be\u09a4\u09c7 \u0986\u09b0\u09cb \u0995\u09bf\u099b\u09c1 \u09a6\u09bf\u09a8\u09c7\u09b0 \u09b2\u09c7\u09a8\u09a6\u09c7\u09a8 \u09b2\u09be\u0997\u09ac\u09c7।"\n',
    '        elif h["risk_level"] == "red" and h["shortfall_date"]:\n',
    '            drivers = tool("get_shortfall_drivers")["drivers"]\n',
    '            why = ", ".join(d["text_bn"] for d in drivers[:2])\n',
    '            text = f"\u098f\u0987 \u09ae\u09be\u09b8\u09c7 \u098f\u0995\u099f\u09c1 \u09b8\u09be\u09ac\u09a7\u09be\u09a8 \u09a5\u09be\u0995\u09cb \u2014 {why} \u0995\u09be\u09b0\u09a3\u09c7 {_day(h[\'shortfall_date\'])} \u09a6\u09bf\u0995\u09c7 \u099f\u09be\u09a8\u09be\u099f\u09be\u09a8\u09bf \u09b9\u09a4\u09c7 \u09aa\u09be\u09b0\u09c7।"\n',
    '        elif h["risk_level"] == "amber":\n',
    '            text = "\u09ae\u09be\u09b8\u09c7\u09b0 \u09b6\u09c7\u09b7 \u09a6\u09bf\u0995\u09c7 \u098f\u0995\u099f\u09c1 \u09aa\u09b0\u09bf\u0995\u09b2\u09cd\u09aa\u09a8\u09be \u0995\u09b0\u09cb \u2014 \u098f\u0996\u09a8\u0987 \u09b8\u09a4\u09b0\u09cd\u0995 \u09b9\u09b2\u09c7 \u099f\u09be\u09a8\u09be\u099f\u09be\u09a8\u09bf \u098f\u09dc\u09be\u09a8\u09cb \u09af\u09be\u09ac\u09c7।"\n',
    '        else:\n',
    '            text = "\u09ad\u09be\u09b2\u09cb \u0995\u09b0\u099b! \u09a4\u09cb\u09ae\u09be\u09b0 \u09b8\u099e\u09cd\u099a\u09af\u09bc\u09c7\u09b0 \u0985\u0997\u09cd\u09b0\u0997\u09a4\u09bf \u099c\u09be\u09a8\u09be\u09a4\u09c7 notification \u09a6\u09bf\u09af\u09bc\u09c7\u099b\u09bf।"\n',
    '    else:\n',
    '        text = "\u098f\u0987 \u09ac\u09bf\u09b7\u09af\u09bc\u09c7 \u0986\u09ae\u09be\u09b0 \u0995\u09bf\u099b\u09c1 \u099c\u09be\u09a8\u09be \u09a8\u09c7\u0987 \u2014 \u0986\u09ae\u09bf \u09b6\u09c1\u09a7\u09c1 \u09a4\u09cb\u09ae\u09be\u09b0 \u0986\u09b0\u09cd\u09a5\u09bf\u0995 \u09b9\u09bf\u09b8\u09be\u09ac \u09a8\u09bf\u09af\u09bc\u09c7 \u0995\u09be\u099c \u0995\u09b0\u09bf।"\n',
]

# Replace lines 199-200 (0-indexed 198-199) with NOTIFICATION_BLOCK
new_lines = lines[:198] + NOTIFICATION_BLOCK + lines[200:]

with open('backend/hishab/llm/fallback.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"SUCCESS: replaced lines 199-200, new total lines = {len(new_lines)}")
