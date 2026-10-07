#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/process_deals_batch_azat.py
=====================================================
Пакетная обработка входящих сделок (переименование, перевод стадии в PREPARATION,
постановка задач снабженцу Азату user/20 с прикреплением спецификаций и файлов).

Поддерживает режимы:
  --dry-run (по умолчанию)
  --execute (боевая запись строго после утверждения пользователем)
"""

import os
import sys
import re
import json
import base64
import argparse
from datetime import datetime, timedelta
import requests

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

def _load_env():
    env_candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        r"C:\Codex\projects\1c_odata\.env",
        r"C:\Codex\.env"
    ]
    for env_file in env_candidates:
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v

_load_env()

B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
DESKTOP_DIR = os.path.join(os.environ.get("USERPROFILE", r"C:\Users\Артем"), "Desktop")

# Реестр конфигурации 8 сделок
DEALS_CONFIG = [
    {
        "deal_id": 2390,
        "company_id": 5712,
        "company_name": "АО «Пермский завод «Машиностроитель»",
        "company_short": "АО «ПЗ «Машиностроитель»",
        "contact_id": 7136,
        "contact_name": "Мишланова Наталья Александровна",
        "current_title": "Пермский завод Машиностроитель.  насос НК-6 (или аналог)",
        "new_title": "АО «ПЗ «Машиностроитель», НК-6 燃油柱塞泵 (насос топливный плунжерный 1 шт)",
        "excel_file": "Запрос КП Насос НК-6 Машиностроитель.xlsx",
        "client_disk_files": [108596, 108598], # Привязка двигателя, заявка (Реквизиты 108602 исключены по Attachment Hygiene Guard)
        "description_ru": "Заявка на топливный шестиплунжерный насос НК-6 (или аналог) — 1 шт. Подача: 0-2,5 л/мин (регулируемая), n=930 об/мин, Pmax=250 кг/см², бак 80 л. Электродвигатель: АОЛ-41-4 (P=1,7 кВт, n=1420 об/мин, 220/380В).",
        "description_cn": "询价清单：НК-6 燃油六柱塞变量泵 1台（流量0-2.5L/min可调，转速930r/min，最高工作压力250kg/cm²，油箱容积80L）及 配套三相异步电动机 АОЛ-41-4 1台（功率1.7kW，转速1420r/min）。请查收附件采购清单并核实中国工厂供货可行性、含税/不含税价格及货期。"
    },
    {
        "deal_id": 2388,
        "company_id": 5712,
        "company_name": "АО «Пермский завод «Машиностроитель»",
        "company_short": "АО «ПЗ «Машиностроитель»",
        "contact_id": 14520,
        "contact_name": "Марина Багаева",
        "current_title": "Mirka AIROS 550CV Машиностроитель ",
        "new_title": "АО «ПЗ «Машиностроитель», Mirka 砂光机 AIROS 550CV (шлифовальная головка для робота 1 шт)",
        "excel_file": "Запрос КП Mirka AIROS 550CV Машиностроитель.xlsx",
        "client_disk_files": [111564], # Запрос.pdf
        "description_ru": "Запрос на электрическую шлифовальную машинку (головку) для промышленного робота Mirka AIROS 550CV — 1 шт. Ход эксцентрика: 5.0 мм, диаметр подошвы: 125 мм.",
        "description_cn": "询价清单：Mirka 工业机器人用电动砂光机 / 自动化打磨头 AIROS 550CV 1台（偏摆5.0mm，磨盘直径125mm）。请查收附件采购清单，向工厂或渠道询价交货期及价格。"
    },
    {
        "deal_id": 2386,
        "company_id": 5712,
        "company_name": "АО «Пермский завод «Машиностроитель»",
        "company_short": "АО «ПЗ «Машиностроитель»",
        "contact_id": 14520,
        "contact_name": "Марина Багаева",
        "current_title": "Револьверная головка Baruffaldi Машиностроитель ",
        "new_title": "АО «ПЗ «Машиностроитель», Baruffaldi 伺服刀塔 TBMR 250 8/12 (револьверная головка 1 шт)",
        "excel_file": "Запрос КП Baruffaldi TBMR 250 Машиностроитель.xlsx",
        "client_disk_files": [111772], # служебное письмо
        "description_ru": "Заявка на револьверную головку с сервоприводом Baruffaldi TBMR 250 8/12 для токарного станка СА1250С100Ф4. Code: К57.А250.210А512.01, ID: 11824/14, U=230V 3~ — 1 шт.",
        "description_cn": "询价清单：Baruffaldi 伺服驱动数控动力刀塔 TBMR 250 8/12 1台（用于СА1250С100Ф4车床中修，Code: К57.А250.210А512.01, ID: 11824/14, 电压 230V 3相）。请向原厂或渠道询价交货期及含税价格。"
    },
    {
        "deal_id": 2384,
        "company_id": 5712,
        "company_name": "АО «Пермский завод «Машиностроитель»",
        "company_short": "АО «ПЗ «Машиностроитель»",
        "contact_id": 14520,
        "contact_name": "Марина Багаева",
        "current_title": "HGW 35 HC Hiwin – 16 шт Машиностроитель ",
        "new_title": "АО «ПЗ «Машиностроитель», Hiwin 导轨滑块 HGW 35 HC (каретки 16 шт, рельсы 8 шт)",
        "excel_file": "Запрос КП Hiwin HGW 35 HC Машиностроитель.xlsx",
        "client_disk_files": [111786, 111788], # Запрос (1).pdf, Линейная направляющая ХИВИН 35 MCV750.docx
        "description_ru": "Запрос на каретки профильные фланцевые Hiwin HGW 35 HC — 16 шт. и рельсовые направляющие Hiwin серии HG типоразмер 35 (станок MCV750) — 8 шт.",
        "description_cn": "询价清单：Hiwin 重载法兰型滚珠直线导轨滑块 HGW 35 HC 16件，及配套 35系列高精度直线导轨 8件（用于MCV750机床）。请向Hiwin中国代理商询价价格及货期。"
    },
    {
        "deal_id": 2382,
        "company_id": 10882,
        "company_name": "ООО «Винсек»",
        "company_short": "ООО «Винсек»",
        "contact_id": 14488,
        "contact_name": "Илья Юрченко",
        "current_title": "Илья Юрченко ВИНСЕК Чиллер FKL-8HP",
        "new_title": "ООО «Винсек», FKL 工业冷水机 FKL-8HP (промышленный чиллер 1 шт)",
        "excel_file": "Запрос КП Чиллер FKL-8HP Винсек.xlsx",
        "client_disk_files": [112384], # аявка на чиллер.pdf
        "description_ru": "Запрос на поставку промышленного охладителя воды (чиллера) FKL-8HP — 1 шт. Холодопроизводительность 22,35 кВт, бак 80 л, 380В/50Гц, насос 0,75 кВт (3-15,6 м³/ч, напор 5-12 м), фреон R22 6,6 кг.",
        "description_cn": "询价清单：FKL 工业风冷箱型冷水机 FKL-8HP 1台（制冷量22.35kW，水箱容积80L，电源380V/50Hz，水泵功率0.75kW，流量3-15.6m³/h，扬程5-12m，冷媒R22 6.6kg）。请查收附件采购清单向生产厂家询价。"
    },
    {
        "deal_id": 2380,
        "company_id": 5422,
        "company_name": "ООО «Спектр»",
        "company_short": "ООО «Спектр»",
        "contact_id": 9218,
        "contact_name": "Вадим Сорокин (Андрей)",
        "current_title": "Спектр, Jingge Electronics Co. JG ST2643 Измеритель удельного объёмного и поверхностного сопротивления",
        "new_title": "ООО «Спектр», JG 电阻测试仪 ST2643 (измеритель сопротивления 1 шт)",
        "excel_file": "Запрос КП ST2643 Измеритель Спектр.xlsx",
        "client_disk_files": [112444], # image (10).png
        "description_ru": "Заявка на измеритель удельного объёмного и поверхностного сопротивления и микротоков JG ST2643 (производитель Jingge Electronics Co., Китай) — 1 шт.",
        "description_cn": "询价清单：JG (Jingge Electronics) 超高阻微电流测试仪 / 表面电阻测试仪 ST2643 1台。请向国内厂家询价供货期及含税价格。"
    },
    {
        "deal_id": 2378,
        "company_id": 4832,
        "company_name": "ООО «Лебедяньмолоко»",
        "company_short": "ООО «Лебедяньмолоко»",
        "contact_id": 8038,
        "contact_name": "Олег Соловьёв",
        "current_title": "Лебедянь KOSME dp232f 91-125 гидрораспределитель",
        "new_title": "ООО «Лебедяньмолоко», Muehlberger 旋转分配器 1221 F 191-05 (водяной распределитель KOSME 1 шт)",
        "excel_file": "Запрос КП Распределитель KOSME Лебедяньмолоко.xlsx",
        "client_disk_files": [112542], # водяной распределитель KOSME.pdf
        "description_ru": "Запрос на ротационный водяной распределитель Muehlberger 1221 F 191-05 (dp232f 91-125) для оборудования розлива KOSME — 1 шт. 3 канала (2RSG1), подача и возврат воды.",
        "description_cn": "询价清单：Muehlberger 水介质多通道旋转接头分配器 1221 F 191-05 (KOSME dp232f 91-125, 2RSG1型，3通道) 1台。请查收图纸并向厂家询价供货期及价格。"
    },
    {
        "deal_id": 2372,
        "company_id": 5582,
        "company_name": "ООО «СПБ ЗПС»",
        "company_short": "ООО «СПБ ЗПС»",
        "contact_id": 9122,
        "contact_name": "Антончик Степан Михайлович",
        "current_title": "ЗПС AR-13D 钻头刃磨机。станок для сверел",
        "new_title": "ООО «СПБ ЗПС», AR-13D 钻头研磨机 (станок для заточки сверл 1 шт)",
        "excel_file": "Запрос КП Станок заточной AR-13D СПБ ЗПС.xlsx",
        "client_disk_files": [], # нет файлов в письме
        "description_ru": "Запрос на портативный станок для заточки спиральных свёрл AR-13D — 1 шт. Диапазон заточки: Ø2-Ø13 мм, цанги ER20 (11 шт), угол при вершине 90°-140°, питание 220В/50Гц.",
        "description_cn": "询价清单：便携式麻花钻研磨机 / 钻头刃磨机 AR-13D 1台（研磨范围 Ø2-Ø13mm，配ER20夹头，电压220V/50Hz）。请向中国工具制造厂询价供货期及含税价格。"
    }
]

def call_b24(method: str, params: dict = None) -> dict:
    url = f"{B24_WEBHOOK}{method}"
    res = requests.post(url, json=params or {}, timeout=30)
    if res.status_code >= 400:
        print(f"  [B24-ERROR] {method} HTTP {res.status_code}: {res.text}")
    res.raise_for_status()
    return res.json()

def upload_file_to_disk(file_path: str, folder_id: int = 27826) -> int:
    """Загрузка файла на Диск Б24 в папку группы 14 (Товары и поставщики Китай)"""
    if not file_path or not os.path.exists(file_path):
        return None
    fname = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    r = call_b24("disk.folder.uploadfile", {
        "id": folder_id,
        "data": {"NAME": fname},
        "fileContent": [fname, b64],
        "generateUniqueName": True
    })
    fid = r.get("result", {}).get("ID")
    if fid:
        return int(fid)
    return None

def process_batch(execute: bool = False, target_deal_id: int = None):
    mode_str = "БОЕВОЙ РЕЖИМ (--execute)" if execute else "ПРЕДПРОСМОТР (--dry-run)"
    print(f"\n========================================================")
    print(f"  СТАРТ ПАКЕТНОЙ ОБРАБОТКИ СДЕЛОК: {mode_str}")
    print(f"  Целевой ответственный по задачам: Азат Денишов (user/20)")
    print(f"  Целевая стадия сделок: PREPARATION (Расчет КП)")
    print(f"========================================================\n")

    results_table = []

    deals_to_process = [d for d in DEALS_CONFIG if d["deal_id"] == target_deal_id] if target_deal_id else DEALS_CONFIG
    for cfg in deals_to_process:
        did = cfg["deal_id"]
        cur_title = cfg["current_title"]
        new_title = cfg["new_title"]
        excel_name = cfg["excel_file"]
        excel_path = os.path.join(DESKTOP_DIR, excel_name)
        excel_exists = os.path.exists(excel_path)
        excel_size = os.path.getsize(excel_path) if excel_exists else 0
        
        client_files = cfg["client_disk_files"]
        
        print(f"\n--- Сделка #{did} ({cfg['company_short']}) ---")
        print(f"  Текущее название : {cur_title}")
        print(f"  Новое название   : {new_title}")
        print(f"  Смена стадии     : NEW -> PREPARATION (Расчет КП)")
        print(f"  Спецификация     : {excel_name} (существует: {excel_exists}, {excel_size} байт)")
        print(f"  Файлы клиента    : {client_files}")

        if not execute:
            # DRY-RUN
            results_table.append({
                "deal_id": did,
                "company": cfg["company_short"],
                "current_title": cur_title,
                "new_title": new_title,
                "stage_change": "NEW -> PREPARATION",
                "excel_file": excel_name,
                "excel_size": excel_size,
                "client_files": client_files,
                "status": "DRY-RUN READY"
            })
        else:
            # EXECUTE (БОЕВАЯ ЗАПИСЬ)
            # 1. Загрузка Excel-спецификации на Диск Б24
            uploaded_excel_id = None
            if excel_exists:
                uploaded_excel_id = upload_file_to_disk(excel_path)
                print(f"  [B24] Excel загружен на Диск: ID {uploaded_excel_id}")
            
            # Собираем все файлы задачи
            task_files = []
            if uploaded_excel_id:
                task_files.append(uploaded_excel_id)
            for cf in client_files:
                if cf not in task_files:
                    task_files.append(cf)

            # 2. Переименование Сделки и перевод стадии в PREPARATION
            deal_update_fields = {
                "TITLE": new_title,
                "STAGE_ID": "PREPARATION"
            }
            if cfg.get("company_id"):
                deal_update_fields["COMPANY_ID"] = cfg["company_id"]
            if cfg.get("contact_id"):
                deal_update_fields["CONTACT_ID"] = cfg["contact_id"]

            call_b24("crm.deal.update", {
                "id": did,
                "fields": deal_update_fields
            })
            print(f"  [B24] Сделка #{did} обновлена: STAGE_ID=PREPARATION, TITLE='{new_title}'")

            # 3. Постановка Задачи на Азата (user/20)
            deadline_dt = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
            task_desc = (
                f"Заявка клиента: {cfg['company_name']}\n"
                f"Контактное лицо: {cfg['contact_name']}\n\n"
                f"ТЕХНИЧЕСКОЕ ЗАДАНИЕ (RU):\n{cfg['description_ru']}\n\n"
                f"ТЕХНИЧЕСКОЕ ЗАДАНИЕ (CN):\n{cfg['description_cn']}\n\n"
                f"Спецификация во вложении: {excel_name}"
            )
            
            task_fields = {
                "TITLE": new_title,
                "DESCRIPTION": task_desc,
                "RESPONSIBLE_ID": 20, # Азат Денишов
                "CREATED_BY": 1,      # Артем Петров
                "AUDITORS": [1],      # Артем Петров в наблюдателях
                "DEADLINE": deadline_dt.strftime("%Y-%m-%d 18:00:00"),
                "UF_CRM_TASK": [f"D_{did}"],
                "GROUP_ID": 14,       # Проект "Товары и поставщики Китай"
                "TAGS": ["Поиск товара - 找货"]
            }
            if task_files:
                task_fields["UF_TASK_WEBDAV_FILES"] = [f"n{fid}" for fid in task_files]

            r_task = call_b24("tasks.task.add", {"fields": task_fields})
            task_id = int(r_task.get("result", {}).get("task", {}).get("id", 0))
            print(f"  [B24] Задача #{task_id} поставлена на Азата (user/20), дедлайн {deadline_dt.strftime('%d.%m.%Y')}")

            # 4. Первый комментарий в задачу с упоминанием Азата
            comment_text = (
                f"[USER=20]Азат[/USER], добрый день!\n\n"
                f"Поступила заявка от клиента {cfg['company_name']} по Сделке #{did}.\n\n"
                f"📋 ВЛОЖЕНИЯ К ЗАДАЧЕ:\n"
            )
            if uploaded_excel_id:
                comment_text += f"📊 [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{uploaded_excel_id}/]Спецификация Excel: {excel_name}[/URL]\n"
            if client_files:
                comment_text += "📎 Оригинальный запрос клиента:\n"
                for cfid in client_files:
                    comment_text += f"  - [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{cfid}/]Файл клиента (Диск ID {cfid})[/URL]\n"
            comment_text += (
                f"\nТЕХНИЧЕСКОЕ ЗАДАНИЕ (RU):\n{cfg['description_ru']}\n\n"
                f"ТЕХНИЧЕСКОЕ ЗАДАНИЕ (CN):\n{cfg['description_cn']}\n\n"
                f"Просьба запросить у поставщиков/фабрик стоимость и сроки поставки.\n"
                f"Дедлайн: {deadline_dt.strftime('%d.%m.%Y')}."
            )
            r_comm = call_b24("task.commentitem.add", {
                "TASKID": task_id,
                "FIELDS": {"POST_MESSAGE": comment_text}
            })
            print(f"  [B24] В чат Задачи #{task_id} отправлен пинг-комментарий для Азата [USER=20] (ID: {r_comm.get('result')})")

            results_table.append({
                "deal_id": did,
                "company": cfg["company_short"],
                "new_title": new_title,
                "task_id": task_id,
                "status": "SUCCESS"
            })

    print(f"\n========================================================")
    print(f"  ИТОГО ОБРАБОТАНО: {len(results_table)} СДЕЛОК")
    print(f"========================================================")
    return results_table

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Пакетная обработка сделок и постановка задач Азату")
    parser.add_argument("--execute", action="store_true", help="Боевое выполнение (без флага работает --dry-run)")
    parser.add_argument("--deal-id", type=int, default=None, help="ID конкретной сделки (например, 2390)")
    args = parser.parse_args()

    process_batch(execute=args.execute, target_deal_id=args.deal_id)
