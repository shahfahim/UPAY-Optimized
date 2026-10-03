import re

with open('scripts/train_ai_advanced.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add specific user examples to the training data
new_examples = """
    ("status", "amar overview ta dao to"),
    ("status", "amar total hisab dao"),
    ("status", "hisab dao"),
    ("shortfall", "keno"),
    ("shortfall", "taka kom keno"),
    ("shortfall", "masher seshe taka kom pore keno"),
    ("shortfall", "keno kom pore"),
"""
code = code.replace('("status", "amar ki khobor"),', '("status", "amar ki khobor"),' + new_examples)

with open('scripts/train_ai_advanced.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Training script updated!")
