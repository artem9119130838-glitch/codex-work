#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/process_deals_without_activities.py
============================================================
Реализация процесса Follow-up сделок по непререкаемому уставу FOLLOWUP_PROCESS_POLICY.md:
1. Quote Attachment Guard: автоматическое скачивание и прикрепление ранее отправленного КП через disk.file.get.
2. 7-Day Touch Cooldown Guard: исключение сделок, где любое касание было < 7 дней назад.
3. Thread Retention & Reply-To Guard: ответ строго в цепочке (In-Reply-To, References, цитирование).
4. Bitrix24 Native Signature Guard: эталонная подпись ящика сотрудника из Битрикс24.
5. AI-Driven Model Drafting: формирование очищенного досье переписки для ИИ-модели (Antigravity).
"""

import os
import sys
import time
import json
import imaplib
import argparse
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

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

B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
IMAP_HOST = os.getenv("IMAP_SERVER", "mail.hostland.ru")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
SENDER_EMAIL = os.getenv("IMAP_USER", "sales@longwang.ru")
SENDER_PASS = os.getenv("IMAP_PASSWORD", "")
SENDER_NAME = "Артем Петров Long Wang, ООО Ци Линь"
IMAP_DRAFTS_FOLDER = "Drafts"

# Эталонная HTML-подпись из Битрикс24
BITRIX_SIGNATURE_HTML = """
<div class="main-mail-form-signature" style="font-family: Arial, sans-serif; font-size: 13px; color: #333; margin-top: 20px;">
	 --<br/>
<span style='font-family: "Times New Roman", Times; font-size: 12pt;'>С уважением,&nbsp;Артем</span><br/>
<a href="https://longwang.ru/" target="_blank"><span style='font-family: "Times New Roman", Times; font-size: 12pt;'>LongWang</span></a><span style='font-family: "Times New Roman", Times; font-size: 12pt;'>&nbsp;Тел&nbsp;</span><a href="tel:+78125091245" target="_blank"><span style='font-family: "Times New Roman", Times; font-size: 12pt;'>+7 (812) 509-1245</span></a><br/>
<a href="mailto:sales@longwang.ru" target="_blank"><span style='font-family: "Times New Roman", Times; font-size: 12pt;'>sales@longwang.ru</span></a><br/>
<br/>
	 ------------------------------<br/>
<i><span style='font-family: "Times New Roman", Times; font-size: 10pt;'>Если Вам в дальнейшем понадобится что-то из оригинального оборудования&nbsp;Atlas Copco, SMC, Caterpillar, Danfoss, Siemens, Megger, Fronius, Brevini, Autonics&nbsp;и/или&nbsp;</span></i><a href="https://longwang.ru/supplies-services-china/brands/" target="_blank"><i><span style='font-family: "Times New Roman", Times; font-size: 10pt;'>этих производителей</span></i></a><i><span style='font-family: "Times New Roman", Times; font-size: 10pt;'>,&nbsp;то у нас и нашего китайского и сербского представительства заключены прямые договоры на поставку с ними и их дистрибьютерами. Также у нашей компании есть филиалы в Казахстане и Кыргызстане для&nbsp;</span></i><a href="https://longwang.ru/supplies-services-china/platezhi-v-kitai/" target="_blank"><i><span style='font-family: "Times New Roman", Times; font-size: 10pt;'>проведения оплат</span></i></a><i><span style='font-family: "Times New Roman", Times; font-size: 10pt;'>&nbsp;и организации&nbsp;</span></i><a href="https://longwang.ru/supplies-services-china/dostavka-is-kitaya/" target="_blank"><i><span style='font-family: "Times New Roman", Times; font-size: 10pt;'>доставки</span></i></a><i><span style='font-family: "Times New Roman", Times; font-size: 10pt;'>.</span></i>
</div>
"""

BITRIX_SIGNATURE_TEXT = """
--
С уважением, Артем
LongWang Тел +7 (812) 509-1245
sales@longwang.ru
------------------------------
Если Вам в дальнейшем понадобится что-то из оригинального оборудования Atlas Copco, SMC, Caterpillar, Danfoss, Siemens, Megger, Fronius, Brevini, Autonics и/или этих производителей, то у нас и нашего китайского и сербского представительства заключены прямые договоры на поставку с ними и их дистрибьютерами. Также у нашей компании есть филиалы в Казахстане и Кыргызстане для проведения оплат и организации доставки.
"""

def call_b24(method: str, params: dict = None) -> dict:
    url = f"{B24_WEBHOOK}{method}"
    res = requests.post(url, json=params or {}, timeout=30)
    res.raise_for_status()
    return res.json().get("result", {})

def download_b24_disk_file(file_id: int):
    """Скачивает файл с диска Битрикс24 по file_id."""
    res = call_b24("disk.file.get", {"id": file_id})
    if not res:
        return None, None
    name = res.get("NAME")
    dl_url = res.get("DOWNLOAD_URL")
    if not dl_url:
        return None, None
    r = requests.get(dl_url, timeout=30)
    if r.status_code == 200:
        return name, r.content
    return None, None

def clean_html_to_text(html_content: str) -> str:
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Удаляем цитаты и стили при очистке
    for q in soup.find_all(["blockquote", "style", "script"]):
        q.decompose()
    text = soup.get_text("\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)

ALLOWED_STAGES = ["NEW", "PREPARATION", "PREPAYMENT_INVOICE", "EXECUTING", "FINAL_INVOICE"]
FALLBACK_REFERENCE_FILE_ID = 89762 # Диск Б24: Презентация и референс-лист.pdf


def get_cross_entity_activities(deal_id, lead_id=None, contact_id=None, to_email=None):
    """
    Правило 7: Сквозной поиск переписки и файлов (Сделка -> Лид -> Контакт -> Поиск лидов по email).
    """
    acts = call_b24("crm.activity.list", {
        "filter": {"OWNER_TYPE_ID": 2, "OWNER_ID": deal_id},
        "order": {"START_TIME": "DESC"},
        "select": ["ID", "SUBJECT", "START_TIME", "TYPE_ID", "DIRECTION", "DESCRIPTION"]
    }) or []
    
    seen_ids = {a.get("ID") for a in acts}
    
    # 1. Проверяем привязанный Лид
    if lead_id:
        lead_acts = call_b24("crm.activity.list", {
            "filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lead_id},
            "order": {"START_TIME": "DESC"},
            "select": ["ID", "SUBJECT", "START_TIME", "TYPE_ID", "DIRECTION", "DESCRIPTION"]
        }) or []
        for la in lead_acts:
            if la.get("ID") not in seen_ids:
                acts.append(la)
                seen_ids.add(la.get("ID"))
                
    # 2. Если писем нет в сделке и лиде, ищем в Контакте
    has_emails = any(a.get("TYPE_ID") == "4" for a in acts)
    if not has_emails and contact_id:
        contact_acts = call_b24("crm.activity.list", {
            "filter": {"OWNER_TYPE_ID": 3, "OWNER_ID": contact_id},
            "order": {"START_TIME": "DESC"},
            "select": ["ID", "SUBJECT", "START_TIME", "TYPE_ID", "DIRECTION", "DESCRIPTION"]
        }) or []
        for ca in contact_acts:
            if ca.get("ID") not in seen_ids:
                acts.append(ca)
                seen_ids.add(ca.get("ID"))
                
    # 3. Если всё еще нет писем, но известен email - ищем связанные лиды по email
    has_emails = any(a.get("TYPE_ID") == "4" for a in acts)
    if not has_emails and to_email:
        search_leads = call_b24("crm.lead.list", {
            "filter": {"=EMAIL": to_email},
            "select": ["ID"]
        }) or []
        for sl in search_leads:
            sl_id = sl.get("ID")
            sl_acts = call_b24("crm.activity.list", {
                "filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": sl_id},
                "order": {"START_TIME": "DESC"},
                "select": ["ID", "SUBJECT", "START_TIME", "TYPE_ID", "DIRECTION", "DESCRIPTION"]
            }) or []
            for sla in sl_acts:
                if sla.get("ID") not in seen_ids:
                    acts.append(sla)
                    seen_ids.add(sla.get("ID"))
                    
    # Сортируем все найденные дела по убыванию времени
    acts.sort(key=lambda x: x.get("START_TIME") or "", reverse=True)
    return acts


def collect_dossier_deals_without_activities(assigned_by=1, max_deals=10, cooldown_days=7, exclude_ids=None):
    """
    Сканирует сделки Артема без активных дел с соблюдением 7-дневного кулдауна
    и формирует полное досье переписки для ИИ-модели.
    """
    now = datetime.now()
    cooldown_limit_dt = now - timedelta(days=cooldown_days)
    today_str = now.strftime("%Y-%m-%d")
    exclude_set = {int(x) for x in exclude_ids} if exclude_ids else set()
    
    print(f"\n[1/3] Поиск открытых сделок Артема (ID={assigned_by})...")
    if exclude_set:
        print(f"  Исключено ранее обработанных ID: {exclude_set}")
    start = 0
    candidate_deals = []
    excluded_deals = []
    
    while len(candidate_deals) < max_deals and start <= 600:
        deals = call_b24("crm.deal.list", {
            "filter": {"ASSIGNED_BY_ID": assigned_by, "CLOSED": "N"},
            "order": {"DATE_CREATE": "DESC"},
            "select": ["ID", "TITLE", "STAGE_ID", "COMPANY_ID", "CONTACT_ID", "DATE_CREATE", "OPPORTUNITY", "CURRENCY_ID", "LEAD_ID"],
            "start": start
        })
        if not deals:
            break
            
        for d in deals:
            did = int(d["ID"])
            if did in exclude_set:
                continue
            stage_id = d.get("STAGE_ID")
            
            # Правило 6: Запрет follow-up для сделок «В работе» и на исполнении (только ручная связь менеджера)
            if stage_id not in ALLOWED_STAGES:
                excluded_deals.append({
                    "deal_id": did,
                    "title": d.get("TITLE"),
                    "stage": stage_id,
                    "reason": f"Стадия '{stage_id}' запрещена для авто-follow-up (в работе / исполнение, только ручная связь менеджера)"
                })
                print(f"  [X] Сделка #{did} ИСКЛЮЧЕНА (стадия '{stage_id}' запрещена для авто-follow-up)")
                continue

            # Проверяем активные незавершенные дела
            pending_acts = call_b24("crm.activity.list", {
                "filter": {"OWNER_TYPE_ID": 2, "OWNER_ID": did, "COMPLETED": "N"},
                "select": ["ID"]
            })
            if pending_acts:
                continue # Есть активные дела, пропускаем
                
            cid = d.get("CONTACT_ID")
            coid = d.get("COMPANY_ID")
            lead_id = d.get("LEAD_ID")
            contact = call_b24("crm.contact.get", {"id": cid}) if cid else {}
            company = call_b24("crm.company.get", {"id": coid}) if coid else {}
            
            emails = contact.get("EMAIL", [])
            to_email = emails[0].get("VALUE") if emails else None
            if not to_email and company:
                to_email = company.get("EMAIL", [{}])[0].get("VALUE")
                
            if not to_email:
                continue

            phones = contact.get("PHONE", [])
            phone_val = phones[0].get("VALUE") if phones else None
            if not phone_val and company:
                phone_val = company.get("PHONE", [{}])[0].get("VALUE")

            # Правило 7: Сквозной сбор переписки (сделка -> лид -> контакт -> поиск по email)
            all_acts = get_cross_entity_activities(deal_id=did, lead_id=lead_id, contact_id=cid, to_email=to_email)
                
            last_touch_date = None
            last_touch_desc = "Нет касаний"
            
            for a in all_acts:
                st = a.get("START_TIME")
                if st:
                    try:
                        dt = datetime.fromisoformat(st.replace("Z", "+00:00")).replace(tzinfo=None)
                        if not last_touch_date or dt > last_touch_date:
                            last_touch_date = dt
                            type_name = "Письмо" if a.get("TYPE_ID") == "4" else ("Звонок" if a.get("TYPE_ID") == "2" else "Дело")
                            last_touch_desc = f"{type_name} '{a.get('SUBJECT')}' от {dt.strftime('%d.%m.%Y')}"
                    except Exception:
                        pass
                        
            if last_touch_date and last_touch_date > cooldown_limit_dt:
                days_ago = (now - last_touch_date).days
                excluded_deals.append({
                    "deal_id": did,
                    "title": d.get("TITLE"),
                    "days_ago": days_ago,
                    "reason": f"Последнее касание было {days_ago} дн. назад ({last_touch_desc}), действует 7-дневный кулдаун"
                })
                print(f"  [X] Сделка #{did} ИСКЛЮЧЕНА (кулдаун {days_ago} дн. < 7 дн.): '{d.get('TITLE')}'")
                continue
                
            # Сделка подошла! Собираем глубокое досье
            print(f"  [+] Сделка #{did} ОТОБРАНА для follow-up: '{d.get('TITLE')}' (касание было {(now - last_touch_date).days if last_touch_date else 'давнее'} дн. назад)")
            
            # История писем
            email_acts = [a for a in all_acts if a.get("TYPE_ID") == "4"]
            outgoing_count = sum(1 for m in email_acts if m.get("DIRECTION") == "2" or "Re:" in m.get("SUBJECT", ""))
            
            # Поиск последнего исходящего/входящего письма и вложений КП
            last_mgr_email = None
            last_any_email = None
            kp_files = []
            
            for ea in email_acts:
                if not last_any_email:
                    last_any_email = call_b24("crm.activity.get", {"id": ea.get("ID")})
                    
                if ea.get("DIRECTION") == "2" and not last_mgr_email:
                    full_ea = call_b24("crm.activity.get", {"id": ea.get("ID")})
                    last_mgr_email = full_ea
                    
                full_ea = call_b24("crm.activity.get", {"id": ea.get("ID")})
                flist = full_ea.get("FILES") or []
                for f in flist:
                    fid = f.get("id")
                    if fid and fid not in [k["id"] for k in kp_files]:
                        kp_files.append({"id": fid, "activity_id": ea.get("ID")})

            chosen_email = last_mgr_email or last_any_email

            # Правило 7: Если персональный файл КП не найден во всей истории, прикрепляем презентацию и референс-лист
            if not kp_files:
                kp_files.append({
                    "id": FALLBACK_REFERENCE_FILE_ID,
                    "activity_id": None,
                    "name": "Презентация и референс-лист.pdf",
                    "is_fallback": True
                })
                            
            # Собираем очищенную историю
            clean_history = []
            for ea in email_acts[:5]:
                direction = "Менеджер -> Клиенту" if ea.get("DIRECTION") == "2" else "Клиент -> Менеджеру"
                clean_text = clean_html_to_text(ea.get("DESCRIPTION", ""))
                clean_history.append({
                    "date": ea.get("START_TIME", "")[:10],
                    "direction": direction,
                    "subject": ea.get("SUBJECT", ""),
                    "text_preview": clean_text[:400]
                })
                
            # Записи звонков
            call_acts = [a for a in all_acts if a.get("TYPE_ID") == "2"]
            clean_calls = []
            for ca in call_acts[:3]:
                clean_calls.append({
                    "date": ca.get("START_TIME", "")[:10],
                    "subject": ca.get("SUBJECT", ""),
                    "notes": ca.get("DESCRIPTION", "")[:300]
                })
                
            c_first = (contact.get("NAME") or "").strip()
            c_last = (contact.get("LAST_NAME") or "").strip()
            c_full = f"{c_first} {c_last}".strip() or "Коллеги"
            
            candidate_deals.append({
                "deal_id": did,
                "title": d.get("TITLE"),
                "stage": d.get("STAGE_ID"),
                "opportunity": f"{d.get('OPPORTUNITY')} {d.get('CURRENCY_ID')}",
                "contact_name": c_full,
                "company_name": company.get("TITLE", ""),
                "to_email": to_email,
                "phone": phone_val,
                "outgoing_count": outgoing_count,
                "last_touch_date": last_touch_date.strftime("%Y-%m-%d") if last_touch_date else "Неизвестно",
                "days_since_touch": (now - last_touch_date).days if last_touch_date else 999,
                "last_mgr_email_id": chosen_email.get("ID") if chosen_email else None,
                "last_mgr_subject": chosen_email.get("SUBJECT") if chosen_email else None,
                "last_mgr_message_id": (chosen_email.get("SETTINGS", {}).get("MESSAGE_HEADERS", {}).get("Message-Id") if chosen_email else None),
                "last_mgr_body_html": chosen_email.get("DESCRIPTION") if chosen_email else "",
                "kp_files": kp_files,
                "clean_history": clean_history,
                "clean_calls": clean_calls
            })
            
            if len(candidate_deals) >= max_deals:
                break
                
        start += 50
        
    return candidate_deals, excluded_deals


class SelfCheckError(Exception):
    """Исключение при непрохождении аппаратного предпроверочного контроля письма."""
    pass


def sanitize_quoted_html(raw_html: str) -> str:
    """
    Очищает цитируемый HTML от полных тегов <!DOCTYPE>, <html>, <head>, <meta>, <style>, <script>,
    чтобы избежать вложенных документов, ломающих MIME и триггерящих антиспам-фильтры промышленных серверов (Kaspersky, DrWeb, ПЗМ).
    """
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup.find_all(["script", "style", "meta", "link", "title", "head"]):
        tag.decompose()
    body = soup.find("body")
    inner_html = body.decode_contents() if body else str(soup)
    return inner_html.strip()


def sanitize_quoted_text(raw_html: str, clean_preview: str = "") -> str:
    """
    Извлекает чистый читаемый текст исходного сообщения для text/plain версии письма.
    """
    if raw_html:
        soup = BeautifulSoup(raw_html, "html.parser")
        for tag in soup.find_all(["script", "style", "meta", "link", "blockquote", "head"]):
            tag.decompose()
        text = soup.get_text("\n")
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned = "\n".join(lines)
        if len(cleaned) > 40:
            return cleaned
    return clean_preview or "Нет доступного текста предыдущего письма."


def download_and_validate_pdf_attachments(deal_data: dict, max_files: int = 2) -> list:
    """
    Скачивает и валидирует вложения.
    Белый список: СТРОГО .pdf!
    Если персональный PDF КП отсутствует (или были только .docx / .jpg), подключает корпоративный PDF референс-листа (ID 89762).
    Возвращает list of tuples: [(filename, bytes), ...]
    """
    valid_attachments = []
    raw_kp_files = deal_data.get("kp_files") or []
    
    for kpf in raw_kp_files:
        fid = kpf.get("id")
        if not fid:
            continue
        fname, fbytes = download_b24_disk_file(fid)
        if not fname or not fbytes:
            continue
            
        # Проверка белого списка .pdf
        if fname.lower().endswith(".pdf") and len(fbytes) >= 5120:
            if fbytes.startswith(b"%PDF"):
                valid_attachments.append((fname, fbytes))
                print(f"    [PDF OK] Прикреплен КП/спецификация: '{fname}' ({len(fbytes)} байт)")
            else:
                print(f"    [WARN] Файл '{fname}' не прошел валидацию сигнатуры %PDF, пропущен")
        else:
            print(f"    [SECURITY GATE FILTER] Файл '{fname}' отклонен: вложения разрешены СТРОГО в формате .pdf (защита от отлупов 550 security reason)")

        if len(valid_attachments) >= max_files:
            break
            
    # Если валидный PDF так и не найден — подключаем гарантированный корпоративный референс-лист
    if not valid_attachments:
        print(f"    [FALLBACK] В истории сделки #{deal_data.get('deal_id')} не найдено валидных PDF КП. Подключаем официальную презентацию и референс-лист (ID {FALLBACK_REFERENCE_FILE_ID})...")
        fb_name, fb_bytes = download_b24_disk_file(FALLBACK_REFERENCE_FILE_ID)
        if fb_name and fb_bytes and fb_bytes.startswith(b"%PDF"):
            valid_attachments.append((fb_name, fb_bytes))
            print(f"    [FALLBACK OK] Корпоративный референс-лист '{fb_name}' ({len(fb_bytes)} байт) успешно прикреплен")
        else:
            raise ValueError(f"Критический сбой: не удалось скачать даже fallback-файл референс-листа ID {FALLBACK_REFERENCE_FILE_ID} с диска Битрикс24!")
            
    return valid_attachments


def pre_send_self_check(
    deal_data: dict,
    subject: str,
    new_letter_text: str,
    new_letter_html: str,
    quoted_text: str,
    quoted_html: str,
    attached_files: list,
    sender_email: str,
    sender_name: str
):
    """
    Правило 9: Аппаратный предпроверочный контроль письма перед созданием черновика или отправкой.
    """
    import re
    errors = []
    
    # 1. Stop-words and placeholders
    stop_patterns = [
        r"(?i)\b(test\s*body|test\s*subject|тестовое\s*тело|тестовая\s*тема|undefined|null|lorem\s*ipsum|заглушка|рыба|тут\s*текст)\b"
    ]
    combined_content = f"{subject}\n{new_letter_text}\n{new_letter_html}".lower()
    for pat in stop_patterns:
        if re.search(pat, combined_content):
            errors.append(f"Обнаружено недопустимое стоп-слово / заглушка по шаблону '{pat}'")

    # 2. Subject validation
    if not subject or len(subject.strip()) < 10:
        errors.append(f"Тема письма слишком короткая или пустая: '{subject}' (минимум 10 символов)")
    if subject.strip().lower() in ["re: запрос", "re: заявка", "re: заказ", "re: (без темы)", "re: без темы"]:
        errors.append(f"Мусорная/неявная тема письма: '{subject}'! Тема должна отражать оборудование и контрагента.")

    # 3. Thread quotation validation
    if not quoted_html or len(quoted_html.strip()) < 50:
        errors.append(f"Отсутствует или слишком короткая HTML-цитата предыдущей переписки (длина: {len(quoted_html.strip()) if quoted_html else 0} < 50 симв.)")
    if not quoted_text or len(quoted_text.strip()) < 30:
        errors.append("Отсутствует или слишком короткая текстовая цитата (plain text) в теле письма")
    forbidden_tags = ["<!doctype", "<html", "<head", "<meta", "<script"]
    for ft in forbidden_tags:
        if ft in quoted_html.lower():
            errors.append(f"Цитата HTML содержит недопустимый сырой тег '{ft}', ломающий MIME-структуру и блокируемый шлюзом безопасности")

    # 4. Attachments validation (PDF-ONLY WHITE LIST)
    if not attached_files:
        errors.append("В письме отсутствуют вложения! (Правило 1 и 9)")
    for fname, fbytes in attached_files:
        if not fname.lower().endswith(".pdf"):
            errors.append(f"Вложение '{fname}' нарушает политику безопасности: разрешены СТРОГО файлы .pdf! (.docx/.doc/.xls запрещены)")
        if len(fbytes) < 5120:
            errors.append(f"Вложение '{fname}' повреждено или имеет подозрительно малый размер: {len(fbytes)} байт (< 5 КБ)")
        if not fbytes.startswith(b"%PDF"):
            errors.append(f"Вложение '{fname}' не является валидным PDF-документом (отсутствует сигнатура %PDF)")

    # 5. Sender identity validation
    if sender_email.lower().strip() != "sales@longwang.ru":
        errors.append(f"Неверный ящик отправителя: '{sender_email}' (разрешен строго sales@longwang.ru)")
    if "salman@longwang.ru" in f"{sender_name} {new_letter_text}".lower():
        errors.append("В тексте нового письма обнаружен адрес 'salman@longwang.ru'! Отправка разрешена строго с sales@longwang.ru")

    # 6. Deal stage safety
    stage = deal_data.get("stage")
    if stage not in ALLOWED_STAGES:
        errors.append(f"Сделка #{deal_data.get('deal_id')} находится в стадии '{stage}' (запрещено для авто-follow-up, только менеджер лично)")

    # 7. Recipient email validation
    to_email = deal_data.get("to_email", "").strip()
    if not to_email or "@" not in to_email or "." not in to_email:
        errors.append(f"Некорректный email получателя: '{to_email}'")

    if errors:
        raise SelfCheckError("PRE-SEND SELF-CHECK СБОЙ! Письмо заблокировано:\n  - " + "\n  - ".join(errors))
    
    print(f"    [SELF-CHECK OK] Все 7 проверок пройдены успешно (PDF-only, цитата валидна, ящик sales, стоп-слов нет)")
    return True


def build_mime_email(deal_data: dict, ai_letter_text: str, ai_letter_html: str, custom_subject: str, valid_attachments: list) -> tuple:
    """
    Собирает валидное multipart/mixed письмо с цитатой, эталонной подписью и PDF вложениями,
    и прогоняет его через pre_send_self_check.
    """
    to_email = deal_data.get("to_email", "").strip()
    
    # Формирование осмысленной темы
    if custom_subject:
        clean_subj = custom_subject if custom_subject.startswith("Re:") else f"Re: {custom_subject}"
    else:
        last_subj = deal_data.get("last_mgr_subject") or ""
        clean_cand = last_subj.replace("Re:", "").replace("RE:", "").replace("Fwd:", "").replace("FW:", "").strip()
        is_generic = not clean_cand or clean_cand.lower() in ["запрос", "заявка", "заказ", "(без темы)", "кп", "без темы"] or len(clean_cand) < 4
        if is_generic:
            entity = deal_data.get("company_name") or deal_data.get("contact_name") or ""
            clean_subj = f"Re: {deal_data.get('title', 'Поставка оборудования')} — {entity}".strip(" —")
        else:
            clean_subj = f"Re: {clean_cand}"

    # Подготовка цитирования
    raw_body_html = deal_data.get("last_mgr_body_html") or ""
    sanitized_quote_html = sanitize_quoted_html(raw_body_html)
    quote_text_body = sanitize_quoted_text(raw_body_html, deal_data.get("title", ""))

    last_subj_display = deal_data.get("last_mgr_subject") or clean_subj
    last_touch_date = deal_data.get("last_touch_date") or datetime.now().strftime("%Y-%m-%d")

    if quote_text_body and len(quote_text_body.strip()) >= 15:
        quoted_html_block = f"""
    <br><br>
    <div class="gmail_quote">
      <div dir="ltr" class="gmail_attr">
        -------- Исходное сообщение --------<br>
        <b>Тема:</b> {last_subj_display}<br>
        <b>Дата:</b> {last_touch_date}<br>
        <b>От:</b> {SENDER_NAME} &lt;{SENDER_EMAIL}&gt;<br>
        <b>Кому:</b> {to_email}<br>
      </div>
      <br>
      <blockquote style="margin: 0 0 0 5px; padding: 5px 5px 5px 8px; border-left: 4px solid #e2e3e5;">
        {sanitized_quote_html}
      </blockquote>
    </div>
    """
        quoted_text_block = (
            f"\n\n-------- Исходное сообщение --------\n"
            f"Тема: {last_subj_display}\n"
            f"Дата: {last_touch_date}\n"
            f"От: {SENDER_NAME} <{SENDER_EMAIL}>\n"
            f"Кому: {to_email}\n\n"
            f"{quote_text_body}\n"
        )
    else:
        quoted_html_block = ""
        quoted_text_block = ""

    full_html = f"<div style='font-family: Arial, sans-serif; font-size: 14px;'>{ai_letter_html}</div>{BITRIX_SIGNATURE_HTML}{quoted_html_block}"
    full_text = f"{ai_letter_text}\n{BITRIX_SIGNATURE_TEXT}\n{quoted_text_block}".strip()

    # ОБЯЗАТЕЛЬНЫЙ АППАРАТНЫЙ SELF-CHECK
    pre_send_self_check(
        deal_data=deal_data,
        subject=clean_subj,
        new_letter_text=ai_letter_text,
        new_letter_html=ai_letter_html,
        quoted_text=quote_text_body,
        quoted_html=sanitized_quote_html,
        attached_files=valid_attachments,
        sender_email=SENDER_EMAIL,
        sender_name=SENDER_NAME
    )

    from email.headerregistry import Address
    msg = EmailMessage()
    msg["From"] = Address(SENDER_NAME, "sales", "longwang.ru")
    msg["To"] = to_email
    msg["Subject"] = clean_subj
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="longwang.ru")
    msg["Reply-To"] = SENDER_EMAIL
    msg["Sender"] = SENDER_EMAIL
    
    parent_msg_id = deal_data.get("last_mgr_message_id")
    if parent_msg_id:
        msg["In-Reply-To"] = parent_msg_id
        msg["References"] = parent_msg_id
        
    # Задаем текстовую часть и HTML-альтернативу
    msg.set_content(full_text)
    msg.add_alternative(full_html, subtype="html")

    # Прикрепляем валидные PDF вложения
    for fname, fbytes in valid_attachments:
        msg.add_attachment(fbytes, maintype="application", subtype="pdf", filename=fname)

    return msg, clean_subj, full_text, full_html


def save_sent_email_to_imap(msg_bytes: bytes) -> bool:
    """
    Сохраняет копию отправленного через SMTP письма в папку 'Sent' на сервере Hostland IMAP.
    """
    try:
        with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
            imap.login(SENDER_EMAIL, SENDER_PASS)
            for sent_folder in ["Sent", "&BB4EQgQ,BEAEMAQyBDsENQQ9BD0ESwQ1-", "INBOX.Sent", "Отправленные"]:
                res, _ = imap.select(sent_folder)
                if res == "OK":
                    imap.append(sent_folder, "\\Seen", imaplib.Time2Internaldate(time.time()), msg_bytes)
                    print(f"    [IMAP SENT OK] Копия письма сохранена в '{sent_folder}'")
                    return True
    except Exception as e:
        print(f"    [WARN] Не удалось сохранить копию в IMAP Sent: {e}")
    return False


def create_followup_draft_in_imap(deal_data: dict, ai_letter_text: str, ai_letter_html: str, custom_subject: str = None, attach_kp: bool = True) -> tuple:
    """
    Создает черновик follow-up в IMAP Roundcube с полным предпроверочным контролем:
    - Ответ в цепочке (In-Reply-To, References, цитирование переписки)
    - Осмысленная тема письма (Meaningful Subject Guard)
    - Прикрепление только валидных PDF вложений
    - Эталонная подпись Битрикс24
    - Предпроверочный Self-Check
    """
    valid_attachments = download_and_validate_pdf_attachments(deal_data) if attach_kp else []
    msg, clean_subj, full_text, full_html = build_mime_email(
        deal_data=deal_data,
        ai_letter_text=ai_letter_text,
        ai_letter_html=ai_letter_html,
        custom_subject=custom_subject,
        valid_attachments=valid_attachments
    )
    
    msg_bytes = msg.as_bytes()
    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
        imap.login(SENDER_EMAIL, SENDER_PASS)
        # Определение системной папки Drafts (никогда не писать в 'Заготовки' или пользовательские папки!)
        drafts_folder = "Drafts"
        status, folder_list = imap.list()
        if status == 'OK':
            for f in folder_list:
                f_str = f.decode('utf-8', errors='replace')
                f_lower = f_str.lower()
                if "\\drafts" in f_lower or "inbox.drafts" in f_lower:
                    import re
                    m_f = re.search(r'"([^"]+)"$', f_str)
                    if m_f:
                        drafts_folder = m_f.group(1)
                    break

        imap.select(f'"{drafts_folder}"')

        # ZERO-DUPLICATE GUARD: Проверяем, нет ли уже черновика для этого получателя
        status, search_res = imap.search(None, f'(TO "{to_email}")')
        if status == 'OK' and search_res[0]:
            print(f"    [DUPLICATE GUARD] В папке '{drafts_folder}' уже найден существующий черновик для {to_email}. Пропуск создания дубля.")
            attached_names = [name for name, _ in valid_attachments]
            return msg["Message-ID"], attached_names, clean_subj

        imap.append(drafts_folder, "\\Draft", imaplib.Time2Internaldate(time.time()), msg_bytes)
                
    attached_names = [name for name, _ in valid_attachments]
    return msg["Message-ID"], attached_names, clean_subj


def send_followup_email_live(deal_data: dict, ai_letter_text: str, ai_letter_html: str, custom_subject: str = None, attach_kp: bool = True) -> tuple:
    """
    Отправляет follow-up письмо напрямую через SMTP клиенту с соблюдением всех правил:
    - Ответ в цепочке (In-Reply-To, References, цитирование переписки)
    - Осмысленная тема письма (Meaningful Subject Guard)
    - Прикрепление только валидных PDF вложений
    - Эталонная подпись Битрикс24
    - Аппаратный Self-Check перед отправкой
    - Сохранение копии в IMAP Sent
    """
    import smtplib
    valid_attachments = download_and_validate_pdf_attachments(deal_data) if attach_kp else []
    msg, clean_subj, full_text, full_html = build_mime_email(
        deal_data=deal_data,
        ai_letter_text=ai_letter_text,
        ai_letter_html=ai_letter_html,
        custom_subject=custom_subject,
        valid_attachments=valid_attachments
    )
    
    with smtplib.SMTP_SSL("mail.hostland.ru", 465, timeout=25) as server:
        server.login(SENDER_EMAIL, SENDER_PASS)
        server.send_message(msg)
        
    msg_bytes = msg.as_bytes()
    save_sent_email_to_imap(msg_bytes)
    
    attached_names = [name for name, _ in valid_attachments]
    return msg["Message-ID"], attached_names, clean_subj, full_html


def record_crm_followup_success(deal_id: int, to_email: str, subject: str, attached_names: list, summary_data: dict, assigned_by: int = 1):
    """
    Правило 10: Фиксирует успешную отправку follow-up письма в CRM:
    - Подробный аналитический комментарий в таймлайне (crm.timeline.comment.add);
    - Закрепление комментария в топе (crm.timeline.item.pin);
    - Постановка контрольного дела (TODO) на +4 дня (crm.activity.todo.add).
    КАТЕГОРИЧЕСКИ НЕ ВЫЗЫВАЕТ crm.activity.add с TYPE_ID: 4, чтобы исключить повторную отправку
    письма почтовым движком Битрикс24 от имени salman@longwang.ru!
    """
    summary = summary_data.get("summary", "").strip()
    recommendation = summary_data.get("recommendation", "").strip()
    should_close = summary_data.get("should_close", False)
    close_reason_text = summary_data.get("close_reason_text", "").strip()
    
    att_str = ", ".join(attached_names) if attached_names else "нет"
    parts = [
        "🤖 [ИИ-Анализ и Follow-up]",
        f"✉️ Отправлено письмо клиенту: {to_email}",
        f"📋 Тема: {subject}",
        f"📎 Прикрепленные файлы (PDF): {att_str}",
        f"📌 РЕЗЮМЕ ПО СДЕЛКЕ: {summary}",
        f"💡 РЕКОМЕНДАЦИЯ МЕНЕДЖЕРУ: {recommendation}"
    ]
    if should_close:
        parts.append("\n⚠️ РЕКОМЕНДАЦИЯ: ЗАКРЫТЬ СДЕЛКУ")
        if close_reason_text:
            parts.append(f'📋 Текст для копирования в карточку отказа:\n"{close_reason_text}"')
            
    full_comment = "\n".join(parts)
    
    try:
        res = call_b24("crm.timeline.comment.add", {
            "fields": {
                "ENTITY_ID": deal_id,
                "ENTITY_TYPE": "deal",
                "COMMENT": full_comment
            }
        })
        comment_id = res.get("ID") if isinstance(res, dict) else res
        if comment_id:
            call_b24("crm.timeline.item.pin", {
                "ownerTypeId": 2,
                "ownerId": deal_id,
                "id": int(comment_id)
            })
            print(f"    [PINNED COMMENT OK] Аналитический комментарий #{comment_id} закреплен вверху таймлайна сделки")
    except Exception as e:
        print(f"    [WARN] Не удалось закрепить комментарий: {e}")
        
    try:
        control_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d 12:00:00")
        call_b24("crm.activity.todo.add", {
            "ownerTypeId": 2,
            "ownerId": deal_id,
            "description": f"Контроль ответа на follow-up: {subject[:40]}",
            "deadline": control_date,
            "responsibleId": assigned_by
        })
        print(f"    [CRM TODO OK] Контрольное дело поставлено Артему на {control_date}")
    except Exception as e:
        print(f"    [WARN] Не удалось поставить CRM todo: {e}")


def post_and_pin_deal_summary_comment(deal_id: int, summary_data: dict) -> bool:
    """
    Правило 8: Добавляет в таймлайн сделки аналитическое резюме от ИИ,
    стратегический вердикт и закрепляет его вверху таймлайна.
    """
    summary = summary_data.get("summary", "").strip()
    recommendation = summary_data.get("recommendation", "").strip()
    should_close = summary_data.get("should_close", False)
    close_reason_text = summary_data.get("close_reason_text", "").strip()
    
    parts = [
        "🤖 [ИИ-Анализ и Follow-up]",
        f"📌 РЕЗЮМЕ ПО СДЕЛКЕ: {summary}",
        f"💡 РЕКОМЕНДАЦИЯ МЕНЕДЖЕРУ: {recommendation}"
    ]
    if should_close:
        parts.append("\n⚠️ РЕКОМЕНДАЦИЯ: ЗАКРЫТЬ СДЕЛКУ")
        if close_reason_text:
            parts.append(f'📋 Текст для копирования в карточку отказа:\n"{close_reason_text}"')
            
    full_comment = "\n".join(parts)
    
    res = call_b24("crm.timeline.comment.add", {
        "fields": {
            "ENTITY_ID": deal_id,
            "ENTITY_TYPE": "deal",
            "COMMENT": full_comment
        }
    })
    comment_id = res.get("ID") if isinstance(res, dict) else res
    if comment_id:
        try:
            call_b24("crm.timeline.item.pin", {
                "ownerTypeId": 2,
                "ownerId": deal_id,
                "id": int(comment_id)
            })
            return True
        except Exception as e:
            print(f"    [WARN] Не удалось закрепить комментарий #{comment_id}: {e}")
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Follow-up deals pipeline with strict charter & Self-Check Guard")
    parser.add_argument("--assigned-to", default="1", help="Ответственный пользователь (1 / artem)")
    parser.add_argument("--deal-id", type=int, help="Обработать одну конкретную сделку по ID")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Количество сделок")
    parser.add_argument("--cooldown", type=int, default=7, help="Кулдаун касаний в днях (по умолчанию 7)")
    parser.add_argument("--exclude-ids", help="Список ID сделок через запятую для исключения")
    parser.add_argument("--dossier-output", default="scratch/followup_dossier.json", help="Путь для сохранения досье")
    parser.add_argument("--export-dossier", action="store_true", help="Сформировать досье для ИИ-модели")
    parser.add_argument("--apply-letters", help="Путь к JSON-файлу с письмами от ИИ-модели для загрузки")
    parser.add_argument("--live", action="store_true", help="Боевой запуск (реальная отправка SMTP и фиксация в CRM)")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Режим проверки (сохранение черновиков в IMAP)")
    args = parser.parse_args()
    
    exclude_list = []
    if args.exclude_ids:
        exclude_list = [x.strip() for x in args.exclude_ids.split(",") if x.strip()]
        
    print("=================================================================")
    print(f" PIPELINE: FOLLOW-UP DEALS ({'БОЕВОЙ ЗАПУСК' if args.live else 'DRY-RUN / DRAFTS'})")
    print(f" Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Ответственный: {args.assigned_to}, Лимит: {args.limit}, Кулдаун: {args.cooldown} дней")
    if args.deal_id:
        print(f" Режим точечной обработки сделки ID: {args.deal_id}")
    if exclude_list:
        print(f" Исключенные ID: {', '.join(exclude_list)}")
    print("=================================================================")
    
    if args.apply_letters:
        dossier_path = args.dossier_output
        if not os.path.exists(dossier_path):
            print(f"[ERR] Досье {dossier_path} не найдено. Сначала запустите сбор досье без --apply-letters.")
            return
            
        with open(dossier_path, "r", encoding="utf-8") as f:
            dossier_data = json.load(f)
            
        with open(args.apply_letters, "r", encoding="utf-8") as f:
            letters_data = json.load(f)
            
        candidates = dossier_data.get("candidates", [])
        if args.deal_id:
            candidates = [c for c in candidates if int(c["deal_id"]) == args.deal_id]
            
        mode_desc = "БОЕВАЯ ОТПРАВКА КЛИЕНТАМ И CRM-МУТАЦИИ" if args.live else "СОХРАНЕНИЕ ЧЕРНОВИКОВ В IMAP"
        print(f"\n[Итерационный процессинг] Применение писем от ИИ-модели к {len(candidates)} сделкам [{mode_desc}]...\n")
        
        success_count = 0
        failed_count = 0
        for i, c in enumerate(candidates, 1):
            did = str(c["deal_id"])
            if did not in letters_data:
                print(f"  [WARN] Сделка #{did}: нет текста письма от модели в {args.apply_letters}, пропуск.")
                continue
                
            let = letters_data[did]
            to_email = c.get("to_email")
            title = c.get("title")
            contact = c.get("contact_name")
            print(f"\n>>> [Итерация {i}/{len(candidates)}] Сделка #{did} ({contact} | {to_email}): '{title}'")
            
            try:
                if args.live:
                    # БОЕВОЙ РЕЖИМ (SMTP + IMAP Sent + CRM Timeline & Todo)
                    msg_id, attached, sent_subj, sent_html = send_followup_email_live(
                        deal_data=c,
                        ai_letter_text=let["text"],
                        ai_letter_html=let["html"],
                        custom_subject=let.get("subject"),
                        attach_kp=True
                    )
                    print(f"    [SMTP OK] Письмо отправлено на {to_email} (Msg-ID: {msg_id})")
                    if attached:
                        print(f"    [ВЛОЖЕНИЯ PDF] {', '.join(attached)}")
                        
                    # Фиксация в CRM через комментарий и задачу без повторной отправки из Б24
                    summary_obj = {
                        "summary": let.get("summary", ""),
                        "recommendation": let.get("recommendation", ""),
                        "should_close": let.get("should_close", False),
                        "close_reason_text": let.get("close_reason_text", "")
                    }
                    record_crm_followup_success(
                        deal_id=int(did),
                        to_email=to_email,
                        subject=sent_subj,
                        attached_names=attached,
                        summary_data=summary_obj,
                        assigned_by=int(args.assigned_to)
                    )
                else:
                    # РЕЖИМ ЧЕРНОВИКОВ (DRY-RUN В IMAP)
                    msg_id, attached, sent_subj = create_followup_draft_in_imap(
                        deal_data=c,
                        ai_letter_text=let["text"],
                        ai_letter_html=let["html"],
                        custom_subject=let.get("subject"),
                        attach_kp=True
                    )
                    print(f"    [IMAP DRAFT OK] Черновик сохранен в IMAP Roundcube (Msg-ID: {msg_id})")
                    if attached:
                        print(f"    [ВЛОЖЕНИЯ PDF] {', '.join(attached)}")
                success_count += 1
            except SelfCheckError as sce:
                print(f"    [SELF-CHECK BLOCKED] Сделка #{did} заблокирована: {sce}")
                failed_count += 1
            except Exception as e:
                print(f"    [ERR] Ошибка обработки сделки #{did}: {e}")
                failed_count += 1
                
        print("\n================== ИТОГ ВЫПОЛНЕНИЯ ==================")
        print(f"Успешно обработано: {success_count} из {len(candidates)}")
        if failed_count > 0:
            print(f"Заблокировано / Ошибок: {failed_count}")
        return

    # Режим сбора досье
    candidates, excluded = collect_dossier_deals_without_activities(
        assigned_by=int(args.assigned_to),
        max_deals=args.limit,
        cooldown_days=args.cooldown,
        exclude_ids=exclude_list
    )
    
    if args.deal_id:
        candidates = [c for c in candidates if int(c["deal_id"]) == args.deal_id]
    
    os.makedirs(os.path.dirname(args.dossier_output) or ".", exist_ok=True)
    dossier_path = args.dossier_output
    with open(dossier_path, "w", encoding="utf-8") as f:
        json.dump({"candidates": candidates, "excluded": excluded}, f, ensure_ascii=False, indent=2)
        
    print(f"\n[2/3] Досье сохранено в {dossier_path}")
    print(f"- Отобрано сделок для анализа ИИ-моделью: {len(candidates)}")
    print(f"- Исключено: {len(excluded)}")
    
    for exc in excluded:
        print(f"  * Сделка #{exc['deal_id']} ('{exc['title']}'): {exc['reason']}")


if __name__ == "__main__":
    main()


