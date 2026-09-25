#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/extract_sprint_points.py
================================
Извлечение ключевых тезисов из переписки и отчетов спринта в текстовый файл UTF-8.
"""

import os
import sys

SCRATCH_IN = r"C:\Codex_Personal\scratch\sprint_full_summary.txt"
SCRATCH_OUT = r"C:\Codex_Personal\scratch\chat_breakdown.txt"

with open(SCRATCH_IN, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
in_chat = True
cur_msg = []

for line in lines:
    if line.startswith("--- 2. ДЕТАЛЬНЫЙ АНАЛИЗ ОТЧЕТОВ"):
        in_chat = False
        break
    if in_chat:
        if line.startswith("[2026-"):
            if cur_msg:
                header = cur_msg[0].strip()
                body = "".join(cur_msg[1:]).strip()
                if "Михаил" in header or "Артем" in header:
                    out.append(f"{header}")
                    out.append(f"{body}\n")
            cur_msg = [line]
        else:
            cur_msg.append(line)

with open(SCRATCH_OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Chat breakdown written to {SCRATCH_OUT} ({len(out)} lines)")
