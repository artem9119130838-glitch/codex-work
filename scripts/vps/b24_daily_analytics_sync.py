#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Automated Synchronization: Bitrix24 -> PostgreSQL (marketing_db)
Updates analytics_closed_deals and analytics_deal_stage_history.
Applies business rule: stage 'В работе' and subsequent execution stages = WON tender.
"""

import sys
import os
import json
import time
import datetime
import urllib.request
import urllib.error
import psycopg2
from psycopg2.extras import execute_values

B24_URL = os.environ.get("B24_WEBHOOK_URL", "https://b24-g4wfjq.bitrix24.ru/rest/1/${BITRIX24_WEBHOOK_TOKEN}").rstrip("/")
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
    # Cat 0
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
    # Cat 4
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

# Stages in Cat 0 that signify the contract is in execution
WON_STAGES_CAT0 = {"1", "UC_UVHNXE", "UC_Y7FU08", "UC_97AEGE", "2", "UC_8CYR5V", "3", "WON"}
WON_STAGES_CAT4 = {"C4:EXECUTING", "C4:FINAL_INVOICE"}
KNOWN_WON_DEALS = {"514", "1010", "766", "942", "840", "1332", "1278", "712", "762", "1890", "1892", "996"}

def b24_post(endpoint, payload=None):
    url = f"{B24_URL}/{endpoint}"
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"B24 request error [{endpoint}]: {e}")
        return None

def fetch_users():
    users = {}
    res = b24_post("user.get.json")
    if res and "result" in res:
        for u in res["result"]:
            uid = str(u.get("ID"))
            full_name = f"{u.get('NAME', '')} {u.get('LAST_NAME', '')}".strip()
            users[uid] = full_name or u.get("EMAIL") or f"Пользователь {uid}"
    return users

def fetch_companies():
    companies = {}
    start = 0
    while True:
        res = b24_post("crm.company.list.json", {"select": ["ID", "TITLE"], "start": start})
        if not res or "result" not in res:
            break
        items = res["result"]
        for c in items:
            cid = str(c.get("ID"))
            companies[cid] = c.get("TITLE", "").strip() or f"Компания #{cid}"
        if "next" in res:
            start = res["next"]
            time.sleep(0.1)
        else:
            break
    return companies

def parse_amt(val):
    if not val:
        return None
    try:
        return float(str(val).split("|")[0].strip())
    except Exception:
        return None

def extract_advance_info(payment_text):
    if not payment_text:
        return False, 0.0, ""
    
    clean_text = payment_text.strip()
    low = clean_text.lower()
    
    import re
    # Check if empty label like "\nПредоплата: " or "Предоплата: -" or "Предоплата: нет"
    sub_text = re.sub(r'(?:условия оплаты|предоплата|аванс)[:\s\-]*', '', low).strip()
    if not sub_text or sub_text in ["нет", "отсутствует", "не найдено", "не указано", "не предусмотрено", "не предусмотрена", "не установлена", "не установлен", "-"]:
        return False, 0.0, ""
    
    adv_pct_match = re.search(r'(?:аванс\w*|предоплат\w*)[^\d%]{0,35}?(\d{1,3})\s*%', low)
    pct_adv_match = re.search(r'(\d{1,3})\s*%\s*(?:аванс\w*|предоплат\w*)', low)
    
    percent = 0.0
    if adv_pct_match:
        percent = float(adv_pct_match.group(1))
    elif pct_adv_match:
        percent = float(pct_adv_match.group(1))
        
    if percent == 100.0:
        if any(p in low for p in ["постоплат", "по факту", "после поставки", "после подписания", "дней с даты приемки", "дней со дня получения"]):
            percent = 0.0
            
    has_adv = False
    if percent > 0:
        has_adv = True
    elif any(pos in low for pos in ["аванс", "предоплат"]):
        is_neg = False
        for neg in ["без аванса", "аванс не предусмотрен", "предоплата не предусмотрена", "не предусмотрена", "не предусмотрено", "не найдено", "не указано", "не установлена", "не установлен", "авансирование не предусмотрено", "отсутствует"]:
            if neg in low:
                is_neg = True
                break
        if not is_neg:
            has_adv = True
            
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

def run_sync():
    start_time = datetime.datetime.now()
    print(f"[{start_time.isoformat()}] STARTING B24 DAILY ANALYTICS SYNC...")
    
    users = fetch_users()
    print(f"Loaded {len(users)} users.")
    companies = fetch_companies()
    print(f"Loaded {len(companies)} companies.")
    
    deals = []
    start = 0
    while True:
        payload = {
            "select": [
                "ID", "TITLE", "CATEGORY_ID", "STAGE_ID", "STAGE_SEMANTIC_ID",
                "DATE_CREATE", "CLOSEDATE", "ASSIGNED_BY_ID", "COMPANY_ID",
                "UF_CRM_1784273768", "UF_CRM_TP_11", "UF_CRM_1776272639039",
                "UF_CRM_1781430179342", "UF_CRM_1782280989770", "OPPORTUNITY"
            ],
            "start": start
        }
        res = b24_post("crm.deal.list.json", payload)
        if not res or "result" not in res:
            break
        items = res["result"]
        deals.extend(items)
        if "next" in res:
            start = res["next"]
            time.sleep(0.1)
        else:
            break
            
    print(f"Total deals fetched from Bitrix24: {len(deals)}")
    
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DBNAME,
        user=PG_USER,
        password=PG_PASS
    )
    cursor = conn.cursor()
    
    won_tender_count = 0
    deals_rows = []
    stages_rows = []
    
    for d in deals:
        deal_id = str(d.get("ID"))
        title = d.get("TITLE") or "Без названия"
        category_id = str(d.get("CATEGORY_ID") or "0")
        stage_raw = str(d.get("STAGE_ID") or "NEW")
        semantic_id = str(d.get("STAGE_SEMANTIC_ID") or "")
        tender_number = d.get("UF_CRM_TP_11")
        date_create = d.get("DATE_CREATE")
        date_close = d.get("CLOSEDATE")
        
        resp_id = str(d.get("ASSIGNED_BY_ID") or "")
        responsible_name = users.get(resp_id, f"ID {resp_id}" if resp_id else "Не назначен")
        
        comp_id = str(d.get("COMPANY_ID") or "")
        customer_name = companies.get(comp_id, f"Компания #{comp_id}" if comp_id else "Не указан")
        
        tender_amount = parse_amt(d.get("UF_CRM_1776272639039"))
        our_offer = parse_amt(d.get("OPPORTUNITY"))
        if not tender_amount and our_offer:
            tender_amount = our_offer
            
        delivery_time = str(d.get("UF_CRM_1781430179342") or "")
        payment_terms = str(d.get("UF_CRM_1782280989770") or "")
        reason_raw = d.get("UF_CRM_1784273768")
        
        # Advance condition extraction
        has_advance, advance_percent, advance_details = extract_advance_info(payment_terms)

        # Determine if tender
        is_tender = (category_id == "4") or bool(tender_number) or stage_raw.startswith("C4:") or ("Тендер" in str(title)) or ("Поставка" in str(title) and tender_number)
        pipeline_name = "Тендеры" if is_tender else "Заказчики (Прямые продажи)"
        
        # Determine won / lost
        is_won = False
        stage_name = STAGE_NAMES.get(stage_raw, stage_raw)
        
        if is_tender:
            # CRITICAL: C4:WON is "Не взяли в работу" (rejection before bid), NOT a win!
            if stage_raw == "C4:WON":
                is_won = False
                close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "Не взяли в работу")
                stage_display = "Не взяли в работу"
            # USER RULE: If in 'В работе' or subsequent execution stages -> WON
            elif (category_id == "0" and stage_raw in WON_STAGES_CAT0 and (bool(tender_number) or deal_id in KNOWN_WON_DEALS)) or \
                 (stage_raw in WON_STAGES_CAT4) or \
                 (deal_id in KNOWN_WON_DEALS):
                is_won = True
                won_tender_count += 1
                close_reason = "Выигран в тендере"
                stage_display = f"Победа ({stage_name})"
            elif stage_raw == "C4:LOSE":
                close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "Проиграли по цене")
                stage_display = "Проигрыш"
            elif stage_raw in ("C4:APOLOGY", "C4:UC_VSDEUH"):
                close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "Не смогли отработать" if stage_raw == "C4:APOLOGY" else "Закупки отменены заказчиком")
                stage_display = stage_name
            else:
                close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "Не указано" if not reason_raw else f"Код {reason_raw}")
                stage_display = stage_name
        else:
            if stage_raw == "WON" or semantic_id == "S":
                is_won = True
                close_reason = "Прямые продажи (Успешно)"
                stage_display = "Прямые продажи (Успешно)"
            elif stage_raw == "LOSE" or semantic_id == "F":
                close_reason = CLOSE_REASON_MAP.get(str(reason_raw), "Отказ (Прямые продажи)")
                stage_display = stage_name
            else:
                close_reason = "В работе"
                stage_display = stage_name
                
        raw_data = json.dumps(d, ensure_ascii=False)
        
        deals_rows.append((
            deal_id, title, tender_number, date_create, date_close, stage_display,
            close_reason, responsible_name, customer_name, tender_amount,
            our_offer, delivery_time, payment_terms, raw_data, pipeline_name, is_won,
            has_advance, advance_percent, advance_details
        ))
        
        stages_rows.append((deal_id, stage_raw, date_close or date_create))

    # Migration
    migration_sql = """
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS has_advance BOOLEAN DEFAULT FALSE;
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS advance_percent NUMERIC DEFAULT 0;
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS advance_details TEXT;
        CREATE INDEX IF NOT EXISTS idx_closed_deals_has_advance ON analytics_closed_deals(has_advance);
    """
    cursor.execute(migration_sql)
    conn.commit()

    # UPSERT into analytics_closed_deals
    upsert_deal_sql = """
        INSERT INTO analytics_closed_deals (
            deal_id, title, tender_number, date_create, date_close, stage_id,
            close_reason, responsible_name, customer_name, tender_amount,
            our_offer_amount, delivery_time, payment_terms, raw_data, pipeline_name, is_won,
            has_advance, advance_percent, advance_details
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
            advance_details = EXCLUDED.advance_details;
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
    
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"[{end_time.isoformat()}] SYNC FINISHED in {duration:.1f}s. Inserted/Updated {len(deals_rows)} deals. Identified {won_tender_count} won tenders.")

if __name__ == "__main__":
    run_sync()
