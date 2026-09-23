"""
Утилита автономной синхронизации и обогащения компаний и контактов в Битрикс24.
НЕ создает лиды и сделки. Не создает лишних пользовательских полей.
Ищет дубликаты компаний по ИНН и контактов по Email.

Использование:
    py scripts/sync_to_bitrix.py --company-inn 2508001544 --company-name "АО «Восточный Порт»" --contact-email "alexey.rauzhin@vostport.ru" --contact-name "Раужин Алексей Вячеславович" --contact-post "Специалист по закупкам"
    py scripts/sync_to_bitrix.py --batch-json path/to/batch.json
"""

import sys, json, argparse, requests

sys.stdout.reconfigure(encoding='utf-8')

B24_WEBHOOK = "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/"
DEFAULT_ASSIGNED_BY = 1 # Артем

def find_company_by_inn(inn):
    r = requests.get(f"{B24_WEBHOOK}crm.company.list?FILTER[UF_CRM_699421CD2A684]={inn}")
    if r.status_code == 200:
        res = r.json().get('result', [])
        return res[0] if res else None
    return None

def find_contact_by_email(email):
    r = requests.get(f"{B24_WEBHOOK}crm.contact.list?FILTER[EMAIL]={email}")
    if r.status_code == 200:
        res = r.json().get('result', [])
        return res[0] if res else None
    return None

def enrich_or_create_company(title, inn, address=None, phone=None, email=None, web=None, comment=None):
    existing = find_company_by_inn(inn)
    if existing:
        cid = existing['ID']
        fields = {}
        if address and not existing.get('ADDRESS'):
            fields['ADDRESS'] = address
        if phone and not existing.get('PHONE'):
            fields['PHONE'] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if email and not existing.get('EMAIL'):
            fields['EMAIL'] = [{"VALUE_TYPE": "WORK", "VALUE": email}]
        if web and not existing.get('WEB'):
            fields['WEB'] = [{"VALUE_TYPE": "WORK", "VALUE": web}]
        if comment:
            cur_comm = existing.get('COMMENTS') or ''
            if comment not in cur_comm:
                fields['COMMENTS'] = f"{cur_comm}<br>{comment}" if cur_comm else comment

        if fields:
            r_up = requests.post(f"{B24_WEBHOOK}crm.company.update", json={"id": cid, "fields": fields})
            return {"action": "updated", "id": cid, "updated_fields": list(fields.keys())}
        return {"action": "exists_unchanged", "id": cid}
    else:
        new_fields = {
            "TITLE": title,
            "UF_CRM_699421CD2A684": inn,
            "ASSIGNED_BY_ID": DEFAULT_ASSIGNED_BY
        }
        if address:
            new_fields["ADDRESS"] = address
        if phone:
            new_fields["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if email:
            new_fields["EMAIL"] = [{"VALUE_TYPE": "WORK", "VALUE": email}]
        if web:
            new_fields["WEB"] = [{"VALUE_TYPE": "WORK", "VALUE": web}]
        if comment:
            new_fields["COMMENTS"] = comment

        r_add = requests.post(f"{B24_WEBHOOK}crm.company.add", json={"fields": new_fields})
        if r_add.status_code == 200:
            return {"action": "created", "id": r_add.json().get('result')}
        return {"action": "error", "error": r_add.text}

def enrich_or_create_contact(name, email, post=None, phone=None, company_id=None):
    existing = find_contact_by_email(email)
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
            r_up = requests.post(f"{B24_WEBHOOK}crm.contact.update", json={"id": cid, "fields": fields})
            return {"action": "updated", "id": cid, "updated_fields": list(fields.keys())}
        return {"action": "exists_unchanged", "id": cid}
    else:
        parts = name.split()
        first_name = parts[0] if parts else name
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        new_fields = {
            "NAME": first_name,
            "LAST_NAME": last_name,
            "EMAIL": [{"VALUE_TYPE": "WORK", "VALUE": email}],
            "ASSIGNED_BY_ID": DEFAULT_ASSIGNED_BY
        }
        if post:
            new_fields["POST"] = post
        if phone:
            new_fields["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if company_id:
            new_fields["COMPANY_ID"] = company_id

        r_add = requests.post(f"{B24_WEBHOOK}crm.contact.add", json={"fields": new_fields})
        if r_add.status_code == 200:
            return {"action": "created", "id": r_add.json().get('result')}
        return {"action": "error", "error": r_add.text}

def main():
    parser = argparse.ArgumentParser(description="Синхронизация Компаний и Контактов в Битрикс24")
    parser.add_argument("--company-title", help="Название компании")
    parser.add_argument("--company-inn", help="ИНН компании")
    parser.add_argument("--address", help="Адрес")
    parser.add_argument("--phone", help="Телефон")
    parser.add_argument("--email", help="Email компании")
    parser.add_argument("--web", help="Сайт")
    parser.add_argument("--comment", help="Комментарий")
    parser.add_argument("--contact-name", help="ФИО контакта")
    parser.add_argument("--contact-email", help="Email контакта")
    parser.add_argument("--contact-post", help="Должность контакта")
    parser.add_argument("--contact-phone", help="Телефон контакта")
    args = parser.parse_args()

    result = {}
    cid = None
    if args.company_inn and args.company_title:
        res_comp = enrich_or_create_company(
            title=args.company_title,
            inn=args.company_inn,
            address=args.address,
            phone=args.phone,
            email=args.email,
            web=args.web,
            comment=args.comment
        )
        result["company"] = res_comp
        cid = res_comp.get("id")

    if args.contact_email and args.contact_name:
        res_cnt = enrich_or_create_contact(
            name=args.contact_name,
            email=args.contact_email,
            post=args.contact_post,
            phone=args.contact_phone,
            company_id=cid
        )
        result["contact"] = res_cnt

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
