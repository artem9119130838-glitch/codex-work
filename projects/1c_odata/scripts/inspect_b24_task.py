# -*- coding: utf-8 -*-
"""
inspect_b24_task.py
Автономный канонический скрипт для чтения задач Битрикс24, истории комментариев, чатов задач и выгрузки прикрепленных скриншотов / файлов.
Поддерживает как классические комментарии (task.commentitem), так и новый формат чатов задач (im.dialog.messages через ENTITY_TYPE=TASKS_TASK).
"""
import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
import requests

def load_env():
    env_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.getcwd(), "projects", "1c_odata", ".env"),
        os.path.join(os.getcwd(), ".env")
    ]
    for p in env_paths:
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

def b24_call(method, payload=None):
    webhook = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
    if not webhook or "http" not in webhook:
        raise ValueError("BITRIX24_WEBHOOK_URL is not configured in .env")
    url = webhook + method
    res = requests.post(url, json=payload or {}, timeout=30)
    res.raise_for_status()
    return res.json()

def download_file_by_id(file_id, download_dir, prefix=""):
    try:
        r_f = b24_call("disk.file.get", {"id": file_id})
        f_info = r_f.get("result", {})
        down_url = f_info.get("DOWNLOAD_URL")
        name = f_info.get("NAME") or f"file_{file_id}.png"
        size = f_info.get("SIZE", 0)
        
        safe_name = f"{prefix}_{file_id}_{name}" if prefix else f"{file_id}_{name}"
        # Clean special chars from filename
        safe_name = re.sub(r'[\\/*?:"<>|]', "_", safe_name)
        save_path = os.path.join(download_dir, safe_name)

        if not os.path.exists(save_path) and down_url:
            resp = requests.get(down_url, timeout=60)
            if resp.status_code == 200:
                with open(save_path, "wb") as f_out:
                    f_out.write(resp.content)
                print(f"    [OK] Скачан: {save_path} ({len(resp.content)} байт)")
                return save_path
            else:
                print(f"    [FAIL] HTTP {resp.status_code} при скачивании {down_url}")
        elif os.path.exists(save_path):
            print(f"    [EXISTS] {save_path}")
            return save_path
    except Exception as e:
        print(f"    [ERROR] Не удалось скачать файл ID {file_id}: {e}")
    return None

def inspect_task(task_id, days=7, download_dir=None, download_files=True):
    print(f"============================================================")
    print(f"           ИНСПЕКЦИЯ ЗАДАЧИ БИТРИКС24 #{task_id}")
    print(f"============================================================")
    
    r_task = b24_call("tasks.task.get", {"taskId": task_id, "select": [
        "ID", "TITLE", "DESCRIPTION", "STATUS", "CREATED_DATE", "DEADLINE",
        "CREATED_BY", "RESPONSIBLE_ID", "ACCOMPLICES", "AUDITORS",
        "UF_TASK_WEBDAV_FILES", "COMMENTS_COUNT"
    ]})
    task = r_task.get("result", {}).get("task", {})
    if not task:
        print(f"[ERROR] Задача #{task_id} не найдена.")
        return None

    print(f"Заголовок: {task.get('title')}")
    print(f"Статус: {task.get('status')} | Создана: {task.get('createdDate')} | Дедлайн: {task.get('deadline')}")
    print(f"Постановщик: {task.get('createdBy')} | Ответственный: {task.get('responsibleId')}")
    print(f"Соисполнители: {task.get('accomplices')} | Аудиторы: {task.get('auditors')}")
    print(f"Описание:\n{task.get('description', '').strip()[:400]}...")
    print("=" * 60)

    if download_dir:
        os.makedirs(download_dir, exist_ok=True)

    cutoff_date = None
    if days > 0:
        cutoff_date = datetime.now() - timedelta(days=days)
        print(f"Фильтр: за последние {days} дн. (с {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')})")

    downloaded_files = []
    
    # 1. Classical comments (task.commentitem)
    r_comm = b24_call("task.commentitem.getlist", [task_id])
    comments = r_comm.get("result", [])
    if comments:
        print(f"\nНайдено классических комментариев: {len(comments)}")
        for c in comments:
            post_date = c.get("POST_DATE", "")
            # date check
            print(f"--- [Comment #{c.get('ID')}] {post_date} | {c.get('AUTHOR_NAME')} ({c.get('AUTHOR_ID')}) ---")
            print(c.get("POST_MESSAGE", "").strip())
            attached = c.get("ATTACHED_OBJECTS") or {}
            # handle attachments...
    
    # 2. Modern task chat (im.chat.get -> im.dialog.messages.get)
    chat_id = None
    try:
        r_chat = b24_call("im.chat.get", {"ENTITY_TYPE": "TASKS_TASK", "ENTITY_ID": task_id})
        res_chat = r_chat.get("result")
        if res_chat and isinstance(res_chat, dict):
            chat_id = res_chat.get("ID")
    except Exception as e:
        print(f"[DEBUG] Ошибка получения чата задачи: {e}")

    if chat_id:
        print(f"\n[ИНФО] Обнаружен чат задачи: chat{chat_id}")
        r_msgs = b24_call("im.dialog.messages.get", {"DIALOG_ID": f"chat{chat_id}", "LIMIT": 50})
        chat_data = r_msgs.get("result", {})
        msgs = chat_data.get("messages", [])
        files = chat_data.get("files", {})
        users = {str(u.get("id")): u.get("name") for u in chat_data.get("users", [])}

        print(f"Всего сообщений в чате задачи: {len(msgs)}, файлов: {len(files)}")
        print("-" * 60)

        # Messages are returned newest first, sort chronologically
        msgs_sorted = sorted(msgs, key=lambda m: m.get("date", ""))
        
        for m in msgs_sorted:
            m_date_str = m.get("date", "")
            m_dt = None
            try:
                m_dt = datetime.fromisoformat(m_date_str)
            except Exception:
                pass

            if cutoff_date and m_dt:
                # remove tz for comparison
                m_dt_naive = m_dt.replace(tzinfo=None)
                if m_dt_naive < cutoff_date:
                    continue

            aid = str(m.get("author_id"))
            author = users.get(aid, f"Пользователь {aid}")
            text = m.get("text", "")
            params = m.get("params") or {}
            file_ids = params.get("FILE_ID") or []

            print(f"\n>>> [{m_date_str}] {author} (ID: {aid}):")
            print(text.strip())

            if file_ids:
                print(f"  Прикрепленные файлы ({len(file_ids)}): {file_ids}")
                if download_files and download_dir:
                    for fid in file_ids:
                        fpath = download_file_by_id(fid, download_dir, prefix=f"task{task_id}")
                        if fpath:
                            downloaded_files.append(fpath)

            # Check files in text [DISK FILE ID=n]
            inline_files = re.findall(r"\[DISK FILE ID=([n\d]+)\]", text)
            if inline_files and download_files and download_dir:
                print(f"  Встроенные файлы из текста: {inline_files}")
                for inf in inline_files:
                    clean_id = inf.lstrip("n")
                    fpath = download_file_by_id(clean_id, download_dir, prefix=f"task{task_id}")
                    if fpath:
                        downloaded_files.append(fpath)

    print("\n" + "=" * 60)
    print(f"Итог: Сохранено файлов на диске: {len(downloaded_files)}")
    if downloaded_files:
        print("Список скачанных файлов:")
        for df in downloaded_files:
            print(f" - {df}")
    print("=" * 60)

    return {
        "task": task,
        "files": downloaded_files
    }

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    load_env()
    parser = argparse.ArgumentParser(description="Инспекция задачи Битрикс24 и выгрузка скриншотов / вложений")
    parser.add_argument("--task-id", type=int, default=1560, help="ID задачи (по умолчанию: 1560)")
    parser.add_argument("--days", type=int, default=7, help="Фильтр сообщений за N последних дней (0 = все)")
    parser.add_argument("--download-dir", type=str, default=None, help="Директория для сохранения скриншотов/файлов")
    parser.add_argument("--no-download", action="store_true", help="Не скачивать файлы, только вывести текст")
    args = parser.parse_args()

    target_dir = args.download_dir
    if not target_dir and not args.no_download:
        target_dir = os.path.join(os.getcwd(), "projects", "Price creating", "Договор_62230426_Штоки_и_Трубы", "media", f"task_{args.task_id}")

    inspect_task(
        task_id=args.task_id,
        days=args.days,
        download_dir=target_dir,
        download_files=not args.no_download
    )

if __name__ == "__main__":
    main()
