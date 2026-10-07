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

# 1. Let's find all group chats where 38, 20, 16, 14 are members
# Let's inspect im.recent.get again or test im.chat.get for IDs
print("=== SCANNING RECENT DIALOGS FOR GROUP CHATS WITH TENDER MEMBERS ===")
recent = b24('im.recent.get')
chats = []
if recent and 'result' in recent:
    for item in recent['result']:
        if item.get('type') == 'chat':
            chats.append((item.get('id'), item.get('title'), item.get('message', {}).get('date')))

print(f"Total recent group chats: {len(chats)}")
for cid, title, dt in chats:
    # Get chat info
    chat_num = str(cid).replace('chat', '')
    c_info = b24('im.chat.get', {'ENTITY_ID': chat_num})
    # If entity_id doesn't work, just get messages
    msgs = b24('im.dialog.messages.get', {'DIALOG_ID': cid, 'LIMIT': 5})
    msg_users = set(m.get('author_id') for m in msgs.get('result', {}).get('messages', []))
    target_overlap = msg_users.intersection({14, 16, 20, 38})
    if target_overlap or any(w in (title or '').lower() for w in ['тендер', 'аст', 'гоз', 'созвон', 'планерка', 'совещание', 'протокол']):
        print(f"\nCHAT {cid} '{title}' (Overlap: {target_overlap}):")
        for m in msgs.get('result', {}).get('messages', [])[:3]:
            print(f"   [{m.get('date')}] User {m.get('author_id')}: {m.get('text')[:100]}")

# 2. Check Task #3580 and Task #2102 and Task #3868 chats
print("\n=== TASK SPECIFIC CHATS ===")
for tid in [3868, 3580, 2102, 1396, 1152]:
    t = b24('tasks.task.get', {'taskId': tid})
    if t and 'result' in t:
        task = t['result']['task']
        chat_id = task.get('chatId')
        print(f"Task #{tid} '{task.get('title')}' -> ChatId: {chat_id}")
        if chat_id:
            m = b24('im.dialog.messages.get', {'DIALOG_ID': f"chat{chat_id}", 'LIMIT': 10})
            mlist = m.get('result', {}).get('messages', [])
            print(f"  Messages in chat{chat_id}: {len(mlist)}")
            for msg in mlist[:5]:
                print(f"    [{msg.get('date')}] User {msg.get('author_id')}: {msg.get('text')[:120]}")
