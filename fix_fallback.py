with open('backend/hishab/llm/fallback.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix transaction_route
code = code.replace('npsb.*tk|npsb.*taka|npsb korba', 'npsb.*????|npsb ???')

# Fix ack
code = code.replace('|thanks|thank you|???????|dhonnobad|jajakallah|???????', '|^thanks$|^thank you$|^???????$|^dhonnobad$|^jajakallah$|^???????$')
code = code.replace('|got it|understood|bujhechi|??????|noted|??????', '|^got it$|^understood$|^bujhechi$|^??????$|^noted$|^??????$')

# Fix memory leak
target_memory = '_user_memory: dict[str, dict] = {}'
if target_memory not in code:
    target_memory = '_user_memory = {}'

replacement_memory = '''_user_memory = {}
def _get_memory(uid: str):
    if len(_user_memory) > 1000:
        _user_memory.clear() # Basic OOM protection
    return _user_memory.setdefault(uid, {})'''

if target_memory in code:
    code = code.replace(target_memory, replacement_memory)
    code = code.replace('_user_memory.setdefault(uid, {})', '_get_memory(uid)')
    code = code.replace('_user_memory[uid]', '_get_memory(uid)')

with open('backend/hishab/llm/fallback.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('fallback.py fixed')
