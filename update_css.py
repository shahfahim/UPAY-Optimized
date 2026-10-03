import re

css_path = r"e:\AI Hackathon DIU-2026\web\src\index.css"

with open(css_path, "r", encoding="utf-8") as f:
    content = f.read()

new_frame_css = """\
.app-frame {
  position: relative;
  max-width: 430px;
  min-height: 100dvh;
  margin: 0 auto;
  background-color: #f4f7fb;
  background-image: 
    repeating-linear-gradient(60deg, rgba(11, 78, 162, 0.04) 0, rgba(11, 78, 162, 0.04) 1px, transparent 1px, transparent 24px),
    repeating-linear-gradient(120deg, rgba(11, 78, 162, 0.04) 0, rgba(11, 78, 162, 0.04) 1px, transparent 1px, transparent 24px);
  background-size: 100% 100%;
  display: flex;
  flex-direction: column;
}"""

content = re.sub(r"\.app-frame\s*\{[^}]+\}", new_frame_css, content, flags=re.DOTALL)

with open(css_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated index.css successfully.")
