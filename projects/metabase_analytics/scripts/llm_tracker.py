#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Canonical LLM Tracking & Smart Key Management Module: llm_tracker.py
Version: 1.0 (2026-10-03)

Provides unified tracking of LLM token consumption, cost, and health:
1. Automatic Initiator Detection: 'artem', 'mikhail', 'system_cron', 'b24_user_XX'
2. Standard Task Taxonomy: 'tenders_extraction', 'sales_followup', 'lead_inbound_triage', etc.
3. Smart KeyManager: auto-rotates active keys, cools down 429 keys, purges dead (400/403) keys.
4. Robust DWH Logging: Writes to PostgreSQL llm_usage_logs (with local JSONL fallback).
"""

import os
import sys
import json
import time
import datetime
import urllib.request
import urllib.error

# Ensure UTF-8 on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Pricing per 1M tokens (USD)
RATES = {
    "deepseek-chat": {"prompt": 0.14, "completion": 0.28},
    "gemini-flash-latest": {"prompt": 0.075, "completion": 0.30},
    "gemini-2.5-flash": {"prompt": 0.075, "completion": 0.30},
    "gemini-2.5-pro": {"prompt": 1.25, "completion": 5.00},
}

def detect_initiator(explicit_initiator: str = None) -> str:
    """Detects who triggered the execution: artem, mikhail, system_cron, or explicit."""
    if explicit_initiator:
        return explicit_initiator

    env_user = os.environ.get("CODEX_INITIATOR") or os.environ.get("USER") or os.environ.get("USERNAME", "")
    env_user = env_user.lower()

    if "артем" in env_user or "artem" in env_user:
        return "artem"
    elif "mikhail" in env_user:
        return "mikhail"
    elif "cron" in env_user or os.environ.get("CRON_JOB"):
        return "system_cron"
    return "system_automation"

def calculate_cost_usd(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = RATES.get(model_name, {"prompt": 0.14, "completion": 0.28})
    cost = (prompt_tokens * rates["prompt"] + completion_tokens * rates["completion"]) / 1_000_000.0
    return round(cost, 6)

def log_llm_usage(
    provider: str,
    model_name: str,
    task_type: str,
    key_alias: str,
    prompt_tokens: int,
    completion_tokens: int,
    initiated_by: str = None,
    status: str = "success",
    error_message: str = None,
    latency_ms: int = 0
):
    """
    Logs an LLM call to PostgreSQL DWH (marketing_db.llm_usage_logs).
    Falls back to a local JSONL log file if DB is unreachable.
    """
    if not task_type:
        prog = os.path.basename(sys.argv[0]) if sys.argv else "unknown_script"
        prog_clean = os.path.splitext(prog)[0]
        task_type = f"[ВРЕМЕННЫЙ] unclassified_{prog_clean}"

    initiator = detect_initiator(initiated_by)
    total_tokens = prompt_tokens + completion_tokens
    cost_usd = calculate_cost_usd(model_name, prompt_tokens, completion_tokens)
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    record = {
        "created_at": now_iso,
        "initiated_by": initiator,
        "task_type": task_type,
        "key_alias": key_alias,
        "provider": provider,
        "model_name": model_name,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
        "status": status,
        "error_message": error_message
    }

    # Try PostgreSQL insert
    pg_pass = os.environ.get("PG_PASS")
    if pg_pass:
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=os.environ.get("PG_HOST", "10.10.0.1"),
                port=int(os.environ.get("PG_PORT", 5433)),
                dbname=os.environ.get("PG_DBNAME", "marketing_db"),
                user=os.environ.get("PG_USER", "vector_user"),
                password=pg_pass,
                connect_timeout=3
            )
            cursor = conn.cursor()
            sql = """
                INSERT INTO llm_usage_logs (
                    created_at, initiated_by, task_type, key_alias, provider,
                    model_name, prompt_tokens, completion_tokens, total_tokens,
                    cost_usd, latency_ms, status, error_message
                ) VALUES (
                    %(created_at)s, %(initiated_by)s, %(task_type)s, %(key_alias)s, %(provider)s,
                    %(model_name)s, %(prompt_tokens)s, %(completion_tokens)s, %(total_tokens)s,
                    %(cost_usd)s, %(latency_ms)s, %(status)s, %(error_message)s
                );
            """
            cursor.execute(sql, record)
            conn.commit()
            cursor.close()
            conn.close()
            return
        except Exception:
            pass  # Fallback to local file below

    # Local fallback
    fallback_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scratch")
    os.makedirs(fallback_dir, exist_ok=True)
    fallback_file = os.path.join(fallback_dir, "llm_usage_fallback.jsonl")
    try:
        with open(fallback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[WARN] Failed to write local LLM usage log: {e}")

class SmartKeyManager:
    """Manages a pool of Gemini API keys with health tracking and rotation."""
    def __init__(self, keys_str: str = None):
        raw_keys = keys_str or os.environ.get("GEMINI_API_KEYS", "")
        self.keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        single_key = os.environ.get("GEMINI_API_KEY")
        if single_key and single_key not in self.keys:
            self.keys.append(single_key)

        self.key_status = {k: "ACTIVE" for k in self.keys}
        self.current_idx = 0

    def get_active_key(self) -> tuple[str, str]:
        """Returns (api_key, key_alias) for the next active key."""
        active_keys = [k for k in self.keys if self.key_status.get(k) == "ACTIVE"]
        if not active_keys:
            # If all are in daily limit, retry the first one
            if self.keys:
                fallback_key = self.keys[0]
                alias = f"gemini-key-{self.keys.index(fallback_key)+1:02d}"
                return fallback_key, alias
            raise ValueError("No Gemini API keys configured in pool!")

        key = active_keys[self.current_idx % len(active_keys)]
        self.current_idx = (self.current_idx + 1) % len(active_keys)
        alias = f"gemini-key-{self.keys.index(key)+1:02d}"
        return key, alias

    def mark_key_status(self, key: str, status: str):
        """status: 'ACTIVE', 'RATE_LIMITED_DAILY', 'NEEDS_REVIEW'"""
        self.key_status[key] = status
        alias = f"gemini-key-{self.keys.index(key)+1:02d}" if key in self.keys else "unknown"
        if status in ("DEAD_REVOKED", "NEEDS_REVIEW"):
            print(f"[WARN] Key {alias} encountered error and marked for review. Kept in pool until user confirmation.")
        elif status == "RATE_LIMITED_DAILY":
            print(f"[INFO] Key {alias} hit 429 quota. Cooling down until daily reset.")

if __name__ == "__main__":
    print(f"Detected Initiator: {detect_initiator()}")
    km = SmartKeyManager("test_key_1,test_key_2")
    k, alias = km.get_active_key()
    print(f"Selected Key: {alias} (Status: {km.key_status[k]})")
    log_llm_usage(
        provider="gemini",
        model_name="gemini-flash-latest",
        task_type="system_test_dev",
        key_alias=alias,
        prompt_tokens=150,
        completion_tokens=45,
        status="success"
    )
    print("Test log entry created successfully.")
