#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/analyze_sprint.py
=========================
Глубокий анализ всех отчетов спринта (Дни 1-7, cost_report) и чата Битрикс24.
"""

import os
import sys
import json
import re

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DOWNLOADS = r"C:\Users\Артем\Downloads"
SCRATCH = r"C:\Codex_Personal\scratch"

REPORTS_MAP = [
    ("sprint_day_1_report.md", "День 1 (17.09)"),
    ("report.md", "День 2 (18.09)"),
    ("report (1).md", "День 3 (19.09)"),
    ("report (2).md", "День 4 (21.09)"),
    ("report (3).md", "День 5 (22.09)"),
    ("report (4).md", "День 6 (23.09)"),
    ("report (5).md", "День 7 (24.09)"),
    ("cost_report.md", "Себестоимость (Фаза 3)")
]

def load_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def main():
    analysis = {}
    
    # 1. Читаем чат
    chat_file = os.path.join(SCRATCH, "bitrix_sprint_chat_25_09.json")
    chat_data = {}
    if os.path.exists(chat_file):
        with open(chat_file, "r", encoding="utf-8") as f:
            chat_data = json.load(f)
    
    analysis["chat_summary"] = {
        "messages_count": len(chat_data.get("messages", [])),
        "users": chat_data.get("users", {})
    }
    
    # Ключевые сообщения чата
    key_messages = []
    for m in chat_data.get("messages", []):
        text = m.get("text", "")
        author = chat_data.get("users", {}).get(str(m.get("author_id")), str(m.get("author_id")))
        date = m.get("date")
        # Сохраняем все содержательные сообщения
        if len(text.strip()) > 0:
            key_messages.append({
                "id": m.get("id"),
                "date": date,
                "author": author,
                "text": text
            })
    analysis["chat_messages"] = key_messages

    # 2. Читаем все отчеты
    reports_data = {}
    for filename, label in REPORTS_MAP:
        path = os.path.join(DOWNLOADS, filename)
        if os.path.exists(path):
            content = load_file(path)
            reports_data[label] = {
                "filename": filename,
                "size": len(content),
                "content": content
            }
        else:
            reports_data[label] = {"error": f"Not found: {path}"}
            
    analysis["reports"] = reports_data

    # Сохраняем полный дамп для детального изучения
    out_analysis = os.path.join(SCRATCH, "full_sprint_data.json")
    with open(out_analysis, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print("Анализ данных подготовлен:")
    print(f"- Сообщений в чате: {len(key_messages)}")
    for label, r in reports_data.items():
        if "size" in r:
            print(f"- {label} ({r['filename']}): {r['size']} симв.")
        else:
            print(f"- {label}: {r.get('error')}")

if __name__ == "__main__":
    main()
