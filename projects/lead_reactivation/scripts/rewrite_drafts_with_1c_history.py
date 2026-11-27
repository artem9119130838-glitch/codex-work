import os
import sys
import json
import re
import time
import datetime
from loguru import logger
from sqlalchemy import text
from email.message import EmailMessage as PyEmailMessage
from imap_tools import MailBox

# Setup paths
sys.path.insert(0, '/app')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import (
    ClientIntel, OnecContact, OnecOwner, ClientReactivationHistory,
    ReactivationFunnelState, EmailMessage, EmailMatchResult
)
from app.services.llm_service import llm_service
from app.services.onec_events_service import OnecEventsService
from app.services.email_composer import (
    load_articles, find_best_article,
    clean_company_name, format_b2b_subject
)

TARGET_EMAILS = [
    "equipment@arzamas-hleb.ru",
    "info@abgroup16.ru",
    "prom.servis.2023@mail.ru",
    "info@alcryo.ru",
    "sale@forsalliance.ru",
    "koral2008@inbox.ru",
    "davidpekov777@gmail.com",
    "tekhservis.yug92@mail.ru",
    "hunshubun_80@mail.ru",
    "tuzom2@yandex.ru",
    "popovrodionrnd@yandex.ru"
]

SIGNATURE_HTML = """<div style="font-family: &quot;Times New Roman&quot;, Times, serif; font-size: 12pt; line-height: 1.2; margin: 0px; padding: 0px;"><br>
С уважением, Артем<br><a href="https://longwang.ru/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">LongWang</a> Тел <a href="tel:+78125091245" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">+7 (812) 509-1245</a><br><a href="mailto:sales@longwang.ru" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">sales@longwang.ru</a><br>------------------------------<br><i>Если Вам в дальнейшем понадобится что-то из оригинального оборудования Atlas Copco, SMC, Caterpillar, Danfoss, Siemens, Megger, Fronius, Brevini, Autonics и/или <a href="https://longwang.ru/supplies-services-china/brands/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">этих производителей</a>, то у нас и нашего китайского и сербского представительства заключены прямые договоры на поставку с ними и их дистрибьютерами. Также мы поставляем промышленное <a href="https://longwang.ru/supplies-services-china/equipment-from-china/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">оборудование из Китая и аналоги</a>. Также у нашей компании есть филиалы в Казахстане и Кыргызстане для <a href="https://longwang.ru/supplies-services-china/platezhi-v-kitai/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">проведения оплат</a> и организации <a href="https://longwang.ru/supplies-services-china/dostavka-is-kitaya/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">доставки</a>.</i>
</div>"""

def get_imap_credentials():
    user = os.environ.get("MAIL_ACCOUNT_2_USER") or settings.IMAP_USER or "sales@longwang.ru"
    password = os.environ.get("MAIL_ACCOUNT_2_PASS") or settings.IMAP_PASSWORD
    imap_host = os.environ.get("IMAP_SERVER") or settings.IMAP_HOST or "mail.hostland.ru"
    if not password:
        accounts_json = os.environ.get("MAIL_ACCOUNTS")
        if accounts_json:
            try:
                accs = json.loads(accounts_json.strip("'"))
                for a in accs:
                    if a.get("user") == "sales@longwang.ru":
                        user = a.get("user")
                        password = a.get("pass")
                        break
            except Exception:
                pass
    return user, password, imap_host

def extract_best_historical_quote(events: list[dict], email: str, client_name: str, company_name: str) -> tuple[str, str]:
    """
    Извлекает наиболее репрезентативное предыдущее сообщение из 1С:УНФ и формирует HTML-цитату <blockquote>
    Возвращает (quote_html, orig_msg_id)
    """
    if not events:
        return "", None

    # Фильтруем события: разделяем на входящие от клиента и наши исходящие
    client_incoming_events = []
    outbound_events = []

    for ev in events:
        content = (ev.get("content") or "").strip()
        subj = (ev.get("subject") or "").strip()
        if not content and not subj:
            continue
        
        # Пропускаем шаблонные новогодние рассылки
        if any(h in subj.lower() or h in content.lower() for h in ["с наступающим новым годом", "команда longwang llc поздравляет"]):
            continue

        first_line = content[:150].lower()
        is_our_letter = any(p in first_line for p in [
            "с уважением, артем", "с уважением, петров", "longwang", "лун-ван",
            "заказывать будем из китая", "спешим сообщить об открытии", "я проверяю качество работы"
        ])

        if not is_our_letter and len(content) > 10:
            client_incoming_events.append(ev)
        else:
            outbound_events.append(ev)

    # Приоритет: последнее входящее от клиента
    chosen_ev = None
    is_client = True
    if client_incoming_events:
        chosen_ev = client_incoming_events[-1]
    elif outbound_events:
        chosen_ev = outbound_events[-1]
        is_client = False
    else:
        chosen_ev = events[-1]

    raw_content = chosen_ev.get("content") or chosen_ev.get("subject") or ""
    # Очищаем подписи LongWang, если попали
    clean_content = re.sub(r'(?i)(?:с уважением, артем|longwang|лун-ван|тел\.\s*\+7|sales@longwang\.ru).*$', '', raw_content, flags=re.DOTALL).strip()
    
    # Очищаем длинные внутренние цепочки цитирования внутри старого письма
    clean_content = re.split(r'(?i)----------------\s*Кому:|(?:<br\s*/?>|\n)\s*(?:[0-9]{2}\.[0-9]{2}\.[0-9]{4}|[0-9]{1,2}\s+[а-яё]+\s+[0-9]{4}).*?написал\(а\):', clean_content)[0].strip()

    # Дата события
    raw_date = chosen_ev.get("date", "")
    try:
        dt = datetime.datetime.fromisoformat(str(raw_date).replace("Z", ""))
        date_str = dt.strftime("%d.%m.%Y, %H:%M")
    except Exception:
        date_str = str(raw_date)[:16]

    # Имя отправителя
    if is_client:
        sender_name = client_name or company_name or email
        sender_display = f"{sender_name} &lt;{email}&gt;"
    else:
        sender_display = "LongWang &lt;sales@longwang.ru&gt;"

    ref_key = chosen_ev.get("ref_key") or "1c_event"
    orig_msg_id = f"1c_event_{ref_key}@longwang.ru"

    # Формируем строки с префиксом '> '
    lines = [l.strip() for l in clean_content.split('\n') if l.strip()]
    quoted_lines = [f"&gt; {l}" for l in lines[:12]]
    if not quoted_lines:
        quoted_lines = [f"&gt; {chosen_ev.get('subject', 'Запрос оборудования')}"]

    quote_body = f"{date_str}, {sender_display} написал(а):<br>\n" + "<br>\n".join(quoted_lines)

    quote_html = f"""<br><br>
<blockquote type="cite" style="border-left: 2px solid #3b82f6; margin-left: 5px; padding-left: 10px; color: #475569; font-style: normal;">
{quote_body}
</blockquote>"""

    return quote_html, orig_msg_id

def create_raw_email(subject: str, body: str, recipient: str, user: str, quote_html: str = "", orig_msg_id: str = None) -> bytes:
    normalized = body.strip().replace('\r\n', '\n').replace('\r', '\n')
    normalized = re.sub(r'\n{3,}', '\n\n', normalized)
    paragraphs = normalized.split('\n\n')
    formatted_paragraphs = [p.strip().replace('\n', '<br>') for p in paragraphs if p.strip()]
    html_body = '<br><br>\n'.join(formatted_paragraphs)

    # Прикрепляем цитату переписки снизу
    if quote_html:
        html_body += f"\n{quote_html}"

    msg = PyEmailMessage()
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = recipient
    
    if orig_msg_id:
        clean_id = str(orig_msg_id).strip().strip('<>')
        msg['In-Reply-To'] = f"<{clean_id}>"
        msg['References'] = f"<{clean_id}>"

    msg.set_content(html_body, subtype='html')

    pdf_paths = [
        "/root/n8n_email_ai/presentation_and_reference.pdf",
        "/app/presentation_and_reference.pdf",
        "presentation_and_reference.pdf"
    ]
    for ppath in pdf_paths:
        if os.path.exists(ppath):
            try:
                with open(ppath, "rb") as f:
                    pdf_data = f.read()
                msg.add_attachment(
                    pdf_data,
                    maintype="application",
                    subtype="pdf",
                    filename="Презентация и референс-лист.pdf"
                )
                break
            except Exception as ex:
                logger.warning(f"Failed attaching PDF {ppath}: {ex}")

    return msg.as_bytes()

def replace_draft_in_imap_with_retries(user, password, imap_host, draft_folder, old_uid, subject, body_with_sig, email, quote_html="", orig_msg_id=None, max_retries=3):
    raw_bytes = create_raw_email(subject, body_with_sig, email, user, quote_html=quote_html, orig_msg_id=orig_msg_id)
    for attempt in range(1, max_retries + 1):
        try:
            with MailBox(imap_host).login(user, password) as mailbox:
                mailbox.folder.set(draft_folder)
                if old_uid:
                    logger.info(f"Deleting old draft UID {old_uid} for {email} (Attempt {attempt})...")
                    try:
                        mailbox.delete([old_uid])
                    except Exception as del_err:
                        logger.warning(f"Old draft delete notice: {del_err}")
                
                logger.info(f"Uploading new draft (with quote & threading) to IMAP {draft_folder} for {email}...")
                mailbox.append(raw_bytes, folder=draft_folder)
                logger.info(f"Successfully saved draft with quote for {email} to IMAP {draft_folder}")
                return True
        except Exception as e:
            logger.warning(f"IMAP save attempt {attempt} failed for {email}: {e}")
            time.sleep(3)
    return False

def main():
    logger.info("=== STARTING REWRITE OF 11 DRAFTS WITH 1C HISTORY QUOTES & THREADING ===")
    user, password, imap_host = get_imap_credentials()
    db = SessionLocal()
    events_svc = OnecEventsService(db)
    articles = load_articles()

    # 1. Fetch current drafts map
    drafts_by_email = {}
    draft_folder = "Drafts"
    try:
        with MailBox(imap_host).login(user, password) as mailbox:
            for f in mailbox.folder.list():
                if f.name.lower() in ["drafts", "inbox.drafts", "черновики", "inbox.черновики"]:
                    draft_folder = f.name
                    break
            mailbox.folder.set(draft_folder)
            msgs = list(mailbox.fetch(reverse=True, mark_seen=False))
            logger.info(f"Found {len(msgs)} total messages in IMAP {draft_folder}")
            for m in msgs:
                for to_addr in (m.to or []):
                    clean_to = to_addr.lower().strip()
                    if clean_to in TARGET_EMAILS:
                        drafts_by_email[clean_to] = {
                            "uid": m.uid,
                            "subject": m.subject,
                            "date": m.date
                        }
    except Exception as imap_init_err:
        logger.error(f"Failed initial IMAP scan: {imap_init_err}")

    logger.info(f"Target drafts mapped in IMAP: {len(drafts_by_email)} of {len(TARGET_EMAILS)}")
    results = []

    for email in TARGET_EMAILS:
        logger.info(f"\n========================================\nPROCESSING: {email}\n========================================")
        try:
            # Find 1C Contact and Owner info
            contact_1c = db.query(OnecContact).filter(text(":email = ANY(emails)")).params(email=email).first()
            company_name = ""
            contact_raw_name = ""
            if contact_1c:
                contact_raw_name = contact_1c.contact_name or ""
                if contact_1c.owner_ref_key:
                    owner = db.query(OnecOwner).filter(OnecOwner.owner_ref_key == contact_1c.owner_ref_key).first()
                    if owner:
                        company_name = owner.owner_name or ""

            # Fetch 1C events (already synced in previous run or loads from snapshot)
            events = events_svc.fetch_events_for_email(email)
            logger.info(f"Found {len(events)} 1C events for {email}")

            intel = db.query(ClientIntel).filter(ClientIntel.email == email).first()
            contact_summary_dict = {}
            company_summary_dict = {}
            if intel and intel.ai_summary:
                try:
                    parsed = json.loads(intel.ai_summary)
                    contact_summary_dict = parsed.get("contact_summary", {})
                    company_summary_dict = parsed.get("company_summary", {})
                except Exception:
                    pass

            extracted_name = contact_summary_dict.get("extracted_person_name") or ""
            if not extracted_name or extracted_name.lower() in ["клиент", "коллега", "менеджер", "не указано"]:
                extracted_name = contact_raw_name
            
            client_name = extracted_name.strip()
            if client_name and any(x in client_name.lower() for x in ["ооо", "ао", "зао", "ип", "хлеб", "инжиниринг"]):
                parts = client_name.split()
                if len(parts) >= 2 and all(p[0].isupper() for p in parts[:2]) and not any(p.upper() in ["ООО","АО","ЗАО","ИП"] for p in parts[:2]):
                    client_name = " ".join(parts[:2])
                else:
                    client_name = ""

            price_obj_text = None
            failed_reason = str(contact_summary_dict.get("reason_deal_failed", "")).lower()
            hist_notes = str(contact_summary_dict.get("interaction_history", "")).lower()
            if any(w in failed_reason or w in hist_notes for w in ["дорого", "цена космос", "высокая цена", "превысил бюджет", "по цене не прошли"]):
                price_obj_text = "предыдущее предложение превышало бюджет / высокая цена"

            skus_str = str(contact_summary_dict.get("skus_and_amounts") or "")
            best_art = find_best_article(articles, f"{skus_str} {hist_notes}")

            # Формируем цитату переписки из 1С
            quote_html, orig_msg_id = extract_best_historical_quote(events, email, client_name, company_name)
            logger.info(f"Built quote for {email} (Length: {len(quote_html)}, In-Reply-To: {orig_msg_id})")

            # Генерация текста письма
            if email == "equipment@arzamas-hleb.ru":
                subject = "КП по коллектору токосъемника Kubler и энкодерам"
                body = """Здравствуйте, Александр Алексеевич!

Ранее мы обсуждали поставку коллектора токосъемника Kubler и энкодеров ВЕС 260 360 для Арзамасского хлеба, но тогда по стоимости не сошлись.

Хотел уточнить — актуальна ли сейчас эта потребность? За последнее время мы оптимизировали логистику прямых поставок из Китая и Европы через наши филиалы, а также расширили базу проверенных производителей надежных промышленных аналогов (в том числе под строгие требования пищевых производств). Это позволяет предложить более гибкие и комфортные условия по цене и срокам.

Если вопрос с токосъемниками или другими комплектующими для линии еще открыт, направьте, пожалуйста, маркировки или требования — сделаем свежий расчет и предложим оптимальные варианты."""
            else:
                # Используем ранее сохраненный текст из истории (чтобы не жечь лимиты LLM без нужды)
                hist_record = db.query(ClientReactivationHistory).filter(
                    ClientReactivationHistory.client_email == email
                ).order_by(ClientReactivationHistory.sent_at.desc()).first()

                if hist_record and hist_record.body and len(hist_record.body.strip()) > 50:
                    logger.info(f"Reusing verified high-quality body from ClientReactivationHistory for {email}")
                    body = hist_record.body
                    subject = hist_record.subject
                else:
                    logger.info(f"Generating LLM draft for {email} with enriched 1C context...")
                    gen_body, gen_subj = llm_service.generate_reactivation_draft(
                        contact_summary=contact_summary_dict,
                        company_summary=company_summary_dict,
                        is_buyer=False,
                        article_title=best_art["title"],
                        article_url=best_art["url"],
                        article_desc=best_art["desc"],
                        style="case_sharing",
                        client_name=client_name or "Коллега",
                        company_name=company_name,
                        previous_email_context=hist_notes,
                        step_num=1,
                        force_provider=None,
                        has_sent_partnership_prelude=False,
                        price_objection_text=price_obj_text,
                        client_email=email
                    )
                    skus_text = str(contact_summary_dict.get("skus_and_amounts") or "")
                    subject = format_b2b_subject("", gen_subj, company_name, client_name or "Коллега", skus_text)
                    body = gen_body

            # Чистим подпись
            body = re.sub(r'(?i)<br\s*/?>\s*(?:с уважением|с наилучшими пожеланиями|искренне ваш|с уважением, менеджер по продажам|с уважением, Артем).*$', '', body, flags=re.DOTALL)
            body = re.sub(r'(?i)(?:с уважением|с наилучшими пожеланиями|искренне ваш|с уважением, менеджер по продажам|с уважением, Артем).*$', '', body, flags=re.DOTALL).strip()
            body_with_signature = body + "\n" + SIGNATURE_HTML

            # Сохранение в IMAP с заменой и цитатой
            old_info = drafts_by_email.get(email)
            old_uid = old_info["uid"] if old_info else None
            saved = replace_draft_in_imap_with_retries(
                user, password, imap_host, draft_folder,
                old_uid, subject, body_with_signature, email,
                quote_html=quote_html, orig_msg_id=orig_msg_id
            )

            if saved:
                logger.info(f"SUCCESS: Draft with quote saved for {email}")
                results.append({
                    "email": email,
                    "client_name": client_name or "Без имени",
                    "company": company_name or "—",
                    "subject": subject,
                    "has_quote": bool(quote_html),
                    "in_reply_to": orig_msg_id
                })
            else:
                logger.error(f"FAILED saving draft for {email}")

        except Exception as client_err:
            logger.error(f"Exception processing client {email}: {client_err}")
            db.rollback()

    db.close()
    
    # Save final report to JSON
    report_path = "/app/docs/REWRITE_DRAFTS_WITH_QUOTES_REPORT.json"
    try:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved rewrite report with quotes to {report_path} (Total processed: {len(results)})")
    except Exception as e:
        logger.warning(f"Could not save report file: {e}")

    logger.info("=== FINISHED REWRITING ALL DRAFTS WITH QUOTES ===")

if __name__ == "__main__":
    main()
