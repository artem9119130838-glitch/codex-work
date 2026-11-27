# -*- coding: utf-8 -*-
"""
harvest_logistics_batch.py
==========================
Сбор и каталогизация данных по логистике (Фаза 1).
Источники:
  1. Локальные регламенты и ДИ с диска D (41 файл) -> batch_existing_rules.json
  2. 16 задач Битрикс24 и личные диалоги ключевых сотрудников -> batch_real_cases.json
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
import requests

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Импорт парсеров документов
import docx
import openpyxl

# Загрузка переменных окружения
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

def b24(method, payload=None, retries=3):
    url = webhook + method
    for attempt in range(retries):
        try:
            r = requests.post(url, json=payload or {}, timeout=30)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 503 or r.status_code == 429:
                time.sleep(1.5)
                continue
            else:
                return r.json() if r.text.startswith("{") else {}
        except Exception as e:
            if attempt == retries - 1:
                return {}
            time.sleep(1.0)
    return {}

users_map = {
    1: "Артем",
    14: "Сауле Бестова",
    16: "Анжелика Павлова",
    20: "Азат Денишов",
    24: "Ирина Мусина",
    28: "Ирина Мусина (2)",
    38: "Александра Пономарева",
    42: "Михаил Денисов",
    64: "Liyan Wang",
    86: "Cindy Qian (Синди / Цянь Ин)"
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
    t = re.sub(r'\[B\](.*?)\[/B\]', r'\1', t)
    t = re.sub(r'\[I\](.*?)\[/I\]', r'\1', t)
    t = re.sub(r'\[TIMESTAMP.*?\](.*?)\[/TIMESTAMP\]', r'\1', t)
    t = re.sub(r'\[USER.*?\]', '', t)
    t = re.sub(r'\[/USER\]', '', t)
    return t.strip()

# --- ЧАСТЬ 1: Сбор локальных правил с диска D ---

def parse_docx_file(file_path):
    try:
        doc = docx.Document(str(file_path))
        paragraphs = []
        for p in doc.paragraphs:
            txt = p.text.strip()
            if txt:
                paragraphs.append(txt)
        
        tables_data = []
        for t_idx, table in enumerate(doc.tables):
            t_rows = []
            for row in table.rows:
                r_cells = [c.text.strip().replace("\n", " ") for c in row.cells]
                if any(r_cells):
                    t_rows.append(r_cells)
            if t_rows:
                tables_data.append(t_rows)
                
        full_text = "\n".join(paragraphs)
        if tables_data:
            full_text += "\n\nТаблицы:\n"
            for t in tables_data:
                for r in t:
                    full_text += " | ".join(r) + "\n"
        return full_text.strip(), paragraphs, tables_data
    except Exception as docx_err:
        # Фолбэк для HTML/текстовых файлов, сохраненных с расширением .docx
        raw = Path(file_path).read_bytes()
        for enc in ["utf-8", "utf-8-sig", "gb18030", "cp1251"]:
            try:
                decoded = raw.decode(enc)
                # Удаляем html-теги
                clean_text = re.sub(r'<[^>]+>', ' ', decoded)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                paragraphs = [p.strip() for p in clean_text.splitlines() if p.strip()]
                return clean_text, paragraphs, []
            except UnicodeDecodeError:
                continue
        raise docx_err

def parse_xlsx_file(file_path, max_rows=200):
    wb = openpyxl.load_workbook(str(file_path), data_only=True, read_only=True)
    sheets_data = {}
    full_text_lines = []
    for s_name in wb.sheetnames:
        ws = wb[s_name]
        sheet_rows = []
        r_cnt = 0
        for row in ws.iter_rows(values_only=True):
            if any(cell is not None for cell in row):
                row_str = ["" if c is None else str(c).strip().replace("\n", " ") for c in row]
                sheet_rows.append(row_str)
                full_text_lines.append(" | ".join(row_str))
                r_cnt += 1
                if r_cnt >= max_rows:
                    break
        sheets_data[s_name] = sheet_rows
    wb.close()
    return "\n".join(full_text_lines).strip(), sheets_data

def harvest_existing_rules(root_dir, output_file):
    print(f"\n==================================================", flush=True)
    print(f"  ФАЗА 1.1: Сбор локальных регламентов с диска D", flush=True)
    print(f"  Каталог: {root_dir}", flush=True)
    print(f"==================================================", flush=True)
    
    all_rules = []
    files_list = []
    for r, d, fs in os.walk(root_dir):
        for f in fs:
            if not f.startswith("~$") and f.lower().endswith((".docx", ".xlsx")):
                files_list.append(os.path.join(r, f))
                
    files_list.sort()
    print(f"Обнаружено файлов для обработки: {len(files_list)}", flush=True)
    
    for idx, fpath in enumerate(files_list, 1):
        rel_path = os.path.relpath(fpath, root_dir)
        fname = os.path.basename(fpath)
        ext = os.path.splitext(fpath)[1].lower()
        folder = os.path.dirname(rel_path) or "Корень"
        stat = os.stat(fpath)
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        item = {
            "id": f"RULE_{idx:03d}",
            "file_name": fname,
            "relative_path": rel_path,
            "category_folder": folder,
            "extension": ext,
            "size_bytes": stat.st_size,
            "modified_at": mtime,
            "extracted_text": "",
            "paragraphs_count": 0,
            "tables_count": 0,
            "sheets_count": 0,
            "key_topics": []
        }
        
        try:
            if ext == ".docx":
                text, paras, tables = parse_docx_file(fpath)
                item["extracted_text"] = text
                item["paragraphs_count"] = len(paras)
                item["tables_count"] = len(tables)
            elif ext == ".xlsx":
                text, sheets = parse_xlsx_file(fpath)
                item["extracted_text"] = text
                item["sheets_count"] = len(sheets)
                item["sheet_names"] = list(sheets.keys())
                
            # Выделение тем по ключевым словам
            kw_map = {
                "бондовая зона": ["бондов", "бондовая"],
                "карго и упаковка": ["карго", "cargo", "упаковк", "паллет", "ящик", "обрешетка"],
                "прямой перевозчик / автопарк": ["перевозчик", "автопарк", "тягач", "водитель", "фура"],
                "железная дорога": ["жд", "ж/д", "железнодорожн", "поезд", "платформа", "контейнер"],
                "таможня и ТОФ": ["тоф", "таможн", "декларац", "гтд", "брокер", "оформлен"],
                "регламент логиста": ["регламент", "должностн", "ди логиста", "обязанност", "инструкция"],
                "расчет себестоимости": ["себестоимост", "тариф", "ставка", "расчет доставки", "котировк"],
                "Китай / офис КНР": ["китай", "лун-ван", "синди", "miss wang", "yunmaotong", "юньмаотун"],
                "ТК в РФ": ["сдэк", "ждэ", "деловые линии", "пэк", "тк в рф", "доставка по рф"]
            }
            topics = []
            text_lower = (fname + " " + item["extracted_text"][:2000]).lower()
            for top, kws in kw_map.items():
                if any(k in text_lower for k in kws):
                    topics.append(top)
            item["key_topics"] = topics
            
            all_rules.append(item)
            print(f"  [{idx:02d}/{len(files_list)}] Обработан: {rel_path} ({len(item['extracted_text'])} симв.)", flush=True)
        except Exception as e:
            print(f"  [ОШИБКА] Не удалось прочитать {rel_path}: {e}", flush=True)
            item["error"] = str(e)
            all_rules.append(item)
            
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_rules, f, ensure_ascii=False, indent=2)
        
    print(f"ИТОГО сохранено правил: {len(all_rules)} в {output_file}", flush=True)
    return all_rules

# --- ЧАСТЬ 2: Сбор реальных кейсов (16 задач и личные диалоги) ---

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

def harvest_real_cases(task_ids, personal_dialogs, output_file):
    print(f"\n==================================================", flush=True)
    print(f"  ФАЗА 1.2: Сбор практических кейсов (16 задач и диалоги)", flush=True)
    print(f"==================================================", flush=True)
    
    all_cases = []
    case_idx = 1
    
    # 1. 16 Задач Битрикс24
    print(f"\n--- Выгрузка целевых задач ({len(task_ids)} шт.) ---", flush=True)
    for tid in task_ids:
        print(f"Обработка задачи #{tid}...", flush=True)
        r_t = b24("tasks.task.get", {"taskId": tid})
        task = r_t.get("result", {}).get("task", {})
        if not task:
            print(f"  [ВНИМАНИЕ] Задача #{tid} не найдена или нет доступа", flush=True)
            continue
            
        t_title = clean_b24(task.get("title", ""))
        t_desc = clean_b24(task.get("description", ""))
        t_created = task.get("createdDate", "")
        t_closed = task.get("closedDate", "")
        resp_id = int(task.get("responsibleId") or 0)
        creator_id = int(task.get("createdBy") or 0)
        resp_name = users_map.get(resp_id, f"User {resp_id}")
        creator_name = users_map.get(creator_id, f"User {creator_id}")
        
        # Кейс 1: Постановка задачи и описание (если содержательное)
        if t_desc and len(t_desc) > 20:
            all_cases.append({
                "case_id": f"CASE_{case_idx:04d}",
                "source_type": "task_description",
                "task_id": tid,
                "title": t_title,
                "author": creator_name,
                "responsible": resp_name,
                "date": t_created,
                "text": t_desc,
                "category": "постановка_задачи",
                "status": task.get("status")
            })
            case_idx += 1
            
        # Комментарии к задаче
        r_c = b24("task.commentitem.getlist", [tid, {"ID": "asc"}, {}])
        comments = r_c.get("result", [])
        if comments:
            print(f"  Найдено комментариев: {len(comments)}", flush=True)
            for c in comments:
                c_text = clean_b24(c.get("POST_MESSAGE", ""))
                if c_text and len(c_text) > 10:
                    a_id = int(c.get("AUTHOR_ID") or 0)
                    all_cases.append({
                        "case_id": f"CASE_{case_idx:04d}",
                        "source_type": "task_comment",
                        "task_id": tid,
                        "title": t_title,
                        "author": users_map.get(a_id, f"User {a_id}"),
                        "date": c.get("POST_DATE", ""),
                        "text": c_text,
                        "category": "комментарий_к_задаче"
                    })
                    case_idx += 1
                    
        # Привязанный чат задачи
        r_chat = b24("im.chat.get", {"ENTITY_TYPE": "TASKS_TASK", "ENTITY_ID": tid})
        chat_id = r_chat.get("result", {}).get("ID") if r_chat.get("result") else None
        if chat_id:
            chat_msgs = fetch_all_dialog_messages(f"chat{chat_id}", max_pages=10)
            if chat_msgs:
                print(f"  Найдено сообщений в чате задачи chat{chat_id}: {len(chat_msgs)}", flush=True)
                for m in chat_msgs:
                    m_text = clean_b24(m.get("text", ""))
                    if m_text and len(m_text) > 10 and not m_text.startswith("--------------------------------------------------"):
                        a_id = int(m.get("author_id") or 0)
                        all_cases.append({
                            "case_id": f"CASE_{case_idx:04d}",
                            "source_type": "task_chat_message",
                            "task_id": tid,
                            "chat_id": f"chat{chat_id}",
                            "title": t_title,
                            "author": users_map.get(a_id, f"User {a_id}"),
                            "date": m.get("date", ""),
                            "text": m_text,
                            "category": "чат_задачи"
                        })
                        case_idx += 1

    # 2. Личные диалоги ключевых лиц
    print(f"\n--- Выгрузка личных диалогов и заметок ({len(personal_dialogs)} источников) ---", flush=True)
    for p_id, p_name in personal_dialogs:
        print(f"Выгрузка диалога: {p_name} ({p_id})...", flush=True)
        # Для личных диалогов cutoff_date берем за последние 90 дней (с 2026-08-01)
        d_msgs = fetch_all_dialog_messages(str(p_id), max_pages=20, cutoff_date="2026-08-01")
        print(f"  Всего сообщений получено: {len(d_msgs)}", flush=True)
        
        for m in d_msgs:
            m_text = clean_b24(m.get("text", ""))
            # Отфильтровываем служебный шум: системные оповещения, короткие реплики
            if not m_text or len(m_text) < 15:
                continue
            if any(m_text.startswith(w) for w in ["Напоминание о событии", "Вы добавлены в чат", "Создана задача"]):
                continue
                
            # Проверяем релевантность логистике, закупкам, фабрикам, отправкам, тарифам
            logistics_kw = [
                "груз", "доставк", "логист", "синди", "cindy", "авто", "фура", "жд", "контейнер",
                "циндао", "дечжоу", "маньчжур", "хэйхэ", "таможн", "брокер", "карго", "тариф",
                "отправк", "погрузк", "вес", "объем", "труб", "шток", "упаковк", "склад", "сдэк",
                "ждэ", "накладн", "деловые", "перевозчик", "автопарк", "инвойс", "пакинг", "гтд",
                "шильдик", "шильды", "дефектовк", "брак", "бондов", "экспорт", "импорт", "1с",
                "вопрос", "список вопросов", "согласован", "3010", "транспорт", "юньмаотун"
            ]
            text_l = m_text.lower()
            is_relevant = any(kw in text_l for kw in logistics_kw) or p_id in [86, 64] # Для Синди и Wang все содержательные сообщения
            
            if is_relevant:
                a_id = int(m.get("author_id") or 0)
                all_cases.append({
                    "case_id": f"CASE_{case_idx:04d}",
                    "source_type": "personal_dialog",
                    "dialog_with": p_name,
                    "author": users_map.get(a_id, f"User {a_id}"),
                    "date": m.get("date", ""),
                    "text": m_text,
                    "category": "личный_диалог_логистика"
                })
                case_idx += 1
                
    # Дедупликация кейсов по тексту и дате
    unique_cases = []
    seen_keys = set()
    for c in all_cases:
        key = (c["date"][:16], c["author"], c["text"][:60])
        if key not in seen_keys:
            seen_keys.add(key)
            unique_cases.append(c)
            
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(unique_cases, f, ensure_ascii=False, indent=2)
        
    print(f"\nИТОГО извлечено кейсов/инцидентов: {len(unique_cases)} в {output_file}", flush=True)
    return unique_cases

def main():
    root_d = r"D:\Документы Victus\Рабочее\Инструкции\Логистика"
    out_rules = os.path.join(os.getcwd(), "projects", "HR", "data_dumps", "batch_existing_rules.json")
    out_cases = os.path.join(os.getcwd(), "projects", "HR", "data_dumps", "batch_real_cases.json")
    
    # 1. Сбор локальных регламентов (41 файл)
    rules = harvest_existing_rules(root_d, out_rules)
    
    # 2. Сбор кейсов из 16 задач и диалогов
    task_ids = [5442, 4592, 5886, 5186, 6222, 5648, 3010, 780, 1048, 4832, 40, 5040, 3566, 32, 108, 1338]
    personal_dialogs = [
        (1, "Заметки Артема"),
        (20, "Азат Денишов"),
        (86, "Cindy Qian"),
        (64, "Liyan Wang"),
        (38, "Александра Пономарева"),
        (16, "Анжелика Павлова"),
        (24, "Ирина Мусина"),
        (28, "Ирина Мусина (2)")
    ]
    cases = harvest_real_cases(task_ids, personal_dialogs, out_cases)
    
    print("\n================== ИТОГОВЫЙ СТАТУС ФАЗЫ 1 ==================", flush=True)
    print(f"Обработано файлов с диска D: {len(rules)} шт. (ожидалось 41)")
    print(f"Извлечено кейсов/инцидентов: {len(cases)} шт. (ожидалось >= 50)")
    print(f"batch_existing_rules.json: {out_rules} ({os.path.getsize(out_rules):,} байт)")
    print(f"batch_real_cases.json: {out_cases} ({os.path.getsize(out_cases):,} байт)")
    print("===========================================================", flush=True)

if __name__ == "__main__":
    main()
