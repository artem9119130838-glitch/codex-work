# -*- coding: utf-8 -*-
import os, sys, json, urllib.request

sys.stdout.reconfigure(encoding='utf-8')
webhook = os.getenv("BITRIX24_WEBHOOK_URL", "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/").rstrip("/") + "/"

def b24(method, params=None):
    req = urllib.request.Request(webhook + method, data=json.dumps(params or {}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

# 1. Inspect Chat 1 (Artem)
print("=== CHAT 1 (ARTEM) RECENT MESSAGES ===")
res1 = b24('im.dialog.messages.get', {'DIALOG_ID': '1', 'LIMIT': 20})
for m in res1.get('result', {}).get('messages', []):
    print(f"[{m.get('date')}] From {m.get('author_id')}: {m.get('text')}")

# 2. Inspect chat474 (Текущая работа АСТ ГОЗ)
print("\n=== CHAT 474 (ТЕКУЩАЯ РАБОТА АСТ ГОЗ) MESSAGES ===")
res474 = b24('im.dialog.messages.get', {'DIALOG_ID': 'chat474', 'LIMIT': 50})
msgs474 = res474.get('result', {}).get('messages', [])
print(f"Found {len(msgs474)} messages in chat474")
for m in msgs474:
    text = m.get('text', '')
    if any(k in text.lower() for k in ['созвон', 'совещан', 'протокол', 'планерк', 'выбор', 'отбор', 'не брать', 'брать', 'два раза', '2 раза', 'аукцион', 'анжелик', 'азат', 'сауле', 'александр']):
        print(f"[{m.get('date')}] User {m.get('author_id')}: {text[:250]}")

# 3. Check what other group chats exist with "Тендер" or "ГОЗ" or "Созвон" in title
print("\n=== ALL GROUP CHATS SEARCH ===")
# Let's check im.chat.get or list of chats
# We can search dialogs from recent or brute search
