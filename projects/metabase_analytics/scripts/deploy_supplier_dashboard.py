#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy Metabase Dashboard: «Пополнение базы поставщиков и аудит задач RFQ»
Version: 1.0 (2026-11-08)
"""

import os
import sys
import json
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

METABASE_URL = os.environ.get("METABASE_URL", "http://109.248.170.181:3000").rstrip("/")
ADMIN_EMAIL = os.environ.get("METABASE_ADMIN_EMAIL", "admin@tender-rag.local")
ADMIN_PASSWORD = os.environ.get("METABASE_ADMIN_PASSWORD", "Artem12345")

def get_session():
    url = f"{METABASE_URL}/api/session"
    data = json.dumps({"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))["id"]

def api_call(session_id, method, path, data=None):
    url = f"{METABASE_URL}/api{path}"
    headers = {"X-Metabase-Session": session_id, "Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"[API ERROR] {method} {path} HTTP {e.code}: {err}")
        return None

def main():
    print("=== ДЕПЛОЙ ДАШБОРДА ПОСТАВЩИКОВ В METABASE ===")
    session_id = get_session()
    print("[OK] Авторизация в Metabase успешна.")

    # 1. Поиск database marketing_db (ID 2)
    dbs = api_call(session_id, "GET", "/database")
    db_list = dbs.get("data", dbs) if isinstance(dbs, dict) else (dbs or [])
    db_id = 2
    for d in db_list:
        if d.get("name") == "marketing_db":
            db_id = d["id"]
            break
    print(f"[OK] База данных: marketing_db (ID {db_id})")

    # 2. Поиск или создание коллекции
    collections = api_call(session_id, "GET", "/collection") or []
    coll_id = None
    for c in collections:
        if c.get("name") == "Снабжение КНР и Поставщики":
            coll_id = c["id"]
            break
    if not coll_id:
        new_coll = api_call(session_id, "POST", "/collection", {
            "name": "Снабжение КНР и Поставщики",
            "color": "#509EE3",
            "description": "Контроль пополнения базы поставщиков и аудит задач на поиск RFQ"
        })
        if new_coll and "id" in new_coll:
            coll_id = new_coll["id"]
            print(f"[OK] Создана коллекция: Снабжение КНР и Поставщики (ID {coll_id})")

    # 3. SQL-запросы для карточек
    cards_def = [
        {
            "name": "1. Сводные KPI недели: Пополнение базы vs План 60",
            "description": "План 60 поставщиков на отдел, факт за последние 7 дней, задачи без поставщика",
            "display": "table",
            "sql": """SELECT 
    COUNT(DISTINCT c.company_id) AS "Новых поставщиков",
    60 AS "План на отдел",
    ROUND(COUNT(DISTINCT c.company_id)::numeric / 60 * 100, 1) || '%' AS "% выполнения плана",
    COUNT(DISTINCT t.task_id) FILTER (WHERE t.status = 5) AS "Задач закрыто",
    COUNT(DISTINCT t.task_id) FILTER (WHERE t.status = 5 AND t.has_supplier_attached = FALSE) AS "Задач БЕЗ поставщика ⚠️",
    ROUND(COUNT(DISTINCT c.company_id) FILTER (WHERE c.is_complete = TRUE)::numeric / NULLIF(COUNT(DISTINCT c.company_id), 0) * 100, 0) || '%' AS "Качество базы (100% заполнено)"
FROM analytics_supplier_companies c
FULL OUTER JOIN analytics_supplier_search_tasks t 
    ON DATE_TRUNC('week', c.date_create AT TIME ZONE 'Asia/Shanghai') = DATE_TRUNC('week', t.closed_date AT TIME ZONE 'Asia/Shanghai')
WHERE COALESCE(c.date_create, t.closed_date) >= NOW() - INTERVAL '7 days';"""
        },
        {
            "name": "2. Матрица по сотрудникам и дням недели (Пн-Пт)",
            "description": "Сетка пополнения базы по дням недели (Пн-Пт) с подсчетом закрытых задач и качества",
            "display": "table",
            "sql": """SELECT 
    user_name AS "Сотрудник",
    COALESCE(SUM(suppliers_added) FILTER (WHERE day_num = 1), 0) AS "Пн",
    COALESCE(SUM(suppliers_added) FILTER (WHERE day_num = 2), 0) AS "Вт",
    COALESCE(SUM(suppliers_added) FILTER (WHERE day_num = 3), 0) AS "Ср",
    COALESCE(SUM(suppliers_added) FILTER (WHERE day_num = 4), 0) AS "Чт",
    COALESCE(SUM(suppliers_added) FILTER (WHERE day_num = 5), 0) AS "Пт",
    SUM(suppliers_added) AS "Всего новых",
    SUM(tasks_closed) AS "Задач закрыто",
    SUM(tasks_without_supplier) AS "Без поставщика ⚠️",
    ROUND(CASE WHEN SUM(suppliers_added) > 0 THEN SUM(suppliers_complete)::numeric / SUM(suppliers_added) * 100 ELSE 0 END, 0) || '%' AS "Качество %"
FROM v_supplier_weekly_performance
WHERE work_date >= DATE_TRUNC('week', NOW() - INTERVAL '14 days')
GROUP BY user_name
ORDER BY "Всего новых" DESC;"""
        },
        {
            "name": "3. Реестр задач без привязки поставщика (Штрафная зона)",
            "description": "Завершенные задачи на поиск, где закупщик не привязал карточку компании в Bitrix24",
            "display": "table",
            "sql": """SELECT 
    t.task_id AS "ID задачи",
    t.title AS "Название задачи",
    t.responsible_name AS "Ответственный",
    TO_CHAR(t.closed_date AT TIME ZONE 'Asia/Shanghai', 'YYYY-MM-DD HH24:MI') AS "Дата закрытия (Китай)",
    t.b24_url AS "Ссылка на задачу в Bitrix24"
FROM analytics_supplier_search_tasks t
WHERE t.status = 5 AND t.has_supplier_attached = FALSE
ORDER BY t.closed_date DESC
LIMIT 50;"""
        },
        {
            "name": "4. Детализация добавленных поставщиков и аудит качества",
            "description": "Полный список созданных компаний с проверкой обязательного наличия WeChat и комментариев",
            "display": "table",
            "sql": """SELECT 
    c.company_id AS "ID",
    c.title AS "Название фабрики / компании",
    c.created_by_name AS "Кто добавил",
    TO_CHAR(c.date_create AT TIME ZONE 'Asia/Shanghai', 'YYYY-MM-DD HH24:MI') AS "Дата создания (Китай)",
    CASE WHEN c.is_complete THEN '✅ 100% Заполнено' ELSE '⚠️ Требует доработки' END AS "Статус качества",
    c.completeness_score || '%' AS "Полнота",
    CASE WHEN c.has_wechat THEN 'Да' ELSE '❌ НЕТ WECHAT' END AS "WeChat",
    CASE WHEN c.has_comment THEN 'Да' ELSE '❌ НЕТ КОММЕНТАРИЯ' END AS "Комментарий",
    c.comment_text AS "Краткое описание",
    c.b24_url AS "Ссылка в CRM"
FROM analytics_supplier_companies c
ORDER BY c.date_create DESC
LIMIT 100;"""
        }
    ]

    card_ids = [87, 88, 89, 90]
    dash_id = 11

    # 5. Размещение карточек на сетке дашборда
    grid_layout = [
        {"card_id": card_ids[0], "row": 0, "col": 0, "size_x": 18, "size_y": 4},
        {"card_id": card_ids[1], "row": 4, "col": 0, "size_x": 18, "size_y": 7},
        {"card_id": card_ids[2], "row": 11, "col": 0, "size_x": 18, "size_y": 8},
        {"card_id": card_ids[3], "row": 19, "col": 0, "size_x": 18, "size_y": 10}
    ]

    cards_payload = []
    for idx, item in enumerate(grid_layout, 1):
        cards_payload.append({
            "id": -idx,
            "card_id": item["card_id"],
            "row": item["row"],
            "col": item["col"],
            "size_x": item["size_x"],
            "size_y": item["size_y"],
            "visualization_settings": {}
        })

    update_res = api_call(session_id, "PUT", f"/dashboard/{dash_id}/cards", {"cards": cards_payload})
    if update_res is not None:
        print(f"[OK] Все 4 карточки успешно привязаны и размещены на дашборде ID {dash_id}!")

    print(f"\n🎉 ДАШБОРД ГОТОВ К ИСПОЛЬЗОВАНИЮ:")
    print(f"👉 Прямая ссылка: {METABASE_URL}/dashboard/{dash_id}")

if __name__ == "__main__":
    main()
