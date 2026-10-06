#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical Metabase BI Management Pipeline: manage_metabase_dashboards.py
Version: 2.4 (2026-10-05)

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

def get_field_id(base_url, session_id, db_id, table_name, field_name, dry_run=False, fallback_id=None):
    """Fetches integer Field ID from database metadata to prevent Metabase H2 conversion error [22018-214]."""
    if dry_run and session_id == "dry-run-token":
        return fallback_id
    meta = api_call(base_url, session_id, "GET", f"/database/{db_id}/metadata", dry_run=False)
    if meta and "tables" in meta:
        for t in meta["tables"]:
            if t.get("name") == table_name:
                for f in t.get("fields", []):
                    if f.get("name") == field_name:
                        return f.get("id")
    return fallback_id

def update_cards(base_url, session_id, dry_run=False):
    print("=== Fetching Database ID for 'marketing_db' ===")
    db_id = get_database_id(base_url, session_id, "marketing_db", dry_run) or 2
    print(f"[OK] Target database ID: {db_id}")

    date_create_id = get_field_id(base_url, session_id, db_id, "analytics_closed_deals", "date_create", dry_run, 76)
    date_close_id = get_field_id(base_url, session_id, db_id, "analytics_closed_deals", "date_close", dry_run, 77)
    print(f"[OK] Resolved Field IDs: date_create={date_create_id}, date_close={date_close_id}")

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
                        "dimension": ["field", date_create_id, None],
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
                        "dimension": ["field", date_close_id, None],
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
    db_id = get_database_id(base_url, session_id, "marketing_db", dry_run) or 2

    token_cards = [
        {
            "id": 68,
            "name": "Сводный расход: Инициатор ➤ Пайплайн ➤ Ключ",
            "display": "table",
            "sql": """SELECT 
    CASE 
        WHEN initiated_by IS NOT NULL AND initiated_by != 'system_automation' THEN initiated_by
        WHEN project_name = 'email_ai' THEN 'Робот Email & Реанимация (VPS Cron)'
        ELSE 'Системная автоматизация (VPS)'
    END AS "Инициатор",
    CASE 
        WHEN request_type = 'company_summary' THEN 'Суммаризация компаний (DWH)'
        WHEN request_type = 'contact_summary' THEN 'Суммаризация контактов (Email AI)'
        WHEN request_type = 'client_intelligence_summary' THEN 'Досье клиента (Intelligence)'
        WHEN request_type = 'reactivation_draft_step1' THEN 'Реанимация лидов: Шаг 1 (Вводное КП)'
        WHEN request_type = 'reactivation_draft_step2' THEN 'Реанимация лидов: Шаг 2 (Презентация)'
        WHEN request_type = 'reactivation_draft_step3' THEN 'Реанимация лидов: Шаг 3 (Каталог продукции)'
        WHEN request_type = 'reactivation_draft_step4' THEN 'Реанимация лидов: Шаг 4 (Спецусловия/Скидки)'
        WHEN request_type = 'reactivation_draft_step5' THEN 'Реанимация лидов: Шаг 5 (Контрольный звонок/Письмо)'
        WHEN request_type = 'reactivation_draft_step6' THEN 'Реанимация лидов: Шаг 6 (Финальный статус)'
        WHEN request_type = 'test' THEN 'Тестовые вызовы'
        ELSE CONCAT('[ВРЕМЕННЫЙ] unclassified_', request_type)
    END AS "Проект / Пайплайн",
    CASE 
        WHEN api_key_mask LIKE '%94Cw' THEN 'Gemini-1 (..94Cw)'
        WHEN api_key_mask LIKE '%aZ1g' THEN 'Gemini-2 (..aZ1g)'
        WHEN api_key_mask LIKE '%VuTA' THEN 'Gemini-3 (..VuTA)'
        WHEN api_key_mask = 'DEEPSEEK_API_KEY' OR provider = 'deepseek' THEN 'DeepSeek-V3 Main'
        ELSE api_key_mask
    END AS "API-Ключ",
    COUNT(*) FILTER (WHERE total_tokens > 0) AS "Успешных",
    COUNT(*) FILTER (WHERE total_tokens = 0) AS "Ошибок/Таймаутов",
    COALESCE(SUM(prompt_tokens), 0) AS "Входных токенов",
    COALESCE(SUM(completion_tokens), 0) AS "Выходных токенов",
    COALESCE(SUM(total_tokens), 0) AS "Всего токенов",
    ROUND(SUM(
        CASE 
            WHEN cost_usd > 0 THEN cost_usd
            WHEN estimated_cost > 0 THEN estimated_cost
            WHEN provider = 'deepseek' OR model_name LIKE '%deepseek%' THEN (COALESCE(prompt_tokens, 0) * 0.14 + COALESCE(completion_tokens, 0) * 0.28) / 1000000.0
            WHEN model_name LIKE '%flash-lite%' THEN (COALESCE(prompt_tokens, 0) * 0.0375 + COALESCE(completion_tokens, 0) * 0.15) / 1000000.0
            ELSE (COALESCE(prompt_tokens, 0) * 0.075 + COALESCE(completion_tokens, 0) * 0.30) / 1000000.0
        END
    )::numeric, 4) AS "Затраты ($)"
FROM llm_usage_logs
GROUP BY 1, 2, 3
ORDER BY "Всего токенов" DESC;"""
        },
        {
            "id": 69,
            "name": "Расход токенов по пайплайнам (Бизнес-задачи)",
            "display": "pie",
            "sql": """SELECT 
    CASE 
        WHEN request_type = 'company_summary' THEN 'Суммаризация компаний (DWH)'
        WHEN request_type = 'contact_summary' THEN 'Суммаризация контактов (Email AI)'
        WHEN request_type = 'client_intelligence_summary' THEN 'Досье клиента (Intelligence)'
        WHEN request_type LIKE 'reactivation_draft%' THEN 'Реанимация лидов (Шаги 1-6)'
        WHEN request_type = 'test' THEN 'Тестовые вызовы'
        ELSE CONCAT('[ВРЕМЕННЫЙ] unclassified_', request_type)
    END AS "Тип задачи / Пайплайн",
    SUM(total_tokens) AS "Всего токенов"
FROM llm_usage_logs
WHERE total_tokens > 0
GROUP BY 1
ORDER BY "Всего токенов" DESC;"""
        },
        {
            "id": 70,
            "name": "Расход токенов по инициаторам (Артем vs Михаил vs Роботы)",
            "display": "table",
            "sql": """SELECT 
    CASE 
        WHEN initiated_by IS NOT NULL AND initiated_by != 'system_automation' THEN initiated_by
        WHEN project_name = 'email_ai' THEN 'Робот Email & Реанимация (VPS Cron)'
        ELSE 'Системная автоматизация (VPS)'
    END AS "Инициатор",
    COUNT(*) FILTER (WHERE total_tokens > 0) AS "Успешных вызовов",
    COUNT(*) FILTER (WHERE total_tokens = 0) AS "Сбоев / Таймаутов",
    COALESCE(SUM(prompt_tokens), 0) AS "Входных токенов",
    COALESCE(SUM(completion_tokens), 0) AS "Выходных токенов",
    COALESCE(SUM(total_tokens), 0) AS "Всего токенов",
    ROUND(SUM(
        CASE 
            WHEN cost_usd > 0 THEN cost_usd
            WHEN estimated_cost > 0 THEN estimated_cost
            WHEN provider = 'deepseek' OR model_name LIKE '%deepseek%' THEN (COALESCE(prompt_tokens, 0) * 0.14 + COALESCE(completion_tokens, 0) * 0.28) / 1000000.0
            WHEN model_name LIKE '%flash-lite%' THEN (COALESCE(prompt_tokens, 0) * 0.0375 + COALESCE(completion_tokens, 0) * 0.15) / 1000000.0
            ELSE (COALESCE(prompt_tokens, 0) * 0.075 + COALESCE(completion_tokens, 0) * 0.30) / 1000000.0
        END
    )::numeric, 4) AS "Затраты ($)"
FROM llm_usage_logs
GROUP BY 1
ORDER BY "Всего токенов" DESC;"""
        },
        {
            "id": 71,
            "name": "Динамика расхода токенов по дням",
            "display": "line",
            "sql": """SELECT 
    DATE_TRUNC('day', created_at)::date AS "Дата",
    CASE 
        WHEN provider = 'deepseek' OR model_name LIKE '%deepseek%' THEN 'DeepSeek'
        WHEN provider = 'gemini' THEN 'Gemini'
        ELSE provider
    END AS "Провайдер",
    SUM(total_tokens) AS "Токенов",
    ROUND(SUM(
        CASE 
            WHEN cost_usd > 0 THEN cost_usd
            WHEN estimated_cost > 0 THEN estimated_cost
            WHEN provider = 'deepseek' OR model_name LIKE '%deepseek%' THEN (COALESCE(prompt_tokens, 0) * 0.14 + COALESCE(completion_tokens, 0) * 0.28) / 1000000.0
            WHEN model_name LIKE '%flash-lite%' THEN (COALESCE(prompt_tokens, 0) * 0.0375 + COALESCE(completion_tokens, 0) * 0.15) / 1000000.0
            ELSE (COALESCE(prompt_tokens, 0) * 0.075 + COALESCE(completion_tokens, 0) * 0.30) / 1000000.0
        END
    )::numeric, 4) AS "Затраты ($)"
FROM llm_usage_logs
WHERE total_tokens > 0
GROUP BY 1, 2
ORDER BY "Дата" ASC;"""
        },
        {
            "id": 72,
            "name": "Светофор здоровья пула API-ключей",
            "display": "table",
            "sql": """SELECT 
    key_alias AS "Ключ",
    provider AS "Провайдер",
    masked_key AS "Маска",
    status AS "Статус",
    last_tested_at AS "Проверен",
    last_error_message AS "Ошибка / Причина"
FROM llm_keys_status
ORDER BY status ASC, key_alias ASC;"""
        }
    ]

    # Create / verify Dashboard for Tokens (Dashboard 8 in Collection 7)
    dash_payload = {
        "name": "Мониторинг лимитов и ключей LLM",
        "description": "Сводный мониторинг затрат токенов по ключам, задачам, пользователям и реестр здоровья пула API",
        "collection_id": 7
    }
    dash_res = api_call(base_url, session_id, "PUT", "/dashboard/8", dash_payload, dry_run)
    dash_id = 8 if dash_res else 9999
    print(f"[OK] Token Economics Dashboard ID: {dash_id}")

    dashcards = []
    card_positions = [
        {"row": 0, "col": 0, "size_x": 24, "size_y": 9},
        {"row": 9, "col": 0, "size_x": 10, "size_y": 8},
        {"row": 9, "col": 10, "size_x": 14, "size_y": 8},
        {"row": 17, "col": 0, "size_x": 12, "size_y": 8},
        {"row": 17, "col": 12, "size_x": 12, "size_y": 8},
    ]
    for idx, card in enumerate(token_cards):
        cid = card.get("id")
        card_payload = {
            "name": card["name"],
            "dataset_query": {
                "type": "native",
                "native": {"query": card["sql"]},
                "database": db_id
            },
            "display": card["display"],
            "collection_id": 7,
            "archived": False,
            "visualization_settings": {}
        }
        print(f"Updating Card {cid}: {card['name']}...")
        api_call(base_url, session_id, "PUT", f"/card/{cid}", card_payload, dry_run)

        pos = card_positions[idx]
        dashcards.append({
            "id": -(idx + 1),
            "card_id": cid,
            "row": pos["row"],
            "col": pos["col"],
            "size_x": pos["size_x"],
            "size_y": pos["size_y"],
            "visualization_settings": {}
        })

    if dashcards and dash_id:
        print(f"Attaching {len(dashcards)} cards to Dashboard {dash_id}...")
        api_call(base_url, session_id, "PUT", f"/dashboard/{dash_id}/cards", {"cards": dashcards}, dry_run)

    print("[SUCCESS] Token analytics cards and dashboard deployed successfully.")

def test_queries(base_url, session_id, dry_run=False):
    """Tests execution of all analytical cards on Dashboards 8 and 4 via Metabase API."""
    print("=== Testing Live Query Execution for Metabase Cards ===")
    cards_to_test = [
        (68, "Сводный расход: Инициатор ➤ Пайплайн ➤ Ключ"),
        (69, "Расход токенов по пайплайнам"),
        (70, "Расход токенов по инициаторам"),
        (71, "Динамика расхода токенов по дням"),
        (72, "Светофор здоровья пула API-ключей"),
        (54, "Сквозная воронка (Продажи)"),
        (49, "Выигранные тендеры - Детали")
    ]
    for cid, name in cards_to_test:
        res = api_call(base_url, session_id, "POST", f"/card/{cid}/query", {}, dry_run)
        if res:
            status = res.get("status")
            rows = len(res.get("data", {}).get("rows", []))
            cols = [c["name"] for c in res.get("data", {}).get("cols", [])]
            print(f"[OK] Card {cid} ('{name}'): status={status}, rows={rows}, cols={cols}")
        else:
            print(f"[ERROR] Card {cid} ('{name}') failed execution.")

def db_stats(base_url, session_id, dry_run=False):
    """Fetches high-level summary statistics from DWH via Metabase native dataset API."""
    print("=== Fetching DWH Analytics High-Level Summary ===")
    db_id = get_database_id(base_url, session_id, "marketing_db", dry_run) or 2
    query_payload = {
        "database": db_id,
        "type": "native",
        "native": {
            "query": "SELECT count(*) as total_logs, COALESCE(sum(total_tokens), 0) as total_tokens, count(distinct request_type) as unique_tasks, count(distinct api_key_mask) as unique_keys FROM llm_usage_logs;"
        }
    }
    res = api_call(base_url, session_id, "POST", "/dataset", query_payload, dry_run)
    if res and "data" in res:
        rows = res["data"].get("rows", [])
        if rows:
            print(f"[OK] DWH LLM Logs: {rows[0][0]:,} total records | {rows[0][1]:,} total tokens | {rows[0][2]} task types | {rows[0][3]} key masks")

def main():
    parser = argparse.ArgumentParser(description="Metabase BI Management and Dashboard Pipeline")
    parser.add_argument("--action", required=True, 
                        choices=["update-cards", "token-analytics", "setup-all", "patch-locale", "create-user", "test-queries", "db-stats"],
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
    elif args.action == "test-queries":
        test_queries(args.url, session_id, args.dry_run)
    elif args.action == "db-stats":
        db_stats(args.url, session_id, args.dry_run)
    elif args.action == "setup-all":
        patch_locale_and_formatting(args.url, session_id, args.dry_run)
        create_manager_user(args.url, session_id, args.manager_email, args.manager_password, args.dry_run)
        update_cards(args.url, session_id, args.dry_run)
        deploy_token_analytics(args.url, session_id, args.dry_run)
        test_queries(args.url, session_id, args.dry_run)
        db_stats(args.url, session_id, args.dry_run)

    print("=== Execution Finished Successfully ===")

if __name__ == "__main__":
    main()
