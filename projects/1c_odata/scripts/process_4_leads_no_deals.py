#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/process_4_leads_no_deals.py
======================================================
Канонический скрипт обработки 4 входящих лидов CRM Битрикс24 БЕЗ СДЕЛОК И ЗАДАЧ СНАБЖЕНИЮ:
- Лид #18550: pek31-73@yandex.ru, Сергей, ООО "ПРОМКОМПЛЕКТ" (Белгород)
- Лид #18546: s.erofeeva@unikom-service.ru, Светлана Ерофеева, АО НПП "Уником-Сервис" (Первоуральск)
- Лид #18542: stropansnab@mail.ru, Нина Иванова, ИП Погребняк В.В.
- Лид #18548: kae1465@bk.ru, Алексей Кравченко, ООО "ТД "ПРОМАЛЬЯНС" (Калуга)

Режимы:
  py projects/1c_odata/scripts/process_4_leads_no_deals.py --dry-run
  py projects/1c_odata/scripts/process_4_leads_no_deals.py --execute
"""

import os
import sys
import json
import argparse
import requests
from requests.auth import HTTPBasicAuth

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import (
    call_b24, USER_ARTEM, ONEC_BASE, ONEC_AUTH_READ, ONEC_AUTH_WRITE,
    link_1c_events_and_address_book, normalize_phone_number
)
from check_contractor import verify_and_enrich_contractor
from create_1c_lead import (
    ODATA_BASE, ODATA_USER, ODATA_PASS,
    RESPONSIBLE_ARTEM, SOURCE_WEBSITE, STATE_ACCEPTED,
    TAG_END_BUYER, TAG_PRODUCTION, TAG_TENDER, TAG_RESELLER, TAG_LARGE, TAG_INDIVIDUAL,
    build_lead_base_payload, build_lead_patch_payload
)

# Точные предопределенные GUID видов контактной информации 1С:УНФ (Strict CI Invariant Guard)
CI_LEAD_EMAIL = "5c0dc769-23c6-11ed-91a8-a068f8f3337c"          # E-mail (Справочник "Лиды")
CI_LEAD_PHONE = "5c0dc76d-23c6-11ed-91a8-a068f8f3337c"          # Телефон (Справочник "Лиды")
CI_LEAD_LEGAL_ADDRESS = "5c0dc76f-23c6-11ed-91a8-a068f8f3337c"  # Юр. адрес (Справочник "Лиды")
CI_LEAD_ACTUAL_ADDRESS = "5c0dc76e-23c6-11ed-91a8-a068f8f3337c" # Факт. адрес (Справочник "Лиды")
CI_LEAD_WEB = "5c0dc76c-23c6-11ed-91a8-a068f8f3337c"             # Сайт (Справочник "Лиды")

CI_LEAD_CONTACT_EMAIL = "5c0dc752-23c6-11ed-91a8-a068f8f3337c"  # E-mail (Справочник "Контакты лидов")
CI_LEAD_CONTACT_PHONE = "5c0dc756-23c6-11ed-91a8-a068f8f3337c"  # Телефон (Справочник "Контакты лидов")

LEADS_CONFIG = [
    {
        "lead_id": 18550,
        "title": 'ООО "ПРОМКОМПЛЕКТ"',
        "inn": "3123416580",
        "kpp": "312301001",
        "ogrn": "1173123023864",
        "address_legal": "308023, Белгородская область, г. Белгород, ул. Студенческая, д. 24",
        "address_actual": "308023, Белгородская область, г. Белгород, ул. Студенческая, д. 24",
        "web": "",
        "director": "Чередов Александр Валентинович",
        "emails_company": ["pekomp@yandex.ru", "pek31-73@yandex.ru"],
        "phones_company": ["+7 (4722) 41-09-95", "+7 (951) 133-74-46"],
        "contact_name": "Сергей",
        "contact_last_name": "",
        "contact_second_name": "",
        "contact_post": "Менеджер по закупкам / сбыту",
        "contact_email": "pek31-73@yandex.ru",
        "contact_phone": "+7 (951) 133-74-46",
        "comment": "Запрос на ремкомплекты GEMU (88233453, 88233457). Оптовая торговля промавтоматикой (SIEMENS, DANFOSS, OMRON, ABB, GEMU). Перепродажник.",
        "tags_1c": [TAG_RESELLER],
        "tag_names": ["Перепродажники"],
        "address_book_guid": "0b118bd8-cd32-11f1-974e-02006df8aab5"
    },
    {
        "lead_id": 18546,
        "title": 'АО НПП "УНИКОМ-СЕРВИС"',
        "inn": "6684040828",
        "kpp": "668401001",
        "ogrn": "1216600073282",
        "address_legal": "623104, Свердловская область, г. Первоуральск, ш. Московское, зд. 3",
        "address_actual": "623104, Свердловская область, г. Первоуральск, ш. Московское, зд. 3",
        "web": "unikom-service.ru",
        "director": "Щапов Константин Федорович",
        "emails_company": ["info@unikom-service.ru", "s.erofeeva@unikom-service.ru"],
        "phones_company": ["+7 (3439) 66-87-10", "+7 (3439) 66-88-40"],
        "contact_name": "Светлана",
        "contact_last_name": "Ерофеева",
        "contact_second_name": "Юрьевна",
        "contact_post": "Экономист по снабжению",
        "contact_email": "s.erofeeva@unikom-service.ru",
        "contact_phone": "+7 (3439) 66-87-10",
        "comment": "Запрос на подовую керамическую плиту 230х170х15 мм (1300°C). Крупный производитель изделий из полиуретана (НПП). Выслан референс-лист.",
        "tags_1c": [TAG_PRODUCTION, TAG_LARGE],
        "tag_names": ["Производство", "Крупный"],
        "address_book_guid": "45f4142a-cd21-11f1-974e-02006df8aab5"
    },
    {
        "lead_id": 18542,
        "title": 'ИП Погребняк В.В.',
        "inn": "550613869941",
        "kpp": "",
        "ogrn": "324508100542763", # ОГРНИП
        "address_legal": "143025, Московская область, г. Одинцово, с. Ромашково, ул. Никольская, д. 8к2, кв. 32",
        "address_actual": "644516, Омская область, Омский район, п. Ключи, ул. Заводская, д. 1",
        "web": "stropan.ru",
        "director": "Погребняк Валерий Викторович",
        "emails_company": ["stropan@mail.ru", "stropansnab@mail.ru"],
        "phones_company": ["+7 (908) 798-79-89"],
        "contact_name": "Нина",
        "contact_last_name": "Иванова",
        "contact_second_name": "",
        "contact_post": "Снабжение",
        "contact_email": "stropansnab@mail.ru",
        "contact_phone": "+7 (908) 798-79-89",
        "comment": "Запрос на мембраны EPDM (DN 15-25, DN 32-40, DN 50) для клапанов GEMU R690 (всего 30 шт.). Бренд STROPAN (производство строп и грузоподъемных систем).",
        "tags_1c": [TAG_PRODUCTION, TAG_END_BUYER],
        "tag_names": ["Производство", "Конечный покупатель"],
        "address_book_guid": "60405242-cd23-11f1-974e-02006df8aab5"
    },
    {
        "lead_id": 18548,
        "title": 'ООО "ТД "ПРОМАЛЬЯНС"',
        "inn": "4028062822",
        "kpp": "402901001",
        "ogrn": "1164027060405",
        "address_legal": "248025, Калужская область, г. Калуга, ул. Зерновая, д. 22, оф. 31",
        "address_actual": "248025, Калужская область, г. Калуга, ул. Зерновая, д. 22, оф. 31",
        "web": "oootdpa.ru",
        "director": "Авдеев Алексей Александрович",
        "emails_company": ["zakaz@oootdpa.ru", "kae1465@bk.ru", "kpk140@ya.ru", "td140@ya.ru"],
        "phones_company": ["+7 (920) 898-06-00", "+7 (929) 033-30-33"],
        "contact_name": "Алексей",
        "contact_last_name": "Кравченко",
        "contact_second_name": "",
        "contact_post": "Менеджер по закупкам",
        "contact_email": "kae1465@bk.ru",
        "contact_phone": "+7 (920) 898-06-00",
        "comment": "Запрос на электромагнитные клапаны SMC V114-6MOU (60 шт.) и V114A-6MOU 12VDC (60 шт.) - всего 120 шт. Торговый дом (комплектация / тендеры). Перепродажник.",
        "tags_1c": [TAG_RESELLER, TAG_TENDER],
        "tag_names": ["Перепродажники", "Тендер"],
        "address_book_guid": "46d51e02-cd21-11f1-974e-02006df8aab5"
    }
]

def run_dry_run():
    print("=" * 80)
    print(">>> DRY-RUN: ОБРАБОТКА 4 ЛИДОВ (БЕЗ СОЗДАНИЯ СДЕЛОК И ЗАДАЧ СНАБЖЕНИЮ)")
    print("=" * 80)
    
    for cfg in LEADS_CONFIG:
        lid = cfg["lead_id"]
        print(f"\n[{lid}] {cfg['title']} (ИНН {cfg['inn']}):")
        print(f"  1. Битрикс24 Компания:")
        print(f"     - Название: {cfg['title']}")
        print(f"     - ИНН: {cfg['inn']}, КПП: {cfg['kpp']}, ОГРН: {cfg['ogrn']}")
        print(f"     - Юр. адрес: {cfg['address_legal']}")
        print(f"     - Факт. адрес: {cfg['address_actual']}")
        print(f"     - Emails: {', '.join(cfg['emails_company'])}")
        print(f"     - Телефоны: {', '.join(cfg['phones_company'])}")
        print(f"     - Web: {cfg['web'] or 'нет'}")
        print(f"     - Ответственный: Артем Петров (ID 1)")
        
        print(f"  2. Битрикс24 Контакт:")
        full_name = f"{cfg['contact_last_name']} {cfg['contact_name']} {cfg['contact_second_name']}".strip()
        print(f"     - ФИО: {full_name}")
        print(f"     - Должность: {cfg['contact_post']}")
        print(f"     - Email: {cfg['contact_email']}")
        print(f"     - Телефон: {cfg['contact_phone']}")
        print(f"     - Привязка: к созданной Компании")
        
        print(f"  3. Битрикс24 Лид #{lid}:")
        print(f"     - Привязка: COMPANY_ID=<Новая компания>, CONTACT_ID=<Новый контакт>")
        print(f"     - Статус: CONVERTED (Сконвертирован без создания сделки)")
        print(f"     - Привязка всех почтовых активностей лида к созданной Компании и Контакту")
        print(f"     - Завершение входящих активностей лида (COMPLETED: Y)")
        print(f"     - СБИС-скоринг карточки компании")
        
        print(f"  4. 1С:УНФ Лид (Zero-Blank Lead Guard):")
        print(f"     - Phase 1 POST Catalog_Лиды: Description='{cfg['title']}', НаименованиеКомпании='{cfg['title']}', Тема='ИНН: {cfg['inn']}'")
        print(f"     - Phase 2 PATCH: ТЧ КонтактнаяИнформация (Emails, Телефоны, Адреса, Web), ТЧ Теги ({', '.join(cfg['tag_names'])})")
        print(f"     - Phase 3 POST Catalog_КонтактыЛидов: ФИО='{full_name}', Должность='{cfg['contact_post']}', Email='{cfg['contact_email']}', Телефон='{cfg['contact_phone']}'")
        print(f"     - Phase 4 Event Linking: Привязка Document_Событие и Catalog_АдресатыПисем (GUID {cfg['address_book_guid']})")
        
        print(f"  5. Сделки и задачи:")
        print(f"     - СТРОГО НЕ СОЗДАЮТСЯ (Запрет пользователя соблюден).")


def execute_processing():
    print("=" * 80)
    print(">>> БОЕВОЕ ИСПОЛНЕНИЕ: ОБРАБОТКА 4 ЛИДОВ")
    print("=" * 80)
    
    results = []
    
    for cfg in LEADS_CONFIG:
        lid = cfg["lead_id"]
        inn = cfg["inn"]
        title = cfg["title"]
        print(f"\n{'='*60}\n>>> Исполнение для Лида #{lid}: {title} (ИНН {inn})\n{'='*60}")
        
        # -------------------------------------------------------------
        # ШАГ 1: Создание / обогащение Компании в Битрикс24
        # -------------------------------------------------------------
        print("1. Создание / обогащение Компании в Битрикс24...")
        company_fields = {
            "TITLE": title,
            "ASSIGNED_BY_ID": USER_ARTEM,
            "OPENED": "Y",
            "COMPANY_TYPE": "CUSTOMER",
            "UF_CRM_699421CD2A684": inn,
            "ADDRESS": cfg["address_actual"],
            "ADDRESS_LEGAL": cfg["address_legal"],
            "EMAIL": [{"VALUE_TYPE": "WORK", "VALUE": em} for em in cfg["emails_company"] if em],
            "PHONE": [{"VALUE_TYPE": "WORK", "VALUE": normalize_phone_number(ph)[0]} for ph in cfg["phones_company"] if ph]
        }
        if cfg["web"]:
            company_fields["WEB"] = [{"VALUE_TYPE": "WORK", "VALUE": cfg["web"]}]
            
        cid = call_b24("crm.company.add", {"fields": company_fields})
        if not cid:
            raise RuntimeError(f"Не удалось создать компанию в Б24 для Лида #{lid}")
        print(f"   -> Создана Компания #{cid} ({title})")
        
        # Добавляем реквизиты компании
        preset_id = 2 if "ИП" in title else 1 # 1 - Организация, 2 - ИП
        req_fields = {
            "ENTITY_TYPE_ID": 4, # Company
            "ENTITY_ID": cid,
            "PRESET_ID": preset_id,
            "NAME": f"Реквизиты {title}",
            "RQ_COMPANY_NAME": title,
            "RQ_INN": inn,
            "RQ_OGRN" if preset_id == 1 else "RQ_OGRNIP": cfg["ogrn"]
        }
        if cfg["kpp"]:
            req_fields["RQ_KPP"] = cfg["kpp"]
        if cfg["director"]:
            req_fields["RQ_DIRECTOR"] = cfg["director"]
        call_b24("crm.requisite.add", {"fields": req_fields})
        print(f"   -> Добавлены реквизиты (ИНН {inn})")
        
        # -------------------------------------------------------------
        # ШАГ 2: Создание Контакта в Битрикс24
        # -------------------------------------------------------------
        print("2. Создание Контакта в Битрикс24...")
        full_contact_name = f"{cfg['contact_last_name']} {cfg['contact_name']} {cfg['contact_second_name']}".strip()
        contact_fields = {
            "NAME": cfg["contact_name"],
            "LAST_NAME": cfg["contact_last_name"],
            "SECOND_NAME": cfg["contact_second_name"],
            "POST": cfg["contact_post"],
            "COMPANY_ID": cid,
            "ASSIGNED_BY_ID": USER_ARTEM,
            "OPENED": "Y",
            "EMAIL": [{"VALUE_TYPE": "WORK", "VALUE": cfg["contact_email"]}],
            "PHONE": [{"VALUE_TYPE": "WORK", "VALUE": normalize_phone_number(cfg["contact_phone"])[0]}] if cfg["contact_phone"] else []
        }
        cnt_id = call_b24("crm.contact.add", {"fields": contact_fields})
        if not cnt_id:
            raise RuntimeError(f"Не удалось создать контакт в Б24 для Лида #{lid}")
        print(f"   -> Создан Контакт #{cnt_id} ({full_contact_name}) с привязкой к Компании #{cid}")
        
        # -------------------------------------------------------------
        # ШАГ 3: Обновление и конвертация Лида в Битрикс24
        # -------------------------------------------------------------
        print("3. Обновление Лида в Битрикс24...")
        call_b24("crm.lead.update", {
            "id": lid,
            "fields": {
                "COMPANY_ID": cid,
                "CONTACT_ID": cnt_id,
                "STATUS_ID": "CONVERTED"
            }
        })
        print(f"   -> Лид #{lid} привязан к Компании #{cid}, Контакту #{cnt_id} и переведен в CONVERTED")
        
        # Привязка всех активностей лида к созданной компании и контакту
        acts = call_b24("crm.activity.list", {"filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lid}}) or []
        for a in acts:
            aid = a.get("ID")
            call_b24("crm.activity.binding.add", {"activityId": aid, "entityTypeId": 4, "entityId": cid})
            call_b24("crm.activity.binding.add", {"activityId": aid, "entityTypeId": 3, "entityId": cnt_id})
            call_b24("crm.activity.update", {"id": aid, "fields": {"COMPLETED": "Y", "STATUS": 2}})
        print(f"   -> Привязано {len(acts)} активностей лида к Компании #{cid} и Контакту #{cnt_id}, статус закрыт")
        
        # СБИС-скоринг
        print("   -> Запуск СБИС-скоринга...")
        try:
            verify_and_enrich_contractor(
                inn=inn,
                b24_company_id=cid,
                b24_lead_id=lid,
                email=cfg["contact_email"],
                dry_run=False
            )
            print("   -> СБИС-скоринг успешно применен")
        except Exception as e_sbis:
            print(f"   [WARN] СБИС-скоринг: {e_sbis}")
            
        # -------------------------------------------------------------
        # ШАГ 4: Создание Лида в 1С:УНФ (Zero-Blank Lead Guard)
        # -------------------------------------------------------------
        print("4. Создание Лида в 1С:УНФ (Zero-Blank Lead Protocol)...")
        # Фаза 1: POST
        base_payload = build_lead_base_payload(
            title=title,
            company_name=title,
            inn=inn,
            comment=f"{cfg['comment']}\nКонтактное лицо: {full_contact_name} ({cfg['contact_email']}, {cfg['contact_phone']})"
        )
        r_post = requests.post(
            f"{ODATA_BASE}/Catalog_Лиды?$format=json",
            auth=(ODATA_USER, ODATA_PASS),
            headers={"Content-Type": "application/json;charset=utf-8"},
            json=base_payload,
            timeout=20
        )
        if r_post.status_code not in (200, 201):
            raise RuntimeError(f"1C POST Lead failed: {r_post.status_code} - {r_post.text}")
        lead_1c_data = r_post.json()
        lead_1c_guid = lead_1c_data.get("Ref_Key")
        print(f"   -> Phase 1 OK: Создан Лид 1С:УНФ GUID: {lead_1c_guid}")
        
        # Фаза 2: PATCH КонтактнаяИнформация и Теги
        patch_payload = build_lead_patch_payload(
            emails=cfg["emails_company"],
            phone=cfg["contact_phone"] or cfg["phones_company"][0],
            legal_address=cfg["address_legal"],
            actual_address=cfg["address_actual"],
            web=cfg["web"],
            tag_keys=cfg["tags_1c"]
        )
        r_patch = requests.patch(
            f"{ODATA_BASE}/Catalog_Лиды(guid'{lead_1c_guid}')?$format=json",
            auth=(ODATA_USER, ODATA_PASS),
            headers={"Content-Type": "application/json;charset=utf-8"},
            json=patch_payload,
            timeout=20
        )
        if r_patch.status_code not in (200, 204):
            raise RuntimeError(f"1C PATCH Lead failed: {r_patch.status_code} - {r_patch.text}")
        print(f"   -> Phase 2 OK: ТЧ КонтактнаяИнформация и Теги ({', '.join(cfg['tag_names'])}) успешно записаны")
        
        # Фаза 3: POST КонтактЛида
        contact_payload = {
            "Description": full_contact_name,
            "Владелец_Key": lead_1c_guid,
            "Должность": cfg["contact_post"],
            "КонтактнаяИнформация": [
                {
                    "LineNumber": "1",
                    "Тип": "АдресЭлектроннойПочты",
                    "Вид_Key": CI_LEAD_CONTACT_EMAIL,
                    "Представление": cfg["contact_email"],
                    "Значение": cfg["contact_email"],
                    "АдресЭП": cfg["contact_email"]
                }
            ]
        }
        if cfg["contact_phone"]:
            contact_payload["КонтактнаяИнформация"].append({
                "LineNumber": "2",
                "Тип": "Телефон",
                "Вид_Key": CI_LEAD_CONTACT_PHONE,
                "Представление": cfg["contact_phone"],
                "Значение": cfg["contact_phone"],
                "НомерТелефона": cfg["contact_phone"]
            })
        r_cnt = requests.post(
            f"{ODATA_BASE}/Catalog_КонтактыЛидов?$format=json",
            auth=(ODATA_USER, ODATA_PASS),
            headers={"Content-Type": "application/json;charset=utf-8"},
            json=contact_payload,
            timeout=20
        )
        if r_cnt.status_code in (200, 201):
            cnt_1c_guid = r_cnt.json().get("Ref_Key")
            print(f"   -> Phase 3 OK: Создан Контакт Лида 1С:УНФ GUID: {cnt_1c_guid}")
        else:
            print(f"   [WARN] 1C Contact Lead: {r_cnt.status_code} - {r_cnt.text}")
            
        # Фаза 4: Event Linking (Привязка Document_Событие и Catalog_АдресатыПисем)
        linked_ev = link_1c_events_and_address_book(
            sender_email=cfg["contact_email"],
            lead_guid=lead_1c_guid,
            company_title=title,
            is_counterparty=False
        )
        print(f"   -> Phase 4 OK: Привязано событий в 1С: {linked_ev}, актуализирован справочник АдресатыПисем")
        
        results.append({
            "lead_id": lid,
            "title": title,
            "inn": inn,
            "b24_company_id": cid,
            "b24_contact_id": cnt_id,
            "onec_lead_guid": lead_1c_guid
        })
        
    print("\n" + "=" * 80)
    print(">>> ИТОГИ ОБРАБОТКИ 4 ЛИДОВ:")
    for res in results:
        print(f"Лид #{res['lead_id']} ({res['title']}): Компания Б24 #{res['b24_company_id']}, Контакт Б24 #{res['b24_contact_id']}, Лид 1С: {res['onec_lead_guid']}")
    print("=" * 80)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обработка 4 лидов БЕЗ сделок и задач снабжению")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Режим симуляции (Dry-Run)")
    parser.add_argument("--execute", action="store_true", default=False, help="Боевое исполнение")
    args = parser.parse_args()
    
    if args.execute:
        execute_processing()
    else:
        run_dry_run()
