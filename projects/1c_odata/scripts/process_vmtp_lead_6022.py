#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/process_vmtp_lead_6022.py
==================================================
Канонический процессор сложного лида #6022 (ПАО «ВМТП» / ZPMC 50 позиций).
Создает Сделку PREPARATION, Задачу Азату (user/20) со сроком 7 раб. дней,
формирует Excel-спецификацию на 50 позиций, загружает на Диск гр. 14,
отправляет двуязычное сообщение в чат с директивой по раздельному лоту.
"""

import os
import sys
import re
import datetime
import requests
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import docx

# Загрузка канонических функций из process_b24_inbound_leads
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import (
    call_b24, get_deadline_business_days, USER_AZAT, USER_ARTEM,
    GROUP_CHINA_SUPPLY, send_template_66_reply, bind_lead_activities_triple,
    verify_lead_processing_result, sanitize_html_email_text
)

LEAD_ID = 6022
COMPANY_ID = 5550  # ВМТП ПАО (ИНН 2504000204)
TZ_DOCX_PATH = "scratch_tz.docx"
DOCX_FILE_ID = 117242  # 3. Техническое задание.docx (Оригинал заказчика)
ZIP_FILE_ID = 117244   # Приложения к ТЗ.zip

DIRECTIVE_RU = (
    "ВНИМАНИЕ АЗАТУ ПО ОБРАБОТКЕ ЗАКУПКИ:\n"
    "Не надо сразу весь список обрабатывать! Там раздельный лот (скорее всего открытый тендер), "
    "что сможем, то и дадим. Выбирай те позиции, где у нас самые хорошие отношения с китайскими "
    "фабриками/поставщиками, самые лучшие цены, и мы быстрее всего с минимальными трудозатратами "
    "получим надежные КП. Представим клиенту сначала их. Что сделаем — то сделаем, чем больше, "
    "тем лучше, конечно, но всё бросать и заниматься только этим не стоит."
)

DIRECTIVE_CN = (
    "给阿扎特的采购说明（分标段采购策略）：\n"
    "注意：此清单包含50项ZPMC港口起重机备件。**不需要一次性全部处理！**\n"
    "客户为分包/分标段采购（大概率为港口公开招标），我们提供能拿到优势价格的部分即可。\n"
    "请优先挑选：我们有稳定优质供应商渠道、价格最优、且能以最小精力和最快速度拿到可靠报价的项目。\n"
    "原则：在不影响当前主要工作的前提下，能报多少项报多少项，以核心优势项目为主。"
)

def parse_tz_items(docx_path):
    doc = docx.Document(docx_path)
    table = doc.tables[0]
    items = []
    # Row 0 - заголовок
    for r in table.rows[1:]:
        cells = [c.text.strip().replace('\n', ' ') for c in r.cells]
        if len(cells) >= 6:
            num = cells[0]
            okpd = cells[1]
            name_ru = cells[2]
            chars = cells[3]
            unit = cells[4]
            qty_str = cells[5]
            
            # Позиция 47 - разрешен аналог, остальные - строго оригинал ZPMC
            allow_analog = (num == "47")
            items.append({
                "num": num,
                "okpd": okpd,
                "name_ru": name_ru,
                "chars": chars,
                "unit": unit,
                "qty": qty_str,
                "allow_analog": allow_analog
            })
    return items

def generate_vmtp_excel(items, output_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ZPMC Specification"
    ws.views.sheetView[0].showGridLines = True

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
    border_thin = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    headers = [
        "№ / 序号", "Наименование детали / 设备名称", "Характеристики / 技术参数",
        "Бренд / 品牌", "Кол-во / 数量", "Ед. изм. / 单位", "Аналог / 同等替代品"
    ]
    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    ws.row_dimensions[1].height = 28

    for it in items:
        analog_str = "РАЗРЕШЕН АНАЛОГ / 允许优质替代品" if it["allow_analog"] else "СТРОГО ОРИГИНАЛ ZPMC / 仅限原装正品"
        row_vals = [
            int(it["num"]) if it["num"].isdigit() else it["num"],
            it["name_ru"],
            it["chars"],
            "ZPMC",
            it["qty"],
            it["unit"],
            analog_str
        ]
        ws.append(row_vals)
        r_idx = ws.max_row
        ws.row_dimensions[r_idx].height = 32
        for col_idx in range(1, len(row_vals) + 1):
            c = ws.cell(row=r_idx, column=col_idx)
            c.border = border_thin
            c.alignment = center_align if col_idx in (1, 4, 5, 6, 7) else left_align
            if it["allow_analog"] and col_idx == 7:
                c.font = Font(name="Calibri", size=10, bold=True, color="008000")

    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 38
    ws.column_dimensions['C'].width = 65
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 14
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 30

    wb.save(output_path)
    print(f"[EXCEL-GEN] Успешно сгенерирован Excel на {len(items)} позиций: {output_path}")

def run_vmtp_pipeline(dry_run=False):
    print(f"=== ЗАПУСК ПРОЦЕССОРА ЛИДА #6022 (ВМТП / ZPMC 50 ПОЗИЦИЙ) [Режим: {'DRY-RUN' if dry_run else 'БОЕВОЙ'}] ===")
    
    lead = call_b24("crm.lead.get", {"id": LEAD_ID})
    if not lead:
        print(f"[ERROR] Лид #{LEAD_ID} не найден")
        return

    # 1. Парсинг позиций из ТЗ docx
    items = parse_tz_items(TZ_DOCX_PATH)
    print(f"1. Извлечено {len(items)} позиций из официального ТЗ docx")

    # 2. Формирование Excel
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    excel_filename = "Запрос КП ZPMC 港口起重机备件 ПАО ВМТП.xlsx"
    excel_full_path = os.path.join(desktop_path, excel_filename)
    if not dry_run:
        generate_vmtp_excel(items, excel_full_path)

    # 3. Дедлайн: 7 рабочих дней
    cur = datetime.datetime.now()
    added = 0
    while added < 7:
        cur += datetime.timedelta(days=1)
        if cur.weekday() < 5:
            added += 1
    cur = cur.replace(hour=18, minute=0, second=0, microsecond=0)
    deadline_plan = cur.strftime("%Y-%m-%dT%H:%M:%S+03:00")

    title_naming = 'ПАО "ВМТП", ZPMC 港口起重机备件 (50 поз.), Запасные части для кранов ZPMC (50 поз.)'

    # Текст описания задачи
    task_description = (
        f"[B]ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА ЗАКУПКУ / 采购技术要求 (ZPMC 港口起重机备件)[/B]\n"
        f"--------------------------------------------------\n"
        f"• Клиент / 客户: ПАО «Владивостокский морской торговый порт» (FESCO)\n"
        f"• Оборудование / 设备名称: Запасные части для кранов ZPMC STS и RTG\n"
        f"• Количество позиций / 清单项数: 50 позиций (подробно в прикрепленной спецификации Excel)\n"
        f"• Место поставки / 交货地点: г. Владивосток, ул. Стрельникова, 9 (склад ПАО «ВМТП»)\n"
        f"• Требования к качеству / 质量要求: Новые, не ранее 2024 года выпуска, гарантия 12 месяцев\n"
        f"• Допустимость аналогов / 替代品要求: По п.п. 1-46, 48-50 — [B]СТРОГО ОРИГИНАЛ ZPMC / 仅限原装正品[/B]. По п. 47 — [B]РАЗРЕШЕН КАЧЕСТВЕННЫЙ АНАЛОГ / 允许同等替代品[/B]\n\n"
        f"[B]{DIRECTIVE_RU}[/B]\n\n"
        f"[B]{DIRECTIVE_CN}[/B]\n\n"
        f"[B]ОРИГИНАЛЬНЫЙ ЗАПРОС КЛИЕНТА / 客户原始询价:[/B]\n"
        f"Добрый день.\n"
        f"Прошу выставить ваше КП на поставку запасных частей по файлам во вложении.\n"
        f"Стоимость доставки до ПАО «ВМТП» (г. Владивосток, ул. Стрельникова, д. 9) прошу включить в стоимость продукции.\n"
        f"Реквизиты ПАО «ВМТП»: ИНН 2504000204, г. Владивосток, ул. Стрельникова, 9\n"
        f"С уважением, Главный специалист отдела снабжения порта ТИМОШИН ВАСИЛИЙ АЛЕКСАНДРОВИЧ"
    )

    if dry_run:
        print(f"\n[DRY-RUN] ДЕТАЛЬНЫЙ ПЛАН ДЕЙСТВИЙ ДЛЯ ЛИДА #6022:")
        print(f"  1. Сделка в CRM: '{title_naming}' (Стадия: PREPARATION, Компания ID: {COMPANY_ID})")
        print(f"  2. Задача снабжению: Азат (user/20), Группа 14, Дедлайн: {deadline_plan} (+7 раб. дней)")
        print(f"  3. Загрузка на Диск группы 14: спецификация Excel + оригинальное ТЗ docx (ID {DOCX_FILE_ID}) + 'Приложения к ТЗ.zip' (ID {ZIP_FILE_ID})")
        print(f"  4. Особые указания Азату в теле задачи и чате:\n{'-'*60}\n{DIRECTIVE_RU}\n{'-'*60}")
        print(f"  5. Контакт: Тимошин Василий (+7 800 23-444-99 доб. 33728, vtimoshin@fesco.com)")
        print(f"  6. Автоответ Шаблон № 66: ДА (на vtimoshin@fesco.com)")
        print(f"  7. Запись в 1С:УНФ: привязка к существующему контрагенту ВМТП ПАО")
        return

    # БОЕВОЙ РЕЖИМ
    # 1. Создание контакта
    res_cnt = call_b24("crm.contact.list", {"filter": {"EMAIL": "vtimoshin@fesco.com"}}) or []
    if res_cnt:
        cnt_id = res_cnt[0]["ID"]
    else:
        cnt_id = call_b24("crm.contact.add", {"fields": {
            "NAME": "Василий", "LAST_NAME": "Тимошин", "SECOND_NAME": "доб. 33728",
            "POST": "Главный специалист отдела снабжения порта",
            "COMPANY_ID": COMPANY_ID,
            "EMAIL": [{"VALUE_TYPE": "WORK", "VALUE": "vtimoshin@fesco.com"}],
            "PHONE": [{"VALUE_TYPE": "WORK", "VALUE": "+7 (800) 234-44-99"}],
            "ASSIGNED_BY_ID": USER_ARTEM, "OPENED": "Y"
        }})
    print(f"  [B24] Контакт Василия Тимошина подготовлен: ID #{cnt_id}")

    # 2. Создание Сделки
    deal_id = call_b24("crm.deal.add", {"fields": {
        "TITLE": title_naming,
        "STAGE_ID": "PREPARATION",
        "COMPANY_ID": COMPANY_ID,
        "CONTACT_ID": cnt_id,
        "LEAD_ID": LEAD_ID,
        "ASSIGNED_BY_ID": USER_ARTEM,
        "OPENED": "Y"
    }})
    print(f"  [B24] Создана Сделка #{deal_id} в стадии PREPARATION")

    # 3. Загрузка Excel и архива чертежей на Диск группы 14
    f_storage = call_b24("disk.storage.getlist", {"filter": {"ENTITY_TYPE": "group", "ENTITY_ID": GROUP_CHINA_SUPPLY}}) or []
    storage_id = f_storage[0]["ID"] if f_storage else 46
    
    with open(excel_full_path, "rb") as ef:
        import base64
        b64_content = base64.b64encode(ef.read()).decode("utf-8")
    
    up_res = call_b24("disk.storage.uploadfile", {
        "id": storage_id,
        "data": {"NAME": excel_filename},
        "fileContent": b64_content,
        "generateUniqueName": "Y"
    })
    excel_disk_id = up_res.get("ID") if up_res else None
    print(f"  [B24-DISK] Спецификация загружена на Диск группы 14 (ID: {excel_disk_id})")

    # Копируем оригинальное ТЗ docx и архив чертежей на Диск группы 14
    docx_copy = call_b24("disk.file.copyto", {"id": DOCX_FILE_ID, "targetFolderId": storage_id})
    docx_disk_id = (docx_copy.get("ID") if docx_copy else None) or DOCX_FILE_ID
    print(f"  [B24-DISK] Оригинальное ТЗ docx подготовлен для снабжения (ID: {docx_disk_id})")

    zip_copy = call_b24("disk.file.copyto", {"id": ZIP_FILE_ID, "targetFolderId": storage_id})
    zip_disk_id = (zip_copy.get("ID") if zip_copy else None) or ZIP_FILE_ID
    print(f"  [B24-DISK] Архив чертежей подготовлен для снабжения (ID: {zip_disk_id})")

    supply_file_ids = [fid for fid in [excel_disk_id, docx_disk_id, zip_disk_id] if fid]

    # 4. Создание Задачи Азату
    task_id = call_b24("tasks.task.add", {"fields": {
        "TITLE": title_naming,
        "DESCRIPTION": task_description,
        "RESPONSIBLE_ID": USER_AZAT,
        "CREATED_BY": USER_ARTEM,
        "GROUP_ID": GROUP_CHINA_SUPPLY,
        "DEADLINE": deadline_plan,
        "UF_CRM_TASK": [f"D_{deal_id}"],
        "UF_TASK_WEBDAV_FILES": [f"n{fid}" for fid in supply_file_ids]
    }})
    if isinstance(task_id, dict) and "task" in task_id:
        task_id = task_id["task"]["id"]
    print(f"  [B24] Создана Задача #{task_id} на Азата (Дедлайн: {deadline_plan})")

    # 5. Двуязычный комментарий в чат задачи
    bilingual_comment = (
        f"[USER=20]阿扎特[/USER] Новая крупная заявка в снабжение КНР (ZPMC 50 позиций):\n\n"
        f"[B]{DIRECTIVE_RU}[/B]\n\n"
        f"[B]{DIRECTIVE_CN}[/B]\n\n"
        f"请协助询价以下设备（采购清单）：\n"
        f"- 品牌及型号：ZPMC 港口起重机备件 (50 项)\n"
        f"- 数量：详见Excel采购清单 (见附件)\n"
        f"- 替代品要求：第1-46项、48-50项仅限原装正品 (仅第47项电源允许同等替代品)\n"
        f"- 采购清单及图纸下载 (Файлы и чертежи):\n"
        f"- [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{excel_disk_id}/]{excel_filename}[/URL] (采购清单 / Спецификация 50 поз. Excel)\n"
        f"- [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{docx_disk_id}/]3. Техническое задание.docx[/URL] (Оригинальное ТЗ заказчика / 客户原始招标文件doc)\n"
        f"- [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{zip_disk_id}/]Приложения к ТЗ.zip[/URL] (图纸附件 / Архив чертежей)\n"
    )
    call_b24("task.commentitem.add", [task_id, {"POST_MESSAGE": bilingual_comment}])
    print(f"  [B24] Отправлен рабочий комментарий с директивой в чат задачи #{task_id}")

    # 6. Triple Activity Binding
    bind_lead_activities_triple(
        LEAD_ID,
        deal_id=deal_id,
        contact_id=cnt_id,
        company_id=COMPANY_ID,
        contact_email="vtimoshin@fesco.com",
        target_email_id=48934,
        dry_run=False
    )

    # 7. Автоответ Шаблон № 66
    send_template_66_reply(
        to_email="vtimoshin@fesco.com",
        original_subject="Запрос на поставку ZPMC 2026-3",
        assigned_user_id=USER_ARTEM,
        is_clear_rfq_flag=True
    )
    print(f"  [MAIL] Отправлен автоответ Шаблон № 66 клиенту на vtimoshin@fesco.com")

    # 8. Конвертация лида
    call_b24("crm.lead.update", {"id": LEAD_ID, "fields": {
        "STATUS_ID": "CONVERTED", "COMPANY_ID": COMPANY_ID, "CONTACT_ID": cnt_id
    }})
    print(f"  [B24] Лид #{LEAD_ID} успешно сконвертирован (CONVERTED)")

    # 9. Result Self-Check
    verify_lead_processing_result(deal_id=deal_id, contact_id=cnt_id, company_id=COMPANY_ID, task_id=task_id)
    print("  [SUCCESS] Обработка лида #6022 завершена успешно!")

if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    run_vmtp_pipeline(dry_run=is_dry)
