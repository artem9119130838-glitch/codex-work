"""
Ingest Cold Leads from 1C:УНФ into DWH (marketing_db) for Client Reactivation Pipeline.

Канонический скрипт отбора и дозированного импорта спящих лидов из 1С:УНФ в DWH.
Строго соблюдает:
- Дозирование по 100 контактов за прогон (--batch-size 100).
- Фильтр давности: дата создания в 1С > 90 дней назад.
- Исключение спама и соискателей через HRGuard.
- Исключение дублей email и корпоративных доменов.
- Cross-System Conflict Guard: проверка отсутствия в DWH (clients_intel, onec_contacts, funnel_states).
- Сохранение курсора в data/cold_leads_cursor.json для продолжения на следующей неделе.
- Режим --dry-run по умолчанию (без записи в БД).
"""

import os
import sys
import json
import uuid
import re
import argparse
import datetime
import subprocess
from typing import List, Dict, Any, Set, Tuple
import requests

# 1. Загрузка переменных окружения
def load_env():
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "1c_odata", ".env"),
        os.path.join(os.getcwd(), ".env")
    ]
    for env_file in possible_paths:
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v

load_env()

# 2. Публичные домены
PUBLIC_EMAIL_DOMAINS = {
    "gmail.com", "mail.ru", "yandex.ru", "bk.ru", "inbox.ru", "list.ru",
    "rambler.ru", "ya.ru", "internet.ru", "icloud.com", "outlook.com", "hotmail.com"
}

# 3. HR-стоп слова и префиксы
HR_STOP_WORDS = [
    r'\bрезюме\b', r'\bваканси[яиюеейям]\b', r'\bсоискател[ьяейем]\b',
    r'\bотклик(?:а|ом|нули)?\b', r'\bинженер\s+по\s+качеству\b',
    r'\bqc\s+специалист\b', r'\bопыт\s+работы\b', r'\bищу\s+работу\b',
    r'\bтрудоустройств[оаеу]\b', r'\bсопроводительное\s+письмо\b',
    r'\bрассмотрите\s+мо[юе]\s+кандидатур[уа]\b', r'\bмо[её]\s+резюме\b',
    r'\bрезюме\s+во\s+вложении\b', r'\bhh\.ru\b', r'\bheadhunter\b',
    r'\bsuperjob\b', r'\brabota\.ru\b', r'\bavito\s+работа\b'
]
HR_EMAIL_PREFIXES = ["job@", "hr@", "resume@", "cv@", "rabota@", "recruitment@", "kadry@"]

def is_hr_or_job_seeker(email: str, name: str) -> Tuple[bool, str]:
    email_clean = (email or "").lower().strip()
    name_clean = (name or "").lower().strip()
    for prefix in HR_EMAIL_PREFIXES:
        if email_clean.startswith(prefix):
            return True, f"HR-префикс: {prefix}"
    for pat in HR_STOP_WORDS:
        if re.search(pat, name_clean, re.IGNORECASE):
            return True, f"Маркер резюме в имени: {pat}"
    return False, ""

def clean_email(email_str: str) -> str:
    if not email_str:
        return ""
    clean = email_str.strip().lower().strip(".,:;!?'\"<>()[]{}")
    # Простейшая валидация
    if "@" not in clean or "." not in clean.split("@")[-1]:
        return ""
    if any(clean.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"]):
        return ""
    return clean

def extract_contacts_from_1c_info(info_list: list) -> Tuple[List[str], List[str]]:
    emails = []
    phones = []
    if not info_list:
        return emails, phones
    for item in info_list:
        c_type = item.get("Тип", "")
        rep = item.get("Представление", "").strip()
        if not rep:
            continue
        if c_type == "АдресЭлектроннойПочты":
            for part in re.split(r'[;,\s]+', rep):
                e = clean_email(part)
                if e and e not in emails:
                    emails.append(e)
        elif c_type == "Телефон":
            for part in re.split(r'[;,\s]+', rep):
                p = part.strip()
                if p and len(p) >= 7 and p not in phones:
                    phones.append(p)
    return emails, phones

def fetch_existing_dwh_emails() -> Tuple[Set[str], Set[str]]:
    """
    Получает за 1 SSH-вызов все известные email и корпоративные домены из DWH на VPS.
    """
    sql = """
    COPY (
        SELECT DISTINCT lower(email) FROM (
            SELECT email FROM clients_intel WHERE email IS NOT NULL AND email != ''
            UNION
            SELECT client_email as email FROM reactivation_funnel_states WHERE client_email IS NOT NULL
            UNION
            SELECT client_email as email FROM client_reactivation_history WHERE client_email IS NOT NULL
            UNION
            SELECT unnest(emails) as email FROM onec_contacts WHERE emails IS NOT NULL
        ) t
    ) TO STDOUT;
    """
    cmd = [
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "vps",
        f"docker exec -i pgvector-db psql -U vector_user -d marketing_db -Atc \"{sql}\""
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"[ERROR] Не удалось подключиться к DWH через SSH: {res.stderr}")
        sys.exit(1)
        
    emails = set()
    domains = set()
    for line in res.stdout.splitlines():
        e = line.strip().lower()
        if e and "@" in e:
            emails.add(e)
            dom = e.split("@")[-1]
            if dom not in PUBLIC_EMAIL_DOMAINS:
                domains.add(dom)
    return emails, domains

def get_cursor_file_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "cold_leads_cursor.json")

def load_cursor() -> Dict[str, Any]:
    path = get_cursor_file_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"skip_offset": 0, "total_ingested": 0, "last_ingested_at": None}

def save_cursor(cursor: Dict[str, Any]):
    path = get_cursor_file_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cursor, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Импорт холодных лидов из 1С:УНФ в DWH для реанимации")
    parser.add_argument("--batch-size", type=int, default=100, help="Количество контактов в одном батче (по умолчанию 100)")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Режим симуляции (без записи в DWH)")
    parser.add_argument("--commit", action="store_true", default=False, help="Реальная запись в DWH (marketing_db)")
    parser.add_argument("--reset-cursor", action="store_true", default=False, help="Сбросить курсор на начало")
    args = parser.parse_args()

    # По умолчанию если не указан --commit, включаем --dry-run
    is_dry_run = not args.commit

    print("=" * 80)
    print(" PIPELINE: ИМПОРТ ХОЛОДНЫХ ЛИДОВ 1С:УНФ -> DWH CLIENT_INTEL")
    print(f" Режим: {'[DRY-RUN] (Безопасная симуляция)' if is_dry_run else '[COMMIT] (БОЕВАЯ ЗАПИСЬ В БАЗУ ДАННЫХ)'}")
    print(f" Размер батча: {args.batch_size} лидов")
    print("=" * 80)

    # 1. Загрузка курсора
    cursor = load_cursor()
    if args.reset_cursor:
        cursor = {"skip_offset": 0, "total_ingested": 0, "last_ingested_at": None}
        print(" [КУРСОР] Сброшен на 0.")
    skip_offset = cursor.get("skip_offset", 0)
    print(f" [КУРСОР] Текущее смещение: skip = {skip_offset}, всего ранее импортировано: {cursor.get('total_ingested', 0)}")

    # 2. Получение существующих email из DWH
    print(" [1/3] Запрос существующих контактов из DWH на VPS...")
    dwh_emails, dwh_domains = fetch_existing_dwh_emails()
    print(f"       Загружено {len(dwh_emails)} существующих email и {len(dwh_domains)} доменов из DWH.")

    # 3. Подключение к 1C OData
    print(" [2/3] Подключение к 1С:УНФ OData (Catalog_Лиды)...")
    odata_url = os.getenv("ONEC_ODATA_URL", "").rstrip("/")
    if not odata_url:
        print("[ERROR] ONEC_ODATA_URL не задан в .env!")
        sys.exit(1)
    leads_endpoint = f"{odata_url}/Catalog_Лиды"
    auth = (os.getenv("ONEC_ODATA_USER", ""), os.getenv("ONEC_ODATA_PASSWORD", ""))
    
    # Порог неактивности (90 дней назад)
    inactivity_threshold = datetime.datetime.now() - datetime.timedelta(days=90)
    print(f"       Фильтр по дате создания: старше {inactivity_threshold.strftime('%Y-%m-%d')} (>90 дней)")

    selected_candidates = []
    stats = {
        "fetched": 0,
        "skipped_deleted": 0,
        "skipped_too_recent": 0,
        "skipped_no_email": 0,
        "skipped_already_in_dwh": 0,
        "skipped_domain_collision": 0,
        "skipped_hr": 0,
        "selected": 0
    }

    current_skip = skip_offset
    page_size = 100
    
    batch_domains_seen = set()
    batch_emails_seen = set()

    while len(selected_candidates) < args.batch_size:
        params = {
            "$format": "json",
            "$skip": current_skip,
            "$top": page_size,
            "$orderby": "Ref_Key asc"
        }
        try:
            resp = requests.get(leads_endpoint, auth=auth, params=params, timeout=25)
            resp.raise_for_status()
            items = resp.json().get("value", [])
        except Exception as e:
            print(f"[ERROR] Сбой OData при skip={current_skip}: {e}")
            break

        if not items:
            print(" [INFO] Достигнут конец каталога лидов в 1С.")
            break

        stats["fetched"] += len(items)

        for lead in items:
            current_skip += 1

            # 1. Пометка удаления
            if lead.get("DeletionMark", False):
                stats["skipped_deleted"] += 1
                continue

            # 2. Проверка даты создания
            d_val = lead.get("ДатаСоздания")
            lead_date = None
            if d_val and not str(d_val).startswith("0001"):
                try:
                    lead_date = datetime.datetime.fromisoformat(str(d_val).replace("Z", ""))
                except Exception:
                    pass
            
            # Если дата создания свежее 90 дней — пропускаем
            if lead_date and lead_date > inactivity_threshold:
                stats["skipped_too_recent"] += 1
                continue

            # 3. Извлечение контактов
            c_info = lead.get("КонтактнаяИнформация", [])
            emails, phones = extract_contacts_from_1c_info(c_info)
            if not emails:
                stats["skipped_no_email"] += 1
                continue

            primary_email = emails[0]
            lead_name = lead.get("Description", "").strip() or "Лид без названия"

            # 4. HR-фильтр
            is_hr, hr_reason = is_hr_or_job_seeker(primary_email, lead_name)
            if is_hr:
                stats["skipped_hr"] += 1
                continue

            # 5. Проверка наличия в DWH
            if primary_email in dwh_emails or primary_email in batch_emails_seen:
                stats["skipped_already_in_dwh"] += 1
                continue

            # 6. Проверка домена компании
            dom = primary_email.split("@")[-1]
            if dom not in PUBLIC_EMAIL_DOMAINS:
                if dom in dwh_domains or dom in batch_domains_seen:
                    stats["skipped_domain_collision"] += 1
                    continue
                batch_domains_seen.add(dom)

            batch_emails_seen.add(primary_email)

            # Кандидат утвержден!
            contact_name = lead.get("КонтактноеЛицо") or "Контактное лицо"
            if isinstance(contact_name, dict):
                contact_name = contact_name.get("Description", "Контактное лицо")
            
            created_str = lead_date.strftime("%Y-%m-%d") if lead_date else "Не указана"

            candidate = {
                "ref_key": lead.get("Ref_Key"),
                "company_name": lead_name,
                "contact_name": str(contact_name),
                "email": primary_email,
                "phone": phones[0] if phones else "",
                "created_at_str": created_str,
                "inn": lead.get("ИНН", ""),
                "raw_lead": lead
            }
            selected_candidates.append(candidate)
            stats["selected"] += 1

            if len(selected_candidates) >= args.batch_size:
                break

    print(f"\n [ИТОГИ ВЫБОРКИ]:")
    print(f" - Всего просканировано лидов 1С: {stats['fetched']}")
    print(f" - Пропущено (помечены на удаление): {stats['skipped_deleted']}")
    print(f" - Пропущено (свежее 90 дней): {stats['skipped_too_recent']}")
    print(f" - Пропущено (нет email): {stats['skipped_no_email']}")
    print(f" - Пропущено (уже в DWH): {stats['skipped_already_in_dwh']}")
    print(f" - Пропущено (коллизия домена компании): {stats['skipped_domain_collision']}")
    print(f" - Пропущено (HR / соискатели): {stats['skipped_hr']}")
    print(f" -> ОТОБРАНО ДЛЯ ИМПОРТА: {len(selected_candidates)} лидов")
    print("-" * 80)

    # 4. Вывод таблицы отобранных кандидатов
    print(f"\n{'№':<4} | {'Компания / Лид':<32} | {'Email':<28} | {'Дата 1С':<10} | {'Телефон':<15}")
    print("-" * 95)
    for idx, c in enumerate(selected_candidates, 1):
        comp = (c['company_name'][:30] + '..') if len(c['company_name']) > 32 else c['company_name']
        em = (c['email'][:26] + '..') if len(c['email']) > 28 else c['email']
        ph = c['phone'][:15]
        print(f"{idx:<4} | {comp:<32} | {em:<28} | {c['created_at_str']:<10} | {ph:<15}")

    # 5. Применение или завершение
    if is_dry_run:
        print("\n" + "=" * 80)
        print(" [DRY-RUN УСПЕШНО ЗАВЕРШЕН]")
        print(" Данные проверены и отфильтрованы, но в базу DWH НЕ записаны.")
        print(f" Для боевого импорта и обновления курсора перезапустите команду с флагом --commit:")
        print(f" py projects/lead_reactivation/scripts/ingest_1c_cold_leads.py --commit --batch-size {args.batch_size}")
        print("=" * 80)
        return

    # 6. БОЕВОЙ ИМПОРТ (--commit)
    print("\n [3/3] Запись 100 кандидатов в DWH (onec_owners, onec_contacts, clients_intel)...")
    
    # Формируем SQL транзакцию
    sql_statements = ["BEGIN;"]
    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')

    for c in selected_candidates:
        lead_ref = c["ref_key"]
        lead_uuid = uuid.UUID(lead_ref)
        synth_contact_uuid = uuid.uuid5(namespace, f"{lead_ref}_{c['email']}")
        
        # Экранирование строк для SQL
        comp_name_esc = c["company_name"].replace("'", "''")
        contact_name_esc = c["contact_name"].replace("'", "''")
        email_esc = c["email"].replace("'", "''")
        phone_esc = c["phone"].replace("'", "''")
        inn_esc = (c["inn"] or "").replace("'", "''")
        raw_json_esc = json.dumps(c["raw_lead"], ensure_ascii=False).replace("'", "''")
        
        ai_summary_dict = {
            "contact_summary": {
                "history_and_notes": "Холодный лид из 1С:УНФ (старше 90 дней).",
                "timeline": [],
                "skus_and_amounts": [],
                "last_managers": [],
                "client_type": "cold_lead",
                "next_action_recommendation": "Первое холодное письмо-реанимация"
            },
            "company_summary": {
                "history_and_notes": "Нет истории переписки по компании."
            }
        }
        ai_summary_esc = json.dumps(ai_summary_dict, ensure_ascii=False).replace("'", "''")

        # 1. Upsert в onec_owners
        sql_owners = f"""
        INSERT INTO onec_owners (
            owner_entity, owner_ref_key, owner_name, owner_inn, owner_is_buyer, owner_is_junk,
            owner_search_emails, owner_search_phones, raw_payload, fetched_at
        ) VALUES (
            'Catalog_Лиды', '{lead_uuid}', '{comp_name_esc}', '{inn_esc}', false, false,
            ARRAY['{email_esc}'], {f"ARRAY['{phone_esc}']" if phone_esc else "ARRAY[]::text[]"},
            '{raw_json_esc}'::jsonb, NOW()
        ) ON CONFLICT (owner_entity, owner_ref_key) DO UPDATE SET
            owner_name = EXCLUDED.owner_name,
            owner_search_emails = array_cat(onec_owners.owner_search_emails, ARRAY['{email_esc}']),
            fetched_at = NOW();
        """
        sql_statements.append(sql_owners)

        # 2. Upsert в onec_contacts
        sql_contacts = f"""
        INSERT INTO onec_contacts (
            contact_entity, contact_ref_key, owner_entity, owner_ref_key, contact_name,
            emails, phones, raw_payload, fetched_at, is_synthetic, contact_is_junk
        ) VALUES (
            'Synthetic', '{synth_contact_uuid}', 'Catalog_Лиды', '{lead_uuid}', '{contact_name_esc}',
            ARRAY['{email_esc}'], {f"ARRAY['{phone_esc}']" if phone_esc else "ARRAY[]::text[]"},
            '{raw_json_esc}'::jsonb, NOW(), true, false
        ) ON CONFLICT (contact_entity, contact_ref_key) DO UPDATE SET
            emails = EXCLUDED.emails,
            fetched_at = NOW();
        """
        sql_statements.append(sql_contacts)

        # 3. Upsert в clients_intel
        sql_intel = f"""
        INSERT INTO clients_intel (
            email, company_name, inn, client_type, ai_summary,
            skus_and_amounts, emails_list, timeline, emails_count, updated_at
        ) VALUES (
            '{email_esc}', '{comp_name_esc}', {f"'{inn_esc}'" if inn_esc else "NULL"},
            'cold_lead', '{ai_summary_esc}',
            '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, 0, NOW()
        ) ON CONFLICT (email) DO UPDATE SET
            client_type = 'cold_lead',
            ai_summary = EXCLUDED.ai_summary,
            updated_at = NOW();
        """
        sql_statements.append(sql_intel)

    sql_statements.append("COMMIT;")
    full_sql = "\n".join(sql_statements)

    # Выполняем SQL на VPS за 1 SSH-сессию через STDIN
    cmd = [
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "vps",
        "docker exec -i pgvector-db psql -U vector_user -d marketing_db -v ON_ERROR_STOP=1"
    ]
    res = subprocess.run(cmd, input=full_sql, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"[ERROR] Сбой выполнения SQL в DWH:\n{res.stderr}")
        sys.exit(1)

    print(" [OK] Все 100 записей успешно зафиксированы в DWH (onec_owners, onec_contacts, clients_intel)!")

    # Обновление курсора
    cursor["skip_offset"] = current_skip
    cursor["total_ingested"] = cursor.get("total_ingested", 0) + len(selected_candidates)
    cursor["last_ingested_at"] = datetime.datetime.now().isoformat()
    save_cursor(cursor)
    print(f" [КУРСОР] Обновлен: новое смещение skip = {current_skip}, всего импортировано = {cursor['total_ingested']}.")
    print("=" * 80)

if __name__ == "__main__":
    main()
