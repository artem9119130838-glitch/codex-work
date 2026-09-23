#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_contractor.py — Комплексная проверка контрагента по ИНН (DaData + Saby)
Автоматическое определение: Перепродажник, Производство, Конечный покупатель, Тендерщик.
"""

import sys
import re
import json
import argparse
import requests

# Настройка UTF-8 для консоли Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Credential defaults (из AGENTS.md)
DADATA_TOKEN = "17c6961838d6a750aeadd323d0aa06342f7044f9"
DADATA_SECRET = "84677c7916912e5ae132b4b7359d4f5ad0b69927"
SABY_LOGIN = "top-gk@yandex.ru"
SABY_PASS = "Artem159753!"

def get_dadata_info(inn: str) -> dict:
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {DADATA_TOKEN}"
    }
    try:
        resp = requests.post(url, json={"query": inn}, headers=headers, timeout=10)
        data = resp.json()
        if not data.get("suggestions"):
            return {"error": "Не найден в DaData"}
        
        party = data["suggestions"][0]
        p_data = party.get("data", {})
        
        name_short = p_data.get("name", {}).get("short_with_opf") or party.get("value")
        name_full = p_data.get("name", {}).get("full_with_opf")
        address = p_data.get("address", {}).get("value")
        status = p_data.get("state", {}).get("status") # ACTIVE, LIQUIDATED, etc.
        
        director = None
        if p_data.get("management"):
            director = p_data["management"].get("name")
            
        okved = p_data.get("okved")
        okved_name = p_data.get("okved_name")
        
        return {
            "inn": p_data.get("inn"),
            "kpp": p_data.get("kpp"),
            "ogrn": p_data.get("ogrn"),
            "name_short": name_short,
            "name_full": name_full,
            "address": address,
            "director": director,
            "status": status,
            "okved": okved,
            "okved_name": okved_name,
            "branch_type": p_data.get("branch_type") # MAIN, BRANCH
        }
    except Exception as e:
        return {"error": f"DaData error: {str(e)}"}

def get_saby_tender_info(inn: str) -> dict:
    session = requests.Session()
    # 1. Auth via JSON-RPC
    login_url = "https://online.sbis.ru/auth/service/"
    payload = {
        "jsonrpc": "2.0",
        "method": "СБИС.Аутентифицировать",
        "params": {
            "Параметр": {
                "Логин": SABY_LOGIN,
                "Пароль": SABY_PASS
            }
        },
        "id": 0
    }
    
    try:
        r = session.post(login_url, json=payload, timeout=10)
        sid = r.json().get("result")
        if not sid:
            return {"error": "Не удалось авторизоваться в Saby"}
            
        session.cookies.set("sid", sid, domain=".sbis.ru")
        session.headers.update({
            "X-SBISSessionID": sid,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        
        # 2. Get contractor page
        url = f"https://online.sbis.ru/page/contractor?inn={inn}"
        resp = session.get(url, timeout=15)
        text = resp.text
        
        tender_res = {
            "counter": 0,
            "is_participant": False,
            "participant_count": 0,
            "is_customer": False,
            "customer_count": 0,
            "details": []
        }
        
        tender_key = '["tender","Торги",'
        pos = text.find(tender_key)
        if pos != -1:
            start_obj = pos + len(tender_key)
            depth = 0
            end_obj = -1
            for i in range(start_obj, min(len(text), start_obj + 2500)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        end_obj = i + 1
                        break
            if end_obj != -1:
                t_json = json.loads(text[start_obj:end_obj])
                tender_res["counter"] = t_json.get("counter", 0)
                tender_res["is_participant"] = t_json.get("isMember", False)
                tender_res["is_customer"] = t_json.get("isOwner", False)
                for item in t_json.get("values", []):
                    subtitle = item.get("subtitle", "")
                    val = item.get("value", 0)
                    tooltip = item.get("tooltip", "")
                    tender_res["details"].append(f"{subtitle}: {val} ({tooltip})")
                    if "участник" in subtitle.lower():
                        tender_res["participant_count"] = val
                    elif "заказчик" in subtitle.lower():
                        tender_res["customer_count"] = val
                        
        return tender_res
    except Exception as e:
        return {"error": f"Saby error: {str(e)}"}

def classify_client(dadata_info: dict, saby_info: dict) -> dict:
    tags = []
    reasons = []
    
    okved = str(dadata_info.get("okved", "") or "")
    okved_name = str(dadata_info.get("okved_name", "") or "")
    p_cnt = saby_info.get("participant_count", 0)
    c_cnt = saby_info.get("customer_count", 0)
    name = (dadata_info.get("name_short") or "").lower()
    
    # 1. Проверка на Тендерщика
    if p_cnt > 0 or saby_info.get("is_participant"):
        tags.append("Тендер")
        reasons.append(f"Участий в торгах в качестве поставщика: {p_cnt}")
        
    # 2. Проверка на Производство
    # ОКВЭД 10..33 — Обрабатывающие производства
    is_production = False
    try:
        okved_prefix = int(okved.split(".")[0])
        if 10 <= okved_prefix <= 33:
            is_production = True
            tags.append("Производство")
            reasons.append(f"Производственный ОКВЭД: {okved} ({okved_name})")
    except Exception:
        pass
        
    # 3. Проверка на Перепродажника
    # Критерии:
    # - Основной ОКВЭД оптовой торговли (46.*)
    # - Активное участие в торгах как поставщик (> 5-10 участий)
    # - Либо в названии слова ТД, Торговый дом, Трейд, Снабжение при наличии оптовой торговли
    is_trade_okved = okved.startswith("46")
    is_reseller = False
    
    if is_trade_okved and p_cnt >= 5:
        is_reseller = True
        tags.append("Перепродажники")
        reasons.append(f"Торговый ОКВЭД 46 + активные поставки по тендерам ({p_cnt} участий)")
    elif p_cnt >= 20 and not is_production:
        is_reseller = True
        tags.append("Перепродажники")
        reasons.append(f"Массовый участник торгов ({p_cnt} участий) без производства")
    elif is_trade_okved and any(w in name for w in ["торговый дом", " тд ", "трейд", "снабжение", "комплект"]):
        is_reseller = True
        tags.append("Перепродажники")
        reasons.append("Торговый ОКВЭД 46 и явное торговое наименование компании")
        
    # 4. Если не перепродажник и не производство
    if not is_reseller and not is_production:
        tags.append("Конечный покупатель")
        reasons.append("Компания приобретает оборудование под собственные нужды / объекты")
    elif is_production and not is_reseller:
        tags.append("Конечный покупатель")
        
    return {
        "verdict": "ПЕРЕПРОДАЖНИК" if is_reseller else ("ПРОИЗВОДСТВО" if is_production else "КОНЕЧНЫЙ ПОКУПАТЕЛЬ"),
        "recommended_tags": list(set(tags)),
        "reasons": reasons
    }

def main():
    parser = argparse.ArgumentParser(description="Проверка контрагента по ИНН через DaData и Saby")
    parser.add_argument("inn", help="ИНН организации (10 или 12 цифр)")
    parser.add_argument("--json", action="store_true", help="Вывод в формате JSON")
    args = parser.parse_args()

    inn = args.inn.strip()
    dadata = get_dadata_info(inn)
    saby = get_saby_tender_info(inn)
    classification = classify_client(dadata, saby)

    result = {
        "inn": inn,
        "dadata": dadata,
        "saby": saby,
        "classification": classification
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print("=" * 60)
    print(f"РЕЗУЛЬТАТ ПРОВЕРКИ КОНТРАГЕНТА: ИНН {inn}")
    print("=" * 60)
    print(f"Организация : {dadata.get('name_short', 'Не определено')}")
    print(f"Юр. адрес   : {dadata.get('address', 'Не определено')}")
    print(f"Руководитель: {dadata.get('director', 'Не определено')}")
    print(f"Статус      : {dadata.get('status', 'Не определено')}")
    print(f"ОКВЭД       : {dadata.get('okved')} — {dadata.get('okved_name')}")
    print("-" * 60)
    print(f"Торги Saby  : Участник (поставщик): {saby.get('participant_count', 0)} | Заказчик: {saby.get('customer_count', 0)}")
    if saby.get("details"):
        print(f"Детали      : {', '.join(saby['details'])}")
    print("=" * 60)
    print(f"ИТОГОВЫЙ ВЕРДИКТ: {classification['verdict']}")
    print(f"Рекомендуемые теги 1С: {', '.join(classification['recommended_tags'])}")
    print(f"Обоснование: {'; '.join(classification['reasons'])}")
    print("=" * 60)

if __name__ == "__main__":
    main()
