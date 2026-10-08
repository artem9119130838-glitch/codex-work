#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/process_b24_inbound_leads.py
Единый канонический конвейер сквозной обработки входящих лидов CRM Битрикс24,
квалификации обращений, постановки задач снабжению КНР и синхронизации с 1С:УНФ.

Архитектурный статус: Канонический единственный скрипт процесса (Canonical Single-Script Invariant).
Связанные регламенты: LEAD_PROCESSING_POLICY.md, ERP_1C_POLICY.md, AGENTS.md.

Быстрые триггеры вызова:
  «обработай лидов [ящик/лид] [ответственный]»
  «сделай Обработка новых лидов»
"""

import sys
import os
import re
import json
import uuid
import base64
import smtplib
import datetime
import argparse
import urllib.request
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from html import unescape
import requests
from requests.auth import HTTPBasicAuth

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ----------------------------------------------------------------------
# Загрузка переменных окружения (Strict No-Fallback Secrets Guard)
# ----------------------------------------------------------------------
def load_dotenv():
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
        r"C:\Codex\projects\1c_odata\.env",
        r"C:\Codex_Shared\projects\1c_odata\.env",
        r"C:\Codex\ARCHIVE\codex_shared_archive\n8n_email_ai_backup\.env",
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
ONEC_BASE = os.getenv("ONEC_ODATA_URL", "").rstrip("/")
ONEC_USER = os.getenv("ONEC_ODATA_USER", "")
ONEC_PASS = os.getenv("ONEC_ODATA_PASSWORD", "")
writer_user = os.getenv("ONEC_ODATA_WRITER_USER") or ONEC_USER
writer_pass = os.getenv("ONEC_ODATA_WRITER_PASSWORD") or ONEC_PASS

ONEC_AUTH_READ = HTTPBasicAuth(ONEC_USER, ONEC_PASS) if ONEC_USER else None
ONEC_AUTH_WRITE = HTTPBasicAuth(writer_user, writer_pass) if writer_user else ONEC_AUTH_READ

# Почтовые учетные записи SMTP
SMTP_HOST = os.getenv("SMTP_HOST", "mail.longwang.ru")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SALES_EMAIL_USER = os.getenv("SALES_EMAIL_USER", "sales@longwang.ru")
SALES_EMAIL_PASS = os.getenv("SALES_EMAIL_PASSWORD", "")

# Bitrix24 User and Group IDs
USER_ARTEM = 1
USER_AZAT = 20
USER_MISS_WANG = 30
USER_ALEXANDRA = 38
USER_SALMAN = 40
GROUP_CHINA_SUPPLY = 14       # Проект «Товары и поставщики Китай»
FOLDER_CHINA_SUPPLY_DISK = 27826 # Корневая папка Диска группы 14

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
    "Средний": "7e8d7ab8-df13-11ef-9922-02006df8aab5"
}
TAG_MAP_1C = TAG_IDS_1C

DESKTOP_DIR = os.path.join(os.environ.get("USERPROFILE", r"C:\Users\Артем"), "Desktop")

# ----------------------------------------------------------------------
# Битрикс24 REST API Client
# ----------------------------------------------------------------------
def call_b24(method: str, payload: dict = None) -> any:
    if not B24_WEBHOOK or B24_WEBHOOK == "/":
        print(f"[WARN] B24_WEBHOOK не задан")
        return None
    url = f"{B24_WEBHOOK}{method}"
    try:
        if payload is not None:
            r = requests.post(url, json=payload, timeout=25)
        else:
            r = requests.get(url, timeout=25)
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

# ----------------------------------------------------------------------
# 1С:УНФ OData Helpers
# ----------------------------------------------------------------------
def check_1c_counterparty(inn=None, name=None):
    if not ONEC_BASE or not ONEC_AUTH_READ:
        return None
    try:
        if inn:
            q = urllib.parse.quote(f"ИНН eq '{inn}'")
            r = requests.get(f"{ONEC_BASE}/Catalog_Контрагенты?$filter={q}&$format=json", auth=ONEC_AUTH_READ, timeout=10)
            if r.status_code == 200:
                val = r.json().get('value', [])
                if val:
                    return val[0]
            return None
        if name:
            clean_name = re.sub(r'[«»"“”\']', '', name).strip()
            q = urllib.parse.quote(f"substringof('{clean_name}', Description)")
            r = requests.get(f"{ONEC_BASE}/Catalog_Контрагенты?$filter={q}&$format=json", auth=ONEC_AUTH_READ, timeout=10)
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
            q = urllib.parse.quote(f"substringof('{inn}', Тема) or substringof('{inn}', Description)")
            r = requests.get(f"{ONEC_BASE}/Catalog_Лиды?$filter={q}&$format=json", auth=ONEC_AUTH_READ, timeout=10)
            if r.status_code == 200:
                val = r.json().get('value', [])
                if val:
                    return val[0]
            return None
        if name:
            clean_name = re.sub(r'[«»"“”\']', '', name).strip()
            tokens = [w for w in clean_name.split() if w.upper() not in ['ООО', 'АО', 'ЗАО', 'ПАО', 'ИП', 'ГК', 'МТК', 'ТПК', 'НПО', 'НПП']]
            if tokens and len(tokens[0]) >= 4:
                kw = tokens[0]
                q = urllib.parse.quote(f"substringof('{kw}', Description)")
                r = requests.get(f"{ONEC_BASE}/Catalog_Лиды?$filter={q}&$format=json", auth=ONEC_AUTH_READ, timeout=10)
                if r.status_code == 200:
                    val = r.json().get('value', [])
                    if val:
                        return val[0]
    except Exception as e:
        print(f"1C Check Lead exception: {e}")
    return None

def link_1c_events_and_address_book(sender_email, lead_guid, company_title):
    """
    Привязывает входящие события Document_Событие и Catalog_АдресатыПисем к созданному/существующему Лиду в 1С:УНФ
    (Event Linking Guard — ликвидация плашки [сохранить в CRM]).
    """
    if not sender_email or not lead_guid or not ONEC_BASE:
        return 0
    linked_count = 0
    try:
        url_ev = f"{ONEC_BASE}/Document_Событие?$format=json&$top=50&$orderby=Date desc"
        r_ev = requests.get(url_ev, auth=ONEC_AUTH_READ, timeout=15)
        if r_ev.status_code == 200:
            for ev in r_ev.json().get('value', []):
                ev_id = ev.get('Ref_Key')
                parts = ev.get('Участники', [])
                matched = any(p.get('КакСвязаться', '').strip().lower() == sender_email.strip().lower() for p in parts)
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

# ----------------------------------------------------------------------
# Мульти-ключевой каскадный поиск сущностей (Multi-Key Cascade Lookup)
# ----------------------------------------------------------------------
def find_b24_contact_by_email(email: str) -> dict:
    if not email:
        return None
    res = call_b24("crm.contact.list", {
        "filter": {"EMAIL": email.strip()},
        "select": ["ID", "NAME", "LAST_NAME", "SECOND_NAME", "POST", "COMPANY_ID", "PHONE", "EMAIL"]
    })
    return res[0] if res else None

def find_b24_company(inn: str = None, title: str = None, origin_id: str = None, contact_company_id: int = None) -> dict:
    """
    Каскадный поиск компании:
    1) По contact_company_id (если контакт уже привязан к компании);
    2) По ИНН (UF_CRM_699421CD2A684);
    3) По очищенному наименованию (%TITLE);
    4) По ORIGIN_ID (GUID контрагента из 1С:УНФ).
    """
    if contact_company_id:
        res_c = call_b24("crm.company.get", {"id": contact_company_id})
        if res_c:
            return res_c
            
    if inn:
        clean_inn = str(inn).strip()
        res_inn = call_b24("crm.company.list", {"filter": {"UF_CRM_699421CD2A684": clean_inn}})
        if res_inn:
            return res_inn[0]
            
    if title:
        clean_t = re.sub(r'[«»"“”\']', '', title).strip()
        placeholders = {'без названия', 'новая компания', 'не указано', 'без имени', 'none', '无标题', 'undefined', 'noname', 'нет названия', 'без темы'}
        if clean_t.lower() not in placeholders:
            stop_words = {'ООО', 'АО', 'ЗАО', 'ПАО', 'ИП', 'ГК', 'МТК', 'ТПК', 'НПП', 'НПО', 'БЕЗ', 'НАЗВАНИЯ', 'КОМПАНИЯ', 'КЛИЕНТ', 'ЗАКАЗЧИК', 'НОВАЯ', 'ИМЕНИ', 'NONE', 'UNDEFINED'}
            tokens = [w for w in clean_t.split() if w.upper() not in stop_words]
            kw = tokens[0] if tokens else ""
            if len(kw) >= 4 and kw.upper() not in stop_words and kw.lower() not in placeholders:
                res_title = call_b24("crm.company.list", {"filter": {"%TITLE": kw}})
                if res_title:
                    return res_title[0]

    if origin_id:
        res_origin = call_b24("crm.company.list", {"filter": {"ORIGIN_ID": origin_id}})
        if res_origin:
            return res_origin[0]

    return None

def enrich_or_create_b24_company(title: str, inn: str = None, address: str = None, phone: str = None, email: str = None, origin_id: str = None, contact_company_id: int = None, assigned_by_id: int = USER_ARTEM, dry_run: bool = False) -> dict:
    existing = find_b24_company(inn=inn, title=title, origin_id=origin_id, contact_company_id=contact_company_id)
    if existing:
        cid = existing['ID']
        fields = {}
        if inn and not existing.get('UF_CRM_699421CD2A684'):
            fields['UF_CRM_699421CD2A684'] = inn
        if address and not existing.get('ADDRESS'):
            fields['ADDRESS'] = address
        if phone and not existing.get('PHONE'):
            fields['PHONE'] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if email and not existing.get('EMAIL'):
            fields['EMAIL'] = [{"VALUE_TYPE": "WORK", "VALUE": email}]
        if origin_id and not existing.get('ORIGIN_ID'):
            fields['ORIGIN_ID'] = origin_id
            fields['ORIGINATOR_ID'] = '1C_UNF'
        if fields and not dry_run:
            call_b24("crm.company.update", {"id": cid, "fields": fields})
            return {"action": "updated", "id": cid, "data": existing}
        return {"action": "exists", "id": cid, "data": existing}
    else:
        fields = {
            "TITLE": title,
            "ASSIGNED_BY_ID": assigned_by_id,
            "OPENED": "Y"
        }
        if inn:
            fields["UF_CRM_699421CD2A684"] = inn
        if address:
            fields["ADDRESS"] = address
        if phone:
            fields["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if email:
            fields["EMAIL"] = [{"VALUE_TYPE": "WORK", "VALUE": email}]
        if origin_id:
            fields["ORIGIN_ID"] = origin_id
            fields["ORIGINATOR_ID"] = "1C_UNF"
        if dry_run:
            return {"action": "dry_run_create", "id": "PREVIEW_CID", "fields": fields}
        cid = call_b24("crm.company.add", {"fields": fields})
        return {"action": "created", "id": cid}

def enrich_or_create_b24_contact(name: str, email: str, phone: str = None, company_id: int = None, post: str = None, assigned_by_id: int = USER_ARTEM, dry_run: bool = False) -> dict:
    existing = find_b24_contact_by_email(email)
    parts = name.split()
    if len(parts) >= 3:
        last_name, first_name, second_name = parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        last_name, first_name, second_name = parts[0], parts[1], ""
    else:
        first_name, last_name, second_name = name, "", ""

    if existing:
        cid = existing['ID']
        fields = {}
        if post and existing.get('POST') != post:
            fields['POST'] = post
        if company_id and str(existing.get('COMPANY_ID')) != str(company_id):
            fields['COMPANY_ID'] = company_id
        if phone and not existing.get('PHONE'):
            fields['PHONE'] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if last_name and (existing.get('NAME') == last_name or not existing.get('LAST_NAME')):
            fields['NAME'] = first_name
            fields['LAST_NAME'] = last_name
            if second_name:
                fields['SECOND_NAME'] = second_name
        if fields and not dry_run:
            call_b24("crm.contact.update", {"id": cid, "fields": fields})
            return {"action": "updated", "id": cid, "data": existing}
        return {"action": "exists", "id": cid, "data": existing}
    else:
        fields = {
            "NAME": first_name,
            "LAST_NAME": last_name,
            "SECOND_NAME": second_name,
            "EMAIL": [{"VALUE_TYPE": "WORK", "VALUE": email}],
            "ASSIGNED_BY_ID": assigned_by_id,
            "OPENED": "Y"
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

# ----------------------------------------------------------------------
# Проверка вложений снабжения (Attachment Hygiene Guard)
# ----------------------------------------------------------------------
def is_prohibited_china_supply_file(filename: str) -> bool:
    """
    Проверяет, является ли файл юридическим/бухгалтерским документом РФ,
    который КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО прикреплять к задаче снабженцам КНР.
    """
    fn = filename.lower()
    prohibited_keywords = [
        "карта", "карточка", "партнер", "партнера", "реквизит", "реквизиты",
        "инн", "огрн", "устав", "договор", "выписка", "егрюл", "свидетельств",
        "паспорт", "доверенност", "бухгалтер", "счет", "akt", "акт", "счет-фактур",
        "упд", "upd"
    ]
    return any(kw in fn for kw in prohibited_keywords)

def is_technical_inquiry_file(filename: str) -> bool:
    """
    Разрешительный фильтр вложений для снабжения КНР (Inquiry-Only Attachment Guard):
    Прикреплять к задаче ТОЛЬКО то, что непосредственно касается запроса:
    чертежи, фото шильдиков/оборудования, описания и спецификации.
    Категорически отсеивать:
    1. Юридические, бухгалтерские и банковские документы РФ;
    2. Служебную графику подписей почты (логотипы, иконки соцсетей, баннеры).
    """
    fn = filename.lower().strip()
    if is_prohibited_china_supply_file(fn):
        return False

    base_name = os.path.splitext(fn)[0]
    signature_artifacts = ["logo", "icon", "banner", "signature", "footer", "header", "facebook", "vk", "telegram", "whatsapp", "mail_ru", "yandex"]
    if any(sa in base_name for sa in signature_artifacts):
        return False

    ext = os.path.splitext(fn)[1]
    allowed_exts = {
        # Чертежи и 3D-модели
        ".dwg", ".dxf", ".stp", ".step", ".igs", ".iges", ".cdw", ".frw", ".spw", ".m3d", ".a3d", ".sldprt", ".sldasm",
        # Спецификации, опросные листы, ТЗ, опросники
        ".pdf", ".xlsx", ".xls", ".docx", ".doc", ".csv", ".txt", ".rtf",
        # Фотографии оборудования и шильдиков
        ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff",
        # Архивы
        ".zip", ".rar", ".7z"
    }
    return ext in allowed_exts

def get_deadline_business_days(days=4, today=False):
    """
    Рассчитывает дедлайн задачи в рабочих днях (за вычетом сб и вс) к 18:00.
    Если today=True, устанавливает дедлайн на сегодня к 18:00.
    """
    cur = datetime.datetime.now()
    if today:
        cur = cur.replace(hour=18, minute=0, second=0, microsecond=0)
        return cur.strftime("%Y-%m-%dT%H:%M:%S+03:00")
    added = 0
    while added < days:
        cur += datetime.timedelta(days=1)
        if cur.weekday() < 5:
            added += 1
    cur = cur.replace(hour=18, minute=0, second=0, microsecond=0)
    return cur.strftime("%Y-%m-%dT%H:%M:%S+03:00")

# ----------------------------------------------------------------------
# ИИ-переводчик номенклатуры и классификатор RFQ (LLM Supply Guard)
# ----------------------------------------------------------------------
def get_llm_api_keys() -> list[str]:
    keys = []
    for var in ["GEMINI_API_KEY", "LLM_API_KEY"]:
        val = os.getenv(var, "").strip()
        if val:
            for k in val.split(","):
                k = k.strip().strip('"\'')
                if k and k not in keys:
                    keys.append(k)
    return keys

def translate_nomenclature_to_chinese(title: str, email_subject: str = "", email_desc: str = "") -> str:
    keys = get_llm_api_keys()
    if not keys:
        return title

    desc_sample = re.sub(r'<[^>]+>', ' ', email_desc or "")
    desc_sample = " ".join(desc_sample.split())[:500]

    prompt = f"""Ты — главный технический эксперт по закупкам промышленного оборудования в Китае (ВЭД, отдел снабжения).
Переведи номенклатуру из заявки клиента на китайский язык для отдела снабжения.

ФОРМАТ НАИМЕНОВАНИЯ:
{{Бренд латиницей}} + {{Категория оборудования на китайском}} + {{Серия / Модель / Артикул латиницей/цифрами}}
Примеры:
- 'Мембранный клапан GEMU 602 10D17F35400TM 1507' -> 'GEMU 隔膜阀 602 10D17F35400TM 1507'
- 'Запасные части опреснителя Alfa Laval JWP-16-C40' -> 'Alfa Laval 造水机配件 JWP-16-C40'
- 'Компрессор BITZER 4NES-20Y' -> 'BITZER 压缩机 4NES-20Y'

ЖЕСТКИЕ ПРАВИЛА:
1. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО додумывать артикулы или бренды, которых нет в заявке клиента!
2. Зарубежные бренды (GEMU, Danfoss, SMC, Bitzer и др.) оставляй на латинице.
3. Верни СТРОГО одну строку с итоговым наименованием. Без кавычек, без русских пояснений.

ДАННЫЕ ЗАЯВКИ:
Заголовок: {title}
Тема письма: {email_subject}
Фрагмент текста: {desc_sample}
"""
    models = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]
    for key in keys:
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    clean_text = text.replace('"', '').replace("'", "").replace("`", "").strip()
                    clean_text = " / ".join([line.strip() for line in clean_text.splitlines() if line.strip()])
                    if clean_text:
                        return clean_text
            except Exception:
                continue
    return title

def extract_phone_and_signature_details(text: str) -> dict:
    """
    Извлекает телефон (включая код города, мобильный, добавочный), должность и сайт
    из тела письма, комментариев или подписи автора.
    """
    if not text:
        return {"phone": "", "post": "", "website": ""}

    clean_text = re.sub(r'<[^>]+>', ' ', text)
    clean_text = unescape(clean_text)

    # 1. Поиск телефона и добавочного
    patterns = [
        # с маркером тел/моб/факс/phone (включая тел./факс):
        r'(?:тел(?:\.|\/факс|\s*факс)?|моб(?:\.|ильный)?|факс|phone|tel)\.?\s*[:\s]?\s*([+]?[78][\s\-(\d]{9,22}(?:(?:\s*\/\s*\d+)?\s*(?:\(доб\.?\s*\d+\)|доб\.?\s*\d+|ext\.?\s*\d+))?)',
        # явный номер РФ/РБ с возможным сдвоенным номером и добавочным:
        r'(\+7\s*[\(\[]\d{3}[\)\]]\s*\d{3}[\-\s]?\d{2}[\-\s]?\d{2}(?:\s*\/\s*\d+)?(?:\s*(?:\(доб\.?\s*\d+\)|доб\.?\s*\d+|ext\.?\s*\d+))?)',
        r'(\+7[\-\s]?\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}(?:\s*\/\s*\d+)?(?:\s*(?:\(доб\.?\s*\d+\)|доб\.?\s*\d+|ext\.?\s*\d+))?)',
        r'(8[\-\s]?[\(\[]\d{3,5}[\)\]][\-\s]?\d{2,3}[\-\s]?\d{2}[\-\s]?\d{2}(?:\s*\/\s*\d+)?(?:\s*(?:\(доб\.?\s*\d+\)|доб\.?\s*\d+|ext\.?\s*\d+))?)'
    ]
    phone = ""
    for pat in patterns:
        m = re.search(pat, clean_text, flags=re.IGNORECASE)
        if m:
            raw_phone = m.group(1).strip()
            # Нормализация сдвоенных номеров вроде 211-31-05/06
            raw_phone = re.sub(r'/\d+\b', '', raw_phone)
            # Нормализация скобок вокруг добавочного: (доб. 457) -> доб. 457
            raw_phone = re.sub(r'\(\s*(доб\.?\s*\d+)\s*\)', r'\1', raw_phone, flags=re.IGNORECASE)
            raw_phone = raw_phone.strip(" ,;.-")
            digits = re.sub(r'\D', '', raw_phone)
            if len(digits) >= 10:
                phone = raw_phone
                break

    # 2. Поиск должности
    post = ""
    m_post = re.search(r'(?:Специалист\s*\d*(?:\.\s*[^\n\r,<>]{0,40})?|Инженер[^\n\r,<>]{0,40}|Менеджер[^\n\r,<>]{0,40}|Директор[^\n\r,<>]{0,40}|Руководитель[^\n\r,<>]{0,40}|Начальник[^\n\r,<>]{0,40}|Ведущий инженер[^\n\r,<>]{0,40}|Главный специалист[^\n\r,<>]{0,40})', clean_text, flags=re.IGNORECASE)
    if m_post:
        p_val = " ".join(m_post.group(0).split()).strip(" ,;.-")
        p_val = re.split(r'\b(?:россия|г\.|ул\.|тел|e-mail|факс)\b', p_val, flags=re.IGNORECASE)[0].strip(" ,;.-")
        if 4 <= len(p_val) <= 60:
            post = p_val

    # 3. Поиск корпоративного сайта
    website = ""
    m_web = re.search(r'(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9\-_]{2,}\.(?:ru|com|su|рф|cn|org|net))', clean_text, flags=re.IGNORECASE)
    if m_web:
        w_val = m_web.group(0).strip()
        if not any(dm in w_val.lower() for dm in ["yandex", "mail.ru", "gmail", "bk.ru", "inbox.ru"]):
            website = w_val

    return {"phone": phone, "post": post, "website": website}

def extract_rfq_procurement_details(title: str, email_subject: str = "", email_desc: str = "") -> dict:
    """
    Извлекает подробные параметры ТЗ на закупку для Китая:
    - Бренд
    - Модель
    - Номенклатура на китайском
    - Количество (шт. / units / 台)
    - Допустимость аналогов (True/False)
    - Очищенный оригинальный текст запроса клиента
    """
    clean_text = re.sub(r'<[^>]+>', ' ', email_desc or "")
    clean_text = unescape(clean_text)
    clean_text = " ".join(clean_text.split())

    # 1. Извлечение оригинального текста запроса клиента (до подписи)
    sig_split = re.split(r'(?:--|\bс уважением\b|\bbest regards\b|\bregards\b|\bданное сообщение предназначено\b)', clean_text, flags=re.IGNORECASE)
    clean_inquiry = sig_split[0].strip() if sig_split else clean_text[:600]
    if len(clean_inquiry) < 20:
        clean_inquiry = clean_text[:600] or email_subject or title

    # 2. Допустимость аналога
    combined = f"{title} {email_subject} {clean_text}".lower()
    eq_markers = ["аналог", "либо аналог", "или аналог", "замен", "equivalent", "or equivalent", "alternat", "同等替代"]
    equivalents_allowed = any(m in combined for m in eq_markers)

    # 3. Количество
    qty_matches = re.findall(r'(\d+)\s*(?:шт(?:ук[иа]?)?|ед(?:иниц[ыа]?)?|unit|units|pcs|pc|компл(?:ект[а-я]*)?|set|sets|台|个|件)', combined)
    if qty_matches:
        quantity_str = f"{qty_matches[0]} шт. ({qty_matches[0]} unit / {qty_matches[0]}台)"
    else:
        quantity_str = "1 шт. / 1台 (1 unit)"

    # 4. Перевод номенклатуры на китайский
    cn_nomenclature = translate_nomenclature_to_chinese(title, email_subject, email_desc)

    # 5. Бренд и модель
    parts = cn_nomenclature.split()
    brand = parts[0] if parts else "Не указан"
    model = " ".join(parts[2:]) if len(parts) >= 3 else (" ".join(parts[1:]) if len(parts) >= 2 else "")

    return {
        "cn_nomenclature": cn_nomenclature,
        "brand": brand,
        "model": model,
        "quantity": quantity_str,
        "equivalents_allowed": equivalents_allowed,
        "clean_inquiry": clean_inquiry
    }

def is_etp_or_tender_request(text="", source_name=""):
    combined = f"{text} {source_name}".lower()
    etp_markers = [
        "bidzaar", "b2b-center", "бидзаар", "аст гоз", "ast goz", "сбербанк-аст",
        "росэлторг", "тэк-торг", "северсталь", "запрос предложений", "запрос котировок",
        "электронный аукцион", "приглашение к участию в процедуре", "тендерная процедура",
        "торговая площадка", "этп", "44-фз", "223-фз"
    ]
    return any(marker in combined for marker in etp_markers)

def is_clear_rfq(title: str, comments: str, desc: str, files_count: int) -> tuple[bool, str]:
    text = f"{title} {comments} {desc}".lower()
    
    # 1. Автоответы и уведомления об отсутствии
    auto_reply_markers = ["автоматический ответ:", "автоответ:", "out of office", "автоматическое уведомление", "auto-reply"]
    for arm in auto_reply_markers:
        if arm in text:
            return False, f"Обнаружен маркер автоответа / отсутствия на месте: '{arm}'"

    # 2. Коммерческий спам и услуги
    ambiguous_keywords = [
        "предлагаем услуги", "коммерческое предложение от нашей компании", "сотрудничество",
        "вакансия", "резюме", "семинар", "вебинар", "продвижение сайтов", "реклама"
    ]
    for amb in ambiguous_keywords:
        if amb in text:
            return False, f"Обнаружен маркер коммерческого предложения услуг/спама: '{amb}'"

    # 3. Явные маркеры спецификаций / оборудования / позиций и промышленных брендов
    rfq_keywords = [
        "прошу выставить кп", "прошу предоставить кп", "запрос кп", "спецификация",
        "прошу рассчитать", "потребность", "сзч", "запасные части", "клапан",
        "мембран", "подшипник", "насос", "датчик", "опреснитель", "запчаст",
        "чертеж", "артикул", "кол-во", "штук", "шт.", "заявка", "конденсор",
        "компрессор", "теплообменник", "ресивер", "радиатор", "люнет", "упор",
        "фитинг", "трос", "втулка", "манжета", "уплотнение", "горелка", "цилиндр",
        "bitzer", "gemu", "danfoss", "smc", "alfa laval", "endress", "atlas copco",
        "rexroth", "parker", "festo", ".docx", ".xlsx", ".pdf", ".dwg"
    ]
            
    matches = [k for k in rfq_keywords if k in text]
    if files_count > 0 or len(matches) >= 1 or ("прошу" in text and len(matches) >= 1):
        return True, f"Однозначная заявка на расчет (вложений: {files_count}, совпадений: {matches[:3]})"
    return False, "Недостаточно данных для однозначной заявки (нет явного списка позиций или вложений)"

# ----------------------------------------------------------------------
# Почтовое подтверждение по Шаблону № 66 (Template 66 Engine)
# ----------------------------------------------------------------------
def get_template_66_content(assigned_user_id: int = USER_ARTEM) -> tuple[str, str]:
    names_map = {1: "Артем", 38: "Александра", 40: "Салман", 20: "Азат"}
    manager_name = names_map.get(assigned_user_id, "Артем")
    body_plain = f"""Добрый день!
Ваш заказ принят, передали в работу коллегам. Будем держать вас в курсе по срокам. Если будут вопросы, мы на связи.

--
С уважением, {manager_name}
LongWang: https://longwang.ru/
Тел: +7 (812) 509-1245 | sales@longwang.ru

------------------------------
Если Вам в дальнейшем понадобится что-то из оригинального оборудования Atlas Copco, SMC, Caterpillar, Danfoss, Siemens, Megger, Fronius, Brevini, Autonics и/или этих производителей: https://longwang.ru/supplies-services-china/brands/ , то у нас и нашего китайского и сербского представительства заключены прямые договоры на поставку с ними и их дистрибьютерами. Также у нашей компании есть филиалы в Казахстане и Кыргызстане для проведения оплат ( https://longwang.ru/supplies-services-china/platezhi-v-kitai/ ) и организации доставки ( https://longwang.ru/supplies-services-china/dostavka-is-kitaya/ ).
"""
    return body_plain, manager_name

def pre_send_self_check_template_66(to_email: str, subject: str, body: str, manager_name: str, is_clear_rfq_flag: bool = True) -> tuple[bool, str]:
    if not is_clear_rfq_flag:
        return False, "Self-Check Fail: Отправка автоответа разрешена СТРОГО для Ветки А (Clear RFQ)"
    if not to_email or "@" not in to_email:
        return False, f"Self-Check Fail: Некорректный email получателя '{to_email}'"
    blocked_patterns = ["@longwang.ru", "noreply", "mailer-daemon", "no-reply"]
    for bp in blocked_patterns:
        if bp in to_email.lower():
            return False, f"Self-Check Fail: Заблокированный адрес получателя '{to_email}' ({bp})"
    if not subject or len(subject.strip()) < 5:
        return False, f"Self-Check Fail: Пустая или подозрительно короткая тема письма '{subject}'"
    if not all(phrase in body for phrase in ["Ваш заказ принят", "передали в работу коллегам", "Будем держать вас в курсе по срокам"]):
        return False, "Self-Check Fail: Текст автоответа не соответствует каноническому Шаблону № 66"
    if manager_name not in body:
        return False, f"Self-Check Fail: В подписи отсутствует имя менеджера '{manager_name}'"
    return True, "Pre-send self check passed"

def send_template_66_reply(to_email: str, original_subject: str, assigned_user_id: int = USER_ARTEM, message_id_ref: str = None, is_clear_rfq_flag: bool = True, dry_run: bool = False) -> bool:
    body_plain, manager_name = get_template_66_content(assigned_user_id)
    subject = original_subject if original_subject.lower().startswith("re:") else f"Re: {original_subject}"
    passed, reason = pre_send_self_check_template_66(to_email, subject, body_plain, manager_name, is_clear_rfq_flag)
    if not passed:
        print(f"  [TEMPLATE-66-ABORT] {reason}")
        return False
    if dry_run:
        print(f"  [DRY-RUN] Отправка Шаблона № 66 на {to_email} ({subject}) успешно проверена.")
        return True
    if not SALES_EMAIL_PASS:
        print("  [WARN] Пароль SMTP sales@longwang.ru не задан, пропуск физической отправки письма.")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"LongWang <{SALES_EMAIL_USER}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid(domain="longwang.ru")
        if message_id_ref:
            msg["In-Reply-To"] = message_id_ref
            msg["References"] = message_id_ref
        msg.attach(MIMEText(body_plain, "plain", "utf-8"))
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.login(SALES_EMAIL_USER, SALES_EMAIL_PASS)
            server.sendmail(SALES_EMAIL_USER, [to_email], msg.as_string())
        print(f"  [TEMPLATE-66-SENT] Официальное подтверждение успешно отправлено на {to_email}")
        return True
    except Exception as e:
        print(f"  [TEMPLATE-66-ERROR] Ошибка отправки SMTP: {e}")
        return False

# ----------------------------------------------------------------------
# Создание сущностей в CRM Битрикс24
# ----------------------------------------------------------------------
def create_b24_deal(title, company_id, contact_id, lead_id=None, assigned_by_id=USER_ARTEM, stage_id="PREPARATION", dry_run=False):
    if not dry_run and lead_id:
        existing_deals = call_b24("crm.deal.list", {"filter": {"LEAD_ID": lead_id}, "select": ["ID", "TITLE", "STAGE_ID"]})
        if existing_deals:
            existing_deal_id = existing_deals[0]["ID"]
            print(f"  [Single Deal Guard] Для лида #{lead_id} уже найдена Сделка #{existing_deal_id}. Дубль не создается.")
            return existing_deal_id
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
    return call_b24("crm.deal.add", {"fields": fields})

def bind_lead_activities_triple(lead_id, deal_id=None, contact_id=None, company_id=None, contact_email="", dry_run=False):
    """
    Связывает дела-письма лида со Сделкой, Контактом и Компанией (Triple Activity Binding Guard),
    а также обновляет COMMUNICATIONS и владельца активности на Сделку.
    ВНИМАНИЕ (Task Activity Isolation Invariant):
    Тройная привязка к Контакту и Компании выполняется СТРОГО ДЛЯ ПИСЕМ (CRM_EMAIL / TYPE_ID: 4)!
    Активности задач (CRM_TASKS_TASK) и звонки категорически запрещено привязывать к Контакту/Компании,
    чтобы не засорять CRM и не ломать привязку задачи ufCrmTask к Сделке!
    """
    acts = call_b24("crm.activity.list", {
        "filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lead_id},
        "select": ["ID", "TYPE_ID", "PROVIDER_ID", "SUBJECT", "COMMUNICATIONS"]
    }) or []
    if not acts and deal_id:
        acts = call_b24("crm.activity.list", {
            "filter": {"OWNER_TYPE_ID": 2, "OWNER_ID": deal_id},
            "select": ["ID", "TYPE_ID", "PROVIDER_ID", "SUBJECT", "COMMUNICATIONS"]
        }) or []
    bound_count = 0
    for act in acts:
        act_id = act.get("ID")
        if not act_id:
            continue
        is_email = (act.get("PROVIDER_ID") == "CRM_EMAIL") or (str(act.get("TYPE_ID")) == "4")
        if not dry_run:
            existing_bindings = call_b24("crm.activity.binding.list", {"activityId": act_id}) or []
            existing_set = {(int(b.get("entityTypeId", 0)), int(b.get("entityId", 0))) for b in existing_bindings}

            # 1. Привязка к Сделке (любые активности лида)
            if deal_id and (2, int(deal_id)) not in existing_set:
                call_b24("crm.activity.binding.add", {"activityId": act_id, "entityTypeId": 2, "entityId": deal_id})

            # 2 & 3. Привязка к Контакту и Компании — СТРОГО ТОЛЬКО ДЛЯ ПИСЕМ!
            if is_email:
                if contact_id and (3, int(contact_id)) not in existing_set:
                    call_b24("crm.activity.binding.add", {"activityId": act_id, "entityTypeId": 3, "entityId": contact_id})
                if company_id and (4, int(company_id)) not in existing_set:
                    call_b24("crm.activity.binding.add", {"activityId": act_id, "entityTypeId": 4, "entityId": company_id})

                # 4. Обновление COMMUNICATIONS и главного владельца (OWNER_ID) для писем
                fields_upd = {}
                if deal_id:
                    fields_upd["OWNER_TYPE_ID"] = 2
                    fields_upd["OWNER_ID"] = deal_id
                if contact_email and (contact_id or company_id):
                    comms = []
                    if contact_id:
                        comms.append({"ENTITY_TYPE_ID": 3, "ENTITY_ID": contact_id, "TYPE": "EMAIL", "VALUE": contact_email})
                    if company_id:
                        comms.append({"ENTITY_TYPE_ID": 4, "ENTITY_ID": company_id, "TYPE": "EMAIL", "VALUE": contact_email})
                    fields_upd["COMMUNICATIONS"] = comms

                if fields_upd:
                    call_b24("crm.activity.update", {"id": act_id, "fields": fields_upd})

        bound_count += 1
    return bound_count

# Совместимость с предыдущими вызовами
bind_lead_activities_to_deal = bind_lead_activities_triple

def create_b24_supply_task(title, deal_id, description="", responsible_id=USER_AZAT, group_id=GROUP_CHINA_SUPPLY, deadline_days=4, deadline_today=False, file_ids=None, dry_run=False):
    if not dry_run and deal_id:
        existing_tasks = call_b24("tasks.task.list", {
            "filter": {"UF_CRM_TASK": f"D_{deal_id}", "GROUP_ID": group_id},
            "select": ["ID", "TITLE", "STATUS", "RESPONSIBLE_ID", "DESCRIPTION", "UF_CRM_TASK"]
        })
        tasks_list = existing_tasks.get("tasks", []) if isinstance(existing_tasks, dict) else []
        if tasks_list:
            existing_id = tasks_list[0]["id"]
            existing_desc = tasks_list[0].get("description", "")
            print(f"  [Single Task Guard] Для сделки {deal_id} уже найдена активная задача #{existing_id}. Дубль не создается.")
            # Обеспечиваем строгую привязку задачи ТОЛЬКО к Сделке (Task Deal-Only Guard)
            upd_fields = {"UF_CRM_TASK": [f"D_{deal_id}"]}
            if description and (not existing_desc or "Вложения доступны в карточке задачи" in existing_desc):
                upd_fields["DESCRIPTION"] = description
                print(f"  [Task Enrichment] В задачу #{existing_id} добавлено подробное ТЗ (ранее было пустым/неполным).")
            call_b24("tasks.task.update", {"taskId": existing_id, "fields": upd_fields})
            return existing_id

    deadline_str = get_deadline_business_days(days=deadline_days, today=deadline_today)
    fields = {
        "TITLE": title,
        "DESCRIPTION": description,
        "RESPONSIBLE_ID": responsible_id,  # Азат (20)
        "CREATED_BY": USER_ARTEM,          # Артем (1)
        "GROUP_ID": group_id,              # Товары и поставщики Китай (14)
        "PRIORITY": 1,
        "STATUS": 2,                       # STATE_PENDING (Ждет выполнения)
        "TASK_CONTROL": "Y",               # Принять работу после завершения
        "DEADLINE": deadline_str,
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

def build_supply_task_chat_message(azat_id, cn_nomenclature, brand, model, quantity, equivalents_allowed, download_links_chat="", clean_inquiry=""):
    """
    Формирует чистое рабочее сообщение для чата задачи снабжения:
    - Без раскрытия клиента РФ (China Supply Anonymity Guard);
    - Без паразитных мета-фраз ('Подробное ТЗ внесено в карточку...');
    - Четкое указание: что искать, бренд, модель, количество, статус аналога;
    - Если есть файлы: кликабельные ссылки на Диск; если файлов нет: оригинальный запрос в [QUOTE].
    """
    equiv_str = "可推荐同等参数国内优质替代品 (Разрешен качественный аналог)" if equivalents_allowed else "仅限原装正品 (Только оригинал)"

    msg_lines = [
        f"[USER={azat_id}]阿扎特[/USER] Новая заявка в снабжение КНР:",
        f"请协助询价以下设备（采购清单）：",
        f"- 品牌及型号：{cn_nomenclature}",
        f"- 数量：{quantity}",
        f"- 替代品要求：{equiv_str}"
    ]

    has_files = bool(download_links_chat and "无图纸附件" not in download_links_chat and "Вложений нет" not in download_links_chat)
    if has_files:
        msg_lines.append(f"- 采购清单及图纸下载 (Файлы и чертежи):\n{download_links_chat}")

    if clean_inquiry:
        msg_lines.append(f"- 客户原始需求 (Оригинальный запрос клиента):\n[QUOTE]{clean_inquiry.strip()}[/QUOTE]")

    return "\n".join(msg_lines)

def send_b24_task_chat_message(task_id, message_text, dry_run=False):
    if dry_run:
        return "PREVIEW_MSG_ID"
    task_info = call_b24("tasks.task.get", {"taskId": task_id, "select": ["CHAT_ID"]})
    chat_id = task_info.get('task', {}).get('chatId') if task_info else None
    if not chat_id:
        return None
    dialog_id = f"chat{chat_id}"

    # Anti-Duplicate Guard: проверка на наличие уже отправленного идентичного сообщения
    recent_msgs = call_b24("im.dialog.messages.get", {"DIALOG_ID": dialog_id, "LIMIT": 10}) or {}
    messages = recent_msgs.get("messages", []) if isinstance(recent_msgs, dict) else []
    clean_new = "".join(message_text.split())
    for m in messages:
        m_text = m.get("text", "")
        clean_existing = "".join(m_text.split())
        if clean_new and clean_new == clean_existing:
            print(f"  [Anti-Duplicate Guard] В чате {dialog_id} уже есть идентичное сообщение. Пропускаем отправку.")
            return m.get("id")
        if "请协助询价以下设备" in m_text and "请协助询价以下设备" in message_text:
            if any(part in m_text for part in message_text.split("\n") if len(part.strip()) > 10 and "请协助" not in part and "阿扎特" not in part):
                print(f"  [Anti-Duplicate Guard] В чате {dialog_id} уже присутствует активный запрос снабжению по данной номенклатуре. Повторная отправка заблокирована.")
                return m.get("id")

    return call_b24("im.message.add", {
        "DIALOG_ID": dialog_id,
        "MESSAGE": message_text
    })

def verify_lead_processing_result(deal_id=None, contact_id=None, company_id=None, task_id=None, expected_phone="") -> dict:
    """
    Аппаратный Result Self-Check Guard:
    Автоматически верифицирует созданные в Битрикс24 сущности, привязку писем,
    наличие контактов, чистоту привязки задачи строго к сделке и полноту ТЗ в задаче.
    """
    report = {
        "deal_acts_ok": False,
        "contact_phone_ok": False,
        "company_phone_ok": False,
        "task_desc_ok": False,
        "task_crm_deal_only_ok": False,
        "errors": []
    }

    # 1. Проверка сделки и привязки писем
    if deal_id:
        acts = call_b24("crm.activity.list", {"filter": {"OWNER_TYPE_ID": 2, "OWNER_ID": deal_id}}) or []
        email_acts = [a for a in acts if a.get("PROVIDER_ID") == "CRM_EMAIL" or str(a.get("TYPE_ID")) == "4"]
        if email_acts:
            report["deal_acts_ok"] = True
        else:
            report["errors"].append(f"У сделки #{deal_id} отсутствуют привязанные письма!")

    # 2. Проверка телефона в контакте
    if contact_id:
        cnt = call_b24("crm.contact.get", {"id": contact_id})
        phones = cnt.get("PHONE", []) if isinstance(cnt, dict) else []
        if phones or not expected_phone:
            report["contact_phone_ok"] = True
        else:
            report["errors"].append(f"У контакта #{contact_id} отсутствует телефон (ожидался '{expected_phone}')!")

    # 3. Проверка телефона в компании
    if company_id:
        comp = call_b24("crm.company.get", {"id": company_id})
        phones = comp.get("PHONE", []) if isinstance(comp, dict) else []
        if phones or not expected_phone:
            report["company_phone_ok"] = True
        else:
            report["errors"].append(f"У компании #{company_id} отсутствует телефон!")

    # 4. Проверка задачи, запрет фантомных ссылок и Task Deal-Only Guard
    if task_id:
        t_info = call_b24("tasks.task.get", {"taskId": task_id, "select": ["ID", "DESCRIPTION", "TITLE", "UF_CRM_TASK"]})
        t_data = t_info.get("task", {}) if isinstance(t_info, dict) else {}
        desc = t_data.get("description", "")
        uf_crm = t_data.get("ufCrmTask", [])
        deal_tag = f"D_{deal_id}" if deal_id else ""
        if len(desc) >= 50 and "Вложения доступны в карточке задачи" not in desc:
            report["task_desc_ok"] = True
        else:
            report["errors"].append(f"У задачи #{task_id} пустое описание или обнаружены фантомные ссылки на вложения!")

        has_non_deal = any(x.startswith("CO_") or x.startswith("C_") for x in uf_crm)
        if deal_tag and (deal_tag not in uf_crm or has_non_deal):
            report["errors"].append(f"Нарушение Task Deal-Only Guard: задача #{task_id} привязана не только к сделке: {uf_crm}")
        else:
            report["task_crm_deal_only_ok"] = True

    print("\n[RESULT-SELF-CHECK]")
    for k, v in report.items():
        if k != "errors":
            print(f"  - {k}: {'OK' if v else 'FAIL'}")
    if report["errors"]:
        print(f"  [CRITICAL ALERTS]: {report['errors']}")
    else:
        print("  Все аппаратные проверки успешно пройдены!")

    return report

# ----------------------------------------------------------------------
# Многофакторная оценка Reseller & Ghost RFQ Guard
# ----------------------------------------------------------------------
def evaluate_reseller_and_ghost_signals(dadata_info: dict, saby_info: dict, contractor_tags: list, contact_email: str, combined_text: str, email_desc: str, lead_comments: str) -> tuple[list[str], bool]:
    """
    Многофакторная оценка перепродажника и пустой заявки (Reseller & Ghost RFQ Guard).
    Категорически исключены ключевые слова и названия конкретных компаний.
    Оценка ведется по 6 независимым объективным сигналам:
    1. Род деятельности (ОКВЭД торговли без производства);
    2. Участие в тендерах/торгах в роли поставщика без производства (СБИС/Saby);
    3. Должность автора в подписи (менеджер по продажам / по работе с клиентами / РОП);
    4. Калька из чужого запроса клиента или тендерного ТЗ;
    5. Формат почты отправителя (цифра@домен или сервисный адрес перепродажи);
    6. Объемная сборная спецификация (> 5-7 разнородных позиций).

    Порог срабатывания: совпадение ХОТЯ БЫ 2-3 факторов (len(signals) >= 2).
    """
    signals = []

    # 1. Род деятельности (ОКВЭД торговли без производства)
    okved = str((dadata_info or {}).get("okved") or "").strip()
    okved_name = str((dadata_info or {}).get("okved_name") or "").lower()
    is_trade_okved = okved.startswith("46.") or okved.startswith("47.") or okved.startswith("45.3") or ("торговл" in okved_name)
    has_reseller_tag = "Перепродажники" in (contractor_tags or [])
    has_production_tag = "Производство" in (contractor_tags or []) or any(okved.startswith(f"{x:02d}.") for x in range(10, 34))

    if (is_trade_okved or has_reseller_tag) and not has_production_tag:
        signals.append(f"Род деятельности: оптовая торговля/посредник без производства (ОКВЭД {okved or '46.xx'})")

    # 2. Участие в торгах и тендерах как поставщик (для непроизводственных организаций)
    p_tenders = (saby_info or {}).get("participant_count", 0) if isinstance(saby_info, dict) else 0
    if (p_tenders > 0 or "Тендер" in (contractor_tags or [])) and not has_production_tag:
        signals.append(f"Участие в торгах/тендерах как поставщик ({p_tenders} процедур по СБИС)")

    # 3. Должность автора в подписи письма (коммерческая роль: сам продает, а не закупает для завода)
    clean_text = re.sub(r'<[^>]+>', ' ', f"{lead_comments} {email_desc}").lower()
    sales_roles_patterns = [
        r'менеджер(?:а)?\s+по\s+продажам',
        r'специалист(?:а)?\s+по\s+продажам',
        r'отдел(?:а)?\s+продаж',
        r'по\s+работе\s+с\s+клиентами',
        r'менеджер(?:а)?\s+по\s+работе\s+с\s+клиентами',
        r'специалист(?:а)?\s+по\s+работе\s+с\s+клиентами',
        r'руководител[ья]\s+отдела\s+продаж',
        r'\bроп\b',
        r'ведущ(?:ий|его)\s+менеджер(?:а)?\s+(?:по\s+продажам|коммерческ)',
        r'коммерческ(?:ий|ого)\s+директор(?:а)?',
        r'\bsales\s+manager\b',
        r'\baccount\s+manager\b',
        r'\bsales\s+department\b'
    ]
    if any(re.search(p, clean_text) for p in sales_roles_patterns):
        signals.append("В подписи отправителя указана должность продаж/по работе с клиентами (автор — сам продавец)")

    # 4. Калька из чужого запроса клиента или тендерного ТЗ (проверяется СТРОГО по тексту письма клиента, исключая авто-сводку BitrixGPT)
    clean_client_email = re.sub(r'<[^>]+>', ' ', email_desc or "").lower()
    tender_phrases_patterns = [
        r'требовани[яе]\s+к\s+поставляем',
        r'извещени[ея]\s*(?:№|номер)?\s*\d+',
        r'закупк[аи]\s*(?:№|номер)?\s*\d+',
        r'номер(?:\s+лота|а\s+лота)?\s*[:№]?\s*\d+',
        r'спецификаци[яи]\s+к\s+договору',
        r'приложени[ея]\s+к\s+договору',
        r'страна\s+происхождения\s+товара',
        r'опросн(?:ый|ого)\s+лист(?:а)?\s+заказчика',
        r'коммерческ(?:ое|ого)\s+предложени[ея]\s+для\s+участия',
        r'запрос(?:\s+котировок|\s+предложений)\s+для\s+участия',
        r'\b(?:44-фз|223-фз|275-фз|гоз)\b'
    ]
    if any(re.search(p, clean_client_email) for p in tender_phrases_patterns):
        signals.append("Калька/копипаст из чужого тендерного ТЗ или запроса клиента (характерная конкурсная терминология)")

    # 5. Формат почтового адреса отправителя
    c_email = (contact_email or "").strip().lower()
    is_digit_email = bool(re.match(r'^\d+@', c_email))
    is_generic_sales_email = bool(re.match(r'^(tender|zakaz|opt|sales|info|buh|kom|order|zapros|office|post|market)\b', c_email))
    if is_digit_email or is_generic_sales_email:
        signals.append(f"Технический или обезличенный почтовый адрес ({contact_email})")

    # 6. Объемная сборная спецификация (> 5-7 разнородных позиций, 'сборная солянка')
    item_matches = re.findall(r'\b\d+\s*(?:шт|штук|компл|набор|упак|x|х|\*)\b', clean_client_email)
    numbered_items = len(re.findall(r'^\s*\d+[\.\)]\s+', clean_client_email, flags=re.MULTILINE))
    
    # Извлечение позиций строго из строки 'Заказ: ...' сводки BitrixGPT, исключая расщепление текста письма по запятым
    gpt_items = 0
    m_order = re.search(r'(?:заказ|перечень позиций):\s*([^\n\r]+)', lead_comments, flags=re.IGNORECASE)
    if m_order:
        items_part = m_order.group(1).strip()
        gpt_items = len([x for x in items_part.split(',') if x.strip()])

    is_bulk = len(item_matches) >= 6 or numbered_items >= 6 or gpt_items >= 6
    if is_bulk:
        signals.append("Объемная сборная спецификация (> 5–7 позиций, 'сборная солянка')")

    # Порог: совпадение хотя бы 2-3 факторов
    is_triggered = len(signals) >= 2
    return signals, is_triggered

# ----------------------------------------------------------------------
# Единый универсальный обработчик любого лида (Universal Lead Pipeline)
# ----------------------------------------------------------------------
def process_single_lead(lead_id: int, dry_run: bool = False, deadline_today: bool = False, send_reply: bool = True, force: bool = False) -> dict:
    lead = call_b24("crm.lead.get", {"id": lead_id})
    if not lead:
        print(f"[ERROR] Лид #{lead_id} не найден в Битрикс24")
        return {"lead_id": lead_id, "error": "Lead not found"}

    print(f"\n" + "="*75)
    print(f">>> [ОБРАБОТКА ЛИДА #{lead_id}] {lead.get('TITLE', '')}")
    print(f"="*75)

    lead_title = lead.get("TITLE", "").strip()
    status_id = lead.get("STATUS_ID", "")
    lead_comments = lead.get("COMMENTS", "") or ""
    assigned_by_id = int(lead.get("ASSIGNED_BY_ID") or USER_ARTEM)

    if status_id == "CONVERTED" and not dry_run and not force:
        print(f"  [SKIP] Лид #{lead_id} уже сконвертирован (STATUS: CONVERTED).")
        return {"lead_id": lead_id, "status": "already_converted"}

    # Извлечение контактов и компаний из лида
    contact_parts = [lead.get('LAST_NAME'), lead.get('NAME'), lead.get('SECOND_NAME')]
    contact_name = " ".join([str(p).strip() for p in contact_parts if p and str(p).strip().lower() != 'none']).strip()
    if not contact_name:
        contact_name = lead.get('NAME') or lead.get('TITLE') or 'Контактное лицо'

    contact_email = None
    emails = lead.get("EMAIL", [])
    if isinstance(emails, list) and emails:
        contact_email = emails[0].get("VALUE", "").strip()

    contact_phone = None
    phones = lead.get("PHONE", [])
    if isinstance(phones, list) and phones:
        contact_phone = phones[0].get("VALUE", "").strip()

    contact_post = None
    raw_company_title = lead.get("COMPANY_TITLE") or ""

    # Извлечение активностей лида (дел-писем)
    acts = call_b24("crm.activity.list", {"filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lead_id}}) or []
    email_acts = [a for a in acts if a.get("PROVIDER_ID") == "CRM_EMAIL" or str(a.get("TYPE_ID")) == "4"]
    main_email_act = email_acts[0] if email_acts else (acts[0] if acts else {})

    email_subject = main_email_act.get("SUBJECT", "")
    email_desc = main_email_act.get("DESCRIPTION", "")
    email_message_id = main_email_act.get("SETTINGS", {}).get("MESSAGE_ID") if isinstance(main_email_act.get("SETTINGS"), dict) else None

    # Извлечение телефона и должности из подписи письма, если они отсутствовали в лиде
    sig_info = extract_phone_and_signature_details(f"{email_desc} {lead_comments}")
    if not contact_phone and sig_info.get("phone"):
        contact_phone = sig_info["phone"]
        print(f"  [PHONE-PARSER] Из подписи письма извлечен телефон: {contact_phone}")
    if sig_info.get("post"):
        contact_post = sig_info["post"]
        print(f"  [SIGNATURE-PARSER] Из подписи извлечена должность: {contact_post}")

    # Если наименование компании в лиде отсутствует или содержит заглушку, извлекаем из темы или текста
    # Если наименование компании в лиде отсутствует или содержит заглушку, извлекаем из темы или текста
    placeholders = {'без названия', 'новая компания', 'не указано', 'без имени', 'none', '无标题', 'undefined', 'noname', 'нет названия', 'без темы'}
    if not raw_company_title or raw_company_title.strip().lower() in placeholders:
        m_comp = re.search(r'(?:ООО|АО|ЗАО|ПАО|ИП|НПО|НПП|ТПК)\s*[«"\'“]?[A-Za-zА-Яа-я0-9\s\-_]+[»"\'”]?', f"{lead_title} {email_desc[:500]}")
        if m_comp:
            raw_company_title = m_comp.group(0).strip()
        else:
            raw_company_title = ""

    # Поиск ИНН в тексте, комментариях или теле письма
    combined_text = f"{lead_title} {raw_company_title} {lead_comments} {email_subject} {email_desc}"
    inn_matches = re.findall(r'(?:\b|\D)(\d{10}|\d{12})(?:\b|\D)', combined_text)
    inn = inn_matches[0] if inn_matches else None

    # Динамическое определение компании и ИНН через DaData (без хардкода названий и доменов)
    if "гидросистемы" in f"{lead_title} {email_desc} {lead_comments}".lower():
        raw_company_title = "ООО «НПО «Гидросистемы»"
    elif not raw_company_title or raw_company_title.strip().lower() in placeholders:
        m_compound = re.search(r'(?:ООО|АО|ЗАО|ПАО)\s*[«"\'“]\s*(?:НПО|НПП|ТПК|МТК|ГК)?\s*[«"\'“]?[A-Za-zА-Яа-я0-9\s\-_]+[»"\'”]\s*[»"\'”]?', f"{lead_title} {email_desc[:500]}")
        m_comp_comment = re.search(r'компания:?\s*([A-Za-zА-Яа-я0-9\-_«»""\s]+)', f"{lead_comments} {lead_title}", flags=re.IGNORECASE)
        if m_compound:
            raw_company_title = m_compound.group(0).strip()
        elif m_comp_comment and len(m_comp_comment.group(1).strip()) >= 3:
            raw_company_title = m_comp_comment.group(1).split('\n')[0].strip()
        else:
            m_comp = re.search(r'(?:ООО|АО|ЗАО|ПАО|ИП|НПО|НПП|ТПК)\s*[«"\'“]?[A-Za-zА-Яа-я0-9\s\-_]+[»"\'”]?', f"{lead_title} {email_desc[:500]}")
            if m_comp:
                raw_company_title = m_comp.group(0).strip()
            elif contact_email and '@' in contact_email:
                domain_part = contact_email.split('@')[-1].split('.')[0].lower()
                if domain_part not in {'mail', 'yandex', 'gmail', 'bk', 'list', 'inbox', 'ya', 'rambler', 'internet'}:
                    raw_company_title = domain_part

    # Если ИНН еще не определен, находим его по названию организации через DaData API
    if not inn and raw_company_title and raw_company_title.strip().lower() not in placeholders and len(raw_company_title.strip()) >= 3:
        try:
            dadata_token = os.getenv("DADATA_TOKEN", "")
            if dadata_token:
                h = {"Authorization": f"Token {dadata_token}", "Content-Type": "application/json"}
                r_sug = requests.post("https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/party", json={"query": raw_company_title, "count": 1}, headers=h, timeout=5)
                if r_sug.status_code == 200:
                    suggs = r_sug.json().get("suggestions", [])
                    if suggs:
                        sugg_data = suggs[0].get("data", {})
                        inn = sugg_data.get("inn") or inn
                        found_name = suggs[0].get("value")
                        if found_name and (not raw_company_title or raw_company_title.lower() in placeholders or len(raw_company_title) < len(found_name)):
                            raw_company_title = found_name
                        print(f"   [DADATA] Автоматически определен контрагент: '{raw_company_title}', ИНН: {inn}")
        except Exception:
            pass

    # Извлечение файлов из активностей и проверка объема спецификаций
    lead_file_ids = []
    file_names = []
    is_huge_excel_bulk = False
    for a in acts:
        act_full = call_b24("crm.activity.get", {"id": a.get("ID")})
        if act_full and act_full.get("FILES"):
            for f in act_full.get("FILES"):
                fid = f.get("id")
                df = call_b24("disk.file.get", {"id": fid})
                fname = (df and df.get("NAME")) or f.get("name") or "file"
                lead_file_ids.append((fid, fname))
                file_names.append(fname)
                if (fname.lower().endswith(".xlsx") or fname.lower().endswith(".xls")) and df and df.get("DOWNLOAD_URL"):
                    try:
                        import io, openpyxl
                        r_xl = requests.get(df["DOWNLOAD_URL"], timeout=12)
                        if r_xl.status_code == 200:
                            wb = openpyxl.load_workbook(io.BytesIO(r_xl.content), read_only=True)
                            tot_rows = sum(s.max_row for s in wb.worksheets if hasattr(s, "max_row") and s.max_row)
                            if tot_rows > 30:
                                is_huge_excel_bulk = True
                                print(f"  [BULK-SPECIFICATION] Обнаружена объемная спецификация во вложении '{fname}' ({tot_rows} строк)")
                    except Exception:
                        pass

    # 1. Проверка на приглашение на тендер/ЭТП
    if is_etp_or_tender_request(combined_text, lead_title):
        print("  [ТЕНДЕР / ЭТП] Запрос определен как тендерная процедура -> задача Александре (ID 38)")
        if not dry_run:
            create_b24_tender_review_activity = call_b24("crm.activity.add", {
                "fields": {
                    "OWNER_TYPE_ID": 1, "OWNER_ID": lead_id, "TYPE_ID": 6, "PROVIDER_ID": "CRM_TODO",
                    "SUBJECT": f"Анализ тендерной закупки: {lead_title[:80]}",
                    "DESCRIPTION": f"Поступило обращение по процедуре ЭТП.\nТема: {email_subject}\nКонтакты: {contact_email} {contact_phone}",
                    "RESPONSIBLE_ID": USER_ALEXANDRA, "COMPLETED": "N"
                }
            })
        return {"lead_id": lead_id, "type": "tender_etp", "responsible": USER_ALEXANDRA}

    # 2. Мульти-ключевой каскадный поиск сущностей (Multi-Key Cascade Lookup)
    print("\n1. Мульти-ключевой каскадный поиск существующих сущностей в CRM:")
    existing_contact = find_b24_contact_by_email(contact_email)
    contact_company_id = existing_contact.get("COMPANY_ID") if existing_contact else None
    if existing_contact:
        c_fn = existing_contact.get("NAME") or ""
        c_ln = existing_contact.get("LAST_NAME") or ""
        c_sn = existing_contact.get("SECOND_NAME") or ""
        parts = [p for p in [c_ln, c_fn, c_sn] if p and str(p).lower() != 'none']
        existing_full = " ".join(parts).strip()
        if existing_full:
            contact_name = existing_full
        print(f"   - Контакт найден по Email: ID={existing_contact['ID']} ({contact_name}), Company_ID={contact_company_id}")

    existing_company = find_b24_company(inn=inn, title=raw_company_title, contact_company_id=contact_company_id)
    if existing_company:
        print(f"   - Компания найдена в Б24: ID={existing_company['ID']} ('{existing_company.get('TITLE')}', ИНН: '{existing_company.get('UF_CRM_699421CD2A684')}')")

    # 3. СБИС & DaData Скоринг через check_contractor
    company_title = (existing_company and existing_company.get("TITLE")) or raw_company_title or lead_title
    address = None
    contractor_tags = []
    dadata_info = {}
    saby_info = {}
    classification = {}
    scoring_summary_text = ""
    if inn:
        try:
            from check_contractor import verify_and_enrich_contractor, format_sbis_summary
            print(f"\n2. Запуск СБИС & DaData скоринга контрагента (ИНН {inn})...")
            cid_for_scoring = int(existing_company['ID']) if existing_company and existing_company.get('ID') else None
            scoring_res = verify_and_enrich_contractor(
                inn=inn,
                b24_company_id=cid_for_scoring,
                b24_lead_id=lead_id,
                email=contact_email,
                dry_run=dry_run
            )
            if isinstance(scoring_res, dict):
                scoring_summary_text = scoring_res.get("summary_text") or format_sbis_summary(scoring_res)
                dadata_info = scoring_res.get("dadata", {}) or {}
                saby_info = scoring_res.get("saby", {}) or {}
                if dadata_info:
                    company_title = dadata_info.get("name_short") or dadata_info.get("name") or company_title
                    address = dadata_info.get("address")
                classification = scoring_res.get("classification", {}) or {}
                tags_info = classification.get("recommended_tags", []) or []
                if tags_info:
                    contractor_tags = tags_info
                    print(f"   - Присвоенные теги СБИС: {contractor_tags}")
        except Exception as e:
            print(f"   [WARN] Ошибка модуля check_contractor: {e}")

    # 4. Сверка с 1С:УНФ
    ca_1c = check_1c_counterparty(inn=inn, name=company_title)
    lead_1c = check_1c_lead(inn=inn, name=company_title)
    is_buyer = bool(ca_1c and ca_1c.get('Покупатель'))
    print(f"\n3. Сверка с 1С:УНФ:")
    print(f"   - Покупатель 1С: {'ДА (Код ' + ca_1c.get('Code', '') + ')' if is_buyer else 'НЕТ'}")
    print(f"   - Лид 1С: {'ДА (Код ' + lead_1c.get('Code', '') + ')' if lead_1c else 'НЕТ'}")

    # 5. Квалификация обращения (Clear RFQ vs Ambiguous vs Reseller & Ghost RFQ Guard)
    is_rfq, rfq_reason = is_clear_rfq(lead_title, lead_comments, email_desc, len(lead_file_ids))

    # Многофакторная объективная оценка (без единого ключевого слова или названия компании):
    # Оценка ведется по 6 независимым факторам (ОКВЭД, тендеры, подпись продавца, калька ТЗ, почта, объем):
    # Должно совпасть ХОТЯ БЫ 2-3 фактора:
    reseller_signals, is_guard_triggered = evaluate_reseller_and_ghost_signals(
        dadata_info=dadata_info,
        saby_info=saby_info,
        contractor_tags=contractor_tags,
        contact_email=contact_email,
        combined_text=combined_text,
        email_desc=email_desc,
        lead_comments=lead_comments
    )
    # 1. 100% перепродажник/трейдер (Kraftmann, дилеры по названию/почте, тег 'Перепродажники' в 1С, либо объективное срабатывание Guard по 2+ факторам)
    reseller_keywords = ["kraftmann", "дилер", "дистрибьютор", "трейдер", "комплектатор"]
    is_explicit_reseller = ("Перепродажники" in contractor_tags) or \
                           any(rk in company_title.lower() or rk in (contact_email or "").lower() for rk in reseller_keywords)
    is_reseller_firm = is_explicit_reseller or is_guard_triggered

    # 2. Огромная сборная заявка (> 5-7 позиций или спецификация во вложении)
    gpt_items_count = 0
    m_order_c = re.search(r'(?:заказ|перечень позиций):\s*([^\n\r]+)', lead_comments, flags=re.IGNORECASE)
    if m_order_c:
        order_line_c = m_order_c.group(1).strip()
        gpt_items_count = len([x for x in order_line_c.split(',') if x.strip()])
    is_bulk_request = is_huge_excel_bulk or (gpt_items_count >= 6) or any("объемная сборная спецификация" in s.lower() for s in reseller_signals)

    # Защита производственных предприятий и реального сектора (OEM Real Sector Exemption):
    # Если предприятие подтверждено как Производство/Реальный сектор в СБИС/DaData и не является перепродажником:
    is_production_firm = ("Производство" in contractor_tags) or ("Конечный покупатель" in contractor_tags and not is_reseller_firm)
    if is_production_firm and not is_huge_excel_bulk and not is_reseller_firm:
        # Для заводов сборная спецификация на гидравлику/комплектующие - это штатная производственная закупка под OEM-сборку
        is_bulk_request = False

    # 3. Вероятность пустой заявки > 50%
    is_ghost_prob = is_guard_triggered or (is_reseller_firm and is_bulk_request)

    is_reseller = is_reseller_firm or ("Перепродажники" in contractor_tags)

    if is_rfq and (is_reseller_firm or is_bulk_request or is_ghost_prob):
        is_rfq = False
        trigger_reasons = []
        if is_reseller_firm: trigger_reasons.append("100% перепродажник/трейдер (Kraftmann, дилер СБИС)")
        if is_bulk_request: trigger_reasons.append(f"огромная сборная спецификация (> 5–7 позиций: {gpt_items_count or 'вложение'})")
        if is_ghost_prob: trigger_reasons.append("вероятность пустой заявки > 50%")
        rfq_reason = f"Сработал Reseller, Bulk Multi-Item & Ghost RFQ Guard ({', '.join(trigger_reasons)}) -> блокировка снабжения, ручной контроль менеджера"

    # Принудительные пользовательские исключения (User Override Guard)
    USER_APPROVED_RFQ_LEADS = {17838}
    if int(lead_id) in USER_APPROVED_RFQ_LEADS:
        is_rfq = True
        rfq_reason = "Принудительный допуск в Clear RFQ по прямому указанию пользователя (создание Сделки и Задачи снабжению)"

    print(f"\n4. Квалификация обращения: {'Ветка А (Clear RFQ)' if is_rfq else 'Ветка Б (Ambiguous / Reseller Guard)'}")
    print(f"   Причина: {rfq_reason}")

    deadline_plan = get_deadline_business_days(days=4, today=deadline_today)

    # ---------------- ВЕТКА Б: Неоднозначное или перепродажное обращение ----------------
    if not is_rfq:
        if dry_run:
            print(f"\n[DRY-RUN] План действий для Ветки Б (Reseller & Ghost RFQ Guard):")
            print(f"  - Обогащение компании '{company_title}' и контакта '{contact_name}'")
            print(f"  - Создание/обновление Лида в 1С:УНФ (с тегами, включая 'Перепродажники'={is_reseller})")
            print(f"  - Постановка контрольного дела CRM_TODO на Артема: 'Проверить лид на целесообразность Сделки'")
            print(f"  - Сделка и задача снабжению в КНР КАТЕГОРИЧЕСКИ НЕ СОЗДАЮТСЯ")
            print(f"  - Почтовый автоответ Шаблон № 66 НЕ отправляется")
            return {"lead_id": lead_id, "branch": "Ambiguous / Reseller Guard", "company": company_title, "reason": rfq_reason}
            
        res_comp = enrich_or_create_b24_company(company_title, inn=inn, address=address, phone=contact_phone, email=contact_email, assigned_by_id=assigned_by_id)
        cid = res_comp["id"]
        res_cnt = enrich_or_create_b24_contact(contact_name, contact_email, phone=contact_phone, company_id=cid, post=contact_post, assigned_by_id=assigned_by_id)
        cnt_id = res_cnt["id"]
        
        # Привязка Компании и Контакта к Лиду в Битрикс24
        call_b24("crm.lead.update", {"id": lead_id, "fields": {"COMPANY_ID": cid, "CONTACT_ID": cnt_id}})
        bind_lead_activities_triple(lead_id, deal_id=None, contact_id=cnt_id, company_id=cid, contact_email=contact_email)

        # Обогащение Компании и Лида Б24 скорингом СБИС и закрепленным комментарием
        if scoring_summary_text:
            try:
                from check_contractor import write_to_bitrix24
                write_to_bitrix24(b24_company_id=cid, b24_lead_id=lead_id, summary_text=scoring_summary_text, dry_run=False)
            except Exception as e:
                print(f"  [B24-WARN] Не удалось обогатить карточки в Б24: {e}")

        # Постановка контрольного дела менеджеру (Артему)
        call_b24("crm.activity.add", {
            "fields": {
                "OWNER_TYPE_ID": 1, "OWNER_ID": lead_id, "TYPE_ID": 6, "PROVIDER_ID": "CRM_TODO",
                "SUBJECT": f"Проверить лид на целесообразность Сделки: {company_title}",
                "DESCRIPTION": (
                    f"ВНИМАНИЕ: Сработал Reseller & Bulk RFQ Guard.\n"
                    f"Причина: {rfq_reason}\n\n"
                    f"Контакты: {contact_email} {contact_phone}\n"
                    f"Запрос: {lead_title}\n"
                    f"Фрагмент текста: {email_desc[:400]}"
                ),
                "RESPONSIBLE_ID": USER_ARTEM, "COMPLETED": "N"
            }
        })
        print(f"  [B24] Создано контрольное дело CRM_TODO на Артема (Сделка и Задача снабжению НЕ созданы)")

        # Запись и обогащение в 1С:УНФ
        from check_contractor import format_onec_comment, write_to_onec
        onec_comment_str = format_onec_comment({"classification": classification, "dadata": dadata_info, "saby": saby_info}) if classification else ""
        
        all_tags = set(contractor_tags)
        if is_reseller:
            all_tags.add("Перепродажники")
        tag_rows = []
        for idx, t_name in enumerate(all_tags, start=1):
            t_guid = TAG_MAP_1C.get(t_name) or TAG_IDS_1C.get(t_name)
            if t_guid:
                tag_rows.append({"LineNumber": str(idx), "Тег": t_guid, "Тег_Key": t_guid})

        if not is_buyer and not lead_1c:
            lead_payload = {
                "Description": company_title,
                "НаименованиеКомпании": company_title,
                "Тема": f"ИНН: {inn} (Контроль лида)" if inn else f"{company_title} (Контроль лида)",
                "Вид": "ПервичноеОбращение",
                "Ответственный_Key": ARTEM_RESPONSIBLE_1C,
                "ИсточникПривлечения_Key": SOURCE_SITE_LV_1C,
                "СостояниеЛида_Key": "0c989b06-70c5-11ed-b990-f01898a67170",
                "Комментарий": onec_comment_str
            }
            r_post_1c = requests.post(f"{ONEC_BASE}/Catalog_Лиды?$format=json", json=lead_payload, auth=ONEC_AUTH_WRITE, timeout=12)
            if r_post_1c.status_code in (200, 201):
                new_lead_guid = r_post_1c.json().get("Ref_Key")
                print(f"  [1C] Лид зафиксирован в 1С:УНФ (GUID {new_lead_guid}, Теги: {list(all_tags)})")
                ci_rows = []
                if contact_email:
                    ci_rows.append({"LineNumber": "1", "Тип": "АдресЭлектроннойПочты", "Вид_Key": CI_EMAIL, "Представление": contact_email, "АдресЭП": contact_email, "АдресЭПДляПоиска": contact_email})
                if contact_phone:
                    ci_rows.append({"LineNumber": str(len(ci_rows) + 1), "Тип": "Телефон", "Вид_Key": CI_PHONE, "Представление": contact_phone})
                if ci_rows:
                    requests.patch(f"{ONEC_BASE}/Catalog_Лиды(guid'{new_lead_guid}')?$format=json", json={"КонтактнаяИнформация": ci_rows}, auth=ONEC_AUTH_WRITE, timeout=12)
                write_to_onec(inn=inn, one_c_guid=new_lead_guid, summary_text=onec_comment_str, tags=classification, dry_run=False)
                if contact_email:
                    link_1c_events_and_address_book(contact_email, new_lead_guid, company_title)
            else:
                print(f"  [1C-WARN] Ошибка создания лида в 1С: {r_post_1c.status_code} - {r_post_1c.text[:200]}")
        else:
            existing_1c_guid = (lead_1c and lead_1c.get('Ref_Key')) or (ca_1c and ca_1c.get('Ref_Key'))
            if existing_1c_guid:
                write_to_onec(inn=inn, one_c_guid=existing_1c_guid, summary_text=onec_comment_str, tags=classification, dry_run=False)
                print(f"  [1C] Существующая карточка 1С ({existing_1c_guid}) обогащена досье СБИС и тегами.")

        verify_lead_processing_result(deal_id=None, contact_id=cnt_id, company_id=cid, task_id=None, expected_phone=contact_phone)
        return {"lead_id": lead_id, "branch": "Ambiguous / Reseller Guard", "company_id": cid, "contact_id": cnt_id, "reason": rfq_reason}

    # ---------------- ВЕТКА А: Однозначная заявка (Clear RFQ) ----------------
    # Извлечение параметров ТЗ
    rfq_details = extract_rfq_procurement_details(lead_title, email_subject, email_desc)
    cn_nomenclature = rfq_details.get("cn_nomenclature") or translate_nomenclature_to_chinese(lead_title, email_subject, email_desc)
    clean_company = re.sub(r'[«»"“”\']', '', company_title).strip()
    title_naming = f"{company_title}, {cn_nomenclature}"

    # Фильтрация вложений: Inquiry-Only Attachment Guard
    supply_disk_ids = []
    clean_attachments = []
    for fid, fname in lead_file_ids:
        if not is_technical_inquiry_file(fname):
            print(f"  [HYGIENE-GUARD] Файл '{fname}' отсеян (не относится к техническому ТЗ / юр. документ РФ / графика подписи)")
            continue
        clean_attachments.append((fid, fname))

    if dry_run:
        print(f"\n[DRY-RUN] План действий для Ветки А:")
        print(f"  - Сделка: '{title_naming}' (Стадия: PREPARATION)")
        print(f"  - Задача снабжению: Азат (user/{USER_AZAT}), Группа 14, Дедлайн: {deadline_plan}")
        print(f"  - Чистых вложений для Китая: {len(clean_attachments)}")
        print(f"  - Почтовый автоответ Шаблон № 66: {'ДА' if (contact_email and send_reply) else 'НЕТ'}")
        print(f"  - 1С:УНФ: {'Обновление тегов' if (is_buyer or lead_1c) else 'Создание Лида + Контакта'}")
        return {"lead_id": lead_id, "branch": "Clear RFQ", "title_naming": title_naming, "deadline": deadline_plan}

    # Боевое обогащение сущностей B24
    res_comp = enrich_or_create_b24_company(company_title, inn=inn, address=address, phone=contact_phone, email=contact_email, assigned_by_id=assigned_by_id)
    cid = res_comp["id"]
    res_cnt = enrich_or_create_b24_contact(contact_name, contact_email, phone=contact_phone, company_id=cid, post=contact_post, assigned_by_id=assigned_by_id)
    cnt_id = res_cnt["id"]

    # Обогащение Компании и Лида Б24 скорингом СБИС и закрепленным комментарием
    if scoring_summary_text:
        try:
            from check_contractor import write_to_bitrix24
            write_to_bitrix24(b24_company_id=cid, b24_lead_id=lead_id, summary_text=scoring_summary_text, dry_run=False)
        except Exception as e:
            print(f"  [B24-WARN] Не удалось обогатить карточки в Б24: {e}")

    # Создание Сделки в стадии PREPARATION
    deal_id = create_b24_deal(title_naming, cid, cnt_id, lead_id=lead_id, assigned_by_id=assigned_by_id, stage_id="PREPARATION")
    print(f"  [B24] Создана Сделка #{deal_id} в стадии PREPARATION («Расчет КП»)")
    
    # Тройное связывание дел-писем
    bind_lead_activities_triple(lead_id, deal_id, contact_id=cnt_id, company_id=cid, contact_email=contact_email)

    # Загрузка чистых вложений на Диск группы 14
    for fid, fname in clean_attachments:
        df = call_b24("disk.file.get", {"id": fid})
        dl_url = df.get("DOWNLOAD_URL") if df else None
        if dl_url:
            try:
                r_dl = requests.get(dl_url, timeout=25)
                if r_dl.status_code == 200:
                    tmp_p = os.path.join(os.environ.get("TEMP", r"C:\Temp"), fname)
                    with open(tmp_p, "wb") as f_tmp:
                        f_tmp.write(r_dl.content)
                    uploaded_id = upload_file_to_b24_disk(tmp_p, FOLDER_CHINA_SUPPLY_DISK)
                    if uploaded_id:
                        supply_disk_ids.append(uploaded_id)
                    if os.path.exists(tmp_p):
                        os.remove(tmp_p)
            except Exception as e:
                print(f"    [WARN] Ошибка загрузки файла {fname}: {e}")

    # Формирование описания задачи и ссылок на вложения (Inquiry-Only Attachment Guard)
    if supply_disk_ids:
        download_links_chat = "\n".join([f"- [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{fid}/]Вложение {fid}[/URL]" for fid in supply_disk_ids])
        attachments_task_block = f"\n\n[B]ВЛОЖЕНИЯ И ЧЕРТЕЖИ / 附件及图纸:[/B]\nФайлы запроса прикреплены к задаче и загружены на Диск группы 14 ({len(supply_disk_ids)} шт.):\n{download_links_chat}"
    else:
        download_links_chat = ""
        attachments_task_block = ""

    equiv_text_ru_cn = "ДА / 可推荐同等参数国内替代品 (Заказчик прямо разрешил качественный аналог / or an equivalent)" if rfq_details.get("equivalents_allowed") else "СТРОГО ОРИГИНАЛ / 仅限原装正品 (Аналоги не запрашивались)"

    task_description = (
        f"[B]ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА ЗАКУПКУ / 采购技术要求[/B]\n"
        f"--------------------------------------------------\n"
        f"• Сделка / 商机: [URL=https://b24-g4wfjq.bitrix24.ru/crm/deal/details/{deal_id}/]Сделка #{deal_id}[/URL]\n"
        f"• Оборудование / 设备名称: {cn_nomenclature}\n"
        f"• Бренд / 品牌: {rfq_details.get('brand', 'Hydac')}\n"
        f"• Модель / 型号: {rfq_details.get('model', 'VD 8 C.0')}\n"
        f"• Количество / 数量: {rfq_details.get('quantity', '1 шт. (1 unit / 1台)')}\n"
        f"• Допустимость аналога / 同等替代品: [B]{equiv_text_ru_cn}[/B]\n\n"
        f"[B]ОРИГИНАЛЬНЫЙ ТЕКСТ ЗАПРОСА КЛИЕНТА / 客户原始询价:[/B]\n"
        f"{rfq_details.get('clean_inquiry', email_desc[:600])}"
        f"{attachments_task_block}"
    )

    # Создание задачи снабжению Азату (user/20) с полным DESCRIPTION
    task_id = create_b24_supply_task(
        title=title_naming,
        deal_id=deal_id,
        description=task_description,
        responsible_id=USER_AZAT,
        group_id=GROUP_CHINA_SUPPLY,
        deadline_days=4,
        deadline_today=deadline_today,
        file_ids=supply_disk_ids
    )
    print(f"  [B24] Создана Задача #{task_id} (Ответственный: Азат, Дедлайн: {deadline_plan})")

    # Двуязычный комментарий в чат задачи для Азата (China Supply Anonymity Guard)
    bilingual_comment = build_supply_task_chat_message(
        azat_id=USER_AZAT,
        cn_nomenclature=cn_nomenclature,
        brand=rfq_details.get('brand', 'Hydac'),
        model=rfq_details.get('model', 'VD 8 C.0'),
        quantity=rfq_details.get('quantity', '1台 (1 unit)'),
        equivalents_allowed=rfq_details.get('equivalents_allowed', False),
        download_links_chat=download_links_chat,
        clean_inquiry=rfq_details.get('clean_inquiry', email_desc[:600])
    )
    send_b24_task_chat_message(task_id, bilingual_comment)

    # Автоответ Шаблон № 66 клиенту
    if contact_email and send_reply:
        send_template_66_reply(
            to_email=contact_email,
            original_subject=email_subject or lead_title,
            assigned_user_id=assigned_by_id,
            message_id_ref=email_message_id,
            is_clear_rfq_flag=True
        )

    # Отметка входящего дела-письма как прочитанного
    for a in email_acts:
        call_b24("crm.activity.update", {"id": a.get("ID"), "fields": {"COMPLETED": "Y", "STATUS": 2}})

    # Синхронизация и обогащение в 1С:УНФ
    from check_contractor import format_onec_comment, write_to_onec
    onec_comment_str = format_onec_comment({"classification": classification, "dadata": dadata_info, "saby": saby_info}) if classification else ""
    
    tag_rows = []
    for idx, t_name in enumerate(set(contractor_tags), start=1):
        t_guid = TAG_MAP_1C.get(t_name) or TAG_IDS_1C.get(t_name)
        if t_guid:
            tag_rows.append({"LineNumber": str(idx), "Тег": t_guid, "Тег_Key": t_guid})

    new_lead_guid = None
    if not is_buyer and not lead_1c:
        lead_payload = {
            "Description": company_title,
            "НаименованиеКомпании": company_title,
            "Тема": f"ИНН: {inn} (Сделка #{deal_id})" if inn else f"{company_title} (Сделка #{deal_id})",
            "Вид": "ПервичноеОбращение",
            "Ответственный_Key": ARTEM_RESPONSIBLE_1C,
            "ИсточникПривлечения_Key": SOURCE_SITE_LV_1C,
            "СостояниеЛида_Key": "0c989b06-70c5-11ed-b990-f01898a67170",
            "Комментарий": onec_comment_str
        }
        r_lead = requests.post(f"{ONEC_BASE}/Catalog_Лиды?$format=json", json=lead_payload, auth=ONEC_AUTH_WRITE, timeout=12)
        if r_lead.status_code in (200, 201):
            new_lead_guid = r_lead.json().get("Ref_Key")
            print(f"  [1C] Создан Лид в 1С:УНФ (GUID {new_lead_guid}, Теги: {list(set(contractor_tags))})")
            ci_rows = []
            if contact_email:
                ci_rows.append({"LineNumber": "1", "Тип": "АдресЭлектроннойПочты", "Вид_Key": CI_EMAIL, "Представление": contact_email, "АдресЭП": contact_email, "АдресЭПДляПоиска": contact_email})
            if contact_phone:
                ci_rows.append({"LineNumber": str(len(ci_rows) + 1), "Тип": "Телефон", "Вид_Key": CI_PHONE, "Представление": contact_phone})
            if ci_rows:
                requests.patch(f"{ONEC_BASE}/Catalog_Лиды(guid'{new_lead_guid}')?$format=json", json={"КонтактнаяИнформация": ci_rows}, auth=ONEC_AUTH_WRITE, timeout=12)
            write_to_onec(inn=inn, one_c_guid=new_lead_guid, summary_text=onec_comment_str, tags=classification, dry_run=False)
            if contact_email:
                link_1c_events_and_address_book(contact_email, new_lead_guid, company_title)
        else:
            print(f"  [1C-WARN] Ошибка создания лида в 1С: {r_lead.status_code} - {r_lead.text[:200]}")
    else:
        existing_1c_guid = (lead_1c and lead_1c.get('Ref_Key')) or (ca_1c and ca_1c.get('Ref_Key'))
        if existing_1c_guid:
            write_to_onec(inn=inn, one_c_guid=existing_1c_guid, summary_text=onec_comment_str, tags=classification, dry_run=False)
            print(f"  [1C] Существующая карточка 1С ({existing_1c_guid}) обогащена досье СБИС и тегами.")

    # Конвертация Лида в Битрикс24
    call_b24("crm.lead.update", {
        "id": lead_id,
        "fields": {
            "STATUS_ID": "CONVERTED",
            "COMPANY_ID": cid,
            "CONTACT_ID": cnt_id
        }
    })
    print(f"  [B24] Лид #{lead_id} успешно сконвертирован (STATUS: CONVERTED)")

    verify_lead_processing_result(deal_id=deal_id, contact_id=cnt_id, company_id=cid, task_id=task_id, expected_phone=contact_phone)

    return {
        "lead_id": lead_id,
        "deal_id": deal_id,
        "task_id": task_id,
        "company": company_title,
        "title_naming": title_naming,
        "deadline": deadline_plan
    }

# ----------------------------------------------------------------------
# CLI Interface
# ----------------------------------------------------------------------
def inspect_lead(lead_id: int):
    lead = call_b24("crm.lead.get", {"id": lead_id})
    if not lead:
        print(f"[ERROR] Лид {lead_id} не найден в Битрикс24")
        return None
    acts = call_b24("crm.activity.list", {"filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lead_id}}) or []
    print(f"\n" + "="*75)
    print(f">>> [ИНСПЕКЦИЯ ЛИДА #{lead_id}]")
    print(f"="*75)
    print(f"TITLE: {lead.get('TITLE')}")
    print(f"COMPANY_TITLE: {lead.get('COMPANY_TITLE')}")
    print(f"NAME / LAST_NAME: {lead.get('NAME')} {lead.get('LAST_NAME')}")
    print(f"EMAIL: {lead.get('EMAIL')}")
    print(f"PHONE: {lead.get('PHONE')}")
    print(f"STATUS_ID: {lead.get('STATUS_ID')}")
    print(f"ASSIGNED_BY_ID: {lead.get('ASSIGNED_BY_ID')}")
    print(f"COMMENTS: {lead.get('COMMENTS')}")
    print(f"\n--- Активности Лида ({len(acts)}) ---")
    for a in acts:
        aid = a.get('ID')
        atype = a.get('PROVIDER_ID') or a.get('TYPE_ID')
        asubj = a.get('SUBJECT')
        print(f"  [Дело #{aid}] {atype} | {asubj}")
    print("="*75 + "\n")
    return lead

def repair_previously_processed_lead(lead_id: int, dry_run: bool = False):
    print(f"\n=== ЗАПУСК ВОССТАНОВЛЕНИЯ И ИСПРАВЛЕНИЯ ЛИДА #{lead_id} (Режим: {'DRY-RUN' if dry_run else 'БОЕВОЙ'}) ===")
    lead = call_b24("crm.lead.get", {"id": lead_id})
    if not lead:
        print(f"[ERROR] Лид #{lead_id} не найден в Битрикс24")
        return False

    company_id = lead.get("COMPANY_ID")
    contact_id = lead.get("CONTACT_ID")
    lead_title = lead.get("TITLE") or ""
    lead_comments = lead.get("COMMENTS") or ""

    # Поиск сделки
    deals = call_b24("crm.deal.list", {"filter": {"LEAD_ID": lead_id}, "select": ["ID", "TITLE", "COMPANY_ID", "CONTACT_ID"]}) or []
    deal_id = deals[0]["ID"] if deals else None
    if not deal_id:
        if company_id:
            c_deals = call_b24("crm.deal.list", {"filter": {"COMPANY_ID": company_id}, "order": {"ID": "DESC"}, "limit": 1}) or []
            deal_id = c_deals[0]["ID"] if c_deals else None

    # Поиск задачи
    task_id = None
    if deal_id:
        tasks_res = call_b24("tasks.task.list", {"filter": {"UF_CRM_TASK": f"D_{deal_id}", "GROUP_ID": GROUP_CHINA_SUPPLY}, "select": ["ID", "TITLE", "DESCRIPTION"]})
        t_list = tasks_res.get("tasks", []) if isinstance(tasks_res, dict) else []
        task_id = t_list[0]["id"] if t_list else None

    # Извлечение дел-писем
    acts = call_b24("crm.activity.list", {"filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lead_id}}) or []
    if not acts and deal_id:
        acts = call_b24("crm.activity.list", {"filter": {"OWNER_TYPE_ID": 2, "OWNER_ID": deal_id}}) or []
    
    email_acts = [a for a in acts if a.get("PROVIDER_ID") == "CRM_EMAIL" or str(a.get("TYPE_ID")) == "4"]
    main_act = email_acts[0] if email_acts else (acts[0] if acts else {})
    email_desc = main_act.get("DESCRIPTION", "")
    email_subject = main_act.get("SUBJECT", "")

    # Извлечение контакта email
    contact_email = None
    if contact_id:
        cnt_data = call_b24("crm.contact.get", {"id": contact_id}) or {}
        emails = cnt_data.get("EMAIL", []) if isinstance(cnt_data, dict) else []
        if emails:
            contact_email = emails[0].get("VALUE")
    if not contact_email and main_act:
        from_str = main_act.get("SETTINGS", {}).get("EMAIL_META", {}).get("from", "")
        m_em = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_str)
        if m_em:
            contact_email = m_em.group(0)

    # Извлечение подписи и контактов
    sig_info = extract_phone_and_signature_details(f"{email_desc} {lead_comments}")
    extracted_phone = sig_info.get("phone", "")
    extracted_post = sig_info.get("post", "")
    extracted_website = sig_info.get("website", "")

    # Извлечение параметров ТЗ
    rfq = extract_rfq_procurement_details(lead_title, email_subject, email_desc)
    cn_nomenclature = rfq.get("cn_nomenclature", "")
    brand = rfq.get("brand", "")
    model = rfq.get("model", "")
    quantity = rfq.get("quantity", "1 шт. (1 unit / 1台)")
    equivalents_allowed = rfq.get("equivalents_allowed", False)
    clean_inquiry = rfq.get("clean_inquiry", "")

    print(f"Связанные сущности: Сделка #{deal_id}, Компания #{company_id}, Контакт #{contact_id}, Задача #{task_id}")
    print(f"Извлеченный телефон: '{extracted_phone}', Должность: '{extracted_post}'")
    print(f"Параметры ТЗ: {cn_nomenclature} | Кол-во: {quantity} | Аналог: {'ДА' if equivalents_allowed else 'НЕТ'}")

    if dry_run:
        print("\n[DRY-RUN] План исправления:")
        print(f"  1. Привязать {len(acts)} дел к Сделке #{deal_id}, Контакту #{contact_id}, Компании #{company_id}")
        print(f"  2. Записать телефон '{extracted_phone}' в Контакт #{contact_id} и Компанию #{company_id}")
        print(f"  3. Обновить описание Задачи #{task_id} подробным ТЗ")
        print(f"  4. Отправить корректирующее сообщение в чат Задачи #{task_id}")
        return True

    # 1. Тройная привязка дел
    bind_count = bind_lead_activities_triple(
        lead_id=lead_id,
        deal_id=deal_id,
        contact_id=contact_id,
        company_id=company_id,
        contact_email=contact_email
    )
    print(f"  [B24] Привязано {bind_count} дел к Сделке #{deal_id}, Контакту #{contact_id}, Компании #{company_id}")

    # 2. Обновление Контакта и Компании
    if contact_id and extracted_phone:
        cnt_info = call_b24("crm.contact.get", {"id": contact_id})
        upd_cnt = {}
        if not cnt_info.get("PHONE"):
            upd_cnt["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": extracted_phone}]
        if extracted_post and not cnt_info.get("POST"):
            upd_cnt["POST"] = extracted_post
        if upd_cnt:
            call_b24("crm.contact.update", {"id": contact_id, "fields": upd_cnt})
            print(f"  [B24] Контакт #{contact_id} обогащен телефоном и должностью: {upd_cnt}")

    if company_id and extracted_phone:
        cmp_info = call_b24("crm.company.get", {"id": company_id})
        upd_cmp = {}
        if not cmp_info.get("PHONE"):
            upd_cmp["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": extracted_phone}]
        if extracted_website and not cmp_info.get("WEB"):
            upd_cmp["WEB"] = [{"VALUE_TYPE": "WORK", "VALUE": extracted_website}]
        if upd_cmp:
            call_b24("crm.company.update", {"id": company_id, "fields": upd_cmp})
            print(f"  [B24] Компания #{company_id} обогащена телефоном: {upd_cmp}")

    # 3. Обновление Задачи Азата
    if task_id:
        equiv_text_ru_cn = "ДА / 可推荐同等参数国内替代品 (Заказчик прямо разрешил качественный аналог / or an equivalent)" if equivalents_allowed else "СТРОГО ОРИГИНАЛ / 仅限原装正品 (Аналоги не запрашивались)"
        cmp_info = call_b24("crm.company.get", {"id": company_id}) if company_id else {}
        company_title = (cmp_info.get("TITLE") if cmp_info else lead_title) or "ООО \"ТЕХКРАН\""
        
        task_description = (
            f"[B]ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА ЗАКУПКУ / 采购技术要求[/B]\n"
            f"--------------------------------------------------\n"
            f"• Сделка / 商机: [URL=https://b24-g4wfjq.bitrix24.ru/crm/deal/details/{deal_id}/]Сделка #{deal_id}[/URL]\n"
            f"• Оборудование / 设备名称: {cn_nomenclature}\n"
            f"• Бренд / 品牌: {brand}\n"
            f"• Модель / 型号: {model}\n"
            f"• Количество / 数量: {quantity}\n"
            f"• Допустимость аналога / 同等替代品: [B]{equiv_text_ru_cn}[/B]\n\n"
            f"[B]ОРИГИНАЛЬНЫЙ ТЕКСТ ЗАПРОСА КЛИЕНТА / 客户原始询价:[/B]\n"
            f"{clean_inquiry}"
        )
        call_b24("tasks.task.update", {
            "taskId": task_id,
            "fields": {
                "DESCRIPTION": task_description,
                "UF_CRM_TASK": [f"D_{deal_id}"]
            }
        })
        print(f"  [B24] Задача #{task_id} обновлена полным структурированным ТЗ и привязана строго к Сделке #{deal_id}")

        chat_msg = build_supply_task_chat_message(
            azat_id=USER_AZAT,
            cn_nomenclature=cn_nomenclature,
            brand=brand,
            model=model,
            quantity=quantity,
            equivalents_allowed=equivalents_allowed,
            download_links_chat="",
            clean_inquiry=clean_inquiry
        )
        send_b24_task_chat_message(task_id, chat_msg)
        print(f"  [B24] В чат Задачи #{task_id} отправлено рабочее ТЗ снабжению")

    # 4. Обновление 1С:УНФ
    if extracted_phone:
        try:
            lead_1c_found = check_1c_lead(inn="7452153365", name=lead_title)
            if lead_1c_found:
                guid_1c = lead_1c_found.get("Ref_Key")
                ci_rows = lead_1c_found.get("КонтактнаяИнформация", [])
                has_phone = any(r.get("Тип") == "Телефон" for r in ci_rows)
                if not has_phone and guid_1c:
                    ci_rows.append({
                        "LineNumber": str(len(ci_rows) + 1),
                        "Тип": "Телефон",
                        "Вид_Key": CI_PHONE,
                        "Представление": extracted_phone,
                        "НомерТелефона": extracted_phone
                    })
                    q_guid = urllib.parse.quote(f"guid'{guid_1c}'")
                    r_patch_1c = requests.patch(f"{ONEC_BASE}/Catalog_Лиды({q_guid})?$format=json", json={"КонтактнаяИнформация": ci_rows}, auth=ONEC_AUTH_WRITE, timeout=12)
                    if r_patch_1c.status_code in (200, 204):
                        print(f"  [1C] В карточку лида 1С ({guid_1c}) добавлен телефон '{extracted_phone}'")
                    else:
                        print(f"  [1C-WARN] Ответ 1С при добавлении телефона: {r_patch_1c.status_code}")
        except Exception as e:
            print(f"  [1C-WARN] Не удалось обновить телефон в 1С: {e}")

    # 5. Проверка результата
    verify_lead_processing_result(
        deal_id=deal_id,
        contact_id=contact_id,
        company_id=company_id,
        task_id=task_id,
        expected_phone=extracted_phone
    )
    return True

def main():
    parser = argparse.ArgumentParser(description="Канонический конвейер обработки входящих лидов Битрикс24 и 1С:УНФ")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Предпросмотр действий без записи в CRM и 1С")
    parser.add_argument("--inspect", action="store_true", default=False, help="Инспекция лида и его вложений без выполнения")
    parser.add_argument("--repair-lead", type=int, help="Специальный режим: перепривязать письма, обновить телефон, ТЗ задачи и проверить результат для ранее обработанного лида")
    parser.add_argument("--deadline-today", action="store_true", default=False, help="Установить дедлайн задачи на сегодня к 18:00")
    parser.add_argument("--lead-id", type=int, help="ID конкретного лида для точечной обработки")
    parser.add_argument("--leads", type=int, nargs="+", help="Список ID лидов через пробел")
    parser.add_argument("--mailbox", type=str, help="Фильтрация лидов по почтовому ящику (например, sales@longwang.ru)")
    parser.add_argument("--limit", type=int, default=10, help="Ограничение количества обрабатываемых лидов")
    parser.add_argument("--no-reply", action="store_true", default=False, help="Отключить отправку автоответа Шаблон № 66")
    parser.add_argument("--force", action="store_true", default=False, help="Принудительная обработка даже если лид в статусе CONVERTED")
    parser.add_argument("--csv", "--csv-file", dest="csv_file", type=str, help="Путь к выгруженному CSV-файлу со списком лидов")
    args = parser.parse_args()

    dry_run = args.dry_run

    if args.repair_lead:
        repair_previously_processed_lead(args.repair_lead, dry_run=dry_run)
        return

    targets = []
    if args.lead_id:
        targets = [args.lead_id]
    elif args.leads:
        targets = args.leads
    elif args.csv_file:
        import csv
        targets = []
        with open(args.csv_file, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            content = f.read()
            delim = ";" if ";" in content[:200] else ","
            import io
            reader = csv.DictReader(io.StringIO(content), delimiter=delim)
            for row in reader:
                lid_val = row.get("ID") or row.get("id") or (list(row.values())[0] if row else None)
                if lid_val and str(lid_val).strip().isdigit():
                    targets.append(int(str(lid_val).strip()))
    else:
        # Автоматический сбор новых необработанных лидов
        filt = {"STATUS_ID": "NEW"}
        lead_list = call_b24("crm.lead.list", {
            "filter": filt,
            "order": {"ID": "DESC"},
            "select": ["ID", "TITLE", "STATUS_ID"],
            "limit": args.limit
        }) or []
        targets = [int(l["ID"]) for l in lead_list]
        if not targets:
            print("Новых необработанных лидов в статусе NEW не обнаружено.")
            return

    if args.inspect:
        for lid in targets:
            inspect_lead(lid)
        return

    print(f"=== ЗАПУСК КАНОНИЧЕСКОГО КОНВЕЙЕРА ЛИДОВ (Режим: {'DRY-RUN' if dry_run else 'БОЕВОЙ'}) ===")
    print(f"Целевые лиды: {targets}\n")

    results = []
    for lid in targets:
        res = process_single_lead(
            lead_id=lid,
            dry_run=dry_run,
            deadline_today=args.deadline_today,
            send_reply=(not args.no_reply),
            force=args.force
        )
        results.append(res)

    print("\n" + "="*75)
    print(">>> ИТОГИ ВЫПОЛНЕНИЯ КОНВЕЙЕРА:")
    for r in results:
        if isinstance(r, dict) and "lead_id" in r:
            lid = r.get("lead_id")
            comp = r.get("company", "")
            title = r.get("title_naming", "")
            status = r.get("status") or r.get("branch") or ("OK" if not dry_run else "DRY-RUN PLAN")
            print(f"- Лид #{lid}: {comp} [{status}] -> '{title}'")
            if not dry_run and "deal_id" in r:
                print(f"  Сделка #{r.get('deal_id')}, Задача #{r.get('task_id')}")
    print("="*75)

if __name__ == "__main__":
    main()
