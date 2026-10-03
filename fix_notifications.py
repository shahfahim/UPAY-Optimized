import re

with open('backend/hishab/engine/notifications.py', 'r', encoding='utf-8') as f:
    code = f.read()

# I will rewrite the message_strip function to only include shortcuts, levels, and lessons.
new_func = '''def message_strip(ctx, risk, safe_today: float, budget_daily: float, shortcuts: list, lesson, level,
                  next_income: date | None) -> list[StripMessage]:
    msgs: list[StripMessage] = []
    
    for s in shortcuts:
        if s.due_in_days:
            msgs.append(StripMessage(2, f"{s.name} {bn_num(s.due_in_days)} দিনের মধ্যে দিতে হবে",
                                     f"{s.name} due in {s.due_in_days} days", "/app/home"))
            break
            
    if level is not None and level.next_level == 1 and level.projection_days:
        msgs.append(StripMessage(5, f"সঞ্চয় লেভেল ১ আর {bn_num(level.projection_days)} দিন দূরে",
                                 f"Savings level 1 is {level.projection_days} days away", "/app/savings/levels"))
    elif lesson is not None:
        msgs.append(StripMessage(5, lesson.title_bn, lesson.title_bn, "/app/hishab/learn"))
        
    msgs.sort(key=lambda m: m.priority)
    return msgs
'''

code = re.sub(r'def message_strip\(.*?\)\s*->\s*list\[StripMessage\]:.*?return msgs', new_func, code, flags=re.DOTALL)

with open('backend/hishab/engine/notifications.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Notifications updated')
