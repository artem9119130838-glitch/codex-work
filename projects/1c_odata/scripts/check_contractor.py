#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/check_contractor.py
============================================
Комплексная проверка и обогащение досье контрагента по ИНН (DaData + Saby/СБИС).
Автоматическое определение: Перепродажник, Производство, Конечный покупатель, Тендерщик.
Сквозная синхронизация результатов скоринга в 3 системы:
1. marketing_db (PostgreSQL / DWH)
2. CRM Битрикс24 (поле COMMENTS Компании/Лида + закрепленный комментарий таймлайна)
3. 1С:УНФ (поле Комментарий Контрагента/Лида + Теги классификации)

Регламенты: AGENTS.md, token_guard, ERP_1C_POLICY.md, LEAD_REACTIVATION_POLICY.md.
"""

import os
import sys
import re
import json
import argparse
import datetime
import requests

if sys.platform == 'win32' and sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.platform == 'win32' and sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8')

def _load_env():
    # Ищем .env в директории 1c_odata или корне
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
    ]
    for env_file in possible_paths:
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

DADATA_TOKEN = os.getenv("DADATA_TOKEN", "17c6961838d6a750aeadd323d0aa06342f7044f9")
DADATA_SECRET = os.getenv("DADATA_SECRET", "84677c7916912e5ae132b4b7359d4f5ad0b69927")
SABY_LOGIN = os.getenv("SABY_LOGIN", "top-gk@yandex.ru")
SABY_PASS = os.getenv("SABY_USER_PASSWORD", "Artem159753!")

B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
ODATA_BASE = os.getenv("ONEC_ODATA_URL", "http://artem.medianasoft.spb.ru/unf/odata/standard.odata")
ODATA_USER = os.getenv("ONEC_ODATA_USER", "odata.writer")
ODATA_PASS = os.getenv("ONEC_ODATA_PASSWORD", "")


def format_revenue(revenue) -> str:
    if not revenue:
        return "Не раскрыта"
    try:
        rev = float(revenue)
        if rev >= 1_000_000_000:
            return f"{rev / 1_000_000_000:.1f} млрд руб."
        elif rev >= 1_000_000:
            return f"{rev / 1_000_000:.1f} млн руб."
        elif rev >= 1_000:
            return f"{rev / 1_000:.1f} тыс. руб."
        return f"{rev:,.0f} руб.".replace(",", " ")
    except Exception:
        return str(revenue)


def calculate_scale(revenue, employee_count) -> str:
    rev = revenue or 0
    emp = employee_count or 0
    try:
        rev = float(rev)
        emp = int(emp)
    except Exception:
        pass
    if rev > 2_000_000_000 or emp > 250:
        return "Крупный бизнес"
    elif rev > 800_000_000 or emp > 100:
        return "Средний бизнес"
    elif rev > 120_000_000 or emp > 15:
        return "Малый бизнес"
    elif rev > 0 or emp > 0:
        return "Микропредприятие"
    return "Не определен"


def get_dadata_info(inn: str) -> dict:
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {DADATA_TOKEN}"
    }
    clean_inn = "".join(filter(str.isdigit, str(inn)))
    try:
        resp = requests.post(url, json={"query": clean_inn}, headers=headers, timeout=10)
        data = resp.json()
        if not data.get("suggestions"):
            return {"error": "Не найден в DaData"}
        
        party = data["suggestions"][0]
        p_data = party.get("data", {})
        
        name_short = p_data.get("name", {}).get("short_with_opf") or party.get("value")
        name_full = p_data.get("name", {}).get("full_with_opf")
        address = p_data.get("address", {}).get("value")
        status = p_data.get("state", {}).get("status")
        
        director = None
        if p_data.get("management"):
            director = p_data["management"].get("name")
            
        okved = p_data.get("okved")
        okved_name = p_data.get("okved_name")
        branch_type = p_data.get("branch_type") # MAIN, BRANCH
        branch_count = p_data.get("branch_count", 0)
        is_holding = (branch_type == "MAIN" and branch_count > 0) or bool(p_data.get("authorities"))

        finance = p_data.get("finance") or {}
        revenue = finance.get("revenue")
        income = finance.get("income")
        fin_year = finance.get("year")
        employee_count = p_data.get("employee_count")
        
        return {
            "inn": p_data.get("inn") or clean_inn,
            "kpp": p_data.get("kpp"),
            "ogrn": p_data.get("ogrn"),
            "name_short": name_short,
            "name_full": name_full,
            "address": address,
            "director": director,
            "status": status,
            "okved": okved,
            "okved_name": okved_name,
            "branch_type": branch_type,
            "is_holding": is_holding,
            "revenue": revenue,
            "income": income,
            "fin_year": fin_year,
            "employee_count": employee_count
        }
    except Exception as e:
        return {"error": f"DaData error: {str(e)}"}


def get_saby_tender_info(inn: str) -> dict:
    session = requests.Session()
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
    
    clean_inn = "".join(filter(str.isdigit, str(inn)))
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
        
        url = f"https://online.sbis.ru/page/contractor?inn={clean_inn}"
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
    
    revenue = dadata_info.get("revenue")
    emp_cnt = dadata_info.get("employee_count")
    scale = calculate_scale(revenue, emp_cnt)
    rev_fmt = format_revenue(revenue)
    is_holding = dadata_info.get("is_holding", False)
    
    # 1. Проверка на Тендерщика
    if p_cnt > 0 or saby_info.get("is_participant"):
        tags.append("Тендер")
        reasons.append(f"Участий в торгах в качестве поставщика: {p_cnt}")
        
    # 2. Проверка на Производство
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
        
    # 4. Конечный покупатель
    if not is_reseller and not is_production:
        tags.append("Конечный покупатель")
        reasons.append("Компания приобретает оборудование под собственные нужды")
    elif is_production and not is_reseller:
        tags.append("Конечный покупатель")
        
    verdict = "ПЕРЕПРОДАЖНИК" if is_reseller else ("ПРОИЗВОДСТВО" if is_production else "КОНЕЧНЫЙ ПОКУПАТЕЛЬ")
    return {
        "verdict": verdict,
        "recommended_tags": list(set(tags)),
        "reasons": reasons,
        "scale": scale,
        "revenue_formatted": rev_fmt,
        "is_holding": is_holding
    }


def format_sbis_summary(data: dict) -> str:
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    dadata = data.get("dadata", {})
    saby = data.get("saby", {})
    clf = data.get("classification", {})
    
    rev_str = clf.get("revenue_formatted", "Не раскрыта")
    scale = clf.get("scale", "Не определен")
    okved = dadata.get("okved", "")
    okved_name = dadata.get("okved_name", "")
    p_cnt = saby.get("participant_count", 0)
    c_cnt = saby.get("customer_count", 0)
    holding_str = "Входит в холдинг / филиальная сеть" if clf.get("is_holding") else "Независимая организация"
    verdict = clf.get("verdict", "НЕ ОПРЕДЕЛЕН")
    
    lines = [
        f"[СБИС / Скоринг надежности {today}]",
        f"• Выручка: {rev_str} ({scale})",
        f"• ОКВЭД: {okved} {okved_name}" if okved else "• ОКВЭД: не указан",
        f"• Торги: Участник (поставщик): {p_cnt} | Заказчик: {c_cnt}",
        f"• Структура: {holding_str}",
        f"• Вердикт: {verdict}"
    ]
    return "\n".join(lines)


def format_onec_comment(data: dict) -> str:
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    clf = data.get("classification", {})
    dadata = data.get("dadata", {})
    saby = data.get("saby", {})
    rev_str = clf.get("revenue_formatted", "Н/Д")
    okved = dadata.get("okved", "Н/Д")
    p_cnt = saby.get("participant_count", 0)
    verdict = clf.get("verdict", "Н/Д")
    return f"[СБИС {today}: Выручка {rev_str}, ОКВЭД {okved}, Тендеров: {p_cnt}, Вердикт: {verdict}]"


def _merge_sbis_block(existing_text: str, new_sbis_block: str) -> str:
    """Заменяет старый блок [СБИС...] на новый или добавляет в начало"""
    if not existing_text:
        return new_sbis_block
    cleaned = re.sub(r'\[СБИС[^\]]*\][\s\S]*?(?=\n\n|$|\[)', '', existing_text).strip()
    return f"{new_sbis_block}\n\n{cleaned}".strip() if cleaned else new_sbis_block


def write_to_bitrix24(b24_company_id: int = None, b24_lead_id: int = None, summary_text: str = "", dry_run: bool = True) -> bool:
    if not B24_WEBHOOK or B24_WEBHOOK == "/":
        return False
    try:
        if b24_company_id:
            if not dry_run:
                r_get = requests.post(f"{B24_WEBHOOK}crm.company.get", json={"id": b24_company_id}, timeout=15)
                cur_comm = r_get.json().get("result", {}).get("COMMENTS", "") or ""
                new_comm = _merge_sbis_block(cur_comm, summary_text)
                requests.post(f"{B24_WEBHOOK}crm.company.update", json={"id": b24_company_id, "fields": {"COMMENTS": new_comm}}, timeout=15)
                r_tl = requests.post(f"{B24_WEBHOOK}crm.timeline.comment.add", json={
                    "fields": {
                        "ENTITY_ID": b24_company_id,
                        "ENTITY_TYPE": "company",
                        "COMMENT": summary_text
                    }
                }, timeout=15)
                if r_tl.status_code == 200 and r_tl.json().get("result"):
                    comment_id = r_tl.json().get("result")
                    requests.post(f"{B24_WEBHOOK}crm.timeline.item.pin", json={"id": comment_id, "pin": "Y"}, timeout=15)
            print(f"  [B24] Скоринг СБИС сохранен в Компанию #{b24_company_id} ({'DRY-RUN' if dry_run else 'OK'})")

        if b24_lead_id:
            if not dry_run:
                r_get = requests.post(f"{B24_WEBHOOK}crm.lead.get", json={"id": b24_lead_id}, timeout=15)
                cur_comm = r_get.json().get("result", {}).get("COMMENTS", "") or ""
                new_comm = _merge_sbis_block(cur_comm, summary_text)
                requests.post(f"{B24_WEBHOOK}crm.lead.update", json={"id": b24_lead_id, "fields": {"COMMENTS": new_comm}}, timeout=15)
                requests.post(f"{B24_WEBHOOK}crm.timeline.comment.add", json={
                    "fields": {
                        "ENTITY_ID": b24_lead_id,
                        "ENTITY_TYPE": "lead",
                        "COMMENT": summary_text
                    }
                }, timeout=15)
            print(f"  [B24] Скоринг СБИС сохранен в Лид #{b24_lead_id} ({'DRY-RUN' if dry_run else 'OK'})")
        return True
    except Exception as e:
        print(f"  [B24-ERROR] Ошибка записи в Битрикс24: {e}")
        return False


def write_to_onec(inn: str = None, one_c_guid: str = None, summary_text: str = "", tags: list = None, dry_run: bool = True) -> bool:
    auth = (ODATA_USER, ODATA_PASS)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    clean_inn = "".join(filter(str.isdigit, str(inn or "")))
    entity_type = "Catalog_Контрагенты"

    if not one_c_guid and clean_inn:
        try:
            r = requests.get(f"{ODATA_BASE}/Catalog_Контрагенты?$format=json&$top=1&$filter=substringof('{clean_inn}',ИНН)", auth=auth, headers=headers, timeout=15)
            if r.status_code == 200 and r.json().get("value"):
                one_c_guid = r.json()["value"][0]["Ref_Key"]
                entity_type = "Catalog_Контрагенты"
            else:
                r_l = requests.get(f"{ODATA_BASE}/Catalog_Лиды?$format=json&$top=1&$filter=substringof('{clean_inn}',Тема)", auth=auth, headers=headers, timeout=15)
                if r_l.status_code == 200 and r_l.json().get("value"):
                    one_c_guid = r_l.json()["value"][0]["Ref_Key"]
                    entity_type = "Catalog_Лиды"
        except Exception:
            return False

    if one_c_guid:
        if not dry_run:
            try:
                r_get = requests.get(f"{ODATA_BASE}/{entity_type}(guid'{one_c_guid}')?$format=json", auth=auth, headers=headers, timeout=15)
                if r_get.status_code == 200:
                    item_data = r_get.json()
                    cur_comment = item_data.get("Комментарий", "") or ""
                    compact_summary = format_onec_comment({"classification": tags or {}, "dadata": {"okved": ""}, "saby": {}})
                    new_comment = _merge_sbis_block(cur_comment, compact_summary)
                    requests.patch(f"{ODATA_BASE}/{entity_type}(guid'{one_c_guid}')?$format=json", json={"Комментарий": new_comment}, auth=auth, headers=headers, timeout=15)
            except Exception as e:
                print(f"  [1C-WARN] Не удалось обновить Комментарий в 1С: {e}")
        print(f"  [1C] Скоринг СБИС сохранен в {entity_type} {one_c_guid} ({'DRY-RUN' if dry_run else 'OK'})")
        return True
    return False


def is_contractor_already_verified(inn: str = None, b24_company_id: int = None, b24_lead_id: int = None, one_c_guid: str = None) -> bool:
    """
    Проверяет, выполнялась ли уже проверка СБИС для данного контрагента.
    Проверяет наличие блока [СБИС...] в Битрикс24 или 1С:УНФ для исключения повторных запросов.
    """
    clean_inn = "".join(filter(str.isdigit, str(inn or "")))
    # 1. Проверка в Битрикс24
    if B24_WEBHOOK and B24_WEBHOOK != "/":
        try:
            if b24_company_id:
                r = requests.post(f"{B24_WEBHOOK}crm.company.get", json={"id": b24_company_id}, timeout=10)
                if r.status_code == 200:
                    comm = r.json().get("result", {}).get("COMMENTS", "") or ""
                    if "[СБИС" in comm:
                        return True
            if b24_lead_id:
                r = requests.post(f"{B24_WEBHOOK}crm.lead.get", json={"id": b24_lead_id}, timeout=10)
                if r.status_code == 200:
                    comm = r.json().get("result", {}).get("COMMENTS", "") or ""
                    if "[СБИС" in comm:
                        return True
        except Exception:
            pass

    # 2. Проверка в 1С:УНФ
    auth = (ODATA_USER, ODATA_PASS)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if one_c_guid:
        try:
            for entity in ("Catalog_Контрагенты", "Catalog_Лиды"):
                r = requests.get(f"{ODATA_BASE}/{entity}(guid'{one_c_guid}')?$format=json", auth=auth, headers=headers, timeout=10)
                if r.status_code == 200:
                    comm = r.json().get("Комментарий", "") or ""
                    if "[СБИС" in comm:
                        return True
        except Exception:
            pass
    elif clean_inn:
        try:
            r = requests.get(f"{ODATA_BASE}/Catalog_Контрагенты?$format=json&$top=1&$filter=substringof('{clean_inn}',ИНН)", auth=auth, headers=headers, timeout=10)
            if r.status_code == 200 and r.json().get("value"):
                comm = r.json()["value"][0].get("Комментарий", "") or ""
                if "[СБИС" in comm:
                    return True
        except Exception:
            pass

    return False


def sync_to_marketing_db(inn: str = None, email: str = None, sbis_result: dict = None, dry_run: bool = True) -> bool:
    """Сохраняет профиль СБИС в таблицу client_intel в marketing_db (DWH)"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        pg_user = os.getenv("POSTGRES_USER")
        pg_pass = os.getenv("POSTGRES_PASSWORD")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5433")
        pg_db = os.getenv("POSTGRES_DB", "marketing_db")
        if pg_user and pg_pass:
            db_url = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    if not db_url:
        return False
    try:
        import psycopg2
        if dry_run:
            print(f"  [DWH] (Dry-run) Запись скоринга СБИС в marketing_db для {email or inn}")
            return True
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'client_intel' AND column_name = 'sbis_checked_at';
        """)
        if not cur.fetchone():
            cur.execute("ALTER TABLE client_intel ADD COLUMN IF NOT EXISTS sbis_checked_at TIMESTAMP;")
            cur.execute("ALTER TABLE client_intel ADD COLUMN IF NOT EXISTS sbis_profile JSONB;")
            conn.commit()

        if email:
            cur.execute("""
                UPDATE client_intel 
                SET sbis_checked_at = NOW(),
                    sbis_profile = %s,
                    updated_at = NOW()
                WHERE email = %s;
            """, (json.dumps(sbis_result, ensure_ascii=False), email.lower()))
            conn.commit()
        cur.close()
        conn.close()
        print(f"  [DWH OK] Скоринг СБИС сохранен в marketing_db для {email or inn}")
        return True
    except Exception as e:
        print(f"  [DWH-WARN] Ошибка сохранения в marketing_db: {e}")
        return False


def verify_and_enrich_contractor(inn: str, b24_company_id: int = None, b24_lead_id: int = None, one_c_guid: str = None, email: str = None, dry_run: bool = True, force: bool = False) -> dict:
    """
    Главная точка входа сквозного скоринга:
    1. Проверяет кэш (если force=False и контрагент уже проверен — возвращает кэш).
    2. Проверяет контрагента через DaData + Saby.
    3. Синхронизирует результаты в Битрикс24 CRM, 1С:УНФ и marketing_db (DWH).
    4. Поддерживает строгий --dry-run.
    """
    clean_inn = "".join(filter(str.isdigit, str(inn or "")))
    if not clean_inn:
        return {"error": "Не задан ИНН"}

    if not force and is_contractor_already_verified(inn=clean_inn, b24_company_id=b24_company_id, b24_lead_id=b24_lead_id, one_c_guid=one_c_guid):
        print(f"[СБИС-КЭШ] Контрагент ИНН {clean_inn} уже верифицирован ранее. Повторный запрос пропущен.")
        return {"inn": clean_inn, "status": "cached", "message": "Контрагент уже верифицирован"}

    print(f"\n[СБИС-СКОРИНГ] Запуск комплексной проверки ИНН: {clean_inn}...")
    dadata = get_dadata_info(clean_inn)
    saby = get_saby_tender_info(clean_inn)
    classification = classify_client(dadata, saby)

    result = {
        "inn": clean_inn,
        "dadata": dadata,
        "saby": saby,
        "classification": classification,
        "checked_at": datetime.datetime.utcnow().isoformat()
    }

    summary_text = format_sbis_summary(result)
    print(f"  Результат: Выручка: {classification['revenue_formatted']} ({classification['scale']}) | Торги: {saby.get('participant_count', 0)} | Вердикт: {classification['verdict']}")

    # 1. Битрикс24
    if b24_company_id or b24_lead_id:
        write_to_bitrix24(b24_company_id=b24_company_id, b24_lead_id=b24_lead_id, summary_text=summary_text, dry_run=dry_run)

    # 2. 1С:УНФ
    if one_c_guid or clean_inn:
        write_to_onec(inn=clean_inn, one_c_guid=one_c_guid, summary_text=summary_text, tags=classification, dry_run=dry_run)

    # 3. marketing_db (DWH)
    sync_to_marketing_db(inn=clean_inn, email=email, sbis_result=result, dry_run=dry_run)

    result["summary_text"] = summary_text
    return result


def main():
    parser = argparse.ArgumentParser(description="Сквозная проверка контрагента по ИНН через DaData и Saby (СБИС)")
    parser.add_argument("inn", help="ИНН организации (10 или 12 цифр)")
    parser.add_argument("--b24-company-id", type=int, help="ID компании в Битрикс24 для синхронизации")
    parser.add_argument("--b24-lead-id", type=int, help="ID лида в Битрикс24 для синхронизации")
    parser.add_argument("--onec-guid", help="GUID контрагента/лида в 1С:УНФ")
    parser.add_argument("--sync-all", action="store_true", help="Синхронизировать скоринг во все связанные системы")
    parser.add_argument("--dry-run", action="store_true", help="Режим предпросмотра без изменения внешних систем")
    parser.add_argument("--json", action="store_true", help="Вывод в формате JSON")
    args = parser.parse_args()

    res = verify_and_enrich_contractor(
        inn=args.inn,
        b24_company_id=args.b24_company_id,
        b24_lead_id=args.b24_lead_id,
        one_c_guid=args.onec_guid,
        dry_run=args.dry_run
    )

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    print("=" * 60)
    print(res.get("summary_text", ""))
    print("=" * 60)


if __name__ == "__main__":
    main()
