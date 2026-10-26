"""
manage_b24_company_requisites.py
================================
Модуль и CLI-скрипт управления системными реквизитами компаний Битрикс24 (crm.requisite).

Позволяет автоматически наполнять штатный блок реквизитов Битрикс24 (crm.requisite)
100% официальными данными из ЕГРЮЛ/ЕГРИП через DaData API:
- Краткое наименование (RQ_COMPANY_NAME)
- Полное наименование (RQ_COMPANY_FULL_NAME)
- ИНН (RQ_INN)
- КПП (RQ_KPP)
- ОГРН / ОГРНИП (RQ_OGRN / RQ_OGRNIP)
- Руководитель / Генеральный директор (RQ_DIRECTOR)
- Дата регистрации (RQ_COMPANY_REG_DATE)
- Юридический адрес (crm.address.add, TYPE_ID=6, ENTITY_TYPE_ID=8)
- Привязка системного реквизита (crm.requisite.link.register)

Использование:
  py manage_b24_company_requisites.py --company-id 5322 --dry-run
  py manage_b24_company_requisites.py --company-id 12548 --inn 7707376106 --dry-run
  py manage_b24_company_requisites.py --company-id 12548 --inn 7707376106
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime

# Импорт вспомогательных функций из базового контура 1C/CRM
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from process_b24_inbound_leads import call_b24, load_dotenv

PRESET_RU_COMPANY = 1     # Организация РФ (Юрлицо)
PRESET_RU_INDIVIDUAL = 3  # ИП РФ
PRESET_RU_PERSON = 5      # Физ. лицо РФ

ENTITY_TYPE_COMPANY = 4   # CRM Компания
ENTITY_TYPE_REQUISITE = 8 # CRM Реквизит
ADDRESS_TYPE_LEGAL = 6    # Юридический адрес
ADDRESS_TYPE_ACTUAL = 1   # Фактический адрес


def get_dadata_token() -> str:
    """Извлекает токен DaData из окружения."""
    load_dotenv()
    return os.getenv("DADATA_API_KEY") or os.getenv("DADATA_TOKEN") or ""


def fetch_party_by_inn(inn: str) -> dict:
    """
    Запрашивает официальные реквизиты контрагента по ИНН через DaData API.
    """
    token = get_dadata_token()
    if not token:
        print("[DADATA-ERROR] Токен DaData не найден в переменных окружения (.env).")
        return {}

    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {token}"
    }
    try:
        resp = requests.post(url, json={"query": inn.strip()}, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            suggestions = data.get("suggestions", [])
            if suggestions:
                return suggestions[0]
        else:
            print(f"[DADATA-WARN] DaData HTTP {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"[DADATA-ERROR] Сбой запроса к DaData: {e}")
    return {}


def format_reg_date(ts_ms) -> str:
    """Преобразует timestamp DaData в формат ДД.ММ.ГГГГ для Битрикс24."""
    if not ts_ms:
        return ""
    try:
        dt = datetime.fromtimestamp(ts_ms / 1000.0)
        return dt.strftime("%d.%m.%Y")
    except Exception:
        return ""


def enrich_company_requisites(company_id: int, inn: str = None, dry_run: bool = False) -> dict:
    """
    Создает или обновляет системные реквизиты (crm.requisite) компании в Битрикс24.
    """
    print(f"\n===========================================================================")
    print(f">>> [УПРАВЛЕНИЕ РЕКВИЗИТАМИ КОМПАНИИ #{company_id}] (Режим: {'DRY-RUN' if dry_run else 'БОЕВОЙ'})")
    print(f"===========================================================================")

    # 1. Получаем карточку компании из Битрикс24
    comp = call_b24("crm.company.get", {"id": company_id})
    if not comp:
        print(f"[ERROR] Компания #{company_id} не найдена в Битрикс24.")
        return {"status": "error", "error": "Company not found"}

    comp_title = comp.get("TITLE", "")
    current_inn = inn or comp.get("UF_CRM_699421CD2A684") or ""

    # Если ИНН не передан, проверяем уже имеющийся реквизит
    if not current_inn:
        existing_reqs = call_b24("crm.requisite.list", {
            "filter": {"ENTITY_TYPE_ID": ENTITY_TYPE_COMPANY, "ENTITY_ID": company_id}
        })
        if existing_reqs:
            for r in existing_reqs:
                if r.get("RQ_INN"):
                    current_inn = r.get("RQ_INN")
                    break

    if not current_inn:
        print(f"[ERROR] Не удалось определить ИНН для Компании #{company_id} ('{comp_title}'). Укажите --inn <ИНН>.")
        return {"status": "error", "error": "No INN provided or found"}

    print(f"  Компания: '{comp_title}' (ID: {company_id})")
    print(f"  Целевой ИНН: {current_inn}")

    # 2. Получаем официальные регистрационные данные из ЕГРЮЛ через DaData
    party = fetch_party_by_inn(current_inn)
    if not party:
        print(f"[ERROR] Контрагент с ИНН {current_inn} не найден в базе DaData / ЕГРЮЛ.")
        return {"status": "error", "error": "Party not found in DaData"}

    data = party.get("data", {})
    party_type = data.get("type", "LEGAL") # LEGAL (Юрлицо) или INDIVIDUAL (ИП)
    preset_id = PRESET_RU_INDIVIDUAL if party_type == "INDIVIDUAL" else PRESET_RU_COMPANY

    short_name = data.get("name", {}).get("short_with_opf") or party.get("value", "")
    full_name = data.get("name", {}).get("full_with_opf") or short_name
    kpp = data.get("kpp") or ""
    ogrn = data.get("ogrn") or ""
    director = data.get("management", {}).get("name") or ""
    reg_date = format_reg_date(data.get("state", {}).get("registration_date"))
    address_val = data.get("address", {}).get("value") or ""
    addr_data = data.get("address", {}).get("data", {}) or {}

    print(f"  [DADATA] Официальное наименование: {full_name}")
    print(f"  [DADATA] Краткое наименование: {short_name}")
    print(f"  [DADATA] Тип: {'Юрлицо (Пресет 1)' if preset_id == PRESET_RU_COMPANY else 'ИП (Пресет 3)'}")
    print(f"  [DADATA] КПП: {kpp} | ОГРН: {ogrn}")
    print(f"  [DADATA] Руководитель: {director}")
    print(f"  [DADATA] Дата рег.: {reg_date}")
    print(f"  [DADATA] Юр. адрес: {address_val}")

    # 3. Проверяем наличие существующих системных реквизитов у компании
    existing_reqs = call_b24("crm.requisite.list", {
        "filter": {"ENTITY_TYPE_ID": ENTITY_TYPE_COMPANY, "ENTITY_ID": company_id}
    })

    req_payload = {
        "ENTITY_TYPE_ID": ENTITY_TYPE_COMPANY,
        "ENTITY_ID": company_id,
        "PRESET_ID": preset_id,
        "NAME": "Основной реквизит",
        "RQ_INN": current_inn,
        "RQ_KPP": kpp,
        "RQ_OGRN": ogrn if preset_id == PRESET_RU_COMPANY else "",
        "RQ_OGRNIP": ogrn if preset_id == PRESET_RU_INDIVIDUAL else "",
        "RQ_COMPANY_NAME": short_name,
        "RQ_COMPANY_FULL_NAME": full_name,
        "RQ_DIRECTOR": director,
        "RQ_COMPANY_REG_DATE": reg_date,
        "ADDRESS_ONLY": "N",
        "ACTIVE": "Y"
    }

    requisite_id = None
    if existing_reqs:
        # Обновляем первый активный реквизит (исключая иммутабельные поля)
        requisite_id = int(existing_reqs[0].get("ID"))
        update_fields = {k: v for k, v in req_payload.items() if k not in ["ENTITY_TYPE_ID", "ENTITY_ID", "PRESET_ID"]}
        print(f"\n  [crm.requisite] Найден существующий реквизит ID #{requisite_id}. Будет обновлен.")
        if dry_run:
            print(f"  [DRY-RUN] Вызов crm.requisite.update(id={requisite_id}, fields={update_fields})")
        else:
            call_b24("crm.requisite.update", {"id": requisite_id, "fields": update_fields})
            print(f"  [SUCCESS] Реквизит ID #{requisite_id} успешно обновлен официальными данными!")
    else:
        # Создаем новый системный реквизит
        print(f"\n  [crm.requisite] Системные реквизиты отсутствуют. Будет создан новый блок.")
        if dry_run:
            print(f"  [DRY-RUN] Вызов crm.requisite.add(fields={req_payload})")
            requisite_id = 99999
        else:
            res = call_b24("crm.requisite.add", {"fields": req_payload})
            requisite_id = int(res) if res else None
            print(f"  [SUCCESS] Создан новый системный реквизит ID #{requisite_id}!")

    # 4. Привязываем юридический адрес к реквизиту (crm.address.add)
    if requisite_id and address_val:
        addr_payload = {
            "TYPE_ID": ADDRESS_TYPE_LEGAL,
            "ENTITY_TYPE_ID": ENTITY_TYPE_REQUISITE,
            "ENTITY_ID": requisite_id,
            "ADDRESS_1": f"{addr_data.get('street_with_type', '')} {addr_data.get('house_type', '')} {addr_data.get('house', '')}".strip() or address_val,
            "CITY": addr_data.get("city") or addr_data.get("region") or "",
            "POSTAL_CODE": addr_data.get("postal_code") or "",
            "PROVINCE": addr_data.get("region_with_type") or "",
            "COUNTRY": "Россия",
            "COUNTRY_CODE": "RU"
        }
        if dry_run:
            print(f"  [DRY-RUN] Вызов crm.address.add(fields={addr_payload})")
        else:
            try:
                # Проверим, есть ли уже юр. адрес
                existing_addrs = call_b24("crm.address.list", {
                    "filter": {"ENTITY_TYPE_ID": ENTITY_TYPE_REQUISITE, "ENTITY_ID": requisite_id, "TYPE_ID": ADDRESS_TYPE_LEGAL}
                })
                if not existing_addrs:
                    call_b24("crm.address.add", {"fields": addr_payload})
                    print(f"  [SUCCESS] Юридический адрес успешно привязан к реквизиту #{requisite_id}.")
                else:
                    print(f"  [crm.address] Юридический адрес уже существует для реквизита #{requisite_id}.")
            except Exception as e:
                print(f"  [WARN] Ошибка привязки адреса: {e}")

    # 6. Дублируем ИНН в пользовательское поле компании для обратной совместимости
    if not dry_run and current_inn and comp.get("UF_CRM_699421CD2A684") != current_inn:
        call_b24("crm.company.update", {
            "id": company_id,
            "fields": {"UF_CRM_699421CD2A684": current_inn}
        })
        print(f"  [crm.company.update] ИНН {current_inn} синхронизирован в карточку компании.")

    return {
        "status": "success",
        "company_id": company_id,
        "requisite_id": requisite_id,
        "inn": current_inn,
        "short_name": short_name,
        "full_name": full_name,
        "kpp": kpp,
        "ogrn": ogrn,
        "director": director,
        "address": address_val
    }


def main():
    parser = argparse.ArgumentParser(description="Управление системными реквизитами компаний Битрикс24 через DaData")
    parser.add_argument("--company-id", type=int, required=True, help="ID компании в Битрикс24")
    parser.add_argument("--inn", type=str, default=None, help="ИНН контрагента (если не указан, берется из CRM)")
    parser.add_argument("--dry-run", action="store_true", help="Режим симуляции без внесения изменений")

    args = parser.parse_args()
    enrich_company_requisites(args.company_id, inn=args.inn, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
