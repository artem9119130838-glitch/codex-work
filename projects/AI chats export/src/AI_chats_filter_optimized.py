import os
import glob
import json
import time
import re
import sys
import socket
from bs4 import BeautifulSoup
from google import generativeai as genai
from google.api_core import exceptions

# Принудительно настраиваем UTF-8 для вывода в консоль
sys.stdout.reconfigure(encoding='utf-8')
socket.setdefaulttimeout(90)

# Настройка путей относительно папки скрипта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "done")
LOG_FILE = os.path.join(OUTPUT_DIR, "report_log.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# API-Ключ и пул моделей
API_KEY = "AIzaSyCj1AUDmL3XtL5zu3lXvwsEsjK0XHdKbjM"
genai.configure(api_key=API_KEY)

MODEL_POOL = [
    'gemini-flash-latest',
    'gemini-flash-lite-latest',
    'gemini-3.5-flash', 
    'gemini-3.1-flash-lite', 
    'gemini-3-flash-preview', 
    'gemini-2.5-flash-lite', 
    'gemini-3.1-flash-lite-preview', 
    'gemini-2.5-flash', 
    'gemini-pro-latest',
    'gemma-4-31b-it', 
    'gemma-4-26b-a4b-it'
]
current_model_idx = 0

PROMPT_TEMPLATE = """
Ты — главный архитектор баз знаний. Перед тобой пакет диалогов из архива чатов ИИ, в которых перемешано несколько тем.
Твоя задача — провести умное укрупнение информации по глобальным жизненным и бизнес-сферам.

ПРАВИЛО ГРУППИРОВКИ (Макро-категории):
Ты должен распределить текст по КРУПНЫМ направлениям. Не дроби темы на мелкие файлы! 
Объединяй родственные темы в один большой блок, разделяя их внутри заголовками Markdown (##).

Примеры укрупнения:
- Все анализы, врачи, показатели здоровья, пульс, а также ветеринария и лечение кота -> в категорию "Здоровье".
- Скрипты n8n, настройки серверов, 1С OData, базы данных, Битрикс24, технический код -> в категорию "Автоматизация".
- Тендеры, ВЭД, таможня, логистика КНР/РФ, а также SEO, маркетинг, аудит сайтов и статьи -> в категорию "Коммерция_и_Маркетинг".
- Выбор телефона, ноутбука, конфигурация Keenetic, настройка почты -> в категорию "Техника_и_Личное".
- Регламенты команды, KPI 4-х сотрудников, контроль и ежедневные отчеты -> в категорию "Управление_командой".

ЖЕСТКОЕ ПРАВИЛО ДЛЯ НОВЫХ ТЕМ (Например, Садоводство, Налоги):
Если в чате обсуждается сфера, которая вообще не лезет в примеры выше — придумай для неё СВОЮ КРУПНУЮ макро-категорию (одно-два слова на русском, например "Садоводство" или "Финансы_и_Налоги"). Слей все мелкие обсуждения по этой теме туда.

ТРЕБОВАНИЕ К ФОРМАТУ ОТВЕТА (КРИТИЧЕСКИ ВАЖНО):
Выдай ответ СТРОГО в формате JSON, где ключи — КРУПНЫЕ категории, а значения — текст в Markdown со всеми важными деталями, кодами, инструкциями и внутренними подзаголовками (##).
Твой ответ должен начинаться с '{{' и заканчиваться на '}}'. Не пиши никакого вводного текста, ссылок или пояснений вне JSON-структуры! Все ссылки и материалы должны быть СТРОГО внутри строковых значений JSON.

Пакет чатов для анализа:
{chat_text}
"""

def log_message(message):
    """Запись строки в консоль и в файл лога"""
    print(message)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception as e:
        print(f"Ошибка записи в лог-файл: {e}")

# ==========================================
# ПАРСЕРЫ СЫРЫХ ДАННЫХ
# ==========================================

def parse_conversations_json(file_path):
    """Парсинг conversations.json (ChatGPT Export)"""
    log_message("Парсинг conversations.json...")
    dialogs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for conv in data:
        title = conv.get('title', 'Без названия').strip()
        chat_text = f"### Чат: {title}\n\n"
        mapping = conv.get('mapping', {})
        
        # Сортируем реплики по времени создания, если есть
        nodes = list(mapping.values())
        try:
            nodes.sort(key=lambda x: x.get('message', {}).get('create_time') or 0 if x.get('message') else 0)
        except Exception:
            pass
            
        has_messages = False
        for node in nodes:
            message = node.get('message')
            if message and message.get('content') and message['content'].get('parts'):
                role = message['author']['role']
                part_text = message['content']['parts'][0]
                if isinstance(part_text, str) and len(part_text.strip()) > 0:
                    author = "Пользователь" if role == "user" else "ИИ"
                    chat_text += f"**{author}**: {part_text.strip()}\n\n"
                    has_messages = True
                    
        if has_messages:
            dialogs.append({
                "source": "conversations.json",
                "title": title,
                "text": chat_text,
                "length": len(chat_text)
            })
    log_message(f"Извлечено диалогов из conversations.json: {len(dialogs)}")
    return dialogs

def parse_gemini_takeout_html(file_path):
    """Парсинг МоиДействия.html (Gemini Takeout)"""
    log_message(f"Парсинг Gemini Takeout HTML: {os.path.basename(file_path)}...")
    dialogs = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    cells = soup.find_all('div', class_='outer-cell')
    
    for cell in cells:
        # Извлекаем дату и метаданные
        header = cell.find('div', class_='header-cell')
        header_text = header.get_text(strip=True) if header else ""
        
        # Извлекаем текст запроса/ответа
        content = cell.find('div', class_='content-cell')
        if not content:
            continue
            
        raw_text = content.get_text(separator='\n', strip=True)
        
        # Пытаемся разбить на запрос пользователя и ответ ИИ
        # Формат обычно: "Отправлен запрос <Запрос> <Дата> <Ответ>" или "Выполнен поиск <Запрос> <Дата> <Ответ>"
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        user_text = ""
        ai_text = ""
        date_str = ""
        
        # Ищем разделители дат и ключевые слова
        is_user = True
        for line in lines:
            if "Отправлен запрос" in line or "Выполнен поиск" in line:
                user_text += line + "\n"
                is_user = True
            elif re.search(r'\d{1,2}\s+[а-яА-Яa-zA-Z]+\s+\d{4}\s+г\.', line): # Дата типа "13 июн. 2026 г."
                date_str = line
                is_user = False
            else:
                if is_user:
                    user_text += line + "\n"
                else:
                    ai_text += line + "\n"
                    
        if user_text.strip():
            title = f"Запрос от {date_str or 'Неизвестная дата'}"
            chat_text = f"### {title}\n\n"
            chat_text += f"**Пользователь**: {user_text.strip()}\n\n"
            if ai_text.strip():
                chat_text += f"**ИИ**: {ai_text.strip()}\n\n"
                
            dialogs.append({
                "source": os.path.basename(file_path),
                "title": title,
                "text": chat_text,
                "length": len(chat_text)
            })
            
    log_message(f"Извлечено запросов из {os.path.basename(file_path)}: {len(dialogs)}")
    return dialogs

def parse_conversation_json_file(file_path):
    """Парсинг отдельных conversation_*.txt файлов (которые на самом деле JSON)"""
    log_message(f"Парсинг файла диалога: {os.path.basename(file_path)}...")
    dialogs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        turns = data.get('conversation_turns', [])
        chat_text = f"### Отдельный диалог: {os.path.basename(file_path)}\n\n"
        has_messages = False
        
        for turn in turns:
            user_turn = turn.get('user_turn', {})
            model_turn = turn.get('model_turn', {})
            
            prompt = user_turn.get('prompt')
            if prompt:
                chat_text += f"**Пользователь**: {prompt.strip()}\n\n"
                has_messages = True
                
            parts = model_turn.get('parts', [])
            for part in parts:
                text = part.get('text')
                if text:
                    chat_text += f"**ИИ**: {text.strip()}\n\n"
                    has_messages = True
                    
        if has_messages:
            dialogs.append({
                "source": os.path.basename(file_path),
                "title": os.path.basename(file_path),
                "text": chat_text,
                "length": len(chat_text)
            })
    except Exception as e:
        log_message(f"Ошибка при парсинге {os.path.basename(file_path)}: {e}")
        
    return dialogs

# ==========================================
# БАТЧИНГ И API
# ==========================================

def make_batches(dialogs, target_size=300000):
    """Группировка диалогов в батчи по размеру без разбиения диалогов"""
    log_message("Группировка диалогов в батчи...")
    batches = []
    current_batch = []
    current_size = 0
    
    for d in dialogs:
        # Если один диалог сам по себе больше лимита, выделяем его в отдельный батч
        if d['length'] > target_size:
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_size = 0
            batches.append([d])
            continue
            
        if current_size + d['length'] > target_size:
            batches.append(current_batch)
            current_batch = [d]
            current_size = d['length']
        else:
            current_batch.append(d)
            current_size += d['length']
            
    if current_batch:
        batches.append(current_batch)
        
    log_message(f"Сформировано батчей: {len(batches)}")
    for idx, b in enumerate(batches):
        total_len = sum([d['length'] for d in b])
        log_message(f"  Батч {idx+1}: {len(b)} диалогов, суммарная длина {total_len} символов")
    return batches

def call_gemini_with_retry(prompt, max_retries=3, initial_delay=12):
    """Вызов Gemini API с ротацией моделей из пула и Exponential Backoff"""
    global current_model_idx
    delay = initial_delay
    attempt = 0
    
    while attempt < max_retries:
        m_name = MODEL_POOL[current_model_idx]
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content(prompt, request_options={"timeout": 90.0})
            
            # Извлекаем JSON
            text = response.text.strip()
            # Убираем markdown-обертку ```json если она есть
            if text.startswith('```json'):
                text = text.removeprefix('```json').removesuffix('```').strip()
            elif text.startswith('```'):
                text = text.removeprefix('```').removesuffix('```').strip()
            return text
            
        except exceptions.ResourceExhausted as e:
            # Если это ResourceExhausted, переключаемся на следующую модель из пула
            if current_model_idx < len(MODEL_POOL) - 1:
                old_model = MODEL_POOL[current_model_idx]
                current_model_idx += 1
                new_model = MODEL_POOL[current_model_idx]
                log_message(f"Модель {old_model} исчерпала лимиты (ResourceExhausted). Переключаюсь на {new_model}...")
                attempt = 0 # Сбрасываем попытки для новой модели
                delay = initial_delay
                time.sleep(2) # небольшая задержка перед переключением
            else:
                log_message(f"Все модели в пуле ({MODEL_POOL}) исчерпали лимиты. Ожидание {delay} сек...")
                time.sleep(delay)
                delay *= 2
                attempt += 1
                
        except exceptions.InternalServerError as e:
            log_message(f"Внутренняя ошибка сервера Gemini ({m_name}). Попытка {attempt+1}/{max_retries}. Ожидание {delay} сек...")
            time.sleep(delay)
            delay *= 2
            attempt += 1
            
        except Exception as e:
            log_message(f"Непредвиденная ошибка API ({m_name}): {e}. Попытка {attempt+1}/{max_retries}. Ожидание {delay} сек...")
            time.sleep(delay)
            delay *= 2
            attempt += 1
            
    raise Exception("Не удалось получить ответ ни от одной модели из пула.")

# ==========================================
# ОСНОВНОЙ ПРОЦЕСС
# ==========================================

def run(dry_run=False, limit_batches=None):
    log_message(f"=== ЗАПУСК СКРИПТА СОРТИРОВКИ (Dry-run: {dry_run}, Limit: {limit_batches}) ===")
    
    # 1. Сканируем файлы
    all_dialogs = []
    
    # Проверяем наличие conversations.json
    conv_json = os.path.join(RAW_DIR, "conversations.json")
    has_conv_json = os.path.exists(conv_json)
    
    raw_files = glob.glob(os.path.join(RAW_DIR, "*"))
    for file_path in raw_files:
        basename = os.path.basename(file_path)
        ext = os.path.splitext(basename)[1].lower()
        
        # Если есть conversations.json, игнорируем chat.html
        if basename == "chat.html" and has_conv_json:
            log_message("Пропуск chat.html (дубликат conversations.json)")
            continue
            
        if basename == "conversations.json":
            all_dialogs.extend(parse_conversations_json(file_path))
        elif basename.endswith(".html") and ("МоиДействия" in basename or "Мои_Действия" in basename):
            all_dialogs.extend(parse_gemini_takeout_html(file_path))
        elif ext == ".txt":
            # Проверяем, JSON ли это
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if content.startswith('{'):
                    all_dialogs.extend(parse_conversation_json_file(file_path))
                else:
                    log_message(f"Пропуск txt-файла (не JSON формат): {basename}")
            except Exception:
                log_message(f"Пропуск txt-файла (ошибка чтения): {basename}")
        else:
            if basename not in ["export_manifest.json", "conversation_asset_file_names.json", 
                                "library_files.json", "message_feedback.json", "shared_conversations.json",
                                "user.json", "user_settings.json"]:
                log_message(f"Пропуск файла (неизвестный формат): {basename}")

    log_message(f"\nВсего собрано диалогов: {len(all_dialogs)}")
    total_chars = sum([d['length'] for d in all_dialogs])
    log_message(f"Суммарный объем текста: {total_chars} символов (~{total_chars / 4:.0f} токенов)")
    
    if not all_dialogs:
        log_message("Диалоги не найдены. Выход.")
        return
        
    # 2. Группируем в батчи
    batches = make_batches(all_dialogs, target_size=300000)
    if limit_batches is not None:
        batches = batches[:limit_batches]
        log_message(f"Ограничение обработки: только первые {limit_batches} батчей.")
    
    if dry_run:
        log_message("\n=== РЕЖИМ DRY-RUN ЗАВЕРШЕН ===")
        log_message("Парсинг и батчинг прошли успешно. Файлы результатов не создавались.")
        return

    # 3. Обработка батчей через API
    stats = {"success_batches": 0, "failed_batches": 0}
    
    for idx, batch in enumerate(batches):
        log_message(f"\n--- Обработка батча {idx+1}/{len(batches)} ---")
        
        # Собираем текст батча
        batch_text = ""
        for d in batch:
            batch_text += d['text'] + "\n"
            
        prompt = PROMPT_TEMPLATE.format(chat_text=batch_text)
        
        try:
            # Делаем запрос в API
            log_message(f"Отправка батча {idx+1} в Gemini API...")
            json_text = call_gemini_with_retry(prompt)
            
            # Парсим полученный JSON
            try:
                data = json.loads(json_text, strict=False)
                log_message("Успешно получен и распарсен JSON от ИИ.")
                
                # Записываем результаты в соответствующие файлы
                for category, content in data.items():
                    if not content or len(content.strip()) < 10:
                        continue
                        
                    # Очищаем имя категории для безопасного имени файла
                    safe_category_name = "".join([c for c in category if c.isalpha() or c.isdigit() or c=='_']).strip()
                    out_file_name = f"{safe_category_name}.md"
                    out_file_path = os.path.join(OUTPUT_DIR, out_file_name)
                    
                    # Сохраняем в UTF-8 с BOM (utf-8-sig)
                    # Если файл уже существует, дописываем в конец
                    file_exists = os.path.exists(out_file_path)
                    
                    # Читаем старый контент, чтобы избежать дублирования BOM, если дописываем
                    if file_exists:
                        with open(out_file_path, 'a', encoding='utf-8-sig') as f_out:
                            f_out.write(f"\n\n\n\n\n# Из батча {idx+1}\n\n")
                            f_out.write(content)
                    else:
                        with open(out_file_path, 'w', encoding='utf-8-sig') as f_out:
                            f_out.write(f"# Категория: {category}\n\n")
                            f_out.write(content)
                            
                    log_message(f"  Добавлены данные в категорию: {safe_category_name}")
                    
                stats["success_batches"] += 1
                
            except json.JSONDecodeError as je:
                log_message(f"Ошибка парсинга JSON ответа от ИИ на батче {idx+1}: {je}")
                log_message("Попытка применить Loose-парсер на регулярных выражениях...")
                try:
                    # Попытка парсинга через регулярные выражения для плоских словарей JSON
                    pattern = r'"([a-zA-Zа-яА-Я0-9_]+)"\s*:\s*"(.*?)"(?=\s*,\s*"[a-zA-Zа-яА-Я0-9_]+"\s*:|\s*\}\s*$)'
                    matches = re.findall(pattern, json_text, re.DOTALL)
                    
                    if matches:
                        data = {}
                        for key, val in matches:
                            try:
                                decoded_val = json.loads(f'"{val}"')
                            except Exception:
                                decoded_val = val.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
                            data[key] = decoded_val
                            
                        log_message("Loose-парсер успешно извлек данные!")
                        for category, content in data.items():
                            if not content or len(content.strip()) < 10:
                                continue
                            
                            safe_category_name = "".join([c for c in category if c.isalpha() or c.isdigit() or c=='_']).strip()
                            out_file_name = f"{safe_category_name}.md"
                            out_file_path = os.path.join(OUTPUT_DIR, out_file_name)
                            
                            file_exists = os.path.exists(out_file_path)
                            if file_exists:
                                with open(out_file_path, 'a', encoding='utf-8-sig') as f_out:
                                    f_out.write(f"\n\n\n\n\n# Из батча {idx+1}\n\n")
                                    f_out.write(content)
                            else:
                                with open(out_file_path, 'w', encoding='utf-8-sig') as f_out:
                                    f_out.write(f"# Категория: {category}\n\n")
                                    f_out.write(content)
                                    
                            log_message(f"  Добавлены данные в категорию (Loose): {safe_category_name}")
                        stats["success_batches"] += 1
                    else:
                        log_message("Loose-парсер не нашел совпадений. Записываю сырой ответ в Неразобранное.md")
                        out_file_path = os.path.join(OUTPUT_DIR, "Неразобранное.md")
                        with open(out_file_path, 'a', encoding='utf-8-sig') as f_out:
                            f_out.write(f"\n\n\n\n\n# Сырой ответ ИИ из батча {idx+1} (Неразобранное)\n\n")
                            f_out.write(json_text)
                        stats["failed_batches"] += 1
                except Exception as loose_e:
                    log_message(f"Ошибка Loose-парсера: {loose_e}. Записываю сырой ответ в Неразобранное.md")
                    out_file_path = os.path.join(OUTPUT_DIR, "Неразобранное.md")
                    with open(out_file_path, 'a', encoding='utf-8-sig') as f_out:
                        f_out.write(f"\n\n\n\n\n# Сырой ответ ИИ из батча {idx+1} (Неразобранное из-за ошибки)\n\n")
                        f_out.write(json_text)
                    stats["failed_batches"] += 1
                
        except Exception as e:
            log_message(f"Ошибка обработки батча {idx+1}: {e}")
            stats["failed_batches"] += 1
            
        # Задержка между батчами для соблюдения лимитов
        log_message("Ожидание 12 секунд перед следующим батчем...")
        time.sleep(12)
        
    log_message("\n=== ИТОГОВЫЙ СЕБЯ-КОНТРОЛЬ (SELF-CHECK) ===")
    log_message(f"Успешно обработано батчей: {stats['success_batches']}")
    log_message(f"Батчей с ошибками: {stats['failed_batches']}")
    log_message("=== РАБОТА СКРИПТА СОРТИРОВКИ ЗАВЕРШЕНА ===")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Оптимизированный фильтр ИИ чатов")
    parser.add_argument("--run", action="store_true", help="Запустить реальную сортировку через Gemini API")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Запустить в режиме dry-run (без API)")
    parser.add_argument("--test-one-batch", action="store_true", help="Запустить тестовый прогон только на первом батче")
    args = parser.parse_args()
    
    if args.test_one_batch:
        run(dry_run=False, limit_batches=1)
    elif args.run:
        run(dry_run=False)
    else:
        # По умолчанию запускаем dry-run
        run(dry_run=True)
