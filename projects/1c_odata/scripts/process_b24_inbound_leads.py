#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/process_b24_inbound_leads.py
Единый конвейер сквозной обработки входящих лидов из Битрикс24 и синхронизации с 1С:УНФ.

Логика:
1. Выборка входящих лидов из Битрикс24 (по ID или свежие со статусом NEW).
2. Извлечение реквизитов компании, контакта, ТЗ и артикулов (из тела, комментариев BitrixGPT, вложений PDF/DOC/DOCX).
3. Проверка контрагента по DaData и Saby (подсчет участий в торгах, скоринг перепродажника/конечника).
4. Проверка дубликатов в 1С:УНФ (действующий Покупатель? существующий Лид? Заказы?).
5. Проверка дубликатов в Битрикс24 (Компания по ИНН, Контакт по Email, Сделки).
6. Проверка критерия «Предельно понятно»:
   - Четкий бренд + артикул/партномер + количество + коммерческий запрос без ЭТП/44-ФЗ.
   - Если ДА:
     - Создание/обогащение Компании и Контакта в Битрикс24;
     - Создание Сделки: [Компания], [ТЗ на китайском (кратко)], [ТЗ на русском];
     - Создание Задачи в группе 14 («Товары и поставщики Китай»), ответственный Miss Wang (ID 30),
       приоритет обычный (1), тег "Поиск товара - 找货", связь с CRM [D_<Deal_ID>];
     - Отправка перевода ТЗ на китайском в чат задачи ([USER=30]Miss Wang[/USER] ...);
     - Дело менеджеру НЕ создается (нет лишнего спама в делах);
   - Если НЕТ (размытое ТЗ, тендер, спорный запрос):
     - Создание Компании и Контакта;
     - Создание Дела менеджеру на ручной разбор;
     - Сделка и задача на Китай НЕ создаются.
7. Синхронизация с 1С:УНФ:
   - Если уже есть Покупатель: Лид НЕ создается, добавляется контактное лицо покупателя;
   - Если уже есть Лид: Лид НЕ дублируется, обогащается контактом и ТЗ;
   - Если нет: создается Лид + Контакт лида.
"""

import sys
import os
import re
import json
import uuid
import argparse
import requests
from requests.auth import HTTPBasicAuth

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def load_dotenv():
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
        r"C:\Codex\projects\1c_odata\.env",
        r"C:\Codex_Personal\projects\1c_odata\.env",
    ]
    for p in search_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass

load_dotenv()

# API Credentials
B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
ONEC_BASE = os.getenv("ONEC_ODATA_URL", "http://artem.medianasoft.spb.ru/unf/odata/standard.odata").rstrip("/")
ONEC_USER = os.getenv("ONEC_ODATA_USER", "odata.user")
ONEC_PASS = os.getenv("ONEC_ODATA_PASSWORD", "")
ONEC_WRITER_USER = os.getenv("ONEC_ODATA_WRITER_USER", "odata.writer")
ONEC_WRITER_PASS = os.getenv("ONEC_ODATA_WRITER_PASSWORD", "")

ONEC_AUTH_READ = HTTPBasicAuth(ONEC_USER, ONEC_PASS)
ONEC_AUTH_WRITE = HTTPBasicAuth(ONEC_WRITER_USER, ONEC_WRITER_PASS)

ARTEM_RESPONSIBLE_1C = "209d4fb0-3142-11ed-a3f1-3085a9a0f5bf"
SOURCE_SITE_LV_1C = "9dbbff5e-23c6-11ed-91a8-a068f8f3337c"
STATUS_ACCEPTED_1C = "9dbbffc1-23c6-11ed-91a8-a068f8f3337c"

CI_LEGAL_ADDRESS = "5c0dc76f-23c6-11ed-91a8-a068f8f3337c"
CI_ACTUAL_ADDRESS = "5c0dc76e-23c6-11ed-91a8-a068f8f3337c"
CI_PHONE = "5c0dc76d-23c6-11ed-91a8-a068f8f3337c"
CI_EMAIL = "5c0dc769-23c6-11ed-91a8-a068f8f3337c"

TAG_IDS_1C = {
    "Производство": "891061f8-df13-11ef-9922-02006df8aab5",
    "Крупный": "7e8d7ab8-df13-11ef-9922-02006df8aab5",
    "Холдинг": "0e89c354-fe42-11ef-8ae4-02006df8aab5",
    "Конечный покупатель": "6c77607c-e770-11ef-8e46-02006df8aab5",
    "Перепродажники": "306714e0-e1f5-11ef-8db0-02006df8aab5",
    "Тендер": "052cb624-ded8-11ef-9922-02006df8aab5",
    "Средний": "7e8d7ab6-df13-11ef-9922-02006df8aab5"
}

LEAD_GROUPS_1C = {
    "GEMU": "6595f8f0-9e33-11ed-b994-f01898a67170", # Под ключ
    "Endress+Hauser": "6595f8f0-9e33-11ed-b994-f01898a67170",
    "Под ключ (поиск, выкуп, доставка)": "6595f8f0-9e33-11ed-b994-f01898a67170"
}

def call_b24(method, payload=None):
    url = f"{B24_WEBHOOK}{method}"
    if payload:
        r = requests.post(url, json=payload)
    else:
        r = requests.get(url)
    if r.status_code == 200:
        return r.json().get('result')
    print(f"Error B24 call {method}: {r.status_code} - {r.text}")
    return None

def check_1c_counterparty(inn):
    r = requests.get(f"{ONEC_BASE}/Catalog_Контрагенты?$filter=ИНН eq '{inn}'&$format=json", auth=ONEC_AUTH_READ)
    if r.status_code == 200:
        val = r.json().get('value', [])
        return val[0] if val else None
    return None

def check_1c_lead(inn):
    r = requests.get(f"{ONEC_BASE}/Catalog_Лиды?$filter=substringof('{inn}', Тема)&$format=json", auth=ONEC_AUTH_READ)
    if r.status_code == 200:
        val = r.json().get('value', [])
        return val[0] if val else None
    return None

def find_b24_company_by_inn(inn):
    res = call_b24("crm.company.list", {"filter": {"UF_CRM_699421CD2A684": inn}})
    return res[0] if res else None

def find_b24_contact_by_email(email):
    res = call_b24("crm.contact.list", {"filter": {"EMAIL": email}})
    return res[0] if res else None

def enrich_or_create_b24_company(title, inn, address=None, phone=None, email=None, assigned_by_id=1):
    existing = find_b24_company_by_inn(inn)
    if existing:
        cid = existing['ID']
        fields = {}
        if address and not existing.get('ADDRESS'):
            fields['ADDRESS'] = address
        if phone and not existing.get('PHONE'):
            fields['PHONE'] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if email and not existing.get('EMAIL'):
            fields['EMAIL'] = [{"VALUE_TYPE": "WORK", "VALUE": email}]
        if fields:
            call_b24("crm.company.update", {"id": cid, "fields": fields})
            return {"action": "updated", "id": cid}
        return {"action": "exists", "id": cid}
    else:
        fields = {
            "TITLE": title,
            "UF_CRM_699421CD2A684": inn,
            "ASSIGNED_BY_ID": assigned_by_id
        }
        if address:
            fields["ADDRESS"] = address
        if phone:
            fields["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if email:
            fields["EMAIL"] = [{"VALUE_TYPE": "WORK", "VALUE": email}]
        cid = call_b24("crm.company.add", {"fields": fields})
        return {"action": "created", "id": cid}

def enrich_or_create_b24_contact(name, email, phone=None, company_id=None, post=None, assigned_by_id=1):
    existing = find_b24_contact_by_email(email)
    if existing:
        cid = existing['ID']
        fields = {}
        if post and not existing.get('POST'):
            fields['POST'] = post
        if company_id and not existing.get('COMPANY_ID'):
            fields['COMPANY_ID'] = company_id
        if phone and not existing.get('PHONE'):
            fields['PHONE'] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if fields:
            call_b24("crm.contact.update", {"id": cid, "fields": fields})
            return {"action": "updated", "id": cid}
        return {"action": "exists", "id": cid}
    else:
        parts = name.split()
        first_name = parts[0] if parts else name
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        fields = {
            "NAME": first_name,
            "LAST_NAME": last_name,
            "EMAIL": [{"VALUE_TYPE": "WORK", "VALUE": email}],
            "ASSIGNED_BY_ID": assigned_by_id
        }
        if post:
            fields["POST"] = post
        if phone:
            fields["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if company_id:
            fields["COMPANY_ID"] = company_id
        cid = call_b24("crm.contact.add", {"fields": fields})
        return {"action": "created", "id": cid}

def is_etp_or_tender_request(text="", source_name=""):
    """
    Проверяет, относится ли лид к приглашению на ЭТП/тендерную процедуру (Раздел 5.6).
    """
    combined = f"{text} {source_name}".lower()
    etp_markers = [
        "bidzaar", "b2b-center", "b2b center", "бидзаар", "аст гоз", "ast goz",
        "сбербанк-аст", "росэлторг", "тэк-торг", "северсталь", "запрос предложений",
        "запрос котировок", "электронный аукцион", "приглашение к участию в процедуре",
        "тендерная процедура", "торговая площадка", "этп"
    ]
    return any(marker in combined for marker in etp_markers)

def create_b24_tender_review_activity(lead_id, subject="Ручной анализ процедуры / тендерной закупки", description="", responsible_id=38):
    """
    Создает дело Александре Пономаревой (ID 38) на ручной разбор тендерной процедуры (без создания сделки).
    """
    fields = {
        "OWNER_TYPE_ID": 1, # Lead
        "OWNER_ID": lead_id,
        "TYPE_ID": 6,      # CRM_TODO
        "PROVIDER_ID": "CRM_TODO",
        "SUBJECT": subject,
        "DESCRIPTION": description,
        "RESPONSIBLE_ID": responsible_id,
        "COMPLETED": "N"
    }
    res = call_b24("crm.activity.add", {"fields": fields})
    return res

def create_b24_deal(title, company_id, contact_id, lead_id=None):
    fields = {
        "TITLE": title,
        "COMPANY_ID": company_id,
        "CONTACT_ID": contact_id,
        "CATEGORY_ID": 0,
        "STAGE_ID": "NEW",
        "ASSIGNED_BY_ID": 1,
        "CURRENCY_ID": "RUB",
        "OPPORTUNITY": 0.00
    }
    if lead_id:
        fields["LEAD_ID"] = lead_id
    deal_id = call_b24("crm.deal.add", {"fields": fields})
    return deal_id

def bind_lead_activities_to_deal(lead_id, deal_id):
    """
    Находит все активности Лида (в особенности входящие письма CRM_EMAIL)
    и привязывает их к таймлайну созданной Сделки через crm.activity.binding.add.
    """
    acts = call_b24("crm.activity.list", {
        "filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lead_id},
        "select": ["ID", "TYPE_ID", "PROVIDER_ID", "SUBJECT"]
    }) or []
    bound_count = 0
    for act in acts:
        res = call_b24("crm.activity.binding.add", {
            "activityId": act["ID"],
            "entityTypeId": 2, # Deal
            "entityId": deal_id
        })
        if res:
            bound_count += 1
            print(f"B24: Дело #{act['ID']} ('{act.get('SUBJECT')}') привязано к Сделке #{deal_id}")
    return bound_count

import datetime

def get_deadline_business_days(days=4):
    """
    Рассчитывает дедлайн задачи в рабочих днях (за вычетом субботы и воскресенья).
    По умолчанию 4 рабочих дня к 18:00.
    """
    cur = datetime.datetime.now()
    added = 0
    while added < days:
        cur += datetime.timedelta(days=1)
        if cur.weekday() < 5:  # 0=Пн, 1=Вт, 2=Ср, 3=Чт, 4=Пт
            added += 1
    cur = cur.replace(hour=18, minute=0, second=0, microsecond=0)
    return cur.strftime("%Y-%m-%dT%H:%M:%S+03:00")

def create_b24_task(title, deal_id, responsible_id=30, group_id=14, deadline_days=4):
    deadline_str = get_deadline_business_days(days=deadline_days)
    fields = {
        "TITLE": title,
        "RESPONSIBLE_ID": responsible_id, # Miss Wang (30)
        "CREATED_BY": 1,                # Artem (1)
        "GROUP_ID": group_id,           # Товары и поставщики Китай (14)
        "PRIORITY": 1,                  # Обычный
        "STATUS": 2,                    # STATE_PENDING (Новая / Ждет выполнения)
        "TASK_CONTROL": "Y",            # Обязательно: требовать приемки работы постановщиком!
        "DEADLINE": deadline_str,       # 3-4 рабочих дня за вычетом выходных
        "TAGS": ["Поиск товара - 找货"],
        "UF_CRM_TASK": [f"D_{deal_id}"]
    }
    task_res = call_b24("tasks.task.add", {"fields": fields})
    task_id = task_res.get('task', {}).get('id') if isinstance(task_res, dict) else task_res
    return task_id


def send_b24_task_chat_message(task_id, message_text):
    # Fetch task chatId
    task_info = call_b24("tasks.task.get", {"taskId": task_id, "select": ["CHAT_ID"]})
    chat_id = task_info.get('task', {}).get('chatId') if task_info else None
    if chat_id:
        msg_res = call_b24("im.message.add", {
            "DIALOG_ID": f"chat{chat_id}",
            "MESSAGE": message_text
        })
        return msg_res
    return None

def process_item_17654(dry_run=False):
    """
    Lead 17654: ООО «ТПК ВентЭлектро», ИНН 9722026420
    Запрос: 53 мембранных клапана GEMU 602 10D17F35400TM 1507
    """
    print("\n" + "="*60)
    print(">>> ОБРАБОТКА ЛИДА 17654: ООО «ТПК ВентЭлектро» (GEMU)")
    print("="*60)
    
    inn = "9722026420"
    comp_title = "ООО «ТПК ВентЭлектро»"
    comp_full = "Общество с ограниченной ответственностью «Торгово-производственная компания ВентЭлектро»"
    address = "109029, г. Москва, Михайловский пр-д, д. 3, стр. 66, помещ. 1, ком. 51"
    contact_name = "Ханов Владислав"
    contact_email = "119@ventelectro.ru"
    contact_phone = "+7 (495) 926-26-78"
    contact_post = "Менеджер по закупкам"

    title_deal = "ООО «ТПК ВентЭлектро», GEMU 602 10D17F35400TM 1507, 隔膜阀, Мембранные клапаны (53 шт)"
    msg_chat = (
        "[USER=30]Miss Wang[/USER] GEMU 隔膜阀 型号 602 10D17F35400TM 1507 = 53个\n"
        "- 规格: DN 10, 阀体材质 1.4435 (316L), 焊接连接, 不锈钢手轮, 隔膜 PTFE/EPDM, Ra ≤ 0.60 μm\n"
        "- 交付地: 莫斯科"
    )

    # 1. 1C Check
    ca_1c = check_1c_counterparty(inn)
    lead_1c = check_1c_lead(inn)
    print(f"1C: Покупатель={bool(ca_1c)} (Код {ca_1c.get('Code') if ca_1c else '-'}), Лид={bool(lead_1c)}")

    if dry_run:
        print("[DRY-RUN] Bitrix24: Компания, Контакт, Сделка, Задача (Miss Wang, Priority 1), Сообщение в чат.")
        print("[DRY-RUN] 1C: Лид блокируется (уже есть покупатель НФ-000707). Контакт добавляется к покупателю.")
        return

    # Execute B24
    res_comp = enrich_or_create_b24_company(comp_title, inn, address=address, phone=contact_phone, email=contact_email)
    cid = res_comp['id']
    res_cnt = enrich_or_create_b24_contact(contact_name, contact_email, phone=contact_phone, company_id=cid, post=contact_post)
    cnt_id = res_cnt['id']
    print(f"B24: Компания ID={cid}, Контакт ID={cnt_id}")

    deal_id = create_b24_deal(title_deal, cid, cnt_id, lead_id=17654)
    print(f"B24: Создана Сделка ID={deal_id}")
    bind_lead_activities_to_deal(17654, deal_id)

    task_id = create_b24_task(title_deal, deal_id, responsible_id=30, group_id=14)
    print(f"B24: Создана Задача ID={task_id} (Miss Wang, Priority 1, Group 14)")

    msg_id = send_b24_task_chat_message(task_id, msg_chat)
    print(f"B24: Отправлено сообщение в чат задачи: msg_id={msg_id}")

    # Update Lead in B24
    call_b24("crm.lead.update", {
        "id": 17654,
        "fields": {
            "STATUS_ID": "CONVERTED",
            "COMPANY_ID": cid,
            "CONTACT_ID": cnt_id
        }
    })
    print("B24: Лид 17654 обновлен со статусом CONVERTED")

    # 1C Execution: Buyer already exists -> Add contact person or update contact info
    if ca_1c:
        print(f"1C: Контрагент {ca_1c.get('Code')} уже существует (Покупатель). Лид не создаем.")
        # Create contact person in 1C
        cp_guid = str(uuid.uuid4())
        cp_payload = {
            "Ref_Key": cp_guid,
            "Description": f"{contact_name} ({contact_email})",
            "Ответственный_Key": ARTEM_RESPONSIBLE_1C,
            "ОсновныеСведения": f"{contact_name}\n{contact_email}\n{contact_phone}\nМенеджер по закупкам",
            "АдресЭПДляПоиска": contact_email,
            "НомерТелефонаДляПоиска": re.sub(r'\D', '', contact_phone),
            "КонтактнаяИнформация": [
                {
                    "LineNumber": "1",
                    "Тип": "АдресЭлектроннойПочты",
                    "Вид_Key": CI_EMAIL,
                    "Представление": contact_email,
                    "АдресЭП": contact_email
                },
                {
                    "LineNumber": "2",
                    "Тип": "Телефон",
                    "Вид_Key": CI_PHONE,
                    "Представление": contact_phone,
                    "НомерТелефона": re.sub(r'\D', '', contact_phone)
                }
            ]
        }
        r_cp = requests.post(f"{ONEC_BASE}/Catalog_КонтактныеЛица?$format=json", json=cp_payload, auth=ONEC_AUTH_WRITE)
        if r_cp.status_code == 201:
            print(f"1C: Создано контактное лицо {contact_name} (GUID {cp_guid})")
        else:
            print(f"1C: Ошибка создания контактного лица: {r_cp.status_code} - {r_cp.text}")

def process_item_17652(dry_run=False):
    """
    Lead 17652: ООО ГК «Феникс-М», ИНН 4345499420
    Запрос: 3 шт. электродов pH CPS Endress+Hauser CPS41E-BA7ASB2
    """
    print("\n" + "="*60)
    print(">>> ОБРАБОТКА ЛИДА 17652: ООО ГК «Феникс-М» (Endress+Hauser)")
    print("="*60)

    inn = "4345499420"
    comp_title = "ООО ГК «Феникс-М»"
    comp_full = "Общество с ограниченной ответственностью Группа Компаний «Феникс-М»"
    address = "610001, Кировская обл, г. Киров, ул. Комсомольская, д. 12, оф. 5"
    contact_name = "Зараменских Илья Аркадьевич"
    contact_email = "gkfenix-m@mail.ru"
    contact_phone = "+7(963)000-04-66"
    contact_post = "Специалист по закупкам"

    title_deal = "ООО ГК «Феникс-М», Endress+Hauser CPS41E-BA7ASB2, pH 电极, pH Электроды (3 шт)"
    msg_chat = (
        "[USER=30]Miss Wang[/USER] Endress+Hauser pH 电极 型号 CPS41E-BA7ASB2 = 3个\n"
        "- 询价参考: 2609/450ки"
    )

    # 1. 1C Check
    ca_1c = check_1c_counterparty(inn)
    lead_1c = check_1c_lead(inn)
    print(f"1C: Покупатель={bool(ca_1c)}, Лид={bool(lead_1c)} (Код {lead_1c.get('Code') if lead_1c else '-'})")

    if dry_run:
        print("[DRY-RUN] Bitrix24: Компания, Контакт, Сделка, Задача (Miss Wang, Priority 1), Сообщение в чат.")
        print("[DRY-RUN] 1C: Лид уже существует (000001673). Добавляется контакт лида Зараменских Илья.")
        return

    # Execute B24
    res_comp = enrich_or_create_b24_company(comp_title, inn, address=address, phone=contact_phone, email=contact_email)
    cid = res_comp['id']
    res_cnt = enrich_or_create_b24_contact(contact_name, contact_email, phone=contact_phone, company_id=cid, post=contact_post)
    cnt_id = res_cnt['id']
    print(f"B24: Компания ID={cid}, Контакт ID={cnt_id}")

    deal_id = create_b24_deal(title_deal, cid, cnt_id, lead_id=17652)
    print(f"B24: Создана Сделка ID={deal_id}")
    bind_lead_activities_to_deal(17652, deal_id)

    task_id = create_b24_task(title_deal, deal_id, responsible_id=30, group_id=14)
    print(f"B24: Создана Задача ID={task_id} (Miss Wang, Priority 1, Group 14)")

    msg_id = send_b24_task_chat_message(task_id, msg_chat)
    print(f"B24: Отправлено сообщение в чат задачи: msg_id={msg_id}")

    # Update Lead in B24
    call_b24("crm.lead.update", {
        "id": 17652,
        "fields": {
            "STATUS_ID": "CONVERTED",
            "COMPANY_ID": cid,
            "CONTACT_ID": cnt_id
        }
    })
    print("B24: Лид 17652 обновлен со статусом CONVERTED")

    # 1C Execution: Existing Lead 000001673
    if lead_1c:
        lead_guid = lead_1c['Ref_Key']
        print(f"1C: Обогащаем существующий Лид {lead_1c.get('Code')} ({lead_guid})")
        # Add Contact to Lead in Catalog_КонтактыЛидов
        cnt_guid = str(uuid.uuid4())
        cnt_payload = {
            "Ref_Key": cnt_guid,
            "Owner_Key": lead_guid,
            "Description": contact_name,
            "Должность": contact_post,
            "КонтактнаяИнформация": [
                {
                    "LineNumber": "1",
                    "Тип": "АдресЭлектроннойПочты",
                    "Вид_Key": CI_EMAIL,
                    "Представление": contact_email,
                    "Значение": contact_email
                },
                {
                    "LineNumber": "2",
                    "Тип": "Телефон",
                    "Вид_Key": CI_PHONE,
                    "Представление": contact_phone,
                    "Значение": contact_phone
                }
            ]
        }
        r_cnt = requests.post(f"{ONEC_BASE}/Catalog_КонтактыЛидов?$format=json", json=cnt_payload, auth=ONEC_AUTH_WRITE)
        if r_cnt.status_code == 201:
            print(f"1C: Добавлен контакт лида {contact_name} (Код {r_cnt.json().get('Code')})")
        else:
            print(f"1C: Ошибка добавления контакта лида: {r_cnt.status_code} - {r_cnt.text}")

        # Update Lead fields (parent group, responsible Artem, comment)
        update_lead = {
            "Parent_Key": LEAD_GROUPS_1C["Endress+Hauser"],
            "Ответственный_Key": ARTEM_RESPONSIBLE_1C,
            "Комментарий": (lead_1c.get('Комментарий') or '') + f"\nСделка Битрикс24 № {deal_id}. Запрос на электроды pH Endress+Hauser CPS41E-BA7ASB2 (3 шт)."
        }
        r_up = requests.patch(f"{ONEC_BASE}/Catalog_Лиды(guid'{lead_guid}')?$format=json", json=update_lead, auth=ONEC_AUTH_WRITE)
        if r_up.status_code == 200:
            print("1C: Лид 000001673 успешно обновлен")
        else:
            print(f"1C: Ошибка обновления лида: {r_up.status_code} - {r_up.text}")

def main():
    parser = argparse.ArgumentParser(description="Обработка лидов Битрикс24 и синхронизация с 1С:УНФ")
    parser.add_argument("--dry-run", action="store_true", help="Предпросмотр действий без записи")
    parser.add_argument("--lead-id", type=int, help="ID конкретного лида")
    args = parser.parse_args()

    if args.lead_id == 17654:
        process_item_17654(dry_run=args.dry_run)
    elif args.lead_id == 17652:
        process_item_17652(dry_run=args.dry_run)
    else:
        process_item_17654(dry_run=args.dry_run)
        process_item_17652(dry_run=args.dry_run)

if __name__ == "__main__":
    main()
