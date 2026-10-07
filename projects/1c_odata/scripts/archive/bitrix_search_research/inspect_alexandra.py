# -*- coding: utf-8 -*-
import os, sys, json, urllib.request

sys.stdout.reconfigure(encoding='utf-8')
webhook = os.getenv("BITRIX24_WEBHOOK_URL", "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/").rstrip("/") + "/"

def b24(method, params=None):
    req = urllib.request.Request(webhook + method, data=json.dumps(params or {}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

res = b24('im.dialog.messages.get', {'DIALOG_ID': '38', 'LIMIT': 50})
print('=== CHAT WITH ALEXANDRA (38) ===')
for m in res.get('result', {}).get('messages', []):
    print(f"[{m.get('date')}] User {m.get('author_id')}: {m.get('text')}")
