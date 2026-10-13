"""
Скрипт наведения порядка на рабочем столе текущего пользователя.
Поддерживает режим --dry-run (по умолчанию) и --execute (боевой запуск).
Соблюдает строгий whitelist, правила вложенности и шаблон ВЭД-отправок.
Создает подробнейшую HTML и TXT памятку с ссылками для Проводника,
а также папку с ярлыками быстрого перехода в Проводнике.
"""

import os
import sys
import io
import shutil
import argparse
from pathlib import Path
from datetime import datetime

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
    "ПАМЯТКА_ГДЕ_МОИ_ФАЙЛЫ.html",
    "📂 ССЫЛКИ ДЛЯ ПРОВОДНИКА",
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
    customs_gtd = SYNC_ROOT / "Рабочее" / "Таможня" / "ГТД ЛВ"
    customs_jde = customs_gtd / "Янтарный комбинат ЖДЭ"
    marketing_blanks = SYNC_ROOT / "Рабочее" / "Маркетинг" / "Бланки"
    requisites_our = SYNC_ROOT / "Рабочее" / "Реквизиты" / "Наши"
    
    lika_dover = SYNC_ROOT / "Лика" / "Доверенности"
    lika_ff = SYNC_ROOT / "Лика" / "Маркетплэйсы" / "ФФ"
    lika_buh = SYNC_ROOT / "Лика" / "Бух Нов"
    lika_dogovory = SYNC_ROOT / "Лика" / "Договоры"
    
    docs_migration = Path(r"C:\Codex\docs\migration")
    temp_dir = SYNC_ROOT / "Общая папка_TEMP" / "Временное_Desktop_2026-10"

    # Папка отправки Ци Линь Проекторы (уровень 4)
    cilin_shipment = ved_root / "2026-09 Ци Линь Проекторы (DATL300926)"
    # Папка контейнера Белый Раст (уровень 4)
    white_rust_shipment = ved_root / "2026-09 Контейнер CICU2663734 (Белый Раст)"

    for name in items:
        # Пропуск whitelist
        if name in STRICT_WHITELIST:
            continue

        src_path = DESKTOP / name

        # 1. Временные lock-файлы Office
        if name.startswith("~$"):
            plan[name] = {
                "action": "delete",
                "dest": None,
                "category": "Удаление временного lock-файла Office",
            }
            continue

        # Пустая папка "Агентский договор"
        if name == "Агентский договор":
            if src_path.is_dir() and len(os.listdir(src_path)) == 0:
                plan[name] = {
                    "action": "delete",
                    "dest": None,
                    "category": "Удаление пустой папки Агентский договор",
                }
                continue
            else:
                plan[name] = {
                    "action": "move",
                    "dest": lika_dogovory / name,
                    "category": "Лика: Договоры",
                }
                continue

        # 2. Технические отчеты о миграции
        if name in ["MATEBOOK_MIGRATION_SUMMARY.md", "TRANSFER_AUDIT_REPORT.md"]:
            plan[name] = {
                "action": "move",
                "dest": docs_migration / name,
                "category": "Codex: Документация миграции",
            }
            continue

        # 3. Таможня и ГТД
        if name.startswith("GTD_") or name.startswith("ДТ Signature"):
            plan[name] = {
                "action": "move",
                "dest": customs_gtd / name,
                "category": "Рабочее: Таможня ГТД",
            }
            continue

        # 4. Логистика ЖДЭ
        if name.startswith("jde_") or name == "Янтарный комбинат ЖДЭ":
            plan[name] = {
                "action": "move",
                "dest": customs_jde / name,
                "category": "Рабочее: Таможня ЖДЭ",
            }
            continue

        # 5. Гидрамакс / готовые цилиндры
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

        # 6. Белый Раст / контейнер
        if any(k in name.lower() for k in ["белый раст", "cicu"]) or name in ["Пакет документов.pdf", "ЦЛ лента разметки.pdf"]:
            dest_sub = "перевозочные документы"
            plan[name] = {
                "action": "move",
                "dest": white_rust_shipment / dest_sub / name,
                "category": "ВЭД: Контейнер Белый Раст",
            }
            continue

        # 7. Отгрузка Пулково и ВЭД Ци Линь (Проекторы DATL300926)
        # 7.1 Расчеты брокера
        if name in [
            "Расчет_пошлин_и_НДС_ЦиЛинь_DATL300926.xlsx",
            "Расчет_пошлин_и_НДС_ЦиЛинь_DATL300926_v2.xlsx",
            "Брокеру.xlsx",
            "итоговый вывод по брокеру.docx",
            "Что сделал брокер Брокер вписал в предварительный.docx",
        ] or "расчет_пошлин" in name.lower() or "брокер" in name.lower():
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "расчеты брокера" / name,
                "category": "ВЭД: Расчеты брокера",
            }
            continue

        # 7.2 Перевозочные документы (включая Пулково)
        if any(k in name.lower() for k in ["пулково", "pulkovo", "транзитная", "экспортная", "авианакладная", "随车文件"]) or name in ["DAT"]:
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "перевозочные документы" / name,
                "category": "ВЭД: Перевозочные документы (в т.ч. Пулково)",
            }
            continue

        # 7.3 Бухгалтерские документы ВЭД (включая пакет УСС)
        if any(k in name.lower() for k in ["инвойс", "vbk", "пакинг", "постановке на учет контракта", "отсутствии страх", "отсутсвии страхования", "отсутствии шкс", "усс-"]):
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "бух документы" / name,
                "category": "ВЭД: Бухгалтерские документы",
            }
            continue

        # 7.4 Техническое описание
        if any(k in name.lower() for k in ["тех описание", "техническое описание", "список и описание", "данные по грузу"]):
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "тех описание" / name,
                "category": "ВЭД: Техническое описание",
            }
            continue

        # 7.5 ДС и СС
        if any(k in name.lower() for k in ["проектор заводской", "21951495", "21951550", "a13b8da3", "декларация о соответствии", "сертификат"]):
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "ДС и СС" / name,
                "category": "ВЭД: Декларации и сертификаты (ДС/СС)",
            }
            continue

        # 7.6 Фото
        if name in ["фото.rar", "фото"]:
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "фото" / name,
                "category": "ВЭД: Фото архива поставки",
            }
            continue

        # 8. Лика (Бухгалтерия, Доверенности, Маркетплейсы/ФФ, Договоры)
        if "доверенност" in name.lower() and "pulkovo" not in name.lower():
            plan[name] = {"action": "move", "dest": lika_dover / name, "category": "Лика: Доверенности"}
            continue
        if any(k in name.lower() for k in ["фулфиллмент", "print-order"]):
            plan[name] = {"action": "move", "dest": lika_ff / name, "category": "Лика: Маркетплейсы ФФ"}
            continue
        if any(k in name.lower() for k in ["упд", "универсальный передаточный", "pavlova", "фау_ниа", "kl_to_1c", "счет для", "счет на оплату", "взаиморасчет"]):
            plan[name] = {"action": "move", "dest": lika_buh / name, "category": "Лика: Бухгалтерия"}
            continue
        if any(k in name.lower() for k in ["договор по кк", "кк рос"]):
            plan[name] = {"action": "move", "dest": lika_dogovory / name, "category": "Лика: Договоры"}
            continue

        # 9. Реквизиты и Бланки
        if "реквизиты" in name.lower():
            target_req = requisites_our / "Ци Линь" if "ци линь" in name.lower() else requisites_our
            plan[name] = {"action": "move", "dest": target_req / name, "category": "Рабочее: Реквизиты"}
            continue
        if name == "Бланк Ци Линь новый.docx":
            plan[name] = {"action": "move", "dest": marketing_blanks / name, "category": "Рабочее: Маркетинг бланки"}
            continue

        # 10. Папка Временное
        if name == "Временное":
            plan[name] = {"action": "move", "dest": temp_dir, "category": "Общая папка TEMP"}
            continue

        # Фолбэк для неопознанных файлов
        plan[name] = {
            "action": "move",
            "dest": SYNC_ROOT / "Общая папка_TEMP" / f"Desktop_Unsorted_2026-10" / name,
            "category": "Общая папка TEMP (Несортированное)",
        }

    return plan


def create_explorer_shortcuts(desktop_dir):
    """
    Создает на рабочем столе специальную папку с .url ярлыками для открытия ключевых папок в Проводнике в 1 клик.
    """
    shortcuts_dir = desktop_dir / "📂 ССЫЛКИ ДЛЯ ПРОВОДНИКА"
    shortcuts_dir.mkdir(exist_ok=True)

    targets = [
        ("1. Ци Линь Проекторы (Белые отправки).url", r"D:\Документы Sync E\Рабочее\В работе\Белые отправки\2026-09 Ци Линь Проекторы (DATL300926)"),
        ("2. Контейнер Белый Раст (Белые отправки).url", r"D:\Документы Sync E\Рабочее\В работе\Белые отправки\2026-09 Контейнер CICU2663734 (Белый Раст)"),
        ("3. Бухгалтерия Анжелики (Бух Нов).url", r"D:\Документы Sync E\Лика\Бух Нов"),
        ("4. Доверенности (Лика).url", r"D:\Документы Sync E\Лика\Доверенности"),
        ("5. Маркетплейсы Фулфиллмент (Лика).url", r"D:\Документы Sync E\Лика\Маркетплэйсы\ФФ"),
        ("6. Таможня и ГТД.url", r"D:\Документы Sync E\Рабочее\Таможня\ГТД ЛВ"),
        ("7. Общая папка Временное.url", r"D:\Документы Sync E\Общая папка_TEMP"),
    ]

    for name, folder_path in targets:
        file_path = shortcuts_dir / name
        content = f"[InternetShortcut]\nURL=file:///{folder_path.replace(os.sep, '/')}\n"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"[ЯРЛЫКИ СОЗДАНЫ] {shortcuts_dir}")


def generate_html_memo(plan):
    """
    Создает интерактивную HTML памятку с удобным копированием путей для Проводника.
    """
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Группируем файлы по целевым папкам
    folder_groups = {}
    for item, info in plan.items():
        if info["action"] == "delete":
            folder_groups.setdefault("Удаленные временные файлы", []).append((item, "Корзина / Удалено", info["category"]))
            continue
        dest_folder = str(info["dest"].parent)
        folder_groups.setdefault(dest_folder, []).append((item, str(info["dest"]), info["category"]))

    rows_html = []
    for folder, files in sorted(folder_groups.items()):
        is_del = folder == "Удаленные временные файлы"
        clean_folder = folder.replace("\\", "\\\\")
        copy_btn = "" if is_del else f"""<button class="copy-btn" onclick="copyPath('{clean_folder}')">📋 Скопировать путь папки</button>"""
        
        file_list_html = "".join([
            f"""<li class="file-item">
                <span class="file-name">📄 {f_name}</span>
                <span class="file-cat">[{f_cat}]</span>
                {"" if is_del else f'''<button class="copy-btn-sm" onclick="copyPath('{f_dest.replace(chr(92), chr(92)+chr(92))}')">📋 путь к файлу</button>'''}
            </li>""" for f_name, f_dest, f_cat in sorted(files)
        ])

        rows_html.append(f"""
        <div class="card">
            <div class="card-header">
                <div class="folder-title">📁 {folder}</div>
                {copy_btn}
            </div>
            <ul class="file-list">
                {file_list_html}
            </ul>
        </div>
        """)

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Памятка: Где лежат файлы (для Анжелики)</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --border: #e2e8f0;
            --success: #16a34a;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 24px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            color: white;
            padding: 28px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 26px; }}
        .header p {{ margin: 0; opacity: 0.9; font-size: 15px; }}
        .toast {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #15803d;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            display: none;
            z-index: 1000;
            font-weight: 500;
        }}
        .tip-box {{
            background: #eff6ff;
            border-left: 4px solid var(--primary);
            padding: 16px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 24px;
            font-size: 14px;
        }}
        .search-box {{
            width: 100%;
            padding: 12px 16px;
            font-size: 16px;
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 24px;
            box-sizing: border-box;
            outline: none;
        }}
        .search-box:focus {{ border-color: var(--primary); ring: 2px solid #bfdbfe; }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-bottom: 16px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .card-header {{
            background: #f1f5f9;
            padding: 14px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}
        .folder-title {{
            font-weight: 600;
            font-size: 15px;
            color: #0f172a;
            word-break: break-all;
        }}
        .copy-btn {{
            background: var(--primary);
            color: white;
            border: none;
            padding: 6px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            white-space: nowrap;
            transition: background 0.15s ease;
        }}
        .copy-btn:hover {{ background: var(--primary-hover); }}
        .file-list {{
            list-style: none;
            margin: 0;
            padding: 8px 18px;
        }}
        .file-item {{
            padding: 8px 0;
            border-bottom: 1px solid #f1f5f9;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 14px;
        }}
        .file-item:last-child {{ border-bottom: none; }}
        .file-name {{ font-weight: 500; color: #334155; }}
        .file-cat {{ color: #64748b; font-size: 12px; margin-left: 8px; }}
        .copy-btn-sm {{
            background: #e2e8f0;
            color: #334155;
            border: none;
            padding: 3px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            transition: background 0.15s;
        }}
        .copy-btn-sm:hover {{ background: #cbd5e1; }}
        .whitelist-card {{
            background: #f8fafc;
            border: 1px dashed #cbd5e1;
            padding: 16px;
            border-radius: 8px;
            margin-top: 24px;
            font-size: 13px;
            color: #475569;
        }}
    </style>
</head>
<body>
    <div id="toast" class="toast">Путь скопирован в буфер обмена!</div>
    <div class="container">
        <div class="header">
            <h1>Памятка для Анжелики: где лежат ваши файлы</h1>
            <p>Рабочий стол очищен • Дата: {now_str}</p>
        </div>

        <div class="tip-box">
            💡 <b>Как мгновенно открыть любую папку в Проводнике:</b><br>
            1. Нажмите кнопку <b>«📋 Скопировать путь папки»</b> у нужного блока ниже.<br>
            2. Нажмите <b>Win + E</b> (откроется Проводник) ➔ нажмите <b>Ctrl + L</b> (выделится адресная строка) ➔ нажмите <b>Ctrl + V</b> и <b>Enter</b>.<br>
            3. Либо на Рабочем столе откройте папку <b>«📂 ССЫЛКИ ДЛЯ ПРОВОДНИКА»</b> и кликните по нужному ярлыку!
        </div>

        <input type="text" id="searchInput" class="search-box" placeholder="🔍 Быстрый поиск по названию файла или папки..." onkeyup="filterFiles()">

        <div id="cardsContainer">
            {''.join(rows_html)}
        </div>

        <div class="whitelist-card">
            📌 <b>Оставлено на Рабочем столе без изменений (строго по вайтлисту):</b><br>
            Пароли.txt • Сертификаты ЭП (ЛУНВАН.cer, ИП Павлова.cer, Ци Линь.pfx) • Ярлыки (Artem-Home, Мышь, папка Soft, Презентация и референс-лист).
        </div>
    </div>

    <script>
        function copyPath(text) {{
            navigator.clipboard.writeText(text).then(() => {{
                const toast = document.getElementById('toast');
                toast.style.display = 'block';
                setTimeout(() => {{ toast.style.display = 'none'; }}, 2500);
            }});
        }}

        function filterFiles() {{
            const filter = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {{
                const text = card.innerText.toLowerCase();
                if (text.includes(filter)) {{
                    card.style.display = '';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
    return html


def generate_txt_memo(plan):
    """Генерирует подробный текстовый файл памятки со ссылками для проводника."""
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    lines = [
        "=================================================================",
        "        ПАМЯТКА: РАСПРЕДЕЛЕНИЕ ФАЙЛОВ С РАБОЧЕГО СТОЛА           ",
        f"                Дата наведения порядка: {now_str}               ",
        "=================================================================",
        "",
        "Анжелика, привет! Рабочий стол очищен и аккуратно структурирован.",
        "Для открытия любой папки скопируйте ее путь и вставьте в строку",
        "адреса Проводника (нажмите Win+E, затем Ctrl+L, вставьте путь и Enter).",
        "",
        "Также на Рабочем столе создана папка '📂 ССЫЛКИ ДЛЯ ПРОВОДНИКА',",
        "где можно открыть любую из ключевых папок в 1 клик!",
        "",
        "=================================================================",
        "1. ВЭД ПОСТАВКА: ПРОЕКТОРЫ ЦИ ЛИНЬ (DATL300926 / ПУЛКОВО)",
        "   Путь к папке: D:\\Документы Sync E\\Рабочее\\В работе\\Белые отправки\\2026-09 Ци Линь Проекторы (DATL300926)\\",
        "   - перевозочные доки/ -> Отгрузка из Пулково, доверенности Пулково, декларации",
        "   - бух документы/     -> Инвойсы (DATL), Пакет УСС-0443463 ЦИ ЛИНЬ, ВБК, письма",
        "   - тех описание/      -> Техническое описание товаров, Данные по грузу (PDF, XLSX)",
        "   - расчеты брокера/   -> Расчеты пошлин и НДС, итоговый вывод по брокеру, Брокеру.xlsx",
        "   - ДС и СС/           -> Декларации соответствия на проекторы (004-020-037, 21951...)",
        "   - фото/              -> Папка фото и архив фото.rar",
        "",
        "2. ВЭД ПОСТАВКА: КОНТЕЙНЕР БЕЛЫЙ РАСТ (CICU2663734)",
        "   Путь к папке: D:\\Документы Sync E\\Рабочее\\В работе\\Белые отправки\\2026-09 Контейнер CICU2663734 (Белый Раст)\\",
        "   - перевозочные доки/ -> Пакет документов СВХ Белый Раст 04.10.2026.rar, Пакет документов.pdf, СМГС, лента разметки",
        "",
        "3. ТАМОЖНЯ И ГТД (РАЗДЕЛ ТАМОЖНЯ)",
        "   Путь к папке: D:\\Документы Sync E\\Рабочее\\Таможня\\ГТД ЛВ\\",
        "   - GTD_10131020_041026_5121673.pdf",
        "   - ДТ Signature - 268f1d47-11eb-42c4-8c81-592f1a0e2b64.pdf",
        "   - Янтарный комбинат ЖДЭ/ -> jde_2252131577672221_5833.pdf, накладные, акты",
        "",
        "4. ДОКУМЕНТЫ АНЖЕЛИКИ (ПАПКА ЛИКА)",
        "   - Бухгалтерия: D:\\Документы Sync E\\Лика\\Бух Нов\\",
        "     * УПД №227, УПД №228 ООО ЦИ ЛИНЬ",
        "     * УПД № НФ-89, УПД № НФ-94, УПД № НФ-96",
        "     * Счет для НПП Алмаз.pdf, Счет на оплату № 91 от 5 октября",
        "     * взаиморасчеты 12-10-26.xlsx, выписка kl_to_1c.txt",
        "   - Доверенности: D:\\Документы Sync E\\Лика\\Доверенности\\",
        "     * Доверенность.docx, Доверенность.pdf, образец доверенности",
        "   - Маркетплейсы: D:\\Документы Sync E\\Лика\\Маркетплэйсы\\ФФ\\",
        "     * print-order-10329419089, print-order-10329421472, print-order-10330654335, Фулфиллмент",
        "   - Договоры:    D:\\Документы Sync E\\Лика\\Договоры\\",
        "",
        "5. РЕКВИЗИТЫ И ОБЩИЕ ДОКУМЕНТЫ (ПАПКА РАБОЧЕЕ)",
        "   - Реквизиты Ци Линь -> D:\\Документы Sync E\\Рабочее\\Реквизиты\\Наши\\Ци Линь\\",
        "   - Реквизиты тенге   -> D:\\Документы Sync E\\Рабочее\\Реквизиты\\Наши\\",
        "   - Готовые цилиндры  -> D:\\Документы Sync E\\Рабочее\\В работе\\Гидрамакс (Логистиктранс)\\Готовые цилиндры\\",
        "",
        "6. ТЕХНИЧЕСКИЕ ОТЧЕТЫ (CODEX)",
        "   - Путь: C:\\Codex\\docs\\migration\\ (MATEBOOK_MIGRATION_SUMMARY.md, TRANSFER_AUDIT_REPORT.md)",
        "",
        "7. ЧТО ОСТАЛОСЬ НА РАБОЧЕМ СТОЛЕ БЕЗ ИЗМЕНЕНИЙ (ВАЙТЛИСТ):",
        "   - Пароли.txt (строго на месте)",
        "   - Сертификаты ЭП: ЛУНВАН.cer, ИП Павлова.cer, Ци Линь.pfx",
        "   - Ярлыки: Artem-Home, Мышь, папка Soft, Презентация и референс-лист",
        "",
        "-----------------------------------------------------------------",
        "ПОДСКАЗКА: Любой файл можно мгновенно найти через Everything",
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

    # 1. Записываем текстовую памятку
    memo_txt_path = DESKTOP / "ПАМЯТКА_ГДЕ_МОИ_ФАЙЛЫ.txt"
    try:
        with open(memo_txt_path, "w", encoding="utf-8") as f:
            f.write(generate_txt_memo(plan))
        print(f"[ПАМЯТКА TXT СОЗДАНА] {memo_txt_path}")
    except Exception as e:
        print(f"[ОШИБКА СОЗДАНИЯ TXT ПАМЯТКИ] {e}")

    # 2. Записываем интерактивную HTML памятку
    memo_html_path = DESKTOP / "ПАМЯТКА_ГДЕ_МОИ_ФАЙЛЫ.html"
    try:
        with open(memo_html_path, "w", encoding="utf-8") as f:
            f.write(generate_html_memo(plan))
        print(f"[ПАМЯТКА HTML СОЗДАНА] {memo_html_path}")
    except Exception as e:
        print(f"[ОШИБКА СОЗДАНИЯ HTML ПАМЯТКИ] {e}")

    # 3. Создаем папку быстрых ссылок для Проводника
    create_explorer_shortcuts(DESKTOP)

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
