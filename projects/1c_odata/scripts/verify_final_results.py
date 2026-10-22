#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import ONEC_BASE, ONEC_AUTH_READ, call_b24

leads = [
    {"lid": 18550, "cid": 12522, "cnt_id": 16884, "lead_guid": "a09ae362-cd36-11f1-974e-02006df8aab5", "title": 'ООО "ПРОМКОМПЛЕКТ"'},
    {"lid": 18546, "cid": 12524, "cnt_id": 16886, "lead_guid": "bd3c4830-cd36-11f1-974e-02006df8aab5", "title": 'АО НПП "УНИКОМ-СЕРВИС"'},
    {"lid": 18542, "cid": 12526, "cnt_id": 16888, "lead_guid": "d1034468-cd36-11f1-974e-02006df8aab5", "title": 'ИП Погребняк В.В.'},
    {"lid": 18548, "cid": 12528, "cnt_id": 16890, "lead_guid": "e19b44ec-cd36-11f1-974e-02006df8aab5", "title": 'ООО "ТД "ПРОМАЛЬЯНС"'}
]

print("=== ФИНАЛЬНАЯ ВЕРИФИКАЦИЯ РЕЗУЛЬТАТОВ ===")
for item in leads:
    lid = item["lid"]
    cid = item["cid"]
    cnt_id = item["cnt_id"]
    guid = item["lead_guid"]
    title = item["title"]
    
    # 1. B24 Lead
    b24_l = call_b24("crm.lead.get", {"id": lid})
    status = b24_l.get("STATUS_ID")
    b_cid = b24_l.get("COMPANY_ID")
    b_cnt = b24_l.get("CONTACT_ID")
    
    # 2. B24 Company
    comp = call_b24("crm.company.get", {"id": cid})
    comp_title = comp.get("TITLE") if comp else "NOT FOUND"
    inn = comp.get("UF_CRM_699421CD2A684") if comp else ""
    
    # 3. 1C Lead
    r_1c = requests.get(f"{ONEC_BASE}/Catalog_Лиды(guid'{guid}')?$format=json", auth=ONEC_AUTH_READ, timeout=10)
    c1_title = r_1c.json().get("Description") if r_1c.status_code == 200 else "ERR"
    c1_ci_len = len(r_1c.json().get("КонтактнаяИнформация", [])) if r_1c.status_code == 200 else 0
    c1_tags_len = len(r_1c.json().get("Теги", [])) if r_1c.status_code == 200 else 0
    
    print(f"\n[{lid}] {title}:")
    print(f"  Б24 Лид: статус={status}, Company_ID={b_cid}, Contact_ID={b_cnt}")
    print(f"  Б24 Компания: ID={cid}, Название='{comp_title}', ИНН={inn}")
    print(f"  1С:УНФ Лид: GUID={guid}, Description='{c1_title}', Строк КИ={c1_ci_len}, Тегов={c1_tags_len}")

# Verify no deals were created for these leads
for item in leads:
    deals = call_b24("crm.deal.list", {"filter": {"LEAD_ID": item["lid"]}}) or []
    assert len(deals) == 0, f"Error: Deal found for lead {item['lid']}"
print("\n[OK] Проверка подтвердила: ни одной сделки по лидам создано НЕ БЫЛО!")
