#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import ONEC_BASE, ONEC_AUTH_READ

emails = [
    "pek31-73@yandex.ru",
    "s.erofeeva@unikom-service.ru",
    "stropansnab@mail.ru",
    "kae1465@bk.ru"
]

print("=== Поиск Document_Событие в 1С:УНФ по email ===")
url = f"{ONEC_BASE}/Document_Событие?$format=json&$top=100&$orderby=Date desc"
r = requests.get(url, auth=ONEC_AUTH_READ, timeout=15)
if r.status_code == 200:
    events = r.json().get("value", [])
    print(f"Всего получено последних событий: {len(events)}")
    for ev in events:
        parts = ev.get("Участники", [])
        for p in parts:
            contact_str = p.get("КакСвязаться", "").lower()
            for em in emails:
                if em.lower() in contact_str:
                    print(f"Найдено событие! GUID: {ev.get('Ref_Key')}, Дата: {ev.get('Date')}, Тема: {ev.get('Тема')}, Email: {em}, Контакт: {p.get('Контакт')}")
else:
    print(f"Ошибка OData: {r.status_code}")
