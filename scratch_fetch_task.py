import os, sys, requests, json

def parse_env(filepath):
    if not os.path.exists(filepath):
        return {}
    res = {}
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                res[k.strip()] = v.strip().strip('\"').strip('\'')
    return res

env_vars = {}
for p in ['C:/Codex/projects/1c_odata/.env', 'C:/Codex/projects/lead_reactivation/.env', 'C:/Codex/projects/metabase_analytics/.env']:
    env_vars.update(parse_env(p))

webhook = env_vars.get('BITRIX24_WEBHOOK_URL') or env_vars.get('B24_WEBHOOK') or env_vars.get('BITRIX_WEBHOOK') or env_vars.get('B24_WEBHOOK_URL')
webhook = webhook.rstrip('/') + '/'

def b24(method, payload=None):
    r = requests.post(webhook + method, json=payload or {}, timeout=30)
    return r.json()

# 1. Task info
t_info = b24('tasks.task.get', {'taskId': 3010})
task = t_info.get('result', {}).get('task', {})

# 2. task.commentitem.getlist with positional params
c_info = b24('task.commentitem.getlist', [3010, {'ID': 'ASC'}])
comments = c_info.get('result', [])
print('task.commentitem count:', len(comments))

# 3. im.chat.get
chat_info = b24('im.chat.get', {'ENTITY_TYPE': 'TASKS_TASK', 'ENTITY_ID': 3010})
chat_id = chat_info.get('result', {}).get('ID') if chat_info.get('result') else None
print('Chat ID:', chat_id)
chat_msgs = []
if chat_id:
    r_msg = b24('im.dialog.messages.get', {'DIALOG_ID': f'chat{chat_id}', 'LIMIT': 50})
    chat_msgs = r_msg.get('result', {}).get('messages', [])
    print('im.dialog messages count:', len(chat_msgs))

with open('c:/Codex/task_3010_full_chat.txt', 'w', encoding='utf-8') as f:
    f.write('Title: ' + str(task.get('title')) + '\n')
    f.write('Description: ' + str(task.get('description')) + '\n\n')
    
    if comments:
        f.write('=== TASK COMMENTS ===\n')
        for c in comments:
            cid = c.get('ID')
            cname = c.get('AUTHOR_NAME')
            caid = c.get('AUTHOR_ID')
            cdate = c.get('POST_DATE')
            f.write(f'--- Comment {cid} by {cname} ({caid}) at {cdate} ---\n')
            f.write(str(c.get('POST_MESSAGE')) + '\n\n')
            
    if chat_msgs:
        f.write('=== CHAT MESSAGES ===\n')
        for m in reversed(chat_msgs):
            mid = m.get('id')
            maid = m.get('author_id')
            mdate = m.get('date')
            f.write(f'--- Msg {mid} by Author {maid} at {mdate} ---\n')
            f.write(str(m.get('text')) + '\n')
            if m.get('params'):
                f.write('Params: ' + json.dumps(m.get('params'), ensure_ascii=False) + '\n')
            f.write('\n')

print('Wrote full task chat to c:/Codex/task_3010_full_chat.txt')
