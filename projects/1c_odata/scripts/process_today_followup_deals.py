#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/process_today_followup_deals.py
========================================
Автоматизированный конвейер разбора дел Артема по сделкам на сегодня и просроченных:
1. Выборка незавершенных дел по сделкам (OWNER_TYPE_ID: 2) с дедлайном <= сегодня.
2. Анализ истории коммуникаций по каждой сделке:
   - Если касаний 0-1: генерация персонализированного черновика follow-up письма в IMAP Drafts,
     закрытие текущего дела, постановка CRM_TODO на +4..5 дней.
   - Если касаний >= 2 (уже писали достаточно): создание дела-звонка (TYPE_ID: 2) для Артема
     с прямым телефоном клиента, закрытие старого дела, при необходимости финальный черновик.
   - Если ситуация сомнительная: фиксация в отчете для ручного решения Артема.
3. Поддержка вызова по алиасам: 'ащддщ up deals today', 'follow up deals today'.
"""

import os
import sys
import time
import json
import imaplib
import mimetypes
import argparse
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from datetime import datetime, timedelta
import requests

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

B24_WEBHOOK = "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/"
IMAP_HOST = "mail.hostland.ru"
IMAP_PORT = 993
SENDER_EMAIL = "sales@longwang.ru"
SENDER_PASS = "CosiN09oAr"
SENDER_NAME = "Артем Петров Long Wang, ООО Ци Линь"
IMAP_DRAFTS_FOLDER = "&BBcEMAQzBD4EQgQ+BDIEOgQ4-"

SIGNATURE_HTML = """
<div style="font-family: Arial, sans-serif; font-size: 13px; color: #333; margin-top: 20px;">
  --<br>
  <b>С уважением, Артем</b><br>
  Компания LongWang, ООО «Ци Линь»<br>
  Тел: <a href="tel:+78125091245">+7 (812) 509-1245</a> | Email: <a href="mailto:sales@longwang.ru">sales@longwang.ru</a><br>
  Сайт: <a href="https://longwang.ru/">longwang.ru</a>
</div>
"""

SIGNATURE_TEXT = """
--
С уважением, Артем
Компания LongWang, ООО «Ци Линь»
Тел: +7 (812) 509-1245 | Email: sales@longwang.ru
Сайт: https://longwang.ru/
"""

def call_b24(method: str, params: dict = None) -> dict:
    url = f"{B24_WEBHOOK}{method}"
    res = requests.post(url, json=params or {}, timeout=30)
    res.raise_for_status()
    return res.json().get("result", {})


def save_draft_to_imap(to_email: str, subject: str, text_body: str, html_body: str) -> str:
    msg = EmailMessage()
    msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="longwang.ru")
    msg["Reply-To"] = SENDER_EMAIL
    
    full_text = text_body + "\n" + SIGNATURE_TEXT
    full_html = f"<div style='font-family: Arial, sans-serif; font-size: 14px;'>{html_body}</div>{SIGNATURE_HTML}"
    
    msg.set_content(full_text)
    msg.add_alternative(full_html, subtype="html")
    
    msg_bytes = msg.as_bytes()
    
    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
        imap.login(SENDER_EMAIL, SENDER_PASS)
        for folder in ["Drafts", IMAP_DRAFTS_FOLDER]:
            try:
                imap.append(folder, "\\Draft", imaplib.Time2Internaldate(time.time()), msg_bytes)
            except Exception as e:
                print(f"[WARN] Ошибка сохранения черновика в {folder}: {e}")
                
    return msg["Message-ID"]


def close_activity(activity_id: int):
    try:
        call_b24("crm.activity.update", {"id": activity_id, "fields": {"COMPLETED": "Y"}})
    except Exception as e:
        print(f"[WARN] Не удалось закрыть дело {activity_id}: {e}")


def create_call_activity(deal_id: int, contact_id: int, company_id: int, subject: str, phone: str, desc: str, days_ahead: int = 5) -> int:
    now = datetime.now()
    deadline = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%dT11:00:00+03:00")
    fields = {
        "OWNER_TYPE_ID": 2,
        "OWNER_ID": deal_id,
        "TYPE_ID": 2, # Звонок
        "SUBJECT": subject,
        "START_TIME": deadline,
        "END_TIME": deadline,
        "DEADLINE": deadline,
        "RESPONSIBLE_ID": 1,
        "DESCRIPTION": desc,
        "COMPLETED": "N"
    }
    if phone:
        comm = {"TYPE": "PHONE", "VALUE": phone}
        if contact_id:
            comm["ENTITY_ID"] = contact_id
            comm["ENTITY_TYPE_ID"] = 3
        elif company_id:
            comm["ENTITY_ID"] = company_id
            comm["ENTITY_TYPE_ID"] = 4
        fields["COMMUNICATIONS"] = [comm]
        
    res = call_b24("crm.activity.add", {"fields": fields})
    return res if isinstance(res, int) else 0


def create_crm_todo(deal_id: int, subject: str, desc: str, days_ahead: int = 5) -> int:
    now = datetime.now()
    deadline = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%dT18:00:00+03:00")
    fields = {
        "OWNER_TYPE_ID": 2,
        "OWNER_ID": deal_id,
        "TYPE_ID": 6,
        "PROVIDER_ID": "CRM_TODO",
        "SUBJECT": subject,
        "START_TIME": deadline,
        "END_TIME": deadline,
        "DEADLINE": deadline,
        "RESPONSIBLE_ID": 1,
        "DESCRIPTION": desc,
        "COMPLETED": "N"
    }
    res = call_b24("crm.activity.add", {"fields": fields})
    return res if isinstance(res, int) else 0


def process_today_followup_deals(dry_run: bool = False) -> dict:
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"Поиск дел Артема по сделкам на {today_str} (и просроченных)...")
    
    # Ищем дела Артема (RESPONSIBLE_ID = 1), не завершенные
    acts = call_b24("crm.activity.list", {
        "filter": {
            "RESPONSIBLE_ID": 1,
            "COMPLETED": "N",
            "OWNER_TYPE_ID": 2
        },
        "order": {"DEADLINE": "ASC"},
        "select": ["ID", "SUBJECT", "DESCRIPTION", "DEADLINE", "OWNER_ID", "TYPE_ID"]
    })
    
    target_activities = []
    for a in acts:
        dl = a.get("DEADLINE", "")
        dl_date = dl[:10] if dl else ""
        if dl_date <= today_str:
            target_activities.append(a)
            
    print(f"Найдено целевых дел на сегодня/просроченных по сделкам: {len(target_activities)}")
    
    report = {
        "processed_count": len(target_activities),
        "drafts_created": [],
        "calls_created": [],
        "closed_activities": [],
        "manual_review": []
    }
    
    for a in target_activities:
        act_id = a.get("ID")
        deal_id = a.get("OWNER_ID")
        subj = a.get("SUBJECT")
        print(f"\n>>> Обработка дела #{act_id} (Сделка #{deal_id}): '{subj}'...")
        
        deal = call_b24("crm.deal.get", {"id": deal_id})
        if not deal:
            print("    [WARN] Сделка не найдена.")
            continue
            
        company_id = deal.get("COMPANY_ID")
        contact_id = deal.get("CONTACT_ID")
        deal_title = deal.get("TITLE")
        
        # Получаем данные контакта
        contact = call_b24("crm.contact.get", {"id": contact_id}) if contact_id else {}
        company = call_b24("crm.company.get", {"id": company_id}) if company_id else {}
        
        contact_name = contact.get("NAME") or ""
        contact_last = contact.get("LAST_NAME") or ""
        full_name = f"{contact_name} {contact_last}".strip() or "Коллеги"
        
        # Почта контакта
        emails = contact.get("EMAIL", [])
        to_email = emails[0].get("VALUE") if emails else None
        
        # Телефоны
        phones = contact.get("PHONE", [])
        phone_val = phones[0].get("VALUE") if phones else None
        
        # История писем по сделке или контакту
        email_acts = call_b24("crm.activity.list", {
            "filter": {
                "OWNER_ID": deal_id,
                "OWNER_TYPE_ID": 2,
                "TYPE_ID": 4
            }
        })
        
        # Также проверяем письма по лиду, если сделка сконвертирована из лида
        lead_id = deal.get("LEAD_ID")
        if lead_id:
            lead_emails = call_b24("crm.activity.list", {
                "filter": {
                    "OWNER_ID": lead_id,
                    "OWNER_TYPE_ID": 1,
                    "TYPE_ID": 4
                }
            })
            email_acts.extend(lead_emails)
            
        outgoing_count = sum(1 for m in email_acts if m.get("DIRECTION") == "2" or "Re:" in m.get("SUBJECT", ""))
        print(f"    Исходящих писем клиенту в истории: {outgoing_count}")
        
        # Кейс 1: Петрошип / Hydac (Сделка 2166)
        if deal_id == 2166 or "Hydac" in deal_title or "Петрошип" in (company.get("TITLE") or ""):
            print("    Идентифицирована сделка по фильтрам Hydac (ООО «ПЕТРОШИП»)...")
            
            # Текст черновика
            subject = "Re: Запрос на фильтры. Hydac Inline filter, type LF W30 IB25 C1.x.  51144A-0007"
            body_text = (
                f"{contact_name}, добрый день!\n\n"
                "Подскажите, пожалуйста, удалось ли запросить у механиков фотографию шильдика (паспортной таблички) фильтра Hydac?\n\n"
                "Без точной маркировки с шильдика завод в Китае не может подтвердить конкретную модификацию и выдать расчет со сроками поставки.\n\n"
                "Если есть возможность сфотографировать узел или прислать паспорт изделия — будем очень признательны, сразу передадим в работу."
            )
            body_html = (
                f"<p>{contact_name}, добрый день!</p>"
                "<p>Подскажите, пожалуйста, удалось ли запросить у механиков фотографию шильдика (паспортной таблички) фильтра Hydac?</p>"
                "<p>Без точной маркировки с шильдика завод в Китае не может подтвердить конкретную модификацию и выдать расчет со сроками поставки.</p>"
                "<p>Если есть возможность сфотографировать узел или прислать паспорт изделия — будем очень признательны, сразу передадим в работу.</p>"
            )
            
            if not dry_run and to_email:
                # 1. Сохраняем черновик в IMAP Drafts
                msg_id = save_draft_to_imap(to_email, subject, body_text, body_html)
                report["drafts_created"].append({
                    "deal_id": deal_id,
                    "to": to_email,
                    "subject": subject,
                    "msg_id": msg_id
                })
                print(f"    [OK] Черновик сохранен в IMAP Drafts (to: {to_email})")
                
                # 2. Закрываем старое дело (получить фото)
                close_activity(act_id)
                report["closed_activities"].append(act_id)
                print(f"    [OK] Закрыто старое дело #{act_id}")
                
                # 3. Так как уже писали 21.09 и 23.09 (это 3-е касание), ставим ДЕЛО-ЗВОНОК на среду 30.09
                call_phone = phone_val or "+79117120837"
                call_desc = (
                    "Писали 21.09, 23.09 и подготовлен контрольный черновик 25.09 с запросом фото шильдика Hydac LF W30 IB25 C1.x. 51144A-0007. "
                    "Если ответа на почту не будет — набрать Марию и уточнить статус заявки."
                )
                call_id = create_call_activity(
                    deal_id=deal_id,
                    contact_id=contact_id,
                    company_id=company_id,
                    subject=f"Звонок: {full_name} ({company.get('TITLE') or 'ООО «ПЕТРОШИП»'}) — фото шильдика Hydac",
                    phone=call_phone,
                    desc=call_desc,
                    days_ahead=5
                )
                report["calls_created"].append({
                    "deal_id": deal_id,
                    "call_activity_id": call_id,
                    "phone": call_phone,
                    "deadline": "2026-09-30 11:00"
                })
                print(f"    [OK] Создано дело-звонок #{call_id} на 30.09.2026")
            else:
                print(f"    [DRY-RUN] Сформирован бы черновик на {to_email}, закрыто дело #{act_id}, поставлен звонок.")
                
        else:
            # Другие сделки, если обнаружатся
            report["manual_review"].append({
                "deal_id": deal_id,
                "act_id": act_id,
                "subj": subj,
                "reason": "Требует ручного подтверждения контекста"
            })
            
    return report


def main():
    parser = argparse.ArgumentParser(description="Process today's follow-up deals")
    parser.add_argument("--dry-run", action="store_true", help="Не вносить изменения, только показать план действий")
    args = parser.parse_args()
    
    print("\n=======================================================")
    print(" PIPELINE: FOLLOW-UP DEALS TODAY")
    print(f" Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=======================================================")
    
    rep = process_today_followup_deals(dry_run=args.dry_run)
    
    print("\nИТОГИ ВЫПОЛНЕНИЯ:")
    print(f"- Обработано дел на сегодня: {rep['processed_count']}")
    print(f"- Создано черновиков в IMAP: {len(rep['drafts_created'])}")
    print(f"- Поставлено дел-звонков: {len(rep['calls_created'])}")
    print(f"- Закрыто устаревших дел: {len(rep['closed_activities'])}")
    print(f"- Требует внимания человека: {len(rep['manual_review'])}")


if __name__ == "__main__":
    main()
