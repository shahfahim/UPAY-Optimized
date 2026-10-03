import sys
import urllib.request
import json
req = urllib.request.urlopen('http://localhost:8000/users/demo1/savings')
data = json.loads(req.read().decode())
for p in data['pockets']:
    print(p['name'], '->', p['name_bn'])
