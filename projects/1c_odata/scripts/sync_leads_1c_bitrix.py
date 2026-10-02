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

B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/").rstrip("/") + "/"
ODATA_BASE = "http://artem.medianasoft.spb.ru/unf/odata/standard.odata"
ODATA_USER = "odata.writer"
ODATA_PASS = os.getenv("ONEC_ODATA_PASSWORD", "CosiN09oAr")

IMAP_HOST = os.getenv("IMAP_SERVER", "mail.hostland.ru")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
MAIL_USER = os.getenv("IMAP_USER", "sales@longwang.ru")
MAIL_PASS = os.getenv("IMAP_PASSWORD", "CosiN09oAr")

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

    return {
        "lead_id": lead_id,
        "company_id": b24_company_id,
        "contact_id": b24_contact_id,
        "one_c_guid": one_c_guid,
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


def main():
    parser = argparse.ArgumentParser(description="Каноническая синхронизация лидов 1С ⮂ Bitrix24 (Zero-Blank Lead Guard)")
    parser.add_argument("--lead-ids", nargs="+", type=int, help="Список явных ID лидов Битрикс24")
    parser.add_argument("--since", help="Дата начала выборки лидов из CRM (формат YYYY-MM-DD, например 2026-09-25)")
    parser.add_argument("--mailbox", default="sales@longwang.ru", help="Ящик IMAP для выборки по входящим письмам")
    parser.add_argument("--folder", help="Папка IMAP (например, INBOX)")
    parser.add_argument("--assigned-to", default="1", help="Ответственный пользователь (1/artem, 38/alexandra, 26/salman)")
    parser.add_argument("--limit", type=int, default=10, help="Лимит количества обрабатываемых лидов (по умолчанию 10)")
    parser.add_argument("--dry-run", action="store_true", help="Режим предпросмотра без изменения 1С и CRM")
    args = parser.parse_args()

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
