#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Получение полных профилей DaData по 4 контрагентам
"""

import os
import sys
import json
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from check_contractor import DADATA_TOKEN, format_revenue, calculate_scale

inns = [
    ("18550", "3123416580", 'ООО "ПРОМКОМПЛЕКТ"'),
    ("18546", "6684040828", 'АО НПП "УНИКОМ-СЕРВИС"'),
    ("18542", "550613869941", 'ИП Погребняк В.В.'),
    ("18548", "4028062822", 'ООО "ТД "ПРОМАЛЬЯНС"')
]

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Token {DADATA_TOKEN}"
}

profiles = {}

for lid, inn, label in inns:
    resp = requests.post(
        "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party",
        json={"query": inn},
        headers=headers,
        timeout=10
    )
    data = resp.json()
    suggs = data.get("suggestions", [])
    if not suggs:
        print(f"[{lid}] Не найден в DaData: {inn}")
        continue
    party = suggs[0]
    p_data = party.get("data", {})
    finance = p_data.get("finance") or {}
    revenue = finance.get("revenue")
    employee_count = p_data.get("employee_count")
    scale = calculate_scale(revenue, employee_count)
    rev_str = format_revenue(revenue)
    
    info = {
        "lead_id": lid,
        "inn": inn,
        "kpp": p_data.get("kpp"),
        "ogrn": p_data.get("ogrn"),
        "name_short": p_data.get("name", {}).get("short_with_opf") or party.get("value"),
        "name_full": p_data.get("name", {}).get("full_with_opf"),
        "address": p_data.get("address", {}).get("value"),
        "status": p_data.get("state", {}).get("status"),
        "director": p_data.get("management", {}).get("name") if p_data.get("management") else None,
        "okved": p_data.get("okved"),
        "okved_name": p_data.get("okved_name"),
        "revenue": revenue,
        "revenue_str": rev_str,
        "employee_count": employee_count,
        "scale": scale,
        "opf_type": p_data.get("opf", {}).get("type")
    }
    profiles[lid] = info
    print(f"\n=== Лид #{lid}: {info['name_short']} ===")
    print(f"ИНН: {inn}, КПП: {info['kpp']}, ОГРН: {info['ogrn']}")
    print(f"Адрес: {info['address']}")
    print(f"Руководитель: {info['director']}")
    print(f"ОКВЭД: {info['okved']} - {info['okved_name']}")
    print(f"Масштаб: {scale}, Выручка: {rev_str}, Сотрудников: {employee_count}")

with open("profiles_4_leads.json", "w", encoding="utf-8") as f:
    json.dump(profiles, f, ensure_ascii=False, indent=2)
