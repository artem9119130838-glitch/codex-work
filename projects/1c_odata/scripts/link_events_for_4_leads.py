#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Привязка всех входящих событий Document_Событие и адресатов Catalog_АдресатыПисем
к созданным Лидам 1С:УНФ
"""

import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import ONEC_BASE, ONEC_AUTH_READ, ONEC_AUTH_WRITE

leads = [
    {
        "lead_guid": "a09ae362-cd36-11f1-974e-02006df8aab5",
        "title": 'ООО "ПРОМКОМПЛЕКТ"',
        "emails": ["pek31-73@yandex.ru", "pekomp@yandex.ru"],
        "adr_guid": "0b118bd8-cd32-11f1-974e-02006df8aab5"
    },
    {
        "lead_guid": "bd3c4830-cd36-11f1-974e-02006df8aab5",
        "title": 'АО НПП "УНИКОМ-СЕРВИС"',
        "emails": ["s.erofeeva@unikom-service.ru", "info@unikom-service.ru"],
        "adr_guid": "45f4142a-cd21-11f1-974e-02006df8aab5"
    },
    {
        "lead_guid": "d1034468-cd36-11f1-974e-02006df8aab5",
        "title": 'ИП Погребняк В.В.',
        "emails": ["stropansnab@mail.ru", "stropan@mail.ru"],
        "adr_guid": "60405242-cd23-11f1-974e-02006df8aab5"
    },
    {
        "lead_guid": "e19b44ec-cd36-11f1-974e-02006df8aab5",
        "title": 'ООО "ТД "ПРОМАЛЬЯНС"',
        "emails": ["kae1465@bk.ru", "zakaz@oootdpa.ru"],
        "adr_guid": "46d51e02-cd21-11f1-974e-02006df8aab5"
    }
]

print("=== 1. Актуализация Catalog_АдресатыПисем ===")
for l in leads:
    guid = l["lead_guid"]
    title = l["title"]
    adr_guid = l["adr_guid"]
    payload = {
        "Description": title,
        "Контакт": guid,
        "Контакт_Type": "StandardODATA.Catalog_Лиды"
    }
    r = requests.patch(
        f"{ONEC_BASE}/Catalog_АдресатыПисем(guid'{adr_guid}')?$format=json",
        auth=ONEC_AUTH_WRITE,
        json=payload,
        timeout=10
    )
    print(f"Адресат {title} ({adr_guid}): HTTP {r.status_code}")

print("\n=== 2. Привязка Document_Событие к Лидам ===")
url_ev = f"{ONEC_BASE}/Document_Событие?$format=json&$top=150&$orderby=Date desc"
r_ev = requests.get(url_ev, auth=ONEC_AUTH_READ, timeout=20)
if r_ev.status_code == 200:
    events = r_ev.json().get("value", [])
    print(f"Получено {len(events)} последних событий.")
    total_linked = 0
    for ev in events:
        ev_id = ev.get("Ref_Key")
        parts = ev.get("Участники", [])
        for p in parts:
            c_str = p.get("КакСвязаться", "").strip().lower()
            for l in leads:
                for em in l["emails"]:
                    if em.lower() == c_str:
                        ev_payload = {
                            "КонтактыПеренесены": True,
                            "Участники": [
                                {
                                    "LineNumber": "1",
                                    "КакСвязаться": em,
                                    "НомерДляОтправки": "",
                                    "ИдентификаторСообщения": "",
                                    "СтатусДоставки": "",
                                    "ТипПолучателяЭлектронногоПисьма": "ОтКого",
                                    "Контакт": l["lead_guid"],
                                    "Контакт_Type": "StandardODATA.Catalog_Лиды"
                                }
                            ]
                        }
                        r_patch = requests.patch(
                            f"{ONEC_BASE}/Document_Событие(guid'{ev_id}')?$format=json",
                            auth=ONEC_AUTH_WRITE,
                            json=ev_payload,
                            timeout=10
                        )
                        print(f"Событие {ev.get('Тема')} ({ev_id}) -> Лид {l['title']}: HTTP {r_patch.status_code}")
                        if r_patch.status_code in (200, 204):
                            total_linked += 1
    print(f"Всего успешно привязано событий: {total_linked}")
