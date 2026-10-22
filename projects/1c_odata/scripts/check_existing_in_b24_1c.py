#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поиск существующих сущностей в B24 и 1С:УНФ по 4 компаниям
"""

import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import call_b24, ONEC_BASE, ONEC_AUTH_READ

INNS = {
    "18550": {"inn": "3123416580", "title": 'ООО "ПРОМКОМПЛЕКТ"', "email": "pek31-73@yandex.ru", "phone": "+74722410995"},
    "18546": {"inn": "6684040828", "title": 'АО НПП "УНИКОМ-СЕРВИС"', "email": "s.erofeeva@unikom-service.ru", "phone": "+73439668710"},
    "18542": {"inn": "550613869941", "title": 'ИП Погребняк В.В.', "email": "stropansnab@mail.ru", "phone": "+79087987989"},
    "18548": {"inn": "4028062822", "title": 'ООО "ТД "ПРОМАЛЬЯНС"', "email": "kae1465@bk.ru", "phone": "+79208980600"}
}

def check_b24():
    print("=== ПРОВЕРКА В БИТРИКС24 ===")
    for lid, d in INNS.items():
        print(f"\nЛид #{lid} ({d['title']}, ИНН {d['inn']}):")
        
        # 1. Поиск компании по ИНН (UF_CRM_699421CD2A684 и UF_CRM_1720689408)
        comps = call_b24("crm.company.list", {
            "filter": {"=UF_CRM_699421CD2A684": d["inn"]},
            "select": ["ID", "TITLE", "UF_CRM_699421CD2A684"]
        }) or []
        if not comps:
            comps = call_b24("crm.company.list", {
                "filter": {"%TITLE": d["inn"]},
                "select": ["ID", "TITLE"]
            }) or []
        if not comps:
            # поиск по названию
            short_title = d["title"].replace('ООО', '').replace('АО', '').replace('НПП', '').replace('ИП', '').replace('ТД', '').replace('"', '').strip()
            comps = call_b24("crm.company.list", {
                "filter": {"%TITLE": short_title},
                "select": ["ID", "TITLE", "UF_CRM_699421CD2A684"]
            }) or []
        print(f"  Компании в B24: {comps}")
        
        # 2. Поиск контакта по email
        cnts = call_b24("crm.contact.list", {
            "filter": {"=EMAIL": d["email"]},
            "select": ["ID", "NAME", "LAST_NAME", "COMPANY_ID"]
        }) or []
        print(f"  Контакты по email ({d['email']}): {cnts}")

def check_1c():
    print("\n=== ПРОВЕРКА В 1С:УНФ ===")
    for lid, d in INNS.items():
        print(f"\nЛид #{lid} ({d['title']}, ИНН {d['inn']}):")
        inn = d["inn"]
        email = d["email"]
        
        # 1. Поиск Лида по Тема (ИНН)
        url_leads = f"{ONEC_BASE}/Catalog_Лиды?$filter=substringof('{inn}',Тема)&$format=json&$select=Ref_Key,Description,Тема,НаименованиеКомпании,СостояниеЛида_Key"
        try:
            r = requests.get(url_leads, auth=ONEC_AUTH_READ, timeout=15)
            leads_data = r.json().get("value", []) if r.status_code == 200 else []
            print(f"  Лиды в 1С по ИНН: {leads_data}")
        except Exception as e:
            print(f"  Ошибка поиска Лида 1С по ИНН: {e}")
            
        # 2. Поиск Лида по Email
        url_ci = f"{ONEC_BASE}/Catalog_Лиды?$filter=substringof('{email}',АдресЭПДляПоиска)&$format=json&$select=Ref_Key,Description,Тема,НаименованиеКомпании"
        try:
            r = requests.get(url_ci, auth=ONEC_AUTH_READ, timeout=15)
            leads_ci = r.json().get("value", []) if r.status_code == 200 else []
            print(f"  Лиды в 1С по Email: {leads_ci}")
        except Exception as e:
            print(f"  Ошибка поиска Лида 1С по Email: {e}")
            
        # 3. Поиск Контрагента в 1С по ИНН
        url_kontr = f"{ONEC_BASE}/Catalog_Контрагенты?$filter=ИНН eq '{inn}'&$format=json&$select=Ref_Key,Description,ИНН,КПП,Недействителен"
        try:
            r = requests.get(url_kontr, auth=ONEC_AUTH_READ, timeout=15)
            kontr_data = r.json().get("value", []) if r.status_code == 200 else []
            print(f"  Контрагенты в 1С по ИНН: {kontr_data}")
        except Exception as e:
            print(f"  Ошибка поиска Контрагента 1С: {e}")

if __name__ == "__main__":
    check_b24()
    check_1c()
