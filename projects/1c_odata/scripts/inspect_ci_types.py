#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import ONEC_BASE, ONEC_AUTH_READ

url = f"{ONEC_BASE}/Catalog_ВидыКонтактнойИнформации?$format=json"
r = requests.get(url, auth=ONEC_AUTH_READ, timeout=15)
if r.status_code == 200:
    for v in r.json().get('value', []):
        name = v.get('Description')
        parent = v.get('Родитель_Key')
        ref = v.get('Ref_Key')
        is_folder = v.get('IsFolder')
        print(f"Ref: {ref} | Folder: {is_folder} | Name: {name} | Parent: {parent}")
else:
    print(f"Error {r.status_code}: {r.text[:200]}")
