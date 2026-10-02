#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/mine_crm_incidents.py
=============================
Канонический инструмент аудита чатов и сбора инцидентов Битрикс24 (Incident Miner).
Консолидирует функционал сбора сообщений, файлов, поиска ошибок, багов, договоренностей
и построения отчетов для руководства.

Поддерживает режимы:
- Боевой сбор переписки через Битрикс24 REST API (im.dialog.messages.get)
- Парсинг локального сохраненного JSON (--input-json)
- Dry-run симуляцию (--dry-run)
- Аппаратный Self-Check (--self-check)
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
# Подгрузка переменных окружения из .env если заданы
for env_path in [".env", "projects/1c_odata/.env", os.path.join(os.path.dirname(__file__), "..", ".env"), os.path.join(os.path.dirname(__file__), "..", "projects", "1c_odata", ".env")]:
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() not in os.environ:
                            os.environ[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass

B24_WEBHOOK_DEFAULT = os.getenv("BITRIX24_WEBHOOK_URL", "")

INCIDENT_KEYWORDS = {
    "CRITICAL": ["провал", "550", "crash", "fatal", "критическ", "блокир", "security reason"],
    "BUG": ["ошибк", "баг", "проблем", "не работает", "завис", "сбой", "ложноположительн", "read-only", "timeout", "обрезк", "reject", "отказ", "не отлавливал", "warning", "error", "failed"],
    "DECISION": ["решили", "договорились", "принято", "согласовано", "дедлайн", "сделано", "готово", "сделай", "нужно сделать", "исправь", "поправь"]
}


def fetch_b24_chat(webhook_url: str, chat_id: str, limit: int = 100) -> dict:
    """Выгружает историю сообщений и пользователей из диалога Битрикс24."""
    import requests
    dialog_id = chat_id if str(chat_id).startswith("chat") else f"chat{chat_id}"
    url = webhook_url.rstrip("/") + "/im.dialog.messages.get"
    
    resp = requests.post(url, json={"DIALOG_ID": dialog_id, "LIMIT": limit}, timeout=25)
    resp.raise_for_status()
    payload = resp.json()
    if "result" not in payload:
        raise ValueError(f"Некорректный ответ Битрикс24: {payload}")
    return payload["result"]


def analyze_messages(messages: list, users_map: dict, files_map: dict, since_date: str = None) -> dict:
    """Проводит глубокий семантический анализ сообщений диалога."""
    sorted_msgs = sorted(messages, key=lambda x: x.get("id", 0))
    if since_date:
        sorted_msgs = [m for m in sorted_msgs if m.get("date", "") >= since_date]

    incidents = []
    decisions = []
    statuses = []
    dialogue_turns = []

    current_turn = None

    for m in sorted_msgs:
        m_id = m.get("id")
        date_str = m.get("date", "")
        author_id = str(m.get("author_id", ""))
        author_name = users_map.get(author_id, f"Пользователь {author_id}")
        text = (m.get("text") or "").strip()
        params = m.get("params", {})

        attached_files = []
        if isinstance(params, dict) and "FILE_ID" in params:
            for fid in params["FILE_ID"]:
                f_info = files_map.get(str(fid)) or files_map.get(fid)
                if f_info:
                    attached_files.append({
                        "id": fid,
                        "name": f_info.get("name"),
                        "url": f_info.get("urlDownload")
                    })

        lower_text = text.lower()

        # Категоризация
        is_crit = any(w in lower_text for w in INCIDENT_KEYWORDS["CRITICAL"])
        is_bug = any(w in lower_text for w in INCIDENT_KEYWORDS["BUG"])
        is_dec = any(w in lower_text for w in INCIDENT_KEYWORDS["DECISION"])

        if is_crit or is_bug:
            incidents.append({
                "id": m_id,
                "date": date_str,
                "author": author_name,
                "severity": "CRITICAL" if is_crit else "WARNING",
                "text": text,
                "files": attached_files
            })

        if is_dec:
            decisions.append({
                "id": m_id,
                "date": date_str,
                "author": author_name,
                "text": text
            })

        # Поиск статусов (PASS / REJECT / WAIVED / FAILED)
        found_st = re.findall(r"([A-Za-zА-Яа-я0-9_\-\s\"«»]{3,40})\s*[:—–-]\s*(PASS|REJECT[A-Z_]*|FSTEK[A-Z_]*|FAILED|WAIVED)", text, re.IGNORECASE)
        for entity, st in found_st:
            statuses.append({
                "entity": entity.strip(),
                "status": st.upper(),
                "message_id": m_id,
                "date": date_str
            })

        # Группировка диалога по авторам
        if current_turn and current_turn["author_id"] == author_id:
            current_turn["messages"].append({"id": m_id, "date": date_str, "text": text, "files": attached_files})
        else:
            if current_turn:
                dialogue_turns.append(current_turn)
            current_turn = {
                "author_id": author_id,
                "author_name": author_name,
                "start_date": date_str,
                "messages": [{"id": m_id, "date": date_str, "text": text, "files": attached_files}]
            }

    if current_turn:
        dialogue_turns.append(current_turn)

    return {
        "summary": {
            "total_messages": len(sorted_msgs),
            "total_incidents": len(incidents),
            "total_decisions": len(decisions),
            "total_statuses": len(statuses),
            "period_start": sorted_msgs[0].get("date") if sorted_msgs else "N/A",
            "period_end": sorted_msgs[-1].get("date") if sorted_msgs else "N/A",
            "participants": list(users_map.values())
        },
        "incidents": incidents,
        "decisions": decisions,
        "statuses": statuses,
        "dialogue_turns": dialogue_turns,
        "raw_messages": sorted_msgs
    }


def generate_markdown_report(analysis_result: dict, chat_title: str = "Чат Битрикс24") -> str:
    """Формирует презентабельный Markdown-отчет по результатам аудита."""
    s = analysis_result["summary"]
    lines = [
        f"# Аналитический аудит чата: {chat_title}",
        f"- **Период:** {s['period_start']} — {s['period_end']}",
        f"- **Всего сообщений:** {s['total_messages']}",
        f"- **Выявлено инцидентов/проблем:** {s['total_incidents']}",
        f"- **Зафиксировано договоренностей:** {s['total_decisions']}",
        f"- **Участники:** {', '.join(s['participants'])}",
        "\n---\n",
        "## 1. Реестр выявленных инцидентов и багов\n"
    ]

    if not analysis_result["incidents"]:
        lines.append("*Инцидентов с ключевыми маркерами сбоев не обнаружено.*\n")
    else:
        lines.append("| ID | Дата | Автор | Уровень | Содержание / Ошибка | Файлы |")
        lines.append("|---|---|---|---|---|---|")
        for inc in analysis_result["incidents"]:
            clean_txt = inc["text"].replace("\n", " ").replace("|", "/")[:120]
            f_str = ", ".join([f["name"] for f in inc["files"]]) if inc["files"] else "—"
            lines.append(f"| #{inc['id']} | {inc['date']} | {inc['author']} | **{inc['severity']}** | {clean_txt} | {f_str} |")
        lines.append("\n")

    lines.append("## 2. Ключевые решения и постановка задач\n")
    if not analysis_result["decisions"]:
        lines.append("*Сообщений с маркерами договоренностей не зафиксировано.*\n")
    else:
        for dec in analysis_result["decisions"]:
            lines.append(f"- **[{dec['date']}] {dec['author']} (msg #{dec['id']}):**")
            lines.append(f"  > {dec['text'].replace(chr(10), chr(10) + '  > ')}")
        lines.append("\n")

    if analysis_result["statuses"]:
        lines.append("## 3. Выявленные статусы объектов / тендеров\n")
        lines.append("| Объект / Тендер | Статус | Сообщение | Дата |")
        lines.append("|---|---|---|---|")
        for st in analysis_result["statuses"]:
            lines.append(f"| {st['entity']} | `{st['status']}` | #{st['message_id']} | {st['date']} |")
        lines.append("\n")

    lines.append("## 4. Хронологический разбор диалога по репликам\n")
    for turn in analysis_result["dialogue_turns"]:
        lines.append(f"### [{turn['start_date']}] {turn['author_name']}")
        for m in turn["messages"]:
            if m["text"]:
                lines.append(m["text"])
            if m["files"]:
                lines.append("\n*Вложения:*")
                for f in m["files"]:
                    lines.append(f"- [{f['name']}]({f['url']})")
        lines.append("\n")

    return "\n".join(lines)


def run_self_check() -> bool:
    """Аппаратный Self-Check логики извлечения инцидентов, статусов и построения Markdown."""
    print("=== [SELF-CHECK] Старт аппаратного теста mine_crm_incidents.py ===")
    mock_users = {"1": "Артем", "2": "Михаил"}
    mock_files = {"101": {"name": "error_log.txt", "urlDownload": "https://b24/f/101"}}
    mock_messages = [
        {"id": 1, "date": "2026-09-25 10:00:00", "author_id": 1, "text": "Михаил, почему скрипт упал с 550 Security reason?", "params": {}},
        {"id": 2, "date": "2026-09-25 10:05:00", "author_id": 2, "text": "Обнаружил баг в модуле цитирования. Вот лог.", "params": {"FILE_ID": [101]}},
        {"id": 3, "date": "2026-09-25 10:15:00", "author_id": 1, "text": "Договорились: исправь это до 18:00. Тендер-1402: PASS", "params": {}}
    ]

    res = analyze_messages(mock_messages, mock_users, mock_files)
    if res["summary"]["total_messages"] != 3:
        print(f"[FAIL] Неверное количество сообщений: {res['summary']['total_messages']}")
        return False

    if res["summary"]["total_incidents"] != 2:
        print(f"[FAIL] Ожидалось 2 инцидента, найдено: {res['summary']['total_incidents']}")
        return False

    if res["summary"]["total_decisions"] != 1:
        print(f"[FAIL] Ожидалась 1 договоренность, найдено: {res['summary']['total_decisions']}")
        return False

    if len(res["statuses"]) != 1 or res["statuses"][0]["status"] != "PASS":
        print(f"[FAIL] Статус тендера не извлечен корректно: {res['statuses']}")
        return False

    md = generate_markdown_report(res, "Тестовый чат")
    if "# Аналитический аудит чата: Тестовый чат" not in md or "error_log.txt" not in md:
        print("[FAIL] Markdown отчет не содержит ожидаемых разделов")
        return False

    print("[PASS] Шаг 1: Семантическая категоризация и парсер диалогов работают безупречно.")
    print("[PASS] Шаг 2: Генерация Markdown и извлечение вложений валидны.")
    print("=== [SELF-CHECK] Все проверки успешно пройдены! ===")
    return True


def main():
    parser = argparse.ArgumentParser(description="Анализатор чатов Битрикс24 и сборщик инцидентов (Incident Miner)")
    parser.add_argument("--chat-id", "-c", default="chat6602", help="ID чата в Битрикс24 (например, chat6602 или 6602)")
    parser.add_argument("--limit", "-l", type=int, default=100, help="Лимит сообщений (по умолчанию 100)")
    parser.add_argument("--since", help="Фильтр даты начала в формате YYYY-MM-DD")
    parser.add_argument("--input-json", help="Путь к локальному JSON дампу (без запроса к API)")
    parser.add_argument("--output-md", default=r"C:\Codex\scratch\crm_incidents_report.md", help="Путь для сохранения Markdown отчета")
    parser.add_argument("--output-json", default=r"C:\Codex\scratch\crm_incidents_report.json", help="Путь для сохранения JSON данных")
    parser.add_argument("--dry-run", action="store_true", help="Режим симуляции без записи файлов на диск")
    parser.add_argument("--self-check", action="store_true", help="Запуск встроенного аппаратного самотестирования")

    args = parser.parse_args()

    if args.self_check:
        ok = run_self_check()
        sys.exit(0 if ok else 1)

    webhook_url = os.getenv("BITRIX24_WEBHOOK_URL", B24_WEBHOOK_DEFAULT)

    if args.input_json:
        print(f"[INCIDENT-MINER] Чтение данных из локального файла: {args.input_json}")
        with open(args.input_json, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        messages = raw_data.get("messages", [])
        users_map = raw_data.get("users", {})
        files_map = {str(f.get("id")): f for f in raw_data.get("files", [])} if isinstance(raw_data.get("files"), list) else raw_data.get("files", {})
    else:
        print(f"[INCIDENT-MINER] Запрос сообщений чата {args.chat_id} через Битрикс24 API...")
        data = fetch_b24_chat(webhook_url, args.chat_id, args.limit)
        users_map = {str(u["id"]): (u.get("name", "") + " " + u.get("last_name", "")).strip() for u in data.get("users", [])}
        files_map = {str(f["id"]): f for f in data.get("files", [])}
        messages = data.get("messages", [])

    print(f"[INCIDENT-MINER] Получено сообщений: {len(messages)}, участников: {len(users_map)}")
    analysis = analyze_messages(messages, users_map, files_map, since_date=args.since)

    s = analysis["summary"]
    print(f"[INCIDENT-MINER] Анализ завершен:")
    print(f"  - Инцидентов / багов: {s['total_incidents']}")
    print(f"  - Договоренностей / задач: {s['total_decisions']}")
    print(f"  - Статусов: {s['total_statuses']}")

    md_report = generate_markdown_report(analysis, chat_title=f"Чат {args.chat_id}")

    if args.dry_run:
        print(f"[DRY-RUN] [INCIDENT-MINER] Отчет Markdown был бы сохранен в: {args.output_md}")
        print(f"[DRY-RUN] [INCIDENT-MINER] JSON дамп был бы сохранен в: {args.output_json}")
        print("[DRY-RUN] Превью первых 5 инцидентов:")
        for inc in analysis["incidents"][:5]:
            print(f"  - [{inc['date']}] {inc['author']} [{inc['severity']}]: {inc['text'][:80]}...")
        return

    os.makedirs(os.path.dirname(os.path.abspath(args.output_md)), exist_ok=True)
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(md_report)

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"[INCIDENT-MINER] Отчет сохранен: {args.output_md}")
    print(f"[INCIDENT-MINER] Данные сохранены: {args.output_json}")


if __name__ == "__main__":
    main()
