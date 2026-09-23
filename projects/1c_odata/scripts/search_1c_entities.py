"""
Утилита быстрого поиска сущностей в 1С:УНФ через OData API.
Ищет: Контрагентов, Покупателей, Лиды, Заказы покупателей, Контакты.
Выводит результат в компактном JSON формате для экономии токенов и лимитов.

Использование:
    py scripts/search_1c_entities.py --inn 7447110140
    py scripts/search_1c_entities.py --email alexey.rauzhin@vostport.ru
    py scripts/search_1c_entities.py --name "Восточный Порт"
"""

import sys, json, argparse, urllib.parse, requests

sys.stdout.reconfigure(encoding='utf-8')

ONEC_BASE = "http://artem.medianasoft.spb.ru/unf/odata/standard.odata"
ONEC_AUTH = ('odata.user', 'n8n159753!')

def search_by_inn(inn):
    res = {"inn": inn, "counterparties": [], "leads": []}
    
    # 1. Counterparties
    q_ca = urllib.parse.quote(f"ИНН eq '{inn}'")
    r_ca = requests.get(f"{ONEC_BASE}/Catalog_Контрагенты?$filter={q_ca}&$format=json", auth=ONEC_AUTH)
    if r_ca.status_code == 200:
        for ca in r_ca.json().get('value', []):
            res["counterparties"].append({
                "ref": ca.get("Ref_Key"),
                "code": ca.get("Code"),
                "name": ca.get("Description"),
                "full_name": ca.get("НаименованиеПолное"),
                "is_buyer": ca.get("Покупатель"),
                "is_supplier": ca.get("Поставщик"),
                "is_other": ca.get("ПрочиеОтношения")
            })

    # 2. Leads
    q_lead = urllib.parse.quote(f"ИНН eq '{inn}'")
    r_lead = requests.get(f"{ONEC_BASE}/Catalog_Лиды?$filter={q_lead}&$format=json", auth=ONEC_AUTH)
    if r_lead.status_code == 200:
        for l in r_lead.json().get('value', []):
            res["leads"].append({
                "ref": l.get("Ref_Key"),
                "code": l.get("Code"),
                "name": l.get("Description"),
                "state": l.get("СостояниеЛида_Key")
            })

    return res

def search_by_email(email):
    res = {"email": email, "ca_contacts": [], "lead_contacts": []}
    
    # 1. CA Contacts
    q_c = urllib.parse.quote(f"АдресЭПДляПоиска eq '{email}'")
    r_c = requests.get(f"{ONEC_BASE}/Catalog_КонтактныеЛица?$filter={q_c}&$format=json", auth=ONEC_AUTH)
    if r_c.status_code == 200:
        for c in r_c.json().get('value', []):
            res["ca_contacts"].append({
                "ref": c.get("Ref_Key"),
                "code": c.get("Code"),
                "name": c.get("Description"),
                "owner": c.get("Владелец_Key"),
                "role": c.get("Должность")
            })
            
    # 2. Lead Contacts
    r_lc = requests.get(f"{ONEC_BASE}/Catalog_КонтактыЛидов?$filter={q_c}&$format=json", auth=ONEC_AUTH)
    if r_lc.status_code == 200:
        for c in r_lc.json().get('value', []):
            res["lead_contacts"].append({
                "ref": c.get("Ref_Key"),
                "code": c.get("Code"),
                "name": c.get("Description"),
                "lead_owner": c.get("Owner_Key"),
                "role": c.get("Должность")
            })
            
    return res

def main():
    parser = argparse.ArgumentParser(description="Поиск сущностей в 1С:УНФ через OData")
    parser.add_argument("--inn", help="Поиск по ИНН организации")
    parser.add_argument("--email", help="Поиск по Email контактов")
    parser.add_argument("--json", action="store_true", default=True, help="Вывод в JSON")
    args = parser.parse_args()

    out = {}
    if args.inn:
        out["by_inn"] = search_by_inn(args.inn)
    if args.email:
        out["by_email"] = search_by_email(args.email)

    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
