import subprocess
import time
import urllib.request
import json
import socket

p = subprocess.Popen(["backend\\.venv\\Scripts\\python.exe", "-m", "uvicorn", "hishab.api.main:create_app", "--factory", "--port", "8000"])

for _ in range(20):
    try:
        with socket.create_connection(("127.0.0.1", 8000), timeout=1):
            break
    except OSError:
        time.sleep(0.5)

try:
    req = urllib.request.urlopen('http://localhost:8000/api/users/demo1/savings')
    data = json.loads(req.read().decode())
    for p_info in data['pockets']:
        try:
            print(p_info['name'], '->', p_info['name_bn'].encode('cp1252', errors='replace').decode('cp1252'))
        except:
            print(p_info['name'], '->', p_info['name_bn'])
finally:
    p.terminate()
