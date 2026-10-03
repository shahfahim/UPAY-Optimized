import re
import sys
from hishab.llm.fallback import _INTENTS

for name, pat in _INTENTS:
    try:
        re.compile(pat)
    except re.error as e:
        print(f"Error in intent '{name}': {e}")
        print(f"Pattern snippet: {pat.encode('utf-8', 'ignore')}")
