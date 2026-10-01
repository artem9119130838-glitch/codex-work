"""
Скрипт наведения порядка на рабочем столе текущего пользователя.
Поддерживает режим --dry-run (по умолчанию) и --execute (боевой запуск).
Соблюдает строгий whitelist, правила вложенности и шаблон ВЭД-отправок.
"""

import os
import sys
import io
import shutil
import argparse
from pathlib import Path

# Обеспечиваем корректный вывод UTF-8 в консоль
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Список объектов на рабочем столе, которые СТРОГО ЗАПРЕЩЕНО перемещать или изменять
STRICT_WHITELIST = {
    "desktop.ini",
    "Artem-Home.lnk",
    "Мышь.lnk",
    "Soft",
    "Презентация и референс-лист.pdf",
    "ЛУНВАН.cer",
    "Ци Линь.pfx",
    "ИП Павлова.cer",
    "Пароли.txt",
    "ПАМЯТКА_ГДЕ_МОИ_ФАЙЛЫ.txt",
}

SYNC_ROOT = Path(r"D:\Документы Sync E")
DESKTOP = Path(os.environ["USERPROFILE"]) / "Desktop"

# Шаблоны стандартных подпапок ВЭД-отправки (уровень 4)
VED_SUBFOLDERS = [
    "тех описание",
    "бух документы",
    "фото",
    "перевозочные документы",
    "расчеты брокера",
    "ДС и СС",
]


def classify_items(items):
    """
    Классифицирует файлы и папки с рабочего стола по целевым путям.
    Возвращает словарь: { item_name: { 'action': 'move'|'delete', 'dest': Path, 'category': str } }
    """
    plan = {}

    # Целевые базовые директории
    ved_root = SYNC_ROOT / "Рабочее" / "В работе" / "Белые отправки"
    gidramax_dir = SYNC_ROOT / "Рабочее" / "В работе" / "Гидрамакс (Логистиктранс)" / "Готовые цилиндры"
    customs_jde = SYNC_ROOT / "Рабочее" / "Таможня" / "ГТД ЛВ" / "Янтарный комбинат ЖДЭ"
    marketing_blanks = SYNC_ROOT / "Рабочее" / "Маркетинг" / "Бланки"
    
    lika_dover = SYNC_ROOT / "Лика" / "Доверенности"
    lika_ff = SYNC_ROOT / "Лика" / "Маркетплэйсы" / "ФФ"
    lika_buh = SYNC_ROOT / "Лика" / "Бух Нов"
    
    temp_dir = SYNC_ROOT / "Общая папка_TEMP" / "Временное_Desktop_2026-10-01"

    # Папка отправки Ци Линь Проекторы (уровень 4)
    cilin_shipment = ved_root / "2026-09 Ци Линь Проекторы (DATL300926)"
    # Папка контейнера Белый Раст (уровень 4)
    white_rust_shipment = ved_root / "2026-09 Контейнер CICU2663734 (Белый Раст)"

    for name in items:
        # Пропуск whitelist
        if name in STRICT_WHITELIST:
            continue

        # 1. Временные lock-файлы Office
        if name.startswith("~$"):
            plan[name] = {
                "action": "delete",
                "dest": None,
                "category": "Удаление временного lock-файла Office",
            }
            continue

        # 2. Гидрамакс / готовые цилиндры
        if name in [
            "drawings.pdf",
            "tech agreement_cn translate.docx",
            "ТЗ готовые цилиндры (финал) (1).pdf",
            "Приложение №6 к Договору № 62_ 23 04 26 (руб.) ГИДРОЦИЛИНДРЫ (1).pdf",
        ]:
            plan[name] = {
                "action": "move",
                "dest": gidramax_dir / name,
                "category": "Гидрамакс / Цилиндры",
            }
            continue

        # 3. Белый Раст / контейнер
        if name in ["Ббелый раст", "Пакет таможенных документов", "Пакет таможенных документов.rar", "ЦЛ лента разметки.pdf"]:
            plan[name] = {
                "action": "move",
                "dest": white_rust_shipment / "перевозочные документы" / name,
                "category": "ВЭД: Контейнер Белый Раст",
            }
            continue

        # 4. Отправка Ци Линь (Проекторы DATL300926)
        # 4.1 Расчеты брокера
        if name in [
            "Расчет_пошлин_и_НДС_ЦиЛинь_DATL300926.xlsx",
            "Расчет_пошлин_и_НДС_ЦиЛинь_DATL300926_v2.xlsx",
            "Брокеру.xlsx",
            "итоговый вывод по брокеру.docx",
            "Что сделал брокер Брокер вписал в предварительный.docx",
        ]:
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "расчеты брокера" / name,
                "category": "ВЭД: Расчеты брокера",
            }
            continue

        # 4.2 Перевозочные документы
        if name in [
            "Транзитная декларация TDGU7014370_38164843.pdf",
            "Экспортная декларация.pdf",
            "280926Копия 2-随车文件模板-圣彼得堡（需要盖章）(2)(1)(1)_20260907163937.pdf",
            "DAT",
        ]:
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "перевозочные документы" / name,
                "category": "ВЭД: Перевозочные документы",
            }
            continue

        # 4.3 Бухгалтерские документы ВЭД
        if name in [
            "Инвойс контракт пакинг.xlsx",
            "Инвойс_на_доставку_KFC2608125  dn.pdf",
            "VBK_26060023_0436_0000_2_1.pdf",
            "заявление о постановке на учет контракта 260600230436000021.pdf",
            "Письмо об отсутсвии страхования.pdf",
            "Письмо об отсутствии страх и лицензионных платежей и прочих затрат.pdf",
            "Письмо об отсутствии страх и лицензионных платежей и прочих затрат_2023.doc",
            "Письмо об отсутствии ШКС.docx",
        ]:
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "бух документы" / name,
                "category": "ВЭД: Бухгалтерские документы",
            }
            continue

        # 4.4 Техническое описание
        if name in [
            "Тех описание товара.docx",
            "Список и описание 5 (2).xlsx",
            "Данные по грузу.xlsx",
        ]:
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "тех описание" / name,
                "category": "ВЭД: Техническое описание",
            }
            continue

        # 4.5 ДС и СС
        if name in [
            "004-020-037 Проектор Заводской 30.09.2026.pdf",
            "21951495 от 28.09.2026.pdf",
            "21951550 от 28.09.2026.pdf",
            "a13b8da3-bafe-11f1-b99a-2755aca75ee3.pdf",
        ]:
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "ДС и СС" / name,
                "category": "ВЭД: Декларации и сертификаты (ДС/СС)",
            }
            continue

        # 4.6 Фото
        if name == "фото.rar":
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "фото" / name,
                "category": "ВЭД: Фото архива поставки",
            }
            continue

        # 5. Лика
        if name == "образец_доверенностиподит.docx":
            plan[name] = {"action": "move", "dest": lika_dover / name, "category": "Лика: Доверенности"}
            continue
        if name == "Фулфиллмент письмо.docx":
            plan[name] = {"action": "move", "dest": lika_ff / name, "category": "Лика: Маркетплейсы ФФ"}
            continue
        if name in ["УПД № 81 от 14.09.26 г..pdf", "Pavlova_20260923234303.pdf", "Инструкция_опо_оплате_ФАУ_НИА_ЛК_1.pdf"]:
            plan[name] = {"action": "move", "dest": lika_buh / name, "category": "Лика: Бухгалтерия"}
            continue

        # 6. Отгрузка ЖДЭ и Бланки
        if name == "Янтарный комбинат ЖДЭ":
            plan[name] = {"action": "move", "dest": customs_jde, "category": "Рабочее: Таможня ЖДЭ"}
            continue
        if name == "Бланк Ци Линь новый.docx":
            plan[name] = {"action": "move", "dest": marketing_blanks / name, "category": "Рабочее: Маркетинг бланки"}
            continue

        # 7. Папка Временное
        if name == "Временное":
            plan[name] = {"action": "move", "dest": temp_dir, "category": "Общая папка TEMP"}
            continue

        # Фолбэк для неопознанных файлов: отправляем в общую временную папку
        plan[name] = {
            "action": "move",
            "dest": SYNC_ROOT / "Общая папка_TEMP" / "Desktop_Unsorted_2026-10-01" / name,
            "category": "Общая папка TEMP (Несортированное)",
        }

    return plan


def generate_memo_content(plan):
    """Генерирует текст памятки для рабочего стола."""
    lines = [
        "=================================================================",
        "        ПАМЯТКА: РАСПРЕДЕЛЕНИЕ ФАЙЛОВ С РАБОЧЕГО СТОЛА           ",
        "                Дата наведения порядка: 01.10.2026               ",
        "=================================================================",
        "",
        "Анжелика, привет! Рабочий стол очищен от временных файлов.",
        "Все рабочие документы бережно разложены по постоянным папкам:",
        "",
        "1. ВЭД ПОСТАВКА: ПРОЕКТОРЫ ЦИ ЛИНЬ (DATL300926)",
        "   Путь: D:\\Документы Sync E\\Рабочее\\В работе\\Белые отправки\\2026-09 Ци Линь Проекторы (DATL300926)\\",
        "   - расчеты брокера/     -> Расчеты пошлин, выводы по брокеру, Брокеру.xlsx",
        "   - перевозочные доки/   -> Транзитная, Экспортная декларации, папка DAT",
        "   - бух документы/       -> Инвойсы, контракт, пакинг, ВБК, письма об отсутствии затрат",
        "   - тех описание/        -> Тех описание товара, Список и описание, Данные по грузу",
        "   - ДС и СС/             -> Декларации соответствия на проекторы (004-020-037, 21951...)",
        "   - фото/                -> Архив фото.rar",
        "",
        "2. ВЭД ПОСТАВКА: КОНТЕЙНЕР БЕЛЫЙ РАСТ (CICU2663734)",
        "   Путь: D:\\Документы Sync E\\Рабочее\\В работе\\Белые отправки\\2026-09 Контейнер CICU2663734 (Белый Раст)\\",
        "   - Папка 'Ббелый раст', 'Пакет таможенных документов', СМГС, лента разметки",
        "",
        "3. ГИДРАМАКС / ГОТОВЫЕ ЦИЛИНДРЫ",
        "   Путь: D:\\Документы Sync E\\Рабочее\\В работе\\Гидрамакс (Логистиктранс)\\Готовые цилиндры\\",
        "   - drawings.pdf, tech agreement, ТЗ готовые цилиндры, Приложение №6 к Договору 62",
        "",
        "4. ДОКУМЕНТЫ АНЖЕЛИКИ (ПАПКА ЛИКА)",
        "   - Бухгалтерия: D:\\Документы Sync E\\Лика\\Бух Нов\\ (УПД №81, Pavlova, оплата ФАУ НИА)",
        "   - Доверенности: D:\\Документы Sync E\\Лика\\Доверенности\\ (образец доверенности)",
        "   - Маркетплейсы: D:\\Документы Sync E\\Лика\\Маркетплэйсы\\ФФ\\ (Фулфиллмент письмо)",
        "",
        "5. ОТГРУЗКА ЖДЭ И ВРЕМЕННЫЕ ПАПКИ",
        "   - Янтарный комбинат ЖДЭ -> D:\\Документы Sync E\\Рабочее\\Таможня\\ГТД ЛВ\\Янтарный комбинат ЖДЭ\\",
        "   - Папка 'Временное'     -> D:\\Документы Sync E\\Общая папка_TEMP\\Временное_Desktop_2026-10-01\\",
        "",
        "6. ЧТО ОСТАЛОСЬ НА РАБОЧЕМ СТОЛЕ БЕЗ ИЗМЕНЕНИЙ:",
        "   - Пароли.txt (строго на месте)",
        "   - Сертификаты ЭП: ЛУНВАН.cer, ИП Павлова.cer, Ци Линь.pfx",
        "   - Ярлыки: Artem-Home, Мышь, папка Soft, Презентация и референс-лист",
        "",
        "-----------------------------------------------------------------",
        "ПОДСКАЗКА: Любой файл можно моментально найти через поиск Everything",
        "(значок лупы в трее или поиск по названию файла).",
        "=================================================================",
    ]
    return "\n".join(lines)


def run_cleanup(execute=False):
    desktop_items = os.listdir(DESKTOP)
    plan = classify_items(desktop_items)

    print(f"=== РЕЖИМ: {'БОЕВОЙ ЗАПУСК (--execute)' if execute else 'ПРОВЕРКА (--dry-run)'} ===")
    print(f"Всего объектов на рабочем столе: {len(desktop_items)}")
    print(f"Объектов в Whitelist (не трогаем): {len(desktop_items) - len(plan)}")
    print(f"Объектов к обработке: {len(plan)}\n")

    # Сводка по категориям
    categories = {}
    for item, info in plan.items():
        categories.setdefault(info["category"], []).append(item)

    for cat, items in categories.items():
        print(f"[{cat}] ({len(items)} объектов):")
        for it in sorted(items):
            dest_str = str(plan[it]["dest"]) if plan[it]["dest"] else "Recycle Bin / Удаление"
            print(f"   - {it} -> {dest_str}")

    if not execute:
        print("\n[DRY-RUN ЗАВЕРШЕН] Файлы не перемещались. Для выполнения запустите с флагом --execute.")
        return True

    # Боевой запуск
    print("\n--- ВЫПОЛНЕНИЕ ПЕРЕНОСА ---")
    success_count = 0
    errors = []

    for item, info in plan.items():
        src = DESKTOP / item
        if not src.exists():
            continue

        if info["action"] == "delete":
            try:
                if src.is_file():
                    src.unlink()
                else:
                    shutil.rmtree(src)
                print(f"[УДАЛЕНО] {item}")
                success_count += 1
            except Exception as e:
                errors.append(f"Ошибка удаления {item}: {e}")
                print(f"[ОШИБКА УДАЛЕНИЯ] {item}: {e}")
            continue

        if info["action"] == "move":
            dest = info["dest"]
            try:
                # Создаем родительские папки
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                # Если целевой файл/папка уже существует - переименовываем с суффиксом
                final_dest = dest
                if final_dest.exists():
                    stem = dest.stem if dest.is_file() else dest.name
                    suffix = dest.suffix if dest.is_file() else ""
                    final_dest = dest.parent / f"{stem}_from_desktop{suffix}"
                
                shutil.move(str(src), str(final_dest))
                print(f"[ПЕРЕНЕСЕНО] {item} -> {final_dest}")
                success_count += 1
            except Exception as e:
                errors.append(f"Ошибка перемещения {item} в {dest}: {e}")
                print(f"[ОШИБКА ПЕРЕМЕЩЕНИЯ] {item}: {e}")

    # Создаем стандартные пустые подпапки ВЭД (если какие-то остались пустыми)
    ved_root = SYNC_ROOT / "Рабочее" / "В работе" / "Белые отправки"
    for shipment in [
        ved_root / "2026-09 Ци Линь Проекторы (DATL300926)",
        ved_root / "2026-09 Контейнер CICU2663734 (Белый Раст)",
    ]:
        for subf in VED_SUBFOLDERS:
            (shipment / subf).mkdir(parents=True, exist_ok=True)

    # Записываем памятку на рабочий стол
    memo_path = DESKTOP / "ПАМЯТКА_ГДЕ_МОИ_ФАЙЛЫ.txt"
    try:
        with open(memo_path, "w", encoding="utf-8") as f:
            f.write(generate_memo_content(plan))
        print(f"\n[ПАМЯТКА СОЗДАНА] {memo_path}")
    except Exception as e:
        print(f"[ОШИБКА СОЗДАНИЯ ПАМЯТКИ] {e}")

    print(f"\nИтог: успешно обработано {success_count} из {len(plan)} объектов.")
    if errors:
        print(f"Ошибок: {len(errors)}")
        for err in errors:
            print(f"  * {err}")
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Desktop Organizer")
    parser.add_argument("--execute", action="store_true", help="Execute moves for real")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without moving files")
    args = parser.parse_args()

    run_cleanup(execute=args.execute)
