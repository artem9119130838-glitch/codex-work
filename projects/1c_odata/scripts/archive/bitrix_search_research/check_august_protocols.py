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

# 1. Let's inspect Task #3868 in full detail
print("=== DETAILS OF TASK 3868 ===")
t3868 = b24_call("tasks.task.get", {"taskId": 3868, "select": ["*", "UF_*"]})
if t3868 and "result" in t3868:
    task_data = t3868["result"].get("task", {})
    print(f"Title: {task_data.get('title')}")
    print(f"Created: {task_data.get('createdDate')}")
    print(f"Description:\n{task_data.get('description')}\n")
    # Check checklist items
    cl = b24_call("tasks.task.checklistitem.getlist", {"taskId": 3868})
    print(f"Checklist items: {cl.get('result') if cl else 'none'}")

# 2. Search for tasks created around mid-August (1.5 months ago = Aug 10 - Aug 30, 2026)
print("\n=== SEARCHING TASKS CREATED IN AUGUST 2026 WITH RELEVANT WORDS ===")
aug_tasks = []
start = 0
while True:
    res = b24_call("tasks.task.list", {
        "filter": {
            ">=CREATED_DATE": "2026-08-01T00:00:00+03:00",
            "<=CREATED_DATE": "2026-09-10T23:59:59+03:00"
        },
        "select": ["ID", "TITLE", "CREATED_DATE", "CREATED_BY", "RESPONSIBLE_ID", "ACCOMPLICES", "AUDITORS", "DESCRIPTION", "COMMENTS_COUNT"],
        "order": {"ID": "DESC"},
        "start": start
    })
    if not res or "result" not in res or "tasks" not in res["result"]:
        break
    tasks = res["result"]["tasks"]
    if not tasks:
        break
    aug_tasks.extend(tasks)
    if "next" in res:
        start = res["next"]
    else:
        break

print(f"Fetched {len(aug_tasks)} tasks from Aug 1 to Sep 10.")

for t in aug_tasks:
    title = (t.get("title") or "").lower()
    desc = (t.get("description") or "").lower()
    comb = title + " " + desc
    
    # Check words
    keywords = ["созвон", "совещан", "протокол", "планерк", "синхрон", "два раза", "2 раза", "отбор", "выборк", "не брать", "брать", "раунд"]
    matched_kws = [k for k in keywords if k in comb]
    
    accomplices = set(str(x) for x in t.get("accomplices") or [])
    auditors = set(str(x) for x in t.get("auditors") or [])
    uids = accomplices.union(auditors)
    uids.add(str(t.get("createdBy", "")))
    uids.add(str(t.get("responsibleId", "")))
    target_match = uids.intersection({'14', '16', '20', '38'})
    
    if matched_kws or ("тендер" in comb and len(target_match) >= 3):
        print(f"\nTask #{t.get('id')} [{t.get('createdDate')}] Title: {t.get('title')}")
        print(f"  Members matched: {target_match} | Kws: {matched_kws}")
        print(f"  Desc snippet: {t.get('description', '')[:200]}")
        
        # Check comments and checklists
        c_res = b24_call("task.commentitem.getlist", [t.get("id")])
        comments = c_res.get("result", []) if (c_res and "result" in c_res) else []
        print(f"  Comments count: {len(comments)}")
        if comments:
            for c in comments:
                print(f"    -> [{c.get('POST_DATE')}] {c.get('AUTHOR_NAME')}: {c.get('POST_MESSAGE')[:150]}")
        
        cl_res = b24_call("tasks.task.checklistitem.getlist", {"taskId": t.get("id")})
        cl_items = cl_res.get("result", []) if (cl_res and "result" in cl_res) else []
        if cl_items:
            print(f"  Checklist items count: {len(cl_items)}")
            for item in cl_items[:5]:
                print(f"    - [chk] {item.get('TITLE')}")
