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

# Fetch up to 100 messages from chat1504
m1504 = b24('im.dialog.messages.get', {'DIALOG_ID': 'chat1504', 'LIMIT': 100})
msgs = m1504.get('result', {}).get('messages', [])
print(f"Total messages fetched: {len(msgs)}")
# Sort chronologically
msgs.sort(key=lambda x: x.get('date', ''))
for m in msgs:
    author = m.get('author_id')
    date = m.get('date')
    text = m.get('text', '')
    if author != 0: # non-system
        print(f"[{date}] User {author}: {text}\n")
