#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import ONEC_BASE, ONEC_AUTH_READ, ONEC_AUTH_WRITE

leads = [
    {"lead_guid": "a09ae362-cd36-11f1-974e-02006df8aab5", "email": "pek31-73@yandex.ru", "name": "Сергей", "phone": "+7 (951) 133-74-46", "post": "Менеджер по закупкам / сбыту"},
    {"lead_guid": "bd3c4830-cd36-11f1-974e-02006df8aab5", "email": "s.erofeeva@unikom-service.ru", "name": "Ерофеева Светлана Юрьевна", "phone": "+7 (3439) 66-87-10", "post": "Экономист по снабжению"},
    {"lead_guid": "d1034468-cd36-11f1-974e-02006df8aab5", "email": "stropansnab@mail.ru", "name": "Иванова Нина", "phone": "+7 (908) 798-79-89", "post": "Снабжение"},
    {"lead_guid": "e19b44ec-cd36-11f1-974e-02006df8aab5", "email": "kae1465@bk.ru", "name": "Кравченко Алексей", "phone": "+7 (920) 898-06-00", "post": "Менеджер по закупкам"}
]

CI_LEAD_CONTACT_EMAIL = "5c0dc752-23c6-11ed-91a8-a068f8f3337c"
CI_LEAD_CONTACT_PHONE = "5c0dc756-23c6-11ed-91a8-a068f8f3337c"

print("=== 1. Создание Catalog_КонтактыЛидов с Owner_Key ===")
for l in leads:
    payload = {
        "Description": l["name"],
        "Owner_Key": l["lead_guid"],
        "Должность": l["post"],
        "КонтактнаяИнформация": [
            {
                "LineNumber": "1",
                "Тип": "АдресЭлектроннойПочты",
                "Вид_Key": CI_LEAD_CONTACT_EMAIL,
                "Представление": l["email"],
                "Значение": l["email"],
                "АдресЭП": l["email"]
            }
        ]
    }
    if l["phone"]:
        payload["КонтактнаяИнформация"].append({
            "LineNumber": "2",
            "Тип": "Телефон",
            "Вид_Key": CI_LEAD_CONTACT_PHONE,
            "Представление": l["phone"],
            "Значение": l["phone"],
            "НомерТелефона": l["phone"]
        })
    r = requests.post(f"{ONEC_BASE}/Catalog_КонтактыЛидов?$format=json", auth=ONEC_AUTH_WRITE, json=payload, timeout=15)
    print(f"Lead {l['name']}: {r.status_code}")
    if r.status_code in (200, 201):
        print(f"  Created Contact GUID: {r.json().get('Ref_Key')}")
    else:
        print(f"  Error: {r.text[:200]}")
