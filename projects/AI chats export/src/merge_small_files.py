import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "done")

def log(msg):
    print(msg)

def read_and_clean_file(filepath):
    """Чтение файла и удаление заголовка категории"""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        text = f.read().strip()
    
    # Убираем заголовок вида "# Категория: ..."
    if text.startswith("# Категория:"):
        first_newline = text.find('\n')
        if first_newline != -1:
            text = text[first_newline:].strip()
    return text

def merge_files(target_name, source_names):
    target_path = os.path.join(OUTPUT_DIR, target_name)
    merged_content = ""
    
    # Читаем существующий контент целевого файла, если есть
    if os.path.exists(target_path):
        merged_content = read_and_clean_file(target_path)
        
    for src_name in source_names:
        src_path = os.path.join(OUTPUT_DIR, src_name)
        if os.path.exists(src_path):
            src_text = read_and_clean_file(src_path)
            if src_text:
                header = f"\n\n\n\n\n# Раздел: {os.path.splitext(src_name)[0].replace('_', ' ')}\n\n"
                merged_content += header + src_text
                
    if merged_content.strip():
        # Сохраняем объединенный файл в utf-8-sig
        with open(target_path, 'w', encoding='utf-8-sig') as f:
            f.write(f"# Категория: {os.path.splitext(target_name)[0]}\n\n")
            f.write(merged_content.strip())
        log(f"Успешно создан объединенный файл: {target_name} ({len(merged_content)} симв.)")
        
        # Удаляем исходные мелкие файлы
        for src_name in source_names:
            src_path = os.path.join(OUTPUT_DIR, src_name)
            if os.path.exists(src_path) and src_name != target_name:
                os.remove(src_path)
                log(f"  Удален мелкий файл: {src_name}")
    else:
        log(f"Нет данных для объединения в {target_name}")

if __name__ == '__main__':
    log("=== Старт слияния мелких файлов ===")
    
    # 1. Слияние Автоматизация
    merge_files("Автоматизация.md", [
        "Автоматизация_и_IT.md",
        "Автоматизация_и_Разработка.md"
    ])
    
    # 2. Слияние Финансы и Право
    finance_sources = [
        "Финансы_и_Бухгалтерия.md",
        "Финансы_и_Инвестиции.md",
        "Финансы_и_Налоги.md",
        "Финансы_и_Юриспруденция.md",
        "Финансы_и_Криптовалюта.md"
    ]
    merge_files("Финансы_и_Право.md", finance_sources)
    
    # 3. Слияние Техника и Личное
    personal_sources = [
        "Личные_Настройки_и_Инструменты.md",
        "Путешествия.md",
        "Путешествия_и_Логистика.md"
    ]
    merge_files("Техника_и_Личное.md", personal_sources)
    
    # 4. Слияние Управление командой
    team_sources = [
        "Маркетинг_и_Управление_Проектами.md",
        "Управление_Проектами.md",
        "Организация_и_Планирование.md"
    ]
    merge_files("Управление_командой.md", team_sources)
    
    # 5. Слияние Общие Знания
    merge_files("Общие_Знания.md", [
        "Переводы_и_Международное_Общение.md"
    ])
    
    log("=== Слияние мелких файлов завершено ===")

