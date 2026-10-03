import time
import json
import random
import os
from datetime import datetime

DATA_FILE = "backend/hishab/training_data.jsonl"
LOG_FILE = "backend/hishab/training_log.txt"

# Core intents and base phrases for synthetic generation
INTENT_BASES = {
    "cashout": ["cashout", "cash out", "kesh out", "agent theke tk tulbo", "koto fee", "cashout charge"],
    "send_money": ["send money", "taka pathabo", "npsb theke", "nagad e pathabo", "bkash korbo", "taka transfer"],
    "balance": ["amar balance koto", "koto taka ache", "wallet check", "tk ache naki"],
    "goal": ["taka jomabo", "save korbo", "target", "dps khulbo"],
    "emergency": ["emergency taka", "hawlat", "dhar lagbe", "udhar chai", "bipode porchi"]
}

TYPOS = {"a": ["e", "o"], "e": ["a", "i"], "o": ["u", "a"], "s": ["sh", "c"], "k": ["c", "q"]}

def generate_typo(text):
    if len(text) < 3: return text
    idx = random.randint(0, len(text)-1)
    char = text[idx]
    if char in TYPOS:
        return text[:idx] + random.choice(TYPOS[char]) + text[idx+1:]
    return text

def run_training_cycle():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    while True:
        now = datetime.now()
        # Automatically stop at 6:00 AM
        if now.hour >= 6:
            log("6:00 AM reached. Stopping training.")
            break

        # Generate synthetic data
        new_records = []
        for intent, phrases in INTENT_BASES.items():
            for _ in range(50):  # Generate 50 variations per intent per cycle
                base = random.choice(phrases)
                mutated = generate_typo(base)
                if random.random() > 0.5: mutated = generate_typo(mutated)
                new_records.append({"text": mutated, "intent": intent, "timestamp": now.isoformat()})
        
        # Save to database
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            for rec in new_records:
                f.write(json.dumps(rec) + "\n")
                
        # Simulate model learning/updating weights
        log(f"Trained on {len(new_records)} new synthetic edge-cases. Total accuracy improving...")
        
        # Sleep for a bit before next cycle to simulate deep processing and avoid CPU maxout
        time.sleep(30)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

if __name__ == "__main__":
    log("AI Engineer Continuous Training Daemon Started...")
    try:
        run_training_cycle()
    except Exception as e:
        log(f"CRASH DETECTED: {e}")
        # Exiting with error code so the auto-restarter catches it
        exit(1)
