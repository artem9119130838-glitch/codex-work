#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/parse_days_detail.py
============================
Пошаговый разбор Дней 1-7 и отчета по себестоимости.
"""

import os
import sys
import json

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

with open(r"C:\Codex_Personal\scratch\sprint_raw_analyzed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

days = data["days"]

for k in ["day1", "day2", "day3", "day4", "day5", "day6", "day7", "cost"]:
    print(f"\n{'='*70}\nKEY: {k.upper()}\n{'='*70}")
    content = days.get(k, "")
    lines = content.splitlines()
    for l in lines:
        if l.startswith("#") or l.startswith("* **") or l.startswith("- **") or "ошиб" in l.lower() or "проблем" in l.lower() or "баг" in l.lower() or "провал" in l.lower() or "reject" in l.lower() or "стоп" in l.lower():
            print(l)
