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
    data=json.dumps({'username': 'manager@tender-rag.local', 'password': 'manager12345'}).encode(),
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req) as resp:
        token = json.loads(resp.read().decode())['id']
        print("[OK] Manager login successful!")
except Exception as e:
    print("[ERROR] Manager login failed:", e)
    sys.exit(1)

headers = {'Content-Type': 'application/json', 'X-Metabase-Session': token}

# Test querying cards 81-86 as manager
for cid in [81, 82, 83, 84, 85, 86]:
    qr = urllib.request.Request(f'{base_url}/api/card/{cid}/query', data=json.dumps({}).encode(), headers=headers)
    try:
        with urllib.request.urlopen(qr) as resp:
            data = json.loads(resp.read().decode())
            status = data.get("status")
            rows = len(data.get("data", {}).get("rows", []))
            print(f"Card {cid} as Manager: status={status}, rows={rows}")
    except urllib.error.HTTPError as e:
        print(f"Card {cid} as Manager HTTP ERROR: {e.code} {e.read().decode()[:150]}")
