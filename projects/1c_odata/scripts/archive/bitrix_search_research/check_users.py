# -*- coding: utf-8 -*-
import urllib.request, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

webhook = os.getenv('BITRIX24_WEBHOOK_URL', 'https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/').rstrip('/') + '/'
req = urllib.request.Request(webhook + 'user.get')
resp = urllib.request.urlopen(req)
users = json.loads(resp.read().decode('utf-8')).get('result', [])
for u in users:
    fn = f"{u.get('NAME')} {u.get('LAST_NAME')}".strip()
    pos = u.get('WORK_POSITION', '')
    if any(n in fn.lower() for n in ['анжелик', 'азат', 'саул', 'александр']):
        print(f"ID {u.get('ID')}: {fn} | Должность: {pos} | Email: {u.get('EMAIL')}")
