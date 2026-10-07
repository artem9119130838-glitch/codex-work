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

# Search tasks with "АСТ" or "ГОЗ" in title
print("=== SEARCHING TASKS WITH 'АСТ' OR 'ГОЗ' ===")
res = b24('tasks.task.list', {
    'filter': {
        '%TITLE': 'АСТ'
    },
    'select': ['ID', 'TITLE', 'CREATED_DATE', 'CREATED_BY', 'RESPONSIBLE_ID', 'CHAT_ID', 'STATUS', 'DESCRIPTION'],
    'order': {'ID': 'DESC'}
})

for t in res.get('result', {}).get('tasks', []):
    print(f"Task #{t.get('id')} [{t.get('createdDate')}] Status {t.get('status')}: {t.get('title')}")
    print(f"  ChatId: {t.get('chatId')}, Resp: {t.get('responsibleId')}, CreatedBy: {t.get('createdBy')}")

# Also search %TITLE: ГОЗ
res2 = b24('tasks.task.list', {
    'filter': {
        '%TITLE': 'ГОЗ'
    },
    'select': ['ID', 'TITLE', 'CREATED_DATE', 'CREATED_BY', 'RESPONSIBLE_ID', 'CHAT_ID', 'STATUS', 'DESCRIPTION'],
    'order': {'ID': 'DESC'}
})
for t in res2.get('result', {}).get('tasks', []):
    print(f"Task #{t.get('id')} [{t.get('createdDate')}] Status {t.get('status')}: {t.get('title')}")
    print(f"  ChatId: {t.get('chatId')}, Resp: {t.get('responsibleId')}, CreatedBy: {t.get('createdBy')}")
