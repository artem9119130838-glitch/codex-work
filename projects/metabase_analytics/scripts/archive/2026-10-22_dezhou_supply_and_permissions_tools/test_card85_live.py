#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import urllib.request
import json

base_url = 'http://109.248.170.181:3000'
req = urllib.request.Request(
    f'{base_url}/api/session',
    data=json.dumps({'username': 'admin@tender-rag.local', 'password': 'Artem12345'}).encode(),
    headers={'Content-Type': 'application/json'}
)
token = json.loads(urllib.request.urlopen(req).read().decode())['id']
headers = {'Content-Type': 'application/json', 'X-Metabase-Session': token}

qr = urllib.request.Request(f'{base_url}/api/card/85/query', data=json.dumps({}).encode(), headers=headers)
res = json.loads(urllib.request.urlopen(qr).read().decode())
rows = res.get("data", {}).get("rows", [])
cols = [c["name"] for c in res.get("data", {}).get("cols", [])]
print(f"Card 85 (Антирейтинг закупщиков) now returned {len(rows)} rows:")
for r in rows:
    print(f"  {r[0]:<30} | Всего: {r[1]:<3} | НМЦК: {r[2]:>14,.2f} | В работе: {r[3]:<2} | Побед: {r[4]:<2} | Срывы: {r[5]:<2} | Limbo: {r[7]}")
