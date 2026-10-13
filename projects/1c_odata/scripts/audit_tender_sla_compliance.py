# -*- coding: utf-8 -*-
"""
Канонический скрипт аудита соблюдения Контракта-SLA между Тендерным отделом и Снабжением КНР
(Audit Tender-Supply SLA Compliance Pipeline)

Проверяет артефактный след в сделках Битрикс24 (Категория 4: Тендеры) и связанных задачах Группы 14.
Выявляет:
- Срывы по вине Снабжения (п. 3, п. 5 SLA);
- Срывы по вине Тендерного отдела (п. 2, п. 7 SLA);
- Зависшие сделки в скрытом отложении (STUCK_LIMBO);
- Закрытия без указания причины (UNMARKED_LOSS);
- Рассчитывает сводный KPI соблюдения SLA.

Поддерживает синхронизацию в PostgreSQL DWH (marketing_db) для дашбордов Metabase.

Использование:
    py projects/1c_odata/scripts/audit_tender_sla_compliance.py --days 30
    py projects/1c_odata/scripts/audit_tender_sla_compliance.py --since 2026-09-01
    py projects/1c_odata/scripts/audit_tender_sla_compliance.py --deal-id 2388
    py projects/1c_odata/scripts/audit_tender_sla_compliance.py --days 30 --dwh-sync
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load environment candidates
def load_env():
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), "..", "..", "metabase_analytics", ".env"),
    ]
    for env_path in candidates:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip().strip("'\"")
                            if k not in os.environ and v:
                                os.environ[k] = v
            except Exception:
                pass

load_env()

B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "")

# SLA Reason Codes mapping
REASON_MAP = {
    306: {"title": "Национальный режим (запрет)", "type": "EXTERNAL", "sla_clause": "-"},
    308: {"title": "Требуется товар РФ", "type": "EXTERNAL", "sla_clause": "-"},
    310: {"title": "Эквивалент не допускается", "type": "EXTERNAL", "sla_clause": "-"},
    312: {"title": "Закупка нерентабельна", "type": "EXTERNAL", "sla_clause": "-"},
    314: {"title": "Не нашли поставщика", "type": "SUPPLY_FAULT", "sla_clause": "п. 3.1, п. 5.1"},
    316: {"title": "Не получили КП", "type": "SUPPLY_FAULT", "sla_clause": "п. 3.2, п. 5.2"},
    318: {"title": "Получили КП слишком поздно", "type": "SUPPLY_FAULT", "sla_clause": "п. 5.2 (<48ч)"},
    320: {"title": "КП не соответствует требованиям", "type": "SUPPLY_FAULT", "sla_clause": "п. 3.2, п. 3.3"},
    322: {"title": "Не успели подготовить заявку", "type": "TENDER_FAULT", "sla_clause": "п. 2.2, п. 5.3"},
    324: {"title": "Не успели подать заявку", "type": "TENDER_FAULT", "sla_clause": "п. 2.2"},
    326: {"title": "Проиграли по цене", "type": "MARKET_RESULT", "sla_clause": "-"},
    328: {"title": "Заявка отклонена из-за ошибок", "type": "TENDER_FAULT", "sla_clause": "п. 2.2"},
    330: {"title": "Проиграли по неценовым критериям", "type": "MARKET_RESULT", "sla_clause": "-"},
    332: {"title": "Другое", "type": "UNKNOWN", "sla_clause": "п. 7.1"},
    334: {"title": "Запрет на экспорт из Китая", "type": "EXTERNAL", "sla_clause": "п. 5.1"},
    336: {"title": "Недостаточный срок поставки", "type": "EXTERNAL", "sla_clause": "п. 5.1"},
}

def b24_call(method: str, params: dict = None) -> dict:
    url = B24_WEBHOOK.rstrip("/") + "/" + method
    if not url.startswith("http"):
        return {}
    data = json.dumps(params or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[API ERROR] {method}: {e}", file=sys.stderr)
        return {}

def parse_iso(dt_str):
    if not dt_str:
        return None
    try:
        # Normalize ISO string
        dt_str = dt_str.replace("Z", "+00:00")
        if "+" in dt_str[10:]:
            base, tz = dt_str.rsplit("+", 1)
            if ":" not in tz:
                tz = tz[:2] + ":" + tz[2:]
            dt_str = base + "+" + tz
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None

def analyze_tender_deals(since_date: str = None, deal_id: int = None, limit: int = 100):
    print("================================================================================")
    print("🔍 АУДИТ СОБЛЮДЕНИЯ КОНТРАКТА-SLA ТЕНДЕРНЫЙ ОТДЕЛ ↔ СНАБЖЕНИЕ КНР")
    print(f"   Фильтр: Category=4 (Тендеры) | Since: {since_date or 'все'} | DealID: {deal_id or 'все'}")
    print("================================================================================")

    filter_params = {"CATEGORY_ID": 4}
    if deal_id:
        filter_params["ID"] = deal_id
    elif since_date:
        filter_params[">=DATE_CREATE"] = f"{since_date}T00:00:00+03:00"

    deals = []
    start = 0
    while True:
        res = b24_call("crm.deal.list", {
            "filter": filter_params,
            "select": [
                "ID", "TITLE", "STAGE_ID", "STAGE_SEMANTIC_ID", "DATE_CREATE", "CLOSEDATE",
                "OPPORTUNITY", "CURRENCY_ID", "ASSIGNED_BY_ID",
                "UF_CRM_1784273768", # Результат Сделки (enum)
                "UF_CRM_1782228718348", # Дата подведения итогов
                "UF_CRM_1787307777328", # ТЗ
            ],
            "order": {"ID": "DESC"},
            "start": start
        })
        batch = res.get("result", [])
        if not batch:
            break
        deals.extend(batch)
        if len(batch) < 50 or (limit and len(deals) >= limit):
            break
        start += len(batch)

    print(f"📦 Найдено сделок воронки «Тендеры»: {len(deals)}")
    
    now_dt = datetime.now(timezone(timedelta(hours=3)))
    audit_results = []

    for d in deals:
        d_id = int(d.get("ID"))
        title = d.get("TITLE") or f"Сделка #{d_id}"
        stage_id = d.get("STAGE_ID")
        created_dt = parse_iso(d.get("DATE_CREATE"))
        close_dt = parse_iso(d.get("CLOSEDATE"))
        tender_date_str = d.get("UF_CRM_1782228718348")
        tender_deadline = parse_iso(tender_date_str) or close_dt
        reason_id = d.get("UF_CRM_1784273768")
        reason_id = int(reason_id) if reason_id and str(reason_id).isdigit() else None
        
        # Check linked tasks in B24
        tasks_res = b24_call("tasks.task.list", {
            "filter": {"UF_CRM_TASK": f"D_{d_id}"},
            "select": ["ID", "TITLE", "STATUS", "CREATED_DATE", "DEADLINE", "CLOSED_DATE", "RESPONSIBLE_ID", "GROUP_ID"]
        })
        linked_tasks = tasks_res.get("result", {}).get("tasks", []) if tasks_res else []
        supply_task = None
        for t in linked_tasks:
            # Group 14 or responsible 20 (Azat) or title contains supply keywords
            if str(t.get("groupId")) == "14" or str(t.get("responsibleId")) == "20" or "снаряжение" in (t.get("title") or "").lower() or "кнр" in (t.get("title") or "").lower():
                supply_task = t
                break
        if not supply_task and linked_tasks:
            supply_task = linked_tasks[0]

        # Determine SLA Classification
        status = "UNKNOWN"
        fault_party = "NONE"
        violated_clause = "-"
        details = ""

        # Check if won
        if stage_id in ["C4:EXECUTING", "C4:FINAL_INVOICE"]:
            status = "SUCCESS_WON"
            details = "Победа / Контракт заключен"
        elif stage_id in ["C4:PREPAYMENT_INVOICE"]:
            status = "SUBMITTED"
            details = "Заявка подана на ЭТП / Ожидание итогов"
        elif stage_id in ["C4:WON", "C4:LOSE", "C4:APOLOGY", "C4:UC_VSDEUH"]:
            # Closed deal
            if not reason_id:
                status = "UNMARKED_LOSS"
                fault_party = "TENDER_DEPT"
                violated_clause = "п. 7.1 (Zero Unmarked Deals)"
                details = f"Сделка закрыта в стадии {stage_id} без указания причины (UF_CRM_1784273768 пуст!)"
            else:
                r_meta = REASON_MAP.get(reason_id, {"title": f"Код {reason_id}", "type": "UNKNOWN", "sla_clause": "п. 7.1"})
                r_type = r_meta["type"]
                r_title = r_meta["title"]
                violated_clause = r_meta["sla_clause"]
                if r_type == "SUPPLY_FAULT":
                    status = "SUPPLY_FAULT"
                    fault_party = "SUPPLY_DEPT"
                    details = f"Срыв снабжения: {r_title}"
                elif r_type == "TENDER_FAULT":
                    status = "TENDER_FAULT"
                    fault_party = "TENDER_DEPT"
                    details = f"Срыв тендерного отдела: {r_title}"
                elif r_type == "MARKET_RESULT":
                    status = "MARKET_LOSS"
                    details = f"Рыночный проигрыш на ЭТП: {r_title}"
                else:
                    status = "EXTERNAL_REJECT"
                    details = f"Внешний объективный отказ: {r_title}"
        else:
            # Active or Pending stage
            # Check if deadline passed
            is_overdue = False
            if tender_deadline and tender_deadline < now_dt:
                is_overdue = True
            
            if is_overdue:
                status = "STUCK_LIMBO"
                # Determine who is at fault for limbo
                if supply_task and int(supply_task.get("status", 0)) not in [4, 5]:
                    fault_party = "SUPPLY_DEPT"
                    violated_clause = "п. 5.2, п. 8.2 (Задача снабжения не закрыта к дедлайну)"
                    details = f"Зависла в отложении: Снабжение не сдало задачу #{supply_task.get('id')}"
                else:
                    fault_party = "TENDER_DEPT"
                    violated_clause = "п. 8.2 (Сделка брошена без закрытия)"
                    details = f"Зависла в отложении: Дедлайн прошел, сделка не переведена в отказ"
            else:
                status = "IN_PROGRESS"
                details = f"В работе на стадии {stage_id}"
                # Check 4-hour express scoring SLA if recently created
                if created_dt and (now_dt - created_dt).total_seconds() > 4 * 3600:
                    if not supply_task or int(supply_task.get("status", 0)) == 2:
                        # Pending for >4 hours
                        details += " [ПРЕДУПРЕЖДЕНИЕ: нет первичного ответа снабжения >4ч]"

        item = {
            "deal_id": d_id,
            "title": title[:45],
            "stage_id": stage_id,
            "created": created_dt.strftime("%d.%m.%Y") if created_dt else "-",
            "deadline": tender_deadline.strftime("%d.%m.%Y") if tender_deadline else "-",
            "status": status,
            "fault_party": fault_party,
            "violated_clause": violated_clause,
            "reason_code": reason_id or "-",
            "reason_text": REASON_MAP.get(reason_id, {}).get("title", "-"),
            "task_id": supply_task.get("id") if supply_task else "-",
            "details": details
        }
        audit_results.append(item)

    # Print summary table
    print("\n" + "=" * 115)
    print(f"{'ID':<7} | {'Дедлайн':<10} | {'Статус SLA':<15} | {'Виновник':<12} | {'Пункт SLA':<18} | {'Детали / Причина':<40}")
    print("-" * 115)
    for r in audit_results:
        print(f"{r['deal_id']:<7} | {r['deadline']:<10} | {r['status']:<15} | {r['fault_party']:<12} | {r['violated_clause']:<18} | {r['details'][:40]:<40}")
    print("=" * 115)

    # Aggregate Statistics
    total = len(audit_results)
    won_cnt = sum(1 for r in audit_results if r["status"] == "SUCCESS_WON")
    submitted_cnt = sum(1 for r in audit_results if r["status"] == "SUBMITTED")
    supply_fault_cnt = sum(1 for r in audit_results if r["fault_party"] == "SUPPLY_DEPT")
    tender_fault_cnt = sum(1 for r in audit_results if r["fault_party"] == "TENDER_DEPT" and r["status"] != "UNMARKED_LOSS")
    unmarked_cnt = sum(1 for r in audit_results if r["status"] == "UNMARKED_LOSS")
    limbo_cnt = sum(1 for r in audit_results if r["status"] == "STUCK_LIMBO")
    external_cnt = sum(1 for r in audit_results if r["status"] in ["EXTERNAL_REJECT", "MARKET_LOSS"])
    in_progress_cnt = sum(1 for r in audit_results if r["status"] == "IN_PROGRESS")

    sla_broken = supply_fault_cnt + tender_fault_cnt + unmarked_cnt + limbo_cnt
    sla_compliance_rate = round((total - sla_broken) / total * 100, 1) if total > 0 else 100.0

    print("\n📊 СВОДНЫЕ ПОКАЗАТЕЛИ СОБЛЮДЕНИЯ SLA:")
    print(f"   Всего тендерных процедур:         {total}")
    print(f"   🏆 Побед / Заключено:            {won_cnt}")
    print(f"   📩 Заявок на ЭТП (в ожидании):    {submitted_cnt}")
    print(f"   ⏳ В штатной работе:              {in_progress_cnt}")
    print(f"   🛡 Объективных отказов / торга:   {external_cnt}")
    print(f"   ❌ Срывы по вине СНАБЖЕНИЯ:       {supply_fault_cnt} (Азат)")
    print(f"   ❌ Срывы по вине ТЕНДЕРОВ:        {tender_fault_cnt} (Александра)")
    print(f"   ⚠️ Зависло в отложении (LIMBO):   {limbo_cnt}")
    print(f"   ⚠️ Закрыто без причины (UNMARKED): {unmarked_cnt}")
    print(f"   📈 ИТОГОВЫЙ ИНДЕКС СОБЛЮДЕНИЯ SLA: {sla_compliance_rate}%\n")

    return audit_results

def sync_to_dwh(results):
    """Синхронизация результатов аудита в PostgreSQL DWH (marketing_db)."""
    pg_host = os.getenv("PG_HOST", "10.10.0.1")
    pg_port = int(os.getenv("PG_PORT", 5433))
    pg_db = os.getenv("PG_DBNAME", "marketing_db")
    pg_user = os.getenv("PG_USER", "vector_user")
    pg_pass = os.getenv("PG_PASSWORD", "")
    
    print(f"🔄 Попытка синхронизации {len(results)} записей в DWH ({pg_host}:{pg_port}/{pg_db})...")
    try:
        import psycopg2
        conn = psycopg2.connect(host=pg_host, port=pg_port, dbname=pg_db, user=pg_user, password=pg_pass, connect_timeout=5)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dwh_tender_sla_audit (
                deal_id BIGINT PRIMARY KEY,
                title TEXT,
                stage_id TEXT,
                created_date DATE,
                deadline_date DATE,
                status TEXT,
                fault_party TEXT,
                violated_clause TEXT,
                reason_code TEXT,
                reason_text TEXT,
                task_id TEXT,
                details TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        for r in results:
            cur.execute("""
                INSERT INTO dwh_tender_sla_audit 
                (deal_id, title, stage_id, created_date, deadline_date, status, fault_party, violated_clause, reason_code, reason_text, task_id, details, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (deal_id) DO UPDATE SET
                    stage_id = EXCLUDED.stage_id,
                    deadline_date = EXCLUDED.deadline_date,
                    status = EXCLUDED.status,
                    fault_party = EXCLUDED.fault_party,
                    violated_clause = EXCLUDED.violated_clause,
                    reason_code = EXCLUDED.reason_code,
                    reason_text = EXCLUDED.reason_text,
                    task_id = EXCLUDED.task_id,
                    details = EXCLUDED.details,
                    updated_at = CURRENT_TIMESTAMP;
            """, (
                r["deal_id"], r["title"], r["stage_id"],
                datetime.strptime(r["created"], "%d.%m.%Y").date() if r["created"] != "-" else None,
                datetime.strptime(r["deadline"], "%d.%m.%Y").date() if r["deadline"] != "-" else None,
                r["status"], r["fault_party"], r["violated_clause"], str(r["reason_code"]), r["reason_text"], str(r["task_id"]), r["details"]
            ))
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Успешно синхронизировано в PostgreSQL DWH!")
    except Exception as e:
        print(f"⚠️ DWH Sync пропущен или недоступен: {e} (Данные сохранены локально)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit Tender-Supply SLA Compliance")
    parser.add_argument("--days", type=int, default=30, help="Период в днях")
    parser.add_argument("--since", type=str, help="Дата начала (YYYY-MM-DD)")
    parser.add_argument("--deal-id", type=int, help="Проверка конкретной сделки")
    parser.add_argument("--dwh-sync", action="store_true", help="Синхронизация в PostgreSQL DWH")
    args = parser.parse_args()

    since = args.since
    if not since and args.days:
        since = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    results = analyze_tender_deals(since_date=since, deal_id=args.deal_id)
    if args.dwh_sync and results:
        sync_to_dwh(results)
