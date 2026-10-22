#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical DWH Sync Pipeline: sync_analytics_dwh.py
Version: 2.2 (2026-10-22)

Synchronizes closed deals and stage transition history from Bitrix24 CRM
into PostgreSQL DWH (marketing_db) for Metabase BI dashboards.
Includes automated extraction of advance / prepayment conditions.

Supports:
- --dry-run mode
- --days N (incremental sync)
- --since-date YYYY-MM-DD (e.g. 2026-01-01)
- --full (complete historical backfill)
- Zero Secrets Policy: Reads all credentials and webhooks from environment variables or .env.
"""

import os
import sys
import json
import time
import re
import argparse
import datetime
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

B24_URL = (os.environ.get("B24_WEBHOOK_URL") or os.environ.get("BITRIX24_WEBHOOK_URL", "")).rstrip("/")
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

USER_MAP = {
    "14": "Сауле Бестова (экс-сотрудник)",
    "38": "Александра Пономарева",
    "20": "Азат Денишов",
    "16": "Анжелика Павлова",
    "36": "Чулпан Хузина",
    "1": "Артем",
    "26": "Салман"
}

SUPPLY_USER_MAP = {
    "20": "Азат Денишов",
    "30": "Miss Wang (Дечжоу)",
    "86": "Cindy Qian (Дечжоу)",
    "84": "Юйнань Ли (Дечжоу)",
    "44": "Liyan Wang (Дечжоу)",
    "38": "Александра Пономарева",
    "14": "Сауле Бестова (экс-сотрудник)"
}

STAGE_NAMES = {
    "NEW": "Заявка на расчет",
    "PREPARATION": "Расчет КП",
    "PREPAYMENT_INVOICE": "КП отправлен, требует ОКК",
    "EXECUTING": "Согласование КП",
    "FINAL_INVOICE": "Ожидает оплаты",
    "1": "В работе",
    "UC_UVHNXE": "Требуется заказать товар",
    "UC_Y7FU08": "Товар заказан и оплачен",
    "UC_97AEGE": "Товар прибыл, ожидает отправки",
    "2": "В пути (международном)",
    "UC_8CYR5V": "Товар прибыл в РФ, отправить!",
    "3": "Отправлен клиенту",
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
KNOWN_WON_DEALS = {"514", "1010", "766", "942", "840", "1332", "1278", "712", "762", "1890", "1892", "996"}

def extract_advance_info(payment_text):
    """
    Parses payment_terms text and extracts advance information:
    Returns: (has_advance: bool, advance_percent: float, advance_details: str)
    """
    if not payment_text:
        return False, 0.0, ""
    
    clean_text = payment_text.strip()
    low = clean_text.lower()
    
    # Check if empty label like "\nПредоплата: " or "Предоплата: -" or "Предоплата: нет"
    sub_text = re.sub(r'(?:условия оплаты|предоплата|аванс)[:\s\-]*', '', low).strip()
    if not sub_text or sub_text in ["нет", "отсутствует", "не найдено", "не указано", "не предусмотрено", "не предусмотрена", "не установлена", "не установлен", "-"]:
        return False, 0.0, ""
    
    # 1. Negative markers
    negative_markers = [
        "без аванса", "аванс не предусмотрен", "предоплата не предусмотрена",
        "не предусмотрена", "не предусмотрено", "не найдено", "не указано",
        "не установлена", "не установлен", "авансирование не предусмотрено",
        "авансирование по договору не предусмотрено", "аванс: не предусмотрен",
        "предоплата: не предусмотрена", "предоплата: не указано", "предоплата: не найдено",
        "предоплата: отсутствует", "аванс: отсутствует", "предоплата: не установлена",
        "аванс: не установлен", "постоплата", "100% постоплата", "оплата по факту",
        "после поставки", "после подписания акта", "100% оплата поставляемого товара",
        "оплата осуществляется в течение", "оплата товара производится заказчиком в течение"
    ]
    
    # 2. Match percentage
    adv_pct_match = re.search(r'(?:аванс\w*|предоплат\w*)[^\d%]{0,35}?(\d{1,3})\s*%', low)
    pct_adv_match = re.search(r'(\d{1,3})\s*%\s*(?:аванс\w*|предоплат\w*)', low)
    
    percent = 0.0
    if adv_pct_match:
        percent = float(adv_pct_match.group(1))
    elif pct_adv_match:
        percent = float(pct_adv_match.group(1))
        
    # Check for "100%" - verify it's not post-payment
    if percent == 100.0:
        if any(p in low for p in ["постоплат", "по факту", "после поставки", "после подписания", "дней с даты приемки", "дней со дня получения"]):
            percent = 0.0
            
    has_adv = False
    if percent > 0:
        has_adv = True
    elif any(pos in low for pos in ["аванс", "предоплат"]):
        is_neg = False
        for neg in ["без аванса", "аванс не предусмотрен", "предоплата не предусмотрена", "не предусмотрена", "не предусмотрено", "не найдено", "не указано", "авансирование не предусмотрено", "отсутствует"]:
            if neg in low:
                is_neg = True
                break
        if not is_neg:
            has_adv = True
            
    # Extract short detail summary
    details = ""
    lines = clean_text.splitlines()
    for line in lines:
        line_clean = line.strip()
        line_sub = re.sub(r'^(?:условия оплаты|предоплата|аванс)[:\s\-]*', '', line_clean.lower()).strip()
        if any(w in line_clean.lower() for w in ["аванс", "предоплат"]) and line_sub and line_sub not in ["не найдено", "не указано", "отсутствует", "-"]:
            details = line_clean[:180]
            break
    if not details and lines:
        for line in lines:
            if line.strip():
                details = line.strip()[:180]
                break
        
    return has_adv, percent, details

def parse_amt(val):
    if not val:
        return 0.0
    try:
        return float(str(val).split("|")[0].strip())
    except Exception:
        return 0.0

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
        time.sleep(0.15)
    return items

def fetch_group14_supply_tasks(b24_url):
    """
    Fetches all tasks from Bitrix24 Group 14 (Снабжение КНР) and maps deals
    via UF_CRM_TASK (e.g. 'D_1234') to the responsible supply specialist.
    Returns dict: {deal_id_str: (resp_name, task_id)}
    """
    url = f"{b24_url.rstrip('/')}/tasks.task.list.json"
    deal_to_supply = {}
    start = 0

    while True:
        payload = {
            "filter": {"GROUP_ID": 14},
            "select": ["ID", "TITLE", "RESPONSIBLE_ID", "UF_CRM_TASK", "CREATED_DATE"],
            "order": {"ID": "DESC"},
            "start": start
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                tasks = res.get("result", {}).get("tasks", [])
                if not tasks:
                    break
                for t in tasks:
                    crm_list = t.get("ufCrmTask") or []
                    resp_id = str(t.get("responsibleId") or "")
                    resp_name = SUPPLY_USER_MAP.get(resp_id, USER_MAP.get(resp_id, f"Закупщик ID {resp_id}"))
                    task_id = t.get("id")
                    for crm_item in crm_list:
                        if isinstance(crm_item, str) and crm_item.startswith("D_"):
                            d_id = crm_item[2:]
                            if d_id not in deal_to_supply:
                                deal_to_supply[d_id] = (resp_name, task_id)
                if len(tasks) < 50:
                    break
                start += len(tasks)
                time.sleep(0.1)
        except Exception as e:
            print(f"[WARNING] Failed to fetch chunk at start={start} for Group 14: {e}")
            break

    return deal_to_supply

def main():
    parser = argparse.ArgumentParser(description="Bitrix24 CRM to PostgreSQL DWH Sync Pipeline (v2.0 with Advance Analysis)")
    parser.add_argument("--days", type=int, default=0, help="Days to look back for incremental sync")
    parser.add_argument("--since-date", type=str, default="", help="Sync deals created/modified since date (YYYY-MM-DD)")
    parser.add_argument("--full", action="store_true", help="Perform full historical backfill")
    parser.add_argument("--dry-run", action="store_true", help="Fetch from CRM, parse and display audit without DB write")
    parser.add_argument("--inspect-supply", action="store_true", help="Inspect Group 14 supply tasks and assignee breakdown without sync")
    parser.add_argument("--check-db", action="store_true", help="Test direct PostgreSQL connectivity and display table stats")
    args = parser.parse_args()

    print(f"=== Starting CRM to DWH Sync Pipeline v2.0 (Dry-Run: {args.dry_run}) ===")

    if args.check_db:
        print("=== Checking PostgreSQL DWH Connection ===")
        try:
            import psycopg2
            conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DBNAME, user=PG_USER, password=PG_PASS, connect_timeout=5)
            cur = conn.cursor()
            cur.execute("SELECT count(*), count(supply_responsible_name), count(CASE WHEN has_advance THEN 1 END) FROM analytics_closed_deals;")
            row = cur.fetchone()
            print(f"[SUCCESS] PostgreSQL Connected! Total deals: {row[0]} | With Supply Assignee: {row[1]} | With Advance: {row[2]}")
            conn.close()
        except Exception as e:
            print(f"[FAIL] PostgreSQL Connection Error: {e}")
        sys.exit(0)

    if not B24_URL:
        print("[ERROR] B24_WEBHOOK_URL / BITRIX24_WEBHOOK_URL is not defined.")
        sys.exit(1)

    if args.inspect_supply:
        print("=== Inspecting Group 14 Supply Tasks & Dezhou Assignees ===")
        deal_to_supply = fetch_group14_supply_tasks(B24_URL)
        resp_counts = {}
        for d_id, (resp_name, t_id) in deal_to_supply.items():
            resp_counts[resp_name] = resp_counts.get(resp_name, 0) + 1
        print(f"Total Linked Deals from Group 14: {len(deal_to_supply)}")
        print("Distribution by Dezhou Supply Assignees:")
        for r_name, cnt in sorted(resp_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {r_name:<25}: {cnt} deals")
        sys.exit(0)

    filter_params = {}
    if args.since_date:
        filter_params[">=DATE_CREATE"] = f"{args.since_date}T00:00:00"
        print(f"[INFO] Filtering deals with DATE_CREATE >= {args.since_date}")
    elif not args.full and args.days > 0:
        since_date = (datetime.datetime.now() - datetime.timedelta(days=args.days)).strftime("%Y-%m-%dT00:00:00")
        filter_params[">=DATE_MODIFY"] = since_date
        print(f"[INFO] Incremental mode: filtering >= {since_date}")
    else:
        print("[INFO] Full backfill mode selected.")

    print("Fetching deals from Bitrix24 CRM...")
    deals = fetch_all_items("crm.deal.list", ["*", "UF_*"], filter_params)
    print(f"[OK] Fetched {len(deals)} deals from CRM.")

    print("Fetching supply tasks from Group 14...")
    deal_to_supply = fetch_group14_supply_tasks(B24_URL)
    print(f"[OK] Mapped supply tasks for {len(deal_to_supply)} deals.")

    deals_rows = []
    stages_rows = []

    tender_count = 0
    advance_count = 0
    advance_by_bracket = {"0% (Без аванса)": 0, "10-30%": 0, "31-50%": 0, ">50%": 0, "Упоминание без %": 0}
    lost_advance_by_reason = {}

    for d in deals:
        deal_id = str(d.get("ID"))
        title = d.get("TITLE") or "Без названия"
        category_id = str(d.get("CATEGORY_ID", "0"))
        stage_raw = str(d.get("STAGE_ID", "NEW"))
        date_create = d.get("DATE_CREATE")
        date_close = d.get("CLOSEDATE") if d.get("CLOSED") == "Y" else None

        tender_number = d.get("UF_CRM_TP_11") or d.get("UF_CRM_1714470984", "")
        reason_raw = d.get("UF_CRM_1784273768") or d.get("UF_CRM_1714470999", "")
        our_offer = parse_amt(d.get("OPPORTUNITY"))
        tender_amount = parse_amt(d.get("UF_CRM_1776272639039")) or parse_amt(d.get("UF_CRM_1714471015")) or our_offer

        delivery_time = str(d.get("UF_CRM_1781430179342") or "")
        payment_terms = str(d.get("UF_CRM_1782280989770") or "")

        # Advance extraction
        has_advance, advance_pct, advance_details = extract_advance_info(payment_terms)

        is_tender = (category_id == "4") or bool(tender_number) or stage_raw.startswith("C4:") or ("Тендер" in str(title)) or ("Поставка" in str(title) and tender_number)
        pipeline_name = "Тендеры" if is_tender else "Заказчики (Прямые продажи)"

        is_won = False
        stage_display = STAGE_NAMES.get(stage_raw, stage_raw)

        if is_tender:
            tender_count += 1
            if has_advance:
                advance_count += 1
                if advance_pct == 0:
                    advance_by_bracket["Упоминание без %"] += 1
                elif advance_pct <= 30:
                    advance_by_bracket["10-30%"] += 1
                elif advance_pct <= 50:
                    advance_by_bracket["31-50%"] += 1
                else:
                    advance_by_bracket[">50%"] += 1
            else:
                advance_by_bracket["0% (Без аванса)"] += 1

            if stage_raw == "C4:WON":
                is_won = False
                close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "Не взяли в работу")
                stage_display = "Не взяли в работу"
            elif (category_id == "0" and stage_raw in WON_STAGES_CAT0 and (bool(tender_number) or deal_id in KNOWN_WON_DEALS)) or \
                 (stage_raw in WON_STAGES_CAT4) or (deal_id in KNOWN_WON_DEALS):
                is_won = True
                close_reason = "Выигран в тендере"
                stage_display = f"Победа ({stage_display})"
            elif stage_raw == "C4:LOSE":
                close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "Проиграли по цене")
                stage_display = "Проигрыш"
            elif stage_raw in ("C4:APOLOGY", "C4:UC_VSDEUH"):
                close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "Не смогли отработать" if stage_raw == "C4:APOLOGY" else "Закупки отменены заказчиком")
            else:
                close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "В работе" if not reason_raw else f"Код {reason_raw}")

            if not is_won and close_reason != "В работе" and has_advance:
                lost_advance_by_reason[close_reason] = lost_advance_by_reason.get(close_reason, 0) + 1
        else:
            if stage_raw == "WON":
                is_won = True
                close_reason = "Прямые продажи (Успешно)"
            elif stage_raw == "LOSE":
                close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "Отказ (Прямые продажи)")
            else:
                close_reason = "В работе"

        raw_data = json.dumps(d, ensure_ascii=False)

        supply_info = deal_to_supply.get(str(deal_id), (None, None))
        supply_resp_name = supply_info[0]
        supply_t_id = supply_info[1]

        deals_rows.append((
            deal_id, title, tender_number, date_create, date_close, stage_display,
            close_reason, USER_MAP.get(str(d.get("ASSIGNED_BY_ID")), f"ID {d.get('ASSIGNED_BY_ID')}"), d.get("COMPANY_ID"), tender_amount,
            our_offer, delivery_time, payment_terms, raw_data, pipeline_name, is_won,
            has_advance, advance_pct, advance_details, supply_resp_name, supply_t_id
        ))
        stages_rows.append((deal_id, stage_raw, date_close or date_create))

    print(f"\n--- AUDIT SUMMARY ---")
    print(f"Total deals processed: {len(deals_rows)}")
    print(f"Total tender deals: {tender_count}")
    print(f"Tender deals with advance: {advance_count} ({round(advance_count / max(tender_count, 1) * 100, 1)}%)")
    print(f"Advance brackets distribution: {advance_by_bracket}")
    print(f"Lost advance deals by reason: {lost_advance_by_reason}")

    if args.dry_run:
        print("\n[DRY-RUN] First 5 sample tender deals with advance:")
        adv_samples = [r for r in deals_rows if r[16] is True][:5]
        for r in adv_samples:
            print(f"  Deal {r[0]} | Stg: {r[5]} | Reason: {r[6]} | Pct: {r[17]}% | Adv: '{r[18]}'")
        print("\n[DRY-RUN] Execution completed successfully. Database write skipped.")
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

    # Migration
    migration_sql = """
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS has_advance BOOLEAN DEFAULT FALSE;
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS advance_percent NUMERIC DEFAULT 0;
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS advance_details TEXT;
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS supply_responsible_name VARCHAR(128);
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS supply_task_id BIGINT;
        CREATE INDEX IF NOT EXISTS idx_closed_deals_has_advance ON analytics_closed_deals(has_advance);
        CREATE INDEX IF NOT EXISTS idx_closed_deals_supply_responsible ON analytics_closed_deals(supply_responsible_name);
    """
    cursor.execute(migration_sql)
    conn.commit()

    upsert_deal_sql = """
        INSERT INTO analytics_closed_deals (
            deal_id, title, tender_number, date_create, date_close, stage_id,
            close_reason, responsible_name, customer_name, tender_amount,
            our_offer_amount, delivery_time, payment_terms, raw_data, pipeline_name, is_won,
            has_advance, advance_percent, advance_details, supply_responsible_name, supply_task_id
        ) VALUES %s
        ON CONFLICT (deal_id) DO UPDATE SET
            title = EXCLUDED.title,
            tender_number = EXCLUDED.tender_number,
            date_create = EXCLUDED.date_create,
            date_close = EXCLUDED.date_close,
            stage_id = EXCLUDED.stage_id,
            close_reason = EXCLUDED.close_reason,
            responsible_name = EXCLUDED.responsible_name,
            customer_name = EXCLUDED.customer_name,
            tender_amount = EXCLUDED.tender_amount,
            our_offer_amount = EXCLUDED.our_offer_amount,
            delivery_time = EXCLUDED.delivery_time,
            payment_terms = EXCLUDED.payment_terms,
            raw_data = EXCLUDED.raw_data,
            pipeline_name = EXCLUDED.pipeline_name,
            is_won = EXCLUDED.is_won,
            has_advance = EXCLUDED.has_advance,
            advance_percent = EXCLUDED.advance_percent,
            advance_details = EXCLUDED.advance_details,
            supply_responsible_name = EXCLUDED.supply_responsible_name,
            supply_task_id = EXCLUDED.supply_task_id;
    """
    execute_values(cursor, upsert_deal_sql, deals_rows, page_size=200)

    insert_stage_sql = """
        INSERT INTO analytics_deal_stage_history (deal_id, stage_id, date_entered)
        VALUES %s
        ON CONFLICT (deal_id, stage_id) DO NOTHING;
    """
    execute_values(cursor, insert_stage_sql, stages_rows, page_size=200)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"[SUCCESS] Upserted {len(deals_rows)} deals (including advance conditions) into PostgreSQL.")

if __name__ == "__main__":
    main()
