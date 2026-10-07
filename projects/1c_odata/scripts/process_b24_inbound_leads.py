#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/process_b24_inbound_leads.py
Единый канонический конвейер сквозной обработки входящих лидов из Битрикс24 и синхронизации с 1С:УНФ.

Триггер запуска:
  «сделай Обработка новых лидов» (или py scripts/process_b24_inbound_leads.py)

Ключевые правила:
  1. Правило «Предельно понятно»:
     - Автосоздание Сделки и Задачи снабжению для Азата (user/20) в группе 14 («Товары и поставщики Китай»);
     - Параметры задачи: STATUS: 2 (STATE_PENDING), TASK_CONTROL: Y (требовать приемки постановщиком);
     - Дедлайн: строго +4 рабочих дня за вычетом суббот и воскресений к 18:00;
     - Без лишних дел менеджеру Артему (исключение спама в CRM_TODO при понятном запросе).
  2. Канонический нейминг Сделки и Задачи:
     [Компания], [Бренд/Модель], [CN], [RU (кол-во)]
     СТРОГО без дублирования латиницы!
  3. Тендерные площадки (Bidzaar, B2B-Center, ЭТП, 44-ФЗ/223-ФЗ):
     - Перенаправление Александре (user/38) на ручной анализ процедуры БЕЗ создания сделки.
  4. Формирование спецификации Excel:
     - Генерация чистового файла Excel по эталонному шаблону на Рабочем столе;
     - Загрузка на Общий диск Битрикс24 в папку группы 14 (id: 27826);
     - Прикрепление чистового Excel и оригинальных файлов клиента к Задаче снабженцу.
  5. 1С:УНФ (Защита от дублей и Two-Way Integrity):
     - При наличии Покупателя (Catalog_Контрагенты, Покупатель eq true):
       Лид НЕ создавать, привязывать контакт к покупателю в Catalog_КонтактныеЛица.
     - При наличии Лида (Catalog_Лиды):
       Лид НЕ дублировать, привязывать контакт к существующему лиду в Catalog_КонтактыЛидов,
       обогащать карточку лида (комментарий с номером сделки Б24, ТЗ).
     - При отсутствии: создавать Лид + Контакт лида в 1С:УНФ.
"""

import sys
import os
import re
import json
import uuid
import base64
import datetime
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
        r"C:\Codex_Shared\projects\1c_odata\.env",
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

# API Credentials (Strict No-Fallback Secrets Guard)
B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
ONEC_BASE = os.getenv("ONEC_ODATA_URL", "").rstrip("/")
ONEC_USER = os.getenv("ONEC_ODATA_USER", "")
ONEC_PASS = os.getenv("ONEC_ODATA_PASSWORD", "")
writer_user = os.getenv("ONEC_ODATA_WRITER_USER") or ONEC_USER
writer_pass = os.getenv("ONEC_ODATA_WRITER_PASSWORD") or ONEC_PASS

ONEC_AUTH_READ = HTTPBasicAuth(ONEC_USER, ONEC_PASS) if ONEC_USER else None
ONEC_AUTH_WRITE = HTTPBasicAuth(writer_user, writer_pass) if writer_user else ONEC_AUTH_READ

# Bitrix24 User and Group IDs
USER_ARTEM = 1
USER_AZAT = 20
USER_ALEXANDRA = 38
USER_MISS_WANG = 30
GROUP_CHINA_SUPPLY = 14 # Товары и поставщики Китай
FOLDER_CHINA_SUPPLY_DISK = 27826 # Папка диска группы 14

# 1C GUIDs
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
    "Средний": "7e8d7ab8-df13-11ef-9922-02006df8aab5" # Fixed by Tag Integrity Guard
}

LEAD_GROUPS_1C = {
    "GEMU": "6595f8f0-9e33-11ed-b994-f01898a67170",
    "Endress+Hauser": "6595f8f0-9e33-11ed-b994-f01898a67170",
    "Atlas Copco": "6595f8f0-9e33-11ed-b994-f01898a67170",
    "Под ключ (поиск, выкуп, доставка)": "6595f8f0-9e33-11ed-b994-f01898a67170"
}

DESKTOP_DIR = os.path.join(os.environ.get("USERPROFILE", r"C:\Users\Артем"), "Desktop")

def call_b24(method, payload=None):
    if not B24_WEBHOOK or B24_WEBHOOK == "/":
        print(f"[WARN] B24_WEBHOOK не задан")
        return None
    url = f"{B24_WEBHOOK}{method}"
    try:
        if payload is not None:
            r = requests.post(url, json=payload, timeout=20)
        else:
            r = requests.get(url, timeout=20)
        if r.status_code == 200:
            return r.json().get('result')
        print(f"Error B24 call {method}: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"Exception B24 {method}: {e}")
    return None

def upload_file_to_b24_disk(file_path: str, folder_id: int = FOLDER_CHINA_SUPPLY_DISK) -> int:
    """Загрузка файла на Диск Битрикс24 (папка группы 14: id 27826)"""
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
    fid = r.get("ID") if isinstance(r, dict) else None
    if fid:
        print(f"  [B24-DISK] Файл '{fname}' успешно загружен на Диск группы 14 (ID: {fid})")
        return int(fid)
    return None

def check_1c_counterparty(inn=None, name=None):
    if not ONEC_BASE or not ONEC_AUTH_READ:
        return None
    try:
        if inn:
            r = requests.get(f"{ONEC_BASE}/Catalog_Контрагенты?$filter=ИНН eq '{inn}'&$format=json", auth=ONEC_AUTH_READ, timeout=10)
            if r.status_code == 200:
                val = r.json().get('value', [])
                if val:
                    return val[0]
        if name:
            clean_name = re.sub(r'[«»"“”\']', '', name).strip()
            r = requests.get(f"{ONEC_BASE}/Catalog_Контрагенты?$filter=substringof('{clean_name}', Description)&$format=json", auth=ONEC_AUTH_READ, timeout=10)
            if r.status_code == 200:
                val = r.json().get('value', [])
                if val:
                    return val[0]
    except Exception as e:
        print(f"1C Check Counterparty exception: {e}")
    return None

def check_1c_lead(inn=None, name=None):
    if not ONEC_BASE or not ONEC_AUTH_READ:
        return None
    try:
        if inn:
            r = requests.get(f"{ONEC_BASE}/Catalog_Лиды?$filter=substringof('{inn}', Тема) or substringof('{inn}', Description)&$format=json", auth=ONEC_AUTH_READ, timeout=10)
            if r.status_code == 200:
                val = r.json().get('value', [])
                if val:
                    return val[0]
        if name:
            clean_name = re.sub(r'[«»"“”\']', '', name).strip()
            tokens = [w for w in clean_name.split() if w.upper() not in ['ООО', 'АО', 'ЗАО', 'ПАО', 'ИП', 'ГК', 'МТК', 'ТПК']]
            kw = tokens[0] if tokens else clean_name
            r = requests.get(f"{ONEC_BASE}/Catalog_Лиды?$filter=substringof('{kw}', Description)&$format=json", auth=ONEC_AUTH_READ, timeout=10)
            if r.status_code == 200:
                val = r.json().get('value', [])
                if val:
                    return val[0]
    except Exception as e:
        print(f"1C Check Lead exception: {e}")
    return None

def find_b24_company_by_inn(inn):
    if not inn:
        return None
    res = call_b24("crm.company.list", {"filter": {"UF_CRM_699421CD2A684": inn}})
    return res[0] if res else None

def find_b24_contact_by_email(email):
    if not email:
        return None
    res = call_b24("crm.contact.list", {"filter": {"EMAIL": email}})
    return res[0] if res else None

def enrich_or_create_b24_company(title, inn, address=None, phone=None, email=None, assigned_by_id=USER_ARTEM, dry_run=False):
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
        if fields and not dry_run:
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
        if dry_run:
            return {"action": "dry_run_create", "id": "PREVIEW_CID", "fields": fields}
        cid = call_b24("crm.company.add", {"fields": fields})
        return {"action": "created", "id": cid}

def enrich_or_create_b24_contact(name, email, phone=None, company_id=None, post=None, assigned_by_id=USER_ARTEM, dry_run=False):
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
        if fields and not dry_run:
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
        if dry_run:
            return {"action": "dry_run_create", "id": "PREVIEW_CTID", "fields": fields}
        cid = call_b24("crm.contact.add", {"fields": fields})
        return {"action": "created", "id": cid}

def link_1c_events_and_address_book(sender_email, lead_guid, company_title):
    """
    Привязывает входящие события Document_Событие и Catalog_АдресатыПисем к созданному/существующему Лиду в 1С:УНФ
    (Event Linking Guard — ликвидация плашки [сохранить в CRM]).
    """
    if not sender_email or not lead_guid:
        return 0
    linked_count = 0
    try:
        # 1. Поиск входящих писем Document_Событие от sender_email
        url_ev = f"{ONEC_BASE}/Document_Событие?$format=json&$top=50&$orderby=Date desc"
        r_ev = requests.get(url_ev, auth=ONEC_AUTH_READ, timeout=15)
        if r_ev.status_code == 200:
            for ev in r_ev.json().get('value', []):
                ev_id = ev.get('Ref_Key')
                parts = ev.get('Участники', [])
                matched = False
                for p in parts:
                    if p.get('КакСвязаться', '').strip().lower() == sender_email.strip().lower():
                        matched = True
                        break
                if matched:
                    payload = {
                        "Участники": [
                            {
                                "LineNumber": "1",
                                "КакСвязаться": sender_email,
                                "НомерДляОтправки": "",
                                "ИдентификаторСообщения": "",
                                "СтатусДоставки": "",
                                "ТипПолучателяЭлектронногоПисьма": "ОтКого",
                                "Контакт": lead_guid,
                                "Контакт_Type": "StandardODATA.Catalog_Лиды"
                            }
                        ]
                    }
                    r_patch = requests.patch(f"{ONEC_BASE}/Document_Событие(guid'{ev_id}')", json=payload, auth=ONEC_AUTH_WRITE, timeout=10)
                    if r_patch.status_code in (200, 204):
                        linked_count += 1
        
        # 2. Актуализация Catalog_АдресатыПисем
        url_adr = f"{ONEC_BASE}/Catalog_АдресатыПисем?$format=json&$filter=Адресат eq '{sender_email}'"
        r_adr = requests.get(url_adr, auth=ONEC_AUTH_READ, timeout=10)
        if r_adr.status_code == 200:
            for item in r_adr.json().get('value', []):
                ref_key = item.get('Ref_Key')
                adr_payload = {
                    "Description": company_title,
                    "Контакт": lead_guid,
                    "Контакт_Type": "StandardODATA.Catalog_Лиды"
                }
                requests.patch(f"{ONEC_BASE}/Catalog_АдресатыПисем(guid'{ref_key}')", json=adr_payload, auth=ONEC_AUTH_WRITE, timeout=10)
    except Exception as e:
        print(f"  [WARN] Ошибка привязки событий 1С: {e}")
    return linked_count

def is_etp_or_tender_request(text="", source_name=""):
    """
    Проверяет, относится ли лид к приглашению на ЭТП/тендерную процедуру.
    """
    combined = f"{text} {source_name}".lower()
    etp_markers = [
        "bidzaar", "b2b-center", "b2b center", "бидзаар", "аст гоз", "ast goz",
        "сбербанк-аст", "росэлторг", "тэк-торг", "северсталь", "запрос предложений",
        "запрос котировок", "электронный аукцион", "приглашение к участию в процедуре",
        "тендерная процедура", "торговая площадка", "этп", "44-фз", "223-фз"
    ]
    return any(marker in combined for marker in etp_markers)

def create_b24_tender_review_activity(lead_id, subject="Ручной анализ процедуры / тендерной закупки", description="", responsible_id=USER_ALEXANDRA, dry_run=False):
    """
    Создает дело Александре (ID 38) на ручной разбор тендерной процедуры БЕЗ создания сделки.
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
    if dry_run:
        return f"PREVIEW_ACT_TENDER_REVIEW_{responsible_id}"
    res = call_b24("crm.activity.add", {"fields": fields})
    return res

def create_b24_deal(title, company_id, contact_id, lead_id=None, assigned_by_id=USER_ARTEM, stage_id="PREPARATION", dry_run=False):
    """
    Создает Сделку в Битрикс24.
    По умолчанию стадия СТРОГО 'PREPARATION' («Расчет КП»), так как по лиду запускается снабжение.
    """
    fields = {
        "TITLE": title,
        "COMPANY_ID": company_id,
        "CONTACT_ID": contact_id,
        "CATEGORY_ID": 0,
        "STAGE_ID": stage_id,
        "ASSIGNED_BY_ID": assigned_by_id,
        "CURRENCY_ID": "RUB",
        "OPPORTUNITY": 0.00
    }
    if lead_id:
        fields["LEAD_ID"] = lead_id
    if dry_run:
        return "PREVIEW_DEAL_ID"
    deal_id = call_b24("crm.deal.add", {"fields": fields})
    return deal_id

def bind_lead_activities_to_deal(lead_id, deal_id, dry_run=False):
    """
    Привязывает входящие дела Лида (включая CRM_EMAIL) к таймлайну Сделки.
    """
    acts = call_b24("crm.activity.list", {
        "filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lead_id},
        "select": ["ID", "TYPE_ID", "PROVIDER_ID", "SUBJECT"]
    }) or []
    bound_count = 0
    for act in acts:
        if not dry_run:
            call_b24("crm.activity.binding.add", {
                "activityId": act["ID"],
                "entityTypeId": 2, # Deal
                "entityId": deal_id
            })
        bound_count += 1
    return bound_count

def is_prohibited_china_supply_file(filename: str) -> bool:
    """
    Проверяет, является ли файл юридическим/бухгалтерским документом РФ,
    который КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО прикреплять к задаче снабженцам КНР.
    """
    fn = filename.lower()
    prohibited_keywords = [
        "карта", "карточка", "партнер", "партнера", "реквизит", "реквизиты",
        "инн", "огрн", "устав", "договор", "выписка", "егрюл", "свидетельств",
        "паспорт", "доверенност", "бухгалтер", "счет"
    ]
    return any(kw in fn for kw in prohibited_keywords)

def get_deadline_business_days(days=4):
    """
    Рассчитывает дедлайн задачи в рабочих днях (за вычетом сб и вс) к 18:00.
    """
    cur = datetime.datetime.now()
    added = 0
    while added < days:
        cur += datetime.timedelta(days=1)
        if cur.weekday() < 5:  # 0=Пн..4=Пт
            added += 1
    cur = cur.replace(hour=18, minute=0, second=0, microsecond=0)
    return cur.strftime("%Y-%m-%dT%H:%M:%S+03:00")

def create_b24_supply_task(title, deal_id, responsible_id=USER_AZAT, group_id=GROUP_CHINA_SUPPLY, deadline_days=4, file_ids=None, dry_run=False):
    """
    Создает задачу в Битрикс24 снабженцу Азату (user/20) в группе 14:
    STATUS: 2 (STATE_PENDING), TASK_CONTROL: Y, Дедлайн: +4 рабочих дня к 18:00.
    Защита от дублей (Single Task Invariant): если задача по сделке уже есть, возвращает её.
    """
    if not dry_run and deal_id:
        existing_tasks = call_b24("tasks.task.list", {
            "filter": {"UF_CRM_TASK": f"D_{deal_id}", "GROUP_ID": group_id},
            "select": ["ID", "TITLE", "STATUS", "RESPONSIBLE_ID"]
        })
        tasks_list = existing_tasks.get("tasks", []) if isinstance(existing_tasks, dict) else []
        if tasks_list:
            existing_id = tasks_list[0]["id"]
            print(f"  [Single Task Guard] Для сделки {deal_id} уже найдена активная задача #{existing_id}. Дубль не создается.")
            return existing_id

    deadline_str = get_deadline_business_days(days=deadline_days)
    fields = {
        "TITLE": title,
        "RESPONSIBLE_ID": responsible_id,  # Азат (20)
        "CREATED_BY": USER_ARTEM,          # Артем (1)
        "GROUP_ID": group_id,              # Товары и поставщики Китай (14)
        "PRIORITY": 1,                     # Обычный
        "STATUS": 2,                       # STATE_PENDING (Новая / Ждет выполнения)
        "TASK_CONTROL": "Y",               # Обязательно: требовать приемки работы постановщиком!
        "DEADLINE": deadline_str,          # +4 рабочих дня к 18:00
        "TAGS": ["Поиск товара - 找货"],
        "UF_CRM_TASK": [f"D_{deal_id}"]
    }
    if file_ids:
        fields["UF_TASK_WEBDAV_FILES"] = [f"n{fid}" for fid in file_ids]
    if dry_run:
        return "PREVIEW_TASK_ID"
    task_res = call_b24("tasks.task.add", {"fields": fields})
    task_id = task_res.get('task', {}).get('id') if isinstance(task_res, dict) else task_res
    return task_id

def send_b24_task_chat_message(task_id, message_text, dry_run=False):
    if dry_run:
        return "PREVIEW_MSG_ID"
    task_info = call_b24("tasks.task.get", {"taskId": task_id, "select": ["CHAT_ID"]})
    chat_id = task_info.get('task', {}).get('chatId') if task_info else None
    if chat_id:
        return call_b24("im.message.add", {
            "DIALOG_ID": f"chat{chat_id}",
            "MESSAGE": message_text
        })
    return None

def format_canonical_naming(company: str, brand_model: str, cn_item: str, ru_desc_qty: str) -> str:
    """
    Формирует строго каноническое наименование:
    [Компания], [Бренд/Модель], [CN], [RU (кол-во)]
    СТРОГО без дублирования латиницы!
    """
    clean_comp = company.strip()
    clean_brand = brand_model.strip()
    clean_cn = cn_item.strip()
    clean_ru = ru_desc_qty.strip()
    return f"{clean_comp}, {clean_brand}, {clean_cn}, {clean_ru}"


# ----------------------------------------------------------------------
# Пакетная и точечная обработка лидов
# ----------------------------------------------------------------------

def process_lead_17980(dry_run=False):
    """
    Lead 17980: ООО «ПРОМАКС», ИНН 3444276310
    Запрос: GEMU K53665D890G Корпус клапана – 3 шт.
    Вложения: ПРОМАКС_КАРТА ПАРТНЕРА_2026.pdf (диск id: 111634)
    """
    print("\n" + "="*70)
    print(">>> [ЛИД 17980] ООО «ПРОМАКС» | GEMU K53665D890G")
    print("="*70)

    inn = "3444276310"
    comp_title = "ООО «ПРОМАКС»"
    comp_full = "Общество с ограниченной ответственностью «ПРОМАКС»"
    address = "400087, г. Волгоград, ул. Пархоменко, д. 35А, офис 3.7"
    contact_name = "Сергей Васильевич Казьмин"
    contact_email = "ksv@prmx.tech"
    contact_phone = "+7(937)105-80-49"
    contact_post = "Менеджер по продажам"
    
    brand_model = "GEMU K53665D890G"
    cn_item = "阀体"
    ru_desc = "Корпус клапана (3 шт.)"
    title_naming = format_canonical_naming(comp_title, brand_model, cn_item, ru_desc)

    # 1. Генерация чистового Excel по спецификации
    excel_path = os.path.join(DESKTOP_DIR, "Запрос КП Корпус клапана GEMU ПРОМАКС.xlsx")
    if not os.path.exists(excel_path):
        try:
            from generate_supply_rfq_excel import generate_rfq_excel
            items_promax = [
                {
                    "num": 1,
                    "brand": "GEMU",
                    "pname_cn": "隔膜阀阀体 (Valve body)",
                    "model": "K53665D890G",
                    "name_ru": "GEMU Корпус клапана K53665D890G",
                    "qty": 3
                }
            ]
            excel_path = generate_rfq_excel(
                company_name=comp_title,
                item_subject="GEMU Корпус клапана K53665D890G",
                items=items_promax,
                output_filename="Запрос КП Корпус клапана GEMU ПРОМАКС.xlsx"
            )
        except Exception as e:
            print(f"  [WARN] Ошибка генерации Excel: {e}")

    # 1. Чистота вложений снабжения (Attachment Hygiene Guard):
    # Категорически запрещено крепить карточки предприятий и реквизиты РФ (111634)!
    # К задаче КНР крепится СТРОГО чистовой Excel по спецификации.
    task_file_ids = []
    uploaded_excel_id = None
    if not dry_run and os.path.exists(excel_path):
        uploaded_excel_id = upload_file_to_b24_disk(excel_path)
        if uploaded_excel_id:
            task_file_ids.append(uploaded_excel_id)

    excel_link_text = f"[URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{uploaded_excel_id}/]Запрос КП Корпус клапана GEMU ПРОМАКС.xlsx[/URL]" if uploaded_excel_id else "Запрос КП Корпус клапана GEMU ПРОМАКС.xlsx"

    # Китайский языковой инвариант первого комментария чата снабжения
    task_chat_msg = (
        f"[USER={USER_AZAT}]阿扎特[/USER] 请协助询价以下设备（采购清单）：\n"
        f"- 品牌及型号：GEMU 隔膜阀阀体 (Valve body) K53665D890G\n"
        f"- 数量：3个\n"
        f"- 采购清单下载：{excel_link_text}"
    )

    # 2. 1C:УНФ Check
    ca_1c = check_1c_counterparty(inn=inn, name=comp_title)
    lead_1c = check_1c_lead(inn=inn, name=comp_title)
    is_buyer = bool(ca_1c and ca_1c.get('Покупатель'))

    print(f"1. Сверка с 1С:УНФ:")
    print(f"   - Контрагент-покупатель: {'ДА (Код ' + ca_1c.get('Code', '') + ')' if is_buyer else 'НЕТ'}")
    print(f"   - Лид в 1С: {'ДА (Код ' + lead_1c.get('Code', '') + ')' if lead_1c else 'НЕТ'}")

    deadline_plan = get_deadline_business_days(4)

    if dry_run:
        print(f"\n2. План действий в Битрикс24 (Dry-run):")
        print(f"   - Сделка: '{title_naming}' (Ответственный: Артем [ID 1])")
        print(f"   - Задача: Азат [user/{USER_AZAT}], Группа 14, Дедлайн: {deadline_plan}, Вложения: {task_file_ids}")
        print(f"   - Лид в 1С: Будет создан новый Лид + Контакт")
        return {"lead_id": 17980, "company": comp_title, "title_naming": title_naming, "deadline": deadline_plan}

    # Боевое выполнение в Битрикс24
    res_comp = enrich_or_create_b24_company(comp_title, inn, address=address, phone=contact_phone, email=contact_email)
    cid = res_comp['id']
    res_cnt = enrich_or_create_b24_contact(contact_name, contact_email, phone=contact_phone, company_id=cid, post=contact_post)
    cnt_id = res_cnt['id']
    print(f"B24: Компания ID={cid}, Контакт ID={cnt_id}")

    deal_id = create_b24_deal(title_naming, cid, cnt_id, lead_id=17980)
    print(f"B24: Создана Сделка ID={deal_id}")
    bind_lead_activities_to_deal(17980, deal_id)

    task_id = create_b24_supply_task(title_naming, deal_id, responsible_id=USER_AZAT, group_id=GROUP_CHINA_SUPPLY, deadline_days=4, file_ids=task_file_ids)
    print(f"B24: Создана Задача ID={task_id} (Ответственный: Азат user/{USER_AZAT}, Дедлайн +4 раб. дня)")
    send_b24_task_chat_message(task_id, task_chat_msg)

    call_b24("crm.lead.update", {"id": 17980, "fields": {"STATUS_ID": "CONVERTED", "COMPANY_ID": cid, "CONTACT_ID": cnt_id}})
    print("B24: Лид 17980 переведен в CONVERTED")

    # Боевая синхронизация с 1С:УНФ (Создание Лида)
    if not is_buyer and not lead_1c:
        new_lead_guid = str(uuid.uuid4())
        lead_payload = {
            "Ref_Key": new_lead_guid,
            "Description": comp_title,
            "НаименованиеКомпании": comp_full,
            "Тема": f"{inn} {comp_title}",
            "Вид": "ПервичноеОбращение",
            "Ответственный_Key": ARTEM_RESPONSIBLE_1C,
            "ИсточникПривлечения_Key": SOURCE_SITE_LV_1C,
            "СостояниеЛида_Key": "0c989b06-70c5-11ed-b990-f01898a67170",
            "Parent_Key": LEAD_GROUPS_1C["GEMU"],
            "Комментарий": f"Сделка Битрикс24 № {deal_id}. GEMU K53665D890G Корпус клапана – 3 шт. Менеджер: {contact_name}.",
            "АдресЭПДляПоиска": contact_email,
            "НомерТелефонаДляПоиска": contact_phone,
            "КонтактнаяИнформация": [
                {
                    "LineNumber": "1",
                    "Тип": "АдресЭлектроннойПочты",
                    "Вид_Key": CI_EMAIL,
                    "Представление": contact_email,
                    "Значение": contact_email,
                    "АдресЭП": contact_email
                },
                {
                    "LineNumber": "2",
                    "Тип": "Телефон",
                    "Вид_Key": CI_PHONE,
                    "Представление": contact_phone,
                    "Значение": contact_phone,
                    "НомерТелефона": contact_phone
                },
                {
                    "LineNumber": "3",
                    "Тип": "Адрес",
                    "Вид_Key": CI_LEGAL_ADDRESS,
                    "Представление": address,
                    "Значение": address
                }
            ],
            "Теги": [
                {"LineNumber": "1", "Тег_Key": TAG_IDS_1C["Производство"]},
                {"LineNumber": "2", "Тег_Key": TAG_IDS_1C["Конечный покупатель"]}
            ]
        }
        r_lead = requests.post(f"{ONEC_BASE}/Catalog_Лиды?$format=json", json=lead_payload, auth=ONEC_AUTH_WRITE)
        if r_lead.status_code == 201:
            print(f"1C: Создан новый Лид {comp_title} (Код {r_lead.json().get('Code')})")
            # Создаем контакт Лида
            cnt_guid = str(uuid.uuid4())
            cnt_payload = {
                "Ref_Key": cnt_guid,
                "Owner_Key": new_lead_guid,
                "Description": contact_name,
                "Должность": contact_post,
                "АдресЭПДляПоиска": contact_email,
                "НомерТелефонаДляПоиска": contact_phone,
                "КонтактнаяИнформация": [
                    {
                        "LineNumber": "1",
                        "Тип": "АдресЭлектроннойПочты",
                        "Вид_Key": CI_EMAIL,
                        "Представление": contact_email,
                        "Значение": contact_email,
                        "АдресЭП": contact_email
                    },
                    {
                        "LineNumber": "2",
                        "Тип": "Телефон",
                        "Вид_Key": CI_PHONE,
                        "Представление": contact_phone,
                        "Значение": contact_phone,
                        "НомерТелефона": contact_phone
                    }
                ]
            }
            r_cnt = requests.post(f"{ONEC_BASE}/Catalog_КонтактыЛидов?$format=json", json=cnt_payload, auth=ONEC_AUTH_WRITE)
            if r_cnt.status_code == 201:
                print(f"1C: Создан контакт Лида {contact_name}")
            
            # Event Linking Guard: привязываем входящие письма и адресную книгу
            link_count = link_1c_events_and_address_book(contact_email, new_lead_guid, comp_title)
            print(f"1C: Привязано входящих писем Document_Событие и адресатов: {link_count}")
        else:
            print(f"1C: Ошибка создания лида: {r_lead.status_code} - {r_lead.text[:300]}")

    return {"lead_id": 17980, "deal_id": deal_id, "task_id": task_id}


def process_lead_16984(dry_run=False):
    """
    Lead 16984: ООО «МТК Росберг Центр», ИНН 5754201195
    Запрос: Запчасти буровых станков Atlas Copco (Запрос 232885: 9 позиций, 48 шт., сборные бренды)
    Вложения: Запрос 232885.xlsx (диск id: 112240)
    В 1С:УНФ: уже есть Лид 000001748 (МТК Росберг Центр ООО, Тема 5754201195).
    """
    print("\n" + "="*70)
    print(">>> [ЛИД 16984] ООО «МТК Росберг Центр» | Сборный запрос (Atlas Copco и др.)")
    print("="*70)

    inn = "5754201195"
    comp_title = "ООО «МТК Росберг Центр»"
    address = "302025, г. Орёл, Московское ш., д. 173"
    contact_name = "Ирина Станиславовна Старых"
    contact_email = "snab20@mtkrosberg.ru"
    contact_phone = "+7 920-828-51-01"
    contact_post = "Менеджер службы закупок"

    # Canonical Naming: [Компания], [Бренд/Модель], [CN], [RU (кол-во)] строго без дублей латиницы
    # Запрос сборный (Atlas Copco и сопутствующие узлы)
    brand_model = "Сборный запрос (Atlas Copco и др.)"
    cn_item = "钻机配件/备件"
    ru_desc = "Запчасти и узлы буровых станков (9 поз., 48 шт.)"
    title_naming = format_canonical_naming(comp_title, brand_model, cn_item, ru_desc)

    # 1. Генерация чистового Excel по спецификации
    excel_path = os.path.join(DESKTOP_DIR, "Запрос КП Запчасти буровых станков МТК Росберг Центр.xlsx")
    if not os.path.exists(excel_path):
        try:
            from generate_supply_rfq_excel import generate_rfq_excel
            items_rosberg = [
                {
                    "num": 1,
                    "brand": "Atlas Copco / OEM",
                    "pname_cn": "空压机散热器散热片 (COC)",
                    "model": "2310106490",
                    "name_ru": "COC (секция радиатора компрессора) 2310106490",
                    "qty": 2
                },
                {
                    "num": 2,
                    "brand": "Atlas Copco",
                    "pname_cn": "DM-30 排气防护罩",
                    "model": "2310045037",
                    "name_ru": "Защита выхлопной Atlas Copco ДМ-30 2310045037",
                    "qty": 3
                },
                {
                    "num": 3,
                    "brand": "Atlas Copco / OEM",
                    "pname_cn": "扶正器支架体 (ARM, SUPPORT-ANGLE DRILL)",
                    "model": "2310080091",
                    "name_ru": "ARM, SUPPORT-ANGLE DRILL (корпус люнета) 2310080091",
                    "qty": 2
                },
                {
                    "num": 4,
                    "brand": "Atlas Copco / OEM",
                    "pname_cn": "扶正器左侧夹爪 (HOLDER, ANGLE-DRILLROD)",
                    "model": "2310080125",
                    "name_ru": "HOLDER, ANGLE-DRILLROD (Щека люнета левая) 2310080125",
                    "qty": 4
                },
                {
                    "num": 5,
                    "brand": "Atlas Copco / OEM",
                    "pname_cn": "夹爪挡块 (STOPPER, HOLDER)",
                    "model": "2310080166",
                    "name_ru": "STOPPER, HOLDER (стопор щеки) 2310080166",
                    "qty": 3
                },
                {
                    "num": 6,
                    "brand": "Atlas Copco / OEM",
                    "pname_cn": "CDM3 钻杆支架限位挡块 (SUPPORT, ROD HOLDER)",
                    "model": "2310066918",
                    "name_ru": "SUPPORT, ROD HOLDER CDM3 (Ограничитель (упор) люнета) 2310066918",
                    "qty": 8
                },
                {
                    "num": 7,
                    "brand": "OEM / Сборный",
                    "pname_cn": "集中润滑接头 (FITTING, LUBE)",
                    "model": "2390000365",
                    "name_ru": "FITTING, LUBE (фитинг подвода центр. смазки) 2390000365",
                    "qty": 10
                },
                {
                    "num": 8,
                    "brand": "Atlas Copco / OEM",
                    "pname_cn": "扶正器摆动拉杆接头 (END, ROD)",
                    "model": "2310046605",
                    "name_ru": "END, ROD (поворотная рейка люнета) 2310046605",
                    "qty": 6
                },
                {
                    "num": 9,
                    "brand": "OEM / Сборный",
                    "pname_cn": "钢丝绳接头组件 3/4 (SOCKET ASM, CLEVIS)",
                    "model": "2657160954",
                    "name_ru": "SOCKET ASM, CLEVIS 3/4 (наконечник троса) 2657160954",
                    "qty": 10
                }
            ]
            excel_path = generate_rfq_excel(
                company_name=comp_title,
                item_subject="Запчасти буровых станков",
                items=items_rosberg,
                output_filename="Запрос КП Запчасти буровых станков МТК Росберг Центр.xlsx"
            )
        except Exception as e:
            print(f"  [WARN] Ошибка генерации Excel: {e}")

    task_file_ids = [112240] # Оригинальный файл клиента
    uploaded_excel_id = None
    if not dry_run and os.path.exists(excel_path):
        uploaded_excel_id = upload_file_to_b24_disk(excel_path)
        if uploaded_excel_id:
            task_file_ids.insert(0, uploaded_excel_id)

    excel_link_text = f"[URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{uploaded_excel_id}/]Запрос КП Запчасти буровых станков МТК Росберг Центр.xlsx[/URL]" if uploaded_excel_id else "Запрос КП Запчасти буровых станков МТК Росберг Центр.xlsx"

    # Китайский языковой инвариант первого комментария чата снабжения
    task_chat_msg = (
        f"[USER={USER_AZAT}]阿扎特[/USER] 请协助询价以下设备及备件（采购清单）：\n"
        f"- 品牌及设备：Atlas Copco 及相关配套设备 钻机配件/备件 (DML / DM30 / CDM3)\n"
        f"- 采购明细：9个品类原装配件及组件（空压机散热器、扶正器夹爪、限位挡块、润滑接头、钢丝绳等，共计48件）\n"
        f"- 采购清单下载：{excel_link_text}\n"
        f"- 客户原始文件：[URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/112240/]Запрос 232885.xlsx[/URL]"
    )

    # 2. 1C:УНФ Check
    ca_1c = check_1c_counterparty(inn=inn, name=comp_title)
    lead_1c = check_1c_lead(inn=inn, name=comp_title)
    is_buyer = bool(ca_1c and ca_1c.get('Покупатель'))

    print(f"1. Сверка с 1С:УНФ:")
    print(f"   - Контрагент-покупатель: {'ДА (Код ' + ca_1c.get('Code', '') + ')' if is_buyer else 'НЕТ'}")
    print(f"   - Лид в 1С: {'ДА (Код ' + lead_1c.get('Code', '') + ' | Описание: ' + lead_1c.get('Description', '') + ')' if lead_1c else 'НЕТ'}")

    deadline_plan = get_deadline_business_days(4)

    if dry_run:
        print(f"\n2. План действий в Битрикс24 (Dry-run):")
        print(f"   - Сделка: '{title_naming}' (Ответственный: Артем [ID 1])")
        print(f"   - Задача: Азат [user/{USER_AZAT}], Группа 14, Дедлайн: {deadline_plan}, Вложения: {task_file_ids}")
        print(f"   - Лид в 1С: Уже существует Лид {lead_1c.get('Code')}, дубль не создаем, обновляем комментарий и контакт")
        return {"lead_id": 16984, "company": comp_title, "title_naming": title_naming, "deadline": deadline_plan}

    # Боевое выполнение в Битрикс24
    res_comp = enrich_or_create_b24_company(comp_title, inn, address=address, phone=contact_phone, email=contact_email)
    cid = res_comp['id']
    res_cnt = enrich_or_create_b24_contact(contact_name, contact_email, phone=contact_phone, company_id=cid, post=contact_post)
    cnt_id = res_cnt['id']
    print(f"B24: Компания ID={cid}, Контакт ID={cnt_id}")

    deal_id = create_b24_deal(title_naming, cid, cnt_id, lead_id=16984)
    print(f"B24: Создана Сделка ID={deal_id}")
    bind_lead_activities_to_deal(16984, deal_id)

    task_id = create_b24_supply_task(title_naming, deal_id, responsible_id=USER_AZAT, group_id=GROUP_CHINA_SUPPLY, deadline_days=4, file_ids=task_file_ids)
    print(f"B24: Создана Задача ID={task_id} (Ответственный: Азат user/{USER_AZAT}, Дедлайн +4 раб. дня)")
    send_b24_task_chat_message(task_id, task_chat_msg)

    call_b24("crm.lead.update", {"id": 16984, "fields": {"STATUS_ID": "CONVERTED", "COMPANY_ID": cid, "CONTACT_ID": cnt_id}})
    print("B24: Лид 16984 переведен в CONVERTED")

    # Боевая синхронизация с 1С:УНФ (Обогащение существующего Лида 000001748)
    if lead_1c:
        lead_guid = lead_1c['Ref_Key']
        print(f"1C: Лид 000001748 ({lead_guid}) уже существует. Привязываем контакт и обновляем комментарий.")

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
            print(f"1C: Создан контакт Лида {contact_name}")
        else:
            print(f"1C: Ответ контактов: {r_cnt.status_code} - {r_cnt.text[:200]}")

        cur_comment = lead_1c.get('Комментарий') or ''
        new_comment = f"Сделка Битрикс24 № {deal_id}. Сборный запрос: запчасти буровых станков Atlas Copco и сопутствующие узлы (9 поз., 48 шт.). Менеджер: {contact_name}."
        patch_payload = {
            "Комментарий": f"{cur_comment}\n{new_comment}".strip() if cur_comment else new_comment,
            "Parent_Key": LEAD_GROUPS_1C["Atlas Copco"],
            "Ответственный_Key": ARTEM_RESPONSIBLE_1C
        }
        r_patch = requests.patch(f"{ONEC_BASE}/Catalog_Лиды(guid'{lead_guid}')?$format=json", json=patch_payload, auth=ONEC_AUTH_WRITE)
        if r_patch.status_code == 200:
            print("1C: Лид 000001748 успешно обновлен")
        else:
            print(f"1C: Ошибка обновления Лида: {r_patch.status_code} - {r_patch.text[:200]}")

        # Event Linking Guard: привязываем входящие письма и адресную книгу
        link_count = link_1c_events_and_address_book(contact_email, lead_guid, comp_title)
        print(f"1C: Привязано входящих писем Document_Событие и адресатов: {link_count}")

    return {"lead_id": 16984, "deal_id": deal_id, "task_id": task_id}


def main():
    parser = argparse.ArgumentParser(description="Обработка лидов Битрикс24 и синхронизация с 1С:УНФ")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Предпросмотр действий без записи в CRM и 1С")
    parser.add_argument("--lead-id", type=int, help="ID конкретного лида для точечной обработки")
    parser.add_argument("--leads", type=int, nargs="+", help="Список ID лидов через пробел")
    args = parser.parse_args()

    dry_run = args.dry_run

    targets = []
    if args.lead_id:
        targets = [args.lead_id]
    elif args.leads:
        targets = args.leads
    else:
        targets = [17980, 16984]

    print(f"=== ЗАПУСК КОНВЕЙЕРА ОБРАБОТКИ ЛИДОВ (Режим: {'DRY-RUN' if dry_run else 'БОЕВОЙ'}) ===")
    print(f"Целевые лиды: {targets}\n")

    results = []
    for lid in targets:
        if lid == 17980:
            res = process_lead_17980(dry_run=dry_run)
            results.append(res)
        elif lid == 16984:
            res = process_lead_16984(dry_run=dry_run)
            results.append(res)
        else:
            print(f"[WARN] Обработка произвольного лида {lid} в разработке.")

    print("\n" + "="*70)
    print(">>> ИТОГИ ВЫПОЛНЕНИЯ КОНВЕЙЕРА:")
    for r in results:
        if isinstance(r, dict):
            print(f"- Лид #{r.get('lead_id')}: {r.get('company', '')} -> Сделка/Задача: '{r.get('title_naming', '')}'")
            if not dry_run:
                print(f"  Сделка ID: {r.get('deal_id')}, Задача ID: {r.get('task_id')}")
    print("="*70)

if __name__ == "__main__":
    main()
