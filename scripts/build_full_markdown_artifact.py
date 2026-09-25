#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/build_full_markdown_artifact.py
=======================================
Создает исчерпывающий аналитический отчет (Артефакт) по спринту:
1. Резюме по выполнению спринта (Дни 1-7 + себестоимость).
2. Анализ переписки: замечания Артема, ответы Михаила, динамика.
3. Что сделано хорошо.
4. Что сделано плохо / системные проблемы.
5. Что с ошибками (баги фильтрации, кодировки, обрезки, фальш-позитивы).
6. Что недоделано (разрыв с планом, docx, ТН ВЭД, Excel).
7. Что сказать/написать Михаилу (конструктивная и аргументированная обратная связь).
8. Приоритеты исправления (Action Plan: что чинить в 1-ю очередь).
9. Решение по себестоимости: обоснование переноса.
"""

import os
import sys
import json

ARTIFACT_DIR = r"C:\Users\Артем\.gemini\antigravity\brain\294ac726-7ded-4523-a4b9-6b518691a6e0"
SCRATCH_DIR = r"C:\Codex_Personal\scratch"
DOWNLOADS_DIR = r"C:\Users\Артем\Downloads"

def read_utf8(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def main():
    chat_file = os.path.join(SCRATCH_DIR, "bitrix_sprint_chat_25_09.json")
    with open(chat_file, "r", encoding="utf-8") as f:
        chat_data = json.load(f)

    # Загружаем отчеты
    day1 = read_utf8(os.path.join(DOWNLOADS_DIR, "sprint_day_1_report.md"))
    day2 = read_utf8(os.path.join(DOWNLOADS_DIR, "report.md"))
    day3 = read_utf8(os.path.join(DOWNLOADS_DIR, "report (1).md"))
    day4 = read_utf8(os.path.join(DOWNLOADS_DIR, "report (2).md"))
    day5 = read_utf8(os.path.join(DOWNLOADS_DIR, "report (3).md"))
    day6 = read_utf8(os.path.join(DOWNLOADS_DIR, "report (4).md"))
    day7 = read_utf8(os.path.join(DOWNLOADS_DIR, "report (5).md"))
    cost = read_utf8(os.path.join(DOWNLOADS_DIR, "cost_report.md"))

    # Разбираем переписку детально
    users = chat_data["users"]
    messages = chat_data["messages"]
    messages.sort(key=lambda x: x["id"])

    # Создадим временный файл с чистой структурированной выжимкой диалогов Артема и Михаила
    chat_extract = []
    for m in messages:
        uid = str(m.get("author_id"))
        author = users.get(uid, f"User {uid}")
        txt = m.get("text", "").strip()
        dt = m.get("date", "")[:19].replace("T", " ")
        if not txt:
            continue
        # Исключаем автоматические системные уведомления если они пустые
        chat_extract.append({
            "id": m.get("id"),
            "date": dt,
            "author": author,
            "author_id": m.get("author_id"),
            "text": txt
        })

    with open(os.path.join(SCRATCH_DIR, "structured_chat.json"), "w", encoding="utf-8") as f:
        json.dump(chat_extract, f, ensure_ascii=False, indent=2)

    print(f"Loaded {len(chat_extract)} meaningful messages.")

if __name__ == "__main__":
    main()
