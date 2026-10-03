import re

with open('web/src/pages/hub/AgentLocator.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_url = r"src=\{`https://www\.google\.com/maps\?q=\$\{agent\.lat\},\$\{agent\.lng\}&z=16&output=embed`\}"
new_url = r"src={`https://www.google.com/maps?saddr=${location?.lat},${location?.lng}&daddr=${agent.lat},${agent.lng}&output=embed`}"

code = re.sub(old_url, new_url, code)

with open('web/src/pages/hub/AgentLocator.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Map updated to show directions from User to Agent!")
