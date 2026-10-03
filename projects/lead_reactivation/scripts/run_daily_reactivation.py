from dotenv import load_dotenv
load_dotenv()
import os
import sys
import datetime
import time
import json
import hashlib
from loguru import logger
from sqlalchemy import text, or_
import requests

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../1c_odata/scripts')))

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import ClientIntel, OnecContact, OnecOwner, ClientReactivationHistory, ReactivationFunnelState, EmailMessage
from app.services.llm_service import llm_service
from app.services.cooldown_guard import CooldownGuard
from scripts.test_pilot_reactivation import (
    extract_first_name, resolve_client_name, get_emails_text_for_contact, get_emails_text_for_company,
    load_articles, find_best_article, get_last_incoming_email_details, save_draft_to_imap,
    get_next_style_for_client, clean_company_name, format_b2b_subject
)

EMAIL_STYLES = {
    "vasin@tbs-semi.ru": "технический",
    "sakrupenko@s1.rosneft.ru": "деловой",
    "n.i.khliustina@sozvezdie.su": "дружелюбный",
    "tahautdinov@aksolit.com": "деловой",
    "info@almaz-snab.ru": "дружелюбный"
}

# Funnel steps configuration (Step number -> Cooldown in days before next step)
FUNNEL_STEPS = {
    1: 21,   # Step 1 -> Ждем 21 день (3 недели) перед Шагом 2
    2: 21,   # Step 2 -> Ждем 21 день перед Шагом 3
    3: 21,   # Step 3 -> Ждем 21 день перед Шагом 4
    4: 21,   # Step 4 -> Ждем 21 день перед Шагом 5
    5: 21,   # Step 5 -> Ждем 21 день перед Шагом 6
    6: 90    # Step 6 -> Завершение воронки, пауза 3 месяца (90 дней)
}

def check_if_prelude_sent(db, email: str) -> bool:
    # 1. Check history
    hist_records = db.query(ClientReactivationHistory).filter(
        ClientReactivationHistory.client_email == email
    ).all()
    for h in hist_records:
        if h.body and any(phrase in h.body.lower() for phrase in ["успешно работали", "ранее успешно работали", "ценим наше сотрудничество", "прошлое сотрудничество"]):
            return True
            
    # 2. Check actual sent emails to this domain or email in email_messages
    from app.db.models import EmailMessage, EmailMatchResult
    outgoing_emails = db.query(EmailMessage).join(
        EmailMatchResult, EmailMessage.message_id == EmailMatchResult.message_id
    ).filter(
        EmailMessage.raw_payload.op('->>')('is_sent') == 'true',
        EmailMatchResult.matched_email == email
    ).all()
    for msg in outgoing_emails:
        payload = msg.raw_payload or {}
        text_content = (payload.get("cleaned_text") or payload.get("text") or "").lower()
        if any(phrase in text_content for phrase in ["успешно работали", "ранее успешно работали", "ценим наше сотрудничество", "прошлое сотрудничество"]):
            return True
            
    return False

PRIORITY_1_EXPLICIT_URLS = {
    "https://longwang.ru/useful-articles/worlds-brend-equipment/",
    "https://longwang.ru/useful-articles/incorrect-import-calculation/"
}

def is_priority_1_article(url: str) -> bool:
    if not url:
        return False
    if "/projects/" in url:
        return True
    clean_url = url.rstrip('/') + '/'
    for target in PRIORITY_1_EXPLICIT_URLS:
        if clean_url == target.rstrip('/') + '/':
            return True
    return False

def select_relevant_non_repeating_article(db, email: str, articles: list, query_context: str = "") -> dict:
    """
    Выбирает релевантную статью/кейс из базы знаний по строгой двухэшелонной очереди:
    - Приоритет 1: Кейсы проектов (/projects/) и две целевые статьи:
      1) https://longwang.ru/useful-articles/worlds-brend-equipment/
      2) https://longwang.ru/useful-articles/incorrect-import-calculation/
    - Приоритет 2: Все остальные статьи базы знаний.
    Пока клиенту не отправлены все материалы из Приоритета 1 (по одному разу),
    материалы из Приоритета 2 отправлять строго запрещено!
    """
    # 1. Запрос всех когда-либо отправленных URL данному клиенту
    sent_records = db.query(ClientReactivationHistory.article_url).filter(
        ClientReactivationHistory.client_email == email
    ).all()
    sent_urls = {(r[0].rstrip('/') + '/') for r in sent_records if r[0]}
    
    # 2. Пул Приоритета 1
    p1_candidates = [art for art in articles if is_priority_1_article(art["url"]) and (art["url"].rstrip('/') + '/') not in sent_urls]
    
    if p1_candidates:
        logger.info(f"Выбор из Приоритета 1 (кейсы + 2 статьи): доступно {len(p1_candidates)} неотправленных для {email}.")
        if query_context:
            best = find_best_article(p1_candidates, query_context)
            logger.info(f"Подобрана статья/кейс Приоритета 1: '{best.get('title')}'")
            return best
        return p1_candidates[0]
        
    # 3. Пул Приоритета 2 (только если все материалы Приоритета 1 уже были отправлены)
    p2_candidates = [art for art in articles if not is_priority_1_article(art["url"]) and (art["url"].rstrip('/') + '/') not in sent_urls]
    
    if p2_candidates:
        logger.info(f"Все материалы Приоритета 1 уже отправлены {email}. Выбор из Приоритета 2: доступно {len(p2_candidates)} статей.")
        if query_context:
            best = find_best_article(p2_candidates, query_context)
            logger.info(f"Подобрана статья Приоритета 2: '{best.get('title')}'")
            return best
        return p2_candidates[0]
        
    logger.warning(f"Все материалы базы знаний уже отправлены {email}. Повторный выбор из полного пула по релевантности.")
    if query_context:
        return find_best_article(articles, query_context)
    return articles[0]

def build_client_query_context(intel: ClientIntel, contact_emails_text: str = "", company_emails_text: str = "") -> str:
    """
    Формирует расширенную строку контекста для точного поиска релевантной статьи в базе знаний.
    """
    parts = []
    if intel:
        if intel.company_name:
            parts.append(str(intel.company_name))
        if intel.skus_and_amounts:
            parts.append(str(intel.skus_and_amounts))
        if intel.ai_summary:
            parts.append(str(intel.ai_summary))
    if contact_emails_text and contact_emails_text != "Нет истории переписки по email.":
        parts.append(contact_emails_text[:500])
    if company_emails_text and company_emails_text != "Нет истории переписки по компании.":
        parts.append(company_emails_text[:500])
    return " ".join(parts)

def check_client_reactivation_eligibility(db, email: str, contact_1c=None, owner_1c=None, intel=None) -> tuple[bool, str]:
    """
    4-ступенчатый Pre-Flight Filter исключения неактуальных/активных клиентов:
    1. Проверка входящих писем за последние 30 дней в email_messages (клиент активен).
    2. Проверка открытых сделок в CRM Битрикс24 (STAGE_SEMANTIC == 'process').
    3. Проверка отказов по цене / претензий в истории переписки и ai_summary (кулдаун 60 дней).
    4. Проверка маркера отписки / bounce.
    """
    now = datetime.datetime.utcnow()
    clean_email = email.strip().lower()

    # 1. Входящие письма за последние 30 дней
    cutoff_30d = now - datetime.timedelta(days=30)
    try:
        from app.db.models import EmailMessage
        recent_msg = db.query(EmailMessage).filter(
            EmailMessage.from_email == clean_email,
            EmailMessage.received_at >= cutoff_30d,
            or_(EmailMessage.is_junk == False, EmailMessage.is_junk == None)
        ).order_by(EmailMessage.received_at.desc()).first()
        if recent_msg:
            return False, f"Клиент присылал входящее письмо {recent_msg.received_at.strftime('%Y-%m-%d')} (контакт активен, реанимация запрещена)"
    except Exception as e_msg:
        logger.warning(f"Ошибка проверки входящих писем: {e_msg}")

    # 2. Проверка открытых сделок в Битрикс24
    b24_webhook = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
    if b24_webhook and b24_webhook != "/":
        try:
            r_ct = requests.post(f"{b24_webhook}crm.contact.list", json={"filter": {"EMAIL": clean_email}, "select": ["ID", "COMPANY_ID"]}, timeout=10)
            ct_list = r_ct.json().get("result", []) if r_ct.status_code == 200 else []
            ct_ids = [c["ID"] for c in ct_list]
            comp_ids = [c["COMPANY_ID"] for c in ct_list if c.get("COMPANY_ID")]

            for cid in ct_ids:
                r_deals = requests.post(f"{b24_webhook}crm.deal.list", json={
                    "filter": {"CONTACT_ID": cid, "STAGE_SEMANTIC": "process"},
                    "select": ["ID", "TITLE", "STAGE_ID"]
                }, timeout=10)
                deals = r_deals.json().get("result", []) if r_deals.status_code == 200 else []
                if deals:
                    return False, f"В Битрикс24 есть активная сделка #{deals[0]['ID']} '{deals[0]['TITLE']}' в стадии '{deals[0]['STAGE_ID']}'"

            for comp_id in comp_ids:
                r_deals = requests.post(f"{b24_webhook}crm.deal.list", json={
                    "filter": {"COMPANY_ID": comp_id, "STAGE_SEMANTIC": "process"},
                    "select": ["ID", "TITLE", "STAGE_ID"]
                }, timeout=10)
                deals = r_deals.json().get("result", []) if r_deals.status_code == 200 else []
                if deals:
                    return False, f"В Битрикс24 есть активная сделка Компании #{comp_id}: сделка #{deals[0]['ID']} '{deals[0]['TITLE']}'"
        except Exception as e_b24:
            logger.warning(f"Ошибка проверки сделок в Битрикс24: {e_b24}")

    # 3. Проверка отказов по цене и претензий в ai_summary / timeline (кулдаун 60 дней)
    if intel and intel.ai_summary:
        summary_lower = str(intel.ai_summary).lower()
        if any(term in summary_lower for term in ["дорого", "отказ по цене", "ушли к конкурентам", "претензия", "штраф", "суд", "не пишите"]):
            updated_at = intel.updated_at.replace(tzinfo=None) if intel.updated_at and hasattr(intel.updated_at, 'tzinfo') and intel.updated_at.tzinfo else (intel.updated_at or now)
            if (now - updated_at).days < 60:
                return False, f"Зафиксирован отказ по цене / претензия / просьба не писать ({updated_at.strftime('%Y-%m-%d')}). Кулдаун 60 дней."

    return True, "OK"


def process_single_client_funnel_step(db, email, step_num, cand, contact_1c, owner_ref_key, style, client_name, is_buyer, company_name, best_art, force_provider=None):
    """
    Helper to generate a draft for a specific step of the funnel and save it.
    """
    contact_emails_text = get_emails_text_for_contact(db, contact_1c.contact_ref_key, email)
    company_emails_text = get_emails_text_for_company(db, owner_ref_key) if owner_ref_key else ""
    
    if not contact_emails_text:
        contact_emails_text = "Нет истории переписки по email."
    if not company_emails_text:
        company_emails_text = "Нет истории переписки по компании."
        
    # Fetch previous draft body from history to write a different one
    last_history = db.query(ClientReactivationHistory).filter(
        ClientReactivationHistory.client_email == email
    ).order_by(ClientReactivationHistory.sent_at.desc()).first()
    
    # Cooldown Guard check (email, drafts, recent correspondence)
    can_send, cd_reason = CooldownGuard.can_send_reactivation(db, email, owner_ref_key=owner_ref_key, days=21, check_company=False)
    if not can_send:
        logger.warning(f"КАТЕГОРИЧЕСКИ: Отказ генерации для {email} (Шаг {step_num}): {cd_reason}. Отмена.")
        return False

    # 4-ступенчатый Pre-Flight Filter (входящие письма, сделки Б24, отказ по цене)
    eligible, elig_reason = check_client_reactivation_eligibility(db, email, contact_1c=contact_1c, owner_1c=None, intel=cand)
    if not eligible:
        logger.warning(f"ОТКЛОНЕНО (Pre-Flight Filter): {email} (Шаг {step_num}): {elig_reason}. Отмена генерации.")
        return False
            
    previous_email_context = last_history.body if last_history else None
    
    # Auto update summary if missing or outdated
    intel = db.query(ClientIntel).filter(ClientIntel.email == email).first()
    contact_summary_dict = None
    company_summary_dict = None
    has_new_emails = False
    
    if intel and intel.updated_at:
        max_rec = db.execute(text("""
            SELECT MAX(m.received_at)
            FROM email_messages m
            JOIN email_match_results r ON m.message_id = r.message_id
            WHERE r.contact_ref_key = :ref_key OR r.owner_ref_key = :owner_key
        """), {"ref_key": contact_1c.contact_ref_key, "owner_key": owner_ref_key}).scalar()
        
        if max_rec:
            max_rec_naive = max_rec.replace(tzinfo=None) if max_rec.tzinfo else max_rec
            if max_rec_naive > intel.updated_at.replace(tzinfo=None):
                has_new_emails = True
                logger.info(f"New emails detected since last summary update. Cache invalidated.")
                
    if intel and intel.ai_summary and not has_new_emails:
        try:
            cached_data = json.loads(intel.ai_summary)
            contact_summary_dict = cached_data.get("contact_summary")
            company_summary_dict = cached_data.get("company_summary")
        except Exception as ex:
            logger.warning(f"Cached summary is plain text: {ex}. Using it as fallback.")
            contact_summary_dict = {"history_and_notes": intel.ai_summary}
            company_summary_dict = {"history_and_notes": "Нет истории компании (заглушка)."}
            
    if not contact_summary_dict or not company_summary_dict:
        logger.info(f"Generating summary profile using forced Gemini key-rotation...")
        summaries = llm_service.generate_client_intelligence_summary(
            contact_emails_text=contact_emails_text,
            company_emails_text=company_emails_text,
            is_buyer=is_buyer,
            client_name=client_name,
            force_provider="gemini"
        )
        contact_summary_dict = summaries.get("contact_summary", {})
        company_summary_dict = summaries.get("company_summary", {})
        
        if not intel:
            intel = ClientIntel(email=email)
            db.add(intel)
            
        intel.company_name = company_name
        intel.ai_summary = json.dumps({
            "contact_summary": contact_summary_dict,
            "company_summary": company_summary_dict
        }, ensure_ascii=False)
        intel.timeline = contact_summary_dict.get("timeline") or []
        intel.skus_and_amounts = contact_summary_dict.get("skus_and_amounts") or []
        intel.last_managers = contact_summary_dict.get("last_managers") or []
        intel.client_type = contact_summary_dict.get("client_type")
        intel.next_action_recommendation = contact_summary_dict.get("next_action_recommendation")
        intel.updated_at = datetime.datetime.utcnow()
        db.commit()

    # Сквозная проверка и обогащение СБИС (Saby) + DaData в 3 системы: DWH, CRM Битрикс24, 1С:УНФ
    inn = intel.inn if intel and intel.inn else None
    if not inn and owner_1c and hasattr(owner_1c, 'raw_payload') and owner_1c.raw_payload:
        inn = owner_1c.raw_payload.get("ИНН")

    sbis_profile = company_summary_dict.get("sbis_profile") if company_summary_dict else None
    if not sbis_profile and inn:
        try:
            from check_contractor import verify_and_enrich_contractor
            clean_inn = "".join(filter(str.isdigit, str(inn)))
            if clean_inn:
                logger.info(f"[СБИС-ИНТЕЛ] Запуск верификации контрагента ИНН {clean_inn} для {email}...")
                sbis_result = verify_and_enrich_contractor(
                    inn=clean_inn,
                    one_c_guid=str(owner_ref_key) if owner_ref_key else None,
                    email=email,
                    dry_run=False
                )
                if sbis_result and "classification" in sbis_result:
                    company_summary_dict["sbis_profile"] = sbis_result
                    if intel:
                        try:
                            cached_summary = json.loads(intel.ai_summary) if intel.ai_summary else {}
                        except Exception:
                            cached_summary = {}
                        cached_summary["company_summary"] = company_summary_dict
                        intel.ai_summary = json.dumps(cached_summary, ensure_ascii=False)
                        db.commit()
                    logger.info(f"[СБИС-ИНТЕЛ OK] Досье обновлено в DWH/Б24/1С: {sbis_result['classification'].get('verdict')} (выручка: {sbis_result['classification'].get('revenue_formatted')})")
        except Exception as e_sbis:
            logger.warning(f"Не удалось выполнить скоринг СБИС для {email} (ИНН {inn}): {e_sbis}")

    # Confident client name resolution
    if not client_name or client_name == "Коллега":
        client_name = resolve_client_name(contact_1c.contact_name, contact_summary_dict, contact_emails_text, email=email)
        
    # Check if we already sent the partnership prelude previously
    has_sent_partnership_prelude = check_if_prelude_sent(db, email)

    # Generate reactivation draft via llm (both Gemini first, then DeepSeek fallback)
    body, llm_subj = llm_service.generate_reactivation_draft(
        contact_summary=contact_summary_dict,
        company_summary=company_summary_dict,
        is_buyer=is_buyer,
        article_title=best_art["title"],
        article_url=best_art["url"],
        article_desc=best_art["desc"],
        style=style,
        client_name=client_name,
        company_name=company_name,
        previous_email_context=previous_email_context,
        step_num=step_num,
        force_provider=force_provider,
        has_sent_partnership_prelude=has_sent_partnership_prelude
    )
    
    # Clean double signatures
    import re
    body = re.sub(r'(?i)<br\s*/?>\s*(?:с уважением|с наилучшими пожеланиями|искренне ваш|с уважением, менеджер по продажам|с уважением, Артем).*$', '', body, flags=re.DOTALL)
    body = re.sub(r'(?i)(?:с уважением|с наилучшими пожеланиями|искренне ваш|с уважением, менеджер по продажам|с уважением, Артем).*$', '', body, flags=re.DOTALL).strip()
    
    signature_html = """<div style="font-family: &quot;Times New Roman&quot;, Times, serif; font-size: 12pt; line-height: 1.2; margin: 0px; padding: 0px;"><br>
С уважением, Артем<br><a href="https://longwang.ru/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">LongWang</a> Тел <a href="tel:+78125091245" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">+7 (812) 509-1245</a><br><a href="mailto:sales@longwang.ru" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">sales@longwang.ru</a><br>------------------------------<br><i>Если Вам в дальнейшем понадобится что-то из оригинального оборудования Atlas Copco, SMC, Caterpillar, Danfoss, Siemens, Megger, Fronius, Brevini, Autonics и/или <a href="https://longwang.ru/supplies-services-china/brands/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">этих производителей</a>, то у нас и нашего китайского и сербского представительства заключены прямые договоры на поставку с ними и их дистрибьютерами. Также мы поставляем промышленное <a href="https://longwang.ru/supplies-services-china/equipment-from-china/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">оборудование из Китая и аналоги</a>. Также у нашей компании есть филиалы в Казахстане и Кыргызстане для <a href="https://longwang.ru/supplies-services-china/platezhi-v-kitai/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">проведения оплат</a> и организации <a href="https://longwang.ru/supplies-services-china/dostavka-is-kitaya/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">доставки</a>.</i>
</div>"""
    
    body_with_signature = body + signature_html
    clean_subj, quote_text = get_last_incoming_email_details(db, contact_1c.contact_ref_key, email)
    skus_text = str(contact_summary_dict.get("skus_and_amounts") or "")
    subject = format_b2b_subject(clean_subj, llm_subj, company_name, client_name, skus_text)
    
    # Save draft to IMAP
    saved_to_imap = save_draft_to_imap(subject, body_with_signature, email, quote_text=quote_text)
    if saved_to_imap:
        logger.info(f"Successfully saved draft for {email} (Step {step_num}) to IMAP!")
        
        # Log to history table
        hist = ClientReactivationHistory(
            client_email=email,
            article_url=best_art["url"],
            sent_at=datetime.datetime.utcnow(),
            template_used=f"{style}_step_{step_num}",
            subject=subject,
            body=body
        )
        db.add(hist)
        db.commit()
        return True
    else:
        logger.error(f"Failed saving draft for {email} to IMAP.")
        return False


def run_daily_reactivation(new_limit: int = 10, old_limit: int = 10, cooldown_days: int = 30, inactivity_months: int = 1, force_run: bool = False):
    """
    Двухпоточный ежедневный процесс коммуникации с клиентами 1С:
    1. По выходным дням письма НЕ отправляются (суббота=5, воскресенье=6).
    2. ПОТОК 1 (Повторные касания/Реактивация):
       - Клиенты из 1С/БД, у которых последнее касание было > 30 дней назад.
       - Повторный проход строго не ранее чем через 30 дней (cooldown_days = 30).
       - Квота: old_limit (по умолчанию 10 писем).
    3. ПОТОК 2 (Первичный охват базы 1С):
       - Контакты из onec_contacts, которым модель ЕЩЕ НИ РАЗУ НЕ ПИСАЛА.
       - Квота: new_limit (по умолчанию 10 писем).
       - Работает день за днем до тех пор, пока у ВСЕХ контактов 1С не будет хотя бы 1 касания.
    """
    from app.services.hr_guard import HRGuard
    from app.services.cooldown_guard import CooldownGuard, PUBLIC_EMAIL_DOMAINS

    # Гарантированная загрузка учетных данных IMAP
    if not os.environ.get("MAIL_ACCOUNT_2_USER"):
        os.environ["MAIL_ACCOUNT_2_USER"] = "sales@longwang.ru"
    if not os.environ.get("MAIL_ACCOUNT_2_PASS"):
        os.environ["MAIL_ACCOUNT_2_PASS"] = "CosiN09oAr"
    if not os.environ.get("IMAP_SERVER"):
        os.environ["IMAP_SERVER"] = "mail.hostland.ru"

    now = datetime.datetime.utcnow()
    # 1. Проверка на выходные дни
    if now.weekday() in (5, 6) and not force_run:
        logger.info(f"Сегодня выходной день (день недели: {now.weekday()}). По регламенту письма по выходным не отправляются. Выход.")
        return

    db = SessionLocal()
    old_drafts_created = 0
    new_drafts_created = 0

    try:
        logger.info(f"Запуск двухпоточной коммуникации: new_limit={new_limit}, old_limit={old_limit}, cooldown={cooldown_days}d...")
        articles = load_articles()
        selected_domains = set()
        selected_owner_keys = set()

        # =====================================================================
        # ПОТОК 1: ПОВТОРНЫЕ КАСАНИЯ (ПОСЛЕДНЕЕ КАСАНИЕ > 30 ДНЕЙ НАЗАД)
        # =====================================================================
        cooldown_threshold = now - datetime.timedelta(days=cooldown_days)
        logger.info(f"--- [ПОТОК 1] Поиск контактов с последним касанием до {cooldown_threshold.strftime('%Y-%m-%d')} (лимит: {old_limit}) ---")

        old_candidates_rows = db.execute(text("""
            SELECT h.client_email, MAX(h.sent_at) as last_sent, COUNT(h.id) as touches
            FROM client_reactivation_history h
            LEFT JOIN reactivation_funnel_states fs ON h.client_email = fs.client_email
            WHERE (fs.step_status IS NULL OR fs.step_status != 'replied')
              AND h.client_email NOT LIKE '%@longwang.ru'
              AND h.client_email NOT LIKE '%@доставкакитай.рф'
            GROUP BY h.client_email
            HAVING MAX(h.sent_at) <= :cooldown_threshold
            ORDER BY MAX(h.sent_at) ASC;
        """), {"cooldown_threshold": cooldown_threshold}).fetchall()

        logger.info(f"Найдено {len(old_candidates_rows)} кандидатов на повторное касание (> {cooldown_days} дней).")

        for row in old_candidates_rows:
            if old_drafts_created >= old_limit:
                break

            email = row[0].strip().lower()
            domain = email.split('@')[-1]
            if domain and domain not in PUBLIC_EMAIL_DOMAINS and domain in selected_domains:
                continue

            contact_1c = db.query(OnecContact).filter(text(":email = ANY(emails)")).params(email=email).first()
            if not contact_1c:
                continue

            is_hr, hr_reason = HRGuard.is_job_seeker(email=email, contact_name=contact_1c.contact_name)
            if is_hr:
                logger.info(f"Пропуск HR/соискателя {email}: {hr_reason}")
                continue

            owner_ref_key = contact_1c.owner_ref_key
            if owner_ref_key and owner_ref_key in selected_owner_keys:
                continue

            owner_1c = db.query(OnecOwner).filter(OnecOwner.owner_ref_key == owner_ref_key).first() if owner_ref_key else None
            is_buyer = bool(owner_1c.owner_is_buyer) if owner_1c else False
            company_name = owner_1c.owner_name if owner_1c else "Неизвестная компания"
            client_name = resolve_client_name(contact_1c.contact_name, None, "")
            style = get_next_style_for_client(db, email)

            # Определяем номер шага
            fs = db.query(ReactivationFunnelState).filter(ReactivationFunnelState.client_email == email).first()
            current_step = fs.current_step if fs and fs.current_step else int(row[2])
            next_step = current_step + 1 if current_step < 6 else 1

            intel_profile = db.query(ClientIntel).filter(ClientIntel.email == email).first()
            query_ctx = build_client_query_context(intel_profile, "", "")
            best_art = select_relevant_non_repeating_article(db, email, articles, query_ctx)

            logger.info(f"[ПОТОК 1] Создание черновика (Шаг {next_step}) для старого контакта: {email} ({company_name})...")
            success = process_single_client_funnel_step(
                db=db, email=email, step_num=next_step, cand=intel_profile,
                contact_1c=contact_1c, owner_ref_key=owner_ref_key,
                style=style, client_name=client_name, is_buyer=is_buyer,
                company_name=company_name, best_art=best_art
            )

            if success:
                old_drafts_created += 1
                if domain and domain not in PUBLIC_EMAIL_DOMAINS:
                    selected_domains.add(domain)
                if owner_ref_key:
                    selected_owner_keys.add(owner_ref_key)

                if fs:
                    fs.current_step = next_step
                    fs.step_status = "draft_created"
                    fs.updated_at = datetime.datetime.utcnow()
                else:
                    fs = ReactivationFunnelState(
                        client_email=email,
                        current_step=next_step,
                        step_status="draft_created",
                        last_action_at=None,
                        created_at=datetime.datetime.utcnow(),
                        updated_at=datetime.datetime.utcnow()
                    )
                    db.add(fs)
                db.commit()
                time.sleep(3.0)

        # =====================================================================
        # ПОТОК 2: ПЕРВИЧНЫЙ ОХВАТ БАЗЫ 1С (КОМУ ЕЩЕ НИ РАЗУ НЕ ПИСАЛИ)
        # =====================================================================
        logger.info(f"--- [ПОТОК 2] Поиск контактов из 1С без единого касания (лимит: {new_limit}) ---")

        new_candidates_rows = db.execute(text("""
            SELECT c.contact_ref_key, c.owner_ref_key, c.contact_name, email
            FROM onec_contacts c, unnest(c.emails) as email
            WHERE c.emails IS NOT NULL
              AND array_length(c.emails, 1) > 0
              AND c.contact_is_junk = false
              AND email NOT LIKE '%@longwang.ru'
              AND email NOT LIKE '%@доставкакитай.рф'
              AND email LIKE '%@%.%'
              AND NOT EXISTS (
                  SELECT 1 FROM client_reactivation_history h
                  WHERE LOWER(h.client_email) = LOWER(email)
              )
              AND NOT EXISTS (
                  SELECT 1 FROM reactivation_funnel_states fs
                  WHERE LOWER(fs.client_email) = LOWER(email)
              )
            ORDER BY c.fetched_at DESC;
        """)).fetchall()

        uncontacted_total = len(new_candidates_rows)
        logger.info(f"Всего контактов 1С, ожидающих первого касания: {uncontacted_total}")

        for row in new_candidates_rows:
            if new_drafts_created >= new_limit:
                break

            contact_ref_key = row[0]
            owner_ref_key = row[1]
            raw_contact_name = row[2]
            email = row[3].strip().lower()

            domain = email.split('@')[-1]
            if domain and domain not in PUBLIC_EMAIL_DOMAINS and domain in selected_domains:
                continue

            if owner_ref_key and owner_ref_key in selected_owner_keys:
                continue

            is_hr, hr_reason = HRGuard.is_job_seeker(email=email, contact_name=raw_contact_name)
            if is_hr:
                continue

            contact_1c = db.query(OnecContact).filter(OnecContact.contact_ref_key == contact_ref_key).first()
            if not contact_1c:
                continue

            owner_1c = db.query(OnecOwner).filter(OnecOwner.owner_ref_key == owner_ref_key).first() if owner_ref_key else None
            is_buyer = bool(owner_1c.owner_is_buyer) if owner_1c else False
            company_name = owner_1c.owner_name if owner_1c else "Неизвестная компания"
            client_name = resolve_client_name(contact_1c.contact_name, None, "")
            style = get_next_style_for_client(db, email)

            intel = db.query(ClientIntel).filter(ClientIntel.email == email).first()
            query_ctx = build_client_query_context(intel, "", "")
            best_art = select_relevant_non_repeating_article(db, email, articles, query_ctx)

            logger.info(f"[ПОТОК 2] Создание черновика (Шаг 1) для НОВОГО контакта 1С: {email} ({company_name})...")
            success = process_single_client_funnel_step(
                db=db, email=email, step_num=1, cand=intel,
                contact_1c=contact_1c, owner_ref_key=owner_ref_key,
                style=style, client_name=client_name, is_buyer=is_buyer,
                company_name=company_name, best_art=best_art
            )

            if success:
                new_drafts_created += 1
                if domain and domain not in PUBLIC_EMAIL_DOMAINS:
                    selected_domains.add(domain)
                if owner_ref_key:
                    selected_owner_keys.add(owner_ref_key)

                fs = ReactivationFunnelState(
                    client_email=email,
                    current_step=1,
                    step_status="draft_created",
                    last_action_at=None,
                    created_at=datetime.datetime.utcnow(),
                    updated_at=datetime.datetime.utcnow()
                )
                db.add(fs)
                db.commit()
                time.sleep(3.0)

        remaining_uncontacted = uncontacted_total - new_drafts_created
        logger.info(
            f"Итоги запуска: Создано черновиков для повторных касаний: {old_drafts_created}/{old_limit}. "
            f"Создано черновиков для новых контактов 1С: {new_drafts_created}/{new_limit}. "
            f"Осталось контактов 1С без первого касания: {remaining_uncontacted}."
        )

    except Exception as e:
        logger.error(f"Ошибка при выполнении ежедневной коммуникации: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Запуск ежедневной двухпоточной коммуникации с клиентами 1С.")
    parser.add_argument("--new-limit", type=int, default=10, help="Квота черновиков новым контактам 1С (по умолчанию: 10)")
    parser.add_argument("--old-limit", type=int, default=10, help="Квота повторных касаний контактам >30 дней (по умолчанию: 10)")
    parser.add_argument("--cooldown-days", type=int, default=30, help="Минимальный кулдаун между повторными касаниями (по умолчанию: 30 дней)")
    parser.add_argument("--force-run", action="store_true", help="Принудительный запуск даже в выходной день (для тестов)")
    args = parser.parse_args()

    try:
        os.makedirs("logs", exist_ok=True)
        logger.add("logs/run_daily_reactivation_{time}.log", rotation="1 day")
    except Exception as e_log:
        logger.warning(f"Could not initialize file log sink: {e_log}")

    run_daily_reactivation(
        new_limit=args.new_limit,
        old_limit=args.old_limit,
        cooldown_days=args.cooldown_days,
        force_run=args.force_run
    )
