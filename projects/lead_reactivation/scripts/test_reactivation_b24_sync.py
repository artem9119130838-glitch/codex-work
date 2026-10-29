import os
import sys
import argparse
import datetime
from typing import Optional

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("test_reactivation_b24_sync")

from app.services.b24_sync_service import ensure_b24_entities_for_reactivation, register_b24_email_activity, resolve_responsible_id

def run_test_sync(email: str, company_name: Optional[str] = None, inn: Optional[str] = None, contact_name: Optional[str] = None, manager_name: Optional[str] = None, dry_run: bool = True):
    logger.info(f"=== ТЕСТ СИНХРОНИЗАЦИИ CRM РЕАНИМАЦИИ (Режим: {'DRY-RUN' if dry_run else 'APPLY'}) ===")
    logger.info(f"Целевой email: {email}")
    logger.info(f"Компания: {company_name or 'Не указана'}, ИНН: {inn or 'Не указан'}, Контакт: {contact_name or 'Не указан'}")

    # 1. Синхронизация сущностей (Компания + Контакт)
    contact_id, company_id = ensure_b24_entities_for_reactivation(
        email=email,
        contact_name=contact_name,
        company_name=company_name,
        inn=inn,
        manager_name=manager_name,
        dry_run=dry_run
    )

    logger.info(f"[ИТОГ CRM СИНХРОНИЗАЦИИ] Contact ID: {contact_id}, Company ID: {company_id}")

    # 2. Пример регистрации исходящего письма в таймлайне Б24
    test_subject = f"Сотрудничество по поставкам промышленного оборудования: {company_name or email}"
    test_body = f"""<p>Добрый день{', ' + contact_name if contact_name else ''}!</p>
<p>Ранее мы обсуждали поставки промышленного оборудования. Направляем обновленную презентацию компании и каталог прямых поставок из Китая.</p>
<p>С уважением, Артем<br>LongWang (+7 812 509-1245)</p>"""

    responsible_id = resolve_responsible_id(manager_name)
    act_id = register_b24_email_activity(
        contact_id=contact_id,
        company_id=company_id,
        subject=test_subject,
        body_html=test_body,
        recipient_email=email,
        assigned_by_id=responsible_id,
        dry_run=dry_run
    )

    logger.info(f"[ИТОГ АКТИВНОСТИ] Activity ID: {act_id}")
    return contact_id, company_id, act_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Тест синхронизации Битрикс24 перед реанимацией спящих клиентов")
    parser.add_argument("--email", type=str, default="elm_2021orel@mail.ru", help="Email клиента")
    parser.add_argument("--company", type=str, default=None, help="Наименование компании")
    parser.add_argument("--inn", type=str, default=None, help="ИНН компании")
    parser.add_argument("--contact", type=str, default=None, help="ФИО контакта")
    parser.add_argument("--manager", type=str, default="Артем", help="Ответственный менеджер из 1С")
    parser.add_argument("--apply", action="store_true", help="Боевой запуск (без dry-run)")

    args = parser.parse_args()
    is_dry_run = not args.apply

    run_test_sync(
        email=args.email,
        company_name=args.company,
        inn=args.inn,
        contact_name=args.contact,
        manager_name=args.manager,
        dry_run=is_dry_run
    )
