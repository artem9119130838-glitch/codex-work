#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/inspect_reports_detail.py
=================================
Детальный парсинг отчетов и переписки чата для составления исчерпывающего резюме.
"""

import os
import sys
import json

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

with open(r"C:\Codex_Personal\scratch\full_sprint_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("="*60)
print("1. ХРОНОЛОГИЯ И СУТЬ ПЕРЕПИСКИ В ЧАТЕ БИТРИКС24")
print("="*60)
for m in data.get("chat_messages", []):
    author = m["author"]
    date = m["date"][:16].replace("T", " ")
    text = m["text"].strip().replace("\n", " ")
    if len(text) > 120:
        text = text[:120] + "..."
    print(f"[{date}] {author}: {text}")

print("\n" + "="*60)
print("2. СТРУКТУРА И СОДЕРЖАНИЕ ОТЧЕТОВ")
print("="*60)
for label, r in data.get("reports", {}).items():
    print(f"\n--- {label} ({r.get('filename')}) ---")
    content = r.get("content", "")
    lines = content.splitlines()
    for l in lines:
        if l.startswith("#") or "ошибк" in l.lower() or "проблем" in l.lower() or "итог" in l.lower() or "статус" in l.lower() or "баг" in l.lower() or "недодел" in l.lower() or "план" in l.lower():
            print("  ", l[:140])
