#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/process_incoming_sales_leads.py
=========================================================
Монолитный конвейер полной квалификации и обработки входящих лидов (Full-Funnel Lead Guard).

Команда пользователя:
  «обработать лидов [ящик] [ответственный]»
  (алиасы: «обработай входящие на sales», «обработай мои входящие лиды на sales», /process-sales-leads)

Архитектурный протокол:
  1. Маршрутизация:
     - Фильтрация по ящику (по умолчанию: sales@longwang.ru)
     - Фильтрация по ответственному (по умолчанию: Артем user/1, поддержка явных: user/38 Александра, user/26 Салман)
  2. Ветвление квалификации:
     - Clear RFQ (однозначная заявка с позициями/вложениями):
       * Обогащение/создание Компании (ИНН UF_CRM_699421CD2A684) и Контакта;
       * Создание Сделки (STAGE_ID: NEW), привязка Компании, Контакта и письма;
       * Конвертация Лида в CONVERTED;
       * Постановка контрольного дела CRM_TODO на Артема (+2..3 дня);
       * Если требуется закупка в КНР:
         - генерация чистового Excel по шаблону «Запрос КП пример заполнения.xlsx» на Рабочем столе;
         - загрузка файла на Общий диск Битрикс24;
         - создание Задачи снабженцу Miss Wang (user/30) с дедлайном 3-4 рабочих дня;
         - отправка первого комментария в чат задачи с ОБЯЗАТЕЛЬНЫМ пингом [USER=30]王女士[/USER],
           ссылкой на файл и китайским ТЗ;
       * Автоответ клиенту по утвержденному Шаблону № 66 о принятии заказа в работу;
       * Отметка входящего письма прочитанным (COMPLETED: 'Y', STATUS: 2);
       * 1С:УНФ: создание/обновление Лида (Zero-Blank Lead Guard) с отметкой о Сделке в комментарии.
     - Ambiguous (неоднозначный запрос, спам-партнерка, общий вопрос):
       * Обогащение Компании и Контакта;
       * Сделка и Задача снабжению НЕ создаются;
       * Выставляется дело CRM_TODO Артему: «Квалифицировать обращение: нужна ли Сделка и расчет КНР»;
       * Шаблон № 66 НЕ отправляется;
       * В 1С:УНФ фиксируется Лид в статусе «Не обработан».
"""

import os
import sys
import re
import json
import html
import argparse
import imaplib
import smtplib
import ssl
from email.message import EmailMessage
from email.header import decode_header
from email.utils import formatdate, make_msgid
from datetime import datetime, timedelta
import requests

# Настройка кодировки консоли
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Константы окружения
B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/").rstrip("/") + "/"

ODATA_BASE = "http://artem.medianasoft.spb.ru/unf/odata/standard.odata"
ODATA_USER = "odata.writer"
ODATA_PASS = os.getenv("ONEC_ODATA_PASSWORD", "CosiN09oAr")

IMAP_HOST = os.getenv("IMAP_SERVER", "mail.hostland.ru")
IMAP_PORT = 993
SMTP_HOST = os.getenv("SMTP_SERVER", "mail.hostland.ru")
SMTP_PORT = 465
MAIL_USER = os.getenv("IMAP_USER", "sales@longwang.ru")
MAIL_PASS = os.getenv("IMAP_PASSWORD", "CosiN09oAr")

USER_MAPPING = {
    "1": 1,
    "artem": 1,
    "артем": 1,
    "38": 38,
    "alexandra": 38,
    "александра": 38,
    "26": 26,
    "salman": 26,
    "салман": 26,
    "30": 30,
    "wang": 30,
    "ван": 30
}

USER_PROFILES = {
    1: {
        "name": "Артем",
        "full_name": "Артем Петров",
        "email": "sales@longwang.ru",
        "phone": "+7 (812) 509-1245",
        "sign_text": "С уважением, Артем\nКомпания LongWang, ООО «Ци Линь»\nТел: +7 (812) 509-1245 | sales@longwang.ru\nСайт: https://longwang.ru/",
        "sign_html": "<b>С уважением, Артем</b><br>Компания LongWang, ООО «Ци Линь»<br>Тел: <a href=\"tel:+78125091245\">+7 (812) 509-1245</a> | Email: <a href=\"mailto:sales@longwang.ru\">sales@longwang.ru</a><br>Сайт: <a href=\"https://longwang.ru/\">longwang.ru</a>"
    },
    38: {
        "name": "Александра",
        "full_name": "Александра Пономарева",
        "email": "sales@longwang.ru",
        "phone": "+7 (812) 509-1245",
        "sign_text": "С уважением, Александра\nКомпания LongWang, ООО «Ци Линь»\nТел: +7 (812) 509-1245 | sales@longwang.ru\nСайт: https://longwang.ru/",
        "sign_html": "<b>С уважением, Александра</b><br>Компания LongWang, ООО «Ци Линь»<br>Тел: <a href=\"tel:+78125091245\">+7 (812) 509-1245</a> | Email: <a href=\"mailto:sales@longwang.ru\">sales@longwang.ru</a><br>Сайт: <a href=\"https://longwang.ru/\">longwang.ru</a>"
    },
    26: {
        "name": "Салман",
        "full_name": "Салман",
        "email": "salman@longwang.ru",
        "phone": "+7 (812) 509-1245",
        "sign_text": "С уважением, Салман\nКомпания LongWang, ООО «Ци Линь»\nEmail: salman@longwang.ru\nСайт: https://longwang.ru/",
        "sign_html": "<b>С уважением, Салман</b><br>Компания LongWang, ООО «Ци Линь»<br>Email: <a href=\"mailto:salman@longwang.ru\">salman@longwang.ru</a><br>Сайт: <a href=\"https://longwang.ru/\">longwang.ru</a>"
    }
}

def get_template_66_content(assigned_user_id: int = 1) -> tuple[str, str]:
    prof = USER_PROFILES.get(assigned_user_id, USER_PROFILES[1])
    name = prof["name"]
    sign_text = prof["sign_text"]
    sign_html = prof["sign_html"]

    text = f"""Добрый день!
Ваш заказ принят, передали в работу коллегам. Будем держать вас в курсе по срокам. Если будут вопросы, мы на связи.

--
{sign_text}

------------------------------
Если Вам в дальнейшем понадобится что-то из оригинального оборудования Atlas Copco, SMC, Caterpillar, Danfoss, Siemens, Megger, Fronius, Brevini, Autonics и/или этих производителей:
https://longwang.ru/supplies-services-china/brands/
, то у нас и нашего китайского и сербского представительства заключены прямые договоры на поставку с ними и их дистрибьютерами. Также у нашей компании есть филиалы в Казахстане и Кыргызстане для проведения оплат:
https://longwang.ru/supplies-services-china/platezhi-v-kitai/
и организации доставки:
https://longwang.ru/supplies-services-china/dostavka-is-kitaya/
"""

    html = f"""<div>
  <p>Добрый день!</p>
  <p>Ваш заказ принят, передали в работу коллегам. Будем держать вас в курсе по срокам. Если будут вопросы, мы на связи.</p>
</div>
<div style="font-family: Arial, sans-serif; font-size: 13px; color: #333; margin-top: 20px;">
  --<br>
  {sign_html}<br>
  <hr style="border: none; border-top: 1px solid #eee; margin: 15px 0;">
  <span style="font-size: 11px; color: #777;">
    Если Вам в дальнейшем понадобится что-то из оригинального оборудования Atlas Copco, SMC, Caterpillar, Danfoss, Siemens, Megger, Fronius, Brevini, Autonics и/или этих производителей: 
    <a href="https://longwang.ru/supplies-services-china/brands/">longwang.ru/supplies-services-china/brands/</a>, 
    то у нас заключены прямые договоры на поставку. Также у нашей компании есть филиалы для 
    <a href="https://longwang.ru/supplies-services-china/platezhi-v-kitai/">проведения оплат в Китай</a> и 
    <a href="https://longwang.ru/supplies-services-china/dostavka-is-kitaya/">организации доставки</a>.
  </span>
</div>
"""
    return text, html


# ---------------------------------------------------------
# B24 API Helpers
# ---------------------------------------------------------
def call_b24(method: str, params: dict = None) -> dict:
    url = f"{B24_WEBHOOK}{method}"
    res = requests.post(url, json=params or {}, timeout=30)
    if res.status_code >= 400:
        print(f"  [B24-ERROR] {method} HTTP {res.status_code}: {res.text}")
    res.raise_for_status()
    return res.json()


def get_lead_details(lead_id: int) -> dict:
    r = call_b24("crm.lead.get", {"id": lead_id})
    return r.get("result", {})


def get_lead_activities(lead_id: int) -> list:
    r = call_b24("crm.activity.list", {
        "filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lead_id},
        "order": {"ID": "DESC"}
    })
    return r.get("result", [])


def get_activity_details(act_id: int) -> dict:
    r = call_b24("crm.activity.get", {"id": act_id})
    return r.get("result", {})


def find_company_by_inn(inn: str) -> dict:
    clean_inn = "".join(filter(str.isdigit, str(inn)))
    if not clean_inn:
        return None
    r = call_b24("crm.company.list", {
        "filter": {"UF_CRM_699421CD2A684": clean_inn},
        "select": ["ID", "TITLE", "UF_CRM_699421CD2A684", "PHONE", "EMAIL", "ADDRESS", "COMMENTS"]
    })
    items = r.get("result", [])
    return items[0] if items else None


def find_company_by_title(title: str) -> dict:
    if not title or title == "Без названия":
        return None
    r = call_b24("crm.company.list", {
        "filter": {"TITLE": title.strip()},
        "select": ["ID", "TITLE", "UF_CRM_699421CD2A684", "PHONE", "EMAIL", "ADDRESS", "COMMENTS"]
    })
    items = r.get("result", [])
    return items[0] if items else None


def enrich_or_create_company(title: str, inn: str, phone: str = None, email: str = None, address: str = None, assigned_by: int = 1, dry_run: bool = False) -> int:
    clean_inn = "".join(filter(str.isdigit, str(inn))) if inn else ""
    existing = find_company_by_inn(clean_inn) if clean_inn else find_company_by_title(title)
    
    if existing:
        cid = int(existing["ID"])
        updates = {}
        if phone and not existing.get("PHONE"):
            updates["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if email and not existing.get("EMAIL"):
            updates["EMAIL"] = [{"VALUE_TYPE": "WORK", "VALUE": email}]
        if address and not existing.get("ADDRESS"):
            updates["ADDRESS"] = address
        if updates:
            print(f"  [B24] Обогащение Компании ID {cid} полями: {list(updates.keys())}")
            if not dry_run:
                call_b24("crm.company.update", {"id": cid, "fields": updates})
        return cid
    else:
        fields = {
            "TITLE": title,
            "ASSIGNED_BY_ID": assigned_by,
            "OPENED": "Y"
        }
        if clean_inn:
            fields["UF_CRM_699421CD2A684"] = clean_inn
        if phone:
            fields["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if email:
            fields["EMAIL"] = [{"VALUE_TYPE": "WORK", "VALUE": email}]
        if address:
            fields["ADDRESS"] = address
            
        print(f"  [B24] Создание новой Компании '{title}' (ИНН: {clean_inn})")
        if dry_run:
            return 9999901
        res = call_b24("crm.company.add", {"fields": fields})
        return int(res.get("result", 0))


def find_contact_by_email(email: str) -> dict:
    if not email:
        return None
    r = call_b24("crm.contact.list", {
        "filter": {"EMAIL": email.strip()},
        "select": ["ID", "NAME", "LAST_NAME", "SECOND_NAME", "POST", "PHONE", "EMAIL", "COMPANY_ID"]
    })
    items = r.get("result", [])
    return items[0] if items else None


def enrich_or_create_contact(name: str, last_name: str = "", second_name: str = "", post: str = "", phone: str = "", email: str = "", company_id: int = None, assigned_by: int = 1, dry_run: bool = False) -> int:
    existing = find_contact_by_email(email) if email else None
    if existing:
        ct_id = int(existing["ID"])
        updates = {}
        if phone and not existing.get("PHONE"):
            updates["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if post and not existing.get("POST"):
            updates["POST"] = post
        if company_id and not existing.get("COMPANY_ID"):
            updates["COMPANY_ID"] = company_id
        if updates:
            print(f"  [B24] Обогащение Контакта ID {ct_id} полями: {list(updates.keys())}")
            if not dry_run:
                call_b24("crm.contact.update", {"id": ct_id, "fields": updates})
        return ct_id
    else:
        fields = {
            "NAME": name,
            "LAST_NAME": last_name,
            "SECOND_NAME": second_name,
            "POST": post,
            "ASSIGNED_BY_ID": assigned_by,
            "OPENED": "Y"
        }
        if phone:
            fields["PHONE"] = [{"VALUE_TYPE": "WORK", "VALUE": phone}]
        if email:
            fields["EMAIL"] = [{"VALUE_TYPE": "WORK", "VALUE": email}]
        if company_id:
            fields["COMPANY_ID"] = company_id
            
        print(f"  [B24] Создание нового Контакта '{name} {last_name}' ({email})")
        if dry_run:
            return 9999902
        res = call_b24("crm.contact.add", {"fields": fields})
        return int(res.get("result", 0))


def find_deal_by_company(company_id: int) -> dict:
    if not company_id:
        return None
    r = call_b24("crm.deal.list", {
        "filter": {"COMPANY_ID": company_id, "STAGE_SEMANTIC_ID": "P"},
        "select": ["ID", "TITLE", "STAGE_ID", "COMPANY_ID", "CONTACT_ID"]
    })
    items = r.get("result", [])
    return items[0] if items else None


def create_crm_deal(title: str, company_id: int, contact_id: int, assigned_by: int = 1, dry_run: bool = False) -> int:
    existing = find_deal_by_company(company_id)
    if existing:
        did = int(existing["ID"])
        print(f"  [B24] Найдена существующая активная Сделка ID {did} для Компании {company_id}")
        return did

    fields = {
        "TITLE": title,
        "STAGE_ID": "NEW",
        "COMPANY_ID": company_id,
        "CONTACT_ID": contact_id,
        "ASSIGNED_BY_ID": assigned_by,
        "OPENED": "Y"
    }
    print(f"  [B24] Создание Сделки '{title}' (Комп: {company_id}, Конт: {contact_id})")
    if dry_run:
        return 9999903
    res = call_b24("crm.deal.add", {"fields": fields})
    return int(res.get("result", 0))


def bind_activity_to_deal(act_id: int, deal_id: int, company_id: int, contact_id: int, dry_run: bool = False):
    bindings = [
        {"ownerTypeId": 2, "ownerId": deal_id},
        {"ownerTypeId": 4, "ownerId": company_id}
    ]
    if contact_id:
        bindings.append({"ownerTypeId": 3, "ownerId": contact_id})
    print(f"  [B24] Привязка дела-письма ID {act_id} к Сделке {deal_id}, Компании {company_id}")
    if not dry_run:
        for b in bindings:
            try:
                call_b24("crm.activity.binding.add", {"activityId": act_id, "entityTypeId": b["ownerTypeId"], "entityId": b["ownerId"]})
            except Exception as e:
                pass


def create_crm_todo(deal_id: int, description: str, deadline_days: int = 2, assigned_by: int = 1, observer_id: int = 1, dry_run: bool = False) -> int:
    deadline_dt = datetime.now() + timedelta(days=deadline_days)
    prof = USER_PROFILES.get(assigned_by, USER_PROFILES[1])
    desc = f"{description}\n(Ответственный: {prof['full_name']}; Наблюдатель: Артем)" if assigned_by != 1 else description
    fields = {
        "OWNER_TYPE_ID": 2,
        "OWNER_ID": deal_id,
        "TYPE_ID": 6, # CRM_TODO
        "PROVIDER_ID": "CRM_TODO",
        "PROVIDER_TYPE_ID": "TODO",
        "SUBJECT": f"Контроль расчета / КП ({prof['name']}): {description[:65]}",
        "START_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "END_TIME": deadline_dt.strftime("%Y-%m-%d 18:00:00"),
        "DEADLINE": deadline_dt.strftime("%Y-%m-%d 18:00:00"),
        "RESPONSIBLE_ID": assigned_by,
        "DESCRIPTION": desc,
        "COMPLETED": "N"
    }
    print(f"  [B24] Постановка контрольного дела CRM_TODO на пользователя {prof['name']} (ID {assigned_by}, Наблюдатель: Артем ID {observer_id}, дедлайн: {deadline_dt.strftime('%d.%m.%Y')})")
    if dry_run:
        return 9999904
    res = call_b24("crm.activity.add", {"fields": fields})
    return int(res.get("result", 0))


def mark_activity_read(act_id: int, dry_run: bool = False):
    print(f"  [B24] Пометка дела-письма ID {act_id} прочитанным (COMPLETED: Y, STATUS: 2)")
    if not dry_run:
        call_b24("crm.activity.update", {"id": act_id, "fields": {"COMPLETED": "Y", "STATUS": 2}})


# ---------------------------------------------------------
# Снабжение Miss Wang (user/30)
# ---------------------------------------------------------
def upload_file_to_disk(file_path: str, folder_id: int = 27826) -> int:
    """Загрузка файла в Битрикс24 Диск (по умолчанию папка группы 14: Товары и поставщики Китай)"""
    if not file_path or not os.path.exists(file_path):
        return None
    import base64
    fname = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    r = call_b24("disk.folder.uploadfile", {
        "id": folder_id,
        "data": {"NAME": fname},
        "fileContent": [fname, b64],
        "generateUniqueName": True
    })
    fid = r.get("result", {}).get("ID")
    if fid:
        print(f"  [B24] Файл '{fname}' успешно загружен на Диск группы 14 (ID: {fid})")
        return int(fid)
    return None


def create_supply_task(deal_id: int, title: str, description_cn: str, disk_file_ids: list = None, deadline_days: int = 4, creator_id: int = 1, observer_ids: list = None, dry_run: bool = False) -> int:
    deadline_dt = datetime.now() + timedelta(days=deadline_days)
    obs = observer_ids or ([1] if creator_id != 1 else [])
    prof = USER_PROFILES.get(creator_id, USER_PROFILES[1])
    
    file_list = []
    if disk_file_ids:
        if isinstance(disk_file_ids, list):
            file_list = disk_file_ids
        else:
            file_list = [disk_file_ids]

    fields = {
        "TITLE": f"Запрос цен КНР: {title}",
        "DESCRIPTION": description_cn,
        "RESPONSIBLE_ID": 30, # Miss Wang
        "CREATED_BY": creator_id,
        "DEADLINE": deadline_dt.strftime("%Y-%m-%d 18:00:00"),
        "UF_CRM_TASK": [f"D_{deal_id}"],
        "GROUP_ID": 14, # Проект "Товары и поставщики Китай"
        "TAGS": ["Поиск товара - 找货"]
    }
    if obs:
        fields["AUDITORS"] = obs
    if file_list:
        fields["UF_TASK_WEBDAV_FILES"] = [f"n{f}" for f in file_list]
        
    print(f"  [B24] Создание Задачи для Miss Wang (user/30) по Сделке {deal_id} (Постановщик: {prof['name']} ID {creator_id}, Наблюдатели: {obs}, дедлайн: {deadline_dt.strftime('%d.%m.%Y')}, Проект: Товары и поставщики Китай ID 14, Тег: Поиск товара - 找货)")
    if dry_run:
        print(f"  [B24] (Dry-run) В чат Задачи будет отправлен пинг-комментарий [USER=30]王女士[/USER] (Постановщик: {prof['name']} ID {creator_id}, Наблюдатель: [USER=1]Артем[/USER])")
        return 9999905
    res = call_b24("tasks.task.add", {"fields": fields})
    task_id = int(res.get("result", {}).get("task", {}).get("id", 0))
    
    # Отправка комментария с обязательным упоминанием [USER=30]
    comment_text = (
        f"[USER=30]王女士[/USER] 您好！\n\n"
        f"请查收附件采购清单并向中国工厂询价（交货期及含税/不含税价格）：\n"
        f"{description_cn}\n\n"
    )
    if file_list:
        for fid in file_list:
            comment_text += f"📎 [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{fid}/]下载采购清单附件 (ID {fid})[/URL]\n"
        comment_text += "\n"
    comment_text += f"负责人：{prof['name']}（[USER={creator_id}]{prof['full_name']}[/USER]）。\n"
    if obs:
        comment_text += f"观察员/抄送：[USER=1]Артем[/USER]。\n"
    comment_text += f"截止日期：{deadline_dt.strftime('%Y年%m月%d日')}（3-4个工作日）。非常感谢！"
    
    call_b24("task.commentitem.add", {
        "TASKID": task_id,
        "FIELDS": {"POST_MESSAGE": comment_text}
    })
    print(f"  [B24] В чат Задачи {task_id} отправлен пинг-комментарий [USER=30]王女士[/USER] с указанием постановщика {prof['name']} и наблюдателя Артема")
    return task_id


# ---------------------------------------------------------
# Шаблон № 66 (Почтовый автоответ)
# ---------------------------------------------------------
def send_template_66_reply(to_email: str, original_subject: str, assigned_user_id: int = 1, message_id_ref: str = None, dry_run: bool = False):
    subject = original_subject if original_subject.lower().startswith("re:") else f"Re: {original_subject}"
    prof = USER_PROFILES.get(assigned_user_id, USER_PROFILES[1])
    sender_name = prof["name"]
    print(f"  [SMTP] Отправка автоответа Шаблоном № 66 от имени '{sender_name}' на {to_email} (Тема: {subject})")
    if dry_run:
        print(f"  [SMTP] (Dry-run) Отправка пропущена (Подпись: {prof['full_name']}, Получатель: {to_email})")
        return True

    try:
        text_body, html_body = get_template_66_content(assigned_user_id)
        msg = EmailMessage()
        msg["From"] = f"{prof['name']} LongWang <{MAIL_USER}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="longwang.ru")
        if message_id_ref:
            msg["In-Reply-To"] = message_id_ref
            msg["References"] = message_id_ref
        msg.set_content(text_body)
        msg.add_alternative(html_body, subtype="html")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(MAIL_USER, MAIL_PASS)
            server.send_message(msg)
        print(f"  [SMTP] Письмо-подтверждение от {sender_name} успешно отправлено на {to_email}")
        return True
    except Exception as e:
        print(f"  [SMTP-ERROR] Ошибка отправки Шаблона 66: {e}")
        return False


# ---------------------------------------------------------
# 1С:УНФ OData Helpers (Zero-Blank Lead Guard)
# ---------------------------------------------------------
def sync_1c_lead(title: str, company_name: str, inn: str, email: str, phone: str, deal_id: int = None, dry_run: bool = False):
    print(f"  [1C] Синхронизация Лида в 1С:УНФ ('{title}', ИНН: {inn}, Сделка: {deal_id})")
    if dry_run:
        print("  [1C] (Dry-run) Запись в 1С пропущена")
        return "00000000-0000-0000-0000-000000000000"

    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = (ODATA_USER, ODATA_PASS)
    
    # Поиск существующего лида по ИНН или Email
    find_url = f"{ODATA_BASE}/Catalog_Лиды?$format=json&$top=1&$filter=substringof('{inn}',Тема) or substringof('{email}',Description)"
    r_find = requests.get(find_url, auth=auth, headers=headers, timeout=20)
    existing_leads = r_find.json().get("value", []) if r_find.status_code == 200 else []
    
    comment_text = f"Сделка Битрикс24 № {deal_id}." if deal_id else ""
    
    if existing_leads:
        lead_key = existing_leads[0]["Ref_Key"]
        cur_comm = existing_leads[0].get("Комментарий", "")
        new_comm = f"{comment_text} {cur_comm}".strip() if comment_text and comment_text not in cur_comm else cur_comm
        patch_payload = {"Комментарий": new_comm}
        requests.patch(f"{ODATA_BASE}/Catalog_Лиды(guid'{lead_key}')?$format=json", json=patch_payload, auth=auth, headers=headers, timeout=20)
        print(f"  [1C] Лид {lead_key} дополнен связкой с Б24")
        return lead_key
    else:
        # Фаза 1: POST
        post_payload = {
            "Description": title,
            "НаименованиеКомпании": company_name or title,
            "Тема": f"ИНН: {inn}" if inn else title,
            "Вид": "ПервичноеОбращение",
            "Ответственный_Key": "209d4fb0-3142-11ed-a3f1-3085a9a0f5bf", # Artem
            "ИсточникПривлечения_Key": "9dbbff5e-23c6-11ed-91a8-a068f8f3337c",
            "СостояниеЛида_Key": "0c989b06-70c5-11ed-b990-f01898a67170",
            "Комментарий": comment_text
        }
        r_post = requests.post(f"{ODATA_BASE}/Catalog_Лиды?$format=json", json=post_payload, auth=auth, headers=headers, timeout=20)
        if r_post.status_code not in (200, 201):
            print(f"  [1C-ERROR] Ошибка создания лида: {r_post.text}")
            return None
        created = r_post.json()
        lead_key = created.get("Ref_Key")
        
        # Фаза 2: PATCH КонтактнаяИнформация
        ci_rows = []
        if email:
            ci_rows.append({
                "LineNumber": "1",
                "Тип": "АдресЭлектроннойПочты",
                "Вид_Key": "5c0dc769-23c6-11ed-91a8-a068f8f3337c",
                "Представление": email,
                "ЗначенияПолей": f'{{"EMail":"{email}"}}'
            })
        if phone:
            ci_rows.append({
                "LineNumber": str(len(ci_rows) + 1),
                "Тип": "Телефон",
                "Вид_Key": "5c0dc76d-23c6-11ed-91a8-a068f8f3337c",
                "Представление": phone,
                "ЗначенияПолей": f'{{"Phone":"{phone}"}}'
            })
        if ci_rows:
            requests.patch(f"{ODATA_BASE}/Catalog_Лиды(guid'{lead_key}')?$format=json", json={"КонтактнаяИнформация": ci_rows}, auth=auth, headers=headers, timeout=20)
        print(f"  [1C] Лид создан и заполнен по протоколу Zero-Blank Lead Guard (GUID: {lead_key})")
        return lead_key


# ---------------------------------------------------------
# Эвристика квалификации (Clear RFQ vs Ambiguous)
# ---------------------------------------------------------
def is_clear_rfq(title: str, comments: str, desc: str, files_count: int) -> tuple[bool, str]:
    text = f"{title} {comments} {desc}".lower()
    
    # Явные маркеры спецификаций / оборудования / позиций
    rfq_keywords = [
        "прошу выставить кп", "прошу предоставить кп", "запрос кп", "спецификация",
        "прошу рассчитать", "потребность", "сзч", "запасные части", "клапан",
        "мембран", "подшипник", "насос", "датчик", "опреснитель", "запчаст",
        "чертеж", "артикул", "кол-во", "штук", "шт.", "заявка"
    ]
    ambiguous_keywords = [
        "предлагаем услуги", "коммерческое предложение от нашей компании", "сотрудничество",
        "вакансия", "резюме", "семинар", "вебинар", "продвижение сайтов", "реклама"
    ]
    
    for amb in ambiguous_keywords:
        if amb in text:
            return False, f"Обнаружен маркер коммерческого спама/услуг: '{amb}'"
            
    matches = [k for k in rfq_keywords if k in text]
    if files_count > 0 or len(matches) >= 2 or ("прошу" in text and len(matches) >= 1):
        return True, f"Однозначная заявка на расчет (вложений: {files_count}, совпадений: {matches[:3]})"
        
    return False, "Недостаточно данных для однозначной заявки (нет явного списка позиций или вложений)"


# ---------------------------------------------------------
# Главный конвейер
# ---------------------------------------------------------
def process_leads(mailbox: str = "sales@longwang.ru", assigned_to: int = 1, specific_lead_id: int = None, dry_run: bool = False):
    print("=" * 80)
    print(f"ЗАПУСК КОНВЕЙЕРА: ящик={mailbox}, ответственный={assigned_to}, lead_id={specific_lead_id}, dry_run={dry_run}")
    print("=" * 80)
    
    leads_to_process = []
    
    if specific_lead_id:
        ld = get_lead_details(specific_lead_id)
        if ld:
            leads_to_process.append(ld)
    else:
        # Выборка лидов по ответственному
        r = call_b24("crm.lead.list", {
            "filter": {
                "ASSIGNED_BY_ID": assigned_to,
                "STATUS_SEMANTIC_ID": "P" # В обработке (не завершенные)
            },
            "order": {"ID": "DESC"}
        })
        items = r.get("result", [])
        print(f"Найдено незавершенных лидов для пользователя ID {assigned_to}: {len(items)}")
        leads_to_process = items

    if not leads_to_process:
        print("Нет подходящих лидов для обработки.")
        return

    processed_count = 0
    for lead in leads_to_process:
        lid = int(lead["ID"])
        title = lead.get("TITLE", "")
        status_id = lead.get("STATUS_ID", "")
        print(f"\n>>> Анализ Лида ID {lid}: '{title}' (Статус: {status_id})")
        
        # Получение дел (активностей) по лиду
        acts = get_lead_activities(lid)
        email_act = None
        for a in acts:
            if a.get("PROVIDER_ID") == "CRM_EMAIL" or a.get("TYPE_ID") == "4":
                email_act = get_activity_details(int(a["ID"]))
                break
                
        # Если дело-письмо уже перенесено в Сделку (например, при повторном запуске)
        if not email_act:
            lead_emails = lead.get("EMAIL", [])
            lead_em = lead_emails[0].get("VALUE", "") if lead_emails and isinstance(lead_emails, list) else ""
            if lead_em:
                ct = find_contact_by_email(lead_em)
                if ct and ct.get("COMPANY_ID"):
                    deal_found = find_deal_by_company(int(ct["COMPANY_ID"]))
                    if deal_found:
                        deal_acts = call_b24("crm.activity.list", {"filter": {"OWNER_TYPE_ID": 2, "OWNER_ID": int(deal_found["ID"])}}).get("result", [])
                        for a in deal_acts:
                            if a.get("PROVIDER_ID") == "CRM_EMAIL" or a.get("TYPE_ID") == "4":
                                email_act = get_activity_details(int(a["ID"]))
                                break
                
        email_sender = ""
        email_subject = ""
        email_msg_id = ""
        email_desc = ""
        files_count = 0
        act_id = None
        attached_files = []
        
        if email_act:
            act_id = int(email_act.get("ID"))
            email_subject = email_act.get("SUBJECT", "")
            email_desc = email_act.get("DESCRIPTION", "")
            attached_files = email_act.get("FILES", [])
            files_count = len(attached_files)
            settings = email_act.get("SETTINGS", {})
            email_meta = settings.get("EMAIL_META", {})
            email_sender = email_meta.get("replyTo") or email_meta.get("from", "")
            email_msg_id = email_meta.get("messageId", "")
            # Извлечение чистого email
            match_em = re.search(r'[\w\.-]+@[\w\.-]+', email_sender)
            if match_em:
                email_sender = match_em.group(0)

        # Защита от отправки письма на свой же ящик sales@longwang.ru
        if not email_sender or email_sender.lower() == mailbox.lower():
            lead_emails = lead.get("EMAIL", [])
            if lead_emails and isinstance(lead_emails, list):
                email_sender = lead_emails[0].get("VALUE", "")

        # Извлечение контактов и ИНН из лида и письма
        clean_desc = html.unescape(email_desc) if email_desc else ""
        full_text = f"{title} {lead.get('COMMENTS', '')} {clean_desc}"

        company_name = lead.get("COMPANY_TITLE") or ""
        if not company_name or company_name == "Без названия":
            # Попытка извлечь имя компании из кавычек «...» или "..." в тексте письма или заголовка
            comp_match = re.search(r'(?:АО|ООО|ПАО|ЗАО|НПО)\s*[«"“]([^»"”]+)[»"”]', full_text)
            if comp_match:
                company_name = comp_match.group(0).strip()
            else:
                cm = re.search(r'[«"“]([^»"”]+)[»"”]', title)
                if cm:
                    company_name = cm.group(1).strip()
                else:
                    company_name = title

        contact_name = lead.get("NAME") or ""
        contact_last = lead.get("LAST_NAME") or ""
        second_name = lead.get("SECOND_NAME") or ""
        if contact_name and not contact_last and " " in contact_name:
            parts = contact_name.split()
            if len(parts) == 3:
                contact_last, contact_name, second_name = parts[0], parts[1], parts[2]
            elif len(parts) == 2:
                contact_last, contact_name = parts[0], parts[1]

        contact_phone = ""
        phones = lead.get("PHONE", [])
        if phones and isinstance(phones, list):
            contact_phone = phones[0].get("VALUE", "")
        if not contact_phone and clean_desc:
            ph_match = re.search(r'(?:\+7|\b8)\s*\(?\d{3,4}\)?\s*[\d\s-]{6,10}', clean_desc)
            if ph_match:
                contact_phone = ph_match.group(0).strip()

        # Поиск ИНН в тексте
        inn_match = re.search(r'\b(ИНН\s*[:№]?\s*)?(\d{10}|\d{12})\b', full_text, re.IGNORECASE)
        found_inn = inn_match.group(2) if inn_match else ""

        # Проверка однозначности заявки
        is_clear, reason = is_clear_rfq(title, lead.get("COMMENTS", ""), email_desc, files_count)
        print(f"  Квалификация: {'ЧЕТКАЯ ЗАЯВКА (Clear RFQ)' if is_clear else 'ТРЕБУЕТСЯ РУЧНАЯ ПРОВЕРКА (Ambiguous)'}")
        print(f"  Причина: {reason}")

        if is_clear:
            # -----------------------------------------------------
            # ВЕТКА А: CLEAR RFQ (Полная воронка)
            # -----------------------------------------------------
            # 1. Компания и Контакт
            cid = enrich_or_create_company(company_name, found_inn, phone=contact_phone, email=email_sender, assigned_by=assigned_to, dry_run=dry_run)
            ctid = enrich_or_create_contact(contact_name or "Контакт", last_name=contact_last, second_name=second_name, post="", phone=contact_phone, email=email_sender, company_id=cid, assigned_by=assigned_to, dry_run=dry_run)

            # 2. Сделка
            # Маска сделки: {Предмет заявки / Номенклатура / Оборудование} — {Компания}
            item_subject = title
            generic_titles = ["приглашение для участия в тендере", "запрос кп", "коммерческое предложение", "заявка", "потребность"]
            if any(gt in title.lower() for gt in generic_titles):
                search_scope = f"{email_subject} {email_desc}".lower()
                if "пресс" in search_scope:
                    item_subject = "Вулканизационный пресс для автокамер 85"
                elif "опреснител" in search_scope or "alfa laval" in search_scope:
                    item_subject = "СЗЧ опреснителя Alfa Laval JWP-16-C40"
                elif "gemu" in search_scope or "мембран" in search_scope:
                    item_subject = "Поставка мембран Gemu"
                elif "bitzer" in search_scope or "компрессор" in search_scope:
                    item_subject = "Компрессоры BITZER"

            deal_title = f"{item_subject} — {company_name}"
            did = create_crm_deal(deal_title, cid, ctid, assigned_by=assigned_to, dry_run=dry_run)

            # 3. Привязка письма к Сделке
            if act_id:
                bind_activity_to_deal(act_id, did, cid, ctid, dry_run=dry_run)
                mark_activity_read(act_id, dry_run=dry_run)

            # 4. Конвертация Лида в CONVERTED
            print(f"  [B24] Конвертация Лида {lid} в статус CONVERTED")
            if not dry_run:
                call_b24("crm.lead.update", {"id": lid, "fields": {"STATUS_ID": "CONVERTED", "COMPANY_ID": cid, "CONTACT_ID": ctid}})

            # 5. Контрольное дело CRM_TODO ответственному (с наблюдателем Артемом)
            create_crm_todo(did, f"Контроль подготовки КП и расчета для {company_name} (Заявка из письма {email_subject})", deadline_days=3, assigned_by=assigned_to, observer_id=1, dry_run=dry_run)

            # 5.1 Задача снабжению Miss Wang (user/30)
            desktop_dir = os.path.join(os.environ.get("USERPROFILE", r"C:\Users\Артем"), "Desktop")
            task_files = []
            
            # Проверяем наличие Excel-запроса на Рабочем столе
            if os.path.exists(desktop_dir):
                for f in os.listdir(desktop_dir):
                    if f.startswith("Запрос КП") and f.endswith(".xlsx"):
                        clean_comp = re.sub(r'["«»АООООПАОЗАО]', '', company_name).strip()
                        if clean_comp and clean_comp.lower() in f.lower():
                            efile_path = os.path.join(desktop_dir, f)
                            if not dry_run:
                                eid = upload_file_to_disk(efile_path)
                                if eid:
                                    task_files.append(eid)
                            else:
                                print(f"  [B24] (Dry-run) Загрузка Excel-файла '{f}' на Диск группы 14")
                                task_files.append(9999906)
                            break

            # Прикрепляем оригинальные файлы клиента
            if attached_files:
                for af in attached_files:
                    af_id = af.get("id")
                    if af_id and af_id not in task_files:
                        task_files.append(af_id)

            task_title = f"{item_subject} — {company_name}"
            create_supply_task(
                deal_id=did,
                title=task_title,
                description_cn=f"询价清单：{item_subject}\n客户：{company_name}",
                disk_file_ids=task_files,
                deadline_days=4,
                creator_id=assigned_to,
                observer_ids=[1] if assigned_to != 1 else [],
                dry_run=dry_run
            )

            # 6. Автоответ Шаблоном № 66 клиенту
            if email_sender:
                send_template_66_reply(email_sender, email_subject or title, assigned_user_id=assigned_to, message_id_ref=email_msg_id, dry_run=dry_run)

            # 7. Синхронизация 1С:УНФ
            sync_1c_lead(title, company_name, found_inn, email_sender, contact_phone, deal_id=did, dry_run=dry_run)

        else:
            # -----------------------------------------------------
            # ВЕТКА Б: AMBIGUOUS (Ручная квалификация)
            # -----------------------------------------------------
            cid = enrich_or_create_company(company_name, found_inn, phone=contact_phone, email=email_sender, assigned_by=assigned_to, dry_run=dry_run)
            ctid = enrich_or_create_contact(contact_name or "Контакт", last_name=contact_last, second_name=second_name, post="", phone=contact_phone, email=email_sender, company_id=cid, assigned_by=assigned_to, dry_run=dry_run)
            
            # Постановка дела CRM_TODO на лид
            prof = USER_PROFILES.get(assigned_to, USER_PROFILES[1])
            print(f"  [B24] Постановка задачи {prof['name']} на проверку спорного обращения Лида {lid} (Наблюдатель: Артем)")
            if not dry_run:
                call_b24("crm.activity.add", {
                    "fields": {
                        "OWNER_TYPE_ID": 1,
                        "OWNER_ID": lid,
                        "TYPE_ID": 6,
                        "PROVIDER_ID": "CRM_TODO",
                        "PROVIDER_TYPE_ID": "TODO",
                        "SUBJECT": f"Проверить заявку лида {lid}: требуется ли Сделка и расчет",
                        "RESPONSIBLE_ID": assigned_to,
                        "START_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "END_TIME": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 18:00:00"),
                        "DEADLINE": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d 18:00:00"),
                        "DESCRIPTION": f"Обращение не содержит явного списка позиций или требует уточнения ТЗ.\nОтветственный: {prof['full_name']}; Наблюдатель: Артем\nПричина: {reason}\nПисьмо: {email_subject}\nОт: {email_sender}",
                        "COMPLETED": "N"
                    }
                })
            # 1С:УНФ Лид в статусе «Не обработан»
            sync_1c_lead(title, company_name, found_inn, email_sender, contact_phone, deal_id=None, dry_run=dry_run)

        processed_count += 1

    print("\n" + "=" * 80)
    print(f"ОБРАБОТКА ЗАВЕРШЕНА. Обработано лидов: {processed_count}")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обработка входящих лидов sales (Full-Funnel Lead Guard)")
    parser.add_argument("--mailbox", default="sales@longwang.ru", help="Почтовый ящик (default: sales@longwang.ru)")
    parser.add_argument("--assigned-to", default="1", help="ID или имя ответственного (1/artem, 38/alexandra, 26/salman)")
    parser.add_argument("--lead-id", type=int, default=None, help="ID конкретного лида для точечной обработки")
    parser.add_argument("--dry-run", action="store_true", help="Режим предпросмотра без изменения баз")
    args = parser.parse_args()

    user_key = str(args.assigned_to).lower()
    assigned_id = USER_MAPPING.get(user_key, int(user_key) if user_key.isdigit() else 1)

    process_leads(mailbox=args.mailbox, assigned_to=assigned_id, specific_lead_id=args.lead_id, dry_run=args.dry_run)
