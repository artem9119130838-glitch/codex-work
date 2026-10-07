# -*- coding: utf-8 -*-
import os, glob, json, sys
sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', 'venv', 'site-packages', 'node_modules']):
        continue
    for f in files:
        if f.endswith('.json'):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                    if '"nodes":' in content and '"connections":' in content:
                        data = json.loads(content)
                        if isinstance(data, list):
                            workflows = data
                        elif isinstance(data, dict):
                            workflows = [data]
                        else:
                            continue
                        for wf in workflows:
                            if not isinstance(wf, dict): continue
                            name = wf.get('name', f)
                            nodes = [n.get('name', '') + ' (' + n.get('type', '') + ')' for n in wf.get('nodes', []) if isinstance(n, dict)]
                            nodes_str = ' '.join(nodes).lower()
                            if any(k in nodes_str or k in name.lower() for k in ['chat', 'task', 'bitrix', 'search', 'задач', 'поиск', 'сообщени', 'битрикс', 'crm', 'поручени']):
                                print(f"Workflow: {name} -> {fp}")
                                for n in nodes:
                                    if any(k in n.lower() for k in ['bitrix', 'chat', 'task', 'search', 'ai', 'openai', 'llm', 'gemini', 'anthropic', 'langchain']):
                                        print(f"   node: {n}")
            except Exception as e:
                pass
