#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import call_b24

emails = [
    "pek31-73@yandex.ru",
    "s.erofeeva@unikom-service.ru",
    "stropansnab@mail.ru",
    "kae1465@bk.ru"
]

inns = [
    "3123416580",
    "6684040828",
    "550613869941",
    "4028062822"
]

print("=== Поиск Контактов в Б24 по email ===")
for em in emails:
    res = call_b24("crm.contact.list", {"filter": {"EMAIL": em}, "select": ["ID", "NAME", "LAST_NAME", "COMPANY_ID", "EMAIL"]})
    print(f"Email {em}: found {len(res) if res else 0}")
    if res:
        for c in res:
            print(f"  ID: {c.get('ID')}, Name: {c.get('NAME')} {c.get('LAST_NAME')}, Company: {c.get('COMPANY_ID')}")

print("\n=== Поиск Компаний в Б24 по ИНН ===")
for inn in inns:
    # check UF_CRM_699421CD2A684 (custom field for INN)
    res = call_b24("crm.company.list", {"filter": {"UF_CRM_699421CD2A684": inn}, "select": ["ID", "TITLE", "UF_CRM_699421CD2A684"]})
    print(f"INN {inn}: found {len(res) if res else 0}")
    if res:
        for c in res:
            print(f"  ID: {c.get('ID')}, Title: {c.get('TITLE')}")
