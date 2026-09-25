import urllib.request
import json
import urllib.parse
import sys

sys.stdout.reconfigure(encoding='utf-8')
webhook = 'https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/'

def b24_call(method, params=None):
    url = webhook + method
    data = None
    if params:
        data = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

print("==================================================")
print("1. DIALOG_ID=1 (Personal chat / 'Заметки' Артема)")
print("==================================================")
res1 = b24_call('im.dialog.messages.get', {'DIALOG_ID': 1, 'LIMIT': 50})
msgs1 = res1.get('result', {}).get('messages', [])
users1 = {str(u['id']): u.get('name') for u in res1.get('result', {}).get('users', [])}
print(f"Total messages fetched: {len(msgs1)}")
for m in msgs1:
    author = users1.get(str(m.get('author_id')), str(m.get('author_id')))
    print(f"[{m.get('date')}] {author} (ID {m.get('author_id')}):")
    print(m.get('text'))
    print("-" * 40)

print("\n==================================================")
print("2. Task 1876 Chat (chatId: 3452, 'Штрафы')")
print("==================================================")
res2 = b24_call('im.dialog.messages.get', {'DIALOG_ID': 'chat3452', 'LIMIT': 50})
msgs2 = res2.get('result', {}).get('messages', [])
users2 = {str(u['id']): u.get('name') for u in res2.get('result', {}).get('users', [])}
print(f"Total messages fetched: {len(msgs2)}")
for m in msgs2:
    author = users2.get(str(m.get('author_id')), str(m.get('author_id')))
    print(f"[{m.get('date')}] {author} (ID {m.get('author_id')}):")
    print(m.get('text'))
    print("-" * 40)
