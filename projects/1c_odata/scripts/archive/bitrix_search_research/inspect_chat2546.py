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

# 1. Check messages in chat2546 (from task 1396)
msgs = b24('im.dialog.messages.get', {'DIALOG_ID': 'chat2546', 'LIMIT': 50})
print('=== CHAT 2546 MESSAGES ===')
if msgs and 'result' in msgs:
    for m in msgs['result'].get('messages', []):
        print(f"[{m.get('date')}] User {m.get('author_id')}: {m.get('text')}")
else:
    print(msgs)

# 2. Check task 1152
t1152 = b24('tasks.task.get', {'taskId': 1152, 'select': ['*', 'UF_*']})
print('\n=== TASK 1152 ===')
if t1152 and 'result' in t1152:
    t = t1152['result']['task']
    print('Title:', t.get('title'))
    print('Created:', t.get('createdDate'))
    print('Desc:', t.get('description'))
    print('ChatId:', t.get('chatId'))
    if t.get('chatId'):
        m1152 = b24('im.dialog.messages.get', {'DIALOG_ID': f"chat{t.get('chatId')}", 'LIMIT': 50})
        print(f"Messages count in chat{t.get('chatId')}: {len(m1152.get('result', {}).get('messages', []))}")
        for m in m1152.get('result', {}).get('messages', [])[:10]:
            print(f"  [{m.get('date')}] {m.get('author_id')}: {m.get('text')[:100]}")
