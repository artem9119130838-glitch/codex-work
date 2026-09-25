import urllib.request
import json
import urllib.parse
import sys

sys.stdout.reconfigure(encoding='utf-8')
webhook = 'https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/'

def b24_call(method, params=None):
    url = webhook + method
    data = None
    if params:
        data = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = b24_call('im.dialog.messages.get', {'DIALOG_ID': 1, 'LIMIT': 50})
msgs = res.get('result', {}).get('messages', [])

print("=== USER NOTES IN DIALOG_ID=1 (Non-automated alerts) ===")
user_notes = []
for m in msgs:
    txt = m.get('text', '')
    if not txt.startswith('=Ошибка при обработке тендера'):
        user_notes.append(m)
        print(f"[{m.get('date')}] ID {m.get('id')}:")
        print(txt)
        print("=" * 60)

print(f"\nTotal human notes found: {len(user_notes)}")
