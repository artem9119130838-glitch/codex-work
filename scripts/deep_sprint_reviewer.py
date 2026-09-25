#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/deep_sprint_reviewer.py
===============================
Детальный синтез отчетов спринта, переписки, выявление багов, недоделок,
сильных сторон, критических точек и формирование рекомендаций для Михаила.
"""

import os
import sys
import json

SCRATCH = r"C:\Codex_Personal\scratch"

with open(os.path.join(SCRATCH, "sprint_raw_analyzed.json"), "r", encoding="utf-8") as f:
    data = json.load(f)

days = data["days"]
chat = data["chat"]

lines = []
def p(s=""):
    lines.append(s)

p("="*70)
p("ПОЛНЫЙ ДЕТАЛЬНЫЙ ТЕКСТ ВСЕХ ОТЧЕТОВ")
p("="*70)

for k, name in [
    ("day1", "ДЕНЬ 1 (17.09)"),
    ("day2", "ДЕНЬ 2 (18.09)"),
    ("day3", "ДЕНЬ 3 (19.09)"),
    ("day4", "ДЕНЬ 4 (21.09)"),
    ("day5", "ДЕНЬ 5 (22.09)"),
    ("day6", "ДЕНЬ 6 (23.09)"),
    ("day7", "ДЕНЬ 7 (24.09)"),
    ("cost", "СЕБЕСТОИМОСТЬ (ФАЗА 3)")
]:
    p(f"\n{'#'*60}\n# {name}\n{'#'*60}")
    p(days.get(k, ""))

p("\n" + "="*70)
p("ПОЛНЫЙ ДИАЛОГ В ЧАТЕ БИТРИКС24")
p("="*70)
p(chat)

with open(os.path.join(SCRATCH, "review_output.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"review_output.txt written ({len(lines)} lines)")
