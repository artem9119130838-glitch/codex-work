import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "done")
UNRESOLVED_PATH = os.path.join(OUTPUT_DIR, "Неразобранное.md")
SEO_PATH = os.path.join(OUTPUT_DIR, "SEO_и_Контент.md")
COMMERCE_PATH = os.path.join(OUTPUT_DIR, "Коммерция_и_Маркетинг.md")

def log(msg):
    print(msg)

def append_to_file(filename, text, batch_num=None):
    filepath = os.path.join(OUTPUT_DIR, filename)
    file_exists = os.path.exists(filepath)
    
    # Очищаем имя категории для безопасности
    safe_name = "".join([c for c in filename if c.isalnum() or c in '._-']).strip()
    filepath = os.path.join(OUTPUT_DIR, safe_name)
    
    header = f"\n\n\n\n\n# Перенесено из неразобранного (Батч {batch_num or '?'})\n\n"
    
    if file_exists:
        with open(filepath, 'a', encoding='utf-8-sig') as f:
            f.write(header)
            f.write(text.strip())
    else:
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(f"# Категория: {os.path.splitext(safe_name)[0]}\n\n")
            f.write(text.strip())
    log(f"  Дописано в {safe_name} ({len(text)} симв.)")

def clean_value(val):
    """Очистка строкового значения из Loose-парсера"""
    try:
        # Пытаемся раскодировать JSON-строку
        return json.loads(f'"{val}"')
    except Exception:
        # Ручная замена экранированных символов
        return val.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')

def parse_json_block(text, batch_num):
    # Ищем первую { и последнюю }
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx == -1 or end_idx == -1:
        log(f"  Не найдены скобки {{}} в батче {batch_num}")
        return False
        
    json_text = text[start_idx:end_idx+1]
    
    # Пробуем обычный парсинг
    try:
        data = json.loads(json_text, strict=False)
        log(f"  Батч {batch_num}: успешно распарсен стандартным JSON-парсером.")
        for cat, val in data.items():
            if not val or len(val.strip()) < 10:
                continue
            target_file = get_target_file_by_category(cat)
            append_to_file(target_file, val, batch_num)
        return True
    except Exception as e:
        log(f"  Батч {batch_num}: стандартный JSON упал ({e}). Пробуем Loose-парсер...")
        
    # Loose-парсер по регулярным выражениям
    # Ищем ключи и текстовые значения в кавычках
    pattern = r'"([a-zA-Zа-яА-Я0-9_ -]+)"\s*:\s*"(.*?)"(?=\s*,\s*"[a-zA-Zа-яА-Я0-9_ -]+"\s*:|\s*\}\s*$)'
    matches = re.findall(pattern, json_text, re.DOTALL)
    
    if matches:
        log(f"  Loose-парсер извлек {len(matches)} категорий.")
        for key, val in matches:
            decoded_val = clean_value(val)
            if not decoded_val or len(decoded_val.strip()) < 10:
                continue
            target_file = get_target_file_by_category(key)
            append_to_file(target_file, decoded_val, batch_num)
        return True
    else:
        log(f"  Loose-парсер не нашел совпадений в батче {batch_num}.")
        return False

def get_target_file_by_category(cat):
    cat_lower = cat.lower().strip()
    if "коммерция" in cat_lower or "маркетинг" in cat_lower or "commerce" in cat_lower:
        return "Коммерция_и_Маркетинг.md"
    elif "автоматизация" in cat_lower or "automation" in cat_lower:
        return "Автоматизация.md"
    elif "управление" in cat_lower or "team" in cat_lower or "hr" in cat_lower:
        return "Управление_командой.md"
    elif "техник" in cat_lower or "личн" in cat_lower or "personal" in cat_lower:
        return "Техника_и_Личное.md"
    elif "здоров" in cat_lower or "health" in cat_lower:
        return "Здоровье.md"
    elif "финанс" in cat_lower or "налог" in cat_lower or "бухгалтер" in cat_lower or "инвест" in cat_lower or "юрисп" in cat_lower or "право" in cat_lower or "law" in cat_lower:
        # Сливаем мелкие финансовые в более крупные, но пока пишем в Финансы_и_Юриспруденция.md
        if "право" in cat_lower or "юрисп" in cat_lower or "law" in cat_lower:
            return "Финансы_и_Юриспруденция.md"
        else:
            return "Финансы_и_Налоги.md"
    else:
        # Для всех остальных
        safe_name = "".join([c for c in cat if c.isalnum() or c == '_']).strip()
        return f"{safe_name}.md"

def merge_seo_and_content():
    """Слияние SEO_и_Контент.md в Коммерция_и_Маркетинг.md"""
    if not os.path.exists(SEO_PATH):
        log("SEO_и_Контент.md не существует, слияние не требуется.")
        return
        
    log("Слияние SEO_и_Контент.md в Коммерция_и_Маркетинг.md...")
    with open(SEO_PATH, 'r', encoding='utf-8-sig') as f:
        seo_text = f.read()
        
    # Убираем заголовок категории
    if seo_text.startswith("# Категория:"):
        seo_text = seo_text[seo_text.find('\n'):].strip()
        
    append_to_file("Коммерция_и_Маркетинг.md", seo_text, "SEO_Слияние")
    
    os.remove(SEO_PATH)
    log("Файл SEO_и_Контент.md успешно удален.")

def process_unresolved():
    if not os.path.exists(UNRESOLVED_PATH):
        log("Файл Неразобранное.md не найден. Выход.")
        return
        
    with open(UNRESOLVED_PATH, 'r', encoding='utf-8-sig') as f:
        content = f.read()
        
    # Разрезаем по батчам
    batches = re.split(r'# Сырой ответ ИИ из батча (\d+).*?\n', content)
    
    if len(batches) < 2:
        log("Батчи в Неразобранное.md не обнаружены.")
        return
        
    # Первое разделение дает пустую строку или преамбулу перед первым батчем
    # batches[1] - номер 1-го батча, batches[2] - текст 1-го батча
    # batches[3] - номер 2-го батча, batches[4] - текст 2-го батча и т.д.
    
    for i in range(1, len(batches), 2):
        batch_num = batches[i]
        batch_text = batches[i+1].strip()
        
        log(f"\nРазбор батча {batch_num}...")
        
        # Определяем тип: JSON или прямой Markdown
        has_braces = '{' in batch_text and '}' in batch_text
        
        processed = False
        if has_braces:
            processed = parse_json_block(batch_text, batch_num)
            
        if not processed:
            # Прямой Markdown переносим по эвристикам на весь текст батча
            log(f"  Определение категории для прямого Markdown батча {batch_num}...")
            
            # Эвристика по ключевым словам
            text_lower = batch_text.lower()
            
            if "freefilesync" in text_lower or "синхронизац" in text_lower and "ноутбук" in text_lower:
                target_file = "Техника_и_Личное.md"
            elif "seo" in text_lower or "longwang.ru" in text_lower or "тендер" in text_lower or "закупк" in text_lower or "вэд" in text_lower:
                target_file = "Коммерция_и_Маркетинг.md"
            elif "autohotkey" in text_lower or "ahk" in text_lower:
                target_file = "Автоматизация.md"
            elif "hr" in text_lower or "ваканси" in text_lower or "найм" in text_lower or "kpi" in text_lower:
                target_file = "Управление_командой.md"
            else:
                target_file = "Общие_Знания.md"
                
            append_to_file(target_file, batch_text, batch_num)

if __name__ == '__main__':
    log("=== Запуск разбора Неразобранное.md ===")
    process_unresolved()
    merge_seo_and_content()
    
    # Очищаем Неразобранное.md
    if os.path.exists(UNRESOLVED_PATH):
        os.remove(UNRESOLVED_PATH)
        log("\nУдален файл Неразобранное.md")
        
    log("=== Разбор завершен ===")
