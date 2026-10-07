# -*- coding: utf-8 -*-
import os, sys, json, urllib.request, urllib.parse

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

print("=== 1. FETCHING BITRIX24 USERS ===")
u_res = b24_call("user.get")
users = {}
if u_res and "result" in u_res:
    for u in u_res["result"]:
        uid = str(u.get("ID"))
        name = f"{u.get('NAME', '')} {u.get('LAST_NAME', '')}".strip()
        users[uid] = name
        if any(n in name.lower() for n in ["анжелик", "азат", "александр", "саул"]):
            print(f"User ID {uid}: {name} ({u.get('WORK_POSITION', '')})")

print("\n=== 2. FETCHING TASKS FROM 2026-07-01 ===")
start = 0
all_tasks = []
while True:
    t_res = b24_call("tasks.task.list", {
        "filter": {
            ">=CREATED_DATE": "2026-07-01T00:00:00+03:00"
        },
        "select": ["ID", "TITLE", "CREATED_DATE", "RESPONSIBLE_ID", "CREATED_BY", "GROUP_ID", "COMMENTS_COUNT", "DESCRIPTION", "ACCOMPLICES", "AUDITORS"],
        "order": {"CREATED_DATE": "DESC"},
        "start": start
    })
    if not t_res or "result" not in t_res or "tasks" not in t_res["result"]:
        break
    tasks_batch = t_res["result"]["tasks"]
    if not tasks_batch:
        break
    all_tasks.extend(tasks_batch)
    if "next" in t_res:
        start = t_res["next"]
    else:
        break

print(f"Total tasks fetched: {len(all_tasks)}")

# Score and filter candidate tasks
matches = []
for t in all_tasks:
    tid = t.get("id")
    title = t.get("title", "") or ""
    desc = t.get("description", "") or ""
    comments_cnt = int(t.get("commentsCount", 0) or 0)
    comb = (title + " " + desc).lower()
    
    # Check keywords
    kw_hits = []
    for kw in ["тендер", "аукцион", "созвон", "совещан", "протокол", "отбор", "выборк", "планерк", "встреч", "анжелик", "азат", "саул", "александр", "не брать", "брать", "два раза в неделю", "совещани"]:
        if kw in comb:
            kw_hits.append(kw)
            
    # Also check if it has lots of comments (often meeting protocols are in comments!)
    matches.append({
        "task": t,
        "score": len(kw_hits),
        "kw_hits": kw_hits,
        "comments_cnt": comments_cnt
    })

# Sort by score and comments
matches.sort(key=lambda x: (x["score"], x["comments_cnt"]), reverse=True)

print("\n=== TOP 20 CANDIDATE TASKS ===")
for m in matches[:20]:
    t = m["task"]
    resp_name = users.get(str(t.get("responsibleId")), str(t.get("responsibleId")))
    creator_name = users.get(str(t.get("createdBy")), str(t.get("createdBy")))
    print(f"\nTask #{t.get('id')} [Created: {t.get('createdDate')}] Score: {m['score']} (Hits: {m['kw_hits']}) | Comments: {m['comments_cnt']}")
    print(f"  Title: {t.get('title')}")
    print(f"  Creator: {creator_name} | Resp: {resp_name}")
    if t.get('description'):
        print(f"  Desc: {t.get('description')[:200]}...")
