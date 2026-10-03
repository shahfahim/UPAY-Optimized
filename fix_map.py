import re

with open('web/src/pages/hub/AgentLocator.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace iframe src
# I will use a robust regex to replace the entire iframe tag
old_pattern = r'<iframe[^>]*src=\{`https://www\.openstreetmap\.org/export/embed\.html[^`]+`\}[^>]*></iframe>'
new_iframe = """<iframe
                        width="100%"
                        height="100%"
                        frameBorder="0"
                        src={`https://www.google.com/maps?q=${agent.lat},${agent.lng}&z=16&output=embed`}
                        style={{ border: 0 }}
                        allowFullScreen
                      ></iframe>"""

code = re.sub(old_pattern, new_iframe, code)

with open('web/src/pages/hub/AgentLocator.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated map to use Google Maps Embed!")
