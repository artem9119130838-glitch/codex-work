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

# Fetch tasks created between 2026-08-01 and 2026-09-10
all_tasks = []
start = 0
while True:
    res = b24_call("tasks.task.list", {
        "filter": {
            ">=CREATED_DATE": "2026-08-01T00:00:00+03:00",
            "<=CREATED_DATE": "2026-09-15T23:59:59+03:00"
        },
        "select": ["ID", "TITLE", "CREATED_DATE", "CREATED_BY", "RESPONSIBLE_ID", "ACCOMPLICES", "AUDITORS", "DESCRIPTION", "GROUP_ID"],
        "order": {"CREATED_DATE": "ASC"},
        "start": start
    })
    if not res or "result" not in res or "tasks" not in res["result"]:
        break
    tasks = res["result"]["tasks"]
    if not tasks:
        break
    all_tasks.extend(tasks)
    if "next" in res:
        start = res["next"]
    else:
        break

print(f"Fetched {len(all_tasks)} tasks from Aug 1 to Sep 15.")

# Now let's check tasks whose title has "тендер", "аукцион", "совещан", "созвон", "отбор", "выборк", "планерк", "согласован", "протокол", "результат", "проверить"
candidates = []
for t in all_tasks:
    title = (t.get("title") or "").lower()
    desc = (t.get("description") or "").lower()
    comb = title + " " + desc
    
    # Check if any keywords match
    if any(w in comb for w in ["созвон", "протокол", "совещан", "аукцион", "выборк", "отбор", "не брать", "брать", "планерк"]):
        candidates.append(t)
    elif any(w in title for w in ["тендер", "аукцион", "план", "результат"]):
        candidates.append(t)

print(f"Candidates based on title/desc keywords: {len(candidates)}")

# Now for each candidate, check comments count and content!
matching_comment_tasks = []
for idx, t in enumerate(candidates):
    tid = t.get("id")
    c_res = b24_call("task.commentitem.getlist", [tid])
    if c_res and "result" in c_res and len(c_res["result"]) > 0:
        comments = c_res["result"]
        # Check if comments contain protocol words or discussions
        comment_texts = " ".join([c.get("POST_MESSAGE", "") for c in comments])
        print(f"\n[FOUND COMMENTS] Task #{tid} [{t.get('createdDate')}]: {t.get('title')}")
        print(f"  Creator: {t.get('createdBy')} | Resp: {t.get('responsibleId')} | Comments: {len(comments)}")
        for c in comments:
            post_msg = c.get("POST_MESSAGE", "")
            author = c.get("AUTHOR_NAME", "")
            date = c.get("POST_DATE", "")
            print(f"    - [{date}] {author}: {post_msg[:120]}...")
            if any(w in post_msg.lower() for w in ["брать", "не брать", "созвон", "протокол", "тендер", "аукцион", "отказ", "пас"]):
                matching_comment_tasks.append((t, c))

print(f"\nDone scanning comments. Tasks with relevant comments: {len(matching_comment_tasks)}")
