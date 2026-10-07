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

# We can query forum comments or tasks directly.
# Let's fetch all tasks created since 2026-06-01, ordered by CREATED_DATE desc
print("=== FETCHING ALL TASKS SINCE 2026-06-01 ===")
all_tasks = []
start = 0
while True:
    res = b24_call("tasks.task.list", {
        "filter": {
            ">=CREATED_DATE": "2026-06-01T00:00:00+03:00"
        },
        "select": ["ID", "TITLE", "CREATED_DATE", "CREATED_BY", "RESPONSIBLE_ID", "ACCOMPLICES", "AUDITORS", "DESCRIPTION", "GROUP_ID"],
        "order": {"ID": "DESC"},
        "start": start
    })
    if not res or "result" not in res or "tasks" not in res["result"]:
        break
    tasks = res["result"]["tasks"]
    if not tasks:
        break
    all_tasks.extend(tasks)
    print(f"Fetched {len(all_tasks)} tasks so far (start={start})...")
    if "next" in res:
        start = res["next"]
    else:
        break

print(f"Total tasks: {len(all_tasks)}")

# Let's inspect tasks whose title has ANY words related to meetings, discussions, protocols, tenders, plans
suspects = []
for t in all_tasks:
    title = (t.get("title") or "").lower()
    desc = (t.get("description") or "").lower()
    comb = title + " " + desc
    
    # Check if multiple target users (14, 16, 20, 38) are in the task
    accomplices = set(str(x) for x in t.get("accomplices") or [])
    auditors = set(str(x) for x in t.get("auditors") or [])
    uids = accomplices.union(auditors)
    uids.add(str(t.get("createdBy", "")))
    uids.add(str(t.get("responsibleId", "")))
    target_match = uids.intersection({'14', '16', '20', '38'})
    
    # Check keywords
    kw_match = any(w in comb for w in [
        "созвон", "совещан", "протокол", "планерк", "встреч", "аукцион", 
        "выборк", "отбор", "два раза", "2 раза", "не брать", "брать", 
        "обсужден", "согласован", "комитет", "синхронизац"
    ])
    
    if len(target_match) >= 3 or (len(target_match) >= 2 and kw_match) or ("созвон" in comb or "протокол" in comb or "совещан" in comb):
        suspects.append((len(target_match), kw_match, t, target_match))

print(f"\nFound {len(suspects)} suspect tasks!")
suspects.sort(key=lambda x: (x[0], x[1]), reverse=True)

# Now check comments for top suspects
for tm_len, kw_m, t, target_match in suspects[:40]:
    tid = t.get("id")
    c_res = b24_call("task.commentitem.getlist", [tid])
    c_list = c_res.get("result", []) if (c_res and "result" in c_res) else []
    print(f"\nTask #{tid} [{t.get('createdDate')}] Title: {t.get('title')}")
    print(f"   Target members ({tm_len}): {target_match} | Comments: {len(c_list)}")
    if t.get('description'):
        print(f"   Desc: {t.get('description')[:150]}...")
    if c_list:
        for c in c_list[:5]:
            print(f"     Comment by {c.get('AUTHOR_NAME')} [{c.get('POST_DATE')}]: {c.get('POST_MESSAGE', '')[:120]}...")
        if len(c_list) > 5:
            print(f"     ... and {len(c_list) - 5} more comments!")
