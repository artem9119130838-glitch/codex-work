import os
import sys
import glob
import time
import json
import re
from google import generativeai as genai
from google.api_core import exceptions

# Добавляем папку src в пути поиска модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем базовые настройки и парсеры
from AI_chats_filter_optimized import (
    RAW_DIR, OUTPUT_DIR, API_KEY, PROMPT_TEMPLATE,
    parse_conversations_json, parse_gemini_takeout_html, parse_conversation_json_file,
    make_batches, log_message
)

# Переопределяем API-ключ для уверенности
genai.configure(api_key=API_KEY)

# Наш оптимизированный пул моделей (БЕЗ медленной Gemma)
RETRY_MODEL_POOL = [
    'gemini-flash-lite-latest',
    'gemini-flash-latest'
]
current_model_idx = 0

# Список упавших батчей (1-indexed)
FAILED_BATCH_NUMBERS = [20, 39, 40, 42, 44, 46]

def call_gemini_retry_pool(prompt, max_retries=3, initial_delay=12):
    """Вызов Gemini API с ротацией моделей из нового пула"""
    global current_model_idx
    delay = initial_delay
    attempt = 0
    
    while attempt < max_retries:
        m_name = RETRY_MODEL_POOL[current_model_idx]
        try:
            log_message(f"  Использую модель: {m_name}")
            model = genai.GenerativeModel(m_name)
            response = model.generate_content(prompt, request_options={"timeout": 90.0})
            
            text = response.text.strip()
            if text.startswith('```json'):
                text = text.removeprefix('```json').removesuffix('```').strip()
            elif text.startswith('```'):
                text = text.removeprefix('```').removesuffix('```').strip()
            return text
            
        except exceptions.ResourceExhausted as e:
            if current_model_idx < len(RETRY_MODEL_POOL) - 1:
                old_model = RETRY_MODEL_POOL[current_model_idx]
                current_model_idx += 1
                new_model = RETRY_MODEL_POOL[current_model_idx]
                log_message(f"Модель {old_model} исчерпала лимиты. Переключение на {new_model}...")
                attempt = 0
                delay = initial_delay
                time.sleep(2)
            else:
                log_message(f"Все модели в пуле исчерпали лимиты. Ожидание {delay} сек...")
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

def run_retry():
    log_message("\n=== ЗАПУСК ПОВТОРНОЙ ОБРАБОТКИ УПАВШИХ БАТЧЕЙ ===")
    
    # 1. Сканируем файлы (так же как в основном скрипте)
    all_dialogs = []
    conv_json = os.path.join(RAW_DIR, "conversations.json")
    has_conv_json = os.path.exists(conv_json)
    
    raw_files = glob.glob(os.path.join(RAW_DIR, "*"))
    for file_path in raw_files:
        basename = os.path.basename(file_path)
        ext = os.path.splitext(basename)[1].lower()
        
        if basename == "chat.html" and has_conv_json:
            continue
            
        if basename == "conversations.json":
            all_dialogs.extend(parse_conversations_json(file_path))
        elif basename.endswith(".html") and ("МоиДействия" in basename or "Мои_Действия" in basename):
            all_dialogs.extend(parse_gemini_takeout_html(file_path))
        elif ext == ".txt":
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if content.startswith('{'):
                    all_dialogs.extend(parse_conversation_json_file(file_path))
            except Exception:
                pass
                
    if not all_dialogs:
        log_message("Диалоги не найдены.")
        return
        
    # 2. Группируем в батчи
    batches = make_batches(all_dialogs, target_size=300000)
    
    # 3. Обрабатываем только упавшие батчи
    stats = {"success": 0, "failed": 0}
    
    for b_idx in FAILED_BATCH_NUMBERS:
        # Индекс в Python 0-indexed, номера батчей 1-indexed
        actual_idx = b_idx - 1
        if actual_idx >= len(batches):
            log_message(f"Ошибка: батч {b_idx} не существует в текущей выборке.")
            continue
            
        batch = batches[actual_idx]
        log_message(f"\n--- Повторная обработка батча {b_idx}/{len(batches)} ---")
        
        batch_text = ""
        for d in batch:
            batch_text += d['text'] + "\n"
            
        prompt = PROMPT_TEMPLATE.format(chat_text=batch_text)
        
        try:
            log_message(f"Отправка батча {b_idx} в Gemini API...")
            json_text = call_gemini_retry_pool(prompt)
            
            # Парсим JSON
            try:
                data = json.loads(json_text, strict=False)
                log_message(f"Успешно получен и распарсен JSON от ИИ для батча {b_idx}.")
                
                for category, content in data.items():
                    if not content or len(content.strip()) < 10:
                        continue
                        
                    safe_category_name = "".join([c for c in category if c.isalpha() or c.isdigit() or c=='_']).strip()
                    out_file_name = f"{safe_category_name}.md"
                    out_file_path = os.path.join(OUTPUT_DIR, out_file_name)
                    
                    file_exists = os.path.exists(out_file_path)
                    if file_exists:
                        with open(out_file_path, 'a', encoding='utf-8-sig') as f_out:
                            f_out.write(f"\n\n\n\n\n# Из батча {b_idx}\n\n")
                            f_out.write(content)
                    else:
                        with open(out_file_path, 'w', encoding='utf-8-sig') as f_out:
                            f_out.write(f"# Категория: {category}\n\n")
                            f_out.write(content)
                            
                    log_message(f"  Добавлены данные в категорию: {safe_category_name}")
                stats["success"] += 1
                
            except json.JSONDecodeError as je:
                log_message(f"Ошибка парсинга JSON для батча {b_idx}: {je}")
                log_message("Попытка применить Loose-парсер...")
                try:
                    pattern = r'"([a-zA-Zа-яА-Я0-9_]+)"\s*:\s*"(.*?)"(?=\s*,\s*"[a-zA-Zа-яА-Я0-9_]+"\s*:|\s*\}\s*$)'
                    matches = re.findall(pattern, json_text, re.DOTALL)
                    
                    if matches:
                        for key, val in matches:
                            try:
                                decoded_val = json.loads(f'"{val}"')
                            except Exception:
                                decoded_val = val.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
                                
                            if not decoded_val or len(decoded_val.strip()) < 10:
                                continue
                                
                            safe_category_name = "".join([c for c in key if c.isalpha() or c.isdigit() or c=='_']).strip()
                            out_file_name = f"{safe_category_name}.md"
                            out_file_path = os.path.join(OUTPUT_DIR, out_file_name)
                            
                            file_exists = os.path.exists(out_file_path)
                            if file_exists:
                                with open(out_file_path, 'a', encoding='utf-8-sig') as f_out:
                                    f_out.write(f"\n\n\n\n\n# Из батча {b_idx} (Loose)\n\n")
                                    f_out.write(decoded_val)
                            else:
                                with open(out_file_path, 'w', encoding='utf-8-sig') as f_out:
                                    f_out.write(f"# Категория: {key}\n\n")
                                    f_out.write(decoded_val)
                            log_message(f"  Добавлены данные в категорию (Loose): {safe_category_name}")
                        stats["success"] += 1
                    else:
                        log_message(f"Loose-парсер не справился с батчем {b_idx}. Пишу в Неразобранное_retry.md")
                        out_file_path = os.path.join(OUTPUT_DIR, "Неразобранное_retry.md")
                        with open(out_file_path, 'a', encoding='utf-8-sig') as f_out:
                            f_out.write(f"\n\n# Сырой ответ из повторного батча {b_idx}\n\n{json_text}")
                        stats["failed"] += 1
                except Exception as loose_e:
                    log_message(f"Ошибка Loose-парсера: {loose_e}")
                    stats["failed"] += 1
                    
        except Exception as e:
            log_message(f"Ошибка обработки батча {b_idx}: {e}")
            stats["failed"] += 1
            
        log_message("Ожидание 20 секунд...")
        time.sleep(20)
        
    log_message("\n=== ИТОГ ПОВТОРНОЙ ОБРАБОТКИ ===")
    log_message(f"Успешно обработано батчей: {stats['success']}")
    log_message(f"Упало батчей: {stats['failed']}")
    log_message("=== ЗАВЕРШЕНО ===")

if __name__ == '__main__':
    run_retry()
