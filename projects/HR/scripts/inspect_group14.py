# -*- coding: utf-8 -*-
import os
import sys
import json
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

p = os.path.join(os.getcwd(), "projects", "1c_odata", ".env")
for line in open(p, "r", encoding="utf-8"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ[k.strip()] = v.strip().strip("'\"")

webhook = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"

def b24(method, payload=None):
    try:
        r = requests.post(webhook + method, json=payload or {}, timeout=30)
        return r.json()
    except Exception as e:
        print(f"Error {method}: {e}")
        return {}

# 1. Check sonet groups
r_groups = b24("sonet_group.get", {})
groups = r_groups.get("result", [])
print(f"Total Sonet Groups: {len(groups)}")
g14 = None
for g in groups:
    gid = g.get("ID")
    name = g.get("NAME")
    if str(gid) == "14" or "китай" in name.lower() or "снабжение" in name.lower():
        print(f"  Group #{gid}: {name}")
        if str(gid) == "14":
            g14 = g

# 2. Get tasks in Group 14
print("\n=== Tasks in Group 14 ===")
r_t = b24("tasks.task.list", {
    "filter": {"GROUP_ID": 14},
    "select": ["ID", "TITLE", "STATUS", "CREATED_DATE", "DEADLINE", "CREATED_BY", "RESPONSIBLE_ID", "UF_TASK_WEBDAV_FILES", "COMMENTS_COUNT"],
    "order": {"ID": "desc"},
    "limit": 20
})
tasks = r_t.get("result", {}).get("tasks", [])
print(f"Recent tasks in Group 14: {len(tasks)}")
for t in tasks:
    print(f"Task #{t.get('id')}: {t.get('title')} | Status: {t.get('status')} | Resp: {t.get('responsibleId')} | Files: {len(t.get('ufTaskWebdavFiles') or [])} | Comments: {t.get('commentsCount')}")
