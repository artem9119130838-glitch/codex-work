import os
import sys
import re
import json
import html
import random
import datetime
from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import EmailMessage, EmailMatchResult, ClientReactivationHistory
from app.services.hr_guard import HRGuard

COMMON_FIRST_NAMES = {
    # Мужские
    "александр", "алексей", "анатолий", "андрей", "антон", "арсений", "артем", "артём", "артур", 
    "богдан", "борис", "вадим", "валентин", "валерий", "василий", "виктор", "виталий", "владимир", 
    "владислав", "всеволод", "вячеслав", "георгий", "глеб", "григорий", "даниил", "данил", "данила", 
    "денис", "дмитрий", "евгений", "егор", "иван", "игорь", "илья", "кирилл", "константин", "лев", 
    "леонид", "максим", "матвей", "михаил", "никита", "николай", "олег", "павел", "петр", "пётр", 
    "роман", "руслан", "сергей", "станислав", "степан", "тарас", "тимофей", "тимур", "федор", "фёдор", 
    "эдуард", "юрий", "ярослав", "роял", "рушан", "рамиль", "марат", "рашид", "азат", "айдар", "айрат",
    # Женские
    "александра", "алена", "алёна", "алина", "алиса", "алла", "анастасия", "ангелина", "анна", "антонина", 
    "валентина", "валерия", "варвара", "василиса", "вера", "вероника", "виктория", "галина", "дарья", 
    "диана", "евгения", "екатерина", "елена", "елизавета", "жанна", "жанетта", "зинаида", "злата", 
    "инна", "ирина", "карина", "кира", "клавдия", "кристина", "ксения", "лариса", "лидия", "лилия", 
    "любовь", "людмила", "маргарита", "марина", "мария", "милана", "надежда", "наталья", "наталия", 
    "нина", "оксана", "олеся", "ольга", "полина", "раиса", "регина", "роза", "светлана", "снежана", 
    "софия", "софья", "тамара", "татьяна", "ульяна", "фаина", "эвелина", "элеонора", "элла", "эльвира", 
    "юлия", "яна", "айгуль", "алсу", "гульназ", "диляра", "зульфия", "лейла", "наиля", "рената", "альфия"
}

GENERIC_TITLES_AND_DEPTS = {
    "инженер", "мтс", "снабжение", "закупки", "логист", "логистика", "бухгалтер", "бухгалтерия",
    "директор", "руководитель", "начальник", "зам", "офис", "склад", "секретарь", "отдел",
    "приемная", "приёмная", "администратор", "специалист", "менеджер", "главный", "ведущий",
    "консультант", "мастер", "гендиректор", "коммерческий", "технический", "продажи", "заказ",
    "общий", "контакт", "компания", "клиент", "партнер", "партнёр", "коллега", "ооо", "зао", "пао", "ао", "ип"
}

SURNAME_ENDINGS = ('ов', 'ев', 'ин', 'их', 'ых', 'ова', 'ева', 'ина', 'ский', 'ская', 'цкий', 'цкая', 'ный', 'ная')

STOP_WORDS_GENERIC = {
    "наш", "ваш", "мой", "свой", "пока", "все", "всё", "это", "тут", "там", "как", "что",
    "где", "когда", "уважаемый", "уважаемая", "дорогие", "дорогой", "коллега", "коллеги",
    "партнеры", "друзья", "сауле", "анна", "директор", "менеджер",
    "руководитель", "отдел", "общий", "команда", "компания", "клиент"
}

PUBLIC_EMAIL_DOMAINS = {
    "mail.ru", "inbox.ru", "bk.ru", "list.ru", "yandex.ru", "ya.ru",
    "gmail.com", "rambler.ru", "internet.ru", "ro.ru"
}

def extract_first_name(full_name: str) -> str:
    if not full_name:
        return ""
    
    parts = re.split(r'[\s,\.-]+', full_name.strip())
    cleaned_tokens = []
    for p in parts:
        p_clean = p.strip()
        if not p_clean or not p_clean.isalpha() or len(p_clean) <= 1:
            continue
        p_lower = p_clean.lower()
        if p_lower in GENERIC_TITLES_AND_DEPTS:
            continue
        if p_lower.endswith(('ович', 'евич', 'ич', 'овна', 'евна', 'ична')):
            continue
        cleaned_tokens.append(p_clean)

    if not cleaned_tokens:
        return ""

    for token in cleaned_tokens:
        if token.lower() in COMMON_FIRST_NAMES:
            return token.capitalize()

    if len(cleaned_tokens) == 2:
        t0_lower = cleaned_tokens[0].lower()
        t1_lower = cleaned_tokens[1].lower()
        t0_is_surname = t0_lower.endswith(SURNAME_ENDINGS)
        t1_is_surname = t1_lower.endswith(SURNAME_ENDINGS)
        if t0_is_surname and not t1_is_surname:
            return cleaned_tokens[1].capitalize()
        elif t1_is_surname and not t0_is_surname:
            return cleaned_tokens[0].capitalize()

    if len(cleaned_tokens) == 1 and cleaned_tokens[0].lower().endswith(SURNAME_ENDINGS):
        return ""

    return ""

def resolve_client_name(contact_1c_name: str, contact_summary: dict = None, contact_emails_text: str = "", email: str = "") -> str:
    if email:
        local_part = email.split('@')[0].lower()
        if 'anastasia' in local_part or 'oxyanastasia' in local_part:
            return 'Анастасия'
        if 'dmitrii' in local_part or 'dmitriy' in local_part:
            return 'Дмитрий'
        if 'sergey' in local_part or 'sergei' in local_part:
            return 'Сергей'

    if contact_1c_name and contact_1c_name.strip() not in ["Общий контакт компании", ""]:
        fn = extract_first_name(contact_1c_name)
        if fn and fn.lower() not in ["коллега", "общий", "отдел"]:
            return fn

    if contact_emails_text and email:
        escaped_email = re.escape(email)
        header_matches = re.findall(r'["\']([А-Яа-яA-Za-z\s]+)["\']\s*<[^>]*' + escaped_email, contact_emails_text, re.IGNORECASE)
        for h in header_matches:
            fn = extract_first_name(h.strip())
            if fn and fn.lower() not in STOP_WORDS_GENERIC:
                return fn

        g_matches1 = re.findall(r'(?:здравствуйте|добрый день|доброе утро|добрый вечер)[,\s]+([А-ЯЁ][а-яё]+)', contact_emails_text)
        g_matches2 = re.findall(r'([А-ЯЁ][а-яё]+)[,\s]+(?:здравствуйте|добрый день|доброе утро|добрый вечер)', contact_emails_text)
        for g in g_matches1 + g_matches2:
            cand = g.strip().capitalize()
            if cand.lower() not in STOP_WORDS_GENERIC and len(cand) >= 3:
                return cand

        sig_matches = re.findall(r'(?:с уважением|с наилучшими пожеланиями|искренне ваш)[,\s]+([А-ЯЁ][а-яё]+)', contact_emails_text)
        for s in sig_matches:
            cand = s.strip().capitalize()
            if cand.lower() not in STOP_WORDS_GENERIC and len(cand) >= 3:
                return cand

    if contact_summary and isinstance(contact_summary, dict):
        extracted = contact_summary.get("extracted_person_name")
        if extracted and isinstance(extracted, str):
            fn = extract_first_name(extracted)
            if fn and fn.lower() not in STOP_WORDS_GENERIC:
                return fn

    return ""

def clean_company_name(raw_name: str) -> str:
    if not raw_name:
        return ""
    name = str(raw_name).strip()
    if any(p in name.lower() for p in ["неизвестная", "частное лицо", "не указано", "без названия", "физическое лицо"]):
        return ""
    
    name = re.sub(r'["«»“”]', '', name).strip()
    legal_forms = ["ООО", "АО", "ПАО", "ЗАО", "ИП", "НПО", "ПКФ", "OOO"]
    found_form = None
    
    for form in legal_forms:
        m_end = re.search(rf'[,.\s/\\-]+{form}$', name, re.IGNORECASE)
        if m_end:
            found_form = "ООО" if form.upper() in ["ООО", "OOO"] else form.upper()
            name = name[:m_end.start()].strip()
            break
            
    if not found_form:
        for form in legal_forms:
            m_start = re.search(rf'^{form}[,.\s/\\-]+', name, re.IGNORECASE)
            if m_start:
                found_form = "ООО" if form.upper() in ["ООО", "OOO"] else form.upper()
                name = name[m_start.end():].strip()
                break

    clean_core = re.sub(r'\s+', ' ', name).strip(" \t\r\n,.;:!?'\"-–—«»")
    if not clean_core or len(clean_core) < 2:
        return ""

    known_acronyms = {"нтзмк", "эпк", "пзм", "рвб", "слк", "тмх", "лпз", "бсм", "аэм", "гк"}
    if clean_core.isupper() and len(clean_core) > 3 and clean_core.lower() not in known_acronyms:
        clean_core = clean_core.title()
    elif clean_core.lower() in known_acronyms:
        clean_core = clean_core.upper()
        
    if found_form:
        if found_form == "ИП":
            return f"ИП {clean_core}"
        return f"{found_form} «{clean_core}»"
    return clean_core

def format_b2b_subject(clean_subj: str, llm_subj: str, company_name: str, client_name: str, skus_text: str = "") -> str:
    cleaned_company = clean_company_name(company_name)
    target_suffix = cleaned_company if cleaned_company else client_name

    boring_markers = [
        "поставки промышленного оборудования", "импорт из китая", "сотрудничес",
        "первая неделя", "запрос оборудования", "прибытие груза", "зарплата",
        "коммерческое предложение", "кп по запросу", "новое сообщение", "без темы",
        "поставки оборудования", "запчасти из кнр"
    ]
    
    selected_subj = ""
    if clean_subj:
        s_clean = re.sub(r'^(?:(?:Re|Fwd|Fw|Исх|Ответ|\[Spam\]):\s*)+', '', clean_subj, flags=re.IGNORECASE).strip()
        is_boring = any(m in s_clean.lower() for m in boring_markers) or len(s_clean) < 4
        if not is_boring:
            selected_subj = s_clean

    if not selected_subj and llm_subj:
        l_clean = re.sub(r'^(?:(?:Re|Fwd|Fw|Исх|Ответ|\[Spam\]):\s*)+', '', llm_subj, flags=re.IGNORECASE).strip()
        is_llm_boring = any(m in l_clean.lower() for m in boring_markers)
        if not is_llm_boring:
            selected_subj = l_clean
        
    if not selected_subj:
        if skus_text and len(skus_text) > 3 and not any(m in skus_text.lower() for m in boring_markers):
            first_sku = skus_text.split('\n')[0].split(',')[0].strip()[:40]
            selected_subj = f"Спецификация {first_sku}"
        else:
            selected_subj = "Спецификация по оборудованию и комплектующим"

    selected_subj = re.sub(r'[,.\s]+(?:ООО|АО|ПАО|ЗАО|ИП|НПО|ПКФ)\s*$', '', selected_subj, flags=re.IGNORECASE)
    selected_subj = re.sub(r'\s+', ' ', selected_subj).strip()
    
    if target_suffix and target_suffix.lower() not in selected_subj.lower():
        final_subj = f"Re: {selected_subj} для {target_suffix}"
    else:
        final_subj = f"Re: {selected_subj}"
        
    final_subj = re.sub(r'^(?:Re:\s*)+', 'Re: ', final_subj, flags=re.IGNORECASE)
    return final_subj

def get_emails_text_for_contact(db: Session, contact_ref_key: str, email: str) -> str:
    messages = db.query(EmailMessage).join(
        EmailMatchResult, EmailMessage.message_id == EmailMatchResult.message_id
    ).filter(
        EmailMatchResult.contact_ref_key == contact_ref_key,
        EmailMessage.is_junk == False
    ).order_by(EmailMessage.received_at.desc()).limit(10).all()
    
    messages.reverse()
    lines = []
    for m in messages:
        direction = "Входящие (от КЛИЕНТА)" if m.from_email == email else "Исходящие (от НАШЕЙ компании)"
        payload = m.raw_payload or {}
        text_content = payload.get("cleaned_text") or payload.get("text") or payload.get("snippet") or ""
        lines.append(f"Дата: {m.received_at} | Направление: {direction} | Тема: {m.subject}\nТекст:\n{text_content[:600]}\n---")
    return "\n\n".join(lines)

def get_emails_text_for_company(db: Session, owner_ref_key: str) -> str:
    messages = db.query(EmailMessage).join(
        EmailMatchResult, EmailMessage.message_id == EmailMatchResult.message_id
    ).filter(
        EmailMatchResult.owner_ref_key == owner_ref_key,
        EmailMessage.is_junk == False
    ).order_by(EmailMessage.received_at.desc()).limit(10).all()
    
    messages.reverse()
    lines = []
    for m in messages:
        direction = "Входящие (от КЛИЕНТА)" if m.from_email != settings.IMAP_USER else "Исходящие (от НАШЕЙ компании)"
        payload = m.raw_payload or {}
        text_content = payload.get("cleaned_text") or payload.get("text") or payload.get("snippet") or ""
        lines.append(f"Дата: {m.received_at} | Направление: {direction} | Тема: {m.subject}\nТекст:\n{text_content[:600]}\n---")
    return "\n\n".join(lines)

def load_articles() -> list:
    articles = []
    paths = [
        "C:/Codex_Shared/projects/n8n_email_ai/40_curated_kb/96_articles_index.md",
        "/app/40_curated_kb/96_articles_index.md",
        "40_curated_kb/96_articles_index.md"
    ]
    path_to_use = None
    for p in paths:
        if os.path.exists(p):
            path_to_use = p
            break
            
    if path_to_use:
        try:
            with open(path_to_use, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("|") and not line.strip().startswith("|---") and "URL" not in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 5:
                            url = parts[1]
                            title = parts[2]
                            desc = parts[3]
                            h1 = parts[4]
                            if url.startswith("http"):
                                articles.append({
                                    "url": url,
                                    "title": title,
                                    "desc": desc,
                                    "h1": h1
                                })
        except Exception as e:
            logger.error(f"Failed parsing articles index: {e}")
            
    if not articles:
        articles = [{
            "url": "https://longwang.ru/useful-articles/worlds-brend-equipment/",
            "title": "Как не купить подделку или б/у санкционное оборудование в Китае через посредника",
            "desc": "Как не купить подделку или б/у санкционное оборудование в Китае через посредника",
            "h1": "Как не купить подделку или б/у санкционное оборудование в Китае через посредника"
        }]
    return articles

def find_best_article(articles: list, query_text: str) -> dict:
    query_words = set(query_text.lower().replace(",", " ").replace(".", " ").replace(":", " ").replace("-", " ").split())
    stop_words = {"это", "для", "как", "или", "что", "этот", "все", "был", "была", "было", "будет", "быть"}
    query_words = {w for w in query_words if len(w) > 3 and w not in stop_words}
    
    best_article = articles[0]
    max_score = -1
    
    for art in articles:
        score = 0
        h1_clean = art["h1"].lower()
        title_clean = art["title"].lower()
        desc_clean = art["desc"].lower()
        
        for word in query_words:
            if word in h1_clean:
                score += 4
            if word in title_clean:
                score += 3
            if word in desc_clean:
                score += 1
                
        if score > max_score:
            max_score = score
            best_article = art
            
    return best_article

def get_next_style_for_client(db: Session, email: str) -> str:
    styles = ["деловой", "дружелюбный", "технический", "короткий"]
    last_hist = db.query(ClientReactivationHistory).filter(
        ClientReactivationHistory.client_email == email
    ).order_by(ClientReactivationHistory.sent_at.desc()).first()
    
    if not last_hist or not last_hist.template_used:
        return "деловой"
        
    last_template = last_hist.template_used.lower()
    last_style = "деловой"
    for s in styles:
        if s in last_template:
            last_style = s
            break
            
    remaining_styles = [s for s in styles if s != last_style]
    return random.choice(remaining_styles)

def search_live_imap_incoming(email: str) -> tuple:
    """
    Живой поиск последнего входящего письма от клиента на IMAP-сервере (Level 2 Fallback):
    1. Ищет письма от клиента в папке INBOX (по точному email).
    2. При отсутствии ищет по корпоративному домену компании.
    3. При нахождении валидирует через HRGuard и формирует (clean_subject, quote_text, orig_message_id).
    """
    user = os.environ.get("MAIL_ACCOUNT_2_USER") or settings.IMAP_USER
    password = os.environ.get("MAIL_ACCOUNT_2_PASS") or settings.IMAP_PASSWORD
    imap_host = os.environ.get("IMAP_SERVER") or settings.IMAP_HOST or "mail.hostland.ru"

    if not user or not password:
        try:
            accounts_json = os.environ.get("MAIL_ACCOUNTS")
            if accounts_json:
                accounts = json.loads(accounts_json.strip("'"))
                for acc in accounts:
                    if acc.get("user") == "sales@longwang.ru":
                        user = acc.get("user")
                        password = acc.get("pass")
                        break
        except Exception as ex:
            logger.warning(f"Failed parsing MAIL_ACCOUNTS: {ex}")

    if not user or not password or not imap_host:
        return None, "", None

    try:
        from imap_tools import MailBox, AND
        with MailBox(imap_host).login(user, password) as mailbox:
            # 1. Поиск по точному email в INBOX
            msgs = list(mailbox.fetch(AND(from_=email), limit=3, reverse=True, mark_seen=False))

            # 2. Если не найдено, поиск по домену (если корпоративный)
            if not msgs:
                domain = email.split('@')[-1].lower().strip()
                if domain and domain not in PUBLIC_EMAIL_DOMAINS:
                    msgs = list(mailbox.fetch(AND(from_=domain), limit=3, reverse=True, mark_seen=False))

            if not msgs:
                return None, "", None

            msg = msgs[0]
            subj = msg.subject or ""
            clean_subj = re.sub(r'^(?:(?:Re|Fwd|Fw|Исх|Ответ|\[Spam\]):\s*)+', '', subj, flags=re.IGNORECASE).strip()
            if not clean_subj:
                clean_subj = "Спецификация оборудования"

            body_text = msg.text or ""
            if not body_text and msg.html:
                body_text = re.sub(r'<[^>]+>', ' ', msg.html)
                body_text = html.unescape(body_text)

            body_text = body_text.strip()
            if len(body_text) < 15:
                return clean_subj, "", None

            is_hr, _ = HRGuard.is_job_seeker(email=msg.from_, subject=subj, messages_text=body_text)
            if is_hr:
                return None, "", None

            date_str = msg.date.strftime("%d.%m.%Y, %H:%M") if msg.date else "Неизвестная дата"
            from_header = msg.from_ or email
            quote_header = f"{date_str}, {from_header}:"

            quoted_lines = []
            for line in body_text.split('\n'):
                line_str = line.strip()
                if line_str:
                    quoted_lines.append(f"&gt; {line_str}")
                if len(quoted_lines) >= 12:
                    break

            quote_text = quote_header + "<br>\n" + "<br>\n".join(quoted_lines)

            orig_msg_id = None
            msg_id_headers = msg.headers.get('message-id', ())
            if msg_id_headers:
                orig_msg_id = msg_id_headers[0] if isinstance(msg_id_headers, (list, tuple)) else str(msg_id_headers)

            logger.info(f"[LIVE IMAP FOUND] Обнаружено входящее письмо от {email} на IMAP: '{clean_subj}'")
            return clean_subj, quote_text, orig_msg_id

    except Exception as e:
        logger.warning(f"Live IMAP search failed for {email}: {e}")
        return None, "", None

def get_last_incoming_email_details(db: Session, contact_ref_key: str, email: str) -> tuple:
    """
    Интеллектуальный поиск предыдущего контекста переписки:
    1. Поиск входящих писем в SQL DWH по контакту и корпоративному домену.
    2. Живой опрос IMAP-сервера Hostland (INBOX), если в базе SQL нет писем.
    3. ФОЛБЭК: Если клиент не отвечал, поиск последнего отправленного нами КП/письма.
    Возвращает: (clean_subject, quote_text, orig_message_id)
    """
    cand_msgs = db.query(EmailMessage).join(
        EmailMatchResult, EmailMessage.message_id == EmailMatchResult.message_id
    ).filter(
        EmailMatchResult.contact_ref_key == contact_ref_key,
        EmailMessage.is_junk == False,
        EmailMessage.from_email == email
    ).order_by(EmailMessage.received_at.desc()).limit(10).all()
    
    msg = None
    for cand in cand_msgs:
        payload = cand.raw_payload or {}
        if payload.get("is_sent") in (True, 'true', 'True'):
            continue
        sm = (cand.source_mailbox or "").lower()
        if any(f in sm for f in ["sent", "отправлен", "outbox"]):
            continue
        body_text = payload.get("cleaned_text") or payload.get("text") or payload.get("snippet") or ""
        body_lower = body_text.lower()
        if any(marker in body_lower for marker in ["longwang.ru", "с уважением, артем", "sales@longwang.ru", "ци линь", "лун-ван"]):
            continue
        is_hr, _ = HRGuard.is_job_seeker(email=cand.from_email, subject=cand.subject or "", messages_text=body_text)
        if not is_hr:
            msg = cand
            break

    if not msg:
        domain = email.split('@')[-1].lower().strip()
        if domain and domain not in PUBLIC_EMAIL_DOMAINS:
            candidates = db.query(EmailMessage).filter(
                EmailMessage.is_junk == False,
                EmailMessage.from_email.like(f"%@{domain}")
            ).order_by(EmailMessage.received_at.desc()).limit(10).all()
            for cand in candidates:
                payload = cand.raw_payload or {}
                if payload.get("is_sent") in (True, 'true', 'True'):
                    continue
                sm = (cand.source_mailbox or "").lower()
                if any(f in sm for f in ["sent", "отправлен", "outbox"]):
                    continue
                cand_text = payload.get("cleaned_text") or payload.get("text") or payload.get("snippet") or ""
                cand_lower = cand_text.lower()
                if any(marker in cand_lower for marker in ["longwang.ru", "с уважением, артем", "sales@longwang.ru", "ци линь", "лун-ван"]):
                    continue
                is_hr, _ = HRGuard.is_job_seeker(email=cand.from_email, subject=cand.subject or "", messages_text=cand_text)
                if not is_hr:
                    msg = cand
                    break

    # 2. LEVEL 2 FALLBACK: Живой поиск на сервере IMAP Hostland, если в SQL базе нет входящего письма
    if not msg:
        live_subj, live_quote, live_msg_id = search_live_imap_incoming(email)
        if live_subj and live_quote:
            return live_subj, live_quote, live_msg_id

    # 3. LEVEL 3 FALLBACK: Поиск последнего отправленного нами КП/письма
    is_outbound_quote = False
    if not msg:
        out_cand_msgs = db.query(EmailMessage).join(
            EmailMatchResult, EmailMessage.message_id == EmailMatchResult.message_id
        ).filter(
            EmailMatchResult.contact_ref_key == contact_ref_key,
            EmailMessage.is_junk == False
        ).order_by(EmailMessage.received_at.desc()).limit(15).all()
        
        for cand in out_cand_msgs:
            payload = cand.raw_payload or {}
            is_sent = payload.get("is_sent") in (True, 'true', 'True')
            sm = (cand.source_mailbox or "").lower()
            in_sent = any(f in sm for f in ["sent", "отправлен", "outbox"])
            if is_sent or in_sent:
                msg = cand
                is_outbound_quote = True
                break
                
        if not msg:
            out_by_to = db.query(EmailMessage).filter(
                EmailMessage.raw_payload.op('->>')('to').like(f"%{email}%"),
                EmailMessage.is_junk == False
            ).order_by(EmailMessage.received_at.desc()).limit(10).all()
            for cand in out_by_to:
                payload = cand.raw_payload or {}
                is_sent = payload.get("is_sent") in (True, 'true', 'True')
                sm = (cand.source_mailbox or "").lower()
                if is_sent or any(f in sm for f in ["sent", "отправлен"]):
                    msg = cand
                    is_outbound_quote = True
                    break

    if msg:
        subject = msg.subject or ""
        clean_subj = re.sub(r'^(?:(?:Re|Fwd|Fw|Исх|Ответ|\[Spam\]):\s*)+', '', subject, flags=re.IGNORECASE).strip()
        if not clean_subj:
            clean_subj = "Спецификация оборудования"
            
        payload = msg.raw_payload or {}
        body = payload.get("cleaned_text") or payload.get("text") or payload.get("snippet") or ""
        if not body or len(body.strip()) < 15:
            return clean_subj, "", None
            
        date_str = msg.received_at.strftime("%d.%m.%Y, %H:%M") if msg.received_at else "Неизвестная дата"
        from_name = msg.from_name or msg.from_email
        
        if is_outbound_quote:
            quote_header = f"{date_str}, {from_name} написал(а):"
            body = re.sub(r'(?i)(?:<br\s*/?>|\n)\s*(?:с\s+уважением|best\s+regards|менеджер|longwang|------------------------------).*$', '', body, flags=re.DOTALL).strip()
        else:
            quote_header = f"{date_str}, {from_name} &lt;{msg.from_email}&gt;:"
            
        quoted_lines = []
        for line in body.split('\n'):
            line_str = line.strip()
            if line_str:
                quoted_lines.append(f"&gt; {line_str}")
            if len(quoted_lines) >= 12:
                break
        
        quote_text = quote_header + "<br>\n" + "<br>\n".join(quoted_lines)
        
        payload_headers = payload.get("headers") or {}
        orig_msg_id = payload_headers.get("message-id") or payload.get("message_id") or msg.message_id
        if orig_msg_id and "_" in orig_msg_id and "@" in orig_msg_id and not orig_msg_id.startswith("<"):
            orig_msg_id = f"{orig_msg_id}@longwang.ru"
            
        return clean_subj, quote_text, orig_msg_id
        
    return None, "", None

def find_last_kp_attachment(imap_host: str, user: str, password: str, recipient: str) -> list:
    from imap_tools import MailBox, AND
    
    kp_attachments = []
    try:
        with MailBox(imap_host).login(user, password) as mailbox:
            sent_folder = None
            for folder in mailbox.folder.list():
                fn_lower = folder.name.lower()
                if fn_lower in ["sent", "inbox.sent", "отправленные", "inbox.отправленные", "sent messages"]:
                    sent_folder = folder.name
                    break
                elif "sent" in fn_lower or "отправлен" in fn_lower:
                    sent_folder = folder.name
                    break
            
            if not sent_folder:
                return []
                
            mailbox.folder.set(sent_folder)
            msgs = list(mailbox.fetch(AND(to=recipient), limit=5, reverse=True, mark_seen=False))
            now_dt = datetime.datetime.now(datetime.timezone.utc)
            for msg in msgs:
                msg_date = msg.date
                if msg_date:
                    if msg_date.tzinfo is None:
                        msg_date = msg_date.replace(tzinfo=datetime.timezone.utc)
                    age_days = (now_dt - msg_date).days
                    if age_days > 45:
                        logger.info(f"[ATTACHMENT SKIPPED] Historical КП for {recipient} was sent {age_days} days ago (>45 days limit). Outdated КП will NOT be attached.")
                        return []
                for att in msg.attachments:
                    fname = att.filename or ""
                    fname_lower = fname.lower()
                    if any(kw in fname_lower for kw in ["кп", "коммерческ", "предложен", "спецификац", "счет", "longwang", "lw", "расчет"]) and fname_lower.endswith((".pdf", ".xlsx", ".xls", ".docx")):
                        kp_attachments.append({
                            "filename": fname,
                            "data": att.payload,
                            "maintype": "application" if fname_lower.endswith(".pdf") else "octet-stream",
                            "subtype": "pdf" if fname_lower.endswith(".pdf") else "bin"
                        })
                        logger.info(f"Found historical fresh КП attachment '{fname}' ({len(att.payload)} bytes) for {recipient}")
                        return kp_attachments
    except Exception as e:
        logger.warning(f"Failed searching historical КП attachment for {recipient}: {e}")
        
    return kp_attachments

def save_draft_to_imap(subject: str, body: str, recipient: str, quote_text: str = "", extra_attachments: list = None, in_reply_to: str = None) -> bool:
    from imap_tools import MailBox
    from email.message import EmailMessage

    user = os.environ.get("MAIL_ACCOUNT_2_USER") or settings.IMAP_USER
    password = os.environ.get("MAIL_ACCOUNT_2_PASS") or settings.IMAP_PASSWORD
    imap_host = os.environ.get("IMAP_SERVER") or settings.IMAP_HOST or settings.IMAP_SERVER

    if not user or not password:
        try:
            accounts_json = os.environ.get("MAIL_ACCOUNTS")
            if accounts_json:
                accounts = json.loads(accounts_json.strip("'"))
                for acc in accounts:
                    if acc.get("user") == "sales@longwang.ru":
                        user = acc.get("user")
                        password = acc.get("pass")
                        break
        except Exception as ex:
            logger.warning(f"Failed parsing MAIL_ACCOUNTS: {ex}")

    if not user or not password or not imap_host:
        logger.error(f"IMAP settings are incomplete (user: {user}, host: {imap_host}). Cannot save draft.")
        return False

    if quote_text:
        cut_patterns = [
            r'(?i)(?:<br\s*/?>|\n)\s*(?:&gt;\s*)?(?:с\s+уважением|best\s+regards|искренне\s+ваш|менеджер\s+по\s+продажам|артем|ци\s+линь|лун-ван|longwang).*$',
            r'(?i)(?:<br\s*/?>|\n)\s*(?:&gt;\s*)?------------------------------.*$'
        ]
        sanitized_quote = quote_text
        for cp in cut_patterns:
            sanitized_quote = re.sub(cp, '', sanitized_quote, flags=re.DOTALL).strip()
        
        if len(sanitized_quote) > 30:
            quote_text = sanitized_quote
        else:
            logger.warning(f"[QUALITY GATE] В цитате для {recipient} не обнаружено содержательного текста. Цитата исключена.")
            quote_text = ""

    subject = re.sub(r'[,.\s]+(?:ООО|АО|ПАО|ЗАО|ИП|НПО|ПКФ)\s*$', '', subject, flags=re.IGNORECASE)
    subject = re.sub(r'«([^»]+),\s*»', r'«\1»', subject)
    subject = re.sub(r'"\s*([^"]+)\s*"', r'«\1»', subject)
    subject = re.sub(r'\s+', ' ', subject).strip()

    body = re.sub(r'(?i)\bскидк[а-я]*\s*(?:в\s*)?(?:10%|до\s*10%)?\b', 'специальные условия', body)
    body = re.sub(r'(?i)\b(?:наше\s+)?предложение\s+(?:сгорает|истекает)\s*(?:сегодня|завтра)?\b', 'будем рады актуализировать предложение', body)
    body = re.sub(r'(?i)\bпоследний\s+шанс\b', 'возможность', body)

    try:
        normalized = body.strip().replace('\r\n', '\n').replace('\r', '\n')
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)
        paragraphs = normalized.split('\n\n')
        formatted_paragraphs = [p.strip().replace('\n', '<br>') for p in paragraphs if p.strip()]
        html_body = '<br><br>\n'.join(formatted_paragraphs)
        
        if quote_text and len(quote_text.strip()) > 20:
            html_body += f"""<br><br>
<blockquote type="cite" style="border-left: 2px solid #3b82f6; margin-left: 5px; padding-left: 10px; color: #475569; font-style: normal;">
{quote_text}
</blockquote>"""
            
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = user
        msg['To'] = recipient
        if in_reply_to:
            clean_id = str(in_reply_to).strip().strip('<>')
            if clean_id:
                msg['In-Reply-To'] = f"<{clean_id}>"
                msg['References'] = f"<{clean_id}>"
                logger.info(f"Thread linking: In-Reply-To=<{clean_id}> for {recipient}")
        msg.set_content(html_body, subtype='html')

        pdf_paths = [
            "/root/n8n_email_ai/presentation_and_reference.pdf",
            "/app/presentation_and_reference.pdf",
            "presentation_and_reference.pdf",
            "../presentation_and_reference.pdf"
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
                    logger.info(f"Successfully attached PDF presentation from {ppath}")
                    break
                except Exception as ex:
                    logger.warning(f"Failed attaching PDF presentation {ppath}: {ex}")

        kp_atts = extra_attachments if extra_attachments is not None else find_last_kp_attachment(imap_host, user, password, recipient)
        if kp_atts:
            for att in kp_atts:
                try:
                    msg.add_attachment(
                        att["data"],
                        maintype=att.get("maintype", "application"),
                        subtype=att.get("subtype", "octet-stream"),
                        filename=att["filename"]
                    )
                    logger.info(f"Successfully attached fresh historical КП '{att['filename']}' for {recipient}")
                except Exception as ex:
                    logger.warning(f"Failed attaching fresh historical КП: {ex}")

        with MailBox(imap_host).login(user, password) as mailbox:
            draft_folder = None
            for folder in mailbox.folder.list():
                fn_lower = folder.name.lower()
                if fn_lower in ["drafts", "inbox.drafts", "черновики", "inbox.черновики"]:
                    draft_folder = folder.name
                    break
            if not draft_folder:
                draft_folder = "Drafts"

            logger.info(f"Uploading draft to IMAP folder: '{draft_folder}' for {recipient}")
            raw_email_bytes = msg.as_bytes()
            mailbox.append(raw_email_bytes, folder=draft_folder)
            logger.info(f"Draft for {recipient} successfully saved to '{draft_folder}'.")
            return True

    except Exception as e:
        logger.error(f"Failed creating/saving draft for {recipient}: {e}")
        return False
