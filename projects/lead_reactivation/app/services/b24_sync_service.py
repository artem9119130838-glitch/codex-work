import os
import re
import requests
from typing import Optional, Dict, Any, Tuple
try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("b24_sync_service")

# Default manager fallback (Артем ID 1)
DEFAULT_RESPONSIBLE_ID = 1

# Mapping 1C manager names to Bitrix24 User IDs
MANAGER_B24_MAP = {
    "артем": 1,
    "артём": 1,
    "азат": 29,
    "мисс ван": 25,
    "ван": 25,
    "михаил": 19,
    "максим": 1,
}

def get_b24_webhook() -> str:
    webhook = os.getenv("BITRIX24_WEBHOOK_URL", "")
    if not webhook:
        # Check potential env files
        for env_path in ["projects/1c_odata/.env", ".env", "C:/Codex/.env"]:
            if os.path.exists(env_path):
                with open(env_path, encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("BITRIX24_WEBHOOK_URL="):
                            webhook = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                            break
            if webhook:
                break
    if webhook and not webhook.endswith("/"):
        webhook += "/"
    return webhook


def resolve_responsible_id(manager_name: Optional[str] = None) -> int:
    if not manager_name:
        return DEFAULT_RESPONSIBLE_ID
    clean = manager_name.strip().lower()
    for key, uid in MANAGER_B24_MAP.items():
        if key in clean:
            return uid
    return DEFAULT_RESPONSIBLE_ID


def find_b24_contact_by_email(webhook: str, email: str) -> Optional[Dict[str, Any]]:
    clean_email = email.strip().lower()
    try:
        r = requests.post(f"{webhook}crm.contact.list", json={
            "filter": {"EMAIL": clean_email},
            "select": ["ID", "NAME", "LAST_NAME", "COMPANY_ID", "ASSIGNED_BY_ID", "EMAIL"]
        }, timeout=10).json()
        contacts = r.get("result", [])
        if contacts:
            return contacts[0]
    except Exception as e:
        logger.error(f"[B24-SYNC] Ошибка поиска контакта по {clean_email}: {e}")
    return None


def find_b24_company_by_inn(webhook: str, inn: str) -> Optional[Dict[str, Any]]:
    clean_inn = inn.strip()
    if not clean_inn or len(clean_inn) not in (10, 12) or not clean_inn.isdigit():
        return None
    try:
        # Search via crm.requisite.list by RQ_INN
        r = requests.post(f"{webhook}crm.requisite.list", json={
            "filter": {"RQ_INN": clean_inn, "ENTITY_TYPE_ID": 4},
            "select": ["ID", "ENTITY_ID"]
        }, timeout=10).json()
        reqs = r.get("result", [])
        if reqs:
            company_id = reqs[0].get("ENTITY_ID")
            r_cmp = requests.post(f"{webhook}crm.company.get", json={"id": company_id}, timeout=10).json()
            return r_cmp.get("result")
    except Exception as e:
        logger.error(f"[B24-SYNC] Ошибка поиска компании по ИНН {clean_inn}: {e}")
    return None


def find_b24_company_by_title(webhook: str, title: str) -> Optional[Dict[str, Any]]:
    clean_title = re.sub(r'[\'\"«»“”]', '', title).strip()
    if not clean_title or len(clean_title) < 5:
        return None
    try:
        r = requests.post(f"{webhook}crm.company.list", json={
            "filter": {"TITLE": clean_title},
            "select": ["ID", "TITLE", "ASSIGNED_BY_ID"]
        }, timeout=10).json()
        cmps = r.get("result", [])
        if cmps:
            return cmps[0]
    except Exception as e:
        logger.error(f"[B24-SYNC] Ошибка поиска компании по названию {clean_title}: {e}")
    return None


def ensure_b24_entities_for_reactivation(
    email: str,
    contact_name: Optional[str] = None,
    company_name: Optional[str] = None,
    inn: Optional[str] = None,
    manager_name: Optional[str] = None,
    dry_run: bool = False
) -> Tuple[Optional[int], Optional[int]]:
    """
    Гарантирует наличие сущностей (Компания + Контакт) в Битрикс24 перед генерацией/отправкой письма.
    Возвращает (contact_id, company_id).
    """
    webhook = get_b24_webhook()
    if not webhook:
        logger.warning("[B24-SYNC] BITRIX24_WEBHOOK_URL не найден, синхронизация пропущена.")
        return None, None

    clean_email = email.strip().lower()
    responsible_id = resolve_responsible_id(manager_name)

    # 1. Поиск контакта
    existing_contact = find_b24_contact_by_email(webhook, clean_email)
    contact_id = int(existing_contact["ID"]) if existing_contact else None
    company_id = int(existing_contact["COMPANY_ID"]) if existing_contact and existing_contact.get("COMPANY_ID") else None

    # 2. Поиск или создание Компании (если есть ИНН или валидное наименование)
    if not company_id and inn:
        existing_company = find_b24_company_by_inn(webhook, inn)
        if existing_company:
            company_id = int(existing_company["ID"])

    if not company_id and company_name and not inn:
        existing_company = find_b24_company_by_title(webhook, company_name)
        if existing_company:
            company_id = int(existing_company["ID"])

    # Создание Компании, если не найдена и есть данные
    if not company_id and (inn or (company_name and len(company_name.strip()) >= 5)):
        title = company_name.strip() if company_name else f"Компания (ИНН {inn})"
        if dry_run:
            logger.info(f"[B24-SYNC] [DRY-RUN] Будет создана Компания '{title}' (ИНН: {inn or 'нет'}), отв: {responsible_id}")
            company_id = 999999
        else:
            try:
                r_create_cmp = requests.post(f"{webhook}crm.company.add", json={
                    "fields": {
                        "TITLE": title,
                        "COMPANY_TYPE": "CUSTOMER",
                        "ASSIGNED_BY_ID": responsible_id,
                        "OPENED": "Y"
                    }
                }, timeout=10).json()
                company_id = r_create_cmp.get("result")
                logger.info(f"[B24-SYNC] Создана Компания #{company_id}: '{title}'")

                # Добавляем реквизит ИНН
                if company_id and inn:
                    requests.post(f"{webhook}crm.requisite.add", json={
                        "fields": {
                            "ENTITY_TYPE_ID": 4, # Company
                            "ENTITY_ID": company_id,
                            "PRESET_ID": 1, # Юрлицо РФ
                            "NAME": "Основные реквизиты",
                            "RQ_INN": inn.strip()
                        }
                    }, timeout=10)
            except Exception as e:
                logger.error(f"[B24-SYNC] Ошибка создания Компании в Б24: {e}")

    # 3. Создание или обновление Контакта
    c_name = contact_name.strip() if contact_name else clean_email
    if not contact_id:
        if dry_run:
            logger.info(f"[B24-SYNC] [DRY-RUN] Будет создан Контакт '{c_name}', email={clean_email}, company_id={company_id}, отв: {responsible_id}")
            contact_id = 888888
        else:
            try:
                contact_fields = {
                    "NAME": c_name,
                    "TYPE_ID": "CLIENT",
                    "ASSIGNED_BY_ID": responsible_id,
                    "OPENED": "Y",
                    "EMAIL": [{"VALUE": clean_email, "VALUE_TYPE": "WORK"}]
                }
                if company_id and company_id != 999999:
                    contact_fields["COMPANY_ID"] = company_id

                r_ct = requests.post(f"{webhook}crm.contact.add", json={"fields": contact_fields}, timeout=10).json()
                contact_id = r_ct.get("result")
                logger.info(f"[B24-SYNC] Создан Контакт #{contact_id}: '{c_name}' (Email: {clean_email})")
            except Exception as e:
                logger.error(f"[B24-SYNC] Ошибка создания Контакта в Б24: {e}")
    else:
        # Если контакт уже был, но не был привязан к компании
        if company_id and company_id != 999999 and not existing_contact.get("COMPANY_ID"):
            if dry_run:
                logger.info(f"[B24-SYNC] [DRY-RUN] Контакт #{contact_id} будет привязан к Компании #{company_id}")
            else:
                try:
                    requests.post(f"{webhook}crm.contact.update", json={
                        "id": contact_id,
                        "fields": {"COMPANY_ID": company_id}
                    }, timeout=10)
                    logger.info(f"[B24-SYNC] Контакт #{contact_id} привязан к Компании #{company_id}")
                except Exception as e:
                    logger.error(f"[B24-SYNC] Ошибка привязки Контакта #{contact_id} к Компании: {e}")

    return contact_id, company_id


def register_b24_email_activity(
    contact_id: int,
    company_id: Optional[int],
    subject: str,
    body_html: str,
    recipient_email: str,
    assigned_by_id: int = DEFAULT_RESPONSIBLE_ID,
    dry_run: bool = False
) -> Optional[int]:
    """
    Регистрирует исходящее письмо в таймлайне Битрикс24 (crm.activity.add).
    """
    webhook = get_b24_webhook()
    if not webhook or not contact_id:
        return None

    clean_email = recipient_email.strip().lower()

    if dry_run:
        logger.info(f"[B24-SYNC] [DRY-RUN] Будет зарегистрировано исходящее дело в таймлайне Контакта #{contact_id}: Тема='{subject}'")
        return 777777

    try:
        bindings = [{"OWNER_TYPE_ID": 3, "OWNER_ID": contact_id}]
        if company_id and company_id != 999999:
            bindings.append({"OWNER_TYPE_ID": 4, "OWNER_ID": company_id})

        activity_payload = {
            "fields": {
                "TYPE_ID": 4, # EMAIL
                "PROVIDER_ID": "CRM_EMAIL",
                "PROVIDER_TYPE_ID": "EMAIL",
                "DIRECTION": 2, # Исходящее
                "COMPLETED": "Y",
                "STATUS": 2, # Выполнено
                "SUBJECT": subject,
                "DESCRIPTION": body_html,
                "DESCRIPTION_TYPE": 3, # HTML
                "RESPONSIBLE_ID": assigned_by_id,
                "OWNER_TYPE_ID": 3, # Привязка к Контакту
                "OWNER_ID": contact_id,
                "COMMUNICATIONS": [
                    {
                        "VALUE": clean_email,
                        "ENTITY_ID": contact_id,
                        "ENTITY_TYPE_ID": 3,
                        "TYPE": "EMAIL"
                    }
                ],
                "BINDINGS": bindings
            }
        }
        r = requests.post(f"{webhook}crm.activity.add", json=activity_payload, timeout=10).json()
        act_id = r.get("result")
        if act_id:
            logger.info(f"[B24-SYNC] Исходящее письмо успешно зарегистрировано в таймлайне Контакта #{contact_id} (Activity #{act_id})")
            return int(act_id)
        else:
            logger.error(f"[B24-SYNC] Ошибка crm.activity.add: {r}")
    except Exception as e:
        logger.error(f"[B24-SYNC] Исключение при регистрации email-активности: {e}")

    return None
