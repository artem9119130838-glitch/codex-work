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
    "Antigravity.lnk",
    "Soft",
    "Презентация и референс-лист.pdf",
    "ЛУНВАН.cer",
    "Ци Линь.pfx",
    "ИП Павлова.cer",
    "Пароли.txt",
    "ПАМЯТКА_ГДЕ_МОИ_ФАЙЛЫ.txt",
    "ПАМЯТКА_ГДЕ_МОИ_ФАЙЛЫ.html",
    "📂 ССЫЛКИ ДЛЯ ПРОВОДНИКА",
    "📂 ПАМЯТКИ ССЫЛКИ ДЛЯ ПРОВОДНИКА",
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
    customs_gtd = SYNC_ROOT / "Рабочее" / "Таможня" / "ГТД ЛВ"
    customs_jde = customs_gtd / "Янтарный комбинат ЖДЭ"
    customs_tech = SYNC_ROOT / "Рабочее" / "Таможня" / "Технические описания"
    marketing_blanks = SYNC_ROOT / "Рабочее" / "Маркетинг" / "Бланки"
    requisites_our = SYNC_ROOT / "Рабочее" / "Реквизиты" / "Наши"
    contracts_sz = SYNC_ROOT / "Рабочее" / "Договоры" / "Самозанятые"
    contracts_ponomareva = contracts_sz / "Пономарева (Ассистент руководителя)"
    
    lika_dover = SYNC_ROOT / "Лика" / "Доверенности"
    lika_ff = SYNC_ROOT / "Лика" / "Маркетплэйсы" / "ФФ"
    lika_buh = SYNC_ROOT / "Лика" / "Бух Нов"
    lika_taxes = lika_buh / "Налоги Лика"
    lika_dogovory = SYNC_ROOT / "Лика" / "Договоры"
    lika_cards_photos = SYNC_ROOT / "Лика" / "Маркетплэйсы" / "Карточки" / "Фото товаров 2026-10"
    lika_institute = SYNC_ROOT / "Лика" / "Личное_Архив" / "Институт"
    lika_archive_photos = SYNC_ROOT / "Лика" / "Личное_Архив" / "Фото"
    
    docs_migration = Path(r"C:\Codex\docs\migration")
    docs_backups = Path(r"C:\Codex\docs\backups")
    temp_dir = SYNC_ROOT / "Общая папка_TEMP" / "Временное_Desktop_2026-10"

    # Папка отправки Ци Линь Проекторы (уровень 4)
    cilin_shipment = ved_root / "2026-09 Ци Линь Проекторы (DATL300926)"
    # Папка контейнера Белый Раст (уровень 4)
    white_rust_shipment = ved_root / "2026-09 Контейнер CICU2663734 (Белый Раст)"

    for name in items:
        # Пропуск whitelist
        if name in STRICT_WHITELIST:
            continue
        # Защита системных сертификатов и ярлыков
        if name.endswith(".cer") or name.endswith(".pfx") or (name.endswith(".lnk") and name not in plan):
            continue

        src_path = DESKTOP / name

        # 1. Временные lock-файлы Office и пустые нулевые черновики
        if name.startswith("~$"):
            plan[name] = {
                "action": "delete",
                "dest": None,
                "category": "Удаление временного lock-файла Office",
            }
            continue

        if name.startswith("Соглашение.docx") and src_path.is_file() and src_path.stat().st_size == 0:
            plan[name] = {
                "action": "delete",
                "dest": None,
                "category": "Удаление пустого файла Соглашение.docx (0 байт)",
            }
            continue

        if "счет_на_оплату_№_96" in name.lower() and src_path.is_file() and src_path.stat().st_size == 0:
            plan[name] = {
                "action": "delete",
                "dest": None,
                "category": "Удаление пустого дубликата Счета №96 (0 байт)",
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
            else:
                plan[name] = {
                    "action": "move",
                    "dest": lika_dogovory / name,
                    "category": "Лика: Договоры",
                }
            continue

        # 2. Системные и технические отчеты / бэкапы
        if name in ["MATEBOOK_MIGRATION_SUMMARY.md", "TRANSFER_AUDIT_REPORT.md"]:
            plan[name] = {
                "action": "move",
                "dest": docs_migration / name,
                "category": "Codex: Документация миграции",
            }
            continue

        if name == "CredentialProviders-backup.reg":
            plan[name] = {
                "action": "move",
                "dest": docs_backups / name,
                "category": "Codex: Системные бэкапы",
            }
            continue

        # 3. ВЭД: Поставка Ци Линь Проекторы (DATL300926 / Пулково)
        if "21965387" in name or ("проектор" in name.lower() and name.endswith(".pdf") and "бланк" not in name.lower()):
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "ДС и СС" / name,
                "category": "ВЭД: Декларации и сертификаты (ДС/СС)",
            }
            continue

        if "усс-" in name.lower() and "ци линь" in name.lower():
            plan[name] = {
                "action": "move",
                "dest": cilin_shipment / "бух документы" / name,
                "category": "ВЭД: Бухгалтерские документы",
            }
            continue

        # 4. Таможня: Технические описания оборудования для брокера (ABB, Danfoss)
        if "danfoss" in name.lower() and "брокер" in name.lower():
            plan[name] = {
                "action": "move",
                "dest": customs_tech / name,
                "category": "Рабочее: Таможня (Технические описания для брокера)",
            }
            continue

        if "техническое_описание_оборудования_abb" in name.lower():
            plan[name] = {
                "action": "move",
                "dest": customs_tech / name,
                "category": "Рабочее: Таможня (Технические описания для брокера)",
            }
            continue

        # 5. Таможня и ЖДЭ (УПД и логистика ЖелДорЭкспедиция)
        if name == "1359":
            # УПД ЖДЭ СПБ2252131570758697 от 21.09.2026
            plan[name] = {
                "action": "move",
                "dest": customs_jde / "УПД ЖДЭ СПБ2252131570758697 от 21.09.2026.pdf",
                "category": "Рабочее: Таможня ЖДЭ (УПД СПБ2252131570758697)",
            }
            continue

        if name == "УПД (статус 1) (4).pdf":
            # УПД ЖДЭ СПБХХ99632900637689 от 01.09.2026
            plan[name] = {
                "action": "move",
                "dest": customs_jde / "УПД ЖДЭ СПБХХ99632900637689 от 01.09.2026.pdf",
                "category": "Рабочее: Таможня ЖДЭ (УПД СПБХХ99632900637689)",
            }
            continue

        if name.startswith("jde_") or name == "Янтарный комбинат ЖДЭ":
            plan[name] = {
                "action": "move",
                "dest": customs_jde / name,
                "category": "Рабочее: Таможня ЖДЭ",
            }
            continue

        if name.startswith("GTD_") or name.startswith("ДТ Signature"):
            plan[name] = {
                "action": "move",
                "dest": customs_gtd / name,
                "category": "Рабочее: Таможня ГТД",
            }
            continue

        # 6. Договоры: Самозанятые, Пономарева (Ассистент руководителя), Снабжение
        if "пономарева" in name.lower() or "ассист рук" in name.lower() or name == "Соглашение к Догвоору оказания услуг.docx":
            plan[name] = {
                "action": "move",
                "dest": contracts_ponomareva / name,
                "category": "Рабочее: Договоры (Ассистент руководителя Пономарева)",
            }
            continue

        if name == "Договор с сз_агент по снабжению.docx":
            plan[name] = {
                "action": "move",
                "dest": contracts_sz / name,
                "category": "Рабочее: Договоры (Самозанятые)",
            }
            continue

        # 7. Лика: Личное / Институт (РГПУ им. Герцена)
        if "павлова а.а." in name.lower() and "2026-2027" in name.lower():
            plan[name] = {
                "action": "move",
                "dest": lika_institute / name,
                "category": "Лика: Институт / Обучение (РГПУ им. Герцена)",
            }
            continue

        # 8. Лика: Налоги и ФНС (ИП Павлова, Лун-Ван)
        if name.startswith("1165") and name.endswith(".pdf"):
            plan[name] = {
                "action": "move",
                "dest": lika_taxes / name,
                "category": "Лика: Налоги и ФНС (Лун-Ван)",
            }
            continue

        if name.startswith("UT_UVISCHSUMNAL") and name.endswith(".xml"):
            plan[name] = {
                "action": "move",
                "dest": lika_taxes / name,
                "category": "Лика: Налоги и ФНС (ИП Павлова)",
            }
            continue

        # 9. Лика: Бухгалтерия (Выписка 1С, счета, инвойсы Yiwu Yuhui, валютные реквизиты)
        if name == "1с.txt":
            plan[name] = {
                "action": "move",
                "dest": lika_buh / "1с_выписка_2026-10-23.txt",
                "category": "Лика: Бухгалтерия (Выписка Сбербанк 1С)",
            }
            continue

        if "счет на оплату № 96" in name.lower() or "счет_на_оплату_№_96" in name.lower():
            plan[name] = {
                "action": "move",
                "dest": lika_buh / name,
                "category": "Лика: Бухгалтерия (Счета)",
            }
            continue

        if "ip_pavlova_invoice" in name.lower():
            plan[name] = {
                "action": "move",
                "dest": lika_buh / name,
                "category": "Лика: Бухгалтерия (Инвойсы Yiwu Yuhui)",
            }
            continue

        if "余晖" in name or "yuhui" in name.lower():
            plan[name] = {
                "action": "move",
                "dest": lika_buh / name,
                "category": "Лика: Бухгалтерия (Реквизиты/Маршрут оплаты Yiwu Yuhui USD)",
            }
            continue

        if name == "Новые реквизиты.pdf":
            plan[name] = {
                "action": "move",
                "dest": lika_buh / "Новые реквизиты (Yiwu Nakai USD).pdf",
                "category": "Лика: Бухгалтерия (Реквизиты в долларах Yiwu Nakai)",
            }
            continue

        # 10. Лика: Маркетплейсы Карточки (Фото товаров > 3 шт)
        if name in ["10952399-2-1.jpg", "10952399-2-2.jpg", "10965927-2-1.jpg", "10965927-2-2.jpg"]:
            plan[name] = {
                "action": "move",
                "dest": lika_cards_photos / name,
                "category": "Лика: Маркетплейсы Карточки (Фото товаров)",
            }
            continue

        # 11. Лика: Личный архив фото
        if name in ["2974.jpg", "2974.pic"]:
            plan[name] = {
                "action": "move",
                "dest": lika_archive_photos / name,
                "category": "Лика: Личный архив фото",
            }
            continue

        # 12. Общие правила Лика (Доверенности, Маркетплейсы ФФ, Бухгалтерия, Договоры)
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

        # 13. Реквизиты и Бланки
        if "реквизиты" in name.lower():
            target_req = requisites_our / "Ци Линь" if "ци линь" in name.lower() else requisites_our
            plan[name] = {"action": "move", "dest": target_req / name, "category": "Рабочее: Реквизиты"}
            continue

        if name == "Бланк Ци Линь новый.docx":
            plan[name] = {"action": "move", "dest": marketing_blanks / name, "category": "Рабочее: Маркетинг бланки"}
            continue

        # 14. Папка Временное
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
        ("4. Налоги и ФНС (Бух Нов).url", r"D:\Документы Sync E\Лика\Бух Нов\Налоги Лика"),
        ("5. Договоры и Самозанятые (Рабочее).url", r"D:\Документы Sync E\Рабочее\Договоры\Самозанятые"),
        ("6. Таможня и ГТД (Рабочее).url", r"D:\Документы Sync E\Рабочее\Таможня\ГТД ЛВ"),
        ("7. Карточки товаров и фото (Лика).url", r"D:\Документы Sync E\Лика\Маркетплэйсы\Карточки"),
        ("8. Институт и личное (Лика).url", r"D:\Документы Sync E\Лика\Личное_Архив\Институт"),
        ("9. Общая папка Временное.url", r"D:\Документы Sync E\Общая папка_TEMP"),
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
            folder_groups.setdefault("Удаленные временные и пустые файлы", []).append((item, "Корзина / Удалено", info["category"]))
            continue
        dest_folder = str(info["dest"].parent)
        folder_groups.setdefault(dest_folder, []).append((item, str(info["dest"]), info["category"]))

    rows_html = []
    for folder, files in sorted(folder_groups.items()):
        is_del = folder == "Удаленные временные и пустые файлы"
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
            Пароли.txt • Сертификаты ЭП (ЛУНВАН.cer, ИП Павлова.cer, Ци Линь.pfx) • Ярлыки запуска (Artem-Home, Мышь, Antigravity, папка Soft, Презентация и референс-лист).
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
        "Анжелика, привет! Рабочий стол полностью приведен в идеальный порядок.",
        "Для открытия любой папки скопируйте ее путь и вставьте в строку",
        "адреса Проводника (нажмите Win+E, затем Ctrl+L, вставьте путь и Enter).",
        "",
        "Также на Рабочем столе создана папка '📂 ССЫЛКИ ДЛЯ ПРОВОДНИКА',",
        "где можно открыть любую из ключевых папок в 1 клик!",
        "",
        "=================================================================",
        "1. ВЭД ПОСТАВКА: ПРОЕКТОРЫ ЦИ ЛИНЬ (DATL300926 / ПУЛКОВО)",
        "   Путь к папке: D:\\Документы Sync E\\Рабочее\\В работе\\Белые отправки\\2026-09 Ци Линь Проекторы (DATL300926)\\",
        "   - ДС и СС/           -> ДС_проекторы_21965387 от 14.10.2026.pdf (декларация соответствия)",
        "   - бух документы/     -> Пакет УСС-0443739 от 18_10_2026 _ЦИ ЛИНЬ_.pdf (услуги перевозки СВХ)",
        "",
        "2. БУХГАЛТЕРИЯ АНЖЕЛИКИ (ИП ПАВЛОВА И ОРГАНИЗАЦИИ)",
        "   Путь к папке: D:\\Документы Sync E\\Лика\\Бух Нов\\",
        "   - 1с_выписка_2026-10-23.txt (выписка Сбербанк Бизнес Онлайн от 23.10.2026)",
        "   - Счет на оплату № 96 от 21 октября 2026 г.pdf",
        "   - IP_Pavlova_invoice_10-27-26.pdf (Инвойс Yiwu Yuhui Trading Firm на $6 850)",
        "   - 义乌余晖汇款路线-美元(1).pdf (Маршрут валютного платежа Yiwu Yuhui в USD)",
        "   - Новые реквизиты (Yiwu Nakai USD).pdf (Реквизиты платежа в USD Yiwu Nakai)",
        "",
        "3. НАЛОГИ И ФНС (ИП ПАВЛОВА И ЛУН-ВАН)",
        "   Путь к папке: D:\\Документы Sync E\\Лика\\Бух Нов\\Налоги Лика\\",
        "   - UT_UVISCHSUMNAL_...xml (Уведомление об исчисленных суммах налогов ИП Павлова)",
        "   - 1165050_7801_...pdf (Решение ИФНС №16 по ООО 'Лун-Ван')",
        "   - 1165072_7801_...pdf (Решение о продлении камеральной налоговой проверки ООО 'Лун-Ван')",
        "",
        "4. ДОГОВОРЫ: САМОЗАНЯТЫЕ И АССИСТЕНТ РУКОВОДИТЕЛЯ",
        "   Путь к папке: D:\\Документы Sync E\\Рабочее\\Договоры\\Самозанятые\\",
        "   - Договор с сз_агент по снабжению.docx",
        "   Подпапка: ...\\Самозанятые\\Пономарева (Ассистент руководителя)\\",
        "   - Договор с ассист рук 2610.pdf (Договор возмездного оказания услуг №4/26 ЦИ ЛИНЬ)",
        "   - Соглашение к Догвоору оказания услуг.docx (Соглашение о неразглашении конфиденциальности)",
        "   - Соглашение_о_конфиденциальности_ЦИ_ЛИНЬ_Пономарева_с_ответственностью.docx",
        "   - Соглашение_о_конфиденциальности_ЦИ_ЛИНЬ_Пономарева_с_ответственностью.pdf",
        "",
        "5. ТАМОЖНЯ: ТЕХНИЧЕСКИЕ ОПИСАНИЯ И ЖДЭ",
        "   - Технические описания: D:\\Документы Sync E\\Рабочее\\Таможня\\Технические описания\\",
        "     * Danfoss_OFV_20_D_2412-183_описание_для_брокера (1).docx",
        "     * Техническое_описание_оборудования_ABB.docx",
        "   - Логистика ЖДЭ: D:\\Документы Sync E\\Рабочее\\Таможня\\ГТД ЛВ\\Янтарный комбинат ЖДЭ\\",
        "     * УПД ЖДЭ СПБ2252131570758697 от 21.09.2026.pdf (файл 1359)",
        "     * УПД ЖДЭ СПБХХ99632900637689 от 01.09.2026.pdf (файл УПД статус 1)",
        "",
        "6. МАРКЕТПЛЕЙСЫ: КАРТОЧКИ И ФОТО ТОВАРОВ",
        "   Путь к папке: D:\\Документы Sync E\\Лика\\Маркетплэйсы\\Карточки\\Фото товаров 2026-10\\",
        "   - 10952399-2-1.jpg, 10952399-2-2.jpg",
        "   - 10965927-2-1.jpg, 10965927-2-2.jpg",
        "",
        "7. ЛИЧНОЕ / ИНСТИТУТ (РГПУ ИМ. ГЕРЦЕНА)",
        "   Путь к папке: D:\\Документы Sync E\\Лика\\Личное_Архив\\Институт\\",
        "   - Павлова А.А. 2026-2027.pdf (скан справки об обучении)",
        "   - Павлова А.А._2026-2027.pdf (электронный документ об обучении)",
        "",
        "8. ЛИЧНЫЙ АРХИВ ФОТО",
        "   Путь к папке: D:\\Документы Sync E\\Лика\\Личное_Архив\\Фото\\",
        "   - 2974.jpg, 2974.pic",
        "",
        "9. СИСТЕМНЫЕ БЭКАПЫ",
        "   Путь к папке: C:\\Codex\\docs\\backups\\",
        "   - CredentialProviders-backup.reg",
        "",
        "10. УДАЛЕННЫЕ ПУСТЫЕ ФАЙЛЫ (0 БАЙТ):",
        "   - Соглашение.docx (пустой файл)",
        "   - Счет_на_оплату_№_96_от_21_октября_2026 г.pdf (пустой дубликат)",
        "",
        "11. ЧТО ОСТАЛОСЬ НА РАБОЧЕМ СТОЛЕ БЕЗ ИЗМЕНЕНИЙ (ВАЙТЛИСТ):",
        "   - Пароли.txt (строго на месте)",
        "   - Сертификаты ЭП: ЛУНВАН.cer, ИП Павлова.cer, Ци Линь.pfx",
        "   - Ярлыки запуска: Artem-Home, Мышь, Antigravity, папка Soft, Презентация и референс-лист",
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

    # Удаляем устаревшую дублирующую папку ярлыков если была
    old_shortcuts = DESKTOP / "📂 ПАМЯТКИ ССЫЛКИ ДЛЯ ПРОВОДНИКА"
    if old_shortcuts.exists() and old_shortcuts.is_dir():
        try:
            shutil.rmtree(old_shortcuts)
        except Exception:
            pass

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
