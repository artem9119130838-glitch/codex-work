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

# Check Task 3868
print("=== TASK 3868 DETAILS ===")
t3868 = b24_call("tasks.task.get", {"taskId": 3868, "select": ["*"]})
if t3868 and "result" in t3868:
    t = t3868["result"]["task"]
    print("Title:", t.get("title"))
    print("Description:", t.get("description"))
    print("Created:", t.get("createdDate"))
    print("Responsible:", t.get("responsible", {}).get("name"))
    print("Auditors:", t.get("auditors"))
    print("Accomplices:", t.get("accomplices"))

# Fetch comments for task 3868
comments = b24_call("task.commentitem.getlist", [3868])
if comments and "result" in comments:
    print(f"\nComments count in 3868: {len(comments['result'])}")
    for c in comments["result"]:
        print(f"[{c.get('POST_DATE')}] Author {c.get('AUTHOR_NAME')}:")
        print(c.get("POST_MESSAGE"))
        print("-" * 50)

# Also search all tasks for keywords "созвон" or "протокол" or "аукцион" or "выборк"
print("\n=== SEARCHING ALL TASKS FOR 'созвон' OR 'протокол' OR 'аукцион' ===")
res = b24_call("tasks.task.list", {
    "filter": {
        ">=CREATED_DATE": "2026-07-01T00:00:00+03:00"
    },
    "select": ["ID", "TITLE", "CREATED_DATE", "COMMENTS_COUNT", "DESCRIPTION"]
})

if res and "result" in res and "tasks" in res["result"]:
    for task in res["result"]["tasks"]:
        comb = (task.get("title", "") + " " + (task.get("description", "") or "")).lower()
        if any(w in comb for w in ["созвон", "протокол", "два раза в неделю", "аукцион", "брать, а какие", "какие брать", "совещан"]):
            print(f"Task #{task.get('id')} [{task.get('createdDate')}]: {task.get('title')}")
            print(f"  Desc: {(task.get('description') or '')[:200]}")
            print(f"  Comments: {task.get('commentsCount')}")
            print("="*50)
