import sys

file_path = 'backend/hishab/engine/notifications.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the budget message
old_msg = 'bn = f"এই মাসে একটু সাবধান থাকো — আর প্রায় {bn_num(days_left or 3)} দিনের বাজেট আছে"'
new_msg = 'bn = f"এই মাসে একটু সাবধান থাকো — খরচের দিকে একটু নজর দিন"'
text = text.replace(old_msg, new_msg)

# Also check if there's any other budget strip message
old_msg_2 = 'bn = f"এই মাসে একটু সাবধান থাকো - আর প্রায় {bn_num(days_left or 3)} দিনের বাজেট আছে"'
new_msg_2 = 'bn = f"এই মাসে একটু সাবধান থাকো — খরচের দিকে একটু নজর দিন"'
text = text.replace(old_msg_2, new_msg_2)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Notification banner updated.")
