import urllib.request
try:
    req = urllib.request.Request("https://www.upaybd.com/images/logo.png", method="HEAD")
    res = urllib.request.urlopen(req, timeout=3)
    print("logo.png exists:", res.status)
except Exception as e:
    print("logo.png error:", e)

try:
    req = urllib.request.Request("https://www.upaybd.com/assets/images/logo.png", method="HEAD")
    res = urllib.request.urlopen(req, timeout=3)
    print("assets logo.png exists:", res.status)
except Exception as e:
    print("assets logo.png error:", e)
