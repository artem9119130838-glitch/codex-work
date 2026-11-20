import re
import os
import sys
import time
import json
import datetime
from loguru import logger

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.services.llm_service import llm_service
from app.db.database import get_db
from app.db.models import ClientIntel, OnecOwner, OnecContact, KnowledgeBaseChunk, EmailMessage, EmailMatchResult, ClientReactivationHistory
from sqlalchemy.orm import Session
from sqlalchemy import text

TEST_EMAILS = [
    "vasin@tbs-semi.ru",
    "sakrupenko@s1.rosneft.ru",
    "n.i.khliustina@sozvezdie.su",
    "tahautdinov@aksolit.com",
    "info@almaz-snab.ru"
]

EMAIL_STYLES = {
    "vasin@tbs-semi.ru": "технический",
    "sakrupenko@s1.rosneft.ru": "деловой",
    "n.i.khliustina@sozvezdie.su": "дружелюбный",
    "tahautdinov@aksolit.com": "деловой",
    "info@almaz-snab.ru": "дружелюбный"
}

OUTPUT_FILE = "/tmp/pilot_test_results.md"

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

def extract_first_name(full_name: str) -> str:
    import re
    if not full_name:
        return ""
    
    parts = re.split(r'[\s,\.-]+', full_name.strip())
    # Отсекаем пустые части, однобуквенные инициалы и известные служебные слова/должности
    cleaned_tokens = []
    for p in parts:
        p_clean = p.strip()
        if not p_clean or not p_clean.isalpha() or len(p_clean) <= 1:
            continue
        p_lower = p_clean.lower()
        if p_lower in GENERIC_TITLES_AND_DEPTS:
            continue
        # Отсекаем отчества
        if p_lower.endswith(('ович', 'евич', 'ич', 'овна', 'евна', 'ична')):
            continue
        cleaned_tokens.append(p_clean)

    if not cleaned_tokens:
        return ""

    # Приоритет 1: Ищем токен из проверенного белого списка имен
    for token in cleaned_tokens:
        if token.lower() in COMMON_FIRST_NAMES:
            return token.capitalize()

    # Приоритет 2: Если токенов 2, и один оканчивается на окончание фамилии, а второй нет
    if len(cleaned_tokens) == 2:
        t0_lower = cleaned_tokens[0].lower()
        t1_lower = cleaned_tokens[1].lower()
        t0_is_surname = t0_lower.endswith(SURNAME_ENDINGS)
        t1_is_surname = t1_lower.endswith(SURNAME_ENDINGS)
        if t0_is_surname and not t1_is_surname:
            return cleaned_tokens[1].capitalize()
        elif t1_is_surname and not t0_is_surname:
            return cleaned_tokens[0].capitalize()

    # Если токен 1, и он оканчивается на окончание фамилии (например, "Куликова", "Иванов") - СТРОГО ЗАПРЕЩЕНО
    if len(cleaned_tokens) == 1 and cleaned_tokens[0].lower().endswith(SURNAME_ENDINGS):
        return ""

    # Во всех сомнительных случаях возвращаем пустую строку для безопасного обращения "Добрый день!"
    return ""

STOP_WORDS_GENERIC = {
    "наш", "ваш", "мой", "свой", "пока", "все", "всё", "это", "тут", "там", "как", "что",
    "где", "когда", "уважаемый", "уважаемая", "дорогие", "дорогой", "коллега", "коллеги",
    "партнеры", "друзья", "сауле", "анна", "директор", "менеджер",
    "руководитель", "отдел", "общий", "команда", "компания", "клиент"
}

def resolve_client_name(contact_1c_name: str, contact_summary: dict = None, contact_emails_text: str = "", email: str = "") -> str:
    """
    Интеллектуальное определение имени клиента:
    1. Имя из email (например, oxyanastasia -> Анастасия)
    2. Из 1С (ФИО контакта)
    3. Из цитат заголовков писем ("Имя Фамилия" <email>)
    4. Из приветствий наших менеджеров в переписке ("Анастасия, добрый день")
    5. Из подписей клиента ("С уважением, Имя")
    6. Из contact_summary
    """
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

def get_emails_text_for_contact(db: Session, contact_ref_key: str, email: str) -> str:
    # Fetch last 10 messages matched to this contact to prevent token overflow and reduce costs
    messages = db.query(EmailMessage).join(
        EmailMatchResult, EmailMessage.message_id == EmailMatchResult.message_id
    ).filter(
        EmailMatchResult.contact_ref_key == contact_ref_key,
        EmailMessage.is_junk == False
    ).order_by(EmailMessage.received_at.desc()).limit(10).all()
    
    # Reverse to keep chronological order
    messages.reverse()
    
    lines = []
    for m in messages:
        direction = "Входящие (от КЛИЕНТА)" if m.from_email == email else "Исходящие (от НАШЕЙ компании)"
        payload = m.raw_payload or {}
        text_content = payload.get("cleaned_text") or payload.get("text") or payload.get("snippet") or ""
        lines.append(f"Дата: {m.received_at} | Направление: {direction} | Тема: {m.subject}\nТекст:\n{text_content[:600]}\n---")
    return "\n\n".join(lines)

def get_emails_text_for_company(db: Session, owner_ref_key: str) -> str:
    # Fetch last 10 messages matched to this company (owner) to prevent token overflow and reduce costs
    messages = db.query(EmailMessage).join(
        EmailMatchResult, EmailMessage.message_id == EmailMatchResult.message_id
    ).filter(
        EmailMatchResult.owner_ref_key == owner_ref_key,
        EmailMessage.is_junk == False
    ).order_by(EmailMessage.received_at.desc()).limit(10).all()
    
    # Reverse to keep chronological order
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
    # Local path and Docker path
    paths = [
        "C:/Codex_Shared/projects/n8n_email_ai/40_curated_kb/96_articles_index.md",
        "/app/40_curated_kb/96_articles_index.md"
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
            
    # Return default articles list if parsing failed
    if not articles:
        articles = [{
            "url": "https://longwang.ru/useful-articles/worlds-brend-equipment/",
            "title": "Как не купить подделку или б/у санкционное оборудование в Китае через посредника",
            "desc": "Как не купить подделку или б/у санкционное оборудование в Китае через посредника",
            "h1": "Как не купить подделку или б/у санкционное оборудование в Китае через посредника"
        }]
    return articles

def find_best_article(articles: list, query_text: str) -> dict:
    # Simple keyword matching score
    query_words = set(query_text.lower().replace(",", " ").replace(".", " ").replace(":", " ").replace("-", " ").split())
    # Remove short stop-words and common junk words
    stop_words = {"это", "для", "как", "или", "что", "этот", "все", "был", "была", "было", "будет", "быть"}
    query_words = {w for w in query_words if len(w) > 3 and w not in stop_words}
    
    best_article = articles[0]
    max_score = -1
    
    for art in articles:
        # Give higher weight to matches in title and h1
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

def get_next_style_for_client(db, email: str) -> str:
    # Available styles to choose from
    styles = ["деловой", "дружелюбный", "технический", "короткий"]
    
    # Get last history record
    last_hist = db.query(ClientReactivationHistory).filter(
        ClientReactivationHistory.client_email == email
    ).order_by(ClientReactivationHistory.sent_at.desc()).first()
    
    if not last_hist or not last_hist.template_used:
        # Default or first choice
        default_style = EMAIL_STYLES.get(email)
        return default_style if default_style else "деловой"
        
    last_template = last_hist.template_used.lower()
    # Find which style was used in the last template
    last_style = "деловой"
    for s in styles:
        if s in last_template:
            last_style = s
            break
            
    # Filter out the last style and pick the next one
    remaining_styles = [s for s in styles if s != last_style]
    import random
    return random.choice(remaining_styles)

def clean_company_name(raw_name: str) -> str:
    """
    Очищает и форматирует название компании (например: 'МАНКОР ООО' -> 'ООО «Манкор»').
    Возвращает пустую строку, если компания неизвестна или является частным лицом.
    """
    import re
    if not raw_name:
        return ""
    name = str(raw_name).strip()
    if any(p in name.lower() for p in ["неизвестная", "частное лицо", "не указано", "без названия", "физическое лицо"]):
        return ""
    
    # 1. Снимаем внешние и внутренние паразитные кавычки
    name = re.sub(r'["«»“”]', '', name).strip()
    
    legal_forms = ["ООО", "АО", "ПАО", "ЗАО", "ИП", "НПО", "ПКФ", "OOO"]
    found_form = None
    
    # В конце: ', ООО' или ' ООО'
    for form in legal_forms:
        m_end = re.search(rf'[,.\s/\\-]+{form}$', name, re.IGNORECASE)
        if m_end:
            found_form = "ООО" if form.upper() in ["ООО", "OOO"] else form.upper()
            name = name[:m_end.start()].strip()
            break
            
    # В начале: 'ООО ' или 'ООО, '
    if not found_form:
        for form in legal_forms:
            m_start = re.search(rf'^{form}[,.\s/\\-]+', name, re.IGNORECASE)
            if m_start:
                found_form = "ООО" if form.upper() in ["ООО", "OOO"] else form.upper()
                name = name[m_start.end():].strip()
                break

    # 2. Чистка ядра от висячих знаков препинания и лишних пробелов
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
    """
    Формирует живую, нерекламную B2B-тему письма.
    - Исключает рекламные клише ('Поставки промышленного оборудования...', 'импорт из китая' и т.п.)
    - Гарантирует префикс Re: без дубликатов
    - Добавляет 'для <Компания>' (или 'для <Имя>') в конец, если известно и еще не добавлено.
    """
    import re
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
        # Strip all existing Re:, Fwd:, etc.
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

    # Add target suffix ('для <Компания/Имя>') at the end if not already present
    if target_suffix:
        # Normalize uppercase words in suffix
        if target_suffix.isupper() and len(target_suffix) > 4:
            target_suffix = target_suffix.title()
        if not re.search(r'\bдля\b', selected_subj, re.IGNORECASE):
            selected_subj = f"{selected_subj} для {target_suffix}"

    final_subj = f"Re: {selected_subj}"
    final_subj = re.sub(r'^(?:Re:\s*)+', 'Re: ', final_subj, flags=re.IGNORECASE)
    # Final cleanup of uppercase company in subject
    final_subj = re.sub(r'(?i)\bдля\s+([А-ЯЁA-Z\s]{4,})\b', lambda m: f"для {m.group(1).title()}" if m.group(1).isupper() and m.group(1).strip() not in ["ООО", "ЗАО", "ПАО", "НПО"] else m.group(0), final_subj)
    return final_subj

PUBLIC_EMAIL_DOMAINS = {
    "gmail.com", "mail.ru", "yandex.ru", "bk.ru", "inbox.ru", "list.ru",
    "rambler.ru", "internet.ru", "ya.ru", "outlook.com", "hotmail.com", "icloud.com", "yahoo.com"
}

def get_last_incoming_email_details(db: Session, contact_ref_key: str, email: str) -> tuple:
    from app.services.hr_guard import HRGuard

    # 1. Поиск подлинных входящих писем от конкретного контакта
    # КАТЕГОРИЧЕСКИ ИСКЛЮЧАЕМ:
    # - Исходящие письма (raw_payload->>'is_sent' == True)
    # - Папки отправленных (source_mailbox содержит 'sent' или 'отправлен')
    # - Собственные подписи LongWang, Артема, Ци Линь
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
        # 2. Поиск по корпоративному домену компании (только для непобличных доменов)
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

    is_outbound_quote = False
    if not msg:
        # 3. ФОЛБЭК: Если входящих писем от клиента не было, ищем последнее ИСХОДЯЩЕЕ письмо (КП / спецификацию)
        # для формирования связки ветки (In-Reply-To) и цитирования ранее отправленного предложения
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
        import re
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
            # Для исходящего КП убираем длинную футерную подпись, оставляя суть предложения
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
        
        # Extract RFC Message-ID for In-Reply-To threading
        payload_headers = payload.get("headers") or {}
        orig_msg_id = payload_headers.get("message-id") or payload.get("message_id") or msg.message_id
        if orig_msg_id and "_" in orig_msg_id and "@" in orig_msg_id and not orig_msg_id.startswith("<"):
            # Fallback for synthetic IDs like sales@longwang.ru_INBOX_123
            orig_msg_id = f"{orig_msg_id}@longwang.ru"
            
        return clean_subj, quote_text, orig_msg_id
        
    return None, "", None

def find_last_kp_attachment(imap_host: str, user: str, password: str, recipient: str) -> list:
    """
    Ищет в папках Sent/Отправленные последнее отправленное клиенту КП или спецификацию
    и возвращает структуру для вложения: [{'filename': ..., 'data': bytes, 'maintype': ..., 'subtype': ...}]
    """
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
                # Check message age - prohibit attaching outdated КП older than 45 days
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
    import datetime

    user = os.environ.get("MAIL_ACCOUNT_2_USER") or settings.IMAP_USER
    password = os.environ.get("MAIL_ACCOUNT_2_PASS") or settings.IMAP_PASSWORD
    imap_host = os.environ.get("IMAP_SERVER") or settings.IMAP_HOST or settings.IMAP_SERVER

    # Try to parse MAIL_ACCOUNTS if flat variables are not present
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

    # QUALITY GATE 1: Умная санитизация цитат (отсечение нашей старой подписи из хвоста)
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
            logger.warning(f"[QUALITY GATE] В цитате для {recipient} не обнаружено содержательного ответа клиента. Цитата исключена.")
            quote_text = ""

    # QUALITY GATE 2: Нормализация темы письма от висячих запятых и кривых названий
    subject = re.sub(r'[,.\s]+(?:ООО|АО|ПАО|ЗАО|ИП|НПО|ПКФ)\s*$', '', subject, flags=re.IGNORECASE)
    subject = re.sub(r'«([^»]+),\s*»', r'«\1»', subject)
    subject = re.sub(r'"\s*([^"]+)\s*"', r'«\1»', subject)
    subject = re.sub(r'\s+', ' ', subject).strip()

    # QUALITY GATE 3: Санитизация тела письма от запрещенных B2C-скидок и тавтологий
    body = re.sub(r'(?i)\bскидк[а-я]*\s*(?:в\s*)?(?:10%|до\s*10%)?\b', 'специальные условия', body)
    body = re.sub(r'(?i)\b(?:наше\s+)?предложение\s+(?:сгорает|истекает)\s*(?:сегодня|завтра)?\b', 'будем рады актуализировать предложение', body)
    body = re.sub(r'(?i)\bпоследний\s+шанс\b', 'возможность', body)

    try:
        # Convert Plain Text body newlines to HTML br tags
        normalized = body.strip().replace('\r\n', '\n').replace('\r', '\n')
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)
        paragraphs = normalized.split('\n\n')
        formatted_paragraphs = [p.strip().replace('\n', '<br>') for p in paragraphs if p.strip()]
        html_body = '<br><br>\n'.join(formatted_paragraphs)
        
        # Append stylized blockquote if present
        if quote_text and len(quote_text.strip()) > 20:
            html_body += f"""<br><br>
<blockquote type="cite" style="border-left: 2px solid #3b82f6; margin-left: 5px; padding-left: 10px; color: #475569; font-style: normal;">
{quote_text}
</blockquote>"""
            
        # Create HTML email message with RFC threading headers
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

        # Try to attach PDF presentation (Always attached)
        pdf_paths = [
            "/root/n8n_email_ai/presentation_and_reference.pdf",
            "/app/presentation_and_reference.pdf",
            "presentation_and_reference.pdf",
            "../presentation_and_reference.pdf"
        ]
        pdf_attached = False
        for ppath in pdf_paths:
            if os.path.exists(ppath):
                try:
                    with open(ppath, "rb") as f:
                        file_data = f.read()
                        msg.add_attachment(
                            file_data,
                            maintype='application',
                            subtype='pdf',
                            filename="Презентация и референс-лист.pdf"
                        )
                    logger.info(f"Successfully attached PDF presentation from {ppath}")
                    pdf_attached = True
                    break
                except Exception as ex:
                    logger.warning(f"Failed to attach PDF from {ppath}: {ex}")
        if not pdf_attached:
            logger.warning("PDF presentation was NOT attached because the file could not be found.")

        # Auto-lookup last sent Commercial Proposal (КП) if not explicitly provided
        if extra_attachments is None:
            extra_attachments = find_last_kp_attachment(imap_host, user, password, recipient)

        # Attach extra files (e.g. historical КП / specification)
        if extra_attachments:
            for att in extra_attachments:
                try:
                    fname = att.get("filename", "Коммерческое_предложение.pdf")
                    fdata = att.get("data")
                    if fdata:
                        msg.add_attachment(
                            fdata,
                            maintype=att.get("maintype", "application"),
                            subtype=att.get("subtype", "pdf"),
                            filename=fname
                        )
                        logger.info(f"Successfully attached extra file: {fname} ({len(fdata)} bytes) for {recipient}")
                except Exception as e_att:
                    logger.warning(f"Failed to attach extra file {att}: {e_att}")

        # Connect to mailbox
        with MailBox(imap_host).login(user, password) as mailbox:
            # Detect drafts folder (Prioritize Drafts / INBOX.Drafts / Черновики)
            drafts_folder = "Drafts"
            for folder in mailbox.folder.list():
                folder_name_lower = folder.name.lower()
                if folder_name_lower in ["drafts", "inbox.drafts", "черновики", "inbox.черновики"]:
                    drafts_folder = folder.name
                    break
                elif "draft" in folder_name_lower or "черновик" in folder_name_lower:
                    drafts_folder = folder.name
                    break
            
            logger.info(f"Uploading draft to IMAP folder: '{drafts_folder}' for {recipient}")
            mailbox.folder.set(drafts_folder)
            mailbox.append(msg.as_bytes(), folder=drafts_folder, flag_set=['\\Draft'])
            return True
    except Exception as e:
        logger.error(f"Failed to save draft to IMAP for {recipient}: {e}")
        return False

def main():
    logger.info("Starting pilot test generation with drafts creation...")
    db = next(get_db())
    articles = load_articles()
    
    markdown_report = []
    markdown_report.append("# Пилотный отчет: Тестовая генерация Саммари и Черновиков реанимации\n")
    markdown_report.append("Этот отчет содержит 5 тестовых клиентов. Для каждого сгенерировано контактное и корпоративное саммари, осуществлен RAG-поиск по базе знаний, сформировано реанимационное письмо в индивидуальном стиле и сохранено в черновики sales@longwang.ru по IMAP.\n")
    
    try:
        for idx, email in enumerate(TEST_EMAILS):
            logger.info(f"Processing {email} ({idx+1}/{len(TEST_EMAILS)})...")
            
            # Find contact and company info
            contact_1c = db.query(OnecContact).filter(text(":email = ANY(emails)")).params(email=email).first()
            if not contact_1c:
                logger.warning(f"Contact {email} not found in 1C sync table.")
                continue
                
            owner_ref_key = contact_1c.owner_ref_key
            owner_1c = db.query(OnecOwner).filter(OnecOwner.owner_ref_key == owner_ref_key).first() if owner_ref_key else None
            
            is_buyer = bool(owner_1c.owner_is_buyer) if owner_1c else False
            company_name = owner_1c.owner_name if owner_1c else "Неизвестная компания"
            
            # Get email history texts (limited to 10 latest to save tokens and costs)
            contact_emails_text = get_emails_text_for_contact(db, contact_1c.contact_ref_key, email)
            company_emails_text = get_emails_text_for_company(db, owner_ref_key) if owner_ref_key else ""
            
            if not contact_emails_text:
                contact_emails_text = "Нет переписки с этим email в базе данных."
            if not company_emails_text:
                company_emails_text = "Нет переписки с этой компанией в базе данных."
                
            # 1. RAG Search (done locally to save tokens by matching keywords in history)
            best_art = find_best_article(articles, contact_emails_text + " " + company_emails_text)
            logger.info(f"Matched article: {best_art['url']} | Title: {best_art['title']}")
            
                                    # 2. Check if we already have a summary in clients_intel
            intel = db.query(ClientIntel).filter(ClientIntel.email == email).first()
            
            contact_summary_dict = None
            company_summary_dict = None
            has_new_emails = False
            
            if intel and intel.updated_at:
                                # SQL check: max email timestamp for this contact/company compared to summary update time
                max_received = db.execute(text("""
                    SELECT MAX(m.received_at)
                    FROM email_messages m
                    JOIN email_match_results r ON m.message_id = r.message_id
                    WHERE r.contact_ref_key = :ref_key OR r.owner_ref_key = :owner_key
                """), {"ref_key": contact_1c.contact_ref_key, "owner_key": owner_ref_key}).scalar()
                
                if max_received and max_received > intel.updated_at:
                    has_new_emails = True
                    logger.info(f"Detected new email messages since last summary update ({max_received} > {intel.updated_at}). Cache invalidated.")
            
            if intel and intel.ai_summary and not has_new_emails:
                logger.info(f"Found cached summary in database for {email}.")
                try:
                    cached_data = json.loads(intel.ai_summary)
                    contact_summary_dict = cached_data.get("contact_summary")
                    company_summary_dict = cached_data.get("company_summary")
                except Exception as ex:
                    logger.warning(f"Failed parsing cached summary: {ex}")
                    
            if not contact_summary_dict or not company_summary_dict:
                logger.info(f"No cached summary found (or parsing failed/outdated). Generating summary via LLM (Forced Gemini)...")
                style = EMAIL_STYLES.get(email, "деловой")
                client_name = extract_first_name(contact_1c.contact_name)
                
                # Generate summary via LLM (Automatic provider cascade with DeepSeek fallback)
                summaries = llm_service.generate_client_intelligence_summary(
                    contact_emails_text=contact_emails_text,
                    company_emails_text=company_emails_text,
                    is_buyer=is_buyer,
                    client_name=client_name,
                    force_provider=None
                )
                contact_summary_dict = summaries.get("contact_summary", {})
                company_summary_dict = summaries.get("company_summary", {})
                
                # Save to database
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
                logger.info(f"Saved generated summary to database for {email}.")
                
            contact_summary = json.dumps(contact_summary_dict, ensure_ascii=False, indent=2)
            company_summary = json.dumps(company_summary_dict, ensure_ascii=False, indent=2)
            
            # Now generate reactivation draft from cached summary via DeepSeek
            provider_type = "deepseek"
            logger.info(f"Generating reactivation email draft using provider: {provider_type.upper()}...")
            style = get_next_style_for_client(db, email)
            client_name = resolve_client_name(contact_1c.contact_name, contact_summary_dict, contact_emails_text)
            
            # Check if we already sent the partnership prelude previously
            has_sent_partnership_prelude = check_if_prelude_sent(db, email)
            
            # Check price objection
            price_objection_text = None
            if contact_summary_dict:
                failed_reason = str(contact_summary_dict.get("reason_deal_failed", "")).lower()
                hist_notes = str(contact_summary_dict.get("interaction_history", "")).lower()
                if any(w in failed_reason or w in hist_notes for w in ["дорого", "цена космос", "высокая цена", "превысил бюджет"]):
                    price_objection_text = "предыдущее предложение превышало бюджет / высокая цена"

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
                force_provider=provider_type,
                has_sent_partnership_prelude=has_sent_partnership_prelude,
                price_objection_text=price_objection_text
            )
            
            # Determine manager name
            manager_name = "Артем"
            last_mgrs = contact_summary_dict.get("last_managers") or []
            company_portr = company_summary_dict.get("key_decision_makers") or ""
            mgrs_str = (" ".join(last_mgrs) + " " + company_portr).lower()
            if "сауле" in mgrs_str:
                manager_name = "Сауле"
            elif "анна" in mgrs_str:
                manager_name = "Анна"
            
            # Format realistic B2B subject: Re: [equipment/sku/request] для [Company/Client]
            clean_subj, quote_text, orig_msg_id = get_last_incoming_email_details(db, contact_1c.contact_ref_key, email)
            skus_text = str(contact_summary_dict.get("skus_and_amounts") or "")
            subject = format_b2b_subject(clean_subj, llm_subj, company_name, client_name, skus_text)
            
            # Clean double signatures if generated by LLM (remove anything starting with 'С уважением' till the end)
            import re
            body = re.sub(r'(?i)<br\s*/?>\s*(?:с уважением|с наилучшими пожеланиями|искренне ваш|с уважением, менеджер по продажам).*$', '', body, flags=re.DOTALL)
            body = re.sub(r'(?i)(?:с уважением|с наилучшими пожеланиями|искренне ваш|с уважением, менеджер по продажам).*$', '', body, flags=re.DOTALL).strip()
            
            # HTML Signature (Tightly spaced, without empty line gaps)
            signature_html = f"""<div style="font-family: 'Times New Roman', Times, serif; font-size: 12pt; line-height: 1.2; margin: 0; padding: 0;">
С уважением, {manager_name}<br>
<a href="https://longwang.ru/" target="_blank" tabindex="-1" style="text-decoration: underline; color: blue;">LongWang</a> Тел <a href="tel:+78125091245" target="_blank" tabindex="-1" style="text-decoration: underline; color: blue;">+7 (812) 509-1245</a><br>
<a href="mailto:sales@longwang.ru" target="_blank" tabindex="-1" style="text-decoration: underline; color: blue;">sales@longwang.ru</a><br>
<br>
------------------------------<br>
<i>Если Вам в дальнейшем понадобится что-то из оригинального оборудования Atlas Copco, SMC, Caterpillar, Danfoss, Siemens, Megger, Fronius, Brevini, Autonics и/или <a href="https://longwang.ru/supplies-services-china/brands/" target="_blank" tabindex="-1" style="text-decoration: underline; color: blue;">этих производителей</a>, то у нас и нашего китайского и сербского представительства заключены прямые договоры на поставку с ними и их дистрибьютерами. Также мы поставляем промышленное <a href="https://longwang.ru/supplies-services-china/equipment-from-china/" target="_blank" tabindex="-1" style="text-decoration: underline; color: blue;">оборудование из Китая и аналоги</a>. Также у нашей компании есть филиалы в Казахстане и Кыргызстане для <a href="https://longwang.ru/supplies-services-china/platezhi-v-kitai/" target="_blank" tabindex="-1" style="text-decoration: underline; color: blue;">проведения оплат</a> и организации <a href="https://longwang.ru/supplies-services-china/dostavka-is-kitaya/" target="_blank" tabindex="-1" style="text-decoration: underline; color: blue;">доставки</a>.</i>
</div>"""
            
            body_with_signature = body + "<br><br>" + signature_html
            
            # 3. Save to IMAP
            logger.info(f"Saving draft to IMAP '{style}' style...")
            saved_to_imap = save_draft_to_imap(subject, body_with_signature, email, quote_text=quote_text, in_reply_to=orig_msg_id)
            imap_status = "УСПЕШНО СОХРАНЕНО В ЧЕРНОВИКИ SALES" if saved_to_imap else "ОШИБКА СОХРАНЕНИЯ В IMAP"
            if saved_to_imap:
                hist = ClientReactivationHistory(
                    client_email=email,
                    article_url=best_art["url"],
                    sent_at=datetime.datetime.utcnow(),
                    template_used=f"{style}_test_draft",
                    subject=subject,
                    body=body
                )
                db.add(hist)
                db.commit()
                logger.info(f"Saved test reactivation draft history for {email}")
            time.sleep(2.0)
            
            # 4. Form report slice
            report_slice = f"""
## Клиент {idx+1}: {email}
*   **Компания (1С):** {company_name} (ID: {owner_ref_key})
*   **Статус покупателя (1С):** {'Покупатель (Да)' if is_buyer else 'Лид (Нет)'}
*   **Выбранный стиль:** {style}
*   **Использованный провайдер ИИ:** {provider_type.upper()}
*   **Статус IMAP:** {imap_status}

### 📋 Саммари Контакта
```json
{contact_summary}
```

### 🏢 Саммари Компании
```json
{company_summary}
```

### 📝 Черновик Реанимационного Письма
**Тема:** {subject}

**Тело письма:**
{body}

**Официальная подпись:**
{signature_html}

---
"""
            markdown_report.append(report_slice)
            
        # Write report
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.writelines(markdown_report)
            
        logger.info(f"Report successfully written to {OUTPUT_FILE}")
        
    except Exception as e:
        logger.exception("Error in pilot test:")
    finally:
        db.close()

if __name__ == "__main__":
    main()
