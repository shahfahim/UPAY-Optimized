import re
from hishab.llm.fallback import _INTENTS

for name, pat in _INTENTS:
    try:
        re.compile(pat)
    except re.error as e:
        print(f"Error in intent '{name}': {e} for pattern: {pat}")
