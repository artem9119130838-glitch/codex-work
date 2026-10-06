#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical Session Wishes & Transcripts Search Pipeline: search_session_wishes.py
Version: 1.0 (2026-10-05)

Consolidates all transcript exploration and user request extraction tools
into a single canonical CLI tool. Searches all session history transcripts in
`C:\\Users\\Артем\\.gemini\\antigravity\\brain` for explicit user wishes, prompts,
and requirements with clustering, filtering, and reporting.

Usage:
    py projects/metabase_analytics/scripts/search_session_wishes.py --keywords metabase,токен,дашборд
    py projects/metabase_analytics/scripts/search_session_wishes.py --keywords metabase --cluster --export wishes.json
"""

import os
import sys
import json
import glob
import re
import argparse

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BRAIN_DIR = r"C:\Users\Артем\.gemini\antigravity\brain"

DEFAULT_KEYWORDS = [
    "metabase", "метабейз", "метабаз", "дашборд", "dashboard",
    "воронка", "лимит", "токен", "dwh", "marketing_db", "cron", "крон", "светофор"
]

def search_transcripts(brain_dir, keywords_pattern):
    transcript_files = glob.glob(os.path.join(brain_dir, "*", ".system_generated", "logs", "transcript.jsonl"))
    user_requests = []

    for tf in transcript_files:
        conv_id = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(tf))))
        try:
            with open(tf, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        step = json.loads(line)
                    except Exception:
                        continue
                    
                    src = step.get("source", "")
                    stype = step.get("type", "")
                    if src == "USER_EXPLICIT" or stype == "USER_INPUT":
                        content = step.get("content", "")
                        if not content or len(content.strip()) < 5:
                            continue
                        
                        if keywords_pattern.search(content):
                            clean = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", content, flags=re.DOTALL)
                            clean = re.sub(r"<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>", "", clean, flags=re.DOTALL)
                            clean = re.sub(r"<USER_REQUEST>|</USER_REQUEST>", "", clean).strip()
                            
                            user_requests.append({
                                "conv_id": conv_id,
                                "created_at": step.get("created_at", ""),
                                "text": clean
                            })
        except Exception:
            continue

    user_requests.sort(key=lambda x: x["created_at"])
    return user_requests

def cluster_requests(requests):
    clusters = {
        "llm_limits_and_keys": [],
        "dashboards_and_cards": [],
        "funnel_and_deals": [],
        "cron_and_automation": [],
        "permissions_and_security": [],
        "other": []
    }
    for r in requests:
        t = r["text"].lower()
        if any(k in t for k in ["токен", "ключ", "лимит", "расход", "llm", "deepseek", "gemini", "светофор"]):
            clusters["llm_limits_and_keys"].append(r)
        elif any(k in t for k in ["дашборд", "карточк", "card", "dashboard", "metabase"]):
            clusters["dashboards_and_cards"].append(r)
        elif any(k in t for k in ["воронка", "тендер", "сделк", "отказ", "кп"]):
            clusters["funnel_and_deals"].append(r)
        elif any(k in t for k in ["крон", "cron", "daemon", "автоматиз"]):
            clusters["cron_and_automation"].append(r)
        elif any(k in t for k in ["менеджер", "доступ", "права", "пароль"]):
            clusters["permissions_and_security"].append(r)
        else:
            clusters["other"].append(r)
    return clusters

def main():
    parser = argparse.ArgumentParser(description="Canonical Session Wishes & Transcripts Search Pipeline")
    parser.add_argument("--keywords", help="Comma-separated keywords regex pattern", default=None)
    parser.add_argument("--brain-dir", default=BRAIN_DIR, help="Path to Antigravity brain logs")
    parser.add_argument("--cluster", action="store_true", help="Group matching requests into thematic clusters")
    parser.add_argument("--export", help="Output JSON filepath for found requests")
    parser.add_argument("--limit", type=int, default=50, help="Max results to print in console")
    args = parser.parse_args()

    kw_list = [k.strip() for k in args.keywords.split(",")] if args.keywords else DEFAULT_KEYWORDS
    pattern = re.compile("|".join(kw_list), re.IGNORECASE)

    print(f"=== Scanning transcripts in {args.brain_dir} ===")
    print(f"Keywords: {', '.join(kw_list)}")

    results = search_transcripts(args.brain_dir, pattern)
    print(f"Total matching requests found: {len(results)}")

    if args.export:
        with open(args.export, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"[OK] Exported {len(results)} items to {args.export}")

    if args.cluster:
        clustered = cluster_requests(results)
        print("\n=== CLUSTERED RESULTS ===")
        for cname, items in clustered.items():
            print(f"\n--- {cname.upper()} ({len(items)} requests) ---")
            for it in items[:5]:
                preview = it['text'].replace('\n', ' ')[:140]
                print(f"  [{it['created_at'][:10]} | {it['conv_id'][:8]}] {preview}...")
    else:
        for idx, r in enumerate(results[:args.limit], 1):
            preview = r['text'].replace('\n', ' ')[:140]
            print(f"#{idx} [{r['created_at'][:10]} | {r['conv_id'][:8]}] {preview}...")

if __name__ == "__main__":
    main()
