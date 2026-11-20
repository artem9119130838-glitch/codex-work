#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from check_contractor import DADATA_TOKEN, B24_WEBHOOK

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Token {DADATA_TOKEN}"
}

def search_dadata(query):
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/party"
    resp = requests.post(url, json={"query": query}, headers=headers, timeout=10)
    data = resp.json()
    return data.get("suggestions", [])

print("=== DaData Search: ИП Погребняк ===")
res = search_dadata("ИП Погребняк В.В.")
for r in res[:5]:
    d = r.get("data", {})
    print(r.get("value"), "| ИНН:", d.get("inn"), "| ОГРНИП:", d.get("ogrn"), "| Адрес:", d.get("address", {}).get("value"))

print("\n=== DaData Search: ПРОМКОМПЛЕКТ Белгород ===")
res = search_dadata("ООО ПРОМКОМПЛЕКТ Белгород")
for r in res[:5]:
    d = r.get("data", {})
    print(r.get("value"), "| ИНН:", d.get("inn"), "| Адрес:", d.get("address", {}).get("value"), "| Руководитель:", d.get("management", {}).get("name"))

print("\n=== DaData Search: АО НПП Уником-Сервис ===")
res = search_dadata("АО НПП Уником-Сервис")
for r in res[:3]:
    d = r.get("data", {})
    print(r.get("value"), "| ИНН:", d.get("inn"), "| Адрес:", d.get("address", {}).get("value"))
