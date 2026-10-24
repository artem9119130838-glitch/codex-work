# -*- coding: utf-8 -*-
"""
harvest_team_qa.py
Канонический скрипт сбора и аудита реальных вопросов и ответов (Q&A) сотрудников в Битрикс24
(личные диалоги, чаты задач, профильные группы).
Поддерживает сбор по конкретным пользователям (Азат ID: 20, Александра ID: 38) или сводный аудит.
"""
import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def load_env():
    paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "1c_odata", ".env"),
        os.path.join(os.getcwd(), "projects", "1c_odata", ".env"),
        os.path.join(os.getcwd(), ".env")
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
            break

load_env()
webhook = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
if not webhook or "http" not in webhook:
    print("[ERROR] BITRIX24_WEBHOOK_URL is not configured in .env")
    sys.exit(1)

def b24(method, payload=None):
    try:
        r = requests.post(webhook + method, json=payload or {}, timeout=30)
        return r.json()
    except Exception as e:
        return {}

users_map = {
    1: "Артем",
    14: "Сауле Бестова",
    16: "Анжелика Павлова",
    20: "Азат Денишов",
    24: "Ирина Мусина",
    38: "Александра Пономарева",
    42: "Михаил Денисов"
}

def clean_b24(text):
    if not text:
        return ""
    t = re.sub(r'\[USER=\d+\](.*?)\[/USER\]', r'\1', text)
    t = re.sub(r'\[URL.*?\](.*?)\[/URL\]', r'\1', t)
    t = re.sub(r'\[ATTACH.*?\]', '', t)
    t = re.sub(r'\[SIZE.*?\]', '', t)
    t = re.sub(r'\[/SIZE\]', '', t)
    t = re.sub(r'\[COLOR.*?\]', '', t)
    t = re.sub(r'\[/COLOR\]', '', t)
    t = re.sub(r'\[TIMESTAMP.*?\](.*?)\[/TIMESTAMP\]', r'\1', t)
    return t.strip()

def fetch_all_dialog_messages(dialog_id, max_pages=15, cutoff_date="2026-06-01"):
    all_msgs = []
    first_id = None
    for page in range(max_pages):
        params = {"DIALOG_ID": str(dialog_id), "LIMIT": 50}
        if first_id:
            params["LAST_ID"] = first_id
        r = b24("im.dialog.messages.get", params)
        msgs = r.get("result", {}).get("messages", [])
        if not msgs:
            break
        all_msgs.extend(msgs)
        first_id = msgs[-1].get("id")
        oldest = msgs[-1].get("date", "")
        if oldest and oldest < cutoff_date:
            break
    all_msgs.sort(key=lambda x: x.get("date", ""))
    seen = set()
    unique = []
    for m in all_msgs:
        mid = m.get("id")
        if mid not in seen:
            seen.add(mid)
            unique.append(m)
    return unique

def extract_qa_pairs(messages, target_user_id):
    pairs = []
    for i, m in enumerate(messages):
        aid = m.get("author_id")
        text = clean_b24(m.get("text", ""))
        date = m.get("date", "")
        if aid == target_user_id:
            is_q = (
                "?" in text or
                any(text.lower().startswith(w) for w in [
                    "как ", "где ", "что ", "куда ", "какой ", "какая ", "какие ",
                    "можно ", "нужно ", "надо ", "почему ", "подскажите ", "откройте ",
                    "с какой ", "мы ", "если ", "не понимаю ", "пароль "
                ]) or
                any(w in text.lower() for w in [
                    "пароль", "где лежит", "где взять", "где найти", "как завести",
                    "какой статус", "как считать", "не могу найти", "нет доступа",
                    "не открывается", "как заполнять", "как оформить", "что делать",
                    "откройте контакты", "с какой причиной", "логин"
                ])
            )
            if is_q and len(text) > 8:
                answers = []
                for j in range(i+1, min(i+6, len(messages))):
                    next_m = messages[j]
                    next_aid = next_m.get("author_id")
                    if next_aid != target_user_id and next_aid != 0:
                        ans_text = clean_b24(next_m.get("text", ""))
                        if ans_text:
                            answers.append({
                                "author": users_map.get(next_aid, f"User {next_aid}"),
                                "date": next_m.get("date"),
                                "text": ans_text
                            })
                    elif next_aid == target_user_id:
                        extra = clean_b24(next_m.get("text", ""))
                        if "?" not in extra:
                            text += " " + extra
                pairs.append({
                    "date": date,
                    "question_raw": text,
                    "answers": answers
                })
    return pairs

def harvest_user(user_id, user_name, output_file, tasks_list=None, extra_chats=None):
    print(f"\n==================================================", flush=True)
    print(f"  СБОР ВОПРОСОВ И ОТВЕТОВ: {user_name} (ID: {user_id})", flush=True)
    print(f"==================================================", flush=True)
    all_qa = []
    
    # 1. Личный чат
    print(f"Скачивание личного диалога с {user_name}...", flush=True)
    direct_msgs = fetch_all_dialog_messages(str(user_id), max_pages=25)
    print(f"  Всего сообщений в диалоге: {len(direct_msgs)}", flush=True)
    qa_direct = extract_qa_pairs(direct_msgs, user_id)
    print(f"  Извлечено Q&A из лички: {len(qa_direct)}", flush=True)
    for q in qa_direct:
        q["source"] = "Личный диалог с Артемом"
    all_qa.extend(qa_direct)
    
    # 2. Групповые чаты
    if extra_chats:
        for cid, title in extra_chats:
            print(f"Скачивание чата {cid} ('{title}')...", flush=True)
            c_msgs = fetch_all_dialog_messages(cid, max_pages=10)
            qa_c = extract_qa_pairs(c_msgs, user_id)
            print(f"  Извлечено Q&A: {len(qa_c)}", flush=True)
            for q in qa_c:
                q["source"] = f"Чат '{title}'"
            all_qa.extend(qa_c)
            
    # 3. Задачи
    if tasks_list:
        for tid in tasks_list:
            try:
                r_chat = b24("im.chat.get", {"ENTITY_TYPE": "TASKS_TASK", "ENTITY_ID": tid})
                chat_id = r_chat.get("result", {}).get("ID") if r_chat.get("result") else None
                if chat_id:
                    t_msgs = fetch_all_dialog_messages(f"chat{chat_id}", max_pages=5)
                    qa_t = extract_qa_pairs(t_msgs, user_id)
                    if qa_t:
                        print(f"  Извлечено Q&A из задачи #{tid}: {len(qa_t)}", flush=True)
                        for q in qa_t:
                            q["source"] = f"Задача #{tid}"
                        all_qa.extend(qa_t)
            except Exception:
                pass
                
    print(f"ИТОГО собрано Q&A для {user_name}: {len(all_qa)}", flush=True)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_qa, f, ensure_ascii=False, indent=2)
    print(f"Сохранено в: {output_file}", flush=True)
    return all_qa

def main():
    parser = argparse.ArgumentParser(description="Сборщик Q&A истории сотрудников Битрикс24")
    parser.add_argument("--user", choices=["20", "38", "all"], default="all", help="ID пользователя (20: Азат, 38: Александра, all: оба)")
    args = parser.parse_args()
    
    dumps_dir = os.path.join(os.getcwd(), "projects", "HR", "data_dumps")
    
    if args.user in ["20", "all"]:
        azat_chats = [
            ("chat7254", "Инструкции и экзамен Азат + 1С"),
            ("chat2", "Общий чат"),
            ("chat8056", "Просмотрите регламент"),
            ("chat7884", "Регламент снабжения"),
            ("chat6220", "Тендеры, созвон"),
            ("chat8232", "Выводы по аналитике тендеров")
        ]
        azat_tasks = [4974, 5168, 780, 32, 522]
        harvest_user(20, "Азат Денишов", os.path.join(dumps_dir, "raw_azat_qa.json"), azat_tasks, azat_chats)
        
    if args.user in ["38", "all"]:
        alex_chats = [
            ("chat2138", "Задача #1152 (Вопросы - Александра)"),
            ("chat2", "Общий чат"),
            ("chat7262", "Сделка 41915 ДКХП"),
            ("chat4796", "Сделка Запчасти Mattei"),
            ("chat6220", "Тендеры, созвон")
        ]
        alex_tasks = [522, 32, 780, 2634, 5168, 1488, 5186, 4882, 4974]
        harvest_user(38, "Александра Пономарева", os.path.join(dumps_dir, "raw_alexandra_qa.json"), alex_tasks, alex_chats)

if __name__ == "__main__":
    main()
