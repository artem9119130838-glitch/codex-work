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

# 1. Get recent dialogs
print("=== RECENT CHATS ===")
recent = b24('im.recent.get')
if recent and 'result' in recent:
    for item in recent['result']:
        cid = item.get('id')
        title = item.get('title')
        msg = item.get('message', {}).get('text', '')
        date = item.get('message', {}).get('date', '')
        chat_type = item.get('type')
        print(f"Chat {cid} [{chat_type}] '{title}': {msg[:100]} ({date})")

# 2. Search for tasks created between 2026-08-01 and 2026-09-01 that have task chats with messages
print("\n=== SEARCHING TASKS WITH TASK CHATS IN AUGUST ===")
tasks_res = b24('tasks.task.list', {
    'filter': {
        '>=CREATED_DATE': '2026-08-01T00:00:00+03:00',
        '<=CREATED_DATE': '2026-09-05T23:59:59+03:00'
    },
    'select': ['ID', 'TITLE', 'CREATED_DATE', 'CREATED_BY', 'RESPONSIBLE_ID', 'CHAT_ID', 'ACCOMPLICES', 'AUDITORS', 'DESCRIPTION'],
    'order': {'ID': 'DESC'}
})

tasks = tasks_res.get('result', {}).get('tasks', [])
print(f"Found {len(tasks)} tasks.")
for t in tasks:
    chat_id = t.get('chatId')
    title = t.get('title', '')
    desc = t.get('description', '')
    comb = (title + " " + desc).lower()
    
    # Check if mentions Angelica, Azat, Alexandra, Saule or sync / calls
    if any(k in comb for k in ['созвон', 'совещан', 'протокол', 'планерк', 'выбор', 'отбор', 'аукцион', 'два раза', '2 раза', 'тендер', 'павлова', 'денишов', 'пономарева', 'бестова']) or chat_id:
        if title.startswith('=Проанализировать') or title.startswith('=Тендер'):
            continue
        print(f"\nTask #{t.get('id')} [{t.get('createdDate')}] Title: {title}")
        print(f"  CreatedBy: {t.get('createdBy')}, Resp: {t.get('responsibleId')}, ChatId: {chat_id}")
        if desc:
            print(f"  Desc: {desc[:200]}")
        if chat_id:
            cmsgs = b24('im.dialog.messages.get', {'DIALOG_ID': f"chat{chat_id}", 'LIMIT': 5})
            m_list = cmsgs.get('result', {}).get('messages', [])
            print(f"  Messages in chat{chat_id}: {len(m_list)}")
            for m in m_list:
                print(f"    [{m.get('date')}] User {m.get('author_id')}: {m.get('text')[:120]}")
