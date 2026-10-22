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

# Get collections graph
cg_req = urllib.request.Request(f'{base_url}/api/collection/graph', headers=headers)
cg = json.loads(urllib.request.urlopen(cg_req).read().decode())
print("Collection graph revision:", cg.get("revision"))
print("Groups:", list(cg.get("groups", {}).keys()))
for grp_id, perms in cg.get("groups", {}).items():
    print(f"Group {grp_id}: Collection 8 perm = {perms.get('8')}")

# Update collection graph to give Group 1 (All Users) and any manager group 'read' access to Collection 8
rev = cg.get("revision", 0)
for grp_id in cg.get("groups", {}):
    cg["groups"][grp_id]["8"] = "read"

put_req = urllib.request.Request(
    f'{base_url}/api/collection/graph',
    data=json.dumps(cg).encode(),
    headers=headers,
    method='PUT'
)
try:
    with urllib.request.urlopen(put_req) as resp:
        print("[SUCCESS] Collection 8 permissions updated to 'read' for all groups!")
except urllib.error.HTTPError as e:
    print("HTTP Error updating collection graph:", e.code, e.read().decode())

# Also check database permissions graph
pg_req = urllib.request.Request(f'{base_url}/api/permissions/graph', headers=headers)
pg = json.loads(urllib.request.urlopen(pg_req).read().decode())
print("Permissions graph revision:", pg.get("revision"))
