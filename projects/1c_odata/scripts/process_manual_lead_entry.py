#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/process_manual_lead_entry.py
Канонический скрипт управляемой ручной обработки лидов и оффлайн-заявок (Canonical Manual Lead Entry).

Обеспечивает точечную калибровку параметров (ИНН, бренд, номенклатура, контакты)
при сбоях авто-парсинга на цитатах переписки, а также обработку сырых спам/оффлайн обращений
без накопления временных файлов в scratch/.

Соблюдает строгие регламенты:
- LEAD_PROCESSING_POLICY.md
- ERP_1C_POLICY.md
- CHINA_SUPPLY_POLICY.md
"""

import sys
import os
import re
import json
import argparse
import datetime
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Подключение каталога скриптов
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

import process_b24_inbound_leads as core
from check_contractor import verify_and_enrich_contractor, format_sbis_summary, write_to_bitrix24, format_onec_comment
from generate_supply_rfq_excel import generate_rfq_excel

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")

def process_manual_lead(
    lead_id: int = None,
    dry_run: bool = True,
    deadline_today: bool = True,
    override_inn: str = None,
    override_company: str = None,
    override_contact: str = None,
    override_email: str = None,
    override_phone: str = None,
    override_city: str = None,
    override_post: str = None,
    override_brand: str = None,
    override_model: str = None,
    override_name_ru: str = None,
    override_name_cn: str = None,
    override_qty_str: str = None,
    override_inquiry_text: str = None,
    technical_file_ids: list = None,
    responsible_id: int = core.USER_AZAT
):
    log(f"=== ЗАПУСК УПРАВЛЯЕМОЙ ОБРАБОТКИ ЛИДА #{lead_id} (Режим: {'DRY-RUN' if dry_run else 'БОЕВОЙ'}) ===")

    lead_data = {}
    lead_activities = []

    if lead_id:
        lead_data = core.call_b24("crm.lead.get", {"id": lead_id}) or {}
        if not lead_data:
            log(f"[ERROR] Лид #{lead_id} не найден в Битрикс24 CRM!")
            return None
        lead_activities = core.call_b24("crm.activity.list", {
            "filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lead_id},
            "select": ["ID", "SUBJECT", "DESCRIPTION", "FILES", "COMMUNICATIONS", "SETTINGS"]
        }) or []

    # 1. Контакты
    lead_email = override_email or ""
    if not lead_email and lead_data.get("EMAIL"):
        emails = lead_data.get("EMAIL", [])
        if emails and isinstance(emails, list):
            lead_email = emails[0].get("VALUE", "").strip()

    phone = override_phone or ""
    if not phone and lead_data.get("PHONE"):
        raw_p = lead_data["PHONE"][0].get("VALUE")
        if raw_p:
            phone, _ = core.normalize_phone_number(raw_p)

    contact_name = override_contact or ""
    if not contact_name:
        fn = lead_data.get("NAME") or ""
        ln = lead_data.get("LAST_NAME") or ""
        contact_name = f"{fn} {ln}".strip() or "Контактное лицо"

    # 2. ИНН и Скоринг DaData & СБИС
    inn = override_inn or ""
    company_title = override_company or lead_data.get("COMPANY_TITLE") or ""

    # Поиск сущностей в Б24
    existing_companies = []
    found_comp = core.find_b24_company(inn=inn, title=company_title)
    if found_comp:
        existing_companies = [found_comp]

    existing_company_id = int(existing_companies[0]["ID"]) if existing_companies else None

    # Запуск скоринга DaData & СБИС
    sbis_summary = ""
    tags_sbis = ["Конечный покупатель"]
    dadata_info = {}
    saby_info = {}
    official_name = company_title or "Компания клиента"

    if inn:
        log(f"Запуск СБИС-скоринга для ИНН: {inn}...")
        try:
            scoring_res = verify_and_enrich_contractor(
                inn=inn,
                b24_company_id=existing_company_id,
                b24_lead_id=lead_id,
                email=lead_email,
                dry_run=dry_run
            )
            if isinstance(scoring_res, dict):
                sbis_summary = scoring_res.get("summary_text") or format_sbis_summary(scoring_res)
                dadata_info = scoring_res.get("dadata", {}) or {}
                saby_info = scoring_res.get("saby", {}) or {}
                if dadata_info:
                    name_from_dadata = dadata_info.get("name_short") or dadata_info.get("name")
                    if name_from_dadata:
                        official_name = name_from_dadata.split(",")[0].strip()
                classification = scoring_res.get("classification", {}) or {}
                tags_sbis = classification.get("recommended_tags", ["Конечный покупатель"]) or ["Конечный покупатель"]
                log(f"СБИС Скоринг завершен: {saby_info.get('status')} | Теги: {tags_sbis}")
        except Exception as e:
            log(f"[WARN] Ошибка скоринга СБИС: {e}")

    log(f"Контрагент: '{official_name}', ИНН: '{inn}', Контакт: '{contact_name}', Email: '{lead_email}', Тел: '{phone}'")

    # 3. Номенклатура и ТЗ
    brand = override_brand or "OEM"
    model = override_model or ""
    name_ru = override_name_ru or ""
    name_cn = override_name_cn or ""
    qty_str = override_qty_str or "1 шт."

    # 4-составное наименование Сделки и Задачи
    deal_title = f"{official_name}, {brand} {model}, {name_cn}, {name_ru}".replace("  ", " ").strip(" ,")
    deal_title = re.sub(r'\s+', ' ', deal_title)
    if len(deal_title) > 250:
        deal_title = deal_title[:247] + "..."

    log(f"Каноническое наименование: '{deal_title}'")

    # Дедлайн
    now = datetime.datetime.now()
    if deadline_today:
        deadline_iso = f"{now.strftime('%Y-%m-%d')}T18:00:00+03:00"
    else:
        deadline_dt = core.get_deadline_business_days(days=4)
        deadline_iso = deadline_dt.strftime("%Y-%m-%dT18:00:00+03:00")

    # 4. Вложения и файлы Диска группы 14 (Shared Group Disk Invariant)
    uploaded_files_group14 = []
    supply_disk_ids = []

    # Перезаливка технических вложений
    if technical_file_ids and not dry_run:
        for tfid in technical_file_ids:
            try:
                df = core.call_b24("disk.file.get", {"id": tfid})
                if df and df.get("DOWNLOAD_URL"):
                    dl_url = df["DOWNLOAD_URL"]
                    fname = df.get("NAME", f"attachment_{tfid}")
                    r_dl = requests.get(dl_url, timeout=35)
                    if r_dl.status_code == 200:
                        tmp_p = os.path.join(os.environ.get("TEMP", r"C:\Temp"), fname)
                        with open(tmp_p, "wb") as f_tmp:
                            f_tmp.write(r_dl.content)
                        up_id = core.upload_file_to_b24_disk(tmp_p, core.FOLDER_CHINA_SUPPLY_DISK)
                        if up_id:
                            supply_disk_ids.append(up_id)
                            uploaded_files_group14.append({
                                "id": up_id,
                                "name": fname,
                                "url": f"https://b24-g4wfjq.bitrix24.ru/disk/showFile/{up_id}/"
                            })
                            log(f"[DISK-14] Технический файл '{fname}' загружен на Диск группы 14: ID={up_id}")
                        if os.path.exists(tmp_p):
                            os.remove(tmp_p)
            except Exception as e:
                log(f"[WARN] Ошибка перезаливки файла {tfid}: {e}")

    # Генерация и загрузка Excel-спецификации
    clean_company = re.sub(r'[^a-zA-Zа-яА-Я0-9]+', '_', official_name).strip('_')
    excel_fname = f"Запрос КП {clean_company}.xlsx"

    items_for_excel = [{
        "num": 1,
        "brand": brand,
        "model": model,
        "name_ru": name_ru,
        "pname_cn": name_cn,
        "qty": int(re.search(r'\d+', qty_str).group(0)) if re.search(r'\d+', qty_str) else 1
    }]

    if not dry_run:
        try:
            excel_path = generate_rfq_excel(official_name, item_subject=name_cn, items=items_for_excel, dry_run=False)
            if excel_path and os.path.exists(excel_path):
                up_xl = core.upload_file_to_b24_disk(excel_path, core.FOLDER_CHINA_SUPPLY_DISK)
                if up_xl:
                    supply_disk_ids.append(up_xl)
                    uploaded_files_group14.append({
                        "id": up_xl,
                        "name": excel_fname,
                        "url": f"https://b24-g4wfjq.bitrix24.ru/disk/showFile/{up_xl}/"
                    })
                    log(f"[DISK-14] Excel-спецификация загружена на Диск группы 14: ID={up_xl}")
        except Exception as e:
            log(f"[WARN] Ошибка генерации Excel: {e}")

    # 5. Тексты Задачи и Сообщения в Чат
    inquiry_text = override_inquiry_text or ""
    if not inquiry_text and lead_activities:
        # Извлекаем текст из самого свежего письма
        for a in lead_activities:
            desc = a.get("DESCRIPTION")
            if desc:
                inquiry_text = core.sanitize_html_email_text(desc)
                # Отсекаем цитирование старых писем
                inquiry_text = re.split(r'(?:--|\bс уважением\b|----------------|-----Original Message-----|\bКому:)', inquiry_text, flags=re.IGNORECASE)[0].strip()
                break

    if not inquiry_text:
        inquiry_text = lead_data.get("COMMENTS", "") or ""
        inquiry_text = re.sub(r'\[СБИС-СКОРИНГ\].*$', '', inquiry_text, flags=re.DOTALL | re.IGNORECASE).strip()

    links_block = ""
    for uf in uploaded_files_group14:
        links_block += f"- [URL={uf['url']}]{uf['name']}[/URL] (Диск группы 14 / 原图纸)\n"
    if not links_block and dry_run:
        links_block = "- [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/GROUP14_DISK_ID/]Спецификация и чертежи на общем Диске[/URL]\n"

    chat_message = (
        f"[USER={responsible_id}]阿扎特[/USER] Новая заявка в снабжение КНР:\n"
        f"请协助询价以下设备（采购清单）：\n"
        f"- 品牌及型号：{brand} {model}\n"
        f"- 数量：{qty_str}\n"
        f"- 替代品要求：仅限原装正品 (Только оригинал)\n"
        f"- 采购清单及图纸下载 (Файлы и чертежи):\n"
        f"{links_block}"
        f"- 客户原始需求 (Оригинальный запрос клиента):\n"
        f"[QUOTE]{inquiry_text[:1200]}[/QUOTE]"
    )

    task_desc = (
        f"[B]ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА ЗАКУПКУ / 采购技术要求[/B]\n"
        f"--------------------------------------------------\n"
        f"• Оборудование / 设备名称: {name_cn}\n"
        f"• Бренд / 品牌: {brand}\n"
        f"• Модель / 型号: {model}\n"
        f"• Количество / 数量: {qty_str}\n"
        f"• Допустимость аналога: [B]СТРОГО ОРИГИНАЛ / 仅限原装正品[/B]\n\n"
        f"[B]ОРИГИНАЛЬНЫЙ ТЕКСТ ЗАПРОСА КЛИЕНТА / 客户原始询价:[/B]\n"
        f"{inquiry_text[:1200]}\n\n"
        f"[B]СПЕЦИФИКАЦИЯ И ВЛОЖЕНИЯ / 附件及图纸:[/B]\n"
        f"{links_block}"
    )

    if dry_run:
        log("\n" + "="*65)
        log(f"[DRY-RUN ПЛАН ДЛЯ ЛИДА #{lead_id}]:")
        log(f"  Компания: {official_name} (ИНН {inn})")
        log(f"  Контакт: {contact_name} ({lead_email}, {phone})")
        log(f"  Сделка: '{deal_title}' (Стадия: PREPARATION)")
        log(f"  Задача: Азату ([USER={responsible_id}]), Дедлайн: {deadline_iso}")
        log(f"  Технические файлы: {technical_file_ids or 'Нет'}")
        log(f"  1С:УНФ: Создание/обновление Лида в каталоге Лиды с ТЧ КонтактнаяИнформация")
        log(f"  Б24 Лид #{lead_id}: статус CONVERTED")
        log("="*65 + "\n")
        return {"status": "DRY-RUN OK", "deal_title": deal_title}

    # ================= БОЕВОЙ РЕЖИМ =================
    log(">>> ВЫПОЛНЕНИЕ БОЕВЫХ ОПЕРАЦИЙ В CRM И 1С...")

    # 1. Компания
    comp_res = core.enrich_or_create_b24_company(
        title=official_name,
        inn=inn,
        phone=phone,
        email=lead_email,
        web=dadata_info.get("website") or "",
        address=dadata_info.get("address"),
        contact_company_id=existing_company_id,
        dry_run=False
    )
    company_id = int(comp_res.get("ID") or comp_res.get("id")) if isinstance(comp_res, dict) else int(comp_res)
    log(f"[B24] Компания #{company_id} готова ('{official_name}')")

    if sbis_summary and company_id:
        try:
            write_to_bitrix24(b24_company_id=company_id, b24_lead_id=lead_id, summary_text=sbis_summary, dry_run=False)
        except Exception as e:
            log(f"[WARN] Ошибка записи скоринга в компанию: {e}")

    # 2. Контакт
    cont_res = core.enrich_or_create_b24_contact(
        name=contact_name,
        email=lead_email,
        phone=phone,
        company_id=company_id,
        post=override_post or "Специалист",
        dry_run=False
    )
    contact_id = int(cont_res.get("ID") or cont_res.get("id")) if isinstance(cont_res, dict) else int(cont_res)
    log(f"[B24] Контакт #{contact_id} готов ('{contact_name}')")

    # 3. Сделка
    deal_id = core.create_b24_deal(
        title=deal_title,
        company_id=company_id,
        contact_id=contact_id,
        lead_id=lead_id,
        assigned_by_id=core.USER_ARTEM,
        stage_id="PREPARATION"
    )
    log(f"[B24] Создана Сделка #{deal_id} в стадии PREPARATION")

    if sbis_summary and deal_id:
        try:
            write_to_bitrix24(b24_deal_id=deal_id, summary_text=sbis_summary, dry_run=False)
        except Exception as e:
            log(f"[WARN] Ошибка записи скоринга в сделку: {e}")

    # 4. Задача снабжению
    task_desc_with_deal = f"• Сделка / 商机: [URL=https://b24-g4wfjq.bitrix24.ru/crm/deal/details/{deal_id}/]Сделка #{deal_id}[/URL]\n" + task_desc
    task_id = core.create_b24_supply_task(
        title=deal_title,
        deal_id=deal_id,
        description=task_desc_with_deal,
        responsible_id=responsible_id,
        group_id=core.GROUP_CHINA_SUPPLY,
        deadline_days=4,
        deadline_today=deadline_today,
        file_ids=supply_disk_ids
    )
    log(f"[B24] Поставлена Задача #{task_id} на Азата в группе 14 (дедлайн: {deadline_iso})")

    # Чат задачи
    if task_id:
        core.send_b24_task_chat_message(task_id, chat_message, dry_run=False)
        log(f"[B24] В чат задачи #{task_id} отправлено двуязычное ТЗ")

    # 5. Тройная привязка активностей
    target_act_id = lead_activities[0].get("ID") if lead_activities else None
    core.bind_lead_activities_triple(
        lead_id=lead_id,
        deal_id=deal_id,
        contact_id=contact_id,
        company_id=company_id,
        contact_email=lead_email,
        target_email_id=target_act_id
    )
    log(f"[B24] Активности лида привязаны к Сделке #{deal_id}")

    # 6. Регистрация в 1С:УНФ
    try:
        log("Синхронизация с 1С:УНФ...")
        ca_1c = core.check_1c_counterparty(inn=inn, name=official_name)
        lead_1c = core.check_1c_lead(inn=inn, name=official_name)

        onec_comment_str = format_onec_comment({"classification": {"recommended_tags": tags_sbis}, "dadata": dadata_info, "saby": saby_info})
        if sbis_summary:
            onec_comment_str += f"\nСделка Б24: #{deal_id}"

        # Папка бренда
        brand_folder_key = None
        BRAND_FOLDERS_1C = {
            "abb": "235c18df-65e7-11ef-969d-70a8d3ba8753",
            "siemens": "7f686a73-80a8-11ef-96a0-70a8d3ba8753",
            "caterpillar": "f11aae25-c8cb-11ed-b999-f01898a67170",
            "cat": "f11aae25-c8cb-11ed-b999-f01898a67170",
            "festo": "896e53ec-b5fd-11ef-81a9-02006df8aab5",
            "danfoss": "511b6a35-f182-11ee-9684-70a8d3ba8753",
            "hydac": "2af0066c-5de5-11f1-9151-02006df8aab5",
            "gemu": "93e23206-5dec-11f1-9151-02006df8aab5",
        }
        b_low = brand.lower()
        for bk, bval in BRAND_FOLDERS_1C.items():
            if bk in b_low:
                brand_folder_key = bval
                break

        tag_rows = []
        for idx, t_name in enumerate(set(tags_sbis), start=1):
            t_guid = core.TAG_IDS_1C.get(t_name)
            if t_guid:
                tag_rows.append({"LineNumber": str(idx), "Тег": t_guid, "Тег_Key": t_guid})

        if not ca_1c and not lead_1c:
            lead_payload = {
                "Description": official_name,
                "НаименованиеКомпании": official_name,
                "Тема": f"ИНН: {inn} (Сделка #{deal_id})" if inn else f"{official_name} (Сделка #{deal_id})",
                "Вид": "ПервичноеОбращение",
                "Ответственный_Key": core.ARTEM_RESPONSIBLE_1C,
                "ИсточникПривлечения_Key": core.SOURCE_SITE_LV_1C,
                "СостояниеЛида_Key": "0c989b06-70c5-11ed-b990-f01898a67170",
                "Комментарий": onec_comment_str
            }
            if brand_folder_key:
                lead_payload["Parent_Key"] = brand_folder_key
                log(f"[1C] Назначена папка бренда: {brand} (Parent_Key: {brand_folder_key})")

            r_lead = requests.post(f"{core.ONEC_BASE}/Catalog_Лиды?$format=json", json=lead_payload, auth=core.ONEC_AUTH_WRITE, timeout=15)
            if r_lead.status_code in (200, 201):
                new_guid = r_lead.json().get("Ref_Key")
                log(f"[1C] Создан новый Лид в 1С:УНФ (GUID {new_guid})")
                ci_rows = []
                if lead_email:
                    ci_rows.append({"LineNumber": "1", "Тип": "АдресЭлектроннойПочты", "Вид_Key": core.CI_EMAIL, "Представление": lead_email, "АдресЭП": lead_email, "АдресЭПДляПоиска": lead_email})
                if phone:
                    ci_rows.append({"LineNumber": "2", "Тип": "Телефон", "Вид_Key": core.CI_PHONE, "Представление": phone, "НомерТелефона": phone, "НомерДляПоиска": re.sub(r'\D', '', phone)})
                if ci_rows:
                    requests.patch(f"{core.ONEC_BASE}/Catalog_Лиды(guid'{new_guid}')?$format=json", json={"КонтактнаяИнформация": ci_rows}, auth=core.ONEC_AUTH_WRITE, timeout=15)
                if tag_rows:
                    requests.patch(f"{core.ONEC_BASE}/Catalog_Лиды(guid'{new_guid}')?$format=json", json={"Теги": tag_rows}, auth=core.ONEC_AUTH_WRITE, timeout=15)
        elif lead_1c:
            l_guid = lead_1c.get("Ref_Key")
            log(f"[1C] Обновление существующего Лида 1С (GUID {l_guid})")
            existing_comm = lead_1c.get("Комментарий") or ""
            new_comm = f"{existing_comm}\nСделка #{deal_id}: {deal_title}".strip()
            requests.patch(f"{core.ONEC_BASE}/Catalog_Лиды(guid'{l_guid}')?$format=json", json={"Комментарий": new_comm}, auth=core.ONEC_AUTH_WRITE, timeout=15)
            if tag_rows:
                requests.patch(f"{core.ONEC_BASE}/Catalog_Лиды(guid'{l_guid}')?$format=json", json={"Теги": tag_rows}, auth=core.ONEC_AUTH_WRITE, timeout=15)
    except Exception as e:
        log(f"[WARN] Ошибка синхронизации с 1С: {e}")

    # 7. Конвертация Лида Б24
    if lead_id:
        core.call_b24("crm.lead.update", {
            "id": lead_id,
            "fields": {
                "STATUS_ID": "CONVERTED",
                "COMPANY_ID": company_id,
                "CONTACT_ID": contact_id
            }
        })
        log(f"[B24] Лид #{lead_id} успешно сконвертирован (STATUS_ID=CONVERTED)")

    log(f"=== ОБРАБОТКА ЛИДА #{lead_id} УСПЕШНО ЗАВЕРШЕНА! ===")
    return {
        "lead_id": lead_id,
        "company_id": company_id,
        "contact_id": contact_id,
        "deal_id": deal_id,
        "task_id": task_id,
        "deal_title": deal_title
    }

def main():
    parser = argparse.ArgumentParser(description="Канонический скрипт управляемой ручной обработки лидов и оффлайн заявок")
    parser.add_argument("--lead-id", type=int, help="ID лида Битрикс24")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Режим сухого прогона без сохранения изменений")
    parser.add_argument("--deadline-today", action="store_true", default=True, help="Дедлайн сегодня к 18:00 (по умолчанию True)")
    parser.add_argument("--responsible", type=str, default="azat", help="Ответственный: azat (20) или wang (30)")
    parser.add_argument("--inn", type=str, help="Точный ИНН организации")
    parser.add_argument("--company", type=str, help="Официальное наименование компании")
    parser.add_argument("--contact", type=str, help="ФИО контактного лица")
    parser.add_argument("--email", type=str, help="Email")
    parser.add_argument("--phone", type=str, help="Телефон")
    parser.add_argument("--city", type=str, help="Город клиента")
    parser.add_argument("--post", type=str, help="Должность контакта")
    parser.add_argument("--brand", type=str, help="Бренд оборудования")
    parser.add_argument("--model", type=str, help="Модель оборудования")
    parser.add_argument("--name-ru", type=str, help="Русское наименование оборудования")
    parser.add_argument("--name-cn", type=str, help="Китайское наименование оборудования")
    parser.add_argument("--qty", type=str, help="Количество")
    parser.add_argument("--text", type=str, help="Оригинальный текст заявки")
    parser.add_argument("--technical-files", type=int, nargs="+", help="Список ID файлов на Диске CRM для загрузки в группу 14")

    args = parser.parse_args()

    resp_id = core.USER_MISS_WANG if str(args.responsible).lower() in ["wang", "30", "miss_wang"] else core.USER_AZAT

    process_manual_lead(
        lead_id=args.lead_id,
        dry_run=args.dry_run,
        deadline_today=args.deadline_today,
        override_inn=args.inn,
        override_company=args.company,
        override_contact=args.contact,
        override_email=args.email,
        override_phone=args.phone,
        override_city=args.city,
        override_post=args.post,
        override_brand=args.brand,
        override_model=args.model,
        override_name_ru=args.name_ru,
        override_name_cn=args.name_cn,
        override_qty_str=args.qty,
        override_inquiry_text=args.text,
        technical_file_ids=args.technical_files,
        responsible_id=resp_id
    )

if __name__ == "__main__":
    main()
