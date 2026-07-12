import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "done")
UNRESOLVED_PATH = os.path.join(OUTPUT_DIR, "Неразобранное_recovered.md")

def log(msg):
    print(msg)

def append_to_file(filename, text, batch_num=None):
    filepath = os.path.join(OUTPUT_DIR, filename)
    file_exists = os.path.exists(filepath)
    
    safe_name = "".join([c for c in filename if c.isalnum() or c in '._-']).strip()
    filepath = os.path.join(OUTPUT_DIR, safe_name)
    
    header = f"\n\n\n\n\n# Перенесено из неразобранного (Восстановленный Батч {batch_num or '?'})\n\n"
    
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
    try:
        return json.loads(f'"{val}"')
    except Exception:
        return val.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')

def parse_json_block(text, batch_num):
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx == -1 or end_idx == -1:
        log(f"  Не найдены скобки {{}} в батче {batch_num}")
        return False
        
    json_text = text[start_idx:end_idx+1]
    
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
    elif "техник" in cat_lower or "личн" in cat_lower or "personal" in cat_lower or "путешеств" in cat_lower or "travel" in cat_lower:
        return "Техника_и_Личное.md"
    elif "здоров" in cat_lower or "health" in cat_lower:
        return "Здоровье.md"
    elif "финанс" in cat_lower or "налог" in cat_lower or "бухгалтер" in cat_lower or "инвест" in cat_lower or "юрисп" in cat_lower or "право" in cat_lower or "law" in cat_lower or "крипто" in cat_lower:
        return "Финансы_и_Право.md"
    else:
        safe_name = "".join([c for c in cat if c.isalnum() or c == '_']).strip()
        return f"{safe_name}.md"

def process_unresolved():
    if not os.path.exists(UNRESOLVED_PATH):
        log("Файл Неразобранное_recovered.md не найден. Выход.")
        return
        
    with open(UNRESOLVED_PATH, 'r', encoding='utf-8-sig') as f:
        content = f.read()
        
    batches = re.split(r'# Raw response from recovered batch (\d+) sub-batch (\d+).*?\n', content)
    
    if len(batches) < 3:
        log("Батчи в Неразобранное_recovered.md не обнаружены.")
        return
        
    for i in range(1, len(batches), 3):
        batch_num = batches[i]
        sub_batch_num = batches[i+1]
        batch_text = batches[i+2].strip()
        
        log(f"\nРазбор восстановленного батча {batch_num} (суб-батч {sub_batch_num})...")
        
        has_braces = '{' in batch_text and '}' in batch_text
        processed = False
        if has_braces:
            processed = parse_json_block(batch_text, f"{batch_num}_sub_{sub_batch_num}")
            
        if not processed:
            log(f"  Определение категории для прямого Markdown батча {batch_num}...")
            text_lower = batch_text.lower()
            
            if "freefilesync" in text_lower or "синхронизац" in text_lower or "iphone" in text_lower or "keenetic" in text_lower:
                target_file = "Техника_и_Личное.md"
            elif "seo" in text_lower or "siemens" in text_lower or "hmi" in text_lower or "ozon" in text_lower:
                target_file = "Коммерция_и_Маркетинг.md"
            elif "n8n" in text_lower or "autohotkey" in text_lower or "web data" in text_lower:
                target_file = "Автоматизация.md"
            elif "hr" in text_lower or "kpi" in text_lower:
                target_file = "Управление_командой.md"
            else:
                target_file = "Общие_Знания.md"
                
            append_to_file(target_file, batch_text, f"{batch_num}_sub_{sub_batch_num}")

if __name__ == '__main__':
    log("=== Запуск разбора Неразобранное_recovered.md ===")
    process_unresolved()
    
    if os.path.exists(UNRESOLVED_PATH):
        os.remove(UNRESOLVED_PATH)
        log("\nУдален файл Неразобранное_recovered.md")
        
    log("=== Разбор завершен ===")
