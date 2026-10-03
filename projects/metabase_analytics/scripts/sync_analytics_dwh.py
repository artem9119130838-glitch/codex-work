#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical DWH Sync Pipeline: sync_analytics_dwh.py
Version: 1.0 (2026-10-03)

Synchronizes closed deals and stage transition history from Bitrix24 CRM
into PostgreSQL DWH (marketing_db) for Metabase BI dashboards.

Supports:
- --dry-run mode
- --days N (incremental sync)
- --full (complete historical backfill)
- Zero Secrets Policy: Reads all credentials and webhooks from environment variables.
"""

import os
import sys
import json
import time
import argparse
import datetime
import urllib.request
import urllib.error

B24_URL = os.environ.get("B24_WEBHOOK_URL", "").rstrip("/")
PG_HOST = os.environ.get("PG_HOST", "10.10.0.1")
PG_PORT = int(os.environ.get("PG_PORT", 5433))
PG_DBNAME = os.environ.get("PG_DBNAME", "marketing_db")
PG_USER = os.environ.get("PG_USER", "vector_user")
PG_PASS = os.environ.get("PG_PASS", "")

CLOSE_REASON_MAP = {
    "306": "Национальный режим (запрет)",
    "308": "Требуется товар российского происхождения",
    "310": "Эквивалент не допускается",
    "312": "Закупка нерентабельна",
    "314": "Не нашли поставщика",
    "316": "Не получили коммерческое предложение",
    "318": "Получили коммерческое предложение слишком поздно",
    "320": "Коммерческое предложение не соответствует требованиям",
    "322": "Не успели подготовить заявку",
    "324": "Не успели подать заявку",
    "326": "Проиграли по цене",
    "328": "Заявка отклонена из-за ошибок заполнения",
    "330": "Проиграли по неценовым критериям",
    "332": "Другое",
    "334": "Запрет на экспорт из Китая",
    "336": "Недостаточный срок поставки"
}

STAGE_NAMES = {
    "NEW": "Заявка на расчет",
    "PREPARATION": "Расчет КП",
    "PREPAYMENT_INVOICE": "КП отправлен, требует ОКК",
    "EXECUTING": "Согласование КП",
    "FINAL_INVOICE": "Ожидает оплаты",
    "1": "В работе",
    "WON": "Сделка успешна",
    "LOSE": "Сделка провалена",
    "C4:NEW": "Анализ тендера",
    "C4:UC_8F7MST": "Поиск товара, анализ ВЭД",
    "C4:PREPARATION": "Расчет КП",
    "C4:UC_X1NI23": "Подготовка документов",
    "C4:UC_5Y3KYZ": "Загрузить на ЭТП",
    "C4:PREPAYMENT_INVOICE": "Заявка подана / Ожидание",
    "C4:EXECUTING": "Победа / Заключение договора",
    "C4:FINAL_INVOICE": "Исполнение договора",
    "C4:WON": "Не взяли в работу",
    "C4:LOSE": "Проигрыш",
    "C4:APOLOGY": "Не смогли отработать",
    "C4:UC_VSDEUH": "Закупки отменены заказчиком"
}

WON_STAGES_CAT0 = {"1", "FINAL_INVOICE", "UC_UVHNXE", "UC_Y7FU08", "UC_97AEGE", "2", "UC_8CYR5V", "3", "WON"}
WON_STAGES_CAT4 = {"C4:EXECUTING", "C4:FINAL_INVOICE"}

def b24_call(method, params=None):
    if not B24_URL:
        raise ValueError("B24_WEBHOOK_URL environment variable is not set!")
    url = f"{B24_URL}/{method}.json"
    data = json.dumps(params).encode("utf-8") if params else None
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res.get("result", {})
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except Exception:
            time.sleep(2 * (attempt + 1))
    return {}

def fetch_all_items(method, select_fields=None, filter_params=None):
    items = []
    start = 0
    params = {"order": {"ID": "DESC"}, "start": start}
    if select_fields:
        params["select"] = select_fields
    if filter_params:
        params["filter"] = filter_params

    while True:
        params["start"] = start
        res = b24_call(method, params)
        if isinstance(res, list):
            chunk = res
        elif isinstance(res, dict) and "deals" in res:
            chunk = res["deals"]
        else:
            chunk = res.get("items", []) if isinstance(res, dict) else []

        if not chunk:
            break
        items.extend(chunk)
        if len(chunk) < 50:
            break
        start += len(chunk)
        time.sleep(0.2)
    return items

def main():
    parser = argparse.ArgumentParser(description="Bitrix24 CRM to PostgreSQL DWH Sync Pipeline")
    parser.add_argument("--days", type=int, default=30, help="Days to look back for incremental sync")
    parser.add_argument("--full", action="store_true", help="Perform full historical backfill")
    parser.add_argument("--dry-run", action="store_true", help="Fetch from CRM and parse without writing to database")
    args = parser.parse_args()

    print(f"=== Starting CRM to DWH Sync (Dry-Run: {args.dry_run}) ===")

    if not B24_URL:
        print("[ERROR] B24_WEBHOOK_URL is not defined in environment variables. Please set it before running.")
        sys.exit(1)

    filter_params = {}
    if not args.full and args.days > 0:
        since_date = (datetime.datetime.now() - datetime.timedelta(days=args.days)).strftime("%Y-%m-%dT00:00:00")
        filter_params[">=DATE_MODIFY"] = since_date
        print(f"[INFO] Incremental mode: filtering >= {since_date}")
    else:
        print("[INFO] Full backfill mode selected.")

    print("Fetching deals from Bitrix24...")
    deals = fetch_all_items("crm.deal.list", ["*", "UF_*"], filter_params)
    print(f"[OK] Fetched {len(deals)} deals.")

    if args.dry_run:
        print(f"[DRY-RUN] Processed {len(deals)} deals successfully. Database write skipped.")
        sys.exit(0)

    # Database insertion
    try:
        import psycopg2
        from psycopg2.extras import execute_values
    except ImportError:
        print("[ERROR] psycopg2 is not installed. Install with 'pip install psycopg2-binary'")
        sys.exit(1)

    if not PG_PASS:
        print("[ERROR] PG_PASS environment variable is not defined.")
        sys.exit(1)

    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DBNAME,
        user=PG_USER,
        password=PG_PASS
    )
    cursor = conn.cursor()

    deals_rows = []
    stages_rows = []

    for d in deals:
        deal_id = str(d.get("ID"))
        title = d.get("TITLE") or "Без названия"
        category_id = str(d.get("CATEGORY_ID", "0"))
        stage_raw = str(d.get("STAGE_ID", "NEW"))
        date_create = d.get("DATE_CREATE")
        date_close = d.get("CLOSEDATE") if d.get("CLOSED") == "Y" else None
        tender_number = d.get("UF_CRM_1714470984", "")
        reason_raw = d.get("UF_CRM_1714470999", "")
        our_offer = float(d.get("OPPORTUNITY") or 0)
        tender_amount = float(d.get("UF_CRM_1714471015") or our_offer)

        is_tender = (category_id == "4") or bool(tender_number) or stage_raw.startswith("C4:")
        pipeline_name = "Тендеры" if is_tender else "Заказчики (Прямые продажи)"
        is_won = (stage_raw in WON_STAGES_CAT4) or (stage_raw == "WON")

        close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "Не указано")
        stage_display = STAGE_NAMES.get(stage_raw, stage_raw)

        raw_data = json.dumps(d, ensure_ascii=False)

        deals_rows.append((
            deal_id, title, tender_number, date_create, date_close, stage_display,
            close_reason, d.get("ASSIGNED_BY_ID"), d.get("COMPANY_ID"), tender_amount,
            our_offer, "", "", raw_data, pipeline_name, is_won
        ))
        stages_rows.append((deal_id, stage_raw, date_close or date_create))

    # UPSERT deals
    upsert_deal_sql = """
        INSERT INTO analytics_closed_deals (
            deal_id, title, tender_number, date_create, date_close, stage_id,
            close_reason, responsible_name, customer_name, tender_amount,
            our_offer_amount, delivery_time, payment_terms, raw_data, pipeline_name, is_won
        ) VALUES %s
        ON CONFLICT (deal_id) DO UPDATE SET
            title = EXCLUDED.title,
            tender_number = EXCLUDED.tender_number,
            date_create = EXCLUDED.date_create,
            date_close = EXCLUDED.date_close,
            stage_id = EXCLUDED.stage_id,
            close_reason = EXCLUDED.close_reason,
            tender_amount = EXCLUDED.tender_amount,
            our_offer_amount = EXCLUDED.our_offer_amount,
            pipeline_name = EXCLUDED.pipeline_name,
            is_won = EXCLUDED.is_won;
    """
    execute_values(cursor, upsert_deal_sql, deals_rows, page_size=200)

    # Insert stage history
    insert_stage_sql = """
        INSERT INTO analytics_deal_stage_history (deal_id, stage_id, date_entered)
        VALUES %s
        ON CONFLICT (deal_id, stage_id) DO NOTHING;
    """
    execute_values(cursor, insert_stage_sql, stages_rows, page_size=200)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"[SUCCESS] Upserted {len(deals_rows)} deals and {len(stages_rows)} stage history records into PostgreSQL.")

if __name__ == "__main__":
    main()
