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

import os

def _load_env():
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
        r"C:\Codex\projects\1c_odata\.env",
        r"C:\Codex_Shared\projects\1c_odata\.env",
    ]
    for p in search_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if k not in os.environ:
                            os.environ[k] = v

_load_env()

ONEC_BASE = os.getenv("ONEC_ODATA_URL", "").rstrip("/")
ONEC_USER = os.getenv("ONEC_ODATA_USER", "")
ONEC_PASS = os.getenv("ONEC_ODATA_PASSWORD", "")
ONEC_AUTH = (ONEC_USER, ONEC_PASS) if ONEC_USER else None

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

def search_by_name(name):
    import re
    res = {"name": name, "counterparties": [], "leads": [], "ca_contacts": [], "lead_contacts": []}
    clean = re.sub(r'[«»"“”\']', '', name).strip()
    
    # 1. Counterparties
    q_ca = urllib.parse.quote(f"substringof('{clean}', Description)")
    r_ca = requests.get(f"{ONEC_BASE}/Catalog_Контрагенты?$filter={q_ca}&$format=json", auth=ONEC_AUTH)
    if r_ca.status_code == 200:
        for ca in r_ca.json().get('value', []):
            res["counterparties"].append({
                "ref": ca.get("Ref_Key"),
                "code": ca.get("Code"),
                "name": ca.get("Description"),
                "is_buyer": ca.get("Покупатель"),
                "inn": ca.get("ИНН")
            })

    # 2. Leads
    q_lead = urllib.parse.quote(f"substringof('{clean}', Description) or substringof('{clean}', Тема)")
    r_lead = requests.get(f"{ONEC_BASE}/Catalog_Лиды?$filter={q_lead}&$format=json", auth=ONEC_AUTH)
    if r_lead.status_code == 200:
        for l in r_lead.json().get('value', []):
            res["leads"].append({
                "ref": l.get("Ref_Key"),
                "code": l.get("Code"),
                "name": l.get("Description")
            })

    # 3. CA Contacts
    q_c = urllib.parse.quote(f"substringof('{clean}', Description)")
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

    # 4. Lead Contacts
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

def search_by_guid(guid):
    res = {"guid": guid, "entity": None, "sub_contacts": []}
    for ent in ["Catalog_Контрагенты", "Catalog_Лиды", "Catalog_КонтактныеЛица", "Catalog_КонтактыЛидов"]:
        r = requests.get(f"{ONEC_BASE}/{ent}(guid'{guid}')?$format=json", auth=ONEC_AUTH)
        if r.status_code == 200:
            res["entity"] = {"type": ent, "data": r.json()}
            break

    # Search contacts belonging to this guid
    q_own = urllib.parse.quote(f"Owner_Key eq guid'{guid}'")
    r_lc = requests.get(f"{ONEC_BASE}/Catalog_КонтактыЛидов?$filter={q_own}&$format=json", auth=ONEC_AUTH)
    if r_lc.status_code == 200:
        for c in r_lc.json().get('value', []):
            res["sub_contacts"].append({"type": "Catalog_КонтактыЛидов", "name": c.get("Description"), "code": c.get("Code"), "ref": c.get("Ref_Key")})

    q_ca_c = urllib.parse.quote(f"Владелец_Key eq guid'{guid}'")
    r_ca_c = requests.get(f"{ONEC_BASE}/Catalog_КонтактныеЛица?$filter={q_ca_c}&$format=json", auth=ONEC_AUTH)
    if r_ca_c.status_code == 200:
        for c in r_ca_c.json().get('value', []):
            res["sub_contacts"].append({"type": "Catalog_КонтактныеЛица", "name": c.get("Description"), "code": c.get("Code"), "ref": c.get("Ref_Key")})

    return res

def main():
    parser = argparse.ArgumentParser(description="Поиск сущностей в 1С:УНФ через OData")
    parser.add_argument("--inn", help="Поиск по ИНН организации")
    parser.add_argument("--email", help="Поиск по Email контактов")
    parser.add_argument("--name", help="Поиск по наименованию или ФИО")
    parser.add_argument("--guid", help="Поиск по GUID сущности 1C")
    parser.add_argument("--json", action="store_true", default=True, help="Вывод в JSON")
    args = parser.parse_args()

    out = {}
    if args.inn:
        out["by_inn"] = search_by_inn(args.inn)
    if args.email:
        out["by_email"] = search_by_email(args.email)
    if args.name:
        out["by_name"] = search_by_name(args.name)
    if args.guid:
        out["by_guid"] = search_by_guid(args.guid)

    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
