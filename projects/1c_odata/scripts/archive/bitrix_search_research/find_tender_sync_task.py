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

# Fetch all tasks created since July 1, 2026 to September 25, 2026
print("Fetching human tasks...")
human_tasks = []
start = 0
while True:
    res = b24_call("tasks.task.list", {
        "filter": {
            ">=CREATED_DATE": "2026-07-01T00:00:00+03:00",
            "<=CREATED_DATE": "2026-09-30T23:59:59+03:00"
        },
        "select": ["ID", "TITLE", "CREATED_DATE", "CREATED_BY", "RESPONSIBLE_ID", "ACCOMPLICES", "AUDITORS", "DESCRIPTION", "GROUP_ID", "STATUS"],
        "order": {"ID": "DESC"},
        "start": start
    })
    if not res or "result" not in res or "tasks" not in res["result"]:
        break
    tasks = res["result"]["tasks"]
    if not tasks:
        break
    for t in tasks:
        title = t.get("title", "")
        # Filter out obvious automated parser tasks
        if title.startswith("=Проанализировать") or title.startswith("=Тендер с суммой") or "货物物流" in title:
            continue
        human_tasks.append(t)
    if "next" in res:
        start = res["next"]
    else:
        break

print(f"Found {len(human_tasks)} human/non-automated tasks.")

# Inspect them
candidate_matches = []
for t in human_tasks:
    tid = t.get("id")
    title = (t.get("title") or "")
    desc = (t.get("description") or "")
    comb = (title + " " + desc).lower()
    
    accomplices = set(str(x) for x in t.get("accomplices") or [])
    auditors = set(str(x) for x in t.get("auditors") or [])
    uids = accomplices.union(auditors)
    uids.add(str(t.get("createdBy", "")))
    uids.add(str(t.get("responsibleId", "")))
    target_match = uids.intersection({'14', '16', '20', '38'})
    
    # We want to check for tender selection, protocols, meetings, calls, twice a week, etc.
    keywords = ["созвон", "совещан", "протокол", "планерк", "выборк", "отбор", "аукцион", "не брать", "брать", "два раза", "2 раза", "недел", "тендер"]
    matched_kws = [k for k in keywords if k in comb]
    
    # Let's check comments for all tasks where target_match >= 2 or matched_kws >= 2
    if len(target_match) >= 2 or len(matched_kws) >= 2:
        candidate_matches.append((t, target_match, matched_kws))

print(f"Candidate tasks count: {len(candidate_matches)}")

for t, target_match, matched_kws in candidate_matches:
    tid = t.get("id")
    c_res = b24_call("task.commentitem.getlist", [tid])
    comments = c_res.get("result", []) if (c_res and "result" in c_res) else []
    
    print(f"\n==========================================")
    print(f"TASK #{tid} | Status: {t.get('status')} | Created: {t.get('createdDate')}")
    print(f"Title: {t.get('title')}")
    print(f"Created By: {t.get('createdBy')} | Resp: {t.get('responsibleId')} | Target Members ({len(target_match)}): {target_match}")
    print(f"Matched KWs: {matched_kws}")
    print(f"Comments count: {len(comments)}")
    if t.get('description'):
        print(f"Description snippet: {t.get('description')[:300]}")
    if comments:
        print(f"--- Comments ({len(comments)}) ---")
        for c in comments:
            msg = c.get('POST_MESSAGE', '')
            print(f"  [{c.get('POST_DATE')}] {c.get('AUTHOR_NAME')}: {msg[:200]}...")
