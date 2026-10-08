import os
import sys
import datetime
import time
import json
import hashlib
from loguru import logger
from sqlalchemy import text, or_

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

def check_client_reactivation_eligibility(db, email: str, contact_1c=None, owner_1c=None, intel=None) -> tuple[bool, str, dict]:
    """
    Интеллектуальный фильтр исключения неактуальных/активных клиентов (Intent Classification Gate):
    1. Входящие письма за последние 30 дней в email_messages (клиент активен).
    2. Анализ текста ПОСЛЕДНЕГО входящего письма от контакта/домена (Intent Gate):
       - Маркеры активного заказа / доставки / счета / договора -> блокировать воронку (ручная обработка менеджером).
       - Маркеры отписки / покупки у конкурентов / просьбы не писать -> закрыть воронку (completed).
       - Маркеры ценового возражения ("цена космос", "дорого") -> передать для отработки возражения в LLM.
    3. Открытые сделки в CRM Битрикс24 (STAGE_SEMANTIC == 'process').
    4. Отказ по цене или претензия в ai_summary (кулдаун 60 дней).
    """
    import datetime
    import re
    now = datetime.datetime.utcnow()
    clean_email = email.strip().lower()
    intent_info = {"intent": "ok", "detail": "", "price_objection_text": None}

    # 1. Анализ текста ПОСЛЕДНЕГО входящего письма от контакта (Intent Gate)
    cutoff_30d = now - datetime.timedelta(days=30)
    try:
        last_incoming = db.query(EmailMessage).filter(
            EmailMessage.from_email == clean_email,
            or_(
                EmailMessage.raw_payload.op('->>')('is_sent') == None,
                EmailMessage.raw_payload.op('->>')('is_sent') == 'false'
            ),
            or_(EmailMessage.is_junk == False, EmailMessage.is_junk == None)
        ).order_by(EmailMessage.received_at.desc()).first()

        if last_incoming:
            payload = last_incoming.raw_payload or {}
            inc_text = (payload.get("cleaned_text") or payload.get("text") or payload.get("snippet") or "").lower()

            # А) Маркеры активного заказа / доставки / счета / договора (абсолютный приоритет)
            order_patterns = [
                r"отправ(?:ьте|ляйте|ить)", r"доставк", r"делов(?:ые|ыми)\s+лини", r"сдэк", r"пэк",
                r"адрес\s*(?:доставки)?\s*[:—]", r"грузополучател", r"получател\w*\s*[:—]",
                r"выставите\s+счет", r"счет\s+на\s+оплат", r"договор", r"реквизит",
                r"платежк", r"оплатил", r"прошу\s+выставить"
            ]
            for pat in order_patterns:
                m = re.search(pat, inc_text)
                if m:
                    match_word = m.group(0)
                    intent_info["intent"] = "order_active"
                    intent_info["detail"] = f"Маркер заказа/доставки '{match_word}' в письме от {last_incoming.received_at.strftime('%Y-%m-%d') if last_incoming.received_at else ''}"
                    return False, f"[INTENT GATE BLOCKED] Последнее входящее содержит данные заказа/доставки/счета ('{match_word}'). Требуется ручная обработка менеджером, а не авто-реанимация!", intent_info

            # Б) Маркеры жесткого отказа / отписки / покупки у других
            reject_patterns = [
                r"не\s+пишите", r"отпишите", r"удалите\s+(?:из|свою)\s+рассылк",
                r"купили\s+у\s+друг", r"уже\s+приобрели", r"больше\s+не\s+требуется", r"не\s+актуально"
            ]
            for pat in reject_patterns:
                m = re.search(pat, inc_text)
                if m:
                    match_word = m.group(0)
                    intent_info["intent"] = "rejected"
                    intent_info["detail"] = f"Отказ/покупка у конкурентов '{match_word}'"
                    return False, f"[INTENT GATE REJECTED] Клиент сообщил об отказе/покупке у других ('{match_word}'). Воронка закрывается.", intent_info

            # В) Маркеры ценового возражения ("цена космос", "слишком дорого")
            price_patterns = [
                r"цена\s+космос", r"слишком\s+дорого", r"дорого", r"не\s+проходим\s+по\s+бюджет",
                r"высокая\s+цена", r"цены\s+завышен"
            ]
            for pat in price_patterns:
                m = re.search(pat, inc_text)
                if m:
                    intent_info["intent"] = "price_objection"
                    intent_info["price_objection_text"] = "предыдущее предложение превышало бюджет (высокая цена / цена космос)"
                    logger.info(f"[INTENT GATE] Для {clean_email} обнаружено ценовое возражение: '{m.group(0)}'. Включается сценарий отработки возражения!")
                    break

            # Г) Проверка недавней активности (< 30 дней)
            if last_incoming.received_at:
                rec_naive = last_incoming.received_at.replace(tzinfo=None) if last_incoming.received_at.tzinfo else last_incoming.received_at
                if rec_naive >= cutoff_30d:
                    intent_info["detail"] = f"Входящее письмо {last_incoming.received_at.strftime('%Y-%m-%d')}"
                    if intent_info.get("intent") == "ok":
                        intent_info["intent"] = "active_recent"
                    return False, f"Клиент присылал входящее письмо {last_incoming.received_at.strftime('%Y-%m-%d')} (контакт активен, авто-реанимация запрещена)", intent_info

    except Exception as e_intent:
        logger.warning(f"Ошибка проверки Intent Gate для {clean_email}: {e_intent}")

    # 3. Проверка открытых сделок, лидов и недавних касаний (активностей) в CRM Битрикс24
    raw_b24 = getattr(settings, "BITRIX24_WEBHOOK_URL", None) or os.getenv("BITRIX24_WEBHOOK_URL", "")
    b24_webhook = raw_b24.rstrip("/") + "/" if raw_b24 else ""
    if b24_webhook and b24_webhook != "/":
        try:
            import requests
            cutoff_b24_act = (now - datetime.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")

            # 3.1. Контакты
            r_ct = requests.post(f"{b24_webhook}crm.contact.list", json={"filter": {"EMAIL": clean_email}, "select": ["ID", "COMPANY_ID"]}, timeout=10)
            ct_list = r_ct.json().get("result", []) if r_ct.status_code == 200 else []
            ct_ids = [c["ID"] for c in ct_list]
            comp_ids = [c["COMPANY_ID"] for c in ct_list if c.get("COMPANY_ID")]

            # 3.2. Компании по email напрямую
            r_cmp = requests.post(f"{b24_webhook}crm.company.list", json={"filter": {"EMAIL": clean_email}, "select": ["ID"]}, timeout=10)
            if r_cmp.status_code == 200:
                for c in r_cmp.json().get("result", []):
                    if c.get("ID") and c["ID"] not in comp_ids:
                        comp_ids.append(c["ID"])

            # 3.3. Лиды по email
            r_lead = requests.post(f"{b24_webhook}crm.lead.list", json={"filter": {"EMAIL": clean_email}, "select": ["ID", "TITLE", "STATUS_ID", "STATUS_SEMANTIC"]}, timeout=10)
            lead_list = r_lead.json().get("result", []) if r_lead.status_code == 200 else []
            lead_ids = []
            for ld in lead_list:
                lead_ids.append(ld["ID"])
                if ld.get("STATUS_SEMANTIC") == "process":
                    intent_info["intent"] = "b24_lead_active"
                    return False, f"В Битрикс24 есть активный Лид #{ld['ID']} '{ld.get('TITLE')}' в стадии '{ld.get('STATUS_ID')}'", intent_info

            # 3.4. Активные сделки по контактам
            for cid in ct_ids:
                r_deals = requests.post(f"{b24_webhook}crm.deal.list", json={
                    "filter": {"CONTACT_ID": cid, "STAGE_SEMANTIC": "process"},
                    "select": ["ID", "TITLE", "STAGE_ID"]
                }, timeout=10)
                deals = r_deals.json().get("result", []) if r_deals.status_code == 200 else []
                if deals:
                    intent_info["intent"] = "b24_deal_active"
                    return False, f"В Битрикс24 есть активная сделка #{deals[0]['ID']} '{deals[0]['TITLE']}' в стадии '{deals[0]['STAGE_ID']}'", intent_info

            # 3.5. Активные сделки по компаниям
            for comp_id in comp_ids:
                r_deals = requests.post(f"{b24_webhook}crm.deal.list", json={
                    "filter": {"COMPANY_ID": comp_id, "STAGE_SEMANTIC": "process"},
                    "select": ["ID", "TITLE", "STAGE_ID"]
                }, timeout=10)
                deals = r_deals.json().get("result", []) if r_deals.status_code == 200 else []
                if deals:
                    intent_info["intent"] = "b24_deal_active"
                    return False, f"В Битрикс24 есть активная сделка Компании #{comp_id}: сделка #{deals[0]['ID']} '{deals[0]['TITLE']}'", intent_info

            # 3.6. Недавние касания и активности менеджера (< 30 дней)
            for cid in ct_ids:
                r_act = requests.post(f"{b24_webhook}crm.activity.list", json={
                    "filter": {"OWNER_TYPE_ID": 3, "OWNER_ID": cid, ">=START_TIME": cutoff_b24_act},
                    "select": ["ID", "SUBJECT", "START_TIME", "TYPE_ID"]
                }, timeout=10)
                acts = r_act.json().get("result", []) if r_act.status_code == 200 else []
                if acts:
                    intent_info["intent"] = "b24_activity_active"
                    return False, f"В Битрикс24 есть недавняя активность Контакта #{cid}: #{acts[0]['ID']} '{acts[0].get('SUBJECT')}' от {acts[0].get('START_TIME', '')[:10]}", intent_info

            for comp_id in comp_ids:
                r_act = requests.post(f"{b24_webhook}crm.activity.list", json={
                    "filter": {"OWNER_TYPE_ID": 4, "OWNER_ID": comp_id, ">=START_TIME": cutoff_b24_act},
                    "select": ["ID", "SUBJECT", "START_TIME", "TYPE_ID"]
                }, timeout=10)
                acts = r_act.json().get("result", []) if r_act.status_code == 200 else []
                if acts:
                    intent_info["intent"] = "b24_activity_active"
                    return False, f"В Битрикс24 есть недавняя активность Компании #{comp_id}: #{acts[0]['ID']} '{acts[0].get('SUBJECT')}' от {acts[0].get('START_TIME', '')[:10]}", intent_info

            for lid in lead_ids:
                r_act = requests.post(f"{b24_webhook}crm.activity.list", json={
                    "filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lid, ">=START_TIME": cutoff_b24_act},
                    "select": ["ID", "SUBJECT", "START_TIME", "TYPE_ID"]
                }, timeout=10)
                acts = r_act.json().get("result", []) if r_act.status_code == 200 else []
                if acts:
                    intent_info["intent"] = "b24_activity_active"
                    return False, f"В Битрикс24 есть недавняя активность Лида #{lid}: #{acts[0]['ID']} '{acts[0].get('SUBJECT')}' от {acts[0].get('START_TIME', '')[:10]}", intent_info

        except Exception as e_b24:
            logger.warning(f"Ошибка проверки сделок, лидов и активностей в Битрикс24: {e_b24}")

    # 4. Проверка отказов по цене в ai_summary (кулдаун 60 дней)
    if intel and intel.ai_summary:
        summary_lower = str(intel.ai_summary).lower()
        if any(term in summary_lower for term in ["дорого", "отказ по цене", "цена космос"]):
            intent_info["intent"] = "price_objection"
            intent_info["price_objection_text"] = "предыдущее предложение превышало бюджет"

    return True, "OK", intent_info

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

    # Intent Classification Gate
    eligible, elig_reason, intent_info = check_client_reactivation_eligibility(db, email, contact_1c=contact_1c, owner_1c=None, intel=cand)
    if not eligible:
        logger.warning(f"ОТКЛОНЕНО (Intent Gate): {email} (Шаг {step_num}): {elig_reason}. Отмена генерации.")
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
        logger.info(f"Generating summary profile using LLM cascade...")
        summaries = llm_service.generate_client_intelligence_summary(
            contact_emails_text=contact_emails_text,
            company_emails_text=company_emails_text,
            is_buyer=is_buyer,
            client_name=client_name,
            force_provider=None
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

    # Confident client name resolution
    if not client_name or client_name == "Коллега":
        client_name = resolve_client_name(contact_1c.contact_name, contact_summary_dict, contact_emails_text)
        
    # Check if we already sent the partnership prelude previously
    has_sent_partnership_prelude = check_if_prelude_sent(db, email)

    # Price objection context from intent_info or contact summary
    price_obj_text = intent_info.get("price_objection_text")
    if not price_obj_text and contact_summary_dict:
        failed_reason = str(contact_summary_dict.get("reason_deal_failed", "")).lower()
        hist_notes = str(contact_summary_dict.get("interaction_history", "")).lower()
        if any(w in failed_reason or w in hist_notes for w in ["дорого", "цена космос", "высокая цена", "превысил бюджет"]):
            price_obj_text = "предыдущее предложение превышало бюджет / высокая цена"

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
        has_sent_partnership_prelude=has_sent_partnership_prelude,
        price_objection_text=price_obj_text
    )
    
    # Clean double signatures
    import re
    body = re.sub(r'(?i)<br\s*/?>\s*(?:с уважением|с наилучшими пожеланиями|искренне ваш|с уважением, менеджер по продажам|с уважением, Артем).*$', '', body, flags=re.DOTALL)
    body = re.sub(r'(?i)(?:с уважением|с наилучшими пожеланиями|искренне ваш|с уважением, менеджер по продажам|с уважением, Артем).*$', '', body, flags=re.DOTALL).strip()
    
    signature_html = """<div style="font-family: &quot;Times New Roman&quot;, Times, serif; font-size: 12pt; line-height: 1.2; margin: 0px; padding: 0px;"><br>
С уважением, Артем<br><a href="https://longwang.ru/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">LongWang</a> Тел <a href="tel:+78125091245" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">+7 (812) 509-1245</a><br><a href="mailto:sales@longwang.ru" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">sales@longwang.ru</a><br>------------------------------<br><i>Если Вам в дальнейшем понадобится что-то из оригинального оборудования Atlas Copco, SMC, Caterpillar, Danfoss, Siemens, Megger, Fronius, Brevini, Autonics и/или <a href="https://longwang.ru/supplies-services-china/brands/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">этих производителей</a>, то у нас и нашего китайского и сербского представительства заключены прямые договоры на поставку с ними и их дистрибьютерами. Также мы поставляем промышленное <a href="https://longwang.ru/supplies-services-china/equipment-from-china/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">оборудование из Китая и аналоги</a>. Также у нашей компании есть филиалы в Казахстане и Кыргызстане для <a href="https://longwang.ru/supplies-services-china/platezhi-v-kitai/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">проведения оплат</a> и организации <a href="https://longwang.ru/supplies-services-china/dostavka-is-kitaya/" style="text-decoration: underline; color: blue;" target="_blank" tabindex="-1">доставки</a>.</i>
</div>"""
    
    body_with_signature = body + signature_html
    clean_subj, quote_text, orig_msg_id = get_last_incoming_email_details(db, contact_1c.contact_ref_key, email)
    skus_text = str(contact_summary_dict.get("skus_and_amounts") or "")
    subject = format_b2b_subject(clean_subj, llm_subj, company_name, client_name, skus_text)
    
    # Save draft to IMAP with RFC threading headers
    saved_to_imap = save_draft_to_imap(subject, body_with_signature, email, quote_text=quote_text, in_reply_to=orig_msg_id)
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


def run_daily_reactivation(limit: int = 3, active_limit: int = 3, cooldown_days: int = 60, inactivity_months: int = 3, cold_limit: int = 3, max_daily_drafts: int = 6):
    """
    Ежедневный процесс реанимации клиентов:
    1. Ведение активных воронок по шагам 2-6 (с проверкой отправок и ответов, лимит active_limit).
    2. Запуск новых клиентов по стандарту (Шаг 1, лимит limit).
    3. Жесткий суточный лимит черновиков (max_daily_drafts): суммарно не более max_daily_drafts в день.
    4. Защита от писем соискателям (HRGuard).
    5. Защита от дублей в одну компанию за один день.
    """
    from app.services.hr_guard import HRGuard
    from app.services.cooldown_guard import PUBLIC_EMAIL_DOMAINS

    db = SessionLocal()
    drafts_created_today = 0
    try:
        now = datetime.datetime.utcnow()
        logger.info(f"Starting daily reactivation pipeline (max_daily_drafts={max_daily_drafts}, active_limit={active_limit}, new_limit={limit}, cold_limit={cold_limit}, cooldown={cooldown_days}d, inactivity={inactivity_months}m)...")
        
        articles = load_articles()
        
        # =====================================================================
        # ЧАСТЬ 1: ОБРАБОТКА АКТИВНЫХ ВОРОНОК (ШАГИ 2-6)
        # =====================================================================
        active_funnels = db.query(ReactivationFunnelState).filter(
            ReactivationFunnelState.step_status.in_(["draft_created", "sent"])
        ).all()
        
        logger.info(f"Активных воронок в процессе: {len(active_funnels)}")
        
        for fs in active_funnels:
            if drafts_created_today >= active_limit or drafts_created_today >= max_daily_drafts:
                logger.info(f"Достигнут лимит черновиков для активных воронок ({active_limit}/{max_daily_drafts}). Переход к новым клиентам 1С.")
                break

            email = fs.client_email
            
            # Поиск контакта в 1С
            contact_1c = db.query(OnecContact).filter(text(":email = ANY(emails)")).params(email=email).first()
            if not contact_1c:
                continue
                
            # Проверка HRGuard
            is_hr, hr_reason = HRGuard.is_job_seeker(email=email, contact_name=contact_1c.contact_name)
            if is_hr:
                logger.warning(f"Контакт {email} определен как соискатель/HR ({hr_reason}). Воронка закрывается.")
                fs.step_status = "completed"
                fs.updated_at = datetime.datetime.utcnow()
                db.commit()
                continue

            owner_ref_key = contact_1c.owner_ref_key
            owner_1c = db.query(OnecOwner).filter(OnecOwner.owner_ref_key == owner_ref_key).first() if owner_ref_key else None
            is_buyer = bool(owner_1c.owner_is_buyer) if owner_1c else False
            company_name = owner_1c.owner_name if owner_1c else "Неизвестная компания"
            client_name = extract_first_name(contact_1c.contact_name)
            style = get_next_style_for_client(db, email)
            
            # Шаг A: Проверка отправки черновика менеджером
            if fs.step_status == "draft_created":
                out_msg = db.query(EmailMessage).filter(
                    EmailMessage.from_email == email,
                    EmailMessage.raw_payload.op('->>')('is_sent') == 'true',
                    EmailMessage.received_at >= fs.updated_at - datetime.timedelta(minutes=5)
                ).order_by(EmailMessage.received_at.desc()).first()
                
                if not out_msg:
                    raw_out = db.execute(text("""
                        SELECT MAX(m.received_at)
                        FROM email_messages m
                        JOIN email_match_results r ON m.message_id = r.message_id
                        WHERE (r.contact_ref_key = :ref_key OR r.owner_ref_key = :owner_key)
                          AND m.raw_payload->>'is_sent' = 'true'
                          AND m.received_at >= :updated_at - INTERVAL '5 minutes'
                    """), {
                        "ref_key": contact_1c.contact_ref_key,
                        "owner_key": owner_ref_key,
                        "updated_at": fs.updated_at
                    }).scalar()
                    if raw_out:
                        fs.step_status = "sent"
                        fs.last_action_at = raw_out
                        db.commit()
                        logger.info(f"Detected sent email to {email} for Step {fs.current_step}. Transitioning status to 'sent'.")
                else:
                    fs.step_status = "sent"
                    fs.last_action_at = out_msg.received_at
                    db.commit()
                    logger.info(f"Detected sent email to {email} for Step {fs.current_step}. Transitioning status to 'sent'.")
                    
            # Шаг B: Проверка ответа клиента (входящее письмо в IMAP)
            if fs.step_status == "sent":
                in_msg = db.query(EmailMessage).filter(
                    EmailMessage.from_email == email,
                    or_(
                        EmailMessage.raw_payload.op('->>')('is_sent') == None,
                        EmailMessage.raw_payload.op('->>')('is_sent') == 'false'
                    ),
                    EmailMessage.received_at > fs.last_action_at
                ).first()
                
                if in_msg:
                    fs.step_status = "replied"
                    fs.updated_at = datetime.datetime.utcnow()
                    db.commit()
                    logger.info(f"Detected incoming reply from {email}. Funnel stopped with status 'replied'.")
                    continue
                    
                # Шаг C: Проверка истечения кулдауна до следующего шага
                last_action_naive = fs.last_action_at.replace(tzinfo=None) if fs.last_action_at.tzinfo else fs.last_action_at
                days_passed = (now - last_action_naive).days
                cooldown_needed = FUNNEL_STEPS.get(fs.current_step, 2)
                
                if days_passed >= cooldown_needed:
                    if fs.current_step >= 6:
                        fs.step_status = "completed"
                        fs.updated_at = datetime.datetime.utcnow()
                        db.commit()
                        logger.info(f"Funnel completed for client {email} at Step 6. Cooldown {cooldown_days} days activated.")
                    else:
                        next_step = fs.current_step + 1
                        logger.info(f"Cooldown expired ({days_passed} days passed >= {cooldown_needed}d). Generating Step {next_step} for {email}...")
                        
                        intel_profile = db.query(ClientIntel).filter(ClientIntel.email == email).first()
                        query_ctx = build_client_query_context(intel_profile, "", "")
                        # Intent Gate: проверяем статус перед переходом к следующему шагу
                        eligible, elig_reason, intent_info = check_client_reactivation_eligibility(db, email, contact_1c=contact_1c, owner_1c=owner_1c, intel=None)
                        if not eligible:
                            if intent_info.get("intent") == "order_active":
                                logger.warning(f"[INTENT GATE] Воронка {email} остановлена: {elig_reason}. Статус переведен в 'manual_order_pending'.")
                                fs.step_status = "manual_order_pending"
                                fs.updated_at = datetime.datetime.utcnow()
                                db.commit()
                                continue
                            elif intent_info.get("intent") == "rejected":
                                logger.warning(f"[INTENT GATE] Воронка {email} остановлена: {elig_reason}. Статус переведен в 'completed'.")
                                fs.step_status = "completed"
                                fs.updated_at = datetime.datetime.utcnow()
                                db.commit()
                                continue
                            else:
                                logger.warning(f"[INTENT GATE] Воронка {email} пропущена: {elig_reason}")
                                continue

                        best_art = select_relevant_non_repeating_article(db, email, articles, query_ctx)

                        success = process_single_client_funnel_step(
                            db=db, email=email, step_num=next_step, cand=None,
                            contact_1c=contact_1c, owner_ref_key=owner_ref_key,
                            style=style, client_name=client_name, is_buyer=is_buyer,
                            company_name=company_name, best_art=best_art
                        )
                        if success:
                            drafts_created_today += 1
                            fs.current_step = next_step
                            fs.step_status = "draft_created"
                            fs.updated_at = datetime.datetime.utcnow()
                            db.commit()
                            time.sleep(5.0)

        # =====================================================================
        # ЧАСТЬ 2: СТАРТ НОВЫХ КЛИЕНТОВ ПО СТАНДАРТУ (ШАГ 1)
        # =====================================================================
        remaining_slots = max_daily_drafts - drafts_created_today
        effective_new_limit = min(limit, remaining_slots)
        if effective_new_limit <= 0:
            logger.info(f"Суточный лимит черновиков ({max_daily_drafts}) уже полностью исчерпан на активных воронках (создано {drafts_created_today}). Запуск новых клиентов отложен на следующий день.")
            return

        cooldown_threshold = now - datetime.timedelta(days=cooldown_days)
        inactivity_threshold = now - datetime.timedelta(days=inactivity_months * 30)
        
        # Исключения по истории реанимации (< 60 дней)
        recently_reactivated = db.query(ClientReactivationHistory.client_email).filter(
            ClientReactivationHistory.sent_at >= cooldown_threshold
        ).all()
        exclude_emails = {r[0] for r in recently_reactivated if r[0]}
        
        # Исключения по активным воронкам или завершенным < 60 дней назад
        active_funnels_emails = db.query(ReactivationFunnelState).filter(
            or_(
                ReactivationFunnelState.step_status.in_(["draft_created", "sent"]),
                ReactivationFunnelState.last_action_at >= cooldown_threshold,
                ReactivationFunnelState.updated_at >= cooldown_threshold
            )
        ).all()
        for r in active_funnels_emails:
            if r.client_email:
                exclude_emails.add(r.client_email)
                
        # Выборка кандидатов
        warm_candidates = db.query(ClientIntel).filter(or_(ClientIntel.client_type != 'cold_lead', ClientIntel.client_type == None)).order_by(ClientIntel.updated_at.desc()).all()
        cold_candidates = db.query(ClientIntel).filter(ClientIntel.client_type == 'cold_lead').order_by(ClientIntel.updated_at.desc()).all()
        new_candidates = []
        
        # Защита от дубликатов компаний и доменов внутри одной выборки
        selected_owner_keys = set()
        selected_domains = set()

        # 1. Сбор теплых кандидатов
        for cand in warm_candidates:
            if len(new_candidates) >= effective_new_limit:
                break
                
            email = cand.email
            if not email or email in exclude_emails:
                continue
                
            contact_1c = db.query(OnecContact).filter(text(":email = ANY(emails)")).params(email=email).first()
            if not contact_1c:
                continue
                
            # Проверка HRGuard
            is_hr, hr_reason = HRGuard.is_job_seeker(email=email, contact_name=contact_1c.contact_name)
            if is_hr:
                logger.info(f"Skipping job seeker / HR candidate {email}: {hr_reason}")
                continue

            owner_ref_key = contact_1c.owner_ref_key
            if owner_ref_key and owner_ref_key in selected_owner_keys:
                continue

            domain = email.split('@')[-1].lower().strip()
            if domain and domain not in PUBLIC_EMAIL_DOMAINS and domain in selected_domains:
                continue

            max_received = db.execute(text("""
                SELECT MAX(m.received_at)
                FROM email_messages m
                JOIN email_match_results r ON m.message_id = r.message_id
                WHERE r.contact_ref_key = :ref_key OR r.owner_ref_key = :owner_key
            """), {"ref_key": contact_1c.contact_ref_key, "owner_key": owner_ref_key}).scalar()
            
            raw_max = db.execute(text("""
                SELECT MAX(received_at)
                FROM email_messages
                WHERE from_email = :email
            """), {"email": email}).scalar()
            
            last_contact_date = None
            if max_received and raw_max:
                last_contact_date = max(max_received, raw_max)
            elif max_received:
                last_contact_date = max_received
            elif raw_max:
                last_contact_date = raw_max
                
            if last_contact_date:
                last_contact_naive = last_contact_date.replace(tzinfo=None) if last_contact_date.tzinfo else last_contact_date
                if last_contact_naive > inactivity_threshold:
                    continue
            
            # Cooldown Guard check (email, drafts, recent correspondence, company cooldown)
            can_send, reason = CooldownGuard.can_send_reactivation(db, email, owner_ref_key=owner_ref_key, days=cooldown_days, check_company=True)
            if not can_send:
                logger.info(f"Skipping warm candidate {email}: {reason}")
                continue

            new_candidates.append({
                "cand": cand,
                "contact_1c": contact_1c,
                "owner_ref_key": owner_ref_key,
                "max_received": max_received
            })
            if owner_ref_key:
                selected_owner_keys.add(owner_ref_key)
            if domain and domain not in PUBLIC_EMAIL_DOMAINS:
                selected_domains.add(domain)
            
        # 2. Сбор холодных кандидатов (если слоты еще остались)
        cold_selected = 0
        for cand in cold_candidates:
            if len(new_candidates) >= effective_new_limit or cold_selected >= cold_limit:
                break
                
            email = cand.email
            if not email or email in exclude_emails:
                continue
                
            contact_1c = db.query(OnecContact).filter(text(":email = ANY(emails)")).params(email=email).first()
            if not contact_1c:
                continue
                
            # Проверка HRGuard
            is_hr, hr_reason = HRGuard.is_job_seeker(email=email, contact_name=contact_1c.contact_name)
            if is_hr:
                logger.info(f"Skipping job seeker / HR cold candidate {email}: {hr_reason}")
                continue

            owner_ref_key = contact_1c.owner_ref_key
            if owner_ref_key and owner_ref_key in selected_owner_keys:
                continue

            domain = email.split('@')[-1].lower().strip()
            if domain and domain not in PUBLIC_EMAIL_DOMAINS and domain in selected_domains:
                continue

            owner_1c = db.query(OnecOwner).filter(OnecOwner.owner_ref_key == owner_ref_key).first() if owner_ref_key else None
            
            # Check 1C creation date (> 90 days ago / inactivity threshold)
            c_date = None
            if contact_1c.raw_payload:
                d_val = contact_1c.raw_payload.get("ДатаСоздания")
                if d_val and not str(d_val).startswith("0001"):
                    try:
                        c_date = datetime.datetime.fromisoformat(str(d_val).replace("Z", ""))
                    except Exception:
                        pass
            if not c_date and owner_1c and owner_1c.raw_payload:
                d_val = owner_1c.raw_payload.get("ДатаСоздания")
                if d_val and not str(d_val).startswith("0001"):
                    try:
                        c_date = datetime.datetime.fromisoformat(str(d_val).replace("Z", ""))
                    except Exception:
                        pass
                        
            # If creation date is missing or younger than inactivity threshold, skip!
            if not c_date or c_date > inactivity_threshold:
                continue
                
            # Cooldown Guard check (email, drafts, recent correspondence, company cooldown)
            can_send, reason = CooldownGuard.can_send_reactivation(db, email, owner_ref_key=owner_ref_key, days=cooldown_days, check_company=True)
            if not can_send:
                logger.info(f"Skipping cold candidate {email}: {reason}")
                continue

            new_candidates.append({
                "cand": cand,
                "contact_1c": contact_1c,
                "owner_ref_key": owner_ref_key,
                "max_received": None
            })
            if owner_ref_key:
                selected_owner_keys.add(owner_ref_key)
            if domain and domain not in PUBLIC_EMAIL_DOMAINS:
                selected_domains.add(domain)
            cold_selected += 1
                
        logger.info(f"Отобрано {len(new_candidates)} новых кандидатов на первичный контакт (Warm: {len(new_candidates)-cold_selected}, Cold: {cold_selected}).")
        
        for item in new_candidates:
            if drafts_created_today >= max_daily_drafts:
                logger.info(f"Достигнут суточный лимит черновиков ({max_daily_drafts}). Генерация новых черновиков завершена.")
                break

            cand = item["cand"]
            email = cand.email
            contact_1c = item["contact_1c"]
            owner_ref_key = item["owner_ref_key"]
            
            owner_1c = db.query(OnecOwner).filter(OnecOwner.owner_ref_key == owner_ref_key).first() if owner_ref_key else None
            is_buyer = bool(owner_1c.owner_is_buyer) if owner_1c else False
            company_name = owner_1c.owner_name if owner_1c else "Неизвестная компания"
            client_name = resolve_client_name(contact_1c.contact_name, None, "")
            style = get_next_style_for_client(db, email)
            
            query_ctx = build_client_query_context(cand, "", "")
            best_art = select_relevant_non_repeating_article(db, email, articles, query_ctx)
            
            logger.info(f"Запуск Шага 1 (Стандарт) для: {email}...")
            success = process_single_client_funnel_step(
                db=db, email=email, step_num=1, cand=cand,
                contact_1c=contact_1c, owner_ref_key=owner_ref_key,
                style=style, client_name=client_name, is_buyer=is_buyer,
                company_name=company_name, best_art=best_art
            )
            
            if success:
                drafts_created_today += 1
                fs = db.query(ReactivationFunnelState).filter(ReactivationFunnelState.client_email == email).first()
                if fs:
                    fs.current_step = 1
                    fs.step_status = "draft_created"
                    fs.last_action_at = None
                    fs.updated_at = datetime.datetime.utcnow()
                else:
                    fs = ReactivationFunnelState(
                        client_email=email,
                        current_step=1,
                        step_status="draft_created",
                        last_action_at=None
                    )
                    db.add(fs)
                db.commit()
                time.sleep(5.0)

        logger.info(f"Обработка ежедневной реанимации успешно завершена. Создано черновиков сегодня: {drafts_created_today} (лимит: {max_daily_drafts}).")
        
    except Exception as e:
        logger.error(f"Error running daily reactivation pipeline: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Запуск ежедневной реанимации клиентов (6-шаговая воронка).")
    parser.add_argument("--limit", type=int, default=3, help="Лимит новых контактов за один запуск (Шаг 1, по умолчанию: 3)")
    parser.add_argument("--active-limit", type=int, default=3, help="Лимит черновиков для активных воронок (Шаги 2-6, по умолчанию: 3)")
    parser.add_argument("--cold-limit", type=int, default=3, help="Лимит холодных новых контактов за один запуск (по умолчанию: 3)")
    parser.add_argument("--max-daily-drafts", type=int, default=6, help="Максимальное суммарное число создаваемых черновиков за день (по умолчанию: 6)")
    parser.add_argument("--cooldown", type=int, default=60, help="Период в днях (кулдаун) после завершения воронки (по умолчанию: 60 дней / 2 мес)")
    parser.add_argument("--inactivity", type=int, default=3, help="Период неактивности клиента в месяцах (по умолчанию: 3 мес / 90 дней)")
    args = parser.parse_args()
    try:
        os.makedirs("logs", exist_ok=True)
        logger.add("logs/run_daily_reactivation_{time}.log", rotation="1 day")
    except Exception as e_log:
        logger.warning(f"Could not initialize file log sink: {e_log}")

    run_daily_reactivation(
        limit=args.limit,
        active_limit=args.active_limit,
        cooldown_days=args.cooldown,
        inactivity_months=args.inactivity,
        cold_limit=args.cold_limit,
        max_daily_drafts=args.max_daily_drafts
    )
