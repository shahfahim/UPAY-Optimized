with open('web/src/index.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace the background of .app-frame
old_bg = 'background: #f8fafc;'
new_bg = 'background: linear-gradient(145deg, #f0f7fc 0%, #e3eff8 100%);'
css = css.replace(old_bg, new_bg)

# Add a smooth beautiful slide transition animation for the welcome slides
css = css.replace(
    '--animate-rise: rise 400ms ease-out both;',
    '--animate-rise: rise 800ms cubic-bezier(0.16, 1, 0.3, 1) both;'
)
css = css.replace(
    '@keyframes rise {\n  from { opacity: 0; transform: translateY(8px); }\n  to { opacity: 1; transform: none; }\n}',
    '@keyframes rise {\n  0% { opacity: 0; transform: translateY(16px) scale(0.98); }\n  100% { opacity: 1; transform: none; scale: 1; }\n}'
)

with open('web/src/index.css', 'w', encoding='utf-8') as f:
    f.write(css)
print('index.css updated')
