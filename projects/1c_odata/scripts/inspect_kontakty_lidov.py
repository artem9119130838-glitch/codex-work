#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import ONEC_BASE, ONEC_AUTH_READ

# Inspect one record of Catalog_КонтактыЛидов
url = f"{ONEC_BASE}/Catalog_КонтактыЛидов?$format=json&$top=1"
r = requests.get(url, auth=ONEC_AUTH_READ, timeout=10)
if r.status_code == 200:
    val = r.json().get("value", [])
    if val:
        print("Fields in Catalog_КонтактыЛидов:")
        for k, v in val[0].items():
            print(f"  {k}: {repr(v)[:80]}")
    else:
        print("Catalog_КонтактыЛидов is empty")
else:
    print(f"Error {r.status_code}: {r.text[:200]}")
