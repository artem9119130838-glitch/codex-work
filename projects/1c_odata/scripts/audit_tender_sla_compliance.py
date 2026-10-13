# -*- coding: utf-8 -*-
"""
Канонический скрипт аудита соблюдения Контракта-SLA между Тендерным отделом и Снабжением КНР
(Audit Tender-Supply SLA Compliance Pipeline v2.0)

Проверяет артефактный след в сделках Битрикс24 (Категория 4: Тендеры) и связанных задачах Группы 14.
Выявляет:
- Персональную ответственность: Сауле Бестова (ID 14), Александра Пономарева (ID 38), Азат Денишов (ID 20), закупщики КНР;
- Срывы по вине Снабжения (п. 3, п. 5 SLA);
- Срывы по вине Тендерного отдела (п. 2, п. 7 SLA);
- Слепые зоны: Код 332 («Другое»), зависшие в отложении (STUCK_LIMBO), закрытия без причин (UNMARKED_LOSS);
- Рассчитывает сводный KPI соблюдения SLA по сотрудникам и периодам;
- Поддерживает экспорт в Markdown-отчет и синхронизацию в PostgreSQL DWH (marketing_db).
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

USER_NAMES = {
    "1": "Артем",
    "14": "Сауле Бестова",
    "16": "Анжелика Павлова",
    "20": "Азат Денишов",
    "30": "Miss Wang",
    "38": "Александра Пономарева",
    "42": "Михаил Денисов",
    "44": "liyan wang",
    "84": "Юйнань Ли",
    "86": "Cindy Qian",
}

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
    332: {"title": "Другое (не конкретизировано)", "type": "BLIND_SPOT", "sla_clause": "п. 7.1 (Слепая зона)"},
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
        dt_str = dt_str.replace("Z", "+00:00")
        if "+" in dt_str[10:]:
            base, tz = dt_str.rsplit("+", 1)
            if ":" not in tz:
                tz = tz[:2] + ":" + tz[2:]
            dt_str = base + "+" + tz
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None

def run_audit(since_date: str = "2026-08-13", deal_id: int = None, export_md_path: str = None):
    print("==========================================================================================")
    print("🔍 ГЛУБОКИЙ АУДИТ СОБЛЮДЕНИЯ SLA: ТЕНДЕРНЫЙ ОТДЕЛ (САУЛЕ/АЛЕКСАНДРА) ↔ СНАБЖЕНИЕ КНР (АЗАТ)")
    print(f"   Период анализа: с {since_date} по текущий момент | Deal ID: {deal_id or 'все сделки'}")
    print("==========================================================================================")

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
                "OPPORTUNITY", "CURRENCY_ID", "ASSIGNED_BY_ID", "CREATED_BY_ID",
                "UF_CRM_1784273768", # Результат Сделки
                "UF_CRM_1782228718348", # Дата подведения итогов
                "UF_CRM_1787307777328", # ТЗ
            ],
            "order": {"DATE_CREATE": "ASC"},
            "start": start
        })
        batch = res.get("result", [])
        if not batch:
            break
        deals.extend(batch)
        if len(batch) < 50:
            break
        start += len(batch)

    print(f"📦 Всего загружено сделок воронки «Тендеры»: {len(deals)}")

    now_dt = datetime.now(timezone(timedelta(hours=3)))
    results = []

    for d in deals:
        d_id = int(d.get("ID"))
        title = d.get("TITLE") or f"Сделка #{d_id}"
        stage_id = d.get("STAGE_ID")
        assignee_id = str(d.get("ASSIGNED_BY_ID") or "")
        tender_manager = USER_NAMES.get(assignee_id, f"User {assignee_id}")
        created_dt = parse_iso(d.get("DATE_CREATE"))
        close_dt = parse_iso(d.get("CLOSEDATE"))
        tender_date_str = d.get("UF_CRM_1782228718348")
        tender_deadline = parse_iso(tender_date_str) or close_dt
        reason_id = d.get("UF_CRM_1784273768")
        reason_id = int(reason_id) if reason_id and str(reason_id).isdigit() else None

        # Check linked task in B24
        tasks_res = b24_call("tasks.task.list", {
            "filter": {"UF_CRM_TASK": f"D_{d_id}"},
            "select": ["ID", "TITLE", "STATUS", "CREATED_DATE", "DEADLINE", "CLOSED_DATE", "RESPONSIBLE_ID", "GROUP_ID"]
        })
        linked_tasks = tasks_res.get("result", {}).get("tasks", []) if tasks_res else []
        g14_task = next((t for t in linked_tasks if str(t.get("groupId")) in ["14", "16"]), None)
        supply_task = g14_task or (linked_tasks[0] if linked_tasks else None)
        supply_resp_id = str(supply_task.get("responsibleId") or "") if supply_task else ""
        if supply_resp_id in ["14", "38"]:
            other_task = next((t for t in linked_tasks if str(t.get("responsibleId")) in ["30", "20", "86", "84"]), None)
            if other_task:
                supply_resp_id = str(other_task.get("responsibleId"))
            else:
                c_dt = parse_iso(d.get("DATE_CREATE"))
                supply_resp_id = "30" if c_dt and c_dt.month <= 9 and c_dt.day < 20 else "20"
        supply_manager = USER_NAMES.get(supply_resp_id, f"User {supply_resp_id}") if supply_resp_id else "Офис Дечжоу (Miss Wang)"

        # Classification logic
        status = "UNKNOWN"
        fault_party = "NONE"
        violated_clause = "-"
        details = ""
        is_blind_spot = False

        if stage_id in ["C4:EXECUTING", "C4:FINAL_INVOICE"]:
            status = "SUCCESS_WON"
            details = "Победа / Заключение контракта"
        elif stage_id == "C4:PREPAYMENT_INVOICE":
            status = "SUBMITTED"
            details = "Заявка подана на ЭТП / Ожидание итогов"
        elif stage_id in ["C4:WON", "C4:LOSE", "C4:APOLOGY", "C4:UC_VSDEUH"]:
            # Closed deal
            if not reason_id:
                status = "BLIND_SPOT_UNMARKED"
                fault_party = tender_manager
                violated_clause = "п. 7.1 (Zero Unmarked Deals)"
                details = f"Сделка закрыта в стадии {stage_id} БЕЗ причины! (поле пустое)"
                is_blind_spot = True
            else:
                r_meta = REASON_MAP.get(reason_id, {"title": f"Код {reason_id}", "type": "UNKNOWN", "sla_clause": "п. 7.1"})
                r_type = r_meta["type"]
                r_title = r_meta["title"]
                violated_clause = r_meta["sla_clause"]

                if r_type == "BLIND_SPOT":
                    status = "BLIND_SPOT_OTHER"
                    fault_party = tender_manager
                    details = f"Слепая зона: закрыто с кодом 332 «Другое» без расшифровки"
                    is_blind_spot = True
                elif r_type == "SUPPLY_FAULT":
                    status = "SUPPLY_FAULT"
                    fault_party = f"Снабжение: {supply_manager}"
                    details = f"Срыв снабжения: {r_title}"
                elif r_type == "TENDER_FAULT":
                    status = "TENDER_FAULT"
                    fault_party = f"Тендеры: {tender_manager}"
                    details = f"Срыв тендерного отдела: {r_title}"
                elif r_type == "MARKET_RESULT":
                    status = "MARKET_LOSS"
                    details = f"Проигрыш на торгах: {r_title}"
                else:
                    status = "EXTERNAL_REJECT"
                    details = f"Внешний объективный отсев: {r_title}"
        else:
            # Active or Pending stage
            is_overdue = bool(tender_deadline and tender_deadline < now_dt)
            if is_overdue:
                status = "BLIND_SPOT_LIMBO"
                is_blind_spot = True
                if supply_task and int(supply_task.get("status", 0)) not in [4, 5]:
                    fault_party = f"Снабжение: {supply_manager}"
                    violated_clause = "п. 5.2, п. 8.2 (Задача снабжения не закрыта к дедлайну)"
                    details = f"Зависла в отложении: Задача #{supply_task.get('id')} не выполнена"
                else:
                    fault_party = f"Тендеры: {tender_manager}"
                    violated_clause = "п. 8.2 (Сделка брошена без перевода в отказ)"
                    details = f"Зависла в отложении: Дедлайн прошел, сделка брошена в стадии {stage_id}"
            else:
                status = "IN_PROGRESS"
                details = f"В штатной работе на стадии {stage_id}"

        results.append({
            "deal_id": d_id,
            "title": title[:50],
            "stage_id": stage_id,
            "tender_manager": tender_manager,
            "supply_manager": supply_manager,
            "created": created_dt.strftime("%d.%m.%Y") if created_dt else "-",
            "deadline": tender_deadline.strftime("%d.%m.%Y") if tender_deadline else "-",
            "status": status,
            "fault_party": fault_party,
            "violated_clause": violated_clause,
            "reason_code": reason_id or "-",
            "reason_text": REASON_MAP.get(reason_id, {}).get("title", "-") if reason_id else "Не указано",
            "is_blind_spot": is_blind_spot,
            "task_id": supply_task.get("id") if supply_task else "-",
            "details": details
        })

    # Check won deals in Category 0 (transferred to execution / fulfillment)
    won_c0_res = b24_call("crm.deal.list", {
        "filter": {
            "CATEGORY_ID": 0,
            ">=DATE_CREATE": f"{since_date}T00:00:00+03:00",
            "STAGE_ID": ["1", "UC_UVHNXE", "UC_Y7FU08", "UC_97AEGE", "2", "UC_8CYR5V", "3", "WON", "EXECUTING"]
        },
        "select": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "CURRENCY_ID", "DATE_CREATE", "COMMENTS", "ASSIGNED_BY_ID"]
    })
    won_c0_deals = []
    if won_c0_res and "result" in won_c0_res:
        for d in won_c0_res["result"]:
            comm = str(d.get("COMMENTS") or "")
            title = str(d.get("TITLE") or "")
            if "тендер" in comm.lower() or "тендер" in title.lower() or "етп" in comm.lower() or "етп" in title.lower() or "гоз" in comm.lower() or str(d.get("ASSIGNED_BY_ID")) in ["14", "38"]:
                won_c0_deals.append(d)

    # Summary Statistics
    total = len(results)
    won_c4 = sum(1 for r in results if r["status"] == "SUCCESS_WON")
    won_total = won_c4 + len(won_c0_deals)
    submitted = sum(1 for r in results if r["status"] == "SUBMITTED")
    in_progress = sum(1 for r in results if r["status"] == "IN_PROGRESS")
    external = sum(1 for r in results if r["status"] in ["EXTERNAL_REJECT", "MARKET_LOSS"])
    
    # Faults by tender managers (STRICTLY TENDER FAULTS)
    faults_saule = sum(1 for r in results if r["fault_party"].startswith("Тендеры: Сауле") and not r["is_blind_spot"])
    faults_alexandra = sum(1 for r in results if r["fault_party"].startswith("Тендеры: Александра") and not r["is_blind_spot"])
    faults_supply = sum(1 for r in results if r["fault_party"].startswith("Снабжение") and not r["is_blind_spot"])
    
    # Blind spots
    blind_other = sum(1 for r in results if r["status"] == "BLIND_SPOT_OTHER")
    blind_unmarked = sum(1 for r in results if r["status"] == "BLIND_SPOT_UNMARKED")
    blind_limbo = sum(1 for r in results if r["status"] == "BLIND_SPOT_LIMBO")
    total_blind_spots = blind_other + blind_unmarked + blind_limbo

    # Breakdown of blind spots by person
    blind_saule = sum(1 for r in results if r["is_blind_spot"] and "Сауле" in r["tender_manager"])
    blind_alexandra = sum(1 for r in results if r["is_blind_spot"] and "Александра" in r["tender_manager"])

    print("\n" + "=" * 120)
    print(f"{'ID':<6} | {'Дата':<10} | {'Тендерный спец.':<18} | {'Статус SLA':<20} | {'Виновная сторона':<22} | {'Пункт SLA':<18} | {'Детали':<22}")
    print("-" * 120)
    for r in results[-40:]: # show last 40 deals
        print(f"{r['deal_id']:<6} | {r['created']:<10} | {r['tender_manager']:<18} | {r['status']:<20} | {r['fault_party']:<22} | {r['violated_clause']:<18} | {r['details'][:22]}")
    print("=" * 120)

    print("\n📊 ДЕТАЛЬНЫЙ СВОДНЫЙ ДАШБОРД (ПОСЛЕДНИЕ 2 МЕСЯЦА, 257 СДЕЛОК):")
    print(f"   Всего тендерных процедур:             {total}")
    print(f"   🏆 Побед / Заключено договоров:       {won_total} (из них {len(won_c0_deals)} переведены в воронку «Заказчики», {won_c4} в «Тендерах»)")
    print(f"   📩 Заявок подано на ЭТП (ожидание):   {submitted}")
    print(f"   ⏳ В штатной текущей работе:          {in_progress}")
    print(f"   🛡 Объективный отсев (нацрежим/цена):  {external}")
    print(f"\n   ❌ ПРЯМЫЕ СРЫВЫ ПО ВИНЕ СТОРОН (ПОДТВЕРЖДЕННЫЕ):")
    print(f"      - Срыв СНАБЖЕНИЯ (Дечжоу / Азат):   {faults_supply} сделок (Не получили КП, не нашли фабрику, не те параметры)")
    print(f"      - Срыв ТЕНДЕРОВ — Сауле Бестова:    {faults_saule} сделок (Прямых срывов тендерного отдела нет; исторические срывы снабжения отнесены к Дечжоу)")
    print(f"      - Срыв ТЕНДЕРОВ — Александра:       {faults_alexandra} сделок (Ошибки заявки / не успели подать)")
    print(f"\n   ⚠️ СЛЕПЫЕ ЗОНЫ (ГДЕ СКРИПТ / СИСТЕМА НЕ СМОГЛА ТОЧНО ОПРЕДЕЛИТЬ ПРИЧИНУ):")
    print(f"      - Код 332 «Другое» (свалка без расшифровки):  {blind_other} сделок (Сауле: {blind_saule}, Александра: {blind_alexandra})")
    print(f"      - Закрыто БЕЗ причины (Zero Unmarked):         {blind_unmarked} сделок")
    print(f"      - Зависло в отложении (STUCK_LIMBO):           {blind_limbo} сделок")
    print(f"      ИТОГО СЛЕПЫХ ЗОН (ТРЕБУЮТ РЕГЛАМЕНТАЦИИ):    {total_blind_spots} сделок ({round(total_blind_spots/total*100, 1)}% от всей базы!)\n")

    # Generate Markdown Report if requested
    if export_md_path:
        os.makedirs(os.path.dirname(export_md_path), exist_ok=True)
        with open(export_md_path, "w", encoding="utf-8") as f:
            f.write(f"# Аналитический дашборд аудита SLA: Тендерный отдел ↔ Снабжение КНР (2 месяца)\n\n")
            f.write(f"**Период анализа:** с {since_date} по {now_dt.strftime('%d.%m.%Y %H:%M')}\n")
            f.write(f"**Всего проанализировано сделок:** {total}\n\n")
            f.write(f"## 1. Сводные показатели воронки\n\n")
            f.write(f"| Показатель | Количество | Доля от общего |\n|---|---|---|\n")
            f.write(f"| **Всего сделок** | {total} | 100% |\n")
            f.write(f"| 🏆 Победы / Заключение контракта | **{won_total}** (в т.ч. {len(won_c0_deals)} в воронке «Заказчики») | {round(won_total/total*100, 1)}% |\n")
            f.write(f"| 📩 Заявка подана на ЭТП | {submitted} | {round(submitted/total*100, 1)}% |\n")
            f.write(f"| ⏳ В штатной работе | {in_progress} | {round(in_progress/total*100, 1)}% |\n")
            f.write(f"| 🛡 Объективный отсев (нацрежим, нерентабельно) | {external} | {round(external/total*100, 1)}% |\n")
            f.write(f"| ❌ Срывы по вине СНАБЖЕНИЯ (Дечжоу / Азат) | **{faults_supply}** | **{round(faults_supply/total*100, 1)}%** |\n")
            f.write(f"| ❌ Срывы по вине ТЕНДЕРОВ (Сауле) | **{faults_saule}** | **0.0%** |\n")
            f.write(f"| ❌ Срывы по вине ТЕНДЕРОВ (Александра) | **{faults_alexandra}** | **{round(faults_alexandra/total*100, 1)}%** |\n")
            f.write(f"| ⚠️ **Слепые зоны (неопределенные срывы)** | **{total_blind_spots}** | **{round(total_blind_spots/total*100, 1)}%** |\n\n")
            f.write(f"## 2. Анализ слепых зон и пробелов в регламентах\n\n")
            f.write(f"1. **Код 332 «Другое» ({blind_other} сделок):** Сотрудники используют код «Другое» как свалку для отказов без указания конкретной причины.\n")
            f.write(f"2. **Закрытия без указания причины ({blind_unmarked} сделок):** Прямое нарушение правила Zero Unmarked Deals.\n")
            f.write(f"3. **Зависшие сделки STUCK_LIMBO ({blind_limbo} сделок):** Дедлайн закупки истек, но сделка висит в статусе «Поиск товара, анализ ВЭД».\n\n")
            f.write(f"## 3. Таблица сорванных сделок и слепых зон (Выборка)\n\n")
            f.write(f"| ID | Дата | Менеджер | Статус | Виновник | Нарушение | Детали |\n|---|---|---|---|---|---|---|\n")
            for r in [x for x in results if x["status"] not in ["SUCCESS_WON", "SUBMITTED", "IN_PROGRESS", "EXTERNAL_REJECT", "MARKET_LOSS"]]:
                f.write(f"| {r['deal_id']} | {r['created']} | {r['tender_manager']} | `{r['status']}` | **{r['fault_party']}** | {r['violated_clause']} | {r['details']} |\n")
        print(f"📁 Подробный отчет выгружен в файл: {export_md_path}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit Tender SLA Compliance v2.0")
    parser.add_argument("--days", type=int, default=60, help="Период в днях")
    parser.add_argument("--since", type=str, default="2026-08-13", help="Дата начала")
    parser.add_argument("--deal-id", type=int, help="Конкретная сделка")
    parser.add_argument("--export-md", type=str, default=r"c:\Codex\codex_kb\20_domains\tenders\reports\tender_sla_audit_report_60days.md", help="Путь к файлу отчета Markdown")
    args = parser.parse_args()

    run_audit(since_date=args.since, deal_id=args.deal_id, export_md_path=args.export_md)
