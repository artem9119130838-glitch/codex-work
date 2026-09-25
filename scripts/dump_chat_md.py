#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/dump_chat_md.py
=======================
Дамп сообщений между Артемом и Михаилом в Markdown для чтения через view_file.
"""

import json

with open(r"C:\Codex_Personal\scratch\structured_chat.json", "r", encoding="utf-8") as f:
    messages = json.load(f)

lines = ["# Диалог Артема и Михаила в задаче\n"]

for m in messages:
    txt = m["text"]
    auth = m["author"]
    dt = m["date"]
    mid = m["id"]
    if len(txt.strip()) == 0:
        continue
    # пропускаем чисто системные если нужно
    lines.append(f"### [{dt}] **{auth}** (Сообщение #{mid})")
    lines.append(f"{txt}\n")

with open(r"C:\Codex_Personal\scratch\chat_clean_view.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Saved chat_clean_view.md")
