# -*- coding: utf-8 -*-
"""
Канонический скрипт интеллектуального поиска знаний, задач, чатов и протоколов в Битрикс24
(Search Bitrix Knowledge & Meetings Pipeline)

Позволяет искать задачи, совещания, договоренности и переписки по размытым запросам,
участникам, ключевым словам с глубоким анализом комментариев и связанных чатов задач.

Использование:
    py projects/1c_odata/scripts/search_bitrix_knowledge.py --query "созвон тендеры" --users 20,38 --since 2026-08-01
    py projects/1c_odata/scripts/search_bitrix_knowledge.py --task-id 780
    py projects/1c_odata/scripts/search_bitrix_knowledge.py --chat-id 1504 --limit 50
"""

import os
import sys
import json
import argparse
import urllib.request
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Загрузка боевого вебхука строго через os.getenv (Zero Secrets Guard)
DEFAULT_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "")
if not DEFAULT_WEBHOOK:
    # Попытка прочитать из .env локально
    env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("BITRIX24_WEBHOOK_URL="):
                    DEFAULT_WEBHOOK = line.strip().split("=", 1)[1].strip("'\"")

def b24_call(method: str, params: dict = None, webhook_url: str = None) -> dict:
    url = (webhook_url or DEFAULT_WEBHOOK).rstrip("/") + "/" + method
    if not url.startswith("http"):
        print(f"[ERROR] Не задан валидный BITRIX24_WEBHOOK_URL.")
        return {}
    data = json.dumps(params or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[API ERROR] {method}: {e}", file=sys.stderr)
        return {}

def inspect_task(task_id: int, webhook: str = None):
    """Детальный осмотр задачи, ее описания, комментариев и связанного чата."""
    print(f"\n=======================================================")
    print(f"🔍 ИНСПЕКЦИЯ ЗАДАЧИ #{task_id}")
    print(f"=======================================================")
    res = b24_call("tasks.task.get", {"taskId": task_id, "select": ["*", "UF_*"]}, webhook)
    if not res or "result" not in res:
        print(f"Задача #{task_id} не найдена.")
        return

    task = res["result"].get("task", {})
    print(f"📌 Название: {task.get('title')}")
    print(f"📅 Создана: {task.get('createdDate')} | Статус: {task.get('status')} | Дедлайн: {task.get('deadline')}")
    print(f"👤 Постановщик: {task.get('creator', {}).get('name')} (ID: {task.get('createdBy')})")
    print(f"🎯 Ответственный: {task.get('responsible', {}).get('name')} (ID: {task.get('responsibleId')})")
    
    accomplices = task.get("accomplicesData", {})
    if accomplices:
        acc_names = [f"{v.get('name')} (ID {k})" for k, v in accomplices.items()]
        print(f"👥 Соисполнители: {', '.join(acc_names)}")
    
    auditors = task.get("auditorsData", {})
    if auditors:
        aud_names = [f"{v.get('name')} (ID {k})" for k, v in auditors.items()]
        print(f"👁 Аудиторы: {', '.join(aud_names)}")

    chat_id = task.get("chatId")
    if chat_id:
        print(f"💬 Чат задачи: chat{chat_id}")

    desc = task.get("description", "").strip()
    if desc:
        print(f"\n📝 ОПИСАНИЕ / РЕГЛАМЕНТ:\n{desc}\n")

    # Комментарии к задаче
    c_res = b24_call("task.commentitem.getlist", [task_id], webhook)
    comments = c_res.get("result", []) if (c_res and "result" in c_res) else []
    print(f"💬 Комментариев в задаче: {len(comments)}")
    for c in comments:
        print(f"  [{c.get('POST_DATE')}] {c.get('AUTHOR_NAME')}: {c.get('POST_MESSAGE', '')[:200]}")

    # Чат задачи
    if chat_id:
        m_res = b24_call("im.dialog.messages.get", {"DIALOG_ID": f"chat{chat_id}", "LIMIT": 20}, webhook)
        msgs = m_res.get("result", {}).get("messages", [])
        print(f"📨 Сообщений в привязанном чате (chat{chat_id}): {len(msgs)}")
        for m in sorted(msgs, key=lambda x: x.get("date", ""))[-10:]:
            print(f"  [{m.get('date')}] User {m.get('author_id')}: {m.get('text', '')[:180]}")

def inspect_chat(chat_id: str, limit: int = 50, webhook: str = None):
    """Выгрузка сообщений из конкретного чата."""
    dialog_id = f"chat{chat_id}" if not str(chat_id).startswith("chat") and str(chat_id).isdigit() else str(chat_id)
    print(f"\n=== ВЫГРУЗКА СООБЩЕНИЙ ИЗ {dialog_id} (LIMIT: {limit}) ===")
    res = b24_call("im.dialog.messages.get", {"DIALOG_ID": dialog_id, "LIMIT": limit}, webhook)
    msgs = res.get("result", {}).get("messages", [])
    if not msgs:
        print("Сообщений не найдено.")
        return
    for m in sorted(msgs, key=lambda x: x.get("date", "")):
        print(f"[{m.get('date')}] User {m.get('author_id')}: {m.get('text')}\n")

def search_tasks_and_knowledge(query: str, users: list, since_date: str, limit: int, check_chats: bool, webhook: str = None):
    """Комплексный поиск задач по участникам и нечетким ключевым словам."""
    print(f"\n🔍 Запуск поиска: query='{query}', users={users}, since={since_date}, limit={limit}")
    
    keywords = [k.strip().lower() for k in query.split() if len(k.strip()) >= 3] if query else []
    user_set = set(str(u).strip() for u in users) if users else set()

    found_tasks = []
    start = 0
    batch_size = 50
    total_scanned = 0

    while True:
        res = b24_call("tasks.task.list", {
            "filter": {
                ">=CREATED_DATE": f"{since_date}T00:00:00+03:00"
            },
            "select": ["ID", "TITLE", "CREATED_DATE", "CREATED_BY", "RESPONSIBLE_ID", "ACCOMPLICES", "AUDITORS", "DESCRIPTION", "CHAT_ID", "STATUS"],
            "order": {"ID": "DESC"},
            "start": start
        }, webhook)

        if not res or "result" not in res or "tasks" not in res["result"]:
            break
        tasks = res["result"]["tasks"]
        if not tasks:
            break

        total_scanned += len(tasks)
        for t in tasks:
            title = (t.get("title") or "").strip()
            # Фильтр авто-парсера тендеров
            if title.startswith("=Проанализировать") or title.startswith("=Тендер с суммой"):
                continue

            desc = (t.get("description") or "").strip()
            comb = (title + " " + desc).lower()

            # Сверка участников
            accomplices = set(str(x) for x in t.get("accomplices") or [])
            auditors = set(str(x) for x in t.get("auditors") or [])
            uids = accomplices.union(auditors)
            uids.add(str(t.get("createdBy", "")))
            uids.add(str(t.get("responsibleId", "")))

            user_match = len(uids.intersection(user_set)) if user_set else 1
            kw_match = sum(1 for kw in keywords if kw in comb) if keywords else 1

            if (user_set and user_match > 0 and kw_match > 0) or (not user_set and kw_match > 0):
                score = user_match * 2 + kw_match
                found_tasks.append((score, t, uids.intersection(user_set) if user_set else uids))

        if len(found_tasks) >= limit or "next" not in res:
            break
        start = res["next"]

    found_tasks.sort(key=lambda x: x[0], reverse=True)
    print(f"✅ Просканировано задач: {total_scanned}. Найдено релевантных: {len(found_tasks)}")

    for score, t, matched_users in found_tasks[:limit]:
        tid = t.get("id")
        print(f"\n-------------------------------------------------------")
        print(f"⭐ [Score: {score}] Задача #{tid} | Статус: {t.get('status')} | Создана: {t.get('createdDate')}")
        print(f"📌 Название: {t.get('title')}")
        print(f"👥 Совпавшие участники: {matched_users} | ChatID: {t.get('chatId')}")
        if t.get('description'):
            print(f"📝 Описание: {t.get('description')[:250]}...")

        if check_chats and t.get('chatId'):
            m_res = b24_call("im.dialog.messages.get", {"DIALOG_ID": f"chat{t.get('chatId')}", "LIMIT": 3}, webhook)
            msgs = m_res.get("result", {}).get("messages", [])
            if msgs:
                print(f"💬 Последние сообщения из чата задачи:")
                for m in msgs:
                    print(f"   [{m.get('date')}] User {m.get('author_id')}: {m.get('text', '')[:120]}")

def main():
    parser = argparse.ArgumentParser(description="Поиск знаний, задач, созвонов и чатов в Битрикс24.")
    parser.add_argument("--query", "-q", type=str, default="", help="Ключевые слова для поиска")
    parser.add_argument("--users", "-u", type=str, default="", help="ID пользователей через запятую (например, 20,38)")
    parser.add_argument("--since", type=str, default="2026-07-01", help="Дата начала поиска (ГГГГ-ММ-ДД)")
    parser.add_argument("--limit", type=int, default=10, help="Максимальное количество результатов")
    parser.add_argument("--task-id", type=int, default=None, help="Детальный осмотр конкретной задачи")
    parser.add_argument("--chat-id", type=str, default=None, help="Выгрузка сообщений из чата")
    parser.add_argument("--check-chats", action="store_true", help="Автоматически проверять сообщения в связанных чатах задач")
    parser.add_argument("--dry-run", action="store_true", help="Холостой запуск (только чтение)")

    args = parser.parse_args()

    if args.task_id:
        inspect_task(args.task_id)
    elif args.chat_id:
        inspect_chat(args.chat_id, limit=args.limit)
    else:
        user_list = [x.strip() for x in args.users.split(",") if x.strip()] if args.users else []
        search_tasks_and_knowledge(
            query=args.query,
            users=user_list,
            since_date=args.since,
            limit=args.limit,
            check_chats=args.check_chats
        )

if __name__ == "__main__":
    main()
