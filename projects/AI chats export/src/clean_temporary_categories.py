import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "done")

cat_name_path = os.path.join(OUTPUT_DIR, "CategoryName.md")
cat_name_underscore_path = os.path.join(OUTPUT_DIR, "Category_Name.md")

def append_to_file(filename, text):
    filepath = os.path.join(OUTPUT_DIR, filename)
    file_exists = os.path.exists(filepath)
    
    # Записываем в utf-8-sig (UTF-8 с BOM)
    if file_exists:
        with open(filepath, 'a', encoding='utf-8-sig') as f:
            f.write("\n\n\n\n\n# Перенесено из временной категории\n\n")
            f.write(text.strip())
    else:
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(text.strip())
    print(f"Добавлены данные в {filename} ({len(text)} символов)")

def process_category_name():
    if not os.path.exists(cat_name_path):
        print(f"Файл {cat_name_path} не найден. Пропуск.")
        return
        
    with open(cat_name_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
        
    # 1. Извлекаем блок для "Техника_и_Личное"
    start_tech = content.find("## Решение проблем с HTTPS и TLS")
    end_tech = content.find("# Из батча 45")
    
    if start_tech != -1 and end_tech != -1:
        tech_text = content[start_tech:end_tech].strip()
        # Убираем возможный мусор в конце
        tech_text = tech_text.rstrip('` \t\n}')
        append_to_file("Техника_и_Личное.md", tech_text)
    else:
        print("Не удалось найти границы блока Техника_и_Личное в CategoryName.md")
        
    # 2. Извлекаем блок для "Здоровье"
    start_health = content.find("# Здоровье и Физическая форма")
    if start_health != -1:
        health_text = content[start_health:].strip()
        # Очищаем от кавычек и фигурных скобок на конце, если они есть
        health_text = health_text.rstrip('` \t\n}"')
        append_to_file("Здоровье.md", health_text)
    else:
        print("Не удалось найти блок Здоровье в CategoryName.md")

def process_category_name_underscore():
    if not os.path.exists(cat_name_underscore_path):
        print(f"Файл {cat_name_underscore_path} не найден. Пропуск.")
        return
        
    with open(cat_name_underscore_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
        
    # Извлекаем блок для "Управление_командой"
    start_team = content.find("## HR-Стратегия и Главный Контекст")
    if start_team != -1:
        team_text = content[start_team:].strip()
        # Очищаем от кавычек и фигурных скобок на конце
        team_text = team_text.rstrip('` \t\n}"')
        append_to_file("Управление_командой.md", team_text)
    else:
        print("Не удалось найти блок Управление_командой в Category_Name.md")

if __name__ == '__main__':
    print("=== Старт переноса временных категорий ===")
    process_category_name()
    process_category_name_underscore()
    
    # Удаляем временные файлы
    if os.path.exists(cat_name_path):
        os.remove(cat_name_path)
        print(f"Удален временный файл: {cat_name_path}")
    if os.path.exists(cat_name_underscore_path):
        os.remove(cat_name_underscore_path)
        print(f"Удален временный файл: {cat_name_underscore_path}")
        
    print("=== Перенос завершен ===")
