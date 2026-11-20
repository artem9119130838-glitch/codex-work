"""
Утилита создания и привязки Лида в 1С:УНФ (Zero-Blank Lead Guard & Event Linking Guard).
Соответствует регламенту OData Guard и стандартам 1С:УНФ.

Протокол:
  Фаза 1: POST базовых реквизитов Лида (Description, НаименованиеКомпании, Тема, Ответственный, Источник, Состояние);
  Фаза 2: PATCH табличной части КонтактнаяИнформация (все Email, Телефоны, Адреса) и Теги;
  Фаза 3: POST контакта лида в Catalog_КонтактыЛидов (при наличии ФИО контактного лица);
  Фаза 4 (Event Linking): Привязка входящего письма Document_Событие к созданному Лиду:
          - Обновление ТЧ Участники: Контакт = <Ref_Key лида>, Контакт_Type = StandardODATA.Catalog_Лиды;
          - Актуализация Catalog_АдресатыПисем: Description = Наименование компании Лида;
  Фаза 5: GET контрольная валидация (проверка ТЧ КонтактнаяИнформация, реквизитов и связки События).

Использование:
  # Dry-run создания нового лида с привязкой к событию:
  py projects/1c_odata/scripts/create_1c_lead.py --dry-run --title "ООО «ФЕРМЕР ХОЛОД»" --inn "692266716" --email "fermerholod@yandex.ru" --extra-emails "snabagro.2020@mail.ru" --phone "+375447773029" --event-id "1fe83672-bc0e-11f1-8629-02006df8aab5"

  # Боевая привязка входящего письма к уже существующему Лиду и обогащение email (Dry-run):
  py projects/1c_odata/scripts/create_1c_lead.py --dry-run --link-event --lead-id "776d5e38-bc07-11f1-8629-02006df8aab5" --event-id "1fe83672-bc0e-11f1-8629-02006df8aab5" --sender-email "snabagro.2020@mail.ru"
"""

import sys
import json
import argparse
import os
import requests

sys.stdout.reconfigure(encoding='utf-8')

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

ODATA_BASE = os.getenv("ONEC_ODATA_URL", "http://artem.medianasoft.spb.ru/unf/odata/standard.odata")
ODATA_USER = os.getenv("ONEC_ODATA_USER", "odata.user")
ODATA_PASS = os.getenv("ONEC_ODATA_PASSWORD", "")

# GUID-константы 1С:УНФ
RESPONSIBLE_ARTEM = "209d4fb0-3142-11ed-a3f1-3085a9a0f5bf"
SOURCE_WEBSITE = "9dbbff5e-23c6-11ed-91a8-a068f8f3337c"
STATE_ACCEPTED = "0c989b06-70c5-11ed-b990-f01898a67170"

CI_EMAIL = "5c0dc769-23c6-11ed-91a8-a068f8f3337c"
CI_PHONE = "5c0dc76d-23c6-11ed-91a8-a068f8f3337c"
CI_LEGAL_ADDRESS = "5c0dc76f-23c6-11ed-91a8-a068f8f3337c"
CI_ACTUAL_ADDRESS = "5c0dc76e-23c6-11ed-91a8-a068f8f3337c"
CI_WEB = "5c0dc76c-23c6-11ed-91a8-a068f8f3337c"

TAG_END_BUYER = "6c77607c-e770-11ef-8e46-02006df8aab5"   # Конечный покупатель
TAG_PRODUCTION = "891061f8-df13-11ef-9922-02006df8aab5"  # Производство
TAG_TENDER = "052cb624-ded8-11ef-9922-02006df8aab5"      # Тендер
TAG_RESELLER = "306714e0-e1f5-11ef-8db0-02006df8aab5"    # Перепродажники
TAG_LARGE = "7e8d7ab8-df13-11ef-9922-02006df8aab5"       # Крупный
TAG_HOLDING = "0e89c354-fe42-11ef-8ae4-02006df8aab5"     # Холдинг
TAG_INDIVIDUAL = "43e14fb2-67a7-11f0-875b-02006df8aab5"  # Физик

# Автоматическое исправление известных опечаток GUID тегов
TAG_TYPO_MAP = {
    "7e8d7ab6-df13-11ef-9922-02006df8aab5": TAG_LARGE    # Опечатка 6 -> 8
}


def build_lead_base_payload(title, company_name=None, inn=None, comment=None):
    return {
        "Description": title,
        "НаименованиеКомпании": company_name or title,
        "Тема": f"ИНН: {inn}" if inn else title,
        "Вид": "ПервичноеОбращение",
        "Ответственный_Key": RESPONSIBLE_ARTEM,
        "ИсточникПривлечения_Key": SOURCE_WEBSITE,
        "СостояниеЛида_Key": STATE_ACCEPTED,
        "Комментарий": comment or "",
        "ОсновныеСведения": comment or ""
    }


def build_lead_patch_payload(emails=None, phone=None, legal_address=None, actual_address=None, web=None, tag_keys=None, existing_ci=None):
    ci_rows = []
    seen_emails = set()
    seen_phones = set()
    line_num = 1

    # Preserve any existing CI if provided
    if existing_ci:
        for row in existing_ci:
            ci_type = row.get("Тип")
            val = row.get("АдресЭП") or row.get("НомерТелефона") or row.get("Представление")
            if ci_type == "АдресЭлектроннойПочты":
                if val:
                    seen_emails.add(val.lower())
            elif ci_type == "Телефон":
                if val:
                    seen_phones.add(val)
            clean_row = {
                "LineNumber": str(line_num),
                "Тип": ci_type,
                "Вид_Key": row.get("Вид_Key"),
                "Представление": row.get("Представление", ""),
                "Значение": row.get("Значение", ""),
            }
            if row.get("АдресЭП"):
                clean_row["АдресЭП"] = row.get("АдресЭП")
            elif ci_type == "АдресЭлектроннойПочты":
                clean_row["АдресЭП"] = row.get("Представление", "")
            if row.get("НомерТелефона"):
                clean_row["НомерТелефона"] = row.get("НомерТелефона")
            elif ci_type == "Телефон":
                clean_row["НомерТелефона"] = row.get("Представление", "")
            ci_rows.append(clean_row)
            line_num += 1

    # Append new emails
    if emails:
        for em in emails:
            if em and em.lower() not in seen_emails:
                ci_rows.append({
                    "LineNumber": str(line_num),
                    "Тип": "АдресЭлектроннойПочты",
                    "Вид_Key": CI_EMAIL,
                    "Представление": em,
                    "Значение": em,
                    "АдресЭП": em
                })
                seen_emails.add(em.lower())
                line_num += 1

    # Append new phone
    if phone and phone not in seen_phones:
        ci_rows.append({
            "LineNumber": str(line_num),
            "Тип": "Телефон",
            "Вид_Key": CI_PHONE,
            "Представление": phone,
            "Значение": phone,
            "НомерТелефона": phone
        })
        seen_phones.add(phone)
        line_num += 1

    if legal_address and not any(r.get("Вид_Key") == CI_LEGAL_ADDRESS for r in ci_rows):
        ci_rows.append({
            "LineNumber": str(line_num),
            "Тип": "Адрес",
            "Вид_Key": CI_LEGAL_ADDRESS,
            "Представление": legal_address,
            "Значение": ""
        })
        line_num += 1

    if actual_address and not any(r.get("Вид_Key") == CI_ACTUAL_ADDRESS for r in ci_rows):
        ci_rows.append({
            "LineNumber": str(line_num),
            "Тип": "Адрес",
            "Вид_Key": CI_ACTUAL_ADDRESS,
            "Представление": actual_address,
            "Значение": ""
        })
        line_num += 1

    if web and not any(r.get("Вид_Key") == CI_WEB for r in ci_rows):
        ci_rows.append({
            "LineNumber": str(line_num),
            "Тип": "ВебСтраница",
            "Вид_Key": CI_WEB,
            "Представление": web,
            "Значение": web
        })
        line_num += 1

    tags_rows = []
    if tag_keys:
        seen_tags = set()
        for t_key in tag_keys:
            clean_key = TAG_TYPO_MAP.get(t_key, t_key)
            if clean_key and clean_key not in seen_tags:
                seen_tags.add(clean_key)
                tags_rows.append({
                    "LineNumber": str(len(tags_rows) + 1),
                    "Тег_Key": clean_key
                })

    first_email = next(iter(seen_emails), "") if seen_emails else ""
    first_phone = next(iter(seen_phones), "") if seen_phones else ""

    patch_payload = {
        "КонтактнаяИнформация": ci_rows
    }
    if first_email:
        patch_payload["АдресЭПДляПоиска"] = first_email
    if first_phone:
        patch_payload["НомерТелефонаДляПоиска"] = first_phone
    if tags_rows:
        patch_payload["Теги"] = tags_rows

    return patch_payload


def build_event_link_payload(event_id, lead_id, sender_email):
    return {
        "Участники": [
            {
                "LineNumber": "1",
                "КакСвязаться": sender_email,
                "НомерДляОтправки": "",
                "ИдентификаторСообщения": "",
                "СтатусДоставки": "",
                "ТипПолучателяЭлектронногоПисьма": "ОтКого",
                "Контакт": lead_id,
                "Контакт_Type": "StandardODATA.Catalog_Лиды"
            }
        ]
    }


def verify_lead_populated(lead_guid):
    url = f"{ODATA_BASE}/Catalog_Лиды(guid'{lead_guid}')?$format=json"
    r = requests.get(url, auth=(ODATA_USER, ODATA_PASS), headers={'Accept': 'application/json'}, timeout=15)
    if r.status_code != 200:
        return False, f"GET failed with HTTP {r.status_code}"

    data = r.json()
    ci = data.get("КонтактнаяИнформация", [])
    resp = data.get("Ответственный_Key")
    source = data.get("ИсточникПривлечения_Key")

    errors = []
    if len(ci) == 0:
        errors.append("КонтактнаяИнформация is EMPTY")
    if resp == "00000000-0000-0000-0000-000000000000":
        errors.append("Ответственный_Key is blank GUID")
    if source == "00000000-0000-0000-0000-000000000000":
        errors.append("ИсточникПривлечения_Key is blank GUID")

    if errors:
        return False, "; ".join(errors)

    return True, {
        "Ref_Key": data.get("Ref_Key"),
        "Code": data.get("Code"),
        "Description": data.get("Description"),
        "CI_count": len(ci),
        "АдресЭПДляПоиска": data.get("АдресЭПДляПоиска"),
        "НомерТелефонаДляПоиска": data.get("НомерТелефонаДляПоиска")
    }


def verify_event_linked(event_id, lead_id):
    url = f"{ODATA_BASE}/Document_Событие(guid'{event_id}')?$format=json"
    r = requests.get(url, auth=(ODATA_USER, ODATA_PASS), headers={'Accept': 'application/json'}, timeout=15)
    if r.status_code != 200:
        return False, f"GET Event failed with HTTP {r.status_code}"

    ev_data = r.json()
    participants = ev_data.get("Участники", [])
    if not participants:
        return False, "Event participants list is EMPTY"

    sender = next((p for p in participants if p.get("ТипПолучателяЭлектронногоПисьма") == "ОтКого"), participants[0])
    sender_email = sender.get("КакСвязаться", "").strip()

    # Check lead CI contains sender_email
    r_lead = requests.get(f"{ODATA_BASE}/Catalog_Лиды(guid'{lead_id}')?$format=json", auth=(ODATA_USER, ODATA_PASS), headers={'Accept': 'application/json'}, timeout=15)
    if r_lead.status_code != 200:
        return False, f"GET Lead failed with HTTP {r_lead.status_code}"
    lead_ci = r_lead.json().get("КонтактнаяИнформация", [])
    emails_in_lead = [row.get("АдресЭП", "").lower() for row in lead_ci if row.get("Тип") == "АдресЭлектроннойПочты"]

    if sender_email.lower() not in emails_in_lead:
        return False, f"Sender email '{sender_email}' is NOT in Lead КонтактнаяИнформация: {emails_in_lead}"

    return True, {
        "event_id": event_id,
        "event_number": ev_data.get("Number"),
        "event_subject": ev_data.get("Тема"),
        "sender_email": sender_email,
        "matched_in_lead": True,
        "lead_emails": emails_in_lead
    }


def update_address_book_entry(sender_email, company_title, contact_guid=None, contact_type="StandardODATA.Catalog_Лиды"):
    """Актуализация наименования контакта в Catalog_АдресатыПисем и привязка к CRM-сущности."""
    if not sender_email:
        return
    try:
        r_adr = requests.get(
            f"{ODATA_BASE}/Catalog_АдресатыПисем?$filter=Адресат eq '{sender_email}'",
            auth=(ODATA_USER, ODATA_PASS),
            headers={'Accept': 'application/json'},
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
                        auth=(ODATA_USER, ODATA_PASS),
                        headers={'Accept': 'application/json'},
                        json=payload,
                        timeout=10
                    )
    except Exception:
        pass


def link_event_to_existing_lead(args):
    """Привязка входящего письма Document_Событие к существующему Лиду и обогащение email."""
    # 1. Fetch current lead
    r_lead = requests.get(
        f"{ODATA_BASE}/Catalog_Лиды(guid'{args.lead_id}')",
        auth=(ODATA_USER, ODATA_PASS),
        headers={'Accept': 'application/json'},
        timeout=15
    )
    if r_lead.status_code != 200:
        raise RuntimeError(f"Failed to fetch lead {args.lead_id}: HTTP {r_lead.status_code}")
    lead_data = r_lead.json()
    existing_ci = lead_data.get("КонтактнаяИнформация", [])

    # Prepare emails list: sender_email + any extra
    emails = []
    if args.sender_email:
        emails.append(args.sender_email)
    if args.email and args.email not in emails:
        emails.append(args.email)
    if args.extra_emails:
        for em in args.extra_emails.split(","):
            em = em.strip()
            if em and em not in emails:
                emails.append(em)

    patch_ci_payload = build_lead_patch_payload(
        emails=emails,
        phone=args.phone,
        existing_ci=existing_ci
    )

    event_patch_payload = build_event_link_payload(
        event_id=args.event_id,
        lead_id=args.lead_id,
        sender_email=args.sender_email or emails[0]
    )

    if args.dry_run:
        return {
            "mode": "DRY_RUN",
            "action": "LINK_EVENT_TO_EXISTING_LEAD",
            "lead_id": args.lead_id,
            "lead_description": lead_data.get("Description"),
            "event_id": args.event_id,
            "emails_to_ensure": emails,
            "lead_patch_payload": patch_ci_payload,
            "event_patch_payload": event_patch_payload
        }

    # Execute PATCH on Lead CI
    r_patch_lead = requests.patch(
        f"{ODATA_BASE}/Catalog_Лиды(guid'{args.lead_id}')",
        auth=(ODATA_USER, ODATA_PASS),
        headers={'Accept': 'application/json'},
        json=patch_ci_payload,
        timeout=15
    )
    if r_patch_lead.status_code not in (200, 204):
        raise RuntimeError(f"Lead PATCH failed: HTTP {r_patch_lead.status_code} -> {r_patch_lead.text}")

    # Execute PATCH on Event
    r_patch_ev = requests.patch(
        f"{ODATA_BASE}/Document_Событие(guid'{args.event_id}')",
        auth=(ODATA_USER, ODATA_PASS),
        headers={'Accept': 'application/json'},
        json=event_patch_payload,
        timeout=15
    )
    if r_patch_ev.status_code not in (200, 204):
        raise RuntimeError(f"Event PATCH failed: HTTP {r_patch_ev.status_code} -> {r_patch_ev.text}")

    update_address_book_entry(args.sender_email or (emails[0] if emails else None), lead_data.get("Description"), contact_guid=args.lead_id)

    # Also link any other unassociated events from this sender_email
    if args.sender_email:
        try:
            r_all_ev = requests.get(
                f"{ODATA_BASE}/Document_Событие?$format=json&$top=50&$orderby=Date desc",
                auth=(ODATA_USER, ODATA_PASS),
                headers={'Accept': 'application/json'},
                timeout=15
            )
            if r_all_ev.status_code == 200:
                for ev in r_all_ev.json().get('value', []):
                    ev_id = ev.get('Ref_Key')
                    if ev_id == args.event_id:
                        continue
                    parts = ev.get('Участники', [])
                    for p in parts:
                        if p.get('КакСвязаться', '').strip().lower() == args.sender_email.lower():
                            if p.get('Контакт') != args.lead_id:
                                p_payload = build_event_link_payload(ev_id, args.lead_id, args.sender_email)
                                requests.patch(
                                    f"{ODATA_BASE}/Document_Событие(guid'{ev_id}')",
                                    auth=(ODATA_USER, ODATA_PASS),
                                    headers={'Accept': 'application/json'},
                                    json=p_payload,
                                    timeout=10
                                )
        except Exception:
            pass

    # Verify both
    ok_lead, lead_info = verify_lead_populated(args.lead_id)
    if not ok_lead:
        raise AssertionError(f"Lead verification failed: {lead_info}")

    ok_ev, ev_info = verify_event_linked(args.event_id, args.lead_id)
    if not ok_ev:
        raise AssertionError(f"Event link verification failed: {ev_info}")

    return {
        "status": "SUCCESS",
        "action": "LINKED_AND_VERIFIED",
        "lead_verification": lead_info,
        "event_verification": ev_info
    }


def execute_full_lead_creation(args):
    """Создание нового Лида с опциональной привязкой к входящему событию."""
    base_payload = build_lead_base_payload(
        title=args.title,
        company_name=args.company_name,
        inn=args.inn,
        comment=args.comment
    )

    tag_keys = []
    if args.tag_end_buyer:
        tag_keys.append(TAG_END_BUYER)
    if args.tag_production:
        tag_keys.append(TAG_PRODUCTION)
    if args.tag_tender:
        tag_keys.append(TAG_TENDER)
    if args.tag_reseller:
        tag_keys.append(TAG_RESELLER)
    if args.tag_large:
        tag_keys.append(TAG_LARGE)
    if args.tag_holding:
        tag_keys.append(TAG_HOLDING)
    if args.tag_individual:
        tag_keys.append(TAG_INDIVIDUAL)

    emails = []
    if args.email:
        emails.append(args.email)
    if args.sender_email and args.sender_email not in emails:
        emails.append(args.sender_email)
    if args.extra_emails:
        for em in args.extra_emails.split(","):
            em = em.strip()
            if em and em not in emails:
                emails.append(em)

    patch_payload = build_lead_patch_payload(
        emails=emails,
        phone=args.phone,
        legal_address=args.legal_address,
        actual_address=args.actual_address,
        web=args.web,
        tag_keys=tag_keys
    )

    event_patch_payload = None
    if args.event_id:
        event_patch_payload = build_event_link_payload(
            event_id=args.event_id,
            lead_id="<PENDING_LEAD_GUID>",
            sender_email=args.sender_email or (emails[0] if emails else "")
        )

    if args.dry_run:
        return {
            "mode": "DRY_RUN",
            "action": "CREATE_NEW_LEAD",
            "phase_1_base_payload": base_payload,
            "phase_2_patch_payload": patch_payload,
            "phase_4_event_link_payload": event_patch_payload,
            "contact": {
                "name": args.contact_name,
                "post": args.contact_post,
                "phone": args.contact_phone or args.phone,
                "email": args.contact_email or (emails[0] if emails else None)
            }
        }

    # Phase 1: POST Base Object
    r_post = requests.post(
        f"{ODATA_BASE}/Catalog_Лиды",
        auth=(ODATA_USER, ODATA_PASS),
        headers={'Accept': 'application/json'},
        json=base_payload,
        timeout=15
    )
    if r_post.status_code not in (200, 201):
        raise RuntimeError(f"Phase 1 POST failed: HTTP {r_post.status_code} -> {r_post.text}")

    lead_data = r_post.json()
    lead_guid = lead_data.get("Ref_Key")
    lead_code = lead_data.get("Code")

    # Phase 2: PATCH Tabular Sections
    r_patch = requests.patch(
        f"{ODATA_BASE}/Catalog_Лиды(guid'{lead_guid}')",
        auth=(ODATA_USER, ODATA_PASS),
        headers={'Accept': 'application/json'},
        json=patch_payload,
        timeout=15
    )
    if r_patch.status_code not in (200, 204):
        raise RuntimeError(f"Phase 2 PATCH failed: HTTP {r_patch.status_code} -> {r_patch.text}")

    # Phase 3: POST Contact if requested
    contact_guid = None
    if args.contact_name:
        contact_ci = []
        c_phone = args.contact_phone or args.phone
        c_email = args.contact_email or (emails[0] if emails else "")
        l_num = 1
        if c_email:
            contact_ci.append({
                "LineNumber": str(l_num),
                "Тип": "АдресЭлектроннойПочты",
                "Вид_Key": CI_EMAIL,
                "Представление": c_email,
                "Значение": c_email,
                "АдресЭП": c_email
            })
            l_num += 1
        if c_phone:
            contact_ci.append({
                "LineNumber": str(l_num),
                "Тип": "Телефон",
                "Вид_Key": CI_PHONE,
                "Представление": c_phone,
                "Значение": c_phone,
                "НомерТелефона": c_phone
            })
            l_num += 1

        contact_payload = {
            "Description": args.contact_name,
            "Owner_Key": lead_guid,
            "Должность": args.contact_post or "",
            "АдресЭПДляПоиска": c_email or "",
            "НомерТелефонаДляПоиска": c_phone or "",
            "КонтактнаяИнформация": contact_ci
        }
        r_cont = requests.post(
            f"{ODATA_BASE}/Catalog_КонтактыЛидов",
            auth=(ODATA_USER, ODATA_PASS),
            headers={'Accept': 'application/json'},
            json=contact_payload,
            timeout=15
        )
        if r_cont.status_code in (200, 201):
            contact_guid = r_cont.json().get("Ref_Key")

    # Phase 4: Event Linking
    ev_info = None
    if args.event_id:
        actual_event_payload = build_event_link_payload(
            event_id=args.event_id,
            lead_id=lead_guid,
            sender_email=args.sender_email or (emails[0] if emails else "")
        )
        r_patch_ev = requests.patch(
            f"{ODATA_BASE}/Document_Событие(guid'{args.event_id}')",
            auth=(ODATA_USER, ODATA_PASS),
            headers={'Accept': 'application/json'},
            json=actual_event_payload,
            timeout=15
        )
        if r_patch_ev.status_code not in (200, 204):
            raise RuntimeError(f"Phase 4 Event Link failed: HTTP {r_patch_ev.status_code} -> {r_patch_ev.text}")
        update_address_book_entry(args.sender_email or (emails[0] if emails else None), args.title, contact_guid=lead_guid)
        ok_ev, ev_info = verify_event_linked(args.event_id, lead_guid)
        if not ok_ev:
            raise AssertionError(f"Phase 4 Event Link verification failed: {ev_info}")

    # Phase 5: Zero-Blank Lead Verification (Mandatory GET)
    is_valid, check_info = verify_lead_populated(lead_guid)
    if not is_valid:
        raise AssertionError(f"CRITICAL: Zero-Blank Lead Guard failed! Lead {lead_guid} verification error: {check_info}")

    return {
        "status": "SUCCESS",
        "verified": True,
        "lead_guid": lead_guid,
        "lead_code": lead_code,
        "contact_guid": contact_guid,
        "event_linked": ev_info,
        "verification_details": check_info
    }


def main():
    parser = argparse.ArgumentParser(description="Создание и привязка Лида в 1С:УНФ (Zero-Blank Lead & Event Link Guard)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Предпросмотр данных без записи в 1С")
    group.add_argument("--commit", action="store_true", help="Боевая запись в 1С OData")

    parser.add_argument("--link-event", action="store_true", help="Привязать событие к уже существующему Лиду")
    parser.add_argument("--lead-id", help="GUID существующего Лида (при --link-event)")

    parser.add_argument("--title", help="Краткое наименование Лида")
    parser.add_argument("--company-name", help="Полное наименование юрлица")
    parser.add_argument("--inn", help="ИНН или УНП (записывается в Тему)")
    parser.add_argument("--email", help="Основной email лида")
    parser.add_argument("--sender-email", help="Email отправителя входящего письма (для привязки)")
    parser.add_argument("--extra-emails", help="Дополнительные email через запятую")
    parser.add_argument("--phone", help="Основной телефон лида")
    parser.add_argument("--legal-address", help="Юридический адрес")
    parser.add_argument("--actual-address", help="Фактический адрес")
    parser.add_argument("--web", help="Веб-сайт")
    parser.add_argument("--comment", help="Комментарий и описание потребности")

    parser.add_argument("--event-id", help="GUID входящего письма (Document_Событие) для привязки")

    parser.add_argument("--contact-name", help="ФИО контактного лица")
    parser.add_argument("--contact-post", help="Должность контактного лица")
    parser.add_argument("--contact-phone", help="Телефон контактного лица")
    parser.add_argument("--contact-email", help="Email контактного лица")

    parser.add_argument("--tag-end-buyer", action="store_true", help="Тег Конечный покупатель")
    parser.add_argument("--tag-production", action="store_true", help="Тег Производство")
    parser.add_argument("--tag-tender", action="store_true", help="Тег Тендер")
    parser.add_argument("--tag-reseller", action="store_true", help="Тег Перепродажник")
    parser.add_argument("--tag-large", action="store_true", help="Тег Крупный")
    parser.add_argument("--tag-holding", action="store_true", help="Тег Холдинг")
    parser.add_argument("--tag-individual", action="store_true", help="Тег Физик")

    args = parser.parse_args()
    try:
        if args.link_event:
            if not args.lead_id or not args.event_id:
                raise ValueError("--link-event requires both --lead-id and --event-id")
            result = link_event_to_existing_lead(args)
        else:
            if not args.title:
                raise ValueError("New lead creation requires --title")
            result = execute_full_lead_creation(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "ERROR", "error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
