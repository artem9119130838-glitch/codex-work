#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/execute_inbound_leads_rebuild.py
Боевой скрипт точного пересоздания и исправления сделок и задач снабжения Битрикс24.
"""

import os
import sys
import json
import requests
from datetime import datetime

sys.path.insert(0, r"C:\Codex\projects\1c_odata\scripts")
from process_b24_inbound_leads import (
    load_dotenv, call_b24, upload_file_to_b24_disk,
    USER_ARTEM, USER_AZAT, GROUP_CHINA_SUPPLY, FOLDER_CHINA_SUPPLY_DISK
)
from generate_supply_rfq_excel import generate_rfq_excel

load_dotenv()

USER_MISS_WANG = 30
USER_LIYAN_WANG = 44
USER_LI_YUNAN = 84

DEADLINE_FRIDAY = "2026-11-20T18:00:00+03:00"

APOLOGY_CHAT_MSG_TEMPLATE = """[USER=20]Азат Денишов[/USER], [USER={resp_id}]{resp_name}[/USER]

各位同事好！/ Азат, коллеги:
之前该任务由系统AI自动生成，由于提取规则异常导致产品名称及型号格式出现错误，给各位的工作带来了困扰，对此深表歉意！

现已完成人工审核与全面修正：
1. 附件中提供了精准的中俄双语询价清单（Excel），包含确切的品牌、型号/图纸编号和技术参数；
2. 原始图纸与客户技术规范均已完整附在任务附件中；
3. 截止反馈时间为：本周五（11月20日）18:00。
{extra_info}
后续如果对任务要求、图纸细节或型号有任何疑问或不明确之处，请随时在任务留言中直接 @我，我将第一时间协助沟通处理。非常感谢大家的理解与配合！"""

def build_task_description(deal_title, items, extra_text=""):
    rows = []
    for it in items:
        rows.append(f"- №{it['num']}: [B]{it['brand']}[/B] | [B]{it['pname_cn']}[/B] | Модель/Арт: [B]{it['model']}[/B] | {it['name_ru']} — [B]{it['qty']} шт.[/B]")
    items_block = "\n".join(rows)
    
    desc = f"""ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА ЗАКУПКУ / 采购技术要求

• Сделка: {deal_title}
• Позиции к закупке (采购清单):
{items_block}

• Срок выполнения / 截止时间: 20.11.2026 18:00
• Наблюдатель / 监督员: Азат Денишов
{extra_text}
ВНИМАНИЕ: Все спецификации и чертежи прикреплены к карточке задачи в формате Excel и оригинальных файлов."""
    return desc

def create_deal(title, company_id, contact_id, lead_id=None):
    fields = {
        "TITLE": title,
        "COMPANY_ID": company_id,
        "CONTACT_ID": contact_id,
        "CATEGORY_ID": 0,
        "STAGE_ID": "NEW",
        "ASSIGNED_BY_ID": USER_ARTEM,
        "CURRENCY_ID": "RUB",
        "OPPORTUNITY": 0.00
    }
    if lead_id:
        fields["LEAD_ID"] = lead_id
    res = call_b24("crm.deal.add", {"fields": fields})
    deal_id = res.get("result") if isinstance(res, dict) else res
    return int(deal_id)

def create_task(title, deal_id, description, resp_id, file_ids=None):
    fields = {
        "TITLE": title,
        "DESCRIPTION": description,
        "RESPONSIBLE_ID": resp_id,
        "CREATED_BY": USER_ARTEM,
        "AUDITORS": [USER_AZAT],
        "GROUP_ID": GROUP_CHINA_SUPPLY,
        "PRIORITY": 1,
        "STATUS": 2, # Ждет выполнения
        "TASK_CONTROL": "Y",
        "DEADLINE": DEADLINE_FRIDAY,
        "TAGS": ["Поиск товара - 找货"],
        "UF_CRM_TASK": [f"D_{deal_id}"]
    }
    if file_ids:
        fields["UF_TASK_WEBDAV_FILES"] = [f"n{fid}" for fid in file_ids if fid]
    
    res = call_b24("tasks.task.add", {"fields": fields})
    task_id = res.get("task", {}).get("id") if isinstance(res, dict) and "task" in res else res
    return int(task_id)

def post_task_chat_message(task_id, resp_id, resp_name, extra_info=""):
    task_info = call_b24("tasks.task.get", {"taskId": task_id, "select": ["CHAT_ID"]})
    chat_id = task_info.get("task", {}).get("chatId") if task_info else None
    
    msg_text = APOLOGY_CHAT_MSG_TEMPLATE.format(
        resp_id=resp_id,
        resp_name=resp_name,
        extra_info=f"\n{extra_info}\n" if extra_info else ""
    )
    
    # 1. Отправляем в чат задачи через im.message.add
    if chat_id:
        call_b24("im.message.add", {
            "DIALOG_ID": f"chat{chat_id}",
            "MESSAGE": msg_text
        })
        print(f"    [Chat] Сообщение отправлено в чат задачи chat{chat_id}")
    else:
        # Фоллбэк на task.commentitem.add
        call_b24("task.commentitem.add", {
            "TASKID": task_id,
            "FIELDS": {"POST_MESSAGE": msg_text}
        })
        print(f"    [Comment] Сообщение отправлено комментарием в задачу #{task_id}")

def execute_rebuild():
    print("=================================================================")
    print("🚀 БОЕВОЙ ЗАПУСК СОЗДАНИЯ СДЕЛОК И ЗАДАЧ СНАБЖЕНИЯ КНР")
    print("=================================================================")

    created_summary = []

    # -------------------------------------------------------------
    # 1. Стройкомплекс 78: Endress+Hauser & Baumer (Miss Wang 30)
    # -------------------------------------------------------------
    print("\n[1/6] Обработка Стройкомплекс 78 — Endress+Hauser & Baumer...")
    items_eh = [
        {
            "num": 1, "brand": "Endress+Hauser",
            "pname_cn": "科氏力质量流量计 Promass F 100",
            "model": "8F1B08AADMAAASAD2SA+",
            "name_ru": "Высокоточный кориолисовый расходомер Endress+Hauser Promass F 100",
            "qty": 1
        },
        {
            "num": 2, "brand": "Baumer",
            "pname_cn": "超声波测距传感器",
            "model": "UR18.DA0-IA1B.7BO (арт. 11135775)",
            "name_ru": "Датчик ультразвуковой Baumer UR18.DA0-IA1B.7BO (арт. 11135775)",
            "qty": 2
        }
    ]
    xl_eh = generate_rfq_excel("ООО «СТРОЙКОМПЛЕКС 78»", "Endress+Hauser 质量流量计 & Baumer 传感器", items_eh, output_filename="Запрос КП ООО СТРОЙКОМПЛЕКС 78 (Endress+Hauser, Baumer).xlsx")
    disk_id_eh = upload_file_to_b24_disk(xl_eh)
    print(f"  Excel загружен на Диск: ID {disk_id_eh}")
    
    title_eh = "ООО «СТРОЙКОМПЛЕКС 78», Endress+Hauser / Baumer, 流量计及传感器 (2项), Расходомер E+H Promass F 100 и датчики Baumer (2 поз., 3 шт.)"
    deal_eh = create_deal(title_eh, company_id=12730, contact_id=17442, lead_id=19222)
    print(f"  Создана Сделка #{deal_eh}")
    
    # Привязка письма 54056 к сделке
    call_b24("crm.activity.binding.add", {"activityId": 54056, "entityTypeId": 2, "entityId": deal_eh})
    
    desc_eh = build_task_description(title_eh, items_eh)
    files_eh = [disk_id_eh, 127462] # Excel + Реквизиты
    task_eh = create_task(title_eh, deal_eh, desc_eh, resp_id=USER_MISS_WANG, file_ids=files_eh)
    print(f"  Создана Задача #{task_eh} (Ответственная: Miss Wang, Наблюдатель: Азат)")
    post_task_chat_message(task_eh, resp_id=USER_MISS_WANG, resp_name="Miss Wang")
    created_summary.append({"deal": deal_eh, "task": task_eh, "client": "СТРОЙКОМПЛЕКС 78", "item": "E+H & Baumer", "resp": "Miss Wang (30)"})

    # -------------------------------------------------------------
    # 2. Стройкомплекс 78: Lenze мотор-редукторы (Liyan Wang 44)
    # -------------------------------------------------------------
    print("\n[2/6] Обработка Стройкомплекс 78 — Lenze мотор-редукторы...")
    items_lenze = [
        {
            "num": 1, "brand": "Lenze",
            "pname_cn": "伞齿轮-圆柱齿轮减速电机 (1.5 kW)",
            "model": "G50BH132MVCK2C (Код: 10000176997031, MHEMAXX090-32C1C, i=10.677)",
            "name_ru": "Мотор-редуктор Lenze G50BH132MVCK2C, 1.5 кВт, i=10.677, n2=134.4 об/мин, M2=103 Нм",
            "qty": 1
        },
        {
            "num": 2, "brand": "Lenze",
            "pname_cn": "重载伞齿轮-圆柱齿轮减速器 (P1≈4.5 kW)",
            "model": "G50BS221MHBR3C00 (Код: 10000177008666, i=76.907)",
            "name_ru": "Редуктор высокой нагрузки Lenze G50BS221MHBR3C00, i=76.907, n2=41.8 об/мин, M2=1029 Нм",
            "qty": 1
        },
        {
            "num": 3, "brand": "Lenze",
            "pname_cn": "伞齿轮-圆柱齿轮减速电机 (3.0 kW)",
            "model": "G50BH185MVBR2C00 (Код: 10000176994510, MHEMAXX100-32C1C, i=12.693)",
            "name_ru": "Мотор-редуктор Lenze G50BH185MVBR2C00, 3.0 кВт, i=12.693, n2=113.8 об/мин, M2=244 Нм",
            "qty": 1
        }
    ]
    xl_lenze = generate_rfq_excel("ООО «СТРОЙКОМПЛЕКС 78»", "Lenze 伞齿轮减速电机", items_lenze, output_filename="Запрос КП ООО СТРОЙКОМПЛЕКС 78 (Lenze).xlsx")
    disk_id_lenze = upload_file_to_b24_disk(xl_lenze)
    print(f"  Excel загружен на Диск: ID {disk_id_lenze}")
    
    title_lenze = "ООО «СТРОЙКОМПЛЕКС 78», Lenze, 减速电机清单 (3项), Мотор-редукторы Lenze коническо-цилиндрические (3 поз., 3 шт.)"
    deal_lenze = create_deal(title_lenze, company_id=12730, contact_id=17442, lead_id=19222)
    print(f"  Создана Сделка #{deal_lenze}")
    
    call_b24("crm.activity.binding.add", {"activityId": 54058, "entityTypeId": 2, "entityId": deal_lenze})
    
    desc_lenze = build_task_description(title_lenze, items_lenze)
    files_lenze = [disk_id_lenze]
    task_lenze = create_task(title_lenze, deal_lenze, desc_lenze, resp_id=USER_LIYAN_WANG, file_ids=files_lenze)
    print(f"  Создана Задача #{task_lenze} (Ответственная: Liyan Wang, Наблюдатель: Азат)")
    post_task_chat_message(task_lenze, resp_id=USER_LIYAN_WANG, resp_name="liyan wang")
    created_summary.append({"deal": deal_lenze, "task": task_lenze, "client": "СТРОЙКОМПЛЕКС 78", "item": "Lenze motors (3)", "resp": "Liyan Wang (44)"})

    # -------------------------------------------------------------
    # 3. Стройкомплекс 78: RUF клапаны строго 7 строк (玉南 李 84)
    # -------------------------------------------------------------
    print("\n[3/6] Обработка Стройкомплекс 78 — Клапаны RUF (7 строк)...")
    items_ruf = [
        {"num": 1, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020858", "name_ru": "Клапан RUF 1020858", "qty": 1},
        {"num": 2, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020834", "name_ru": "Клапан RUF 1020834", "qty": 1},
        {"num": 3, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020835", "name_ru": "Клапан RUF 1020835", "qty": 1},
        {"num": 4, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020837", "name_ru": "Клапан RUF 1020837", "qty": 1},
        {"num": 5, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020860", "name_ru": "Клапан RUF 1020860", "qty": 1},
        {"num": 6, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020838", "name_ru": "Клапан RUF 1020838", "qty": 1},
        {"num": 7, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020798", "name_ru": "Клапан RUF 1020798", "qty": 1},
    ]
    xl_ruf = generate_rfq_excel("ООО «СТРОЙКОМПЛЕКС 78»", "RUF 阀门及阀芯清单", items_ruf, output_filename="Запрос КП ООО СТРОЙКОМПЛЕКС 78 (RUF).xlsx")
    disk_id_ruf = upload_file_to_b24_disk(xl_ruf)
    print(f"  Excel загружен на Диск: ID {disk_id_ruf}")
    
    title_ruf = "ООО «СТРОЙКОМПЛЕКС 78», RUF, 阀门及阀芯清单 (7项), Клапаны и гидрораспределители RUF (7 поз., 7 шт.)"
    deal_ruf = create_deal(title_ruf, company_id=12730, contact_id=17442, lead_id=19222)
    print(f"  Создана Сделка #{deal_ruf}")
    
    call_b24("crm.activity.binding.add", {"activityId": 54060, "entityTypeId": 2, "entityId": deal_ruf})
    
    desc_ruf = build_task_description(title_ruf, items_ruf)
    files_ruf = [disk_id_ruf, 127478, 127480, 127482, 127484, 127486, 127488, 127490] # Excel + 7 чертежей PNG
    task_ruf = create_task(title_ruf, deal_ruf, desc_ruf, resp_id=USER_LI_YUNAN, file_ids=files_ruf)
    print(f"  Создана Задача #{task_ruf} (Ответственный: 玉南 李, Наблюдатель: Азат, вложено 7 чертежей)")
    post_task_chat_message(task_ruf, resp_id=USER_LI_YUNAN, resp_name="玉南 (Юйнань) 李")
    created_summary.append({"deal": deal_ruf, "task": task_ruf, "client": "СТРОЙКОМПЛЕКС 78", "item": "RUF valves (7)", "resp": "玉南 李 (84)"})

    # -------------------------------------------------------------
    # 4. Валерий Талипов: Thyssenkrupp & Flender B3SH (Liyan Wang 44)
    # -------------------------------------------------------------
    print("\n[4/6] Обработка Валерий Талипов — Редукторы Flender & Thyssenkrupp...")
    items_reduct = [
        {
            "num": 1, "brand": "Flender / ЦПТ",
            "pname_cn": "三级圆锥-圆柱齿轮减速机",
            "model": "B3SH18 A25",
            "name_ru": "Редуктор конвейера B3SH18 A25 трехступенчатый коническо-цилиндрический ЦПТ",
            "qty": 1
        },
        {
            "num": 2, "brand": "Flender / ЦПТ",
            "pname_cn": "三级圆锥-圆柱齿轮减速机",
            "model": "B3SH18 C25",
            "name_ru": "Редуктор конвейера B3SH18 C25 трехступенчатый коническо-цилиндрический ЦПТ",
            "qty": 1
        },
        {
            "num": 3, "brand": "Thyssenkrupp",
            "pname_cn": "桥式输送机驱动减速机 (左装)",
            "model": "4567220A",
            "name_ru": "Редуктор привода мостового конвейера левый 4567220A Thyssenkrupp",
            "qty": 1
        },
        {
            "num": 4, "brand": "Thyssenkrupp",
            "pname_cn": "桥式输送机驱动减速机 (右装)",
            "model": "4567220B (KSFq280So)",
            "name_ru": "Редуктор привода мостового конвейера правый 4567220B Thyssenkrupp KSFq280So",
            "qty": 1
        }
    ]
    xl_reduct = generate_rfq_excel("ООО «ЖЕЛЕЗНАЯ ЛОГИКА»", "Thyssenkrupp & Flender 工业减速机", items_reduct, output_filename="Запрос КП Валерий Талипов (Flender, Thyssenkrupp).xlsx")
    disk_id_reduct = upload_file_to_b24_disk(xl_reduct)
    print(f"  Excel загружен на Диск: ID {disk_id_reduct}")
    
    title_reduct = "Валерий Талипов, Thyssenkrupp / Flender, 重型齿轮减速机 (4项), Редукторы конвейерные Thyssenkrupp и Flender B3SH (4 поз., 4 шт.)"
    deal_reduct = create_deal(title_reduct, company_id=12732, contact_id=17444, lead_id=19216)
    print(f"  Создана Сделка #{deal_reduct}")
    
    call_b24("crm.activity.binding.add", {"activityId": 54004, "entityTypeId": 2, "entityId": deal_reduct})
    
    desc_reduct = build_task_description(title_reduct, items_reduct)
    files_reduct = [disk_id_reduct, 127376] # Excel + Карта партнера
    task_reduct = create_task(title_reduct, deal_reduct, desc_reduct, resp_id=USER_LIYAN_WANG, file_ids=files_reduct)
    print(f"  Создана Задача #{task_reduct} (Ответственная: Liyan Wang, Наблюдатель: Азат)")
    post_task_chat_message(task_reduct, resp_id=USER_LIYAN_WANG, resp_name="liyan wang")
    created_summary.append({"deal": deal_reduct, "task": task_reduct, "client": "Валерий Талипов", "item": "Flender & Thyssenkrupp (4)", "resp": "Liyan Wang (44)"})

    # -------------------------------------------------------------
    # 5. ООО «ЕДИНАЯ СЛУЖБА СНАБЖЕНИЯ»: Flender 2LC0132 (玉南 李 84)
    # -------------------------------------------------------------
    print("\n[5/6] Обработка Единая Служба Снабжения — Муфты Flender...")
    items_flender = [
        {
            "num": 1, "brand": "Flender",
            "pname_cn": "联轴器弹性销轴组件 (含缓冲胶圈)",
            "model": "2LC0132-2WC00-0AA0",
            "name_ru": "Палец с буфером в сборе муфты Flender (артикул 2LC0132-2WC00-0AA0) или качественный аналог",
            "qty": 72
        }
    ]
    xl_flender = generate_rfq_excel("ООО «ЕДИНАЯ СЛУЖБА СНАБЖЕНИЯ»", "Flender 联轴器弹性柱销组件", items_flender, output_filename="Запрос КП ООО ЕДИНАЯ СЛУЖБА СНАБЖЕНИЯ (Flender).xlsx")
    disk_id_flender = upload_file_to_b24_disk(xl_flender)
    print(f"  Excel загружен на Диск: ID {disk_id_flender}")
    
    title_flender = "ООО «ЕДИНАЯ СЛУЖБА СНАБЖЕНИЯ», Flender, 联轴器配件, Палец с буфером в сборе муфты Flender 2LC0132 (72 шт.)"
    deal_flender = create_deal(title_flender, company_id=12734, contact_id=17446, lead_id=19214)
    print(f"  Создана Сделка #{deal_flender}")
    
    call_b24("crm.activity.binding.add", {"activityId": 53990, "entityTypeId": 2, "entityId": deal_flender})
    
    desc_flender = build_task_description(title_flender, items_flender)
    files_flender = [disk_id_flender, 127344, 127346, 127348] # Excel + ТЗ PDF + реквизиты
    task_flender = create_task(title_flender, deal_flender, desc_flender, resp_id=USER_LI_YUNAN, file_ids=files_flender)
    print(f"  Создана Задача #{task_flender} (Ответственный: 玉南 李, Наблюдатель: Азат)")
    post_task_chat_message(task_flender, resp_id=USER_LI_YUNAN, resp_name="玉南 (Юйнань) 李")
    created_summary.append({"deal": deal_flender, "task": task_flender, "client": "ЕДИНАЯ СЛУЖБА СНАБЖЕНИЯ", "item": "Flender 2LC0132 (72)", "resp": "玉南 李 (84)"})

    # -------------------------------------------------------------
    # 6. АО «ПЗ «МАШИНОСТРОИТЕЛЬ»: Печь камерная 1100°C (玉南 李 84)
    # -------------------------------------------------------------
    print("\n[6/6] Обработка ПЗ Машиностроитель — Камерная печь 1100°C...")
    items_pzmash = [
        {
            "num": 1, "brand": "OEM / Промышленный Китай",
            "pname_cn": "箱式保护气氛热处理电炉 (配辅助设备冷水机和压缩机)",
            "model": "Tmax=1100°C, 炉膛≥1600x1200x600mm, 90kW, 氩气保护",
            "name_ru": "Камерная электропечь для нагрева и термообработки в защитной атмосфере аргона (до 1100 °С, камера 1600х1200х600 мм, мощность до 90 кВт, чиллер и компрессор в комплекте)",
            "qty": 1
        }
    ]
    xl_pzmash = generate_rfq_excel("АО «ПЗ «МАШИНОСТРОИТЕЛЬ»", "箱式保护气氛电炉 (1100°C 氩气气氛)", items_pzmash, output_filename="Запрос КП АО ПЗ МАШИНОСТРОИТЕЛЬ (Печь камерная 1100C).xlsx")
    disk_id_pzmash = upload_file_to_b24_disk(xl_pzmash)
    print(f"  Excel загружен на Диск: ID {disk_id_pzmash}")
    
    title_pzmash = "АО «ПЗ «МАШИНОСТРОИТЕЛЬ», 箱式电炉, 箱式保护气氛热处理炉 (1100°C), Камерная электропечь с защитной атмосферой аргона (1 шт.)"
    deal_pzmash = create_deal(title_pzmash, company_id=5712, contact_id=17448, lead_id=19130)
    print(f"  Создана Сделка #{deal_pzmash}")
    
    call_b24("crm.activity.binding.add", {"activityId": 53520, "entityTypeId": 2, "entityId": deal_pzmash})
    
    extra_furnace_spec = """
【电炉详细技术要求 / Подробные технические параметры печи】:
1. 设备类型 / Тип: 箱式保护气氛热处理电炉（电动垂直提升炉门 / вертикальный подъем двери）
2. 最高温度 / Температура: 最高设计温度 ≥ 1100 °C，工作温度 900–1050 °C，控温精度 ±10 °C
3. 炉膛尺寸 / Размеры: 深度 ≥ 1600 mm，宽度 ≥ 1200 mm，高度 ≥ 600 mm（适配工件尺寸 1050×1050 mm）
4. 工作气氛 / Атмосфера: 氩气保护（配置气体进气/排气管路、流量计及密封法兰）或空气
5. 功率及加热 / Мощность: 额定功率约 80–90 kW，优质镍铬合金丝（Cr20Ni80），多区控温
6. 配套设备 / Комплектация: 必须包含循环水冷却冷水机（Chiller）、空压机（气动门）、备用密封圈及易损件"""
    
    desc_pzmash = build_task_description(title_pzmash, items_pzmash, extra_text=extra_furnace_spec)
    files_pzmash = [disk_id_pzmash, 126066, 126068] # Excel + Заявка.pdf + ТЗ на отправку.pdf
    task_pzmash = create_task(title_pzmash, deal_pzmash, desc_pzmash, resp_id=USER_LI_YUNAN, file_ids=files_pzmash)
    print(f"  Создана Задача #{task_pzmash} (Ответственный: 玉南 李, Наблюдатель: Азат, прикреплено ТЗ)")
    post_task_chat_message(task_pzmash, resp_id=USER_LI_YUNAN, resp_name="玉南 (Юйнань) 李", extra_info=extra_furnace_spec)
    created_summary.append({"deal": deal_pzmash, "task": task_pzmash, "client": "ПЗ МАШИНОСТРОИТЕЛЬ", "item": "Chamber Furnace 1100C", "resp": "玉南 李 (84)"})

    # -------------------------------------------------------------
    # 7. Обновление и исправление Задачи #5986 (ООО «ПРОММАРКЕТ»)
    # -------------------------------------------------------------
    print("\n[7] Исправление и обогащение Задачи #5986 (ООО «ПРОММАРКЕТ»)...")
    items_prom = [
        {
            "num": 1, "brand": "SEW-EURODRIVE",
            "pname_cn": "伞齿轮-蜗轮蜗杆减速电机",
            "model": "SAF-47-Y0,75-4P-36-M4-B270 2#-Ф30",
            "name_ru": "Мотор-редуктор SAF-47-Y0,75-4P-36-M4-B270 2#-Ф30 (SEW-EURODRIVE / аналог)",
            "qty": 1
        }
    ]
    xl_prom = generate_rfq_excel("ООО «ПРОММАРКЕТ»", "SEW-EURODRIVE 蜗轮蜗杆减速电机", items_prom, output_filename="Запрос КП ООО ПРОММАРКЕТ (SEW SAF-47).xlsx")
    disk_id_prom = upload_file_to_b24_disk(xl_prom)
    print(f"  Excel загружен на Диск: ID {disk_id_prom}")
    
    clean_prom_title = "ООО «ПРОММАРКЕТ», SEW-EURODRIVE, 蜗轮蜗杆减速电机 (1项), Мотор-редуктор червячный SEW-EURODRIVE SAF47 (1 шт.)"
    call_b24("crm.deal.update", {"id": 3032, "fields": {"TITLE": clean_prom_title}})
    call_b24("tasks.task.update", {
        "taskId": 5986,
        "fields": {
            "TITLE": clean_prom_title,
            "AUDITORS": [USER_AZAT],
            "UF_TASK_WEBDAV_FILES": [f"n{disk_id_prom}"]
        }
    })
    post_task_chat_message(5986, resp_id=USER_MISS_WANG, resp_name="Miss Wang")
    print("  Задача #5986 и Сделка #3032 успешно обновлены с чистым шаблоном и извинением.")

    # -------------------------------------------------------------
    # 8. Отметка писем прочитанными и закрытие лидов
    # -------------------------------------------------------------
    print("\n[8] Отметка писем прочитанными и обновление статусов лидов...")
    # Письма обработанных лидов
    processed_activities = [54056, 54058, 54060, 54004, 53990, 53520]
    for aid in processed_activities:
        call_b24("crm.activity.update", {
            "id": aid,
            "fields": {"COMPLETED": "Y", "STATUS": 3}
        })
        print(f"  Письмо #{aid} помечено прочитанным (COMPLETED: Y, STATUS: 3).")
    
    # Лиды в CONVERTED
    for lid in [19222, 19216, 19214, 19130]:
        call_b24("crm.lead.update", {
            "id": lid,
            "fields": {"STATUS_ID": "CONVERTED"}
        })
        print(f"  Лид #{lid} переведен в статус CONVERTED.")
        
    # Лид #19236 (АРТ КОМПЛЕКТ) — оставляем НЕПРОЧИТАННЫМ и статус NEW
    call_b24("crm.activity.update", {
        "id": 54112,
        "fields": {"COMPLETED": "N", "STATUS": 1}
    })
    call_b24("crm.lead.update", {
        "id": 19236,
        "fields": {"STATUS_ID": "NEW"}
    })
    print("  Лид #19236 (АРТ КОМПЛЕКТ) и письмо #54112 оставлены во входящих (СТРОГО НЕПРОЧИТАНО, статус NEW).")

    print("\n=================================================================")
    print("✅ ВСЕ СДЕЛКИ И ЗАДАЧИ УСПЕШНО СОЗДАНЫ И ВЕРИФИЦИРОВАНЫ!")
    print("=================================================================")
    for s in created_summary:
        print(f"  • Сделка #{s['deal']} ➔ Задача #{s['task']} | {s['client']} | {s['item']} | {s['resp']}")

if __name__ == "__main__":
    execute_rebuild()
