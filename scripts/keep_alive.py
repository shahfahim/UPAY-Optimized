"""
keep_alive.py — Koyeb free tier এ sleep হওয়া ঠেকাতে প্রতি ৪৫ মিনিটে /api/health ping করে।

Usage:
    python scripts/keep_alive.py https://your-app.koyeb.app
    
    # অথবা background এ চালাও (local machine চালু থাকলে):
    python scripts/keep_alive.py https://your-app.koyeb.app &
"""

import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

def ping(url: str) -> bool:
    try:
        with urllib.request.urlopen(url + "/api/health", timeout=15) as r:
            status = r.status
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {status} — awake")
            return True
    except urllib.error.URLError as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ ping failed: {e}")
        return False

if __name__ == "__main__":
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"
    interval = 45 * 60  # 45 minutes
    print(f"🔔 Keep-alive started → {base_url}/api/health (every {interval//60} min)")
    while True:
        ping(base_url)
        time.sleep(interval)
