#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical Pipeline: sync_suppliers_and_tasks_dwh.py
Version: 1.0 (2026-11-08)

Synchronizes China supply search tasks (Group 14, Template 44, RFQ) and 
created supplier companies from Bitrix24 CRM into PostgreSQL DWH (marketing_db)
for Metabase BI dashboard: «Пополнение базы поставщиков и аудит задач RFQ».

Includes automated Quality Scoring:
- Title & Category
- Linked Contact Person
- WeChat requirement (Phone +861..., IM WECHAT, or comment mention)
- Phone / Email
- Mandatory substantive comment (factory profile / terms)

Supports:
- --dry-run mode
- --days N (incremental sync)
- --full (complete historical backfill)
- Zero Secrets Policy: Reads credentials from environment variables or .env.
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

TARGET_USER_MAP = {
    30: "Miss Wang",
    44: "Лиень (Lien)",
    84: "Ли Юйнань (Li Yunan)",
    86: "Цянь Ин (Cindy Qian)",
    20: "Азат Денишов (Azat)"
}

CHINA_GROUP_ID = 14
SEARCH_TEMPLATE_ID = 44

def b24_call(method, payload, max_retries=3):
    if not B24_URL:
        raise ValueError("BITRIX24_WEBHOOK_URL is not set!")
    url = f"{B24_URL}/{method}.json"
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
    
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res.get("result")
        except urllib.error.HTTPError as e:
            if e.code == 429: # Rate limit
                time.sleep(2.0 * (attempt + 1))
                continue
            err_body = e.read().decode("utf-8", errors="replace")
            print(f"[B24 ERROR] HTTP {e.code} on {method}: {err_body}")
            raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    return None

def fetch_search_tasks(since_date=None):
    print(f"\n--- [1/3] Извлечение задач на поиск поставщиков (Группа {CHINA_GROUP_ID}, Шаблон {SEARCH_TEMPLATE_ID}) ---")
    tasks = []
    start = 0
    batch_size = 50
    
    date_filter = {}
    if since_date:
        date_filter[">=CREATED_DATE"] = since_date.strftime("%Y-%m-%d")

    while True:
        payload = {
            "order": {"ID": "DESC"},
            "filter": {
                "GROUP_ID": CHINA_GROUP_ID,
                **date_filter
            },
            "select": [
                "ID", "TITLE", "RESPONSIBLE_ID", "STATUS", 
                "CREATED_DATE", "CLOSED_DATE", "GROUP_ID", 
                "UF_CRM_TASK", "TAGS"
            ],
            "start": start
        }
        res = b24_call("tasks.task.list", payload)
        batch = res.get("tasks", []) if isinstance(res, dict) else (res or [])
        if not batch:
            break
        tasks.extend(batch)
        print(f"  Загружено задач: {len(tasks)}...", end="\r")
        if len(batch) < batch_size:
            break
        start += batch_size

    print(f"\n  Всего найдено задач в группе {CHINA_GROUP_ID}: {len(tasks)}")
    
    # Нормализуем задачи
    normalized = []
    for t in tasks:
        task_id = str(t.get("id"))
        title = t.get("title", "")
        resp_id = int(t.get("responsibleId") or 0)
        status = int(t.get("status") or 0)
        created_date = t.get("createdDate")
        closed_date = t.get("closedDate")
        group_id = int(t.get("groupId") or 0)
        
        uf_crm = t.get("ufCrmTask") or []
        attached_companies = []
        if isinstance(uf_crm, list):
            for item in uf_crm:
                if str(item).startswith("CO_"):
                    attached_companies.append(str(item).replace("CO_", ""))
        
        # Теги
        raw_tags = t.get("tags") or {}
        tags_list = []
        if isinstance(raw_tags, dict):
            for tag_info in raw_tags.values():
                if isinstance(tag_info, dict) and "title" in tag_info:
                    tags_list.append(tag_info["title"])
        elif isinstance(raw_tags, list):
            tags_list = [str(x) for x in raw_tags]

        has_supplier = len(attached_companies) > 0
        b24_url = f"https://b24-g4wfjq.bitrix24.ru/company/personal/user/{resp_id}/tasks/task/view/{task_id}/"

        normalized.append({
            "task_id": task_id,
            "title": title,
            "responsible_id": resp_id,
            "responsible_name": TARGET_USER_MAP.get(resp_id, f"User {resp_id}"),
            "created_date": created_date,
            "closed_date": closed_date,
            "status": status,
            "group_id": group_id,
            "template_id": SEARCH_TEMPLATE_ID if SEARCH_TEMPLATE_ID else None,
            "tags": tags_list,
            "uf_crm_raw": uf_crm,
            "attached_companies_count": len(attached_companies),
            "attached_company_ids": attached_companies,
            "has_supplier_attached": has_supplier,
            "b24_url": b24_url
        })
        
    return normalized

def fetch_supplier_companies(since_date=None):
    print(f"\n--- [2/3] Извлечение компаний-поставщиков (Создатели: {list(TARGET_USER_MAP.keys())}) ---")
    companies = []
    start = 0
    batch_size = 50
    
    date_filter = {}
    if since_date:
        date_filter[">=DATE_CREATE"] = since_date.strftime("%Y-%m-%d")

    while True:
        payload = {
            "order": {"DATE_CREATE": "DESC"},
            "filter": {
                "CREATED_BY_ID": list(TARGET_USER_MAP.keys()),
                **date_filter
            },
            "select": [
                "ID", "TITLE", "COMPANY_TYPE", "DATE_CREATE", 
                "CREATED_BY_ID", "ASSIGNED_BY_ID", "COMMENTS", 
                "INDUSTRY", "PHONE", "EMAIL", "WEB", "IM"
            ],
            "start": start
        }
        batch = b24_call("crm.company.list", payload) or []
        if not batch:
            break
        companies.extend(batch)
        print(f"  Загружено компаний: {len(companies)}...", end="\r")
        if len(batch) < batch_size:
            break
        start += batch_size

    print(f"\n  Всего найдено компаний: {len(companies)}")

    # Получаем контакты для каждой компании (batching)
    normalized = []
    for idx, c in enumerate(companies, 1):
        comp_id = str(c.get("ID"))
        title = c.get("TITLE", "")
        comp_type = c.get("COMPANY_TYPE", "")
        creator_id = int(c.get("CREATED_BY_ID") or 0)
        assigned_id = int(c.get("ASSIGNED_BY_ID") or 0)
        date_create = c.get("DATE_CREATE")
        comments = c.get("COMMENTS") or ""
        
        # Контакты компании: телефон, почта, IM
        raw_phone = c.get("PHONE") or []
        raw_email = c.get("EMAIL") or []
        raw_im = c.get("IM") or []
        
        phone_nums = [p.get("VALUE") for p in raw_phone if isinstance(p, dict) and p.get("VALUE")]
        email_addrs = [e.get("VALUE") for e in raw_email if isinstance(e, dict) and e.get("VALUE")]
        im_vals = [im.get("VALUE") for im in raw_im if isinstance(im, dict) and im.get("VALUE")]

        has_phone = len(phone_nums) > 0
        has_email = len(email_addrs) > 0
        
        # Проверка WeChat:
        # 1. Любой китайский мобильный телефон 11 знаков (обычно начинается с +861 или 13/15/17/18/19)
        # 2. Поле мессенджера IM
        # 3. Упоминание '微信' или 'wechat' или 'wx:' в комментариях
        has_wechat = False
        for p in phone_nums:
            clean_p = re.sub(r'[\s\-\+\(\)]', '', p)
            if (clean_p.startswith("861") and len(clean_p) == 13) or (clean_p.startswith("1") and len(clean_p) == 11):
                has_wechat = True
                break
        if not has_wechat:
            for im in im_vals:
                if "wechat" in str(im).lower() or "wx" in str(im).lower():
                    has_wechat = True
                    break
        if not has_wechat and comments:
            if any(k in comments.lower() for k in ["微信", "wechat", "wx:", "微信号"]):
                has_wechat = True

        # Проверка комментария: не пустой и содержит описание продукции/условий (> 15 символов без BB-тегов)
        clean_comment = re.sub(r'\[.*?\]', '', comments).strip()
        has_comment = len(clean_comment) >= 15

        # Проверка связанного контакта (crm.company.contact.items.get)
        has_contact = False
        try:
            contacts_res = b24_call("crm.company.contact.items.get", {"ID": comp_id})
            if contacts_res and len(contacts_res) > 0:
                has_contact = True
        except Exception:
            pass

        # Расчет индекса качества (Quality Score)
        missing_fields = []
        score = 0
        
        if title:
            score += 20
        else:
            missing_fields.append("нет названия")
            
        if has_contact:
            score += 20
        else:
            missing_fields.append("нет контакта")
            
        if has_wechat:
            score += 20
        else:
            missing_fields.append("нет WeChat ⚠️")
            
        if has_phone or has_email:
            score += 20
        else:
            missing_fields.append("нет телефона/email")
            
        if has_comment:
            score += 20
        else:
            missing_fields.append("нет комментария ⚠️")

        is_complete = (score == 100)
        b24_url = f"https://b24-g4wfjq.bitrix24.ru/crm/company/details/{comp_id}/"

        normalized.append({
            "company_id": comp_id,
            "title": title,
            "company_type": comp_type,
            "created_by_id": creator_id,
            "created_by_name": TARGET_USER_MAP.get(creator_id, f"User {creator_id}"),
            "assigned_by_id": assigned_id,
            "date_create": date_create,
            "has_contact": has_contact,
            "has_phone": has_phone,
            "has_email": has_email,
            "has_wechat": has_wechat,
            "has_comment": has_comment,
            "comment_text": clean_comment[:500] if clean_comment else "",
            "phone_numbers": phone_nums,
            "email_addresses": email_addrs,
            "is_complete": is_complete,
            "completeness_score": score,
            "missing_fields": missing_fields,
            "b24_url": b24_url
        })
        
    return normalized

def upsert_to_dwh(tasks, companies):
    print(f"\n--- [3/3] Запись в PostgreSQL DWH ({PG_HOST}:{PG_PORT}/{PG_DBNAME}) ---")
    import psycopg2
    from psycopg2.extras import execute_values
    
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DBNAME,
        user=PG_USER,
        password=PG_PASS
    )
    cur = conn.cursor()
    
    # 1. Upsert tasks
    if tasks:
        task_query = """
        INSERT INTO analytics_supplier_search_tasks (
            task_id, title, responsible_id, responsible_name, created_date,
            closed_date, status, group_id, template_id, tags, uf_crm_raw,
            attached_companies_count, attached_company_ids, has_supplier_attached,
            b24_url
        ) VALUES %s
        ON CONFLICT (task_id) DO UPDATE SET
            title = EXCLUDED.title,
            responsible_id = EXCLUDED.responsible_id,
            responsible_name = EXCLUDED.responsible_name,
            created_date = EXCLUDED.created_date,
            closed_date = EXCLUDED.closed_date,
            status = EXCLUDED.status,
            group_id = EXCLUDED.group_id,
            template_id = EXCLUDED.template_id,
            tags = EXCLUDED.tags,
            uf_crm_raw = EXCLUDED.uf_crm_raw,
            attached_companies_count = EXCLUDED.attached_companies_count,
            attached_company_ids = EXCLUDED.attached_company_ids,
            has_supplier_attached = EXCLUDED.has_supplier_attached,
            b24_url = EXCLUDED.b24_url,
            updated_at = NOW();
        """
        task_data = [
            (
                t["task_id"], t["title"], t["responsible_id"], t["responsible_name"],
                t["created_date"], t["closed_date"], t["status"], t["group_id"],
                t["template_id"], json.dumps(t["tags"]), json.dumps(t["uf_crm_raw"]),
                t["attached_companies_count"], json.dumps(t["attached_company_ids"]),
                t["has_supplier_attached"], t["b24_url"]
            )
            for t in tasks
        ]
        execute_values(cur, task_query, task_data)
        print(f"  Успешно обновлено задач в DWH: {len(tasks)}")

    # 2. Upsert companies
    if companies:
        comp_query = """
        INSERT INTO analytics_supplier_companies (
            company_id, title, company_type, created_by_id, created_by_name,
            assigned_by_id, date_create, has_contact, has_phone, has_email,
            has_wechat, has_comment, comment_text, phone_numbers, email_addresses,
            is_complete, completeness_score, missing_fields, b24_url
        ) VALUES %s
        ON CONFLICT (company_id) DO UPDATE SET
            title = EXCLUDED.title,
            company_type = EXCLUDED.company_type,
            created_by_id = EXCLUDED.created_by_id,
            created_by_name = EXCLUDED.created_by_name,
            assigned_by_id = EXCLUDED.assigned_by_id,
            date_create = EXCLUDED.date_create,
            has_contact = EXCLUDED.has_contact,
            has_phone = EXCLUDED.has_phone,
            has_email = EXCLUDED.has_email,
            has_wechat = EXCLUDED.has_wechat,
            has_comment = EXCLUDED.has_comment,
            comment_text = EXCLUDED.comment_text,
            phone_numbers = EXCLUDED.phone_numbers,
            email_addresses = EXCLUDED.email_addresses,
            is_complete = EXCLUDED.is_complete,
            completeness_score = EXCLUDED.completeness_score,
            missing_fields = EXCLUDED.missing_fields,
            b24_url = EXCLUDED.b24_url,
            updated_at = NOW();
        """
        comp_data = [
            (
                c["company_id"], c["title"], c["company_type"], c["created_by_id"],
                c["created_by_name"], c["assigned_by_id"], c["date_create"],
                c["has_contact"], c["has_phone"], c["has_email"], c["has_wechat"],
                c["has_comment"], c["comment_text"], json.dumps(c["phone_numbers"]),
                json.dumps(c["email_addresses"]), c["is_complete"], c["completeness_score"],
                json.dumps(c["missing_fields"]), c["b24_url"]
            )
            for c in companies
        ]
        execute_values(cur, comp_query, comp_data)
        print(f"  Успешно обновлено компаний в DWH: {len(companies)}")

    conn.commit()
    cur.close()
    conn.close()
    print("  Все транзакции зафиксированы успешно.")

def print_summary(tasks, companies):
    print("\n" + "=" * 80)
    print("📊 СВОДНЫЙ АУДИТ ПОПОЛНЕНИЯ БАЗЫ ПОСТАВЩИКОВ И ЗАДАЧ НА ПОИСК")
    print("=" * 80)
    
    # 1. Статистика по компаниям
    print("\n--- 🏢 ПОПОЛНЕНИЕ БАЗЫ ПО СОТРУДНИКАМ ---")
    by_creator = {}
    for c in companies:
        name = c["created_by_name"]
        by_creator.setdefault(name, {"total": 0, "complete": 0, "no_wechat": 0, "no_comment": 0})
        by_creator[name]["total"] += 1
        if c["is_complete"]:
            by_creator[name]["complete"] += 1
        if not c["has_wechat"]:
            by_creator[name]["no_wechat"] += 1
        if not c["has_comment"]:
            by_creator[name]["no_comment"] += 1

    print(f"{'Сотрудник':<25} | {'Создано':<8} | {'100% Заполнено':<15} | {'Без WeChat':<12} | {'Без описания':<12}")
    print("-" * 80)
    for name, s in by_creator.items():
        comp_pct = f"{(s['complete'] / s['total'] * 100):.0f}%" if s["total"] > 0 else "0%"
        print(f"{name:<25} | {s['total']:<8} | {s['complete']} ({comp_pct}){'':<7} | {s['no_wechat']:<12} | {s['no_comment']:<12}")

    # 2. Статистика по задачам
    print("\n--- 🎯 ЗАДАЧИ НА ПОИСК (ГРУППА 14) ---")
    by_resp = {}
    for t in tasks:
        name = t["responsible_name"]
        by_resp.setdefault(name, {"total": 0, "closed": 0, "with_supp": 0, "without_supp": 0})
        by_resp[name]["total"] += 1
        if t["status"] == 5:
            by_resp[name]["closed"] += 1
            if t["has_supplier_attached"]:
                by_resp[name]["with_supp"] += 1
            else:
                by_resp[name]["without_supp"] += 1

    print(f"{'Ответственный':<25} | {'Всего задач':<12} | {'Завершено':<10} | {'С поставщиком':<14} | {'БЕЗ ПОСТАВЩИКА ⚠️':<18}")
    print("-" * 80)
    for name, s in by_resp.items():
        print(f"{name:<25} | {s['total']:<12} | {s['closed']:<10} | {s['with_supp']:<14} | {s['without_supp']:<18}")

    # 3. Детализация задач без поставщиков
    without_supp_tasks = [t for t in tasks if t["status"] == 5 and not t["has_supplier_attached"]]
    if without_supp_tasks:
        print(f"\n⚠️ СПИСОК ЗАВЕРШЕННЫХ ЗАДАЧ БЕЗ ПРИВЯЗКИ ПОСТАВЩИКА ({len(without_supp_tasks)} шт.):")
        for t in without_supp_tasks[:10]:
            print(f"  • Задача #{t['task_id']}: {t['title'][:60]} | {t['responsible_name']} | Ссылка: {t['b24_url']}")
        if len(without_supp_tasks) > 10:
            print(f"  ... и еще {len(without_supp_tasks) - 10} задач.")
    else:
        print("\n✅ Все завершенные задачи имеют привязанных поставщиков!")

def main():
    parser = argparse.ArgumentParser(description="Sync Supplier Tasks & Companies from Bitrix24 to PostgreSQL DWH")
    parser.add_argument("--dry-run", action="store_true", help="Run without modifying database, print report to console")
    parser.add_argument("--days", type=int, default=14, help="Number of days to sync (default: 14)")
    parser.add_argument("--full", action="store_true", help="Run full historical sync without date filter")
    args = parser.parse_args()

    since_date = None
    if not args.full:
        since_date = datetime.datetime.now() - datetime.timedelta(days=args.days)

    print("=== ЗАПУСК СИНХРОНИЗАЦИИ ПОСТАВЩИКОВ И ЗАДАЧ СНАБЖЕНИЯ ===")
    print(f"Режим: {'DRY-RUN (Только чтение)' if args.dry_run else 'БОЕВОЙ (Запись в DWH)'}")
    since_str = since_date.strftime("%Y-%m-%d") if since_date else "All"
    period_str = "Вся история (--full)" if args.full else f"Последние {args.days} дней (с {since_str})"
    print(f"Период: {period_str}")

    tasks = fetch_search_tasks(since_date)
    companies = fetch_supplier_companies(since_date)

    print_summary(tasks, companies)

    if not args.dry_run:
        upsert_to_dwh(tasks, companies)
    else:
        print("\n[DRY-RUN] Изменения не сохранены в базу данных (для записи запустите без --dry-run).")

if __name__ == "__main__":
    main()
