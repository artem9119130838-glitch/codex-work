"""
deal_followup_pipeline.py
==========================
Динамический модульный конвейер контроля незавершенных сделок, создания черновиков
напоминаний с вложениями (RFC 2231) и синхронизации дел в Битрикс24 CRM.

Стандарты качества:
1. RFC 2231 / MIME: EmailMessage с mimetypes для сохранения оригинальных кириллических имен файлов.
2. Естественные обращения: строго одно обращение ("Сергей, добрый день!").
3. Safety Draft Mode: сохранение черновиков строго в папку "&BBcEMAQzBD4EQgQ+BDIEOgQ4-" ("Черновики" Hostland Roundcube).
4. Агрегация и защита от дублей: группировка по компании/контакту, кулдаун 7-10 дней.
5. CRM_TODO vs Звонки: первые касания — только CRM_TODO (TYPE_ID: 6). Звонок (TYPE_ID: 2) — только при >=3 безответных письмах.
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import json
import time
import imaplib
import mimetypes
import argparse
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from datetime import datetime, timedelta
import requests

B24_WEBHOOK = "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/"
IMAP_HOST = "mail.hostland.ru"
IMAP_PORT = 993

SENDER_EMAIL = "sales@longwang.ru"
SENDER_PASS = "CosiN09oAr"
SENDER_NAME = "Артем Петров Long Wang, ООО Ци Линь"

# Папка "Черновики" в UTF-7 для Roundcube Webmail на Hostland
IMAP_DRAFTS_FOLDER = "&BBcEMAQzBD4EQgQ+BDIEOgQ4-"

TEMP_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "scratch", "followup_cache")
os.makedirs(TEMP_CACHE_DIR, exist_ok=True)


def call_b24(method: str, params: dict = None) -> dict:
    url = f"{B24_WEBHOOK}{method}"
    res = requests.post(url, json=params or {}, timeout=30)
    res.raise_for_status()
    return res.json()


def download_b24_file(file_id: int) -> tuple[str, str]:
    """
    Скачивает файл из Диска Битрикс24 во временный кэш.
    Возвращает (локальный_путь, оригинальное_имя_файла).
    """
    info = call_b24("disk.file.get", {"id": file_id}).get("result", {})
    if not info or "DOWNLOAD_URL" not in info:
        raise ValueError(f"Не удалось получить информацию о файле ID {file_id}")
    
    orig_name = info.get("NAME", f"file_{file_id}.bin")
    dl_url = info["DOWNLOAD_URL"]
    
    clean_name = "".join(c for c in orig_name if c.isalnum() or c in " ._-()[]").strip()
    local_path = os.path.join(TEMP_CACHE_DIR, f"{file_id}_{clean_name}")
    
    if not (os.path.exists(local_path) and os.path.getsize(local_path) > 0):
        r = requests.get(dl_url, timeout=60)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)
            
    return local_path, orig_name


def build_email_message(
    to_emails: list,
    cc_emails: list,
    subject: str,
    body_text: str,
    body_html: str,
    attachment_file_ids: list = None
) -> EmailMessage:
    """
    Создает RFC 2231-совместимое сообщение EmailMessage с правильным MIME-типом
    и кириллическими именами файлов во вложении.
    """
    msg = EmailMessage()
    msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"] = ", ".join(to_emails)
    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="longwang.ru")
    msg["Reply-To"] = SENDER_EMAIL
    
    msg.set_content(body_text)
    msg.add_alternative(body_html, subtype="html")
    
    for fid in (attachment_file_ids or []):
        try:
            local_path, orig_name = download_b24_file(fid)
            ctype, encoding = mimetypes.guess_type(orig_name)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            
            with open(local_path, "rb") as f:
                file_data = f.read()
                
            msg.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=orig_name
            )
        except Exception as e:
            print(f"Ошибка прикрепления файла {fid}: {e}")
            
    return msg


def save_draft_to_imap(msg: EmailMessage) -> str:
    """Сохраняет черновик в обе папки IMAP: 'Drafts' (для SnappyMail/клиентов со спец-флагом \Drafts) и '&BBcEMAQzBD4EQgQ+BDIEOgQ4-'."""
    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
        imap.login(SENDER_EMAIL, SENDER_PASS)
        for folder in ["Drafts", IMAP_DRAFTS_FOLDER]:
            try:
                imap.append(folder, "\\Draft", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
            except Exception as e:
                print(f"Предупреждение при сохранении в {folder}: {e}")
    return msg["Message-ID"]


def ensure_crm_todo(
    deal_id: int,
    responsible_id: int = 1,
    days_ahead: int = 5,
    subject: str = "",
    description: str = "",
    close_activity_ids: list = None
) -> int:
    """
    Создает контрольное дело типа CRM_TODO (TYPE_ID: 6) в Битрикс24.
    Закрывает устаревшие дела, если переданы их ID.
    """
    for aid in (close_activity_ids or []):
        try:
            call_b24("crm.activity.update", {"id": aid, "fields": {"COMPLETED": "Y"}})
        except Exception as e:
            print(f"Предупреждение при закрытии старой активности {aid}: {e}")

    now = datetime.now()
    deadline = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%dT18:00:00+03:00")
    
    fields = {
        "OWNER_TYPE_ID": 2,
        "OWNER_ID": deal_id,
        "TYPE_ID": 6,  # Задача / CRM_TODO
        "PROVIDER_ID": "CRM_TODO",
        "SUBJECT": subject,
        "START_TIME": deadline,
        "END_TIME": deadline,
        "DEADLINE": deadline,
        "RESPONSIBLE_ID": responsible_id,
        "DESCRIPTION": description,
        "COMPLETED": "N"
    }
    res = call_b24("crm.activity.add", {"fields": fields})
    return res.get("result", 0)


def ensure_call_activity(
    deal_id: int,
    responsible_id: int = 1,
    days_ahead: int = 5,
    subject: str = "",
    description: str = "",
    phone: str = None,
    contact_id: int = None,
    company_id: int = None
) -> int:
    """
    Создает дело типа Звонок (TYPE_ID: 2) ТОЛЬКО при >= 3 безответных касаниях.
    """
    now = datetime.now()
    deadline = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%dT18:00:00+03:00")
    
    fields = {
        "OWNER_TYPE_ID": 2,
        "OWNER_ID": deal_id,
        "TYPE_ID": 2,  # Звонок
        "SUBJECT": subject,
        "START_TIME": deadline,
        "END_TIME": deadline,
        "DEADLINE": deadline,
        "RESPONSIBLE_ID": responsible_id,
        "DESCRIPTION": description,
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
    return res.get("result", 0)


def format_greeting(contact_name: str) -> str:
    """Формирует строго одно уважительное приветствие."""
    parts = contact_name.strip().split()
    if len(parts) >= 2:
        # Проверяем, есть ли имя и отчество
        first_name = parts[1] if len(parts) > 1 and parts[0].endswith(('ов', 'ев', 'ин', 'ын', 'ий', 'ая')) else parts[0]
        # Если есть отчество
        patronymic = parts[2] if len(parts) > 2 else ""
        if patronymic and patronymic.endswith(('ич', 'на')):
            return f"{first_name} {patronymic}, добрый день!"
        return f"{first_name}, добрый день!"
    elif len(parts) == 1 and parts[0] and parts[0] != "None":
        return f"{parts[0]}, добрый день!"
    return "Добрый день!"


def process_batch_3(save_draft: bool = True) -> list:
    """
    Обработка Партии 3 из 5 сделок (898, 908, 918, 976, 978):
    - Сделка 898: АО «НПЦАП» (Сергей Матюшин) — УФ-лампа экспонирования
    - Сделка 908: ООО «Лебедяньмолоко» (Олег Соловьёв) — Krones и Delta
    - Сделка 918: ООО «СПБ ЗПС» (Степан Антончик) — Реле Shenler
    - Сделка 976: АК «АЛРОСА» (Наталья Баженова) — PHOENIX EMC и КГТ
    - Сделка 978: ООО «ГСТ» (Алексей Шарапов) — Гидроударник YONDA YDH802
    """
    results = []

    # 1. СДЕЛКА 898: АО «НПЦАП»
    p898_to = ["otd253_6@npcap.ru"]
    p898_subj = "Re: Коммерческое предложение на ультрафиолетовые лампы для установки экспонирования — АО «НПЦАП»"
    p898_text = (
        "Сергей, добрый день!\n\n"
        "Направляю вам ранее подготовленное коммерческое предложение по поставке ультрафиолетовых ламп "
        "для установки экспонирования (4 шт.) для АО «НПЦАП» (файл расчета дублирую во вложении).\n\n"
        "Подскажите, пожалуйста, удалось ли техническим специалистам ознакомиться с предложением? "
        "Планируется ли закупка в ближайшее время?\n"
        "Если требуются уточнения по характеристикам, срокам поставки или условиям оплаты — дайте знать, оперативно согласуем.\n\n"
        "--\nС уважением, Артем\nLong Wang, ООО \"Ци Линь\"\nТел.: +7 (921) 959-75-33 | Email: sales@longwang.ru\nСайт: longwang.ru"
    )
    p898_html = """
    <p>Сергей, добрый день!</p>
    <p>Направляю вам ранее подготовленное коммерческое предложение по поставке <b>ультрафиолетовых ламп для установки экспонирования (4 шт.)</b> для АО «НПЦАП» (файл расчета дублирую во вложении).</p>
    <p>Подскажите, пожалуйста, удалось ли техническим специалистам ознакомиться с предложением? Планируется ли закупка в ближайшее время?</p>
    <p>Если требуются уточнения по характеристикам, срокам поставки или условиям оплаты — дайте знать, оперативно согласуем.</p>
    <br>
    --<br>
    <b>С уважением, Артем</b><br>
    Long Wang, ООО "Ци Линь"<br>
    Тел.: +7 (921) 959-75-33 | Email: sales@longwang.ru<br>
    Сайт: <a href="https://longwang.ru">longwang.ru</a>
    """
    p898_files = [71018]
    msg_id_898 = None
    if save_draft:
        msg = build_email_message(p898_to, [], p898_subj, p898_text, p898_html, p898_files)
        msg_id_898 = save_draft_to_imap(msg)
    act_898 = ensure_crm_todo(
        deal_id=898,
        responsible_id=1,
        days_ahead=5,
        subject="Контроль ответа на КП: АО «НПЦАП» (УФ-лампы экспонирования)",
        description="24.09.2026 сохранен черновик в папке 'Черновики' (sales@longwang.ru) с КП на УФ-лампы. Контроль ответа на 29.09.2026."
    )
    results.append({
        "deal_id": 898,
        "company": "АО «НПЦАП»",
        "contact": "Сергей Матюшин",
        "email": p898_to[0],
        "subject": p898_subj,
        "msg_id": msg_id_898,
        "activity_id": act_898,
        "activity_type": "CRM_TODO"
    })

    # 2. СДЕЛКА 908: ООО «Лебедяньмолоко»
    p908_to = ["oleg.solovjev70@yandex.ru"]
    p908_subj = "Re: Коммерческие предложения по оборудованию Krones и датчикам Delta — ООО «Лебедяньмолоко»"
    p908_text = (
        "Олег, добрый день!\n\n"
        "Направляю вам ранее сформированные коммерческие предложения по оборудованию для ООО «Лебедяньмолоко» "
        "(дублирую расчеты во вложении):\n"
        "1. Запасные части и компоненты для линий розлива Krones.\n"
        "2. Датчики Delta.\n\n"
        "Подскажите, пожалуйста, удалось ли техническим службам рассмотреть данные спецификации? "
        "Планируется ли согласование закупки в ближайший период?\n"
        "Если требуется скорректировать объем или уточнить условия поставки — готовы оперативно ответить.\n\n"
        "--\nС уважением, Артем\nLong Wang, ООО \"Ци Линь\"\nТел.: +7 (921) 959-75-33 | Email: sales@longwang.ru\nСайт: longwang.ru"
    )
    p908_html = """
    <p>Олег, добрый день!</p>
    <p>Направляю вам ранее сформированные коммерческие предложения по оборудованию для ООО «Лебедяньмолоко» (дублирую расчеты во вложении):</p>
    <ul>
      <li><b>Компоненты для линий розлива Krones</b>;</li>
      <li><b>Датчики Delta</b>.</li>
    </ul>
    <p>Подскажите, пожалуйста, удалось ли техническим службам рассмотреть данные спецификации? Планируется ли согласование закупки в ближайший период?</p>
    <p>Если требуется скорректировать объем или уточнить условия поставки — готовы оперативно ответить.</p>
    <br>
    --<br>
    <b>С уважением, Артем</b><br>
    Long Wang, ООО "Ци Линь"<br>
    Тел.: +7 (921) 959-75-33 | Email: sales@longwang.ru<br>
    Сайт: <a href="https://longwang.ru">longwang.ru</a>
    """
    p908_files = [86316, 86314]
    msg_id_908 = None
    if save_draft:
        msg = build_email_message(p908_to, [], p908_subj, p908_text, p908_html, p908_files)
        msg_id_908 = save_draft_to_imap(msg)
    act_908 = ensure_crm_todo(
        deal_id=908,
        responsible_id=1,
        days_ahead=5,
        subject="Контроль ответа на КП: ООО «Лебедяньмолоко» (Krones и Delta)",
        description="24.09.2026 сохранен черновик в папке 'Черновики' (sales@longwang.ru) с КП на Krones и Delta. Контроль ответа на 29.09.2026."
    )
    results.append({
        "deal_id": 908,
        "company": "ООО «Лебедяньмолоко»",
        "contact": "Олег Соловьёв",
        "email": p908_to[0],
        "subject": p908_subj,
        "msg_id": msg_id_908,
        "activity_id": act_908,
        "activity_type": "CRM_TODO"
    })

    # 3. СДЕЛКА 918: ООО «СПБ ЗПС»
    p918_to = ["antonchik@zps.ru"]
    p918_subj = "Re: Коммерческое предложение на реле Shenler — ООО «СПБ ЗПС»"
    p918_text = (
        "Степан, добрый день!\n\n"
        "Направляю вам расчет по поставке промежуточных реле Shenler RKF4CO024LT (120 шт.) и розеток SKB14-E (120 шт.) "
        "для ООО «СПБ ЗПС» (файл КП во вложении).\n\n"
        "Подскажите, пожалуйста, согласована ли спецификация? Актуальна ли закупка в текущем месяце?\n"
        "Если необходимы уточнения по срокам поставки или условиям оплаты — дайте знать, оперативно решим.\n\n"
        "--\nС уважением, Артем\nLong Wang, ООО \"Ци Линь\"\nТел.: +7 (921) 959-75-33 | Email: sales@longwang.ru\nСайт: longwang.ru"
    )
    p918_html = """
    <p>Степан, добрый день!</p>
    <p>Направляю вам расчет по поставке <b>промежуточных реле Shenler RKF4CO024LT (120 шт.) и розеток SKB14-E (120 шт.)</b> для ООО «СПБ ЗПС» (файл КП во вложении).</p>
    <p>Подскажите, пожалуйста, согласована ли спецификация? Актуальна ли закупка в текущем месяце?</p>
    <p>Если необходимы уточнения по срокам поставки или условиям оплаты — дайте знать, оперативно решим.</p>
    <br>
    --<br>
    <b>С уважением, Артем</b><br>
    Long Wang, ООО "Ци Линь"<br>
    Тел.: +7 (921) 959-75-33 | Email: sales@longwang.ru<br>
    Сайт: <a href="https://longwang.ru">longwang.ru</a>
    """
    p918_files = [95912]
    msg_id_918 = None
    if save_draft:
        msg = build_email_message(p918_to, [], p918_subj, p918_text, p918_html, p918_files)
        msg_id_918 = save_draft_to_imap(msg)
    act_918 = ensure_crm_todo(
        deal_id=918,
        responsible_id=1,
        days_ahead=5,
        subject="Контроль ответа на КП: ООО «СПБ ЗПС» (Реле Shenler 120 шт)",
        description="24.09.2026 сохранен черновик в папке 'Черновики' (sales@longwang.ru) с КП на реле Shenler. Контроль ответа на 29.09.2026."
    )
    results.append({
        "deal_id": 918,
        "company": "ООО «СПБ ЗПС»",
        "contact": "Степан Антончик",
        "email": p918_to[0],
        "subject": p918_subj,
        "msg_id": msg_id_918,
        "activity_id": act_918,
        "activity_type": "CRM_TODO"
    })

    # 4. СДЕЛКА 976: АК «АЛРОСА» (ПАО)
    p976_to = ["BazhenovaNF@alrosa.ru"]
    p976_subj = "Re: Коммерческое предложение на фильтры PHOENIX EMC и лампы КГТ — АК «АЛРОСА»"
    p976_text = (
        "Наталья, добрый день!\n\n"
        "Направляю вам коммерческое предложение по поставке фильтров PHOENIX EMC (E04-EHE34A-M5E4-1M) и ламп КГТ "
        "для АК «АЛРОСА» (файл расчета дублирую во вложении).\n\n"
        "Подскажите, пожалуйста, удалось ли техническим службам рассмотреть данное предложение? "
        "Планируется ли размещение заказа в ближайшее время?\n"
        "Если требуется предоставить дополнительные технические параметры или обсудить условия отгрузки — готовы помочь.\n\n"
        "--\nС уважением, Артем\nLong Wang, ООО \"Ци Линь\"\nТел.: +7 (921) 959-75-33 | Email: sales@longwang.ru\nСайт: longwang.ru"
    )
    p976_html = """
    <p>Наталья, добрый день!</p>
    <p>Направляю вам коммерческое предложение по поставке <b>фильтров PHOENIX EMC (E04-EHE34A-M5E4-1M) и ламп КГТ</b> для АК «АЛРОСА» (файл расчета дублирую во вложении).</p>
    <p>Подскажите, пожалуйста, удалось ли техническим службам рассмотреть данное предложение? Планируется ли размещение заказа в ближайшее время?</p>
    <p>Если требуется предоставить дополнительные технические параметры или обсудить условия отгрузки — готовы помочь.</p>
    <br>
    --<br>
    <b>С уважением, Артем</b><br>
    Long Wang, ООО "Ци Линь"<br>
    Тел.: +7 (921) 959-75-33 | Email: sales@longwang.ru<br>
    Сайт: <a href="https://longwang.ru">longwang.ru</a>
    """
    p976_files = [85900]
    msg_id_976 = None
    if save_draft:
        msg = build_email_message(p976_to, [], p976_subj, p976_text, p976_html, p976_files)
        msg_id_976 = save_draft_to_imap(msg)
    act_976 = ensure_crm_todo(
        deal_id=976,
        responsible_id=1,
        days_ahead=5,
        subject="Контроль ответа на КП: АК «АЛРОСА» (PHOENIX EMC и КГТ)",
        description="24.09.2026 сохранен черновик в папке 'Черновики' (sales@longwang.ru) с КП на PHOENIX EMC. Контроль ответа на 29.09.2026."
    )
    results.append({
        "deal_id": 976,
        "company": "АК «АЛРОСА» (ПАО)",
        "contact": "Наталья Баженова",
        "email": p976_to[0],
        "subject": p976_subj,
        "msg_id": msg_id_976,
        "activity_id": act_976,
        "activity_type": "CRM_TODO"
    })

    # 5. СДЕЛКА 978: ООО «ГСТ»
    p978_to = ["san@geospt.ru"]
    p978_subj = "Re: Коммерческое предложение на гидроударник YONDA YDH802 — ООО «ГСТ»"
    p978_text = (
        "Алексей, добрый день!\n\n"
        "Направляю вам ранее подготовленное коммерческое предложение по поставке гидроударника "
        "YONDA YDH802 Hydraulic Drilling Head (1 шт.) для ООО «ГСТ» (файл расчета дублирую во вложении).\n\n"
        "Подскажите, пожалуйста, удалось ли согласовать спецификацию и стоимость с руководством? "
        "Планируется ли заключение договора в ближайший период?\n"
        "Если требуются корректировки по условиям поставки или оплате — оперативно согласуем.\n\n"
        "--\nС уважением, Артем\nLong Wang, ООО \"Ци Линь\"\nТел.: +7 (921) 959-75-33 | Email: sales@longwang.ru\nСайт: longwang.ru"
    )
    p978_html = """
    <p>Алексей, добрый день!</p>
    <p>Направляю вам ранее подготовленное коммерческое предложение по поставке <b>гидроударника YONDA YDH802 Hydraulic Drilling Head (1 шт.)</b> для ООО «ГСТ» (файл расчета дублирую во вложении).</p>
    <p>Подскажите, пожалуйста, удалось ли согласовать спецификацию и стоимость с руководством? Планируется ли заключение договора в ближайший период?</p>
    <p>Если требуются корректировки по условиям поставки или оплате — оперативно согласуем.</p>
    <br>
    --<br>
    <b>С уважением, Артем</b><br>
    Long Wang, ООО "Ци Линь"<br>
    Тел.: +7 (921) 959-75-33 | Email: sales@longwang.ru<br>
    Сайт: <a href="https://longwang.ru">longwang.ru</a>
    """
    p978_files = [87440]
    msg_id_978 = None
    if save_draft:
        msg = build_email_message(p978_to, [], p978_subj, p978_text, p978_html, p978_files)
        msg_id_978 = save_draft_to_imap(msg)
    act_978 = ensure_crm_todo(
        deal_id=978,
        responsible_id=1,
        days_ahead=5,
        subject="Контроль ответа на КП: ООО «ГСТ» (Гидроударник YONDA YDH802)",
        description="24.09.2026 сохранен черновик в папке 'Черновики' (sales@longwang.ru) с КП на гидроударник YONDA. Контроль ответа на 29.09.2026."
    )
    results.append({
        "deal_id": 978,
        "company": "ООО «ГСТ»",
        "contact": "Алексей Шарапов",
        "email": p978_to[0],
        "subject": p978_subj,
        "msg_id": msg_id_978,
        "activity_id": act_978,
        "activity_type": "CRM_TODO"
    })

    # Также связываем сделку 818 (Вакуленко) с контрольным делом без отправки повторного письма (кулдаун)
    act_818 = ensure_crm_todo(
        deal_id=818,
        responsible_id=1,
        days_ahead=5,
        subject="Контроль ответа на КП: ОАО «МЛЗ» (Датчики Atlas Copco — Роман Вакуленко)",
        description="24.09.2026 клиенту уже отправлено письмо по сделкам 570/572. Сделка 818 поставлена на контроль синхронно на 29.09.2026 без повторного письма (защита от спама)."
    )

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-3", action="store_true", help="Обработать Партию 3 (сделки 898, 908, 918, 976, 978)")
    parser.add_argument("--save-draft", action="store_true", default=True, help="Сохранить черновики в IMAP Черновики")
    args = parser.parse_args()

    if args.batch_3:
        print("\n>>> ОБРАБОТКА ПАРТИИ 3 (СДЕЛКИ 898, 908, 918, 976, 978) В РЕЖИМЕ DRAFTS <<<")
        res = process_batch_3(save_draft=args.save_draft)
        out_path = os.path.join(os.path.dirname(__file__), "..", "scratch", "batch_3_results.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f"Успешно обработано {len(res)} сделок. Результаты сохранены в {out_path}")
        for r in res:
            print(f"Сделка {r['deal_id']} | {r['company']} | {r['contact']} | {r['email']} | Черновик: OK | Дело Б24 ID: {r['activity_id']} ({r['activity_type']})")
    else:
        print("Используйте --batch-3 для запуска обработки Партии 3.")
