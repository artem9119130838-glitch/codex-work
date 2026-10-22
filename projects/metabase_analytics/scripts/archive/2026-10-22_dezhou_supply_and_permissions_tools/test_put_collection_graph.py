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

# Get collections
cols = json.loads(urllib.request.urlopen(urllib.request.Request(f'{base_url}/api/collection', headers=headers)).read().decode())
col_ids = [str(c['id']) for c in cols]
print("All collection IDs:", col_ids)

# Get current graph
cg = json.loads(urllib.request.urlopen(urllib.request.Request(f'{base_url}/api/collection/graph', headers=headers)).read().decode())
print("Current collection graph:", cg)

# Build payload for Group 1 ("All Users")
# In Group 1, we want read access to collection 8, 4, 5, etc.
group1_perms = {"root": "none"}
for cid in col_ids:
    group1_perms[cid] = "none"
group1_perms["8"] = "read"
group1_perms["5"] = "read"
group1_perms["4"] = "read"

# Retain group 2 (Admin) exactly as it was:
payload = {
    "revision": cg.get("revision", 0),
    "groups": {
        "1": group1_perms,
        "2": cg.get("groups", {}).get("2", {"root": "write"})
    }
}

print("Sending payload...")
put_req = urllib.request.Request(
    f'{base_url}/api/collection/graph',
    data=json.dumps(payload).encode(),
    headers=headers,
    method='PUT'
)
try:
    with urllib.request.urlopen(put_req) as resp:
        res = json.loads(resp.read().decode())
        print("[SUCCESS] Permissions updated! New revision:", res.get("revision"))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
