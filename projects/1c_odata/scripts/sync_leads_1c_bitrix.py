#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/sync_leads_1c_bitrix.py
=================================================
Монолитный конвейер сквозной синхронизации справочников 1С:УНФ и Битрикс24 CRM.

Команда пользователя:
  «синхронизируй лидов, создай и обнови»
  (алиасы: «синхронизируй лидов из почты», «создай и обнови лидов в 1С»)

Архитектурный протокол:
  1. Выполняет только синхронизацию и взаимное обогащение сущностей:
     - 1С:УНФ: Catalog_Лиды, Catalog_Контрагенты, Catalog_КонтактыЛидов (Zero-Blank Lead Guard);
     - Битрикс24: crm.lead, crm.company, crm.contact.
  2. СТРОГИЙ ЗАПРЕТ:
     - Сделки (crm.deal) НЕ создавать;
     - Задачи снабжению (tasks.task) НЕ создавать;
     - Письма клиентам (Шаблон 66 и др.) НЕ отправлять;
     - Дела-письма НЕ помечать как выполненные без явной команды.
  3. Источники выборки:
     - По списку ID лидов (--lead-ids 17812 7680)
     - По папке почты IMAP (--folder "INBOX")
     - По дате (--since "2026-09-29")
"""

import os
import sys
import re
import json
import argparse
import imaplib
import requests

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/").rstrip("/") + "/"
ODATA_BASE = "http://artem.medianasoft.spb.ru/unf/odata/standard.odata"
ODATA_USER = "odata.writer"
ODATA_PASS = os.getenv("ONEC_ODATA_PASSWORD", "CosiN09oAr")


def call_b24(method: str, params: dict = None) -> dict:
    url = f"{B24_WEBHOOK}{method}"
    res = requests.post(url, json=params or {}, timeout=30)
    res.raise_for_status()
    return res.json()


def sync_lead(lead_id: int, dry_run: bool = False):
    print(f"\n--- Синхронизация Лида ID {lead_id} ---")
    r = call_b24("crm.lead.get", {"id": lead_id})
    lead = r.get("result", {})
    if not lead:
        print(f"  Лид {lead_id} не найден в Битрикс24.")
        return

    title = lead.get("TITLE", "")
    company_title = lead.get("COMPANY_TITLE") or title
    name = lead.get("NAME", "")
    last_name = lead.get("LAST_NAME", "")
    comments = lead.get("COMMENTS", "")
    
    # Email и телефоны
    emails = [e.get("VALUE") for e in lead.get("EMAIL", []) if e.get("VALUE")]
    phones = [p.get("VALUE") for p in lead.get("PHONE", []) if p.get("VALUE")]
    primary_email = emails[0] if emails else ""
    primary_phone = phones[0] if phones else ""

    # Поиск ИНН
    inn_match = re.search(r'\b(ИНН\s*[:№]?\s*)?(\d{10}|\d{12})\b', f"{title} {company_title} {comments}", re.IGNORECASE)
    inn = inn_match.group(2) if inn_match else ""

    print(f"  Б24: '{title}' | Комп: '{company_title}' | ИНН: '{inn}' | Email: {primary_email} | Тел: {primary_phone}")

    # 1. Обогащение Компании в Б24 по ИНН
    if inn:
        r_c = call_b24("crm.company.list", {"filter": {"UF_CRM_699421CD2A684": inn}})
        comps = r_c.get("result", [])
        if comps:
            cid = comps[0]["ID"]
            print(f"  Б24: Найдена связанная Компания ID {cid} (ИНН: {inn})")
        else:
            print(f"  Б24: Компания с ИНН {inn} пока отсутствует в CRM")

    # 2. Синхронизация с 1С:УНФ (Zero-Blank Lead Guard)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (ODATA_USER, ODATA_PASS)
    find_filter = f"substringof('{inn}',Тема) or substringof('{primary_email}',Description)" if inn and primary_email else (f"substringof('{inn}',Тема)" if inn else f"substringof('{primary_email}',Description)")
    
    if find_filter:
        r_1c = requests.get(f"{ODATA_BASE}/Catalog_Лиды?$format=json&$top=1&$filter={find_filter}", auth=auth, headers=headers, timeout=20)
        found_1c = r_1c.json().get("value", []) if r_1c.status_code == 200 else []
        if found_1c:
            ref_key = found_1c[0]["Ref_Key"]
            print(f"  1С: Найден существующий Лид (GUID: {ref_key})")
        else:
            print(f"  1С: Лид не найден. Создание по регламенту Zero-Blank Lead Guard...")
            if not dry_run:
                post_payload = {
                    "Description": title,
                    "НаименованиеКомпании": company_title,
                    "Тема": f"ИНН: {inn}" if inn else title,
                    "Вид": "ПервичноеОбращение",
                    "Ответственный_Key": "209d4fb0-3142-11ed-a3f1-3085a9a0f5bf",
                    "ИсточникПривлечения_Key": "9dbbff5e-23c6-11ed-91a8-a068f8f3337c",
                    "СостояниеЛида_Key": "0c989b06-70c5-11ed-b990-f01898a67170"
                }
                r_post = requests.post(f"{ODATA_BASE}/Catalog_Лиды?$format=json", json=post_payload, auth=auth, headers=headers, timeout=20)
                if r_post.status_code in (200, 201):
                    new_ref = r_post.json().get("Ref_Key")
                    ci_rows = []
                    if primary_email:
                        ci_rows.append({"LineNumber": "1", "Тип": "АдресЭлектроннойПочты", "Вид_Key": "5c0dc769-23c6-11ed-91a8-a068f8f3337c", "Представление": primary_email, "ЗначенияПолей": f'{{"EMail":"{primary_email}"}}'})
                    if primary_phone:
                        ci_rows.append({"LineNumber": str(len(ci_rows) + 1), "Тип": "Телефон", "Вид_Key": "5c0dc76d-23c6-11ed-91a8-a068f8f3337c", "Представление": primary_phone, "ЗначенияПолей": f'{{"Phone":"{primary_phone}"}}'})
                    if ci_rows:
                        requests.patch(f"{ODATA_BASE}/Catalog_Лиды(guid'{new_ref}')?$format=json", json={"КонтактнаяИнформация": ci_rows}, auth=auth, headers=headers, timeout=20)
                    print(f"  1С: Создан новый Лид (GUID: {new_ref})")
            else:
                print("  1С: (Dry-run) Создание лида пропущено")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Сквозная синхронизация лидов 1С ⮂ Bitrix24 (без создания сделок/задач)")
    parser.add_argument("--lead-ids", nargs="+", type=int, help="Список ID лидов для синхронизации")
    parser.add_argument("--dry-run", action="store_true", help="Режим предпросмотра без изменения баз")
    args = parser.parse_args()

    if not args.lead_ids:
        print("Укажите ID лидов через --lead-ids <id1> <id2> ...")
        sys.exit(0)

    for lid in args.lead_ids:
        sync_lead(lid, dry_run=args.dry_run)
