#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import ONEC_BASE, ONEC_AUTH_READ

guids = [
    ("s.erofeeva@unikom-service.ru", "45f4142a-cd21-11f1-974e-02006df8aab5"),
    ("pek31-73@yandex.ru", "0b118bd8-cd32-11f1-974e-02006df8aab5"),
    ("kae1465@bk.ru", "46d51e02-cd21-11f1-974e-02006df8aab5"),
    ("stropansnab@mail.ru", "60405242-cd23-11f1-974e-02006df8aab5")
]

catalogs = [
    "Catalog_АдресатыПисем",
    "Catalog_Лиды",
    "Catalog_Контрагенты",
    "Catalog_КонтактыЛидов",
    "Catalog_КонтактныеЛица"
]

for email, g in guids:
    print(f"\n--- GUID {g} (email {email}) ---")
    found = False
    for cat in catalogs:
        url = f"{ONEC_BASE}/{cat}(guid'{g}')?$format=json"
        try:
            r = requests.get(url, auth=ONEC_AUTH_READ, timeout=10)
            if r.status_code == 200:
                d = r.json()
                print(f"  НАЙДЕН В {cat}!")
                print(f"    Description: {d.get('Description')}")
                if 'Контакт' in d:
                    print(f"    Контакт: {d.get('Контакт')}, Контакт_Type: {d.get('Контакт_Type')}")
                if 'Адресат' in d:
                    print(f"    Адресат: {d.get('Адресат')}")
                found = True
                break
        except Exception as e:
            pass
    if not found:
        print("  НЕ НАЙДЕН в стандартных справочниках")
