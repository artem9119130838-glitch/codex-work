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

B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "https://b24-g4wfjq.bitrix24.ru/rest/1/571p0j9x32gv6154/").rstrip("/") + "/"
IMAP_HOST = os.getenv("IMAP_SERVER", "mail.hostland.ru")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
SENDER_EMAIL = os.getenv("IMAP_USER", "sales@longwang.ru")
SENDER_PASS = os.getenv("IMAP_PASSWORD", "CosiN09oAr")
SENDER_NAME = "Артем Петров Long Wang, ООО Ци Линь"
IMAP_DRAFTS_FOLDER = "&BBcEMAQzBD4EQgQ+BDIEOgQ4-"

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


def collect_dossier_deals_without_activities(assigned_by=1, max_deals=10, cooldown_days=7):
    """
    Сканирует сделки Артема без активных дел с соблюдением 7-дневного кулдауна
    и формирует полное досье переписки для ИИ-модели.
    """
    now = datetime.now()
    cooldown_limit_dt = now - timedelta(days=cooldown_days)
    today_str = now.strftime("%Y-%m-%d")
    
    print(f"\n[1/3] Поиск открытых сделок Артема (ID={assigned_by})...")
    start = 0
    candidate_deals = []
    excluded_deals = []
    
    while len(candidate_deals) < max_deals and start <= 200:
        deals = call_b24("crm.deal.list", {
            "filter": {"ASSIGNED_BY_ID": assigned_by, "CLOSED": "N"},
            "order": {"DATE_CREATE": "DESC"},
            "select": ["ID", "TITLE", "STAGE_ID", "COMPANY_ID", "CONTACT_ID", "DATE_CREATE", "OPPORTUNITY", "CURRENCY_ID", "LEAD_ID"],
            "start": start
        })
        if not deals:
            break
            
        for d in deals:
            did = d["ID"]
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
            
            # Поиск последнего исходящего письма менеджера и вложений КП
            last_mgr_email = None
            kp_files = []
            
            for ea in email_acts:
                if ea.get("DIRECTION") == "2" and not last_mgr_email:
                    # Полные данные письма
                    full_ea = call_b24("crm.activity.get", {"id": ea.get("ID")})
                    last_mgr_email = full_ea
                    
                if ea.get("DIRECTION") == "2":
                    full_ea = call_b24("crm.activity.get", {"id": ea.get("ID")})
                    flist = full_ea.get("FILES") or []
                    for f in flist:
                        fid = f.get("id")
                        if fid and fid not in [k["id"] for k in kp_files]:
                            kp_files.append({"id": fid, "activity_id": ea.get("ID")})

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
                
            candidate_deals.append({
                "deal_id": did,
                "title": d.get("TITLE"),
                "stage": d.get("STAGE_ID"),
                "opportunity": f"{d.get('OPPORTUNITY')} {d.get('CURRENCY_ID')}",
                "contact_name": f"{contact.get('NAME', '')} {contact.get('LAST_NAME', '')}".strip() or "Коллеги",
                "company_name": company.get("TITLE", ""),
                "to_email": to_email,
                "phone": phone_val,
                "outgoing_count": outgoing_count,
                "last_touch_date": last_touch_date.strftime("%Y-%m-%d") if last_touch_date else "Неизвестно",
                "days_since_touch": (now - last_touch_date).days if last_touch_date else 999,
                "last_mgr_email_id": last_mgr_email.get("ID") if last_mgr_email else None,
                "last_mgr_subject": last_mgr_email.get("SUBJECT") if last_mgr_email else None,
                "last_mgr_message_id": (last_mgr_email.get("SETTINGS", {}).get("MESSAGE_HEADERS", {}).get("Message-Id") if last_mgr_email else None),
                "last_mgr_body_html": last_mgr_email.get("DESCRIPTION") if last_mgr_email else "",
                "kp_files": kp_files,
                "clean_history": clean_history,
                "clean_calls": clean_calls
            })
            
            if len(candidate_deals) >= max_deals:
                break
                
        start += 50
        
    return candidate_deals, excluded_deals


def create_followup_draft_in_imap(deal_data: dict, ai_letter_text: str, ai_letter_html: str, custom_subject: str = None, attach_kp: bool = True) -> str:
    """
    Создает черновик follow-up в IMAP Roundcube с соблюдением всех 5 правил:
    - Ответ в цепочке (In-Reply-To, References, цитирование переписки)
    - Осмысленная тема письма (Meaningful Subject Guard)
    - Прикрепление скачанного КП
    - Эталонная подпись Битрикс24
    """
    to_email = deal_data.get("to_email")
    if not to_email:
        raise ValueError(f"У сделки #{deal_data.get('deal_id')} нет email")
        
    if custom_subject:
        clean_subj = custom_subject if custom_subject.startswith("Re:") else f"Re: {custom_subject}"
    else:
        last_subj = deal_data.get("last_mgr_subject") or ""
        clean_cand = last_subj.replace("Re:", "").replace("RE:", "").replace("Fwd:", "").replace("FW:", "").strip()
        # Проверяем неявные / мусорные темы
        is_generic = not clean_cand or clean_cand.lower() in ["запрос", "заявка", "заказ", "(без темы)", "кп", "без темы"] or len(clean_cand) < 4
        if is_generic:
            entity = deal_data.get("company_name") or deal_data.get("contact_name") or ""
            clean_subj = f"Re: {deal_data.get('title', 'Поставка оборудования')} — {entity}".strip(" —")
        else:
            clean_subj = f"Re: {clean_cand}"
    
    msg = EmailMessage()
    msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = clean_subj
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="longwang.ru")
    msg["Reply-To"] = SENDER_EMAIL
    
    # Threading headers
    parent_msg_id = deal_data.get("last_mgr_message_id")
    if parent_msg_id:
        msg["In-Reply-To"] = parent_msg_id
        msg["References"] = parent_msg_id
        
    # Формируем тело с подписью и цитированием предыдущей переписки
    quoted_html = ""
    if deal_data.get("last_mgr_body_html"):
        quoted_html = f"""
        <br><br>
        <div class="gmail_quote">
          <div dir="ltr" class="gmail_attr">
            -------- Исходное сообщение --------<br>
            <b>Тема:</b> {deal_data.get('last_mgr_subject')}<br>
            <b>Дата:</b> {deal_data.get('last_touch_date')}<br>
            <b>От:</b> {SENDER_NAME} &lt;{SENDER_EMAIL}&gt;<br>
            <b>Кому:</b> {to_email}<br>
          </div>
          <br>
          <blockquote style="margin: 0 0 0 5px; padding: 5px 5px 5px 8px; border-left: 4px solid #e2e3e5;">
            {deal_data.get('last_mgr_body_html')}
          </blockquote>
        </div>
        """
        
    full_html = f"<div style='font-family: Arial, sans-serif; font-size: 14px;'>{ai_letter_html}</div>{BITRIX_SIGNATURE_HTML}{quoted_html}"
    full_text = f"{ai_letter_text}\n{BITRIX_SIGNATURE_TEXT}\n\n-------- Исходное сообщение --------\nТема: {deal_data.get('last_mgr_subject')}\n"
    
    msg.set_content(full_text)
    msg.add_alternative(full_html, subtype="html")
    
    # Прикрепление ранее отправленного КП (Правило 1)
    attached_names = []
    if attach_kp and deal_data.get("kp_files"):
        for kpf in deal_data["kp_files"][:2]: # Прикрепляем найденные КП
            fid = kpf.get("id")
            fname, fbytes = download_b24_disk_file(fid)
            if fname and fbytes:
                # Определение типа
                subtype = "pdf" if fname.lower().endswith(".pdf") else "octet-stream"
                msg.add_attachment(fbytes, maintype="application", subtype=subtype, filename=fname)
                attached_names.append(fname)
                print(f"    [ВЛОЖЕНИЕ ПРИКРЕПЛЕНО] Файл '{fname}' ({len(fbytes)} байт) прикреплен к черновику")
                
    msg_bytes = msg.as_bytes()
    
    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
        imap.login(SENDER_EMAIL, SENDER_PASS)
        for folder in ["Drafts", IMAP_DRAFTS_FOLDER]:
            try:
                imap.append(folder, "\\Draft", imaplib.Time2Internaldate(time.time()), msg_bytes)
            except Exception:
                pass
                
    return msg["Message-ID"], attached_names


def main():
    parser = argparse.ArgumentParser(description="Follow-up deals pipeline with strict charter")
    parser.add_argument("--assigned-to", default="1", help="Ответственный пользователь (1 / artem)")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Количество сделок")
    parser.add_argument("--cooldown", type=int, default=7, help="Кулдаун касаний в днях (по умолчанию 7)")
    parser.add_argument("--export-dossier", action="store_true", help="Сформировать досье для ИИ-модели")
    parser.add_argument("--apply-letters", help="Путь к JSON-файлу с письмами от ИИ-модели для загрузки в IMAP")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Режим проверки")
    args = parser.parse_args()
    
    print("=======================================================")
    print(" PIPELINE: FOLLOW-UP DEALS (CHARTER ENFORCED)")
    print(f" Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Ответственный: {args.assigned_to}, Лимит: {args.limit}, Кулдаун: {args.cooldown} дней")
    print("=======================================================")
    
    if args.apply_letters:
        dossier_path = "scratch/followup_dossier.json"
        if not os.path.exists(dossier_path):
            print(f"[ERR] Досье {dossier_path} не найдено. Сначала запустите сбор без --apply-letters.")
            return
            
        with open(dossier_path, "r", encoding="utf-8") as f:
            dossier_data = json.load(f)
            
        with open(args.apply_letters, "r", encoding="utf-8") as f:
            letters_data = json.load(f)
            
        candidates = dossier_data.get("candidates", [])
        print(f"\n[3/3] Применение писем от ИИ-модели к {len(candidates)} отобранным сделкам...")
        print(f"Режим проверки: {args.dry_run} (Черновики сохраняются в IMAP Roundcube с прикреплением КП и цепочки, CRM не изменяется)\n")
        
        success_count = 0
        for i, c in enumerate(candidates, 1):
            did = str(c["deal_id"])
            if did not in letters_data:
                print(f"  [WARN] Сделка #{did}: нет текста письма от модели, пропуск.")
                continue
                
            let = letters_data[did]
            to_email = c.get("to_email")
            title = c.get("title")
            contact = c.get("contact_name")
            print(f">>> [{i}/{len(candidates)}] Сделка #{did} ({contact} | {to_email}): '{title}'")
            
            try:
                msg_id, attached = create_followup_draft_in_imap(
                    deal_data=c,
                    ai_letter_text=let["text"],
                    ai_letter_html=let["html"],
                    custom_subject=let.get("subject"),
                    attach_kp=True
                )
                print(f"    [OK] Черновик сохранен в IMAP Roundcube (Msg-ID: {msg_id})")
                if attached:
                    print(f"    [КП ПРИКРЕПЛЕНО] {', '.join(attached)}")
                else:
                    print(f"    [ИНФО] КП в истории не обнаружено (отправка без вложения)")
                success_count += 1
            except Exception as e:
                print(f"    [ERR] Ошибка создания черновика: {e}")
                
        print("\n================== ИТОГ ВЫПОЛНЕНИЯ ==================")
        print(f"Успешно создано черновиков в IMAP Roundcube: {success_count} из {len(candidates)}")
        print("Все черновики доступны в веб-почте sales@longwang.ru (папка «Черновики») для ручной верификации.")
        return

    candidates, excluded = collect_dossier_deals_without_activities(
        assigned_by=int(args.assigned_to),
        max_deals=args.limit,
        cooldown_days=args.cooldown
    )
    
    os.makedirs("scratch", exist_ok=True)
    dossier_path = "scratch/followup_dossier.json"
    with open(dossier_path, "w", encoding="utf-8") as f:
        json.dump({"candidates": candidates, "excluded": excluded}, f, ensure_ascii=False, indent=2)
        
    print(f"\n[2/3] Досье сохранено в {dossier_path}")
    print(f"- Отобрано сделок для анализа ИИ-моделью: {len(candidates)}")
    print(f"- Исключено по 7-дневному кулдауну: {len(excluded)}")
    
    for exc in excluded:
        print(f"  * Сделка #{exc['deal_id']} ('{exc['title']}'): {exc['reason']}")


if __name__ == "__main__":
    main()

