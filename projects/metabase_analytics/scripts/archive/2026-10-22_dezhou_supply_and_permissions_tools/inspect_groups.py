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

groups = json.loads(urllib.request.urlopen(urllib.request.Request(f'{base_url}/api/permissions/group', headers=headers)).read().decode())
for g in groups:
    print(f"Group ID {g['id']}: {g['name']} (members: {g.get('member_count')})")

cg = json.loads(urllib.request.urlopen(urllib.request.Request(f'{base_url}/api/collection/graph', headers=headers)).read().decode())
print("Collection graph groups:", cg.get("groups", {}).keys())

# If group 1 is not in collection graph, let's see how Metabase collection graph handles it
print(json.dumps(cg, indent=2, ensure_ascii=False))
