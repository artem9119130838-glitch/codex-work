#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical Metabase BI Management Pipeline: manage_metabase_dashboards.py
Version: 2.7 (2026-10-22)

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

# Auto-load .env if variables are not yet populated
def load_env_candidates():
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", "..", "1c_odata", ".env"),
        "/Storage/scripts/metabase_analytics/.env"
    ]
    for env_path in candidates:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip()
                            if k not in os.environ and v:
                                os.environ[k] = v
            except Exception:
                pass

load_env_candidates()

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

    # 3. Deploy/Update Card: Тендеры с авансом: взято в обработку
    sql_advance_kpi = """SELECT 
    COUNT(*) AS "Всего тендеров взято",
    COUNT(*) FILTER (WHERE has_advance = TRUE) AS "С авансом (шт)",
    ROUND((COUNT(*) FILTER (WHERE has_advance = TRUE)::NUMERIC / NULLIF(COUNT(*), 0)) * 100, 1) AS "Доля с авансом (%)",
    COALESCE(SUM(tender_amount), 0) AS "Общая НМЦК (руб)",
    COALESCE(SUM(tender_amount) FILTER (WHERE has_advance = TRUE), 0) AS "НМЦК с авансом (руб)"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  AND date_create >= '2026-01-01'
  [[AND {{date_range}}]];"""

    card_adv_kpi_payload = {
        "name": "Тендеры с авансом: взято в обработку",
        "dataset_query": {
            "type": "native",
            "native": {
                "query": sql_advance_kpi,
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
        },
        "display": "table",
        "collection_id": 4,
        "archived": False,
        "visualization_settings": {}
    }

    # 4. Deploy/Update Card: Причины отказов по сделкам с авансом
    sql_advance_losses = """SELECT 
    COALESCE(close_reason, 'Не указано') AS "Причина отказа / Результат",
    COUNT(*) AS "Всего отказов",
    COUNT(*) FILTER (WHERE has_advance = TRUE) AS "Отказов с авансом",
    ROUND((COUNT(*) FILTER (WHERE has_advance = TRUE)::NUMERIC / NULLIF(COUNT(*), 0)) * 100, 1) AS "Доля с авансом (%)",
    ROUND(AVG(advance_percent) FILTER (WHERE has_advance = TRUE), 1) AS "Средний % аванса",
    COALESCE(SUM(tender_amount) FILTER (WHERE has_advance = TRUE), 0) AS "Потерянная НМЦК с авансом (руб)"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  AND is_won = FALSE
  AND close_reason != 'В работе'
  AND date_create >= '2026-01-01'
  [[AND {{date_range}}]]
GROUP BY "Причина отказа / Результат"
ORDER BY "Отказов с авансом" DESC, "Всего отказов" DESC;"""

    card_adv_losses_payload = {
        "name": "Причины отказов по сделкам с авансом",
        "dataset_query": {
            "type": "native",
            "native": {
                "query": sql_advance_losses,
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
        },
        "display": "table",
        "collection_id": 4,
        "archived": False,
        "visualization_settings": {}
    }

    # Helper function to find or create card
    def sync_card(name, payload, collection_id=4):
        cards = api_call(base_url, session_id, "GET", "/card", dry_run=False) or []
        target = next((c for c in cards if c.get("name") == name and not c.get("archived")), None)
        if target:
            cid = target["id"]
            print(f"Updating existing Card {cid}: '{name}'...")
            api_call(base_url, session_id, "PUT", f"/card/{cid}", payload, dry_run)
            return cid
        else:
            print(f"Creating new Card: '{name}'...")
            res = api_call(base_url, session_id, "POST", "/card", payload, dry_run)
            return res.get("id") if res else None

    cid_kpi = sync_card("Тендеры с авансом: взято в обработку", card_adv_kpi_payload)
    cid_losses = sync_card("Причины отказов по сделкам с авансом", card_adv_losses_payload)

    # 5. Deploy/Update Card: Движение тендеров: В работе / Стадии отказов / Победы
    sql_tender_flow = """WITH deal_flow AS (
    SELECT 
        deal_id,
        title,
        date_create,
        date_close,
        COALESCE(tender_amount, our_offer_amount, 0) as amount,
        has_advance,
        advance_percent,
        CASE 
            WHEN is_won = TRUE THEN '3. Победа (Контракт)'
            WHEN is_won = FALSE AND (close_reason != 'В работе' OR raw_data->>'CLOSED' = 'Y') THEN '2. Отказ'
            ELSE '1. В работе'
        END AS status_category,
        stage_id AS current_stage,
        COALESCE(close_reason, 'В работе') AS reason_or_status
    FROM analytics_closed_deals
    WHERE pipeline_name = 'Тендеры'
      [[AND {{date_range}}]]
)
SELECT 
    status_category AS "Статус",
    current_stage AS "Стадия воронки",
    reason_or_status AS "Причина отказа / Статус",
    COUNT(*) AS "Количество сделок",
    SUM(amount) AS "Сумма НМЦК (руб)",
    COUNT(*) FILTER (WHERE has_advance = TRUE) AS "С авансом (шт)",
    ROUND(AVG(advance_percent) FILTER (WHERE has_advance = TRUE), 1) AS "Средний аванс (%)"
FROM deal_flow
GROUP BY status_category, current_stage, reason_or_status
ORDER BY 
    status_category ASC, 
    COUNT(*) DESC, 
    SUM(amount) DESC;"""

    card_flow_payload = {
        "name": "Движение тендеров: В работе / Стадии отказов / Победы",
        "dataset_query": {
            "type": "native",
            "native": {
                "query": sql_tender_flow,
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
        },
        "display": "table",
        "collection_id": 4,
        "archived": False,
        "visualization_settings": {}
    }
    cid_flow = sync_card("Движение тендеров: В работе / Стадии отказов / Победы", card_flow_payload)

    # Attach to Dashboard 4
    if cid_kpi and cid_losses and not dry_run:
        dash4 = api_call(base_url, session_id, "GET", "/dashboard/4", dry_run=False)
        if dash4:
            dashcards = dash4.get("dashcards", []) or dash4.get("ordered_cards", [])
            attached_ids = {dc.get("card_id") for dc in dashcards if dc.get("card_id")}
            max_row = max([dc.get("row", 0) + dc.get("size_y", 6) for dc in dashcards] or [0])
            
            new_cards = []
            for idx, cid in enumerate([cid_kpi, cid_losses, cid_flow]):
                if cid not in attached_ids:
                    new_cards.append({
                        "id": -(idx + 50),
                        "card_id": cid,
                        "row": max_row + (idx * 8),
                        "col": 0,
                        "size_x": 24,
                        "size_y": 8,
                        "visualization_settings": {}
                    })
            if new_cards:
                print(f"Attaching {len(new_cards)} advance analytics cards to Dashboard 4...")
                all_dashcards = dashcards + new_cards
                api_call(base_url, session_id, "PUT", "/dashboard/4/cards", {"cards": all_dashcards}, dry_run)

    print("[SUCCESS] All sales and advance analytics cards processed.")


def deploy_tender_ops_dashboard(base_url, session_id, dry_run=False):
    """
    Deploys the dedicated operational dashboard:
    'Оперативная аналитика: Активность тендерного отдела и движение сделок'
    with interactive date range, employee filter, deal id search, and clickable links to Bitrix24.
    """
    print("=== Deploying Dedicated Tender Operations & Movement Dashboard ===")
    db_id = get_database_id(base_url, session_id, "marketing_db", dry_run) or 2
    
    date_create_id = get_field_id(base_url, session_id, db_id, "analytics_closed_deals", "date_create", dry_run, 76)
    responsible_name_id = get_field_id(base_url, session_id, db_id, "analytics_closed_deals", "responsible_name", dry_run, 80)
    deal_id_field_id = get_field_id(base_url, session_id, db_id, "analytics_closed_deals", "deal_id", dry_run, 73)
    
    print(f"[OK] Resolved Field IDs: date_create={date_create_id}, responsible_name={responsible_name_id}, deal_id={deal_id_field_id}")

    tag_date_range = {
        "id": "tag_date_range",
        "name": "date_range",
        "display-name": "Период дат",
        "type": "dimension",
        "dimension": ["field", date_create_id, None],
        "widget-type": "date/all-options"
    }
    tag_responsible = {
        "id": "tag_responsible",
        "name": "responsible",
        "display-name": "Сотрудник",
        "type": "dimension",
        "dimension": ["field", responsible_name_id, None],
        "widget-type": "string/="
    }
    tag_deal_id = {
        "id": "tag_deal_id",
        "name": "deal_id",
        "display-name": "ID сделки",
        "type": "dimension",
        "dimension": ["field", deal_id_field_id, None],
        "widget-type": "string/="
    }

    sql_kpi = """SELECT 
    COUNT(*) AS "Всего скачано (шт)",
    COALESCE(SUM(COALESCE(tender_amount, our_offer_amount, 0)), 0) AS "Объем НМЦК (руб)",
    COUNT(*) FILTER (WHERE stage_id != 'Не взяли в работу' OR is_won = TRUE OR (close_reason != 'Не взяли в работу' AND close_reason != 'В работе')) AS "Рассмотрено (шт)",
    COUNT(*) FILTER (WHERE (close_reason = 'В работе' OR raw_data->>'CLOSED' = 'N') AND stage_id NOT IN ('Не взяли в работу')) AS "Взято в работу (шт)",
    COALESCE(SUM(tender_amount) FILTER (WHERE (close_reason = 'В работе' OR raw_data->>'CLOSED' = 'N') AND stage_id NOT IN ('Не взяли в работу')), 0) AS "НМЦК в работе (руб)",
    COUNT(*) FILTER (WHERE is_won = FALSE AND (close_reason = 'Не взяли в работу' OR stage_id = 'Не взяли в работу')) AS "Отсеяно на входе (шт)",
    COUNT(*) FILTER (WHERE is_won = FALSE AND close_reason != 'В работе' AND close_reason != 'Не взяли в работу' AND stage_id != 'Не взяли в работу') AS "Отсеяно в процессе (шт)",
    COUNT(*) FILTER (WHERE is_won = TRUE) AS "Победы (шт)",
    COUNT(*) FILTER (WHERE has_advance = TRUE) AS "С авансом (шт)"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  [[AND {{date_range}}]]
  [[AND {{responsible}}]];"""

    sql_losses = """SELECT 
    CASE 
        WHEN stage_id = 'Не взяли в работу' THEN '1. Отсеяно на входе (Скоринг)'
        WHEN stage_id = 'Не смогли отработать' THEN '2. Отсеяно при проработке (Снабжение)'
        WHEN stage_id = 'Проигрыш' THEN '3. Проигрыш на торгах (ЭТП)'
        ELSE '4. Прочее закрытие'
    END AS "Этап отсева",
    COALESCE(close_reason, 'Не указана') AS "Причина отсева",
    COUNT(*) AS "Количество сделок",
    COALESCE(SUM(tender_amount), 0) AS "Сумма НМЦК (руб)",
    COUNT(*) FILTER (WHERE has_advance = TRUE) AS "С авансом (шт)",
    ROUND(AVG(advance_percent) FILTER (WHERE has_advance = TRUE), 1) AS "Средний аванс (%)"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  AND is_won = FALSE 
  AND (close_reason != 'В работе' OR raw_data->>'CLOSED' = 'Y')
  [[AND {{date_range}}]]
  [[AND {{responsible}}]]
GROUP BY 1, 2
ORDER BY 1 ASC, COUNT(*) DESC;"""

    sql_active = """SELECT 
    stage_id AS "Текущая стадия",
    responsible_name AS "Ответственный",
    COUNT(*) AS "В работе (шт)",
    COALESCE(SUM(tender_amount), 0) AS "Сумма НМЦК (руб)",
    COUNT(*) FILTER (WHERE has_advance = TRUE) AS "С авансом (шт)"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  AND (close_reason = 'В работе' OR raw_data->>'CLOSED' = 'N')
  AND is_won = FALSE
  AND stage_id NOT IN ('Не взяли в работу')
  [[AND {{date_range}}]]
  [[AND {{responsible}}]]
GROUP BY stage_id, responsible_name
ORDER BY COUNT(*) DESC, SUM(tender_amount) DESC;"""

    sql_register = """SELECT 
    deal_id AS "ID сделки",
    'https://b24-g4wfjq.bitrix24.ru/crm/deal/details/' || deal_id || '/' AS "Ссылка в CRM",
    date_create::date AS "Дата скачивания",
    title AS "Наименование закупки",
    tender_number AS "Номер закупки",
    responsible_name AS "Ответственный",
    CASE 
        WHEN is_won = TRUE THEN 'Победа'
        WHEN is_won = FALSE AND (close_reason != 'В работе' OR raw_data->>'CLOSED' = 'Y') THEN 'Отказ'
        ELSE 'В работе'
    END AS "Статус",
    stage_id AS "Текущая стадия",
    COALESCE(close_reason, 'В работе') AS "Причина отказа / Результат",
    COALESCE(tender_amount, our_offer_amount, 0) AS "НМЦК (руб)",
    CASE WHEN has_advance = TRUE THEN 'Да (' || advance_percent || '%)' ELSE 'Нет' END AS "Аванс",
    date_close::date AS "Дата закрытия"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  [[AND {{date_range}}]]
  [[AND {{responsible}}]]
  [[AND {{deal_id}}]]
ORDER BY date_create DESC, deal_id DESC;"""

    sql_history = """SELECT 
    h.deal_id AS "ID сделки",
    'https://b24-g4wfjq.bitrix24.ru/crm/deal/details/' || h.deal_id || '/' AS "Ссылка в CRM",
    d.title AS "Наименование закупки",
    d.responsible_name AS "Ответственный",
    CASE h.stage_id
        WHEN 'C4:NEW' THEN '1. Новый тендер / Скоринг'
        WHEN 'C4:PREPARATION' THEN '2. Расчет КП'
        WHEN 'C4:UC_8F7MST' THEN '3. Поиск товара, анализ ВЭД'
        WHEN 'C4:UC_X1NI23' THEN '4. Подготовка документов'
        WHEN 'C4:PREPAYMENT_INVOICE' THEN '5. Согласование КП'
        WHEN 'C4:EXECUTING' THEN '6. Заявка подана / Ожидание'
        WHEN 'C4:FINAL_INVOICE' THEN '7. Торги на ЭТП'
        WHEN 'C4:WON' THEN '★ Победа / Заключение договора'
        WHEN 'C4:LOSE' THEN '✗ Проигрыш'
        WHEN 'C4:APOLOGY' THEN '✗ Не смогли отработать'
        WHEN 'C4:UC_VSDEUH' THEN '✗ Закупки отменены заказчиком'
        WHEN 'C4:UC_5Y3KYZ' THEN '✗ Не взяли в работу'
        ELSE h.stage_id
    END AS "Стадия воронки",
    h.date_entered AS "Дата перехода на этап"
FROM analytics_deal_stage_history h
JOIN analytics_closed_deals d ON d.deal_id = h.deal_id
WHERE d.pipeline_name = 'Тендеры'
  [[AND {{deal_id}}]]
  [[AND {{date_range}}]]
  [[AND {{responsible}}]]
ORDER BY h.date_entered DESC, h.deal_id DESC;"""

    link_settings = {
        "column_settings": {
            '["name", "Ссылка в CRM"]': {
                "link_url": "https://b24-g4wfjq.bitrix24.ru/crm/deal/details/{{ID сделки}}/",
                "link_text": "Открыть в CRM ↗",
                "view_as": "link"
            }
        }
    }

    cards_def = [
        {
            "name": "Оперативная воронка: Скачано ➤ Рассмотрено ➤ В работе ➤ Отсеяно",
            "sql": sql_kpi,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible},
            "vis": {},
            "pos": {"row": 0, "col": 0, "size_x": 24, "size_y": 5}
        },
        {
            "name": "Отсеяно: Причины отказа по этапам воронки",
            "sql": sql_losses,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible},
            "vis": {},
            "pos": {"row": 5, "col": 0, "size_x": 24, "size_y": 8}
        },
        {
            "name": "В работе: Распределение по этапам проработки",
            "sql": sql_active,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible},
            "vis": {},
            "pos": {"row": 13, "col": 0, "size_x": 24, "size_y": 6}
        },
        {
            "name": "Реестр сделок: Движение и прямой переход в CRM",
            "sql": sql_register,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible, "deal_id": tag_deal_id},
            "vis": link_settings,
            "pos": {"row": 19, "col": 0, "size_x": 24, "size_y": 12}
        },
        {
            "name": "Хронология движения: История этапов сделки",
            "sql": sql_history,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible, "deal_id": tag_deal_id},
            "vis": link_settings,
            "pos": {"row": 31, "col": 0, "size_x": 24, "size_y": 10}
        }
    ]

    def sync_card(name, payload):
        cards = api_call(base_url, session_id, "GET", "/card", dry_run=False) or []
        target = next((c for c in cards if c.get("name") == name and not c.get("archived")), None)
        if target:
            cid = target["id"]
            print(f"Updating existing Card {cid}: '{name}'...")
            api_call(base_url, session_id, "PUT", f"/card/{cid}", payload, dry_run)
            return cid
        else:
            print(f"Creating new Card: '{name}'...")
            res = api_call(base_url, session_id, "POST", "/card", payload, dry_run)
            return res.get("id") if res else None

    deployed_cards = []
    for cdef in cards_def:
        card_payload = {
            "name": cdef["name"],
            "dataset_query": {
                "type": "native",
                "native": {
                    "query": cdef["sql"],
                    "template-tags": cdef["tags"]
                },
                "database": db_id
            },
            "display": cdef["display"],
            "collection_id": 5,
            "archived": False,
            "visualization_settings": cdef["vis"]
        }
        cid = sync_card(cdef["name"], card_payload)
        cdef["cid"] = cid
        deployed_cards.append(cdef)

    dashboards = api_call(base_url, session_id, "GET", "/dashboard", dry_run=False) or []
    dash_name = "Оперативная аналитика: Активность тендерного отдела и движение сделок"
    target_dash = next((d for d in dashboards if d.get("name") == dash_name and not d.get("archived")), None)

    dash_params = [
        {
            "id": "param_period",
            "name": "Период дат (скачивание)",
            "slug": "period",
            "type": "date/all-options",
            "sectionId": "date"
        },
        {
            "id": "param_responsible",
            "name": "Сотрудник",
            "slug": "responsible",
            "type": "string/=",
            "sectionId": "string"
        },
        {
            "id": "param_deal_id",
            "name": "ID сделки",
            "slug": "deal_id",
            "type": "string/=",
            "sectionId": "string"
        }
    ]

    dash_payload = {
        "name": dash_name,
        "description": "Оперативный онлайн-мониторинг работы тендерных специалистов: скачивание, скоринг, воронка отсева и реестр сделок с прямым переходом в CRM",
        "parameters": dash_params
    }

    if target_dash:
        dash_id = target_dash["id"]
        print(f"[OK] Updating existing Dashboard {dash_id}: '{dash_name}'...")
        api_call(base_url, session_id, "PUT", f"/dashboard/{dash_id}", dash_payload, dry_run)
    else:
        print(f"Creating new Dashboard: '{dash_name}' in Collection 5...")
        dash_payload["collection_id"] = 5
        res = api_call(base_url, session_id, "POST", "/dashboard", dash_payload, dry_run)
        dash_id = res.get("id") if res else None

    print(f"[OK] Dashboard ID: {dash_id}")

    dashcards_payload = []
    for idx, cdef in enumerate(deployed_cards):
        cid = cdef["cid"]
        pos = cdef["pos"]
        tags = cdef["tags"]
        
        mappings = [
            {
                "parameter_id": "param_period",
                "card_id": cid,
                "target": ["dimension", ["template-tag", "date_range"]]
            },
            {
                "parameter_id": "param_responsible",
                "card_id": cid,
                "target": ["dimension", ["template-tag", "responsible"]]
            }
        ]
        if "deal_id" in tags:
            mappings.append({
                "parameter_id": "param_deal_id",
                "card_id": cid,
                "target": ["dimension", ["template-tag", "deal_id"]]
            })
            
        dashcards_payload.append({
            "id": -(idx + 100),
            "card_id": cid,
            "row": pos["row"],
            "col": pos["col"],
            "size_x": pos["size_x"],
            "size_y": pos["size_y"],
            "parameter_mappings": mappings,
            "visualization_settings": cdef.get("vis", {})
        })

    api_call(base_url, session_id, "PUT", f"/dashboard/{dash_id}/cards", {"cards": dashcards_payload}, dry_run)
    print(f"[SUCCESS] Dashboard {dash_id} deployed with {len(dashcards_payload)} cards and interactive filters.")
    print(f"URL: {base_url}/dashboard/{dash_id}")


def get_or_create_collection(base_url, session_id, name, color="#509EE3", dry_run=False):
    if dry_run:
        return 8
    cols = api_call(base_url, session_id, "GET", "/collection", dry_run=False) or []
    target = next((c for c in cols if c.get("name") == name and not c.get("archived")), None)
    if target:
        return target["id"]
    payload = {"name": name, "color": color}
    res = api_call(base_url, session_id, "POST", "/collection", payload, dry_run=False)
    return res.get("id") if res else 5


def deploy_weekly_sync_dashboard(base_url, session_id, dry_run=False):
    """
    Deploys the Master Executive Sync Dashboard:
    'Еженедельный синк директоров: Тендеры ↔ Снабжение КНР'
    for weekly meetings between Alexandra Ponomareva and Azat Denishov.
    Features:
    - SLA Health & Weekly Velocity Traffic Light
    - Hot Tenders in next 72 Hours (Pulse)
    - Stuck Limbo Detector (Deadline expired without CRM closure)
    - Root-cause Analysis of Weekly Losses
    - Chinese Supply Specialists Performance & Delay Ranking (Group 14)
    - Won Contracts Economics (4 Financial Fields per Metabase Policy)
    - Interactive Filters: Date Range, Tender Specialist, Supply Assignee
    - Direct Clickable Links to Bitrix24 Deals
    """
    print("=== Deploying Executive Master Sync Dashboard (Tenders ↔ Supply) ===")
    db_id = get_database_id(base_url, session_id, "marketing_db", dry_run) or 2
    collection_id = get_or_create_collection(base_url, session_id, "Тендеры и Снабжение: Управление и Синхронизация", "#509EE3", dry_run)
    print(f"[OK] Target Collection ID: {collection_id}")

    date_create_id = get_field_id(base_url, session_id, db_id, "analytics_closed_deals", "date_create", dry_run, 76)
    responsible_name_id = get_field_id(base_url, session_id, db_id, "analytics_closed_deals", "responsible_name", dry_run, 80)
    deal_id_field_id = get_field_id(base_url, session_id, db_id, "analytics_closed_deals", "deal_id", dry_run, 73)

    print(f"[OK] Resolved Field IDs: date_create={date_create_id}, responsible_name={responsible_name_id}, deal_id={deal_id_field_id}")

    tag_date_range = {
        "id": "tag_date_range",
        "name": "date_range",
        "display-name": "Период дат",
        "type": "dimension",
        "dimension": ["field", date_create_id, None],
        "widget-type": "date/all-options"
    }
    tag_responsible = {
        "id": "tag_responsible",
        "name": "responsible",
        "display-name": "Тендерный специалист",
        "type": "dimension",
        "dimension": ["field", responsible_name_id, None],
        "widget-type": "string/="
    }
    tag_supply = {
        "id": "tag_supply",
        "name": "supply_responsible",
        "display-name": "Закупщик КНР",
        "type": "text"
    }

    sql_kpi_sync = """SELECT 
    COUNT(*) AS "Всего в пайплайне (шт)",
    COALESCE(SUM(COALESCE(tender_amount, our_offer_amount, 0)), 0) AS "Объем НМЦК (руб)",
    COUNT(*) FILTER (WHERE (raw_data->>'CLOSED' != 'Y' OR raw_data->>'CLOSED' IS NULL) AND (close_reason = 'В работе' OR close_reason IS NULL) AND stage_id NOT IN ('Не взяли в работу')) AS "В активной работе (шт)",
    COALESCE(SUM(tender_amount) FILTER (WHERE (raw_data->>'CLOSED' != 'Y' OR raw_data->>'CLOSED' IS NULL) AND (close_reason = 'В работе' OR close_reason IS NULL) AND stage_id NOT IN ('Не взяли в работу')), 0) AS "НМЦК в работе (руб)",
    COUNT(*) FILTER (WHERE is_won = TRUE) AS "Победы (шт)",
    COALESCE(SUM(our_offer_amount) FILTER (WHERE is_won = TRUE), 0) AS "Выиграно контрактов (руб)",
    COUNT(*) FILTER (WHERE is_won = FALSE AND (close_reason != 'В работе' OR raw_data->>'CLOSED' = 'Y')) AS "Отказы (шт)",
    COUNT(*) FILTER (WHERE has_advance = TRUE) AS "С авансом (шт)",
    COUNT(*) FILTER (WHERE (raw_data->>'CLOSEDATE')::timestamp < NOW() AND (raw_data->>'CLOSED' != 'Y' OR raw_data->>'CLOSED' IS NULL) AND is_won = FALSE AND stage_id NOT IN ('Не взяли в работу')) AS "Зависшие (STUCK_LIMBO)"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  [[AND {{date_range}}]]
  [[AND {{responsible}}]]
  [[AND (supply_responsible_name ILIKE '%' || {{supply_responsible}} || '%')]];"""

    sql_hot_72h = """SELECT 
    deal_id AS "ID сделки",
    'https://b24-g4wfjq.bitrix24.ru/crm/deal/details/' || deal_id || '/' AS "Ссылка в CRM",
    (raw_data->>'CLOSEDATE')::date AS "Дедлайн на ЭТП",
    ROUND(EXTRACT(EPOCH FROM ((raw_data->>'CLOSEDATE')::timestamp - NOW())) / 3600.0, 1) AS "Осталось часов",
    title AS "Наименование закупки",
    tender_number AS "Номер закупки",
    responsible_name AS "Тендерный специалист",
    COALESCE(supply_responsible_name, 'Не назначен в CRM') AS "Закупщик КНР",
    stage_id AS "Текущий этап",
    COALESCE(tender_amount, our_offer_amount, 0) AS "НМЦК (руб)",
    CASE WHEN has_advance = TRUE THEN 'Да (' || advance_percent || '%)' ELSE 'Нет' END AS "Аванс"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  AND (raw_data->>'CLOSED' != 'Y' OR raw_data->>'CLOSED' IS NULL)
  AND (close_reason = 'В работе' OR close_reason IS NULL)
  AND stage_id NOT IN ('Не взяли в работу')
  AND (raw_data->>'CLOSEDATE')::timestamp >= NOW() - INTERVAL '1 day'
  AND (raw_data->>'CLOSEDATE')::timestamp <= NOW() + INTERVAL '4 days'
  [[AND {{date_range}}]]
  [[AND {{responsible}}]]
  [[AND (supply_responsible_name ILIKE '%' || {{supply_responsible}} || '%')]]
ORDER BY (raw_data->>'CLOSEDATE')::timestamp ASC;"""

    sql_stuck_limbo = """SELECT 
    deal_id AS "ID сделки",
    'https://b24-g4wfjq.bitrix24.ru/crm/deal/details/' || deal_id || '/' AS "Ссылка в CRM",
    (raw_data->>'CLOSEDATE')::date AS "Просроченный дедлайн",
    ROUND(EXTRACT(EPOCH FROM (NOW() - (raw_data->>'CLOSEDATE')::timestamp)) / 86400.0, 1) AS "Дней просрочки",
    title AS "Наименование закупки",
    responsible_name AS "Тендерный специалист",
    COALESCE(supply_responsible_name, 'Не назначен в CRM') AS "Закупщик КНР",
    stage_id AS "Зависшая стадия",
    CASE 
        WHEN stage_id IN ('Поиск товара, анализ ВЭД', 'C4:UC_8F7MST', 'C4:PREPARATION', 'Расчет КП') THEN '🔴 Срыв снабжения (нет расчета КП)'
        WHEN stage_id IN ('Подготовка документов', 'C4:UC_X1NI23', 'Загрузить на ЭТП', 'C4:UC_5Y3KYZ') THEN '🔴 Срыв тендеров (не подали на ЭТП)'
        ELSE '⚠️ Требует разбора'
    END AS "Первичная атрибуция вины",
    COALESCE(tender_amount, 0) AS "НМЦК (руб)"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  AND (raw_data->>'CLOSED' != 'Y' OR raw_data->>'CLOSED' IS NULL)
  AND (close_reason = 'В работе' OR close_reason IS NULL)
  AND stage_id NOT IN ('Не взяли в работу')
  AND (raw_data->>'CLOSEDATE')::timestamp < NOW()
  [[AND {{date_range}}]]
  [[AND {{responsible}}]]
  [[AND (supply_responsible_name ILIKE '%' || {{supply_responsible}} || '%')]]
ORDER BY (raw_data->>'CLOSEDATE')::timestamp DESC;"""

    sql_losses = """SELECT 
    CASE 
        WHEN stage_id = 'Не взяли в работу' THEN '1. Отсеяно на входе (Скоринг)'
        WHEN stage_id IN ('Не смогли отработать', 'C4:APOLOGY') THEN '2. Отсеяно при подборе (Снабжение КНР)'
        WHEN stage_id IN ('Проигрыш', 'C4:LOSE') THEN '3. Проигрыш на торгах (ЭТП)'
        ELSE '4. Прочее закрытие'
    END AS "Группа отсева",
    COALESCE(close_reason, 'Не указана') AS "Причина отказа (Код CRM)",
    COUNT(*) AS "Количество сделок",
    COALESCE(SUM(tender_amount), 0) AS "Сумма потерь НМЦК (руб)",
    COUNT(*) FILTER (WHERE has_advance = TRUE) AS "С авансом (шт)",
    ROUND(AVG(advance_percent) FILTER (WHERE has_advance = TRUE), 1) AS "Средний аванс (%)"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  AND is_won = FALSE
  AND (close_reason != 'В работе' OR raw_data->>'CLOSED' = 'Y')
  [[AND {{date_range}}]]
  [[AND {{responsible}}]]
  [[AND (supply_responsible_name ILIKE '%' || {{supply_responsible}} || '%')]]
GROUP BY 1, 2
ORDER BY 1 ASC, COUNT(*) DESC;"""

    sql_supply_ranking = """SELECT 
    COALESCE(supply_responsible_name, 'Не назначен в CRM') AS "Специалист снабжения",
    COUNT(*) AS "Всего процедур в работе",
    COALESCE(SUM(tender_amount), 0) AS "Общая сумма НМЦК (руб)",
    COUNT(*) FILTER (WHERE stage_id IN ('Поиск товара, анализ ВЭД', 'Расчет КП', 'C4:UC_8F7MST', 'C4:PREPARATION')) AS "Сейчас на подборе (шт)",
    COUNT(*) FILTER (WHERE is_won = TRUE) AS "Победы (шт)",
    COUNT(*) FILTER (WHERE is_won = FALSE AND close_reason IN ('Не получили коммерческое предложение', 'Получили коммерческое предложение слишком поздно', 'Не успели подготовить заявку')) AS "Срывы по срокам (код 316/318/322)",
    COUNT(*) FILTER (WHERE is_won = FALSE AND close_reason IN ('Не нашли поставщика', 'Коммерческое предложение не соответствует требованиям')) AS "Не подобрали фабрику (код 314/320)",
    COUNT(*) FILTER (WHERE (raw_data->>'CLOSEDATE')::timestamp < NOW() AND (raw_data->>'CLOSED' != 'Y' OR raw_data->>'CLOSED' IS NULL)) AS "Зависло в просрочке (Limbo)"
FROM analytics_closed_deals
WHERE pipeline_name = 'Тендеры'
  [[AND {{date_range}}]]
  [[AND {{responsible}}]]
  [[AND (supply_responsible_name ILIKE '%' || {{supply_responsible}} || '%')]]
GROUP BY 1
ORDER BY COUNT(*) DESC;"""

    sql_won_deals = """SELECT 
    deal_id AS "ID сделки",
    'https://b24-g4wfjq.bitrix24.ru/crm/deal/details/' || deal_id || '/' AS "Ссылка в CRM",
    date_close::date AS "Дата победы",
    title AS "Наименование контракта",
    tender_number AS "Номер закупки",
    responsible_name AS "Тендерный менеджер",
    COALESCE(supply_responsible_name, 'Не назначен в CRM') AS "Закупщик КНР",
    COALESCE(tender_amount, 0) AS "НМЦК (руб)",
    COALESCE(our_offer_amount, 0) AS "Сумма контракта (руб)",
    (COALESCE(tender_amount, 0) - COALESCE(our_offer_amount, 0)) AS "Разница (руб)",
    ROUND(((COALESCE(tender_amount, 0) - COALESCE(our_offer_amount, 0)) / NULLIF(COALESCE(tender_amount, 0), 0)) * 100, 2) AS "Снижение (%)",
    CASE WHEN has_advance = TRUE THEN 'Да (' || advance_percent || '%)' ELSE 'Нет' END AS "Аванс"
FROM analytics_closed_deals
WHERE (pipeline_name = 'Тендеры' OR pipeline_name = 'Заказчики')
  AND is_won = TRUE
  [[AND {{date_range}}]]
  [[AND {{responsible}}]]
  [[AND (supply_responsible_name ILIKE '%' || {{supply_responsible}} || '%')]]
ORDER BY date_close DESC, deal_id DESC;"""

    link_settings = {
        "column_settings": {
            '["name", "Ссылка в CRM"]': {
                "link_url": "https://b24-g4wfjq.bitrix24.ru/crm/deal/details/{{ID сделки}}/",
                "link_text": "Открыть в CRM ↗",
                "view_as": "link"
            }
        }
    }

    cards_def = [
        {
            "name": "1. Светофор недели: Пульс пайплайна и дисциплина SLA",
            "sql": sql_kpi_sync,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible, "supply_responsible": tag_supply},
            "vis": {},
            "pos": {"row": 0, "col": 0, "size_x": 24, "size_y": 4}
        },
        {
            "name": "2. Горящие торги на ближайшие 72 часа (Пульс недели)",
            "sql": sql_hot_72h,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible, "supply_responsible": tag_supply},
            "vis": link_settings,
            "pos": {"row": 4, "col": 0, "size_x": 12, "size_y": 8}
        },
        {
            "name": "3. Детектор зависших сделок (STUCK_LIMBO — просрочки без результата)",
            "sql": sql_stuck_limbo,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible, "supply_responsible": tag_supply},
            "vis": link_settings,
            "pos": {"row": 4, "col": 12, "size_x": 12, "size_y": 8}
        },
        {
            "name": "4. Анализ причин отказов и срывов недели (Root Cause)",
            "sql": sql_losses,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible, "supply_responsible": tag_supply},
            "vis": {},
            "pos": {"row": 12, "col": 0, "size_x": 12, "size_y": 8}
        },
        {
            "name": "4b. Эффективность закупщиков КНР (Антирейтинг задержек снабжения)",
            "sql": sql_supply_ranking,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible, "supply_responsible": tag_supply},
            "vis": {},
            "pos": {"row": 12, "col": 12, "size_x": 12, "size_y": 8}
        },
        {
            "name": "5. Победы недели и экономика контрактов (4 финансовых поля)",
            "sql": sql_won_deals,
            "display": "table",
            "tags": {"date_range": tag_date_range, "responsible": tag_responsible, "supply_responsible": tag_supply},
            "vis": link_settings,
            "pos": {"row": 20, "col": 0, "size_x": 24, "size_y": 8}
        }
    ]

    def sync_card(name, payload):
        cards = api_call(base_url, session_id, "GET", "/card", dry_run=False) or []
        target = next((c for c in cards if c.get("name") == name and not c.get("archived")), None)
        if target:
            cid = target["id"]
            print(f"Updating existing Card {cid}: '{name}'...")
            api_call(base_url, session_id, "PUT", f"/card/{cid}", payload, dry_run)
            return cid
        else:
            print(f"Creating new Card: '{name}'...")
            res = api_call(base_url, session_id, "POST", "/card", payload, dry_run)
            return res.get("id") if res else None

    deployed_cards = []
    for cdef in cards_def:
        card_payload = {
            "name": cdef["name"],
            "dataset_query": {
                "type": "native",
                "native": {
                    "query": cdef["sql"],
                    "template-tags": cdef["tags"]
                },
                "database": db_id
            },
            "display": cdef["display"],
            "collection_id": collection_id,
            "archived": False,
            "visualization_settings": cdef["vis"]
        }
        cid = sync_card(cdef["name"], card_payload)
        cdef["cid"] = cid
        deployed_cards.append(cdef)

    dashboards = api_call(base_url, session_id, "GET", "/dashboard", dry_run=False) or []
    dash_name = "Еженедельный синк директоров: Тендеры ↔ Снабжение КНР"
    target_dash = next((d for d in dashboards if d.get("name") == dash_name and not d.get("archived")), None)

    dash_params = [
        {
            "id": "param_period",
            "name": "Период дат",
            "slug": "period",
            "type": "date/all-options",
            "sectionId": "date"
        },
        {
            "id": "param_responsible",
            "name": "Тендерный специалист",
            "slug": "responsible",
            "type": "string/=",
            "sectionId": "string"
        },
        {
            "id": "param_supply",
            "name": "Закупщик КНР",
            "slug": "supply_responsible",
            "type": "string/=",
            "sectionId": "string"
        }
    ]

    dash_payload = {
        "name": dash_name,
        "description": "Минимально необходимый дашборд для 25-минутных совместных планерок директоров Тендерного отдела и Снабжения КНР (Александра Пономарева & Азат Денишов). Включает светофор SLA, горящие дедлайны на 72ч, детектор Limbo, антирейтинг задержек закупщиков и выигранные контракты.",
        "parameters": dash_params
    }

    if target_dash:
        dash_id = target_dash["id"]
        print(f"[OK] Updating existing Dashboard {dash_id}: '{dash_name}'...")
        api_call(base_url, session_id, "PUT", f"/dashboard/{dash_id}", dash_payload, dry_run)
    else:
        print(f"Creating new Dashboard: '{dash_name}' in Collection {collection_id}...")
        dash_payload["collection_id"] = collection_id
        res = api_call(base_url, session_id, "POST", "/dashboard", dash_payload, dry_run)
        dash_id = res.get("id") if res else None

    print(f"[OK] Dashboard ID: {dash_id}")

    dashcards_payload = []
    for idx, cdef in enumerate(deployed_cards):
        cid = cdef["cid"]
        pos = cdef["pos"]
        
        mappings = [
            {
                "parameter_id": "param_period",
                "card_id": cid,
                "target": ["dimension", ["template-tag", "date_range"]]
            },
            {
                "parameter_id": "param_responsible",
                "card_id": cid,
                "target": ["dimension", ["template-tag", "responsible"]]
            },
            {
                "parameter_id": "param_supply",
                "card_id": cid,
                "target": ["variable", ["template-tag", "supply_responsible"]]
            }
        ]
            
        dashcards_payload.append({
            "id": -(idx + 300),
            "card_id": cid,
            "row": pos["row"],
            "col": pos["col"],
            "size_x": pos["size_x"],
            "size_y": pos["size_y"],
            "parameter_mappings": mappings,
            "visualization_settings": cdef.get("vis", {})
        })

    api_call(base_url, session_id, "PUT", f"/dashboard/{dash_id}/cards", {"cards": dashcards_payload}, dry_run)
    print(f"[SUCCESS] Dashboard {dash_id} ('{dash_name}') deployed with {len(dashcards_payload)} cards and filters.")
    print(f"URL: {base_url}/dashboard/{dash_id}")


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
        WHEN project_name = 'seo_longwang' THEN 'Робот SEO Longwang (VPS Cron)'
        ELSE 'Системная автоматизация (VPS)'
    END AS "Инициатор",
    CASE 
        WHEN request_type = 'longwang_trend_radar' THEN 'SEO Радар трендов Longwang'
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
        WHEN request_type = 'longwang_trend_radar' THEN 'SEO Радар трендов Longwang'
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
        WHEN project_name = 'seo_longwang' THEN 'Робот SEO Longwang (VPS Cron)'
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
    # Dynamically find advance cards
    cards = api_call(base_url, session_id, "GET", "/card", dry_run=False) or []
    for c in cards:
        if "аванс" in c.get("name", "").lower() and not c.get("archived"):
            if c["id"] not in [x[0] for x in cards_to_test]:
                cards_to_test.append((c["id"], c["name"]))

    for cid, name in cards_to_test:
        res = api_call(base_url, session_id, "POST", f"/card/{cid}/query", {}, dry_run)
        if res:
            status = res.get("status")
            rows = len(res.get("data", {}).get("rows", []))
            cols = [c["name"] for c in res.get("data", {}).get("cols", [])]
            print(f"[OK] Card {cid} ('{name}'): status={status}, rows={rows}, cols={cols}")
        else:
            print(f"[ERROR] Card {cid} ('{name}') failed execution.")


def inspect_groups(base_url, session_id, dry_run=False):
    """Fetches and displays all user permission groups from Metabase."""
    print("=== Inspecting Metabase Permission Groups ===")
    groups = api_call(base_url, session_id, "GET", "/permissions/group", dry_run=dry_run)
    if groups:
        print(f"Found {len(groups)} permission groups:")
        for g in groups:
            print(f"  * ID: {g.get('id'):<3} | Name: {g.get('name')}")
    else:
        print("[WARNING] Could not retrieve permission groups.")

def grant_collection_permissions(base_url, session_id, collection_ids, group_id=1, dry_run=False):
    """
    Grants 'read' permissions to a specified group (default Group 1: All Users)
    for the provided collection IDs via PUT /api/collection/graph.
    Safely preserves Administrator (Group 2) permissions.
    """
    print(f"=== Configuring Collection Permissions (Group {group_id} -> Collections: {collection_ids}) ===")
    cols = api_call(base_url, session_id, "GET", "/collection", dry_run=dry_run) or []
    all_col_ids = [str(c["id"]) for c in cols if "id" in c]
    
    cg = api_call(base_url, session_id, "GET", "/collection/graph", dry_run=dry_run) or {}
    revision = cg.get("revision", 0)
    current_groups = cg.get("groups", {})
    
    group_str = str(group_id)
    target_group_perms = {"root": "none"}
    for cid in all_col_ids:
        target_group_perms[cid] = "none"
        
    for cid in collection_ids:
        target_group_perms[str(cid)] = "read"
        
    admin_perms = current_groups.get("2", {"root": "write"})
    payload = {
        "revision": revision,
        "groups": {
            group_str: target_group_perms,
            "2": admin_perms
        }
    }
    
    res = api_call(base_url, session_id, "PUT", "/collection/graph", payload, dry_run=dry_run)
    if res or dry_run:
        print(f"[SUCCESS] Permissions updated: Group {group_id} now has 'read' access to collections: {collection_ids}")
    else:
        print(f"[ERROR] Failed to update collection permissions.")

def test_user_access(base_url, email, password, dashboard_id=10):
    """Tests authentication and dashboard accessibility for a specific user."""
    print(f"=== Testing Access for User: {email} ===")
    user_session = get_session(base_url, email, password)
    if not user_session:
        print(f"[FAIL] Could not authenticate user {email}")
        return False
        
    print(f"[OK] Authenticated successfully as {email}. Session token acquired.")
    dash = api_call(base_url, user_session, "GET", f"/dashboard/{dashboard_id}", dry_run=False)
    if not dash:
        print(f"[FAIL] Could not access Dashboard {dashboard_id} as {email}")
        return False
        
    dash_cards = dash.get("dashcards", [])
    print(f"[OK] Successfully accessed Dashboard {dashboard_id} ('{dash.get('name')}'). Contains {len(dash_cards)} cards.")
    
    success_count = 0
    for dc in dash_cards:
        cid = dc.get("card_id")
        if not cid:
            continue
        cname = dc.get("card", {}).get("name", f"Card {cid}")
        q_res = api_call(base_url, user_session, "POST", f"/card/{cid}/query", {}, dry_run=False)
        if q_res and q_res.get("status") == "completed":
            row_count = len(q_res.get("data", {}).get("rows", []))
            print(f"   [OK] Card {cid} ('{cname[:40]}'): OK ({row_count} rows)")
            success_count += 1
        else:
            print(f"   [RESTRICTED] Card {cid} ('{cname[:40]}'): Failed or restricted")
            
    print(f"[SUMMARY] User {email} has functional access to {success_count}/{len(dash_cards)} cards on Dashboard {dashboard_id}.")
    return True

def test_card_query(base_url, session_id, card_id, parameters=None, dry_run=False):
    """Executes a single Metabase card query and prints results summary."""
    print(f"=== Testing Execution of Card {card_id} ===")
    payload = {"parameters": parameters or []}
    res = api_call(base_url, session_id, "POST", f"/card/{card_id}/query", payload, dry_run=dry_run)
    if not res:
        print(f"[ERROR] Failed to execute query for Card {card_id}")
        return
        
    data = res.get("data", {})
    cols = [c.get("name") for c in data.get("cols", [])]
    rows = data.get("rows", [])
    print(f"[OK] Card {card_id} executed successfully. Status: {res.get('status')}")
    print(f"Columns ({len(cols)}): {cols}")
    print(f"Total Rows: {len(rows)}")
    if rows:
        print("\nFirst up to 5 rows:")
        for i, r in enumerate(rows[:5], 1):
            print(f"  Row {i}: {r}")

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


def parse_date_range(period_str):
    """
    Parses period descriptor into (start_date_str, end_date_str).
    Supported: 'month', 'prev-month', 'week', 'today', or 'YYYY-MM-DD..YYYY-MM-DD'
    """
    import datetime
    now = datetime.datetime.now()
    if period_str == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period_str == "prev-month":
        first_this_month = now.replace(day=1)
        prev_month_end = first_this_month - datetime.timedelta(days=1)
        start_date = prev_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = prev_month_end.replace(hour=23, minute=59, second=59)
    elif period_str == "week":
        start_date = (now - datetime.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period_str == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif ".." in period_str:
        parts = period_str.split("..")
        start_date = datetime.datetime.strptime(parts[0].strip(), "%Y-%m-%d")
        end_date = datetime.datetime.strptime(parts[1].strip(), "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    else:
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    return start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S")

def run_dwh_query(base_url, session_id, db_id, sql_query):
    """Executes SQL query via Metabase dataset API or direct psycopg2."""
    if session_id and session_id != "dry-run-token":
        payload = {
            "database": db_id,
            "type": "native",
            "native": {"query": sql_query}
        }
        res = api_call(base_url, session_id, "POST", "/dataset", payload)
        if res and "data" in res:
            cols = [c["name"] for c in res["data"].get("cols", [])]
            rows = res["data"].get("rows", [])
            return cols, rows

    try:
        import psycopg2
        pg_pass = os.environ.get("PG_PASS", "")
        conn = psycopg2.connect(
            host=os.environ.get("PG_HOST", "10.10.0.1"),
            port=int(os.environ.get("PG_PORT", 5433)),
            dbname=os.environ.get("PG_DBNAME", "marketing_db"),
            user=os.environ.get("PG_USER", "vector_user"),
            password=pg_pass
        )
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description] if cur.description else []
        cur.close()
        conn.close()
        return cols, rows
    except Exception as e:
        print(f"[ERROR] Could not query database: {e}")
        return [], []

def fmt_rub(val):
    if not val:
        return "0.00 ₽"
    return f"{val:,.2f}".replace(",", " ") + " ₽"

def tender_report(base_url, session_id, period="month", filter_by="create", dry_run=False):
    print(f"=== Generating Tender Analytics Operational Report (Period: {period}, Filter: {filter_by}) ===")
    db_id = get_database_id(base_url, session_id, "marketing_db", dry_run) or 2
    start_dt, end_dt = parse_date_range(period)
    date_col = "date_close" if filter_by == "close" else "date_create"
    filter_label = "Дата закрытия (результат)" if filter_by == "close" else "Дата создания (поступление)"

    # 1. Summary query
    sql_summary = f"""
    SELECT 
        COUNT(*) as total_deals,
        COALESCE(SUM(tender_amount), 0) as total_amount,
        COUNT(*) FILTER (WHERE is_won = TRUE) as won_count,
        COALESCE(SUM(our_offer_amount) FILTER (WHERE is_won = TRUE), 0) as won_amount,
        COUNT(*) FILTER (WHERE is_won = FALSE AND (close_reason != 'В работе' OR raw_data->>'CLOSED' = 'Y')) as lost_count,
        COALESCE(SUM(tender_amount) FILTER (WHERE is_won = FALSE AND (close_reason != 'В работе' OR raw_data->>'CLOSED' = 'Y')), 0) as lost_amount,
        COUNT(*) FILTER (WHERE (close_reason = 'В работе' OR close_reason IS NULL) AND raw_data->>'CLOSED' != 'Y') as active_count,
        COALESCE(SUM(tender_amount) FILTER (WHERE (close_reason = 'В работе' OR close_reason IS NULL) AND raw_data->>'CLOSED' != 'Y'), 0) as active_amount,
        COUNT(*) FILTER (WHERE has_advance = TRUE) as advance_count,
        ROUND(AVG(advance_percent) FILTER (WHERE has_advance = TRUE), 1) as avg_advance_pct
    FROM analytics_closed_deals
    WHERE pipeline_name = 'Тендеры'
      AND {date_col} >= '{start_dt}' AND {date_col} <= '{end_dt}';
    """
    _, summary_rows = run_dwh_query(base_url, session_id, db_id, sql_summary)

    # 2. Active stages query
    sql_active = f"""
    SELECT 
        stage_id,
        COUNT(*) as count,
        COALESCE(SUM(tender_amount), 0) as amount,
        COUNT(*) FILTER (WHERE has_advance = TRUE) as adv_count
    FROM analytics_closed_deals
    WHERE pipeline_name = 'Тендеры'
      AND {date_col} >= '{start_dt}' AND {date_col} <= '{end_dt}'
      AND (raw_data->>'CLOSED' != 'Y' AND (close_reason = 'В работе' OR close_reason IS NULL))
    GROUP BY stage_id
    ORDER BY count DESC, amount DESC;
    """
    _, active_rows = run_dwh_query(base_url, session_id, db_id, sql_active)

    # 3. Rejections query
    sql_rejections = f"""
    SELECT 
        stage_id,
        COALESCE(close_reason, 'Не указано') as reason,
        COUNT(*) as count,
        COALESCE(SUM(tender_amount), 0) as amount,
        COUNT(*) FILTER (WHERE has_advance = TRUE) as adv_count
    FROM analytics_closed_deals
    WHERE pipeline_name = 'Тендеры'
      AND {date_col} >= '{start_dt}' AND {date_col} <= '{end_dt}'
      AND (raw_data->>'CLOSED' = 'Y' OR (close_reason != 'В работе' AND close_reason IS NOT NULL AND is_won = FALSE))
    GROUP BY stage_id, reason
    ORDER BY stage_id, count DESC;
    """
    _, rej_rows = run_dwh_query(base_url, session_id, db_id, sql_rejections)

    s = summary_rows[0] if summary_rows else [0]*10
    total, total_amt, won, won_amt, lost, lost_amt, active, active_amt, adv, adv_pct = (
        s[0] or 0, float(s[1] or 0), s[2] or 0, float(s[3] or 0),
        s[4] or 0, float(s[5] or 0), s[6] or 0, float(s[7] or 0),
        s[8] or 0, float(s[9] or 0)
    )

    print("\n" + "=" * 80)
    print(f"📊 ОПЕРАТИВНЫЙ ОТЧЕТ ПО ТЕНДЕРНЫМ СДЕЛКАМ")
    print(f"Период: {start_dt[:10]} — {end_dt[:10]} | Фильтр: {filter_label}")
    print("=" * 80)
    print("\n1. СВОДНЫЕ ПОКАЗАТЕЛИ:")
    print(f"   • Всего сделок в выборке:      {total} (НМЦК: {fmt_rub(total_amt)})")
    print(f"   • Сейчас в активной работе:    {active} ({round(active/total*100, 1) if total else 0}%) | НМЦК: {fmt_rub(active_amt)}")
    print(f"   • Завершено отказом:           {lost} ({round(lost/total*100, 1) if total else 0}%) | Потеряно НМЦК: {fmt_rub(lost_amt)}")
    print(f"   • Выиграно (контракт):         {won} ({round(won/total*100, 1) if total else 0}%) | Контракты: {fmt_rub(won_amt)}")
    print(f"   • С предусмотренным авансом:   {adv} ({round(adv/total*100, 1) if total else 0}%) | Средний размер: {adv_pct}%")

    print("\n2. СЕЙЧАС В АКТИВНОЙ РАБОТЕ ПО СТАДИЯМ:")
    if active_rows:
        for r in active_rows:
            stg, cnt, amt, a_cnt = r[0], r[1], float(r[2] or 0), r[3]
            print(f"   • {stg}: {cnt} сделок | НМЦК: {fmt_rub(amt)} (с авансом: {a_cnt})")
    else:
        print("   (нет активных сделок за указанный период)")

    print("\n3. ОТКАЗЫ: НА КАКОЙ СТАДИИ И ПО КАКИМ ПРИЧИНАМ:")
    if rej_rows:
        current_stg = None
        for r in rej_rows:
            stg, reason, cnt, amt, a_cnt = r[0], r[1], r[2], float(r[3] or 0), r[4]
            if stg != current_stg:
                current_stg = stg
                print(f"\n   ▼ Стадия «{stg}»:")
            print(f"     - {reason}: {cnt} сделок | НМЦК: {fmt_rub(amt)} (с авансом: {a_cnt})")
    else:
        print("   (нет отказов за указанный период)")
    print("\n" + "=" * 80 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Metabase BI Management and Dashboard Pipeline")
    parser.add_argument("--action", required=True, 
                        choices=["update-cards", "tender-report", "deploy-tender-ops", "deploy-weekly-sync", "token-analytics", "setup-all", "patch-locale", "create-user", "test-queries", "db-stats", "grant-permissions", "test-access", "test-card", "inspect-groups"],
                        help="Action to perform on Metabase")
    parser.add_argument("--dry-run", action="store_true", help="Simulate API calls without modifying state")
    parser.add_argument("--url", default=DEFAULT_METABASE_URL, help="Metabase instance URL")
    parser.add_argument("--email", default=DEFAULT_ADMIN_EMAIL, help="Metabase admin email")
    parser.add_argument("--password", default=DEFAULT_ADMIN_PASSWORD, help="Metabase admin password")
    parser.add_argument("--manager-email", default="manager@tender-rag.local", help="Manager user email")
    parser.add_argument("--manager-password", default="TenderManager2026!", help="Manager user password")
    parser.add_argument("--period", default="month", help="Reporting period: 'month', 'prev-month', 'week', 'today', or 'YYYY-MM-DD..YYYY-MM-DD'")
    parser.add_argument("--filter-by", default="create", choices=["create", "close"], help="Filter by 'create' (creation date) or 'close' (outcome date)")
    parser.add_argument("--card-id", type=int, default=85, help="Card ID for --action test-card")
    parser.add_argument("--collection-ids", default="4,5,8", help="Comma-separated Collection IDs for --action grant-permissions")
    parser.add_argument("--dashboard-id", type=int, default=10, help="Dashboard ID for --action test-access")

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
    elif args.action == "tender-report":
        tender_report(args.url, session_id, args.period, args.filter_by, args.dry_run)
    elif args.action == "deploy-tender-ops":
        deploy_tender_ops_dashboard(args.url, session_id, args.dry_run)
    elif args.action == "deploy-weekly-sync":
        deploy_weekly_sync_dashboard(args.url, session_id, args.dry_run)
    elif args.action == "inspect-groups":
        inspect_groups(args.url, session_id, args.dry_run)
    elif args.action == "grant-permissions":
        col_list = [int(x.strip()) for x in args.collection_ids.split(",") if x.strip()]
        grant_collection_permissions(args.url, session_id, col_list, group_id=1, dry_run=args.dry_run)
    elif args.action == "test-access":
        test_user_access(args.url, args.manager_email, args.manager_password, dashboard_id=args.dashboard_id)
    elif args.action == "test-card":
        test_card_query(args.url, session_id, args.card_id, dry_run=args.dry_run)
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
