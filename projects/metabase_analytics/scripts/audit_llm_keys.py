#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
LLM Key Health & Quota Diagnostic Tool: audit_llm_keys.py
Version: 2.0 (2026-10-03)

Tests all configured Gemini and DeepSeek API keys, classifies them:
- ACTIVE (200 OK)
- RATE_LIMITED_DAILY (429 ResourceExhausted)
- NEEDS_REVIEW (400, 401, 403 Invalid / Expired / Error)

IMPORTANT POLICY:
Does NOT automatically purge or exclude keys!
Sends an alert to Bitrix24 chat with details so the user (Artem) can verify
and explicitly decide whether to purge or keep each key.
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def mask_key(key: str) -> str:
    if not key or len(key) < 8:
        return "****"
    return f"{key[:6]}...{key[-4:]}"

def send_bitrix_chat_alert(message: str, b24_url: str = None, dialog_id: str = "1") -> bool:
    """Sends a notification message into Bitrix24 chat."""
    webhook_url = b24_url or os.environ.get("B24_WEBHOOK_URL", "").rstrip("/")
    if not webhook_url:
        print("[INFO] B24_WEBHOOK_URL not configured. Skipping Bitrix chat notification.")
        return False

    url = f"{webhook_url}/im.message.add.json"
    payload = json.dumps({
        "DIALOG_ID": dialog_id,
        "MESSAGE": message
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("result"):
                print("[OK] Alert successfully sent to Bitrix24 chat.")
                return True
    except Exception as ex:
        print(f"[WARN] Failed to send alert to Bitrix24: {ex}")
    return False

def test_gemini_key(api_key: str, model: str = "gemini-flash-latest") -> tuple[str, int, float, str]:
    """Returns (status, http_code, latency_ms, detail)"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": "ping"}]}],
        "generationConfig": {"maxOutputTokens": 1}
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    start_t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            latency = (time.time() - start_t) * 1000.0
            return "ACTIVE", 200, latency, "OK"
    except urllib.error.HTTPError as e:
        latency = (time.time() - start_t) * 1000.0
        err_body = e.read().decode("utf-8", errors="ignore")
        if e.code == 429:
            detail = "Quota Exceeded (RPD/RPM)"
            if "RESOURCE_EXHAUSTED" in err_body:
                detail = "Resource Exhausted (Daily Quota)"
            return "RATE_LIMITED_DAILY", 429, latency, detail
        elif e.code in (400, 401, 403):
            detail = f"Suspected Dead / Error ({e.code})"
            if "API_KEY_INVALID" in err_body:
                detail = "API Key Invalid / Expired"
            elif "PERMISSION_DENIED" in err_body:
                detail = "Permission Denied"
            return "NEEDS_REVIEW", e.code, latency, detail
        else:
            return "ERROR", e.code, latency, f"HTTP {e.code}"
    except Exception as ex:
        latency = (time.time() - start_t) * 1000.0
        return "NETWORK_ERROR", 0, latency, str(ex)[:40]

def test_deepseek_key(api_key: str) -> tuple[str, int, float, str]:
    url = "https://api.deepseek.com/chat/completions"
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1
    }).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    start_t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            latency = (time.time() - start_t) * 1000.0
            return "ACTIVE", 200, latency, "OK"
    except urllib.error.HTTPError as e:
        latency = (time.time() - start_t) * 1000.0
        if e.code == 402:
            return "OUT_OF_BALANCE", 402, latency, "Insufficient Balance"
        elif e.code in (401, 403):
            return "NEEDS_REVIEW", e.code, latency, "Invalid Token"
        elif e.code == 429:
            return "RATE_LIMITED_DAILY", 429, latency, "Rate Limit"
        return "ERROR", e.code, latency, f"HTTP {e.code}"
    except Exception as ex:
        latency = (time.time() - start_t) * 1000.0
        return "NETWORK_ERROR", 0, latency, str(ex)[:40]

def load_keys_from_env_file(filepath: str) -> dict:
    result = {}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    result[k] = v
    return result

def main():
    parser = argparse.ArgumentParser(description="Audit and diagnose health of LLM API keys (No Auto-Purge)")
    parser.add_argument("--env-file", help="Path to .env file containing GEMINI_API_KEYS")
    parser.add_argument("--keys", help="Comma-separated raw keys list to test directly")
    parser.add_argument("--model", default="gemini-flash-latest", help="Gemini model for testing")
    parser.add_argument("--db-sync", action="store_true", help="Sync key health status into PostgreSQL DWH")
    parser.add_argument("--notify-b24", action="store_true", help="Send alert message to Bitrix24 chat if errors found")
    args = parser.parse_args()

    env_vars = {}
    if args.env_file:
        env_vars = load_keys_from_env_file(args.env_file)
    else:
        for possible_env in ["C:/Users/Артем/tender-rag-api/.env", ".env", "projects/metabase_analytics/.env"]:
            if os.path.exists(possible_env):
                env_vars = load_keys_from_env_file(possible_env)
                break

    gemini_keys_str = args.keys or env_vars.get("GEMINI_API_KEYS") or os.environ.get("GEMINI_API_KEYS", "")
    single_gemini = env_vars.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
    deepseek_key = env_vars.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY", "")

    gemini_keys = [k.strip() for k in gemini_keys_str.split(",") if k.strip()]
    if single_gemini and single_gemini not in gemini_keys:
        gemini_keys.append(single_gemini)

    print("\n=======================================================")
    print("       LLM API KEY HEALTH AUDIT & DIAGNOSTICS")
    print("=======================================================")
    print(f"Found Gemini Keys:   {len(gemini_keys)}")
    print(f"Found DeepSeek Key:  {'Configured' if deepseek_key else 'Not configured'}\n")

    results = []

    # 1. Audit Gemini Keys
    for idx, key in enumerate(gemini_keys, 1):
        alias = f"gemini-key-{idx:02d}"
        masked = mask_key(key)
        print(f"Testing {alias} ({masked})...", end="", flush=True)
        status, code, latency, detail = test_gemini_key(key, args.model)
        
        status_tag = "[ACTIVE]" if status == "ACTIVE" else ("[RATE_LIMIT]" if status == "RATE_LIMITED_DAILY" else "[REVIEW]")
        print(f" -> {status_tag} {status} ({code}) [{latency:.0f}ms] - {detail}")

        results.append({
            "alias": alias,
            "provider": "gemini",
            "key": key,
            "masked": masked,
            "status": status,
            "code": code,
            "latency": latency,
            "detail": detail
        })

    # 2. Audit DeepSeek Key
    if deepseek_key:
        alias = "deepseek-main"
        masked = mask_key(deepseek_key)
        print(f"Testing {alias} ({masked})...", end="", flush=True)
        status, code, latency, detail = test_deepseek_key(deepseek_key)
        status_tag = "[ACTIVE]" if status == "ACTIVE" else ("[RATE_LIMIT]" if status in ("RATE_LIMITED_DAILY", "OUT_OF_BALANCE") else "[REVIEW]")
        print(f" -> {status_tag} {status} ({code}) [{latency:.0f}ms] - {detail}")
        results.append({
            "alias": alias,
            "provider": "deepseek",
            "key": deepseek_key,
            "masked": masked,
            "status": status,
            "code": code,
            "latency": latency,
            "detail": detail
        })

    # Summary
    active_count = sum(1 for r in results if r["status"] == "ACTIVE")
    rate_limit_count = sum(1 for r in results if r["status"] == "RATE_LIMITED_DAILY")
    review_count = sum(1 for r in results if r["status"] == "NEEDS_REVIEW")
    err_count = len(results) - (active_count + rate_limit_count + review_count)

    print("\n------------------- AUDIT SUMMARY -------------------")
    print(f"[OK]     Active & Ready:               {active_count}")
    print(f"[WAIT]   In Daily Quota (429):         {rate_limit_count}")
    print(f"[ALERT]  Needs Review / Error:         {review_count}")
    if err_count > 0:
        print(f"[ERR]    Other Errors:                 {err_count}")

    # POLICY ENFORCEMENT: Never auto-purge! Notify user instead
    if review_count > 0:
        alert_lines = [f"⚠️ ВНИМАНИЕ: При проверке LLM-ключей {review_count} ключ(ей) вернули ошибку и требуют вашего решения:"]
        for r in results:
            if r["status"] == "NEEDS_REVIEW":
                alert_lines.append(f"• {r['alias']} ({r['masked']}) — Ошибка {r['code']}: {r['detail']}")
        alert_lines.append("\nКлючи НЕ исключены автоматически. Напишите подтверждение, если их нужно исключить из пула.")
        alert_msg = "\n".join(alert_lines)

        print(f"\n{alert_msg}")

        if args.notify_b24:
            send_bitrix_chat_alert(alert_msg)
    elif len(results) > 0:
        print("\n[OK] Все проверенные ключи функционируют штатно!")
    else:
        print("\n[INFO] Нет ключей для проверки. Укажите --keys или --env-file.")

    # DB Sync
    if args.db_sync and results:
        pg_pass = os.environ.get("PG_PASS")
        if not pg_pass:
            print("[WARN] Skipping DB sync: PG_PASS environment variable not set.")
            return

        try:
            import psycopg2
            from psycopg2.extras import execute_values
            conn = psycopg2.connect(
                host=os.environ.get("PG_HOST", "10.10.0.1"),
                port=int(os.environ.get("PG_PORT", 5433)),
                dbname=os.environ.get("PG_DBNAME", "marketing_db"),
                user=os.environ.get("PG_USER", "vector_user"),
                password=pg_pass
            )
            cursor = conn.cursor()
            upsert_sql = """
                INSERT INTO llm_keys_status (
                    key_alias, provider, masked_key, status, last_tested_at, last_error_code, last_error_message
                ) VALUES %s
                ON CONFLICT (key_alias) DO UPDATE SET
                    status = EXCLUDED.status,
                    last_tested_at = EXCLUDED.last_tested_at,
                    last_error_code = EXCLUDED.last_error_code,
                    last_error_message = EXCLUDED.last_error_message;
            """
            rows = [(r["alias"], r["provider"], r["masked"], r["status"], "NOW()", r["code"], r["detail"]) for r in results]
            execute_values(cursor, upsert_sql, rows)
            conn.commit()
            cursor.close()
            conn.close()
            print("[OK] Successfully updated llm_keys_status in PostgreSQL.")
        except Exception as ex:
            print(f"[ERROR] Failed to sync to PostgreSQL: {ex}")

if __name__ == "__main__":
    main()
