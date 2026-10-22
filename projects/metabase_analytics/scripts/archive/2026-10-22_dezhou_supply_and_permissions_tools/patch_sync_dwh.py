#!/usr/bin/env python3
# -*- coding: utf-8 -*-
with open("projects/metabase_analytics/scripts/sync_analytics_dwh.py", "r", encoding="utf-8") as f:
    text = f.read()

# Add SUPPLY_USER_MAP
user_map_code = """USER_MAP = {
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
}"""

text = text.replace("""USER_MAP = {
    "14": "Сауле Бестова (экс-сотрудник)",
    "38": "Александра Пономарева",
    "20": "Азат Денишов",
    "16": "Анжелика Павлова",
    "36": "Чулпан Хузина",
    "1": "Артем",
    "26": "Салман"
}""", user_map_code)

# Add fetch of group 14 tasks before deals loop
target_fetch = """    print(f"Fetching deals from CRM...")
    deals = fetch_all_items("crm.deal.list", select_fields=select_fields, filter_params=deal_filter)
    print(f"Fetched {len(deals)} deals.")"""

repl_fetch = """    print(f"Fetching deals from CRM...")
    deals = fetch_all_items("crm.deal.list", select_fields=select_fields, filter_params=deal_filter)
    print(f"Fetched {len(deals)} deals.")

    print("Fetching Group 14 tasks for supply assignment...")
    g14_tasks = fetch_all_items("tasks.task.list", select_fields=["ID", "RESPONSIBLE_ID", "UF_CRM_TASK"], filter_params={"GROUP_ID": 14})
    deal_to_supply = {}
    for t in g14_tasks:
        c_list = t.get("ufCrmTask") or []
        r_id = str(t.get("responsibleId") or "")
        r_name = SUPPLY_USER_MAP.get(r_id, f"Закупщик ID {r_id}")
        t_id = int(t.get("id"))
        for item in c_list:
            if item.startswith("D_"):
                d_key = item[2:]
                if d_key not in deal_to_supply or r_id in ["30", "20", "86", "84", "44"]:
                    deal_to_supply[d_key] = (r_name, t_id)
    print(f"Mapped {len(deal_to_supply)} deals to Group 14 supply specialists.")"""

text = text.replace(target_fetch, repl_fetch)

# Add supply_responsible_name, supply_task_id to deals_rows
target_append = """        deals_rows.append((
            deal_id, title, tender_number, date_create, date_close, stage_display,
            close_reason, USER_MAP.get(str(d.get("ASSIGNED_BY_ID")), f"ID {d.get('ASSIGNED_BY_ID')}"), d.get("COMPANY_ID"), tender_amount,
            our_offer, delivery_time, payment_terms, raw_data, pipeline_name, is_won,
            has_advance, advance_pct, advance_details
        ))"""

repl_append = """        supply_info = deal_to_supply.get(str(deal_id), (None, None))
        supply_resp_name = supply_info[0]
        supply_t_id = supply_info[1]

        deals_rows.append((
            deal_id, title, tender_number, date_create, date_close, stage_display,
            close_reason, USER_MAP.get(str(d.get("ASSIGNED_BY_ID")), f"ID {d.get('ASSIGNED_BY_ID')}"), d.get("COMPANY_ID"), tender_amount,
            our_offer, delivery_time, payment_terms, raw_data, pipeline_name, is_won,
            has_advance, advance_pct, advance_details, supply_resp_name, supply_t_id
        ))"""

text = text.replace(target_append, repl_append)

# Update migration SQL
target_mig = """        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS has_advance BOOLEAN DEFAULT FALSE;
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS advance_percent NUMERIC DEFAULT 0;
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS advance_details TEXT;
        CREATE INDEX IF NOT EXISTS idx_closed_deals_has_advance ON analytics_closed_deals(has_advance);"""

repl_mig = """        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS has_advance BOOLEAN DEFAULT FALSE;
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS advance_percent NUMERIC DEFAULT 0;
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS advance_details TEXT;
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS supply_responsible_name VARCHAR(128);
        ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS supply_task_id BIGINT;
        CREATE INDEX IF NOT EXISTS idx_closed_deals_has_advance ON analytics_closed_deals(has_advance);
        CREATE INDEX IF NOT EXISTS idx_closed_deals_supply_responsible ON analytics_closed_deals(supply_responsible_name);"""

text = text.replace(target_mig, repl_mig)

# Update upsert SQL
target_upsert = """        INSERT INTO analytics_closed_deals (
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
            advance_details = EXCLUDED.advance_details;"""

repl_upsert = """        INSERT INTO analytics_closed_deals (
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
            supply_task_id = EXCLUDED.supply_task_id;"""

text = text.replace(target_upsert, repl_upsert)

with open("projects/metabase_analytics/scripts/sync_analytics_dwh.py", "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: sync_analytics_dwh.py updated with Group 14 tasks mapping!")
