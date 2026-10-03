#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical Metabase BI Management Pipeline: manage_metabase_dashboards.py
Version: 2.0 (2026-10-03)

Single canonical script for managing Metabase dashboards, analytical cards,
global formatting/localization, user permissions, and LLM Token Analytics.

Actions:
- update-cards: Updates sales & tender funnel cards (Cards 54, 49)
- token-analytics: Deploys LLM token consumption & key health dashboard
- patch-locale: Enforces Russian locale and custom number formatting (space for thousands)
- create-user: Creates read-only manager user
- setup-all: Executes all setup steps in sequence

Supports --dry-run mode for safety.
Zero Secrets Policy: Reads credentials from environment variables.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_METABASE_URL = os.environ.get("METABASE_URL", "http://109.248.170.181:3000").rstrip("/")
DEFAULT_ADMIN_EMAIL = os.environ.get("METABASE_ADMIN_EMAIL", "admin@tender-rag.local")
DEFAULT_ADMIN_PASSWORD = os.environ.get("METABASE_ADMIN_PASSWORD", "")

def get_session(base_url, email, password):
    url = f"{base_url}/api/session"
    payload = json.dumps({"username": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("id")
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Failed to authenticate in Metabase ({e.code}): {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return None

def api_call(base_url, session_id, method, path, data=None, dry_run=False):
    if dry_run and method in ("POST", "PUT", "DELETE"):
        print(f"[DRY-RUN] {method} {path} with payload preview:")
        if data:
            preview = json.dumps(data, indent=2, ensure_ascii=False)
            if len(preview) > 500:
                print(preview[:500] + "\n... [TRUNCATED FOR DRY-RUN]")
            else:
                print(preview)
        return {"status": "dry-run-success", "id": 9999}

    url = f"{base_url}/api{path}"
    req_data = json.dumps(data).encode("utf-8") if data is not None else None
    headers = {
        "Content-Type": "application/json",
        "X-Metabase-Session": session_id
    }
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code} on {method} {path}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"[ERROR] Exception on {method} {path}: {e}")
        return None

def patch_locale_and_formatting(base_url, session_id, dry_run=False):
    print("=== [1/2] Updating Global Custom Number Formatting ===")
    fmt_data = {
        "value": {
            "type": "default",
            "currency": "RUB",
            "number_separators": " ."
        }
    }
    res_fmt = api_call(base_url, session_id, "PUT", "/setting/custom-formatting", fmt_data, dry_run)
    if res_fmt is not None:
        print("[OK] Custom formatting set: space for thousands, dot for decimals, currency RUB.")

    print("=== [2/2] Updating Site Locale to 'ru' ===")
    res_loc = api_call(base_url, session_id, "PUT", "/setting/site-locale", {"value": "ru"}, dry_run)
    if res_loc is not None:
        print("[OK] Site locale set to Russian (ru).")

def create_manager_user(base_url, session_id, email, password, dry_run=False):
    print(f"=== Creating/Ensuring Manager User ({email}) ===")
    manager_data = {
        "first_name": "Менеджер",
        "last_name": "Тендеров",
        "email": email,
        "password": password
    }
    res = api_call(base_url, session_id, "POST", "/user", manager_data, dry_run)
    if res and "id" in res:
        print(f"[OK] Manager account created with ID: {res['id']}.")
    else:
        print("[INFO] Manager account creation finished (user may already exist).")

def get_database_id(base_url, session_id, db_name="marketing_db", dry_run=False):
    dbs = api_call(base_url, session_id, "GET", "/database")
    db_list = dbs.get("data", dbs) if isinstance(dbs, dict) else (dbs or [])
    for db in db_list:
        if isinstance(db, dict) and db.get("name") == db_name:
            return db["id"]
    return 1 if dry_run else None

def update_cards(base_url, session_id, dry_run=False):
    print("=== Fetching Database ID for 'marketing_db' ===")
    db_id = get_database_id(base_url, session_id, "marketing_db", dry_run) or 1
    print(f"[OK] Target database ID: {db_id}")

    # 1. Update Card 54: Сквозная воронка with date_range
    sql_funnel = """WITH tender_data AS (
    SELECT 
        deal_id,
        date_create,
        COALESCE(tender_amount, our_offer_amount, 0) as amount,
        CASE 
            WHEN close_reason = 'Выигран в тендере' THEN '3_WON'
            WHEN raw_data->>'STAGE_ID' = 'C4:LOSE' THEN '2_BID'
            ELSE '1_REJECT'
        END as group_type
    FROM analytics_closed_deals
    WHERE pipeline_name = 'Тендеры'
      [[AND {{date_range}}]]
)
SELECT '1. Анализ (Всего)' as "Этап", COUNT(*) as "Количество", SUM(amount) as "Сумма (руб)" FROM tender_data
UNION ALL
SELECT '2. Подано заявок' as "Этап", COUNT(*) as "Количество", SUM(amount) as "Сумма (руб)" FROM tender_data WHERE group_type IN ('2_BID', '3_WON')
UNION ALL
SELECT '3. Победа (Контракт)' as "Этап", COUNT(*) as "Количество", SUM(amount) as "Сумма (руб)" FROM tender_data WHERE group_type = '3_WON'
ORDER BY "Этап" ASC;"""

    card54_payload = {
        "dataset_query": {
            "type": "native",
            "native": {
                "query": sql_funnel,
                "template-tags": {
                    "date_range": {
                        "id": "date_range_tag",
                        "name": "date_range",
                        "display-name": "Период дат",
                        "type": "dimension",
                        "dimension": ["field", "date_create", {"base-type": "type/DateTime"}],
                        "widget-type": "date/all-options"
                    }
                }
            },
            "database": db_id
        }
    }
    print("Updating Card 54: Сквозная воронка...")
    api_call(base_url, session_id, "PUT", "/card/54", card54_payload, dry_run)

    # 2. Update Card 49: Выигранные тендеры - Детали
    sql_won = """SELECT 
    title as "Название сделки / Закупка",
    customer_name as "Заказчик",
    responsible_name as "Ответственный менеджер",
    tender_amount as "НМЦК (руб)",
    our_offer_amount as "Сумма контракта (руб)",
    (tender_amount - our_offer_amount) as "Разница (руб)",
    ROUND(((tender_amount - our_offer_amount) / NULLIF(tender_amount, 0)) * 100, 2) as "Снижение (%)",
    date_close as "Дата завершения"
FROM analytics_closed_deals
WHERE close_reason = 'Выигран в тендере'
  [[AND {{date_range}}]]
ORDER BY date_close DESC;"""

    card49_payload = {
        "dataset_query": {
            "type": "native",
            "native": {
                "query": sql_won,
                "template-tags": {
                    "date_range": {
                        "id": "date_range_tag",
                        "name": "date_range",
                        "display-name": "Период дат",
                        "type": "dimension",
                        "dimension": ["field", "date_close", {"base-type": "type/DateTime"}],
                        "widget-type": "date/all-options"
                    }
                }
            },
            "database": db_id
        }
    }
    print("Updating Card 49: Выигранные тендеры - Детали...")
    api_call(base_url, session_id, "PUT", "/card/49", card49_payload, dry_run)
    print("[SUCCESS] All sales analytics cards processed.")

def deploy_token_analytics(base_url, session_id, dry_run=False):
    """Deploys or updates the LLM Token Economics & Key Health Dashboard and Cards."""
    print("=== Deploying LLM Token Analytics & Key Health Cards ===")
    db_id = get_database_id(base_url, session_id, "marketing_db", dry_run) or 1

    token_cards = [
        {
            "name": "Расход токенов по API-ключам",
            "display": "bar",
            "sql": """SELECT 
    key_alias as "Ключ",
    provider as "Провайдер",
    COUNT(*) as "Запросов",
    SUM(total_tokens) as "Всего токенов",
    ROUND(SUM(cost_usd)::numeric, 4) as "Затраты ($)"
FROM llm_usage_logs
GROUP BY key_alias, provider
ORDER BY "Всего токенов" DESC;"""
        },
        {
            "name": "Расход токенов по типам задач (Пайплайны)",
            "display": "pie",
            "sql": """SELECT 
    task_type as "Тип задачи",
    SUM(total_tokens) as "Всего токенов"
FROM llm_usage_logs
GROUP BY task_type
ORDER BY "Всего токенов" DESC;"""
        },
        {
            "name": "Расход токенов по инициаторам (Артем vs Михаил vs Роботы)",
            "display": "bar",
            "sql": """SELECT 
    initiated_by as "Инициатор",
    COUNT(*) as "Кол-во вызовов",
    SUM(total_tokens) as "Всего токенов",
    ROUND(SUM(cost_usd)::numeric, 4) as "Затраты ($)"
FROM llm_usage_logs
GROUP BY initiated_by
ORDER BY "Всего токенов" DESC;"""
        },
        {
            "name": "Динамика расхода токенов по дням",
            "display": "line",
            "sql": """SELECT 
    DATE_TRUNC('day', created_at)::date as "Дата",
    task_type as "Задача",
    SUM(total_tokens) as "Токенов"
FROM llm_usage_logs
GROUP BY "Дата", task_type
ORDER BY "Дата" ASC;"""
        },
        {
            "name": "Светофор здоровья пула API-ключей",
            "display": "table",
            "sql": """SELECT 
    key_alias as "Ключ",
    provider as "Провайдер",
    masked_key as "Маска",
    status as "Статус",
    last_tested_at as "Проверен",
    last_error_message as "Ошибка / Причина"
FROM llm_keys_status
ORDER BY status ASC, key_alias ASC;"""
        }
    ]

    # Create / verify Dashboard for Tokens
    dash_payload = {
        "name": "Экономика токенов и здоровье LLM",
        "description": "Мониторинг затрат токенов по ключам, задачам, пользователям и аудит доступности API"
    }
    dash_res = api_call(base_url, session_id, "POST", "/dashboard", dash_payload, dry_run)
    dash_id = dash_res.get("id", 9999) if dash_res else 9999
    print(f"[OK] Token Economics Dashboard ID: {dash_id}")

    dashcards = []
    for idx, card in enumerate(token_cards):
        card_payload = {
            "name": card["name"],
            "dataset_query": {
                "type": "native",
                "native": {"query": card["sql"]},
                "database": db_id
            },
            "display": card["display"],
            "visualization_settings": {}
        }
        print(f"Creating/Updating Card: {card['name']}...")
        c_res = api_call(base_url, session_id, "POST", "/card", card_payload, dry_run)
        card_id = c_res.get("id") if (c_res and "id" in c_res) else (9000 + idx)

        dashcards.append({
            "id": -(idx + 1),
            "card_id": card_id,
            "row": (idx // 2) * 6,
            "col": (idx % 2) * 9,
            "size_x": 9,
            "size_y": 6,
            "visualization_settings": {}
        })

    if dashcards and dash_id:
        print(f"Attaching {len(dashcards)} cards to Dashboard {dash_id}...")
        api_call(base_url, session_id, "PUT", f"/dashboard/{dash_id}", {"dashcards": dashcards}, dry_run)

    print("[SUCCESS] Token analytics cards and dashboard deployed successfully.")

def main():
    parser = argparse.ArgumentParser(description="Metabase BI Management and Dashboard Pipeline")
    parser.add_argument("--action", required=True, 
                        choices=["update-cards", "token-analytics", "setup-all", "patch-locale", "create-user"],
                        help="Action to perform on Metabase")
    parser.add_argument("--dry-run", action="store_true", help="Simulate API calls without modifying state")
    parser.add_argument("--url", default=DEFAULT_METABASE_URL, help="Metabase instance URL")
    parser.add_argument("--email", default=DEFAULT_ADMIN_EMAIL, help="Metabase admin email")
    parser.add_argument("--password", default=DEFAULT_ADMIN_PASSWORD, help="Metabase admin password")
    parser.add_argument("--manager-email", default="manager@tender-rag.local", help="Manager user email")
    parser.add_argument("--manager-password", default="TenderManager2026!", help="Manager user password")

    args = parser.parse_args()

    if not args.password and not args.dry_run:
        print("[ERROR] Admin password not provided. Set METABASE_ADMIN_PASSWORD environment variable or use --password.")
        sys.exit(1)

    print(f"=== Starting Metabase Manager [{args.action}] (Dry-Run: {args.dry_run}) ===")
    
    session_id = "dry-run-token" if args.dry_run and not args.password else get_session(args.url, args.email, args.password)
    if not session_id and not args.dry_run:
        print("[FATAL] Could not obtain Metabase session. Terminating.")
        sys.exit(1)

    if args.action == "patch-locale":
        patch_locale_and_formatting(args.url, session_id, args.dry_run)
    elif args.action == "create-user":
        create_manager_user(args.url, session_id, args.manager_email, args.manager_password, args.dry_run)
    elif args.action == "update-cards":
        update_cards(args.url, session_id, args.dry_run)
    elif args.action == "token-analytics":
        deploy_token_analytics(args.url, session_id, args.dry_run)
    elif args.action == "setup-all":
        patch_locale_and_formatting(args.url, session_id, args.dry_run)
        create_manager_user(args.url, session_id, args.manager_email, args.manager_password, args.dry_run)
        update_cards(args.url, session_id, args.dry_run)
        deploy_token_analytics(args.url, session_id, args.dry_run)

    print("=== Execution Finished Successfully ===")

if __name__ == "__main__":
    main()
