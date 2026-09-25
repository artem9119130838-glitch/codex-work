#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/export_sprint_chat.py
=============================
Экспорт переписки из чата задачи Битрикс24 "Спринт по 25.09/ Карта проделанной работы" (Chat 6602).
"""

import os
import sys
import json
import requests

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

B24_WEBHOOK = "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/"
CHAT_ID = "chat6602"

def main():
    os.makedirs("scratch", exist_ok=True)
    
    resp = requests.post(f"{B24_WEBHOOK}im.dialog.messages.get", json={"DIALOG_ID": CHAT_ID, "LIMIT": 100})
    resp.raise_for_status()
    data = resp.json().get("result", {})
    
    users = {u["id"]: (u.get("name", "") + " " + u.get("last_name", "")).strip() for u in data.get("users", [])}
    files_map = {f["id"]: f for f in data.get("files", [])}
    msgs = data.get("messages", [])
    
    # Sort chronological (oldest to newest)
    msgs.sort(key=lambda x: x["id"])
    
    md_lines = [
        "# Переписка по задаче «Спринт по 25.09/ Карта проделанной работы» (Чат 6602)",
        f"- **Количество сообщений**: {len(msgs)}",
        f"- **Участники**: {', '.join(users.values())}",
        f"- **Период**: {msgs[0]['date'] if msgs else 'N/A'} — {msgs[-1]['date'] if msgs else 'N/A'}",
        "\n---\n"
    ]
    
    for m in msgs:
        author = users.get(m.get("author_id"), f"Пользователь {m.get('author_id')}")
        date = m.get("date", "")
        text = m.get("text", "")
        params = m.get("params", {})
        
        attached_files = []
        if isinstance(params, dict) and "FILE_ID" in params:
            for fid in params["FILE_ID"]:
                f_info = files_map.get(fid)
                if f_info:
                    attached_files.append(f"{f_info.get('name')} (скачать: {f_info.get('urlDownload')})")
        
        md_lines.append(f"### [{date}] {author} (Сообщение #{m.get('id')})")
        if text:
            md_lines.append(text)
        if attached_files:
            md_lines.append("\n**Вложенные файлы:**\n- " + "\n- ".join(attached_files))
        md_lines.append("\n")
        
    out_md = os.path.abspath("scratch/bitrix_sprint_chat_25_09.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        
    out_json = os.path.abspath("scratch/bitrix_sprint_chat_25_09.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"users": users, "messages": msgs, "files": data.get("files", [])}, f, ensure_ascii=False, indent=2)
        
    print(f"Экспорт завершен успешно:")
    print(f"- Всего сообщений: {len(msgs)}")
    print(f"- Участники: {', '.join(users.values())}")
    print(f"- Период: {msgs[0]['date']} -> {msgs[-1]['date']}")
    print(f"- Прикреплено файлов: {len(data.get('files', []))}")
    print(f"- Файл Markdown: {out_md}")
    print(f"- Файл JSON: {out_json}")

if __name__ == "__main__":
    main()
