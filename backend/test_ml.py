import sys
import os

# append the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from hishab.ml_engine import predict_intent

queries = [
    "amar overview ta dao to",
    "amar total hisab dao",
    "keno",
    "hisab dao"
]

for q in queries:
    print(f"Query: {q} -> Intent: {predict_intent(q)}")

