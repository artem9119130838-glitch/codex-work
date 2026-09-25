#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/build_sprint_evaluation.py
==================================
Автоматический разбор всех 7 дней, себестоимости и диалога в чате.
Формирует детальный структурированный отчет для руководства и фидбека Михаилу.
"""

import os
import sys
import json
import re

SCRATCH = r"C:\Codex_Personal\scratch"

with open(os.path.join(SCRATCH, "sprint_raw_analyzed.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

days = data["days"]
chat = data["chat"]

eval_data = {}

# 1. Анализируем каждый день
for k in ["day1", "day2", "day3", "day4", "day5", "day6", "day7", "cost"]:
    text = days[k]
    # Находим заголовки
    headers = [line.strip() for line in text.splitlines() if line.startswith("#")]
    # Находим проблемы и баги
    bugs = [line.strip() for line in text.splitlines() if any(w in line.lower() for w in ["ошибк", "баг", "проблем", "провал", "ложноположительн", "read-only", "timeout", "обрезк", "reject", "отказ", "не отлавливал", "warning", "error"])]
    # Находим статусы тендеров
    tender_statuses = re.findall(r"([A-Za-zА-Яа-я0-9_\-\s\"«»]+)\s*[:—–-]\s*(PASS|REJECT[A-Z_]*|FSTEK[A-Z_]*|FAILED|WAIVED)", text, re.IGNORECASE)
    
    eval_data[k] = {
        "headers": headers,
        "key_issues": bugs[:15],
        "sample_statuses": tender_statuses[:10],
        "length": len(text)
    }

# 2. Анализируем чат: реплики Артема и Михаила
chat_eval = []
current_block = {}
for line in chat.splitlines():
    if line.startswith("[2026-"):
        if current_block:
            chat_eval.append(current_block)
        current_block = {"header": line, "text": []}
    else:
        if "text" in current_block:
            current_block["text"].append(line)
if current_block:
    chat_eval.append(current_block)

dialogue_summary = []
for c in chat_eval:
    h = c["header"]
    t = "\n".join(c["text"]).strip()
    if not t: continue
    author = "Артем" if "Артем" in h else ("Михаил" if "Михаил" in h else "Система")
    dialogue_summary.append({
        "header": h,
        "author": author,
        "text": t
    })

output = {
    "days_analysis": eval_data,
    "dialogue": dialogue_summary
}

with open(os.path.join(SCRATCH, "sprint_evaluation_summary.json"), "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Evaluation summary generated.")
