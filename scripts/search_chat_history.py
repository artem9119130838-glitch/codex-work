#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/search_chat_history.py
===============================
Поиск по всем чатам и транскриптам Antigravity (включая архивные).
Использование:
    py scripts/search_chat_history.py "поисковый запрос" [--all] [--limit 10]
"""

import os
import sys
import glob
import json
import argparse
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BRAIN_DIR = Path(r"C:\Users\Артем\.gemini\antigravity\brain")

def search_chats(query, user_only=False, max_results=20):
    files = glob.glob(str(BRAIN_DIR / "*" / ".system_generated" / "logs" / "transcript.jsonl"))
    print(f"Поиск по {len(files)} чатам запроса: '{query}'...")
    
    query_lower = query.lower()
    matches = []
    
    for fpath in files:
        conv_id = Path(fpath).parent.parent.parent.name
        # Skip current query if it's the exact same prompt asking to search
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                for line_idx, line in enumerate(f):
                    if query_lower not in line.lower():
                        continue
                    try:
                        data = json.loads(line)
                    except Exception:
                        continue
                        
                    src = data.get("source")
                    stype = data.get("type")
                    content = data.get("content", "")
                    
                    if user_only and (src != "USER_EXPLICIT" or stype != "USER_INPUT"):
                        continue
                        
                    if query_lower not in content.lower():
                        continue
                        
                    matches.append({
                        "conv_id": conv_id,
                        "created_at": data.get("created_at", "н/д"),
                        "source": src,
                        "type": stype,
                        "step_index": data.get("step_index", line_idx),
                        "file_path": fpath,
                        "content": content
                    })
        except Exception as e:
            continue
            
    # Sort matches by date
    matches.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    
    print(f"\nНайдено совпадений: {len(matches)}\n" + "="*80)
    for idx, m in enumerate(matches[:max_results], 1):
        dt = m['created_at'][:19].replace("T", " ") if m.get('created_at') else "н/д"
        print(f"\n[{idx}] Дата: {dt} | Чат ID: {m['conv_id']}")
        print(f"    Тип: {m['type']} ({m['source']}) | Шаг: {m['step_index']}")
        print(f"    Файл: {m['file_path']}")
        
        # Находим фрагмент контекста вокруг совпадения
        text = m['content']
        pos = text.lower().find(query_lower)
        start = max(0, pos - 150)
        end = min(len(text), pos + len(query) + 250)
        snippet = text[start:end].replace("\n", " ").strip()
        print(f"    Фрагмент:\n    ... {snippet} ...\n" + "-"*80)
        
    return matches

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Поиск по истории чатов Antigravity")
    parser.add_argument("query", help="Текст для поиска")
    parser.add_argument("--user-only", action="store_true", help="Искать только в сообщениях пользователя")
    parser.add_argument("--limit", type=int, default=15, help="Максимальное количество результатов")
    args = parser.parse_args()
    
    search_chats(args.query, user_only=args.user_only, max_results=args.limit)
