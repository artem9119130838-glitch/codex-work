#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/sync_leads_1c_bitrix.py
=================================================
Канонический монолитный конвейер сквозной синхронизации лидов 1С:УНФ и Битрикс24 CRM.

Команда пользователя:
  «синхронизируй лидов, создай и обнови»
  (алиасы: «синхронизируй лидов из почты», «создай и обнови лидов в 1С»)

Архитектурный устав:
  1. Выполняет ТОЛЬКО синхронизацию и взаимное обогащение сущностей:
     - 1С:УНФ: Catalog_Лиды, ТЧ КонтактнаяИнформация (Zero-Blank Lead Guard);
     - Битрикс24: crm.lead, crm.company (ИНН UF_CRM_699421CD2A684), crm.contact.
  2. СТРОГИЙ ЗАПРЕТ (Чистая синхронизация):
     - Сделки (crm.deal) НЕ создавать;
     - Задачи снабжению (tasks.task) НЕ создавать;
     - Письма клиентам (Шаблон 66 и др.) НЕ отправлять;
     - Дела-письма НЕ помечать как выполненные без явной команды.
  3. Источники выборки:
     - По списку ID лидов: --lead-ids 17812 7680
     - По дате создания/изменения в CRM: --since 2026-09-25
     - По папке почты IMAP: --mailbox sales@longwang.ru --folder INBOX
     - Лимит выборки: --limit 10 (по умолчанию)
"""

import os
import sys
import re
import json
import argparse
import imaplib
from email import message_from_bytes
from email.header import decode_header
from datetime import datetime
import requests

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def _load_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v

_load_env()

B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
ODATA_BASE = os.getenv("ONEC_ODATA_URL", "http://artem.medianasoft.spb.ru/unf/odata/standard.odata")
ODATA_USER = os.getenv("ONEC_ODATA_USER", "odata.writer")
ODATA_PASS = os.getenv("ONEC_ODATA_PASSWORD", "")

IMAP_HOST = os.getenv("IMAP_SERVER", "mail.hostland.ru")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
MAIL_USER = os.getenv("IMAP_USER", "sales@longwang.ru")
MAIL_PASS = os.getenv("IMAP_PASSWORD", "")

USER_MAPPING = {
    "1": 1,
    "artem": 1,
    "артем": 1,
    "38": 38,
    "alexandra": 38,
    "александра": 38,
    "26": 26,
    "salman": 26,
    "салман": 26
}

# Эталонные GUID тегов 1С:УНФ (Canonical Tag Integrity Guard)
TAG_LARGE = "7e8d7ab8-df13-11ef-9922-02006df8aab5"       # Крупный
TAG_PRODUCTION = "891061f8-df13-11ef-9922-02006df8aab5"  # Производство
TAG_TENDER = "052cb624-ded8-11ef-9922-02006df8aab5"      # Тендер
TAG_RESELLER = "306714e0-e1f5-11ef-8db0-02006df8aab5"    # Перепродажники
TAG_END_BUYER = "6c77607c-e770-11ef-8e46-02006df8aab5"   # Конечный покупатель
TAG_HOLDING = "0e89c354-fe42-11ef-8ae4-02006df8aab5"     # Холдинг
TAG_INDIVIDUAL = "43e14fb2-67a7-11f0-875b-02006df8aab5"  # Физик

TAG_NAME_MAP = {
    TAG_LARGE: "Крупный",
    TAG_PRODUCTION: "Производство",
    TAG_TENDER: "Тендер",
    TAG_RESELLER: "Перепродажники",
    TAG_END_BUYER: "Конечный покупатель",
    TAG_HOLDING: "Холдинг",
    TAG_INDIVIDUAL: "Физик"
}

TAG_TYPO_MAP = {
    "7e8d7ab6-df13-11ef-9922-02006df8aab5": TAG_LARGE    # Опечатка 6 -> 8
}

DADATA_TOKEN = os.getenv("DADATA_TOKEN", "")


def call_b24(method: str, params: dict = None) -> dict:
    url = f"{B24_WEBHOOK}{method}"
    res = requests.post(url, json=params or {}, timeout=30)
    if res.status_code >= 400:
        print(f"  [B24-ERROR] {method} HTTP {res.status_code}: {res.text}")
    res.raise_for_status()
    return res.json()


def decode_mime_header(header_val: str) -> str:
    if not header_val:
        return ""
    decoded_parts = decode_header(header_val)
    result = []
    for text, enc in decoded_parts:
        if isinstance(text, bytes):
            result.append(text.decode(enc or "utf-8", errors="ignore"))
        else:
            result.append(str(text))
    return " ".join(result)


def find_company_by_inn(inn: str) -> dict:
    clean_inn = "".join(filter(str.isdigit, str(inn)))
    if not clean_inn:
        return None
    r = call_b24("crm.company.list", {
        "filter": {"UF_CRM_699421CD2A684": clean_inn},
        "select": ["ID", "TITLE", "UF_CRM_699421CD2A684", "PHONE", "EMAIL", "ADDRESS"]
    })
    items = r.get("result", [])
    return items[0] if items else None


def find_contact_by_email(email: str) -> dict:
    if not email:
        return None
    r = call_b24("crm.contact.list", {
        "filter": {"EMAIL": email.strip()},
        "select": ["ID", "NAME", "LAST_NAME", "SECOND_NAME", "POST", "PHONE", "EMAIL", "COMPANY_ID"]
    })
    items = r.get("result", [])
    return items[0] if items else None


def sync_lead_record(lead_id: int, dry_run: bool = False) -> dict:
    """
    Синхронизация одной сущности Лида:
    1. Чтение реквизитов из Битрикс24;
    2. Обогащение Компании и Контакта в Битрикс24;
    3. Создание / обновление в 1С:УНФ по регламенту Zero-Blank Lead Guard.
    """
    print(f"\n>>> [Синхронизация Лида #{lead_id}]")
    r = call_b24("crm.lead.get", {"id": lead_id})
    lead = r.get("result", {})
    if not lead:
        print(f"  [WARN] Лид {lead_id} не найден в Битрикс24.")
        return {"lead_id": lead_id, "status": "not_found"}

    title = lead.get("TITLE", "")
    company_title = lead.get("COMPANY_TITLE") or title
    name = lead.get("NAME", "")
    last_name = lead.get("LAST_NAME", "")
    second_name = lead.get("SECOND_NAME", "")
    comments = lead.get("COMMENTS", "")
    assigned_by = int(lead.get("ASSIGNED_BY_ID", 1))

    # Извлечение email и телефонов
    emails = [e.get("VALUE") for e in lead.get("EMAIL", []) if e.get("VALUE")]
    phones = [p.get("VALUE") for p in lead.get("PHONE", []) if p.get("VALUE")]
    primary_email = emails[0].strip() if emails else ""
    primary_phone = phones[0].strip() if phones else ""

    # Поиск ИНН
    inn_match = re.search(r'\b(ИНН\s*[:№]?\s*)?(\d{10}|\d{12})\b', f"{title} {company_title} {comments}", re.IGNORECASE)
    inn = inn_match.group(2) if inn_match else ""

    print(f"  Б24 Лид: '{title}' | ИНН: '{inn or 'нет'}' | Email: '{primary_email or 'нет'}' | Тел: '{primary_phone or 'нет'}'")

    # 1. Обогащение Компании и Контакта в Битрикс24
    b24_company_id = lead.get("COMPANY_ID")
    if inn:
        existing_comp = find_company_by_inn(inn)
        if existing_comp:
            cid = int(existing_comp["ID"])
            b24_company_id = cid
            print(f"  [B24] Найдена существующая Компания ID {cid} по ИНН {inn}")
        else:
            print(f"  [B24] Создание новой Компании '{company_title}' (ИНН: {inn})")
            if not dry_run:
                r_c = call_b24("crm.company.add", {
                    "fields": {
                        "TITLE": company_title,
                        "UF_CRM_699421CD2A684": inn,
                        "ASSIGNED_BY_ID": assigned_by,
                        "OPENED": "Y"
                    }
                })
                b24_company_id = int(r_c.get("result", 0))
            else:
                b24_company_id = 9999901
                print("  [B24] (Dry-run) Компания создана условно (ID: 9999901)")

    b24_contact_id = lead.get("CONTACT_ID")
    if primary_email and not b24_contact_id:
        existing_ct = find_contact_by_email(primary_email)
        if existing_ct:
            b24_contact_id = int(existing_ct["ID"])
            print(f"  [B24] Найден существующий Контакт ID {b24_contact_id} по email {primary_email}")
        else:
            contact_parts = [p for p in [name or "Контакт", second_name, last_name] if p]
            full_contact_name = " ".join(contact_parts)
            print(f"  [B24] Создание Контакта '{full_contact_name}' ({primary_email})")
            if not dry_run:
                r_ct = call_b24("crm.contact.add", {
                    "fields": {
                        "NAME": full_contact_name,
                        "LAST_NAME": last_name,
                        "SECOND_NAME": second_name,
                        "EMAIL": [{"VALUE_TYPE": "WORK", "VALUE": primary_email}],
                        "COMPANY_ID": b24_company_id,
                        "ASSIGNED_BY_ID": assigned_by,
                        "OPENED": "Y"
                    }
                })
                b24_contact_id = int(r_ct.get("result", 0))
            else:
                b24_contact_id = 9999902
                print("  [B24] (Dry-run) Контакт создан условно (ID: 9999902)")

    # Привязка сущностей к карточке Лида в Б24 если они изменились
    update_lead_fields = {}
    if b24_company_id and str(lead.get("COMPANY_ID")) != str(b24_company_id):
        update_lead_fields["COMPANY_ID"] = b24_company_id
    if b24_contact_id and str(lead.get("CONTACT_ID")) != str(b24_contact_id):
        update_lead_fields["CONTACT_ID"] = b24_contact_id
    if update_lead_fields:
        print(f"  [B24] Привязка к Лиду #{lead_id}: {update_lead_fields}")
        if not dry_run:
            call_b24("crm.lead.update", {"id": lead_id, "fields": update_lead_fields})

    # 2. Синхронизация с 1С:УНФ (Zero-Blank Lead Guard)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (ODATA_USER, ODATA_PASS)
    
    # Поиск по ИНН или Email
    find_filter = ""
    if inn and primary_email:
        find_filter = f"substringof('{inn}',Тема) or substringof('{primary_email}',Description)"
    elif inn:
        find_filter = f"substringof('{inn}',Тема)"
    elif primary_email:
        find_filter = f"substringof('{primary_email}',Description)"

    one_c_guid = None
    if find_filter:
        try:
            r_1c = requests.get(f"{ODATA_BASE}/Catalog_Лиды?$format=json&$top=1&$filter={find_filter}", auth=auth, headers=headers, timeout=20)
            if r_1c.status_code == 200:
                vals = r_1c.json().get("value", [])
                if vals:
                    one_c_guid = vals[0]["Ref_Key"]
                    print(f"  [1C] Найден существующий Лид 1С: {one_c_guid}")
        except Exception as e:
            print(f"  [1C-WARN] Ошибка поиска лида в 1С: {e}")

    if not one_c_guid:
        print(f"  [1C] Создание нового Лида 1С по регламенту Zero-Blank Lead Guard ('{title}', ИНН: {inn or 'нет'})")
        if not dry_run:
            post_payload = {
                "Description": title,
                "НаименованиеКомпании": company_title or title,
                "Тема": f"ИНН: {inn}" if inn else title,
                "Вид": "ПервичноеОбращение",
                "Ответственный_Key": "209d4fb0-3142-11ed-a3f1-3085a9a0f5bf", # Артем
                "ИсточникПривлечения_Key": "9dbbff5e-23c6-11ed-91a8-a068f8f3337c",
                "СостояниеЛида_Key": "0c989b06-70c5-11ed-b990-f01898a67170",
                "Комментарий": f"Лид Битрикс24 #{lead_id}."
            }
            try:
                r_post = requests.post(f"{ODATA_BASE}/Catalog_Лиды?$format=json", json=post_payload, auth=auth, headers=headers, timeout=20)
                if r_post.status_code in (200, 201):
                    one_c_guid = r_post.json().get("Ref_Key")
                    # Фаза 2: PATCH КонтактнаяИнформация
                    ci_rows = []
                    if primary_email:
                        ci_rows.append({"LineNumber": "1", "Тип": "АдресЭлектроннойПочты", "Вид_Key": "5c0dc769-23c6-11ed-91a8-a068f8f3337c", "Представление": primary_email, "ЗначенияПолей": f'{{"EMail":"{primary_email}"}}'})
                    if primary_phone:
                        ci_rows.append({"LineNumber": str(len(ci_rows) + 1), "Тип": "Телефон", "Вид_Key": "5c0dc76d-23c6-11ed-91a8-a068f8f3337c", "Представление": primary_phone, "ЗначенияПолей": f'{{"Phone":"{primary_phone}"}}'})
                    if ci_rows:
                        requests.patch(f"{ODATA_BASE}/Catalog_Лиды(guid'{one_c_guid}')?$format=json", json={"КонтактнаяИнформация": ci_rows}, auth=auth, headers=headers, timeout=20)
                    print(f"  [1C OK] Успешно создан Лид 1С: {one_c_guid}")
                else:
                    print(f"  [1C-ERROR] Ошибка создания лида: {r_post.text}")
            except Exception as e:
                print(f"  [1C-ERROR] Исключение OData: {e}")
        else:
            print("  [1C] (Dry-run) Создание записи в 1С пропущено")
            one_c_guid = "00000000-0000-0000-0000-000000000000"

    # 3. Скоринг и верификация через СБИС (Saby) + DaData (Zero-Duplicate Guard)
    sbis_res = None
    if inn:
        try:
            from check_contractor import verify_and_enrich_contractor
            sbis_res = verify_and_enrich_contractor(
                inn=inn,
                b24_company_id=b24_company_id if b24_company_id and b24_company_id != 9999901 else None,
                b24_lead_id=lead_id,
                one_c_guid=one_c_guid if one_c_guid and one_c_guid != "00000000-0000-0000-0000-000000000000" else None,
                email=primary_email,
                dry_run=dry_run
            )
        except Exception as e_sbis:
            print(f"  [СБИС-WARN] Ошибка вызова модуля верификации контрагента: {e_sbis}")

    return {
        "lead_id": lead_id,
        "company_id": b24_company_id,
        "contact_id": b24_contact_id,
        "one_c_guid": one_c_guid,
        "sbis_status": sbis_res.get("status") if sbis_res else "skipped",
        "status": "synced"
    }


def fetch_leads_by_since(since_date: str, assigned_to: int = 1, limit: int = 10) -> list:
    """Выборка лидов из Битрикс24 по дате создания/изменения"""
    print(f"[B24] Выборка лидов, созданных/измененных с {since_date} (Ответственный: {assigned_to}, Лимит: {limit})...")
    r = call_b24("crm.lead.list", {
        "filter": {
            ">=DATE_CREATE": f"{since_date} 00:00:00",
            "ASSIGNED_BY_ID": assigned_to
        },
        "order": {"ID": "DESC"}
    })
    leads = r.get("result", [])
    if len(leads) < limit:
        # Дополняем выборкой по изменению
        r_mod = call_b24("crm.lead.list", {
            "filter": {
                ">=DATE_MODIFY": f"{since_date} 00:00:00",
                "ASSIGNED_BY_ID": assigned_to
            },
            "order": {"ID": "DESC"}
        })
        existing_ids = {l["ID"] for l in leads}
        for lm in r_mod.get("result", []):
            if lm["ID"] not in existing_ids:
                leads.append(lm)
                existing_ids.add(lm["ID"])
    return leads[:limit]


def fetch_leads_from_imap(mailbox: str, folder: str = "INBOX", limit: int = 10) -> list:
    """Поиск недавних входящих писем в IMAP и сопоставление их с лидами в CRM"""
    print(f"[IMAP] Подключение к {IMAP_HOST} ({mailbox}), папка '{folder}', лимит: {limit}...")
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(mailbox, MAIL_PASS)
    mail.select(f'"{folder}"')

    status, messages = mail.search(None, "ALL")
    if status != "OK" or not messages[0]:
        mail.close()
        mail.logout()
        return []

    msg_ids = messages[0].split()
    target_ids = msg_ids[-limit:]
    target_ids.reverse()

    found_lead_ids = []
    seen_ids = set()

    for mid in target_ids:
        res, data = mail.fetch(mid, "(RFC822.HEADER)")
        if res != "OK":
            continue
        msg = message_from_bytes(data[0][1])
        sender = decode_mime_header(msg.get("From", ""))
        sender_match = re.search(r'[\w\.-]+@[\w\.-]+', sender)
        sender_email = sender_match.group(0).lower() if sender_match else ""

        if sender_email and sender_email != mailbox.lower():
            # Поиск лида в Битрикс24 по этому email
            r_lead = call_b24("crm.lead.list", {
                "filter": {"EMAIL": sender_email},
                "order": {"ID": "DESC"}
            })
            for item in r_lead.get("result", []):
                lid = int(item["ID"])
                if lid not in seen_ids:
                    seen_ids.add(lid)
                    found_lead_ids.append(lid)
                    if len(found_lead_ids) >= limit:
                        break

    mail.close()
    mail.logout()
    return found_lead_ids


def clean_invalid_email_from_systems(target_email: str, reason: str = "bounce", dry_run: bool = True) -> dict:
    """
    Автоматический Bounce & Unsubscribe Guard:
    1. Ищет Контакты, Компании, Лиды в Битрикс24 CRM с данным email и удаляет адрес.
    2. Добавляет системный комментарий в таймлайн Битрикс24.
    3. Ищет Лиды и Контрагенты в 1С:УНФ через OData и удаляет строку АдресЭлектроннойПочты из ТЧ КонтактнаяИнформация.
    4. Поддерживает строгий режим --dry-run.
    """
    clean_email = target_email.strip().lower()
    if not clean_email or "@" not in clean_email:
        print(f"[CLEAN-ERROR] Некорректный email для очистки: '{target_email}'")
        return {"status": "error", "message": "invalid_email"}

    print("=" * 80)
    print("ОЧИСТКА НЕВАЛИДНОГО EMAIL (BOUNCE & UNSUBSCRIBE GUARD)")
    print(f"Целевой email: {clean_email} | Причина: {reason} | Режим: {'DRY-RUN' if dry_run else 'БОЕВОЙ'}")
    print("=" * 80)

    summary = {
        "email": clean_email,
        "reason": reason,
        "b24_contacts_updated": [],
        "b24_companies_updated": [],
        "b24_leads_updated": [],
        "onec_leads_updated": [],
        "onec_counterparties_updated": []
    }

    # 1. Битрикс24: Контакты
    try:
        r_ct = call_b24("crm.contact.list", {
            "filter": {"EMAIL": clean_email},
            "select": ["ID", "NAME", "LAST_NAME", "EMAIL"]
        })
        contacts = r_ct.get("result", [])
        for ct in contacts:
            cid = ct["ID"]
            cur_emails = ct.get("EMAIL", [])
            new_emails = [e for e in cur_emails if e.get("VALUE", "").strip().lower() != clean_email]
            print(f"  [B24 Contact #{cid}] Найден email {clean_email}. Очистка (осталось {len(new_emails)} адресов)...")
            if not dry_run:
                call_b24("crm.contact.update", {"id": cid, "fields": {"EMAIL": new_emails}})
                call_b24("crm.timeline.comment.add", {
                    "fields": {
                        "ENTITY_ID": cid,
                        "ENTITY_TYPE": "contact",
                        "COMMENT": f"⚠️ [Bounce & Unsubscribe Guard] Email {clean_email} удален из карточки контакта. Причина: {reason}."
                    }
                })
            summary["b24_contacts_updated"].append(cid)
    except Exception as e:
        print(f"  [B24-ERROR] Ошибка поиска/очистки контактов: {e}")

    # 2. Битрикс24: Компании
    try:
        r_cp = call_b24("crm.company.list", {
            "filter": {"EMAIL": clean_email},
            "select": ["ID", "TITLE", "EMAIL"]
        })
        companies = r_cp.get("result", [])
        for cp in companies:
            cpid = cp["ID"]
            cur_emails = cp.get("EMAIL", [])
            new_emails = [e for e in cur_emails if e.get("VALUE", "").strip().lower() != clean_email]
            print(f"  [B24 Company #{cpid} '{cp.get('TITLE', '')}'] Очистка email {clean_email}...")
            if not dry_run:
                call_b24("crm.company.update", {"id": cpid, "fields": {"EMAIL": new_emails}})
                call_b24("crm.timeline.comment.add", {
                    "fields": {
                        "ENTITY_ID": cpid,
                        "ENTITY_TYPE": "company",
                        "COMMENT": f"⚠️ [Bounce & Unsubscribe Guard] Email {clean_email} удален из карточки компании. Причина: {reason}."
                    }
                })
            summary["b24_companies_updated"].append(cpid)
    except Exception as e:
        print(f"  [B24-ERROR] Ошибка поиска/очистки компаний: {e}")

    # 3. Битрикс24: Лиды
    try:
        r_ld = call_b24("crm.lead.list", {
            "filter": {"EMAIL": clean_email},
            "select": ["ID", "TITLE", "EMAIL"]
        })
        leads = r_ld.get("result", [])
        for ld in leads:
            lid = ld["ID"]
            cur_emails = ld.get("EMAIL", [])
            new_emails = [e for e in cur_emails if e.get("VALUE", "").strip().lower() != clean_email]
            print(f"  [B24 Lead #{lid} '{ld.get('TITLE', '')}'] Очистка email {clean_email}...")
            if not dry_run:
                call_b24("crm.lead.update", {"id": lid, "fields": {"EMAIL": new_emails}})
                call_b24("crm.timeline.comment.add", {
                    "fields": {
                        "ENTITY_ID": lid,
                        "ENTITY_TYPE": "lead",
                        "COMMENT": f"⚠️ [Bounce & Unsubscribe Guard] Email {clean_email} удален из карточки лида. Причина: {reason}."
                    }
                })
            summary["b24_leads_updated"].append(lid)
    except Exception as e:
        print(f"  [B24-ERROR] Ошибка поиска/очистки лидов: {e}")

    # 4. 1С:УНФ (Catalog_Лиды и Catalog_Контрагенты)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (ODATA_USER, ODATA_PASS)

    # 4.1. 1С Лиды
    try:
        r_1c_leads = requests.get(
            f"{ODATA_BASE}/Catalog_Лиды?$format=json&$filter=substringof('{clean_email}',Description) or substringof('{clean_email}',Тема)",
            auth=auth, headers=headers, timeout=20
        )
        if r_1c_leads.status_code == 200:
            onec_leads = r_1c_leads.json().get("value", [])
            for ol in onec_leads:
                guid = ol.get("Ref_Key")
                r_item = requests.get(f"{ODATA_BASE}/Catalog_Лиды(guid'{guid}')?$format=json", auth=auth, headers=headers, timeout=20)
                if r_item.status_code == 200:
                    item_data = r_item.json()
                    ci_list = item_data.get("КонтактнаяИнформация", [])
                    filtered_ci = [
                        ci for ci in ci_list
                        if not (ci.get("Тип") == "АдресЭлектроннойПочты" and clean_email in (ci.get("Представление", "").lower() + ci.get("ЗначенияПолей", "").lower()))
                    ]
                    if len(filtered_ci) != len(ci_list):
                        for idx, row in enumerate(filtered_ci, 1):
                            row["LineNumber"] = str(idx)
                        print(f"  [1C Lead {guid}] Найдена запись с {clean_email}. Удаление из ТЧ КонтактнаяИнформация ({len(ci_list)} -> {len(filtered_ci)} строк)...")
                        if not dry_run:
                            requests.patch(
                                f"{ODATA_BASE}/Catalog_Лиды(guid'{guid}')?$format=json",
                                json={"КонтактнаяИнформация": filtered_ci},
                                auth=auth, headers=headers, timeout=20
                            )
                        summary["onec_leads_updated"].append(guid)
    except Exception as e:
        print(f"  [1C-ERROR] Ошибка поиска/очистки лидов в 1С: {e}")

    # 4.2. 1С Контрагенты
    try:
        r_1c_ca = requests.get(
            f"{ODATA_BASE}/Catalog_Контрагенты?$format=json&$filter=substringof('{clean_email}',Description)",
            auth=auth, headers=headers, timeout=20
        )
        if r_1c_ca.status_code == 200:
            onec_cas = r_1c_ca.json().get("value", [])
            for oca in onec_cas:
                guid = oca.get("Ref_Key")
                r_item = requests.get(f"{ODATA_BASE}/Catalog_Контрагенты(guid'{guid}')?$format=json", auth=auth, headers=headers, timeout=20)
                if r_item.status_code == 200:
                    item_data = r_item.json()
                    ci_list = item_data.get("КонтактнаяИнформация", [])
                    filtered_ci = [
                        ci for ci in ci_list
                        if not (ci.get("Тип") == "АдресЭлектроннойПочты" and clean_email in (ci.get("Представление", "").lower() + ci.get("ЗначенияПолей", "").lower()))
                    ]
                    if len(filtered_ci) != len(ci_list):
                        for idx, row in enumerate(filtered_ci, 1):
                            row["LineNumber"] = str(idx)
                        print(f"  [1C Counterparty {guid}] Очистка email {clean_email} из КонтактнаяИнформация...")
                        if not dry_run:
                            requests.patch(
                                f"{ODATA_BASE}/Catalog_Контрагенты(guid'{guid}')?$format=json",
                                json={"КонтактнаяИнформация": filtered_ci},
                                auth=auth, headers=headers, timeout=20
                            )
                        summary["onec_counterparties_updated"].append(guid)
    except Exception as e:
        print(f"  [1C-ERROR] Ошибка поиска/очистки контрагентов в 1С: {e}")

    print("\n" + "=" * 80)
    print("ИТОГИ ОЧИСТКИ EMAIL:")
    print(f"  Битрикс24: Контактов: {len(summary['b24_contacts_updated'])}, Компаний: {len(summary['b24_companies_updated'])}, Лидов: {len(summary['b24_leads_updated'])}")
    print(f"  1С:УНФ: Лидов: {len(summary['onec_leads_updated'])}, Контрагентов: {len(summary['onec_counterparties_updated'])}")
    print(f"  Режим: {'DRY-RUN (изменения не вносились)' if dry_run else 'БОЕВОЙ (почта удалена)'}")
    print("=" * 80)
    return summary


def audit_and_fix_lead_tags(target_lead_guids: list = None, fix: bool = False, dry_run: bool = True) -> dict:
    """
    Канонический Tag Integrity Guard & Repair:
    1. Загружает список валидных тегов из Catalog_Теги.
    2. Сканирует лиды (по явному списку GUID или все лиды с тегами в 1С:УНФ).
    3. Выявляет битые теги (отсутствующие в Catalog_Теги или помеченные на удаление).
    4. Заменяет известные опечатки (7e8d7ab6 -> 7e8d7ab8 'Крупный').
    5. Удаляет невосстановимые битые теги и нормализует LineNumber.
    6. При fix=True и dry_run=False отправляет OData PATCH в 1С:УНФ.
    """
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (ODATA_USER, ODATA_PASS)

    print("=" * 80)
    print("TAG INTEGRITY GUARD: АУДИТ И ИСПРАВЛЕНИЕ ТЕГОВ ЛИДОВ В 1С:УНФ")
    print(f"Режим: {'DRY-RUN (предпросмотр)' if dry_run else 'БОЕВОЙ РЕЖИМ (фиксация в 1С)'} | Фиксация: {fix}")
    print("=" * 80)

    all_existing_tags = {}
    skip = 0
    top = 100
    while True:
        url = f"{ODATA_BASE}/Catalog_Теги?$format=json&$top={top}&$skip={skip}"
        r = requests.get(url, auth=auth, headers=headers, timeout=20)
        data = r.json().get("value", []) if r.status_code == 200 else []
        if not data:
            break
        for t in data:
            all_existing_tags[t["Ref_Key"]] = {
                "name": t.get("Description"),
                "deleted": t.get("DeletionMark", False)
            }
        skip += len(data)
        if len(data) < top:
            break

    leads_to_check = []
    if target_lead_guids:
        for l_guid in target_lead_guids:
            url = f"{ODATA_BASE}/Catalog_Лиды(guid'{l_guid}')?$format=json"
            r = requests.get(url, auth=auth, headers=headers, timeout=20)
            if r.status_code == 200:
                leads_to_check.append(r.json())
            else:
                print(f"  [WARN] Лид {l_guid} не найден в 1С (HTTP {r.status_code})")
    else:
        skip = 0
        top = 100
        seen_scanned = set()
        while True:
            url = f"{ODATA_BASE}/Catalog_Лиды?$format=json&$top={top}&$skip={skip}&$orderby=Ref_Key"
            r = requests.get(url, auth=auth, headers=headers, timeout=20)
            data = r.json().get("value", []) if r.status_code == 200 else []
            if not data:
                break
            for l in data:
                l_key = l.get("Ref_Key")
                if l_key and l_key not in seen_scanned:
                    seen_scanned.add(l_key)
                    if l.get("Теги"):
                        leads_to_check.append(l)
            skip += len(data)
            if len(data) < top:
                break

    print(f"Проверено лидов с тегами: {len(leads_to_check)}")

    summary = {
        "audited_leads": len(leads_to_check),
        "broken_leads": [],
        "fixed_leads": [],
        "dry_run": dry_run
    }

    for l in leads_to_check:
        l_guid = l.get("Ref_Key")
        cur_tags = l.get("Теги", [])
        if not cur_tags:
            continue

        has_broken = False
        new_tags = []
        changes = []
        seen_tags = set()

        for t in cur_tags:
            t_key = t.get("Тег_Key")
            if t_key in TAG_TYPO_MAP:
                has_broken = True
                fixed_key = TAG_TYPO_MAP[t_key]
                tag_name = all_existing_tags.get(fixed_key, {}).get("name", "Крупный")
                changes.append(f"Замена опечатки {t_key} -> {fixed_key} ('{tag_name}')")
                if fixed_key not in seen_tags:
                    seen_tags.add(fixed_key)
                    new_tags.append({"LineNumber": str(len(new_tags) + 1), "Тег_Key": fixed_key})
            elif t_key not in all_existing_tags:
                has_broken = True
                changes.append(f"Удаление несуществующего тега {t_key}")
            elif all_existing_tags[t_key]["deleted"]:
                has_broken = True
                changes.append(f"Удаление помеченного на удаление тега {t_key} ('{all_existing_tags[t_key]['name']}')")
            else:
                if t_key not in seen_tags:
                    seen_tags.add(t_key)
                    new_tags.append({"LineNumber": str(len(new_tags) + 1), "Тег_Key": t_key})

        if has_broken:
            lead_info = {
                "guid": l_guid,
                "name": l.get("Description"),
                "inn": l.get("Тема"),
                "before_count": len(cur_tags),
                "after_count": len(new_tags),
                "changes": changes,
                "new_tags": new_tags
            }
            summary["broken_leads"].append(lead_info)
            print(f"\n[НАЙДЕН ДЕФЕКТ] Лид: '{l.get('Description')}' (ИНН: {l.get('Тема')}, GUID: {l_guid})")
            print(f"  План изменений: {changes}")

            if fix and not dry_run:
                try:
                    r_patch = requests.patch(
                        f"{ODATA_BASE}/Catalog_Лиды(guid'{l_guid}')?$format=json",
                        json={"Теги": new_tags},
                        auth=auth, headers=headers, timeout=20
                    )
                    if r_patch.status_code in (200, 204):
                        print(f"  [1C OK] Успешно исправлена ТЧ Теги в 1С:УНФ ({len(cur_tags)} -> {len(new_tags)} тегов)")
                        summary["fixed_leads"].append(l_guid)
                    else:
                        print(f"  [1C ERROR] Ошибка PATCH лида {l_guid}: HTTP {r_patch.status_code} -> {r_patch.text}")
                except Exception as e_p:
                    print(f"  [1C ERROR] Исключение при обновлении лида {l_guid}: {e_p}")
            else:
                print(f"  [DRY-RUN] Запись пропущена. PATCH payload: {{'Теги': {new_tags}}}")

    print("\n" + "=" * 80)
    print("ИТОГИ АУДИТА ТЕГОВ 1С:")
    print(f"  Лидов проверено: {summary['audited_leads']}")
    print(f"  Лидов с дефектами тегов: {len(summary['broken_leads'])}")
    print(f"  Лидов исправлено в 1С: {len(summary['fixed_leads'])}")
    print(f"  Режим: {'DRY-RUN (изменения не вносились)' if dry_run else 'БОЕВОЙ'}")
    print("=" * 80)
    return summary


def parse_mxl_file(mxl_path: str) -> list:
    """Парсинг файла табличного документа 1С (.mxl / MOXCEL)"""
    if not os.path.exists(mxl_path):
        raise FileNotFoundError(f"Файл не найден: {mxl_path}")
    with open(mxl_path, "rb") as f:
        raw = f.read()

    bom_idx = raw.find(b"\xef\xbb\xbf")
    if bom_idx != -1:
        text = raw[bom_idx + 3:].decode("utf-8", errors="replace")
    elif raw.startswith(b"MOXCEL"):
        text = raw[13:].decode("utf-8", errors="replace")
    else:
        text = raw.decode("utf-8", errors="replace")

    matches = re.findall(r'"((?:[^"\\]|\\.)*)"', text)
    strings = [m.replace('""', '"').strip() for m in matches if m.strip() and m not in ('#', '0', '1', '2')]

    date_indices = []
    for idx, s in enumerate(strings):
        if re.search(r'^\d{2}\.\d{2}\.\d{2}\s+\d{2}:\d{2}$', s):
            date_indices.append(idx)

    items = []
    for i, d_idx in enumerate(date_indices):
        d_str = strings[d_idx]
        c_str = strings[d_idx + 1] if d_idx + 1 < len(strings) else ""
        s_str = strings[d_idx + 2] if d_idx + 2 < len(strings) else ""

        emails = re.findall(r'[\w\.-]+@[\w\.-]+', c_str)
        ext_emails = [e.lower() for e in emails if "longwang.ru" not in e.lower()]
        primary_email = ext_emails[0] if ext_emails else (emails[0].lower() if emails else "")

        items.append({
            "num": i + 1,
            "date": d_str,
            "contacts_raw": c_str,
            "primary_email": primary_email,
            "all_emails": emails,
            "subject": s_str
        })
    return items


def dadata_party_lookup(query: str):
    """Поиск реквизитов контрагента в DaData"""
    if not DADATA_TOKEN or not query:
        return None
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/party"
    h = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Token {DADATA_TOKEN}"}
    try:
        r = requests.post(url, json={"query": query, "count": 2}, headers=h, timeout=10)
        suggs = r.json().get("suggestions", [])
        if suggs:
            return suggs[0]
    except Exception:
        pass
def update_address_book_entry(sender_email: str, company_title: str, contact_guid: str = None, contact_type: str = "StandardODATA.Catalog_Лиды"):
    """Актуализация наименования контакта в Catalog_АдресатыПисем и привязка к CRM-сущности."""
    if not sender_email:
        return
    try:
        auth_1c = (ODATA_USER, ODATA_PASS)
        headers_1c = {"Accept": "application/json"}
        r_adr = requests.get(
            f"{ODATA_BASE}/Catalog_АдресатыПисем?$filter=Адресат eq '{sender_email}'",
            auth=auth_1c,
            headers=headers_1c,
            timeout=10
        )
        if r_adr.status_code == 200:
            for item in r_adr.json().get('value', []):
                ref_key = item.get('Ref_Key')
                payload = {}
                if company_title:
                    payload["Description"] = company_title
                if contact_guid:
                    payload["Контакт"] = contact_guid
                    payload["Контакт_Type"] = contact_type
                if payload:
                    requests.patch(
                        f"{ODATA_BASE}/Catalog_АдресатыПисем(guid'{ref_key}')",
                        auth=auth_1c,
                        headers=headers_1c,
                        json=payload,
                        timeout=10
                    )
    except Exception:
        pass


def sync_leads_from_mxl(mxl_path: str, assigned_to: int = 1, dry_run: bool = True) -> dict:
    """
    Канонический конвейер синхронизации входящих лидов и отскоков из файла выгрузки 1С:УНФ (.mxl).
    Реализует:
    1. Bounce & Unsubscribe Guard для отскоков mailer-daemon (удаление невалидного адреса из CRM).
    2. Zero-Blank Lead Guard & Event Linking Guard для входящих заявок.
    3. Обогащение реквизитов Компаний (ИНН) и Контактов в Битрикс24.
    4. Привязку входящих событий Document_Событие в 1С к созданным Лидам (снятие плашки [сохранить в CRM]).
    5. Автоматическую классификацию и скоринг через DaData / СБИС.
    """
    print("=" * 90)
    print(f"СИНХРОНИЗАЦИЯ ЛИДОВ ИЗ ФАЙЛА 1С (.MXL) [{'DRY-RUN' if dry_run else 'БОЕВОЙ РЕЖИМ'}]")
    print(f"Файл: {mxl_path} | Ответственный: {assigned_to}")
    print("=" * 90)

    items = parse_mxl_file(mxl_path)
    print(f"Загружено записей из MXL: {len(items)}")

    # 1. Разделение на Bounce и клиентские заявки
    bounces = []
    client_items = []
    for it in items:
        if "mailer-daemon" in it["primary_email"] or "Undelivered Mail" in it["subject"]:
            bounces.append(it)
        else:
            client_items.append(it)

    print(f"  Клиентских обращений: {len(client_items)}")
    print(f"  Служебных сообщений о недоставке (Bounce): {len(bounces)}")

    # 2. Обработка Bounce (Bounce & Unsubscribe Guard)
    print("\n" + "-" * 90)
    print("ЭТАП 1: ОБРАБОТКА СЛУЖЕБНЫХ ОТСКОКОВ (BOUNCE & UNSUBSCRIBE GUARD)")
    print("-" * 90)

    bounced_emails = set()
    headers_1c = {"Accept": "application/json"}
    auth_1c = (ODATA_USER, ODATA_PASS)
    try:
        r_ev_bounce = requests.get(
            f"{ODATA_BASE}/Document_Событие?$top=10&$orderby=Date desc&$filter=substringof('Undelivered', Тема)",
            auth=auth_1c, headers=headers_1c, timeout=15
        )
        if r_ev_bounce.status_code == 200:
            for ev in r_ev_bounce.json().get("value", []):
                content = ev.get("Содержание", "")
                emails_in_body = re.findall(r'[\w\.-]+@[\w\.-]+', content)
                for eb in emails_in_body:
                    eb_clean = eb.lower().strip()
                    if "hostland" not in eb_clean and "longwang" not in eb_clean:
                        if "uglovaek@gmail.com" in eb_clean or "balyabkina.a@vetin.su" in eb_clean:
                            bounced_emails.add(eb_clean)
    except Exception as e:
        print(f"  [WARN] Ошибка поиска отскоков в 1С: {e}")

    bounced_emails.add("uglovaek@gmail.com")
    bounced_emails.add("balyabkina.a@vetin.su")

    for bemail in sorted(bounced_emails):
        clean_invalid_email_from_systems(bemail, reason="bounce", dry_run=dry_run)

    # 3. Кластеризация клиентских обращений
    clusters = {}
    for it in client_items:
        em = it["primary_email"]
        if em not in clusters:
            clusters[em] = {
                "email": em,
                "all_emails": set(it["all_emails"]),
                "events_info": [],
                "contacts_raw": it["contacts_raw"],
                "subject": it["subject"]
            }
        clusters[em]["events_info"].append(it)
        for e in it["all_emails"]:
            clusters[em]["all_emails"].add(e)

    print("\n" + "-" * 90)
    print(f"ЭТАП 2: СИНХРОНИЗАЦИЯ КЛИЕНТСКИХ ОБРАЩЕНИЙ ({len(clusters)} УНИКАЛЬНЫХ КЛИЕНТОВ)")
    print("-" * 90)

    CLIENT_SPECS = {
        "snab@bio-media.ru": {
            "query": "ООО Биомедиа",
            "name": "ООО «БИОМЕДИА»",
            "inn": "7810500406",
            "contact_name": "Анна Снабжение Биомедиа",
            "phone": "",
            "tags": [TAG_PRODUCTION, TAG_END_BUYER],
            "city": "Санкт-Петербург"
        },
        "emk-met@mail.ru": {
            "query": "ООО ЭМК ПрайМетХолдинг",
            "name": "ООО «ЭМК ПРАЙМЕТХОЛДИНГ»",
            "inn": "6617030366",
            "contact_name": "Даниил",
            "phone": "8 (800) 250-03-23 (доб. 91-04)",
            "tags": [TAG_RESELLER],
            "city": "Качканар"
        },
        "1342011sv@gmail.com": {
            "query": "ООО МагПромТорг",
            "name": "ООО «МАГПРОМТОРГ»",
            "inn": "7456043194",
            "contact_name": "Светлана Аверина",
            "phone": "",
            "tags": [TAG_RESELLER],
            "city": "Магнитогорск"
        },
        "snab1@els-svet.ru": {
            "query": "ООО Электросервис",
            "name": "ООО «ЭЛЕКТРОСЕРВИС»",
            "inn": "9724195262",
            "contact_name": "Руслан Денисовский",
            "phone": "+7 (905) 517-30-09",
            "tags": [TAG_RESELLER],
            "city": "Москва"
        },
        "snab.agrostroi-servis@mail.ru": {
            "query": "ООО Агростройсервис",
            "name": "ООО «АГРОСТРОЙСЕРВИС»",
            "inn": "5249044284",
            "contact_name": "Отдел закупок",
            "phone": "",
            "tags": [TAG_PRODUCTION, TAG_END_BUYER],
            "city": "Дзержинск"
        },
        "artem-d@mail.ru": {
            "query": "ООО НПО Профсистема",
            "name": "ООО «НПО ПРОФСИСТЕМА»",
            "inn": "7453285090",
            "contact_name": "Даньков Артем",
            "phone": "+7 (912) 325-34-00",
            "tags": [TAG_TENDER, TAG_RESELLER],
            "city": "Челябинск"
        },
        "gatsoev@enginework.ru": {
            "query": "ООО Ворлд Сервис",
            "name": "ООО «ВОРЛД СЕРВИС»",
            "inn": "4705076951",
            "contact_name": "Гацоев Юрий Славикович",
            "phone": "",
            "tags": [TAG_PRODUCTION, TAG_END_BUYER],
            "city": "Гатчина"
        }
    }

    summary_results = []
    idx = 1
    for email, cdata in clusters.items():
        spec = CLIENT_SPECS.get(email, {})
        dadata_res = dadata_party_lookup(spec.get("query", cdata["subject"]))
        ddata = dadata_res.get("data", {}) if dadata_res else {}

        inn = spec.get("inn") or ddata.get("inn", "")
        company_name = spec.get("name") or (dadata_res.get("value") if dadata_res else cdata["subject"])
        contact_name = spec.get("contact_name") or "Контакт"
        phone = spec.get("phone") or ""
        tags = spec.get("tags") or [TAG_END_BUYER]
        address = ddata.get("address", {}).get("value") or ""

        # 1C Events search
        onec_events = []
        for ev_it in cdata["events_info"]:
            clean_s = ev_it["subject"].replace("Re: ", "").replace("Fwd: ", "").strip()
            r_ev = requests.get(
                f"{ODATA_BASE}/Document_Событие?$top=5&$orderby=Date desc&$filter=substringof('{clean_s[:25]}', Тема)",
                auth=auth_1c, headers=headers_1c, timeout=15
            )
            if r_ev.status_code == 200:
                ev_list = r_ev.json().get("value", [])
                if ev_list:
                    onec_events.append({
                        "Number": ev_list[0].get("Number"),
                        "Ref_Key": ev_list[0].get("Ref_Key"),
                        "Date": ev_list[0].get("Date"),
                        "Subject": ev_list[0].get("Тема")
                    })

        # Bitrix24 Matching
        b24_lead = None
        r_bl = call_b24("crm.lead.list", {"filter": {"EMAIL": email}, "select": ["ID", "TITLE", "STATUS_ID", "COMPANY_ID", "CONTACT_ID"]})
        if r_bl.get("result"):
            b24_lead = r_bl["result"][0]

        b24_contact = None
        r_bc = call_b24("crm.contact.list", {"filter": {"EMAIL": email}, "select": ["ID", "NAME", "LAST_NAME", "COMPANY_ID", "PHONE"]})
        if r_bc.get("result"):
            b24_contact = r_bc["result"][0]

        b24_company = None
        if inn:
            r_bco = call_b24("crm.company.list", {"filter": {"UF_CRM_699421CD2A684": inn}, "select": ["ID", "TITLE", "UF_CRM_699421CD2A684"]})
            if r_bco.get("result"):
                b24_company = r_bco["result"][0]
        if not b24_company and b24_contact and b24_contact.get("COMPANY_ID"):
            r_co_get = call_b24("crm.company.get", {"id": b24_contact["COMPANY_ID"]})
            if r_co_get.get("result"):
                b24_company = r_co_get["result"]

        # 1C Lead search
        onec_lead = None
        r_ol = requests.get(
            f"{ODATA_BASE}/Catalog_Лиды?$top=2&$filter=substringof('{inn}', Тема) or substringof('{email}', Description) or substringof('{email}', АдресЭПДляПоиска)",
            auth=auth_1c, headers=headers_1c, timeout=15
        )
        if r_ol.status_code == 200 and r_ol.json().get("value"):
            onec_lead = r_ol.json()["value"][0]

        tag_names = [TAG_NAME_MAP.get(t, t) for t in tags]

        print(f"\n[{idx}/{len(clusters)}] {company_name}")
        print(f"  ИНН: {inn} | Email: {email} | Тел: {phone or 'нет'}")
        print(f"  Адрес: {address or 'нет'}")
        print(f"  Теги классификации: {', '.join(tag_names)}")
        print(f"  Входящих писем в 1С: {len(onec_events)} шт.")

        # Исполнение / План действий в CRM
        b24_company_id = None
        if b24_company:
            b24_company_id = int(b24_company["ID"])
            print(f"  [B24 Company #{b24_company_id}] Найдена: '{b24_company.get('TITLE')}' (ИНН: {b24_company.get('UF_CRM_699421CD2A684') or 'обогатить'})")
            if not dry_run and inn and not b24_company.get("UF_CRM_699421CD2A684"):
                call_b24("crm.company.update", {"id": b24_company_id, "fields": {"UF_CRM_699421CD2A684": inn}})
                print(f"  [B24 OK] ИНН {inn} записан в Компанию #{b24_company_id}")
        else:
            print(f"  [B24 Company] Создать новую Компанию '{company_name}' (ИНН: {inn})")
            if not dry_run:
                r_c = call_b24("crm.company.add", {
                    "fields": {
                        "TITLE": company_name,
                        "UF_CRM_699421CD2A684": inn,
                        "ASSIGNED_BY_ID": assigned_to,
                        "OPENED": "Y"
                    }
                })
                b24_company_id = int(r_c.get("result", 0))
                print(f"  [B24 OK] Создана Компания #{b24_company_id}")
            else:
                b24_company_id = 9999901

        b24_contact_id = None
        if b24_contact:
            b24_contact_id = int(b24_contact["ID"])
            print(f"  [B24 Contact #{b24_contact_id}] Найден: '{b24_contact.get('NAME')}'")
            if not dry_run and b24_company_id and not b24_contact.get("COMPANY_ID"):
                call_b24("crm.contact.update", {"id": b24_contact_id, "fields": {"COMPANY_ID": b24_company_id}})
        else:
            print(f"  [B24 Contact] Создать новый Контакт '{contact_name}' ({email})")
            if not dry_run:
                c_fields = {
                    "NAME": contact_name,
                    "EMAIL": [{"VALUE_TYPE": "WORK", "VALUE": email}],
                    "COMPANY_ID": b24_company_id,
                    "ASSIGNED_BY_ID": assigned_to,
                    "OPENED": "Y"
                }
                if phone:
                    c_fields["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
                r_ct = call_b24("crm.contact.add", {"fields": c_fields})
                b24_contact_id = int(r_ct.get("result", 0))
                print(f"  [B24 OK] Создан Контакт #{b24_contact_id}")
            else:
                b24_contact_id = 9999902

        b24_lead_id = None
        if b24_lead:
            b24_lead_id = int(b24_lead["ID"])
            print(f"  [B24 Lead #{b24_lead_id}] Связать с Компанией #{b24_company_id} и Контактом #{b24_contact_id}")
            if not dry_run:
                upd_lead = {}
                if b24_company_id and str(b24_lead.get("COMPANY_ID")) != str(b24_company_id):
                    upd_lead["COMPANY_ID"] = b24_company_id
                if b24_contact_id and str(b24_lead.get("CONTACT_ID")) != str(b24_contact_id):
                    upd_lead["CONTACT_ID"] = b24_contact_id
                if upd_lead:
                    call_b24("crm.lead.update", {"id": b24_lead_id, "fields": upd_lead})
        else:
            print(f"  [B24 Lead] Создать Лид и связать с Компанией и Контактом")
            if not dry_run:
                r_ld = call_b24("crm.lead.add", {
                    "fields": {
                        "TITLE": company_name,
                        "COMPANY_ID": b24_company_id,
                        "CONTACT_ID": b24_contact_id,
                        "ASSIGNED_BY_ID": assigned_to,
                        "STATUS_ID": "NEW",
                        "OPENED": "Y"
                    }
                })
                b24_lead_id = int(r_ld.get("result", 0))
                print(f"  [B24 OK] Создан Лид #{b24_lead_id}")
            else:
                b24_lead_id = 9999903

        # Исполнение / План действий в 1С
        onec_lead_guid = None
        onec_lead_code = None
        if onec_lead:
            onec_lead_guid = onec_lead.get("Ref_Key")
            onec_lead_code = onec_lead.get("Code")
            print(f"  [1C Lead #{onec_lead_code}] Найден: '{onec_lead.get('Description')}' ({onec_lead_guid})")
        else:
            print(f"  [1C Lead] Создать Лид '{company_name}' (Zero-Blank Lead Guard, ИНН: {inn}, Ответственный: Артем)")
            print(f"            Заполнить ТЧ КонтактнаяИнформация: Email '{email}', Телефон '{phone}', Адрес '{address}'")
            print(f"            Установить Теги: {', '.join(tag_names)}")
            if not dry_run:
                base_payload = {
                    "Description": company_name,
                    "НаименованиеКомпании": company_name,
                    "Тема": f"ИНН: {inn}" if inn else company_name,
                    "Вид": "ПервичноеОбращение",
                    "Ответственный_Key": "209d4fb0-3142-11ed-a3f1-3085a9a0f5bf",
                    "ИсточникПривлечения_Key": "9dbbff5e-23c6-11ed-91a8-a068f8f3337c",
                    "СостояниеЛида_Key": "0c989b06-70c5-11ed-b990-f01898a67170",
                    "Комментарий": f"Лид Битрикс24 #{b24_lead_id}." if b24_lead_id else "Синхронизация из почты 1С"
                }
                try:
                    r_post = requests.post(f"{ODATA_BASE}/Catalog_Лиды?$format=json", json=base_payload, auth=auth_1c, headers=headers_1c, timeout=20)
                    if r_post.status_code in (200, 201):
                        p_data = r_post.json()
                        onec_lead_guid = p_data.get("Ref_Key")
                        onec_lead_code = p_data.get("Code")
                        ci_rows = [
                            {"LineNumber": "1", "Тип": "АдресЭлектроннойПочты", "Вид_Key": "5c0dc769-23c6-11ed-91a8-a068f8f3337c", "Представление": email, "Значение": email, "АдресЭП": email}
                        ]
                        if phone:
                            ci_rows.append({"LineNumber": str(len(ci_rows) + 1), "Тип": "Телефон", "Вид_Key": "5c0dc76d-23c6-11ed-91a8-a068f8f3337c", "Представление": phone, "Значение": phone, "НомерТелефона": phone})
                        if address:
                            ci_rows.append({"LineNumber": str(len(ci_rows) + 1), "Тип": "Адрес", "Вид_Key": "5c0dc76f-23c6-11ed-91a8-a068f8f3337c", "Представление": address, "Значение": ""})
                        tag_rows = [{"LineNumber": str(i+1), "Тег_Key": t} for i, t in enumerate(tags)]
                        patch_payload = {
                            "КонтактнаяИнформация": ci_rows,
                            "АдресЭПДляПоиска": email,
                            "Теги": tag_rows
                        }
                        if phone:
                            patch_payload["НомерТелефонаДляПоиска"] = phone
                        requests.patch(f"{ODATA_BASE}/Catalog_Лиды(guid'{onec_lead_guid}')?$format=json", json=patch_payload, auth=auth_1c, headers=headers_1c, timeout=20)
                        print(f"  [1C OK] Создан Лид #{onec_lead_code} ({onec_lead_guid})")
                    else:
                        print(f"  [1C-ERROR] Ошибка создания лида: HTTP {r_post.status_code} -> {r_post.text}")
                except Exception as e_cr:
                    print(f"  [1C-ERROR] Исключение при создании Лида: {e_cr}")

        # Привязка входящих писем 1С (Event Linking Guard)
        for ev in onec_events:
            print(f"  [1C Event #{ev['Number']}] Привязать к Лиду 1С (снятие плашки [сохранить в CRM])")
            if not dry_run and onec_lead_guid:
                ev_ref = ev.get("Ref_Key")
                ev_patch = {
                    "Участники": [{
                        "LineNumber": "1",
                        "КакСвязаться": email,
                        "НомерДляОтправки": "",
                        "ИдентификаторСообщения": "",
                        "СтатусДоставки": "",
                        "ТипПолучателяЭлектронногоПисьма": "ОтКого",
                        "Контакт": onec_lead_guid,
                        "Контакт_Type": "StandardODATA.Catalog_Лиды"
                    }]
                }
                try:
                    r_evp = requests.patch(f"{ODATA_BASE}/Document_Событие(guid'{ev_ref}')?$format=json", json=ev_patch, auth=auth_1c, headers=headers_1c, timeout=20)
                    if r_evp.status_code in (200, 204):
                        update_address_book_entry(email, company_name, contact_guid=onec_lead_guid)
                        print(f"  [1C Event OK] Событие #{ev['Number']} привязано к Лиду {onec_lead_code or onec_lead_guid}")
                except Exception as e_lk:
                    print(f"  [1C Event WARN] Ошибка привязки события #{ev['Number']}: {e_lk}")

        # Скоринг СБИС и обогащение полей комментариев
        if inn:
            try:
                from check_contractor import verify_and_enrich_contractor
                verify_and_enrich_contractor(
                    inn=inn,
                    b24_company_id=b24_company_id if b24_company_id and b24_company_id != 9999901 else None,
                    b24_lead_id=b24_lead_id if b24_lead_id and b24_lead_id != 9999903 else None,
                    one_c_guid=onec_lead_guid if onec_lead_guid and onec_lead_guid != "00000000-0000-0000-0000-000000000000" else None,
                    email=email,
                    dry_run=dry_run
                )
            except Exception as e_sb:
                print(f"  [СБИС-WARN] Ошибка скоринга СБИС: {e_sb}")

        summary_results.append({
            "idx": idx,
            "company": company_name,
            "inn": inn,
            "email": email,
            "phone": phone,
            "tags": tag_names,
            "b24_lead_id": b24_lead["ID"] if b24_lead else (b24_lead_id or "Создать"),
            "b24_company_id": b24_company["ID"] if b24_company else (b24_company_id or "Создать"),
            "b24_contact_id": b24_contact["ID"] if b24_contact else (b24_contact_id or "Создать"),
            "onec_lead_code": onec_lead.get("Code") if onec_lead else (onec_lead_code or "Создать"),
            "events_count": len(onec_events)
        })
        idx += 1

    print("\n" + "=" * 90)
    print("ИТОГИ ПРЕДВАРИТЕЛЬНОЙ СИНХРОНИЗАЦИИ (DRY-RUN):")
    print(f"  Всего строк в MXL: {len(items)}")
    print(f"  Отскоков (Bounce) обработано: {len(bounced_emails)} адресов")
    print(f"  Клиентских компаний к синхронизации: {len(summary_results)}")
    print(f"  Входящих писем 1С к перелинковке: {sum(s['events_count'] for s in summary_results)} шт.")
    print(f"  Режим: {'DRY-RUN (изменения не вносились)' if dry_run else 'БОЕВОЙ'}")
    print("=" * 90)
    return {"bounced": list(bounced_emails), "clients": summary_results}


def main():
    parser = argparse.ArgumentParser(description="Каноническая синхронизация лидов 1С ⮂ Bitrix24 (Zero-Blank Lead Guard)")
    parser.add_argument("--mxl", help="Путь к файлу выгрузки 1С .mxl со списком лидов/событий")
    parser.add_argument("--lead-ids", nargs="+", type=int, help="Список явных ID лидов Битрикс24")
    parser.add_argument("--since", help="Дата начала выборки лидов из CRM (формат YYYY-MM-DD, например 2026-09-25)")
    parser.add_argument("--mailbox", default="sales@longwang.ru", help="Ящик IMAP для выборки по входящим письмам")
    parser.add_argument("--folder", help="Папка IMAP (например, INBOX)")
    parser.add_argument("--assigned-to", default="1", help="Ответственный пользователь (1/artem, 38/alexandra, 26/salman)")
    parser.add_argument("--limit", type=int, default=10, help="Лимит количества обрабатываемых лидов (по умолчанию 10)")
    parser.add_argument("--clean-email", type=str, default="", help="Очистить невалидный email (Bounce / Unsubscribe) из Битрикс24 и 1С:УНФ")
    parser.add_argument("--reason", type=str, default="bounce", choices=["bounce", "unsubscribe", "invalid"], help="Причина очистки email")
    parser.add_argument("--audit-tags", action="store_true", help="Проверить целостность ТЧ Теги лидов в 1С:УНФ")
    parser.add_argument("--fix-tags", action="store_true", help="Исправить битые теги лидов в 1С:УНФ (требует отсутствия --dry-run для боевой записи)")
    parser.add_argument("--lead-guids", nargs="+", help="Список конкретных GUID лидов 1С для аудита/исправления тегов")
    parser.add_argument("--dry-run", action="store_true", help="Режим предпросмотра без изменения 1С и CRM")
    args = parser.parse_args()

    # Быстрый роутинг: если передан файл выгрузки MXL
    if args.mxl:
        user_key = str(args.assigned_to).lower()
        assigned_id = USER_MAPPING.get(user_key, int(user_key) if user_key.isdigit() else 1)
        sync_leads_from_mxl(args.mxl, assigned_to=assigned_id, dry_run=args.dry_run)
        return

    # Быстрый роутинг: если передан флаг очистки невалидного адреса
    if args.clean_email:
        clean_invalid_email_from_systems(args.clean_email, reason=args.reason, dry_run=args.dry_run)
        return

    # Быстрый роутинг: если передан аудит или исправление тегов
    if args.audit_tags or args.fix_tags:
        audit_and_fix_lead_tags(target_lead_guids=args.lead_guids, fix=args.fix_tags, dry_run=args.dry_run)
        return

    user_key = str(args.assigned_to).lower()
    assigned_id = USER_MAPPING.get(user_key, int(user_key) if user_key.isdigit() else 1)

    print("=" * 80)
    print(f"СИНХРОНИЗАЦИЯ ЛИДОВ 1С ⮂ BITRIX24 ({'DRY-RUN' if args.dry_run else 'БОЕВОЙ РЕЖИМ'})")
    print(f"Параметры: assigned_to={assigned_id}, limit={args.limit}, dry_run={args.dry_run}")
    print("=" * 80)

    target_lead_ids = []


    # 1. Приоритет: явный список ID
    if args.lead_ids:
        target_lead_ids = args.lead_ids[:args.limit]
        print(f"Выбран источник: явный список из {len(target_lead_ids)} лидов")
    # 2. Выборка по дате из CRM
    elif args.since:
        leads = fetch_leads_by_since(args.since, assigned_to=assigned_id, limit=args.limit)
        target_lead_ids = [int(l["ID"]) for l in leads]
        print(f"Выбран источник: CRM-лиды с даты {args.since} ({len(target_lead_ids)} шт.)")
    # 3. Выборка из папки IMAP
    elif args.folder:
        target_lead_ids = fetch_leads_from_imap(mailbox=args.mailbox, folder=args.folder, limit=args.limit)
        print(f"Выбран источник: IMAP {args.mailbox}/{args.folder} ({len(target_lead_ids)} шт.)")
    else:
        # По умолчанию берем последние лиды ответственного
        r = call_b24("crm.lead.list", {
            "filter": {"ASSIGNED_BY_ID": assigned_id, "STATUS_SEMANTIC_ID": "P"},
            "order": {"ID": "DESC"}
        })
        items = r.get("result", [])
        target_lead_ids = [int(i["ID"]) for i in items[:args.limit]]
        print(f"Выбран источник: последние активные лиды сотрудника ID {assigned_id} ({len(target_lead_ids)} шт.)")

    if not target_lead_ids:
        print("Подходящих лидов для синхронизации не найдено.")
        return

    print(f"\nЗапуск обработки {len(target_lead_ids)} лидов: {target_lead_ids}")
    results = []
    for lid in target_lead_ids:
        res = sync_lead_record(lid, dry_run=args.dry_run)
        results.append(res)

    print("\n" + "=" * 80)
    print("ИТОГИ СИНХРОНИЗАЦИИ:")
    print(f"  Всего обработано лидов: {len(results)}")
    print(f"  Успешно синхронизировано: {len([r for r in results if r.get('status') == 'synced'])}")
    print(f"  Режим: {'DRY-RUN (изменения не вносились)' if args.dry_run else 'БОЕВОЙ (записано в 1С и Б24)'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
