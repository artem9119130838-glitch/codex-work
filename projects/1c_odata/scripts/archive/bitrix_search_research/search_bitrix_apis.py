# -*- coding: utf-8 -*-
import os, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

search_dirs = [r'C:\Codex', r'C:\Users\Артем\tender-rag-api', r'D:\Soft\Codex Backup']

patterns = ['tasks.task.list', 'task.item.list', 'tasks.task.get', 'im.dialog.messages.get', 'im.chat.get', 'im.search']

found = []
for sdir in search_dirs:
    if not os.path.exists(sdir): continue
    for root, dirs, files in os.walk(sdir):
        if any(p in root for p in ['.git', 'venv', 'site-packages', 'node_modules']): continue
        for f in files:
            if f.endswith(('.py', '.json', '.md', '.sh')):
                fp = os.path.join(root, f)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()
                        matches = [p for p in patterns if p in content]
                        if matches:
                            found.append((fp, matches))
                except: pass

print(f"Total files found: {len(found)}")
for fp, m in found:
    print(f"{fp} -> {m}")
