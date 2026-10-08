import requests
import json

B24_WEBHOOK = 'https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/'
resp = requests.post(f'{B24_WEBHOOK}im.dialog.messages.get', json={'DIALOG_ID': 'chat6602', 'LIMIT': 50})
data = resp.json().get('result', {})
files_map = {f['id']: f for f in data.get('files', [])}
msgs = data.get('messages', [])

print(f"Total files in response: {len(files_map)}")
for m in msgs:
    params = m.get('params', {})
    if 'FILE_ID' in params:
        dt = m.get('date', '')[:19].replace('T', ' ')
        mid = m.get('id')
        txt = m.get('text', '').strip()
        print(f"Msg #{mid} ({dt}) text: '{txt}'")
        for fid in params['FILE_ID']:
            f_info = files_map.get(fid, {})
            print(f"  - File: {f_info.get('name')} | Download: {f_info.get('urlDownload')}")
