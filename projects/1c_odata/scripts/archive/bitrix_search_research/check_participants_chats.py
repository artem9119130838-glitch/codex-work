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

# 1. Check chat5802
print("=== CHAT 5802 ===")
c5802 = b24('im.dialog.messages.get', {'DIALOG_ID': 'chat5802', 'LIMIT': 50})
for m in c5802.get('result', {}).get('messages', []):
    print(f"[{m.get('date')}] User {m.get('author_id')}: {m.get('text')[:200]}")

# 2. Check user chats around early September 2026 (Alexandra: 38, Azat: 20, Angelica: 16, Saule: 14)
for uid, name in [(38, 'Alexandra'), (20, 'Azat'), (16, 'Angelica'), (14, 'Saule')]:
    print(f"\n=== CHAT WITH {name} (User {uid}) ===")
    res = b24('im.dialog.messages.get', {'DIALOG_ID': str(uid), 'LIMIT': 30})
    for m in res.get('result', {}).get('messages', []):
        d = m.get('date', '')
        if '2026-08' in d or '2026-09' in d:
            print(f"[{d}] User {m.get('author_id')}: {m.get('text')[:200]}")
