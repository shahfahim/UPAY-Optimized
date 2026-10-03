import subprocess
import time
import urllib.request
import socket

p = subprocess.Popen(["backend\\.venv\\Scripts\\python.exe", "-m", "uvicorn", "hishab.api.main:create_app", "--factory", "--port", "8000"])

for _ in range(20):
    try:
        with socket.create_connection(("127.0.0.1", 8000), timeout=1):
            break
    except OSError:
        time.sleep(0.5)

try:
    req = urllib.request.urlopen('http://localhost:8000/users/demo1/savings')
    raw = req.read().decode('utf-8')
    print("RAW:", raw[:200])
finally:
    p.terminate()
