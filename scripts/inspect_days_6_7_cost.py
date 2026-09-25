#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/inspect_days_6_7_cost.py
================================
Детальный вывод отчетов за День 6, День 7 и Себестоимость в файл scratch/days_6_7_cost_clean.md.
"""

import os
import json

DOWNLOADS = r"C:\Users\Артем\Downloads"
SCRATCH = r"C:\Codex_Personal\scratch"

def read_f(name):
    with open(os.path.join(DOWNLOADS, name), "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

out = []
out.append("# ОТЧЕТ ДЕНЬ 6 (report (4).md)")
out.append(read_f("report (4).md"))
out.append("\n" + "="*70 + "\n")
out.append("# ОТЧЕТ ДЕНЬ 7 (report (5).md)")
out.append(read_f("report (5).md"))
out.append("\n" + "="*70 + "\n")
out.append("# ОТЧЕТ ПО СЕБЕСТОИМОСТИ (cost_report.md)")
out.append(read_f("cost_report.md"))

with open(os.path.join(SCRATCH, "days_6_7_cost_clean.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Saved days_6_7_cost_clean.md")
