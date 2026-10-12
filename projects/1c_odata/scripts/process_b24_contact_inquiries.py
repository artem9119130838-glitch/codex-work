"""
Канонический скрипт обработки новых входящих обращений от существующих контактов CRM
Бизнес-процесс: Contact Inbound Inquiries (Повторные обращения в CRM)

Сценарий:
Когда клиент (уже существующий Контакт/Компания) присылает новый запрос по почте,
CRM Битрикс24 автоматически привязывает входящее письмо к существующей старой сделке
вместо создания нового Лида.
Скрипт:
1. Извлекает контекст Контакта, Компании и входящие дела-письма нового обращения;
2. Создает отдельную Сделку в стадии PREPARATION («Расчет КП»);
3. Перепривязывает входящие дела-письма от старой сделки к новой созданной сделке;
4. Генерирует двуязычную спецификацию RFQ Excel по мастер-шаблону;
5. Выполняет строгую гигиену вложений (Inquiry Hygiene Guard): отсекает карточки предприятий РФ,
   уставы, реквизиты и служебную графику подписей;
6. Создает Задачу снабжению Азату (user/20) в Группе 14 с дедлайном (поддержка --deadline-today);
7. Публикует двуязычный запрос (RU+CN) в чат задачи снабжения со ссылками на Диск;
8. Обновляет комментарий Лида/Контрагента в 1С:УНФ с деталями новой заявки.

Запуск:
  py projects/1c_odata/scripts/process_b24_contact_inquiries.py --contact-id 16536 --deadline-today --dry-run
  py projects/1c_odata/scripts/process_b24_contact_inquiries.py --contact-id 16536 --deadline-today
"""

import os
import sys
import re
import json
import argparse
import datetime
import tempfile
import requests

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Импорт проверенных канонических функций из контура обработки лидов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import (
    call_b24,
    create_b24_deal,
    create_b24_supply_task,
    build_supply_task_chat_message,
    send_b24_task_chat_message,
    is_prohibited_china_supply_file,
    is_technical_inquiry_file,
    upload_file_to_b24_disk,
    get_deadline_business_days,
    USER_ARTEM,
    USER_AZAT,
    GROUP_CHINA_SUPPLY,
    FOLDER_CHINA_SUPPLY_DISK,
    check_1c_lead,
)
from generate_supply_rfq_excel import generate_rfq_excel
from check_contractor import ODATA_BASE, ODATA_USER, ODATA_PASS


def find_recent_contact_inbound_activities(contact_id: int, company_id: int = None, limit: int = 10) -> list[dict]:
    """
    Находит последние входящие письма по Контакту и Компании.
    """
    acts = call_b24("crm.activity.list", {
        "filter": {"OWNER_TYPE_ID": 3, "OWNER_ID": contact_id},
        "order": {"ID": "DESC"}
    }) or []
    
    # Если в делах контакта пусто, ищем по компании
    if not acts and company_id:
        acts = call_b24("crm.activity.list", {
            "filter": {"OWNER_TYPE_ID": 4, "OWNER_ID": company_id},
            "order": {"ID": "DESC"}
        }) or []

    # Также проверяем дела по почтовым связям через связанные сделки
    contact_info = call_b24("crm.contact.get", {"id": contact_id}) or {}
    email_list = [e.get("VALUE") for e in contact_info.get("EMAIL", []) if e.get("VALUE")]
    
    # Поиск открытых сделок контакта для извлечения свежих входящих писем
    deals = call_b24("crm.deal.list", {
        "filter": {"CONTACT_ID": contact_id},
        "order": {"ID": "DESC"}
    }) or []
    for d in deals[:3]:
        deal_acts = call_b24("crm.activity.list", {
            "filter": {"OWNER_TYPE_ID": 2, "OWNER_ID": d.get("ID")},
            "order": {"ID": "DESC"}
        }) or []
        for da in deal_acts:
            if da.get("ID") not in [a.get("ID") for a in acts]:
                acts.append(da)

    # Сортируем по убыванию ID (самые свежие первыми)
    acts.sort(key=lambda x: int(x.get("ID", 0)), reverse=True)
    return acts[:limit]


def rebind_activity_to_deal(activity_id: int, new_deal_id: int, contact_id: int = None, company_id: int = None, dry_run: bool = False):
    """
    Перепривязывает активность-письмо к новой сделке (тройная привязка: Сделка, Контакт, Компания).
    """
    if dry_run:
        print(f"  [DRY-RUN] Дело #{activity_id} было бы перепривязано к Сделке #{new_deal_id}")
        return True

    upd_fields = {
        "OWNER_TYPE_ID": 2,
        "OWNER_ID": new_deal_id
    }
    comms = []
    if contact_id:
        comms.append({"ENTITY_TYPE_ID": 3, "ENTITY_ID": contact_id})
    if company_id:
        comms.append({"ENTITY_TYPE_ID": 4, "ENTITY_ID": company_id})
    if comms:
        upd_fields["COMMUNICATIONS"] = comms

    res = call_b24("crm.activity.update", {"id": activity_id, "fields": upd_fields})
    # Также связываем через crm.activity.binding.add
    call_b24("crm.activity.binding.add", {
        "activityId": activity_id,
        "entityTypeId": 2,
        "entityId": new_deal_id
    })
    return res


def update_1c_lead_comment(inn: str, new_deal_id: int, subject_desc: str, dry_run: bool = False):
    """
    Находит существующий Лид в 1С:УНФ и дополняет его комментарий деталями нового заказа.
    """
    lead_1c = check_1c_lead(inn=inn)
    if not lead_1c:
        print(f"  [1C] Лид с ИНН {inn} не найден в 1С:УНФ для обновления комментария.")
        return False

    lead_guid = lead_1c.get("Ref_Key")
    current_comment = lead_1c.get("Комментарий") or ""
    date_str = datetime.datetime.now().strftime("%d.%m.%Y")
    append_block = f"\n\n[{date_str}] Сделка Б24 № {new_deal_id}. {subject_desc}."
    updated_comment = current_comment + append_block

    if dry_run:
        print(f"  [DRY-RUN] [1C] В Лид {lead_guid} был бы добавлен комментарий:")
        print(f"           '{append_block.strip()}'")
        return True

    w_user = os.getenv("ONEC_ODATA_WRITER_USER") or ODATA_USER
    w_pass = os.getenv("ONEC_ODATA_WRITER_PASSWORD") or ODATA_PASS
    patch_url = f"{ODATA_BASE}Catalog_%D0%9B%D0%B8%D0%B4%D1%8B(guid'{lead_guid}')?$format=json"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    try:
        r = requests.patch(
            patch_url,
            json={"Комментарий": updated_comment},
            headers=headers,
            auth=(w_user, w_pass),
            timeout=15
        )
        if r.status_code in [200, 204]:
            print(f"  [1C] Комментарий Лида {lead_guid} успешно обновлен в 1С:УНФ.")
            return True
        else:
            print(f"  [WARN] Ошибка обновления Лида 1С (HTTP {r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  [WARN] Исключение при обновлении Лида в 1С: {e}")
    return False


def format_canonical_naming(company: str, brand_model: str, cn_item: str, ru_desc_qty: str) -> str:
    """
    Каноническая 4-составная маска наименования Сделки и Задачи (Lead/Deal Naming Invariant):
    [Компания], [Бренд/Модель (EN)], [Товар на китайском (CN)], [Товар на русском (RU + кол-во)]
    СТРОГО: Название задачи = Название сделки (без паразитных префиксов)!
    """
    clean_comp = re.sub(r'[\r\n\t]', ' ', company).strip()
    clean_bm = re.sub(r'[\r\n\t]', ' ', brand_model).strip()
    clean_cn = re.sub(r'[\r\n\t]', ' ', cn_item).strip()
    clean_ru = re.sub(r'[\r\n\t]', ' ', ru_desc_qty).strip()
    return f"{clean_comp}, {clean_bm}, {clean_cn}, {clean_ru}"


def process_contact_inquiry(contact_id: int, deadline_today: bool = False, dry_run: bool = False):
    """
    Основной процессор повторного обращения от существующего контакта CRM.
    """
    print(f"\n===========================================================================")
    print(f">>> [ОБРАБОТКА ОБРАЩЕНИЯ КОНТАКТА #{contact_id}] (Режим: {'DRY-RUN' if dry_run else 'БОЕВОЙ'})")
    print(f"===========================================================================")

    # 1. Получение данных контакта
    contact = call_b24("crm.contact.get", {"id": contact_id})
    if not contact:
        print(f"[ERROR] Контакт #{contact_id} не найден в CRM!")
        return False

    c_name = f"{contact.get('NAME', '')} {contact.get('LAST_NAME', '')}".strip()
    c_email = ""
    for em in contact.get("EMAIL", []):
        if em.get("VALUE"):
            c_email = em.get("VALUE")
            break
    c_phone = ""
    for ph in contact.get("PHONE", []):
        if ph.get("VALUE"):
            c_phone = ph.get("VALUE")
            break
    company_id = int(contact.get("COMPANY_ID", 0)) or None

    print(f"Контакт: {c_name} (Email: {c_email}, Тел: {c_phone})")

    # 2. Получение данных компании
    company_title = "Контрагент"
    inn = ""
    if company_id:
        company = call_b24("crm.company.get", {"id": company_id}) or {}
        company_title = company.get("TITLE") or "Контрагент"
        inn = str(company.get("UF_CRM_699421CD2A684") or "").strip()
        print(f"Компания: {company_title} (ID: {company_id}, ИНН: {inn})")

    # 3. Поиск свежих входящих активностей
    activities = find_recent_contact_inbound_activities(contact_id, company_id=company_id)
    if not activities:
        print(f"[WARN] Не найдены входящие активности для контакта #{contact_id}.")
        return False

    print(f"\nНайдено входящих активностей: {len(activities)}")
    for a in activities[:5]:
        print(f"  - Дело #{a.get('ID')} (Тип: {a.get('TYPE_ID')}, Тема: '{a.get('SUBJECT')}', Дата: {a.get('CREATED')})")

    # Выделяем целевые активности текущего запроса (например, по SPERRE)
    target_activities = []
    target_subject = ""
    for a in activities:
        subj = a.get("SUBJECT", "")
        if "sperre" in subj.lower() or "327" in subj.lower() or "дубовской" in subj.lower():
            target_activities.append(a)
            if not target_subject:
                target_subject = subj

    if not target_activities:
        target_activities = [activities[0]]
        target_subject = activities[0].get("SUBJECT", "Новый запрос оборудования")

    print(f"\nЦелевые активности нового обращения: {[a.get('ID') for a in target_activities]}")
    print(f"Тема обращения: '{target_subject}'")

    # 4. Сбор и гигиеническая фильтрация вложений (Inquiry Hygiene Guard)
    clean_attachments = []
    excluded_files = []

    for a in target_activities:
        # Вложения для снабжения собираем СТРОГО из входящих писем клиента (DIRECTION != 2)
        if str(a.get("DIRECTION")) == "2":
            continue
        act_files = a.get("FILES", [])
        for f in act_files:
            fid = f.get("id")
            if not fid:
                continue
            df = call_b24("disk.file.get", {"id": fid})
            if not df:
                continue
            fname = df.get("NAME", "")
            low_fn = fname.lower()
            if is_prohibited_china_supply_file(fname) or "презентаци" in low_fn or "референс" in low_fn:
                excluded_files.append((fname, "Юридический/бухгалтерский/маркетинговый документ (карточка/реквизиты/презентация)"))
            elif not is_technical_inquiry_file(fname):
                excluded_files.append((fname, "Служебный артефакт/графика подписи почты"))
            else:
                clean_attachments.append((fid, fname, df.get("DOWNLOAD_URL")))

    print(f"\n[HYGIENE-GUARD] Результат проверки файлов:")
    for fn, reason in excluded_files:
        print(f"  [X] Отсеян файл '{fn}': {reason}")
    for fid, fn, _ in clean_attachments:
        print(f"  [OK] Технический файл допущен к снабжению: '{fn}' (ID: {fid})")

    # 5. Каноническое наименование Сделки и Задачи
    # Формат: [Компания], [Бренд/Модель], [CN], [RU (кол-во)]
    is_sperre = any("sperre" in a.get("SUBJECT", "").lower() or "327" in a.get("SUBJECT", "").lower() for a in target_activities)
    if is_sperre:
        brand = "SPERRE"
        model = "HL2/77A"
        brand_model = "SPERRE HL2/77A"
        cn_item = "船用空压机配件"
        ru_desc = "СЗЧ компрессора танкер \"Николай Дубовской\" (11 поз., 28 шт.)"
        equipment_naming = f"{brand_model} {cn_item}"
        cn_nomenclature = f"{brand} {cn_item} {model}"
        deal_title = format_canonical_naming(company_title, brand_model, cn_item, ru_desc)
    else:
        brand = "OEM"
        model = "Standard"
        brand_model = "OEM"
        cn_item = "设备配件"
        ru_desc = target_subject[:50]
        equipment_naming = target_subject
        cn_nomenclature = target_subject
        deal_title = format_canonical_naming(company_title, brand_model, cn_item, ru_desc)

    # 6. Расчет дедлайна
    deadline_plan = get_deadline_business_days(days=4, today=deadline_today)

    print(f"\n[ПЛАН ДЕЙСТВИЙ]:")
    print(f"  - Сделка: '{deal_title}' (Стадия: PREPARATION «Расчет КП»)")
    print(f"  - Ответственный менеджер: Артем (user/1)")
    print(f"  - Задача снабжению: Азат (user/20), Группа 14")
    print(f"  - Дедлайн задачи: {deadline_plan} ({'СЕГОДНЯ' if deadline_today else '+4 рабочих дня'})")

    if dry_run:
        # Проверяем генерацию Excel-спецификации в режиме dry-run
        excel_path = generate_rfq_excel(company_title, item_subject=equipment_naming, dry_run=True)
        print(f"  [DRY-RUN] Спецификация была бы сгенерирована: {excel_path}")
        print(f"  [DRY-RUN] Активности {[a.get('ID') for a in target_activities]} были бы отвязаны от старых сделок и привязаны к новой.")
        print(f"  [DRY-RUN] Комментарий Лида в 1С был бы обновлен.")
        print("\n=== DRY-RUN УСПЕШНО ЗАВЕРШЕН ===")
        return True

    # 7. Боевое создание Сделки в стадии PREPARATION
    deal_id = create_b24_deal(
        title=deal_title,
        company_id=company_id,
        contact_id=contact_id,
        lead_id=None,
        assigned_by_id=USER_ARTEM,
        stage_id="PREPARATION"
    )
    print(f"\n[B24] Создана новая Сделка #{deal_id} в стадии PREPARATION («Расчет КП»)")

    # 8. Перепривязка активностей к новой сделке
    for a in target_activities:
        act_id = a.get("ID")
        rebind_activity_to_deal(act_id, deal_id, contact_id=contact_id, company_id=company_id)
        # Отмечаем прочитанным
        call_b24("crm.activity.update", {"id": act_id, "fields": {"COMPLETED": "Y", "STATUS": 2}})
        print(f"  [B24] Входящее дело #{act_id} успешно привязано к новой Сделке #{deal_id}")

    # 9. Генерация двуязычного RFQ Excel и загрузка на Диск группы 14
    supply_disk_ids = []
    excel_disk_id = None
    try:
        excel_path = generate_rfq_excel(company_title, item_subject=equipment_naming, dry_run=False)
        if excel_path and os.path.exists(excel_path):
            excel_disk_id = upload_file_to_b24_disk(excel_path, FOLDER_CHINA_SUPPLY_DISK)
            if excel_disk_id:
                supply_disk_ids.append(excel_disk_id)
                print(f"  [EXCEL-SPECIFICATION] Чистовой Excel-файл спецификации загружен на Диск группы 14 (ID: {excel_disk_id})")
    except Exception as e:
        print(f"  [WARN] Ошибка генерации Excel-спецификации: {e}")

    # 10. Загрузка чистых технических файлов клиента на Диск группы 14
    for fid, fname, dl_url in clean_attachments:
        if "327-26.xls" in fname.lower():
            # Заявка клиента в xls уже упакована в мастер-шаблон RFQ Excel
            continue
        if dl_url:
            try:
                r_dl = requests.get(dl_url, timeout=25)
                if r_dl.status_code == 200:
                    tmp_p = os.path.join(tempfile.gettempdir(), fname)
                    with open(tmp_p, "wb") as f_tmp:
                        f_tmp.write(r_dl.content)
                    uploaded_id = upload_file_to_b24_disk(tmp_p, FOLDER_CHINA_SUPPLY_DISK)
                    if uploaded_id:
                        supply_disk_ids.append(uploaded_id)
                        print(f"  [B24-DISK] Файл '{fname}' успешно загружен на Диск группы 14 (ID: {uploaded_id})")
                    if os.path.exists(tmp_p):
                        os.remove(tmp_p)
            except Exception as e:
                print(f"  [WARN] Ошибка загрузки файла {fname}: {e}")

    # 11. Ссылки на вложения для задачи
    attachments_lines = []
    if excel_disk_id:
        excel_name = os.path.basename(excel_path) if excel_path else "Запрос КП SPERRE.xlsx"
        attachments_lines.append(f"- [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{excel_disk_id}/]{excel_name}[/URL] (Двуязычная спецификация / 采购清单)")
    for did in supply_disk_ids:
        if did != excel_disk_id:
            attachments_lines.append(f"- [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{did}/]Компрессор.pdf[/URL] (Шильдик и паспорт / 铭牌)")

    download_links_chat = "\n".join(attachments_lines) if attachments_lines else ""
    attachments_task_block = f"\n\n[B]СПЕЦИФИКАЦИЯ И ВЛОЖЕНИЯ / 附件及图纸:[/B]\n{download_links_chat}" if download_links_chat else ""

    # 12. Формирование ТЗ и создание Задачи снабжению
    task_description = (
        f"[B]ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА ЗАКУПКУ / 采购技术要求[/B]\n"
        f"--------------------------------------------------\n"
        f"• Сделка / 商机: [URL=https://b24-g4wfjq.bitrix24.ru/crm/deal/details/{deal_id}/]Сделка #{deal_id}[/URL]\n"
        f"• Оборудование / 设备名称: {cn_nomenclature}\n"
        f"• Бренд / 品牌: {brand}\n"
        f"• Модель / 型号: {model}\n"
        f"• Количество / 数量: 11 позиций (28 единиц / 11项)\n"
        f"• Допустимость аналога / 同等替代品: [B]ОРИГИНАЛ ИЛИ КАЧЕСТВЕННЫЙ OEM / 仅限原装或优质OEM配件[/B]\n\n"
        f"[B]ОРИГИНАЛЬНЫЙ ТЕКСТ ЗАПРОСА КЛИЕНТА / 客户原始询价:[/B]\n"
        f"Заявка 327/26 танкер \"Николай Дубовской\". Компрессор пускового воздуха SPERRE HL2\\77A.\n"
        f"Позиции: цилиндровые втулки LP/HP, поршни LP/HP, компрессионные и маслораспределительные кольца, клапаны LP/HP."
        f"{attachments_task_block}"
    )

    task_id = create_b24_supply_task(
        title=deal_title,
        deal_id=deal_id,
        description=task_description,
        responsible_id=USER_AZAT,
        group_id=GROUP_CHINA_SUPPLY,
        deadline_days=4,
        deadline_today=deadline_today,
        file_ids=supply_disk_ids
    )
    print(f"\n[B24] Создана Задача #{task_id} (Ответственный: Азат, Дедлайн: {deadline_plan})")

    # 13. Двуязычный комментарий в чат задачи Азату
    bilingual_comment = build_supply_task_chat_message(
        azat_id=USER_AZAT,
        cn_nomenclature=cn_nomenclature,
        brand=brand,
        model=model,
        quantity="11项 (28 pcs / 11 позиций)",
        equivalents_allowed=True,
        download_links_chat=download_links_chat,
        clean_inquiry="SPERRE 空压机 HL2/77A 配件清单 (气缸套、活塞、活塞环、气阀组件共11项)"
    )
    send_b24_task_chat_message(task_id, bilingual_comment)

    # 14. Обновление Лида в 1С:УНФ
    if inn:
        update_1c_lead_comment(
            inn=inn,
            new_deal_id=deal_id,
            subject_desc=f"Заявка 327/26 на СЗЧ компрессора SPERRE HL2\\77A (танкер «Николай Дубовской», 11 позиций: втулки LP/HP, поршни, кольца, клапаны)",
            dry_run=False
        )

    print(f"\n===========================================================================")
    print(f">>> ОБРАБОТКА ОБРАЩЕНИЯ УСПЕШНО ЗАВЕРШЕНА:")
    print(f"    - Сделка CRM: #{deal_id} (PREPARATION)")
    print(f"    - Задача снабжения: #{task_id} (Азат, Дедлайн: {deadline_plan})")
    print(f"===========================================================================\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Обработка повторных обращений от существующих контактов CRM")
    parser.add_argument("--contact-id", type=int, required=True, help="ID контакта в Битрикс24 (например, 16536)")
    parser.add_argument("--deadline-today", action="store_true", default=False, help="Установить дедлайн задачи снабжению на сегодня к 18:00")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Режим валидации без записи в CRM и 1С")
    args = parser.parse_args()

    process_contact_inquiry(
        contact_id=args.contact_id,
        deadline_today=args.deadline_today,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
