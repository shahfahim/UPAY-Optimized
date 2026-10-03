import re

with open('web/src/index.css', 'r', encoding='utf-8') as f:
    code = f.read()

# Add button interactions
button_styles = """
/* Make all buttons feel highly responsive and tactile (iOS style) */
button, .btn, a {
  transition: transform 150ms cubic-bezier(0.16, 1, 0.3, 1), background-color 200ms ease, opacity 200ms ease, filter 200ms ease;
  touch-action: manipulation;
}
button:active:not(:disabled), a:active:not(:disabled) {
  transform: scale(0.96);
}
"""

if "button:active" not in code:
    code += button_styles

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(code)

print("index.css updated with smooth button interactions!")
