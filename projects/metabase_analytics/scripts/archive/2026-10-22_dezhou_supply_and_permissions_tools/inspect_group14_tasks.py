#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import urllib.request
import json

# Load webhook from 1c_odata/.env
env_path = "projects/1c_odata/.env"
webhook = ""
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("BITRIX24_WEBHOOK_URL="):
                webhook = line.split("=", 1)[1].strip().strip("'\"")

print("Webhook found:", bool(webhook))

url = f"{webhook.rstrip('/')}/tasks.task.list.json"
params = {
    "filter": {"GROUP_ID": 14},
    "select": ["ID", "TITLE", "RESPONSIBLE_ID", "UF_CRM_TASK", "CREATED_DATE"],
    "order": {"ID": "DESC"},
    "start": 0
}
req = urllib.request.Request(url, data=json.dumps(params).encode(), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=15) as resp:
    res = json.loads(resp.read().decode())
    tasks = res.get("result", {}).get("tasks", [])
    print(f"Loaded {len(tasks)} tasks from Group 14.")
    for t in tasks[:10]:
        print(f"Task {t.get('id')} | Resp: {t.get('responsibleId')} | CRM: {t.get('ufCrmTask')} | Title: {t.get('title')[:60]}")
