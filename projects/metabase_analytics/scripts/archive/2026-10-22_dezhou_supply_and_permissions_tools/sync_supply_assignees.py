#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import urllib.request
import json

env_path = "projects/1c_odata/.env"
webhook = ""
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("BITRIX24_WEBHOOK_URL="):
                webhook = line.split("=", 1)[1].strip().strip("'\"")

USER_MAP = {
    "20": "Азат Денишов",
    "30": "Miss Wang (Дечжоу)",
    "86": "Cindy Qian (Дечжоу)",
    "84": "Юйнань Ли (Дечжоу)",
    "44": "Liyan Wang (Дечжоу)"
}

url = f"{webhook.rstrip('/')}/tasks.task.list.json"
deal_to_supply = {}
start = 0

while True:
    params = {
        "filter": {"GROUP_ID": 14},
        "select": ["ID", "TITLE", "RESPONSIBLE_ID", "UF_CRM_TASK", "CREATED_DATE"],
        "order": {"ID": "DESC"},
        "start": start
    }
    req = urllib.request.Request(url, data=json.dumps(params).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        res = json.loads(resp.read().decode())
        tasks = res.get("result", {}).get("tasks", [])
        if not tasks:
            break
        for t in tasks:
            crm_list = t.get("ufCrmTask") or []
            resp_id = str(t.get("responsibleId") or "")
            resp_name = USER_MAP.get(resp_id, f"Закупщик ID {resp_id}")
            task_id = t.get("id")
            for crm_item in crm_list:
                if crm_item.startswith("D_"):
                    d_id = crm_item[2:]
                    if d_id not in deal_to_supply:
                        deal_to_supply[d_id] = {
                            "task_id": task_id,
                            "resp_id": resp_id,
                            "resp_name": resp_name
                        }
        if len(tasks) < 50:
            break
        start += len(tasks)

print(f"Total mapped deals from Group 14 tasks: {len(deal_to_supply)}")
# Breakdown of deals by supply specialist:
from collections import Counter
counts = Counter([v["resp_name"] for v in deal_to_supply.values()])
for name, cnt in counts.most_common():
    print(f"  {name}: {cnt} сделок")
