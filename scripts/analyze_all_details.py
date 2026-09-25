#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/analyze_all_details.py
==============================
Глубокий структурированный анализ всех дней спринта, переписки и багов.
"""

import os
import sys
import json
import re

SCRATCH = r"C:\Codex_Personal\scratch"
DOWNLOADS = r"C:\Users\Артем\Downloads"

def read_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def main():
    chat_text = read_file(os.path.join(SCRATCH, "chat_breakdown.txt"))
    
    # Reports
    day1 = read_file(os.path.join(DOWNLOADS, "sprint_day_1_report.md"))
    day2 = read_file(os.path.join(DOWNLOADS, "report.md"))
    day3 = read_file(os.path.join(DOWNLOADS, "report (1).md"))
    day4 = read_file(os.path.join(DOWNLOADS, "report (2).md"))
    day5 = read_file(os.path.join(DOWNLOADS, "report (3).md"))
    day6 = read_file(os.path.join(DOWNLOADS, "report (4).md"))
    day7 = read_file(os.path.join(DOWNLOADS, "report (5).md"))
    cost = read_file(os.path.join(DOWNLOADS, "cost_report.md"))
    
    # Let's inspect git branches and commits in tender-rag-api
    import subprocess
    git_log_proc = subprocess.run(
        ["git", "log", "--all", "-n", "30", "--format=%h|%ad|%an|%s", "--date=short"],
        cwd=r"C:\Codex_Shared\projects\tender-extraction-lab",
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    git_commits = git_log_proc.stdout.strip().splitlines()
    
    # Git branches
    git_branch_proc = subprocess.run(
        ["git", "branch", "-a", "-v"],
        cwd=r"C:\Codex_Shared\projects\tender-extraction-lab",
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    git_branches = git_branch_proc.stdout.strip().splitlines()

    analysis = {
        "chat": chat_text,
        "git": {
            "branches": git_branches,
            "recent_commits": git_commits[:15]
        },
        "days": {
            "day1": day1,
            "day2": day2,
            "day3": day3,
            "day4": day4,
            "day5": day5,
            "day6": day6,
            "day7": day7,
            "cost": cost
        }
    }
    
    with open(os.path.join(SCRATCH, "sprint_raw_analyzed.json"), "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
        
    print("Exported sprint_raw_analyzed.json successfully.")

if __name__ == "__main__":
    main()
