import os
import sys
import datetime

# Добавляем путь к каноническим скриптам
sys.path.insert(0, os.path.abspath(r"C:\Codex\projects\1c_odata\scripts"))

from process_b24_inbound_leads import (
    process_single_lead,
    USER_MISS_WANG,
    USER_LIYAN_WANG,
    USER_LI_YUNAN,
    call_b24
)

def main():
    dry_run = "--dry-run" in sys.argv
    print(f"=== БЫСТРЫЙ ПАКЕТНЫЙ ЗАПУСК ОБРАБОТКИ ЛИДОВ (Режим: {'DRY-RUN' if dry_run else 'БОЕВОЙ'}) ===")
    
    # План распределения 7 задач между 3 менеджерами (2 - 2 - 3) со сроком до пятницы (deadline_tomorrow=True)
    plan = [
        # Miss Wang (ID: 30) - 2 задачи
        {"lead_id": 19236, "target_act_id": None, "resp_id": USER_MISS_WANG, "no_convert": False, "label": "Лид 19236 (Gemu)"},
        {"lead_id": 19222, "target_act_id": 54056, "resp_id": USER_MISS_WANG, "no_convert": True, "label": "Лид 19222 (Письмо 1 - Endress+Hauser & Baumer)"},
        
        # Liyan Wang (ID: 44) - 2 задачи
        {"lead_id": 19222, "target_act_id": 54058, "resp_id": USER_LIYAN_WANG, "no_convert": True, "label": "Лид 19222 (Письмо 2 - Lenze мотор-редукторы)"},
        {"lead_id": 19216, "target_act_id": None, "resp_id": USER_LIYAN_WANG, "no_convert": False, "label": "Лид 19216 (Редукторы Thyssenkrupp & B3SH)"},
        
        # Юйнань Ли (ID: 84) - 3 задачи
        {"lead_id": 19222, "target_act_id": 54060, "resp_id": USER_LI_YUNAN, "no_convert": False, "label": "Лид 19222 (Письмо 3 - Клапаны RUF)"},
        {"lead_id": 19214, "target_act_id": None, "resp_id": USER_LI_YUNAN, "no_convert": False, "label": "Лид 19214 (Flender муфты)"},
        {"lead_id": 19130, "target_act_id": None, "resp_id": USER_LI_YUNAN, "no_convert": False, "label": "Лид 19130 (ПЗ Машиностроитель, печь)"},
    ]

    results = []
    for item in plan:
        print(f"\n---> Запуск: {item['label']} | Ответственный: {item['resp_id']}")
        res = process_single_lead(
            lead_id=item["lead_id"],
            dry_run=dry_run,
            deadline_tomorrow=True,  # Дедлайн: пятница 18:00
            responsible_id=item["resp_id"],
            force_rfq=True,          # Прямое указание пользователя на создание Сделки и Задачи
            target_act_id=item.get("target_act_id"),
            no_convert=item.get("no_convert", False)
        )
        results.append({"item": item, "result": res})

    print("\n" + "="*75)
    print(">>> ИТОГИ ПАКЕТНОЙ ОБРАБОТКИ:")
    for r in results:
        it = r["item"]
        res = r["result"]
        deal_id = res.get("deal_id") if isinstance(res, dict) else None
        task_id = res.get("task_id") if isinstance(res, dict) else None
        print(f"- {it['label']} (Менеджер {it['resp_id']}): Сделка #{deal_id}, Задача #{task_id}")

if __name__ == "__main__":
    main()
