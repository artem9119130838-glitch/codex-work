import requests
import json
import os

B24_WEBHOOK = 'https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/'
resp = requests.post(f'{B24_WEBHOOK}im.dialog.messages.get', json={'DIALOG_ID': 'chat6602', 'LIMIT': 50})
data = resp.json().get('result', {})
msgs = data.get('messages', [])
users = {u['id']: (u.get('name', '') + ' ' + u.get('last_name', '')).strip() for u in data.get('users', [])}
msgs.sort(key=lambda x: x['id'])

os.makedirs('scratch', exist_ok=True)
with open('scratch/recent_b24_chat.txt', 'w', encoding='utf-8') as f:
    for m in msgs:
        dt = m.get('date', '')[:19].replace('T', ' ')
        author = users.get(m.get('author_id'), f"User {m.get('author_id')}")
        txt = m.get('text', '')
        f.write(f"[{dt}] {author} (ID {m.get('id')}):\n{txt}\n\n")

print(f"Exported {len(msgs)} messages to scratch/recent_b24_chat.txt")
