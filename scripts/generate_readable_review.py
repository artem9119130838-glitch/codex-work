#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_readable_review.py
===================================
Генерирует полный аналитический отчет DETAILED_SPRINT_AUDIT.md
с цитатами из переписки, результатами тестов по дням и выявленными проблемами.
"""

import os
import sys
import json

SCRATCH = r"C:\Codex_Personal\scratch"

with open(os.path.join(SCRATCH, "sprint_raw_analyzed.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

days = data["days"]
chat = data["chat"]

with open(os.path.join(SCRATCH, "sprint_evaluation_summary.json"), "r", encoding="utf-8") as f:
    ev = json.load(f)

md = []
def w(s=""):
    md.append(s)

w("# ПОЛНЫЙ АУДИТ СПРИНТА (ПО 25.09): КАРТА РАБОТЫ, ОТЧЕТЫ И ПЕРЕПИСКА")
w()
w("## 1. ХРОНОЛОГИЯ И СУТЬ ОБЩЕНИЯ В БИТРИКС24")
w()
for d in ev["dialogue"]:
    auth = d["author"]
    h = d["header"]
    t = d["text"]
    w(f"### {auth} ({h})")
    w(t)
    w()

w("---")
w("## 2. АНАЛИЗ ОТЧЕТОВ ПО ДНЯМ (ДНИ 1–7 И СЕБЕСТОИМОСТЬ)")
w()

titles = {
    "day1": "День 1 (17.09) — Старт пайплайна и базовая фильтрация",
    "day2": "День 2 (18.09) — LLM-обработка и извлечение спецификаций",
    "day3": "День 3 (19.09) — Интеграция с Bitrix24 и сквозной тест",
    "day4": "День 4 (21.09) — Массовый прогон и финансовый отчет DeepSeek",
    "day5": "День 5 (22.09) — Борьба с багом обрезки текста и доработка Нацрежима/ФСТЭК",
    "day6": "День 6 (23.09) — Регрессионное тестирование (12 тендеров)",
    "day7": "День 7 (24.09) — LLM-окно контекста 4000 симв. и глобальный флаг WAIVED",
    "cost": "Себестоимость (Фаза 3) — Дни 1-3 реализованы, Дни 4-10 предстоят"
}

for k in ["day1", "day2", "day3", "day4", "day5", "day6", "day7", "cost"]:
    w(f"### {titles[k]}")
    w(days[k])
    w("\n" + "="*50 + "\n")

out_path = os.path.join(SCRATCH, "DETAILED_SPRINT_AUDIT.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Generated {out_path} ({len(md)} lines)")
