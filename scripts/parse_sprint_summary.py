#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/parse_sprint_summary.py
===============================
Извлекает конкретные детали: что сделано, что нет, баги, финансы, замечания Артема, ответы Михаила.
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

print("="*70)
print("1. ЗАМЕЧАНИЯ АРТЕМА И ДИАЛОГ С МИХАИЛОМ")
print("="*70)
lines = data["chat"].splitlines()
for l in lines:
    if l.startswith("[2026-"):
        print("\n" + l)
    elif l.strip():
        print("  " + l[:120])

print("\n" + "="*70)
print("2. GIT ВЕТКИ И КОММИТЫ")
print("="*70)
print("Branches:")
for b in data["git"]["branches"]:
    print(" ", b)
print("\nCommits:")
for c in data["git"]["recent_commits"]:
    print(" ", c)
