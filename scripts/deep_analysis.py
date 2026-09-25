#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/deep_analysis.py
========================
Анализ переписки и отчетов спринта без проблем с кодировкой терминала.
Записывает структурированный отчет в scratch/sprint_full_summary.txt (UTF-8).
"""

import os
import sys
import json

DOWNLOADS = r"C:\Users\Артем\Downloads"
SCRATCH = r"C:\Codex_Personal\scratch"

def main():
    with open(os.path.join(SCRATCH, "full_sprint_data.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    chat_msgs = data.get("chat_messages", [])
    reports = data.get("reports", {})

    out_lines = []
    def p(text=""):
        out_lines.append(text)

    p("=" * 80)
    p("ПОЛНЫЙ АНАЛИЗ СПРИНТА (ПО 25.09) - КАРТА ПРОДЕЛАННОЙ РАБОТЫ")
    p("=" * 80)
    p()

    # 1. Анализ переписки
    p("--- 1. ХРОНОЛОГИЯ И ДИАЛОГ В ЧАТЕ БИТРИКС24 ---")
    for m in chat_msgs:
        auth = m["author"]
        dt = m["date"][:19].replace("T", " ")
        txt = m["text"].strip()
        p(f"[{dt}] {auth}:")
        for line in txt.splitlines():
            p(f"    {line}")
        p()

    # 2. Анализ каждого отчета
    p("=" * 80)
    p("--- 2. ДЕТАЛЬНЫЙ АНАЛИЗ ОТЧЕТОВ ПО ДНЯМ ---")
    p("=" * 80)

    for label, r_info in reports.items():
        fname = r_info.get("filename")
        content = r_info.get("content", "")
        p()
        p(f"### ОТЧЕТ: {label} (файл: {fname}) ###")
        p("-" * 60)
        p(content)
        p()

    out_file = os.path.join(SCRATCH, "sprint_full_summary.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

    print(f"Full summary written to {out_file} ({len(out_lines)} lines)")

if __name__ == "__main__":
    main()
