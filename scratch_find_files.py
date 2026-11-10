import os, sys, requests, json

p = 'C:/Codex/projects/1c_odata/.env'
for line in open(p, encoding='utf-8'):
    if '=' in line and not line.startswith('#'):
        k, v = line.strip().split('=', 1)
        os.environ[k] = v.strip('\'\"')

webhook = os.getenv('BITRIX24_WEBHOOK_URL').rstrip('/') + '/'

r = requests.post(webhook + 'tasks.task.get', json={'taskId': 3010, 'select': ['ID', 'TITLE', 'UF_TASK_WEBDAV_FILES']})
task = r.json().get('result', {}).get('task', {})
print('UF_TASK_WEBDAV_FILES:', task.get('ufTaskWebdavFiles'))

for fid in [103264, 123498, 123500, 124152]:
    rf = requests.post(webhook + 'disk.file.get', json={'id': fid})
    res = rf.json().get('result', {})
    name = res.get('NAME')
    durl = res.get('DOWNLOAD_URL')
    sys.stdout.buffer.write(f'{fid}: {name}\n'.encode('utf-8'))
    if durl:
        content = requests.get(durl).content
        safe_name = f'file_{fid}_' + (name if name else 'unnamed')
        with open(os.path.join('c:/Codex', safe_name), 'wb') as out_f:
            out_f.write(content)
        sys.stdout.buffer.write(f'Saved to {safe_name} ({len(content)} bytes)\n'.encode('utf-8'))
