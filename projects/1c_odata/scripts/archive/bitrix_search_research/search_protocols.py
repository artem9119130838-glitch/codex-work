# -*- coding: utf-8 -*-
import os, sys, json, urllib.request

sys.stdout.reconfigure(encoding='utf-8')
webhook = os.getenv("BITRIX24_WEBHOOK_URL", "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/").rstrip("/") + "/"

def b24_call(method, params=None):
    url = webhook + method
    data = json.dumps(params or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error {method}: {e}")
        return None

# 1. Search in chat474 messages (Текущая работа АСТ ГОЗ)
print("=== 1. SEARCHING IN CHAT 474 (Текущая работа АСТ ГОЗ) ===")
# Fetch recent messages from chat474
c_res = b24_call("im.dialog.messages.get", {"DIALOG_ID": "chat474", "LIMIT": 100})
if c_res and "result" in c_res:
    msgs = c_res["result"].get("messages", [])
    users = {str(u["id"]): f"{u.get('name')} {u.get('last_name')}" for u in c_res["result"].get("users", [])}
    print(f"Fetched {len(msgs)} messages from chat474")
    for m in msgs:
        text = m.get("text", "")
        if any(w in text.lower() for w in ["созвон", "протокол", "два раза", "не брать", "брать", "анжелик", "совещан", "вторник", "четверг", "понедельник", "пятниц"]):
            author = users.get(str(m.get("author_id")), str(m.get("author_id")))
            print(f"[{m.get('date')}] {author} (msg #{m.get('id')}):")
            print(f"  {text[:300]}")
            print("-" * 50)

# 2. Search for tasks with comments!
print("\n=== 2. SEARCHING TASKS WITH COMMENTS (>= 1) CREATED IN AUG-SEP 2026 ===")
tasks_res = b24_call("tasks.task.list", {
    "filter": {
        ">=CREATED_DATE": "2026-08-01T00:00:00+03:00",
        ">COMMENTS_COUNT": 0
    },
    "select": ["ID", "TITLE", "CREATED_DATE", "CREATED_BY", "RESPONSIBLE_ID", "COMMENTS_COUNT", "DESCRIPTION"]
})

if tasks_res and "result" in tasks_res and "tasks" in tasks_res["result"]:
    print(f"Found {len(tasks_res['result']['tasks'])} tasks with comments!")
    for t in tasks_res["result"]["tasks"]:
        print(f"Task #{t.get('id')} [{t.get('createdDate')}] Comments: {t.get('commentsCount')} | {t.get('title')}")
        # Fetch comments
        comments = b24_call("task.commentitem.getlist", [t.get("id")])
        if comments and "result" in comments:
            for c in comments["result"]:
                post_text = c.get("POST_MESSAGE", "")
                if any(w in post_text.lower() for w in ["тендер", "аукцион", "брать", "созвон", "протокол", "не брать", "отказ", "пас"]):
                    print(f"   -> Comment by {c.get('AUTHOR_NAME')} [{c.get('POST_DATE')}]: {post_text[:150]}...")
