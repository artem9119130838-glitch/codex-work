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

# 1. Inspect Task #780
print("=== TASK 780 ===")
t780 = b24('tasks.task.get', {'taskId': 780, 'select': ['*', 'UF_*']})
if t780 and 'result' in t780:
    t = t780['result']['task']
    print("Title:", t.get('title'))
    print("Created:", t.get('createdDate'))
    print("Status:", t.get('status'))
    print("Resp:", t.get('responsibleId'))
    print("CreatedBy:", t.get('createdBy'))
    print("ChatId:", t.get('chatId'))
    print("Accomplices:", t.get('accomplices'))
    print("Auditors:", t.get('auditors'))
    print("Description:\n", t.get('description'))
    
    # Check comments of task 780
    c_res = b24('task.commentitem.getlist', [780])
    comments = c_res.get('result', []) if (c_res and 'result' in c_res) else []
    print(f"Comments count in task 780: {len(comments)}")
    for c in comments:
        print(f"  [{c.get('POST_DATE')}] {c.get('AUTHOR_NAME')}: {c.get('POST_MESSAGE')[:200]}")

# 2. Check chat1504 (Chat of task 780)
print("\n=== CHAT 1504 (Task 780) ===")
m1504 = b24('im.dialog.messages.get', {'DIALOG_ID': 'chat1504', 'LIMIT': 50})
msgs = m1504.get('result', {}).get('messages', [])
print(f"Messages in chat1504: {len(msgs)}")
for m in msgs:
    print(f"[{m.get('date')}] User {m.get('author_id')}: {m.get('text')}")
