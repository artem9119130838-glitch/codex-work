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

target_uids = {'14', '16', '20', '38'}
print(f"Target UIDs: {target_uids} (Сауле, Анжелика, Азат, Александра)")

# Fetch all tasks from 2026-07-15 to 2026-09-20
start = 0
found_tasks = []

while True:
    res = b24_call("tasks.task.list", {
        "filter": {
            ">=CREATED_DATE": "2026-07-15T00:00:00+03:00",
            "<=CREATED_DATE": "2026-09-20T23:59:59+03:00"
        },
        "select": ["ID", "TITLE", "CREATED_DATE", "CREATED_BY", "RESPONSIBLE_ID", "ACCOMPLICES", "AUDITORS", "COMMENTS_COUNT", "DESCRIPTION", "GROUP_ID"],
        "start": start
    })
    if not res or "result" not in res or "tasks" not in res["result"]:
        break
    tasks = res["result"]["tasks"]
    if not tasks:
        break
    for t in tasks:
        tid = t.get("id")
        created_by = str(t.get("createdBy", ""))
        resp_id = str(t.get("responsibleId", ""))
        accomplices = set(str(x) for x in t.get("accomplices") or [])
        auditors = set(str(x) for x in t.get("auditors") or [])
        
        all_uids = accomplices.union(auditors)
        all_uids.add(created_by)
        all_uids.add(resp_id)
        
        common = all_uids.intersection(target_uids)
        # We want tasks where at least 2 or 3 of these people are involved, or where title has tender/auction/meeting keywords
        title = t.get("title", "")
        desc = t.get("description", "") or ""
        comments_cnt = int(t.get("commentsCount", 0) or 0)
        
        if len(common) >= 2 or comments_cnt > 1 or any(k in (title + desc).lower() for k in ["аукцион", "тендер", "созвон", "совещан", "протокол"]):
            found_tasks.append((len(common), comments_cnt, t, common))
            
    if "next" in res:
        start = res["next"]
    else:
        break

print(f"Total filtered candidate tasks: {len(found_tasks)}")
found_tasks.sort(key=lambda x: (x[0], x[1]), reverse=True)

for common_len, comments_cnt, t, common in found_tasks[:25]:
    print(f"\nTask #{t.get('id')} [{t.get('createdDate')}] | Involved ({common_len}): {common} | Comments: {comments_cnt}")
    print(f"  Title: {t.get('title')}")
    print(f"  Creator: {t.get('createdBy')} | Resp: {t.get('responsibleId')}")
    if t.get('description'):
        print(f"  Desc: {t.get('description')[:200]}...")
