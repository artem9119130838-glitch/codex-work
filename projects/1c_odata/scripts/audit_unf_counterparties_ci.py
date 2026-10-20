#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
audit_unf_counterparties_ci.py — Сплошной аппаратный аудит видов контактной информации контрагентов 1С:УНФ.
Защита от сбоя синхронизации EnterpriseData УНФ ↔ Бухгалтерия (Strict CI Invariant).

Выявляет контрагентов, у которых по ошибке записан вид КИ лида:
  - Ошибочный: 5c0dc769-23c6-11ed-91a8-a068f8f3337c (EmailКомпанииЛида)
  - Канонический: 5c0dc758-23c6-11ed-91a8-a068f8f3337c (EmailКонтрагента)

Использование:
  py projects/1c_odata/scripts/audit_unf_counterparties_ci.py
  py projects/1c_odata/scripts/audit_unf_counterparties_ci.py --fix
"""

import os
import sys
import argparse
import requests
from requests.auth import HTTPBasicAuth

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def _load_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v

_load_env()

ODATA_BASE = os.getenv("ONEC_ODATA_URL", "http://artem.medianasoft.spb.ru/unf/odata/standard.odata")
ODATA_USER = os.getenv("ONEC_ODATA_USER", "odata.writer")
ODATA_PASS = os.getenv("ONEC_ODATA_PASSWORD", "")

CI_LEAD_EMAIL = "5c0dc769-23c6-11ed-91a8-a068f8f3337c"
CI_CP_EMAIL = "5c0dc758-23c6-11ed-91a8-a068f8f3337c"

def run_audit(fix_mode=False):
    auth = HTTPBasicAuth(ODATA_USER, ODATA_PASS)
    headers = {"Accept": "application/json"}
    
    print(f"[*] Старт аппаратного аудита контрагентов 1С:УНФ ({ODATA_BASE})...")
    print(f"[*] Режим: {'ИСПРАВЛЕНИЕ (--fix)' if fix_mode else 'ТОЛЬКО ЧТЕНИЕ (Audit)'}")
    
    url = f"{ODATA_BASE}/Catalog_Контрагенты?$format=json&$select=Ref_Key,Description,Code,ИНН,КонтактнаяИнформация&$filter=DeletionMark eq false"
    
    total_checked = 0
    defective_count = 0
    fixed_count = 0
    
    while url:
        r = requests.get(url, auth=auth, headers=headers, timeout=30)
        if r.status_code != 200:
            print(f"[ERROR] Ошибка запроса OData: {r.status_code} - {r.text[:200]}")
            sys.exit(1)
            
        data = r.json()
        items = data.get("value", [])
        for cp in items:
            total_checked += 1
            guid = cp.get("Ref_Key")
            name = cp.get("Description", "")
            code = cp.get("Code", "")
            inn = cp.get("ИНН", "")
            ci_rows = cp.get("КонтактнаяИнформация", [])
            
            lead_ci_rows = [r for r in ci_rows if r.get("Вид_Key") == CI_LEAD_EMAIL]
            if lead_ci_rows:
                defective_count += 1
                print(f"[DEFECT] Контрагент '{name}' (Код: {code}, ИНН: {inn}, GUID: {guid}) содержит {len(lead_ci_rows)} записей EmailКомпанииЛида!")
                
                if fix_mode:
                    new_ci = []
                    for row in ci_rows:
                        r_copy = dict(row)
                        if r_copy.get("Вид_Key") == CI_LEAD_EMAIL:
                            r_copy["Вид_Key"] = CI_CP_EMAIL
                        new_ci.append(r_copy)
                    
                    patch_url = f"{ODATA_BASE}/Catalog_Контрагенты(guid'{guid}')?$format=json"
                    r_patch = requests.patch(patch_url, json={"КонтактнаяИнформация": new_ci}, auth=auth, headers=headers, timeout=20)
                    if r_patch.status_code == 200:
                        fixed_count += 1
                        print(f"  --> [FIXED OK] Контактная информация контрагента '{name}' успешно исправлена.")
                    else:
                        print(f"  --> [FIX FAILED] Ошибка PATCH: {r_patch.status_code} - {r_patch.text[:200]}")
                        
        next_link = data.get("odata.nextLink")
        if next_link:
            url = f"{ODATA_BASE}/{next_link}" if not next_link.startswith("http") else next_link
        else:
            url = None

    print("\n" + "=" * 60)
    print(f"ИТОГ АУДИТА:")
    print(f"  - Всего проверено контрагентов: {total_checked}")
    print(f"  - Выявлено дефектов вида КИ: {defective_count}")
    if fix_mode:
        print(f"  - Успешно исправлено: {fixed_count}")
    print("=" * 60)
    
    if defective_count == 0:
        print("[SUCCESS] База 1С:УНФ находится в зеленой зоне. Дефектов видов КИ не обнаружено.")
    else:
        print(f"[WARNING] Обнаружено {defective_count} дефектов. Рекомендуется запустить с флагом --fix.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Аудит видов контактной информации контрагентов 1С:УНФ")
    parser.add_argument("--fix", action="store_true", help="Автоматически исправить дефектные виды КИ на EmailКонтрагента")
    args = parser.parse_args()
    
    run_audit(fix_mode=args.fix)
