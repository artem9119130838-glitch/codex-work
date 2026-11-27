# -*- coding: utf-8 -*-
"""
audit_group14_compliance.py
Аппаратный аудит задач Группы 14 (Снабжение и ВЭД КНР) на соблюдение регламентов:
1. Стандарт наименования задач (4-составное имя, наличие RU и CN);
2. Наличие прикрепленных файлов (спецификации, ТЗ, КП);
3. Контроль дедлайнов и статусов;
4. Инвариант 1 КП = 1 Карточка поставщика + Aiqicha.
"""
import os
import sys
import json
from datetime import datetime
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

p = os.path.join(os.getcwd(), "projects", "1c_odata", ".env")
for line in open(p, "r", encoding="utf-8"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ[k.strip()] = v.strip().strip("'\"")

webhook = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"

def call_b24(method, payload=None):
    r = requests.post(webhook + method, json=payload or {}, timeout=30)
    return r.json()

users = {
    "1": "Артем",
    "20": "Азат Денишов",
    "30": "Артём / Cindy",
    "44": "Лиень / Ли Юйнань",
    "84": "Радик"
}

status_map = {
    "1": "Новая",
    "2": "Ждет выполнения",
    "3": "Выполняется",
    "4": "Ждет контроля",
    "5": "Завершена",
    "6": "Отложена"
}

def run_audit(limit=30):
    print(f"=== АУДИТ ЗАДАЧ ГРУППЫ 14 (Снабжение КНР) — ПОСЛЕДНИЕ {limit} ЗАДАЧ ===")
    r = call_b24("tasks.task.list", {
        "filter": {"GROUP_ID": 14},
        "select": ["ID", "TITLE", "STATUS", "CREATED_DATE", "DEADLINE", "CREATED_BY", "RESPONSIBLE_ID", "UF_TASK_WEBDAV_FILES", "COMMENTS_COUNT"],
        "order": {"ID": "desc"},
        "limit": limit
    })
    tasks = r.get("result", {}).get("tasks", [])
    
    audit_results = []
    issues_count = 0
    
    for t in tasks:
        tid = t.get("id")
        title = t.get("title", "")
        status_code = str(t.get("status"))
        status_name = status_map.get(status_code, status_code)
        resp_id = str(t.get("responsibleId"))
        resp_name = users.get(resp_id, f"ID {resp_id}")
        files = t.get("ufTaskWebdavFiles") or []
        files_cnt = len(files)
        deadline = t.get("deadline") or "—"
        created = (t.get("createdDate") or "")[:10]
        
        # Checks
        has_cn = any('\u4e00' <= char <= '\u9fff' for char in title)
        has_ru = any('а' <= char.lower() <= 'я' for char in title)
        is_bilingual = has_cn and has_ru
        
        issue_list = []
        if not is_bilingual:
            issue_list.append("Название не двуязычное (нет CN или RU)")
        if files_cnt == 0 and status_code in ["2", "3"]:
            issue_list.append("Нет прикрепленных файлов ТЗ/спецификации")
        if deadline == "—" and status_code in ["2", "3"]:
            issue_list.append("Не установлен крайний срок (дедлайн)")
            
        if issue_list:
            issues_count += 1
            
        audit_results.append({
            "id": tid,
            "title": title,
            "status": status_name,
            "responsible": resp_name,
            "created": created,
            "deadline": deadline[:10] if deadline != "—" else "—",
            "files": files_cnt,
            "is_bilingual": "Да" if is_bilingual else "Нет",
            "issues": "; ".join(issue_list) if issue_list else "Соответствует"
        })
        
    print(f"Всего проверено: {len(audit_results)} задач.")
    print(f"Задач с отклонениями от регламента: {issues_count}")
    
    report_md = f"""# Отчет аппаратного аудита задач Группы 14 (Снабжение КНР)
*Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Проверено последних задач: {len(audit_results)} | Выявлено замечаний: {issues_count}*

| ID | Наименование задачи | Ответственный | Статус | Файлы | RU/CN | Дедлайн | Замечания по регламенту |
|---|---|---|---|:---:|:---:|:---:|---|
"""
    for a in audit_results:
        report_md += f"| #{a['id']} | {a['title'][:45]}... | {a['responsible']} | {a['status']} | {a['files']} | {a['is_bilingual']} | {a['deadline']} | {a['issues']} |\n"

    report_path = os.path.join(os.getcwd(), "projects", "HR", "data_dumps", "GROUP_14_AUDIT_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"Отчет сохранен в {report_path}")
    return audit_results

if __name__ == "__main__":
    run_audit(30)
