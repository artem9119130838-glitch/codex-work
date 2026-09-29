"""
Утилита двухфазного создания и верификации Лида в 1С:УНФ (Zero-Blank Lead Guard).
Соответствует регламенту OData Guard и стандарту двухфазной записи.

Протокол:
  Фаза 1: POST базовых реквизитов (Description, НаименованиеКомпании, Тема, Ответственный, Источник, Состояние);
  Фаза 2: PATCH табличной части КонтактнаяИнформация (Email, Телефон, Адреса) и Теги;
  Фаза 3: POST контакта лида в Catalog_КонтактыЛидов;
  Фаза 4: GET контрольная валидация (проверка наличия строк ТЧ и заполненности экранных полей).

Использование:
  py projects/1c_odata/scripts/create_1c_lead.py --dry-run --title "ООО «ФЕРМЕР ХОЛОД»" --inn "692266716" --email "fermerholod@yandex.ru" --phone "+375447773029"
  py projects/1c_odata/scripts/create_1c_lead.py --commit --title "ООО «ФЕРМЕР ХОЛОД»" --inn "692266716" --email "fermerholod@yandex.ru" --phone "+375447773029" --contact-name "Нечипоренко Евгений Игоревич" --contact-post "Директор"
"""

import sys
import json
import argparse
import os
import requests

sys.stdout.reconfigure(encoding='utf-8')

ODATA_BASE = "http://artem.medianasoft.spb.ru/unf/odata/standard.odata"
ODATA_USER = "odata.user"
ODATA_PASS = os.getenv("ONEC_ODATA_PASSWORD", "n8n159753!")

# GUID-константы 1С:УНФ
RESPONSIBLE_ARTEM = "209d4fb0-3142-11ed-a3f1-3085a9a0f5bf"
SOURCE_WEBSITE = "9dbbff5e-23c6-11ed-91a8-a068f8f3337c"
STATE_ACCEPTED = "0c989b06-70c5-11ed-b990-f01898a67170"

CI_EMAIL = "5c0dc769-23c6-11ed-91a8-a068f8f3337c"
CI_PHONE = "5c0dc76d-23c6-11ed-91a8-a068f8f3337c"
CI_LEGAL_ADDRESS = "5c0dc76f-23c6-11ed-91a8-a068f8f3337c"
CI_ACTUAL_ADDRESS = "5c0dc76e-23c6-11ed-91a8-a068f8f3337c"
CI_WEB = "5c0dc76c-23c6-11ed-91a8-a068f8f3337c"

TAG_END_BUYER = "6c77607c-e770-11ef-8e46-02006df8aab5"
TAG_PRODUCTION = "891061f8-df13-11ef-9922-02006df8aab5"
TAG_TENDER = "052cb624-ded8-11ef-9922-02006df8aab5"
TAG_RESELLER = "306714e0-e1f5-11ef-8db0-02006df8aab5"


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


def build_lead_patch_payload(email=None, phone=None, legal_address=None, actual_address=None, web=None, tag_keys=None):
    ci_rows = []
    line_num = 1

    if email:
        ci_rows.append({
            "LineNumber": str(line_num),
            "Тип": "АдресЭлектроннойПочты",
            "Вид_Key": CI_EMAIL,
            "Представление": email,
            "Значение": email,
            "АдресЭП": email
        })
        line_num += 1

    if phone:
        ci_rows.append({
            "LineNumber": str(line_num),
            "Тип": "Телефон",
            "Вид_Key": CI_PHONE,
            "Представление": phone,
            "Значение": phone,
            "НомерТелефона": phone
        })
        line_num += 1

    if legal_address:
        ci_rows.append({
            "LineNumber": str(line_num),
            "Тип": "Адрес",
            "Вид_Key": CI_LEGAL_ADDRESS,
            "Представление": legal_address,
            "Значение": ""
        })
        line_num += 1

    if actual_address:
        ci_rows.append({
            "LineNumber": str(line_num),
            "Тип": "Адрес",
            "Вид_Key": CI_ACTUAL_ADDRESS,
            "Представление": actual_address,
            "Значение": ""
        })
        line_num += 1

    if web:
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
        for idx, t_key in enumerate(tag_keys, 1):
            tags_rows.append({
                "LineNumber": str(idx),
                "Тег_Key": t_key
            })

    patch_payload = {
        "КонтактнаяИнформация": ci_rows
    }
    if email:
        patch_payload["АдресЭПДляПоиска"] = email
    if phone:
        patch_payload["НомерТелефонаДляПоиска"] = phone
    if tags_rows:
        patch_payload["Теги"] = tags_rows

    return patch_payload


def verify_lead_populated(lead_guid):
    url = f"{ODATA_BASE}/Catalog_Лиды(guid'{lead_guid}')?$format=json"
    r = requests.get(url, auth=(ODATA_USER, ODATA_PASS), timeout=15)
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


def execute_two_phase_lead_creation(args):
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

    patch_payload = build_lead_patch_payload(
        email=args.email,
        phone=args.phone,
        legal_address=args.legal_address,
        actual_address=args.actual_address,
        web=args.web,
        tag_keys=tag_keys
    )

    if args.dry_run:
        return {
            "mode": "DRY_RUN",
            "phase_1_base_payload": base_payload,
            "phase_2_patch_payload": patch_payload,
            "contact": {
                "name": args.contact_name,
                "post": args.contact_post,
                "phone": args.contact_phone or args.phone,
                "email": args.contact_email or args.email
            }
        }

    # Phase 1: POST Base Object
    r_post = requests.post(
        f"{ODATA_BASE}/Catalog_Лиды?$format=json",
        auth=(ODATA_USER, ODATA_PASS),
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
        f"{ODATA_BASE}/Catalog_Лиды(guid'{lead_guid}')?$format=json",
        auth=(ODATA_USER, ODATA_PASS),
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
        c_email = args.contact_email or args.email
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
            f"{ODATA_BASE}/Catalog_КонтактыЛидов?$format=json",
            auth=(ODATA_USER, ODATA_PASS),
            json=contact_payload,
            timeout=15
        )
        if r_cont.status_code in (200, 201):
            contact_guid = r_cont.json().get("Ref_Key")

    # Phase 4: Zero-Blank Lead Verification (Mandatory GET)
    is_valid, check_info = verify_lead_populated(lead_guid)
    if not is_valid:
        raise AssertionError(f"CRITICAL: Zero-Blank Lead Guard failed! Lead {lead_guid} verification error: {check_info}")

    return {
        "status": "SUCCESS",
        "verified": True,
        "lead_guid": lead_guid,
        "lead_code": lead_code,
        "contact_guid": contact_guid,
        "verification_details": check_info
    }


def main():
    parser = argparse.ArgumentParser(description="Двухфазное создание Лида в 1С:УНФ (Zero-Blank Lead Guard)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Предпросмотр данных без записи в 1С")
    group.add_argument("--commit", action="store_true", help="Боевая запись в 1С OData")

    parser.add_argument("--title", required=True, help="Краткое наименование Лида")
    parser.add_argument("--company-name", help="Полное наименование юрлица")
    parser.add_argument("--inn", help="ИНН или УНП (записывается в Тему)")
    parser.add_argument("--email", help="Основной email лида")
    parser.add_argument("--phone", help="Основной телефон лида")
    parser.add_argument("--legal-address", help="Юридический адрес")
    parser.add_argument("--actual-address", help="Фактический адрес")
    parser.add_argument("--web", help="Веб-сайт")
    parser.add_argument("--comment", help="Комментарий и описание потребности")

    parser.add_argument("--contact-name", help="ФИО контактного лица")
    parser.add_argument("--contact-post", help="Должность контактного лица")
    parser.add_argument("--contact-phone", help="Телефон контактного лица")
    parser.add_argument("--contact-email", help="Email контактного лица")

    parser.add_argument("--tag-end-buyer", action="store_true", help="Тег Конечный покупатель")
    parser.add_argument("--tag-production", action="store_true", help="Тег Производство")
    parser.add_argument("--tag-tender", action="store_true", help="Тег Тендер")
    parser.add_argument("--tag-reseller", action="store_true", help="Тег Перепродажник")

    args = parser.parse_args()
    try:
        result = execute_two_phase_lead_creation(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "ERROR", "error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
