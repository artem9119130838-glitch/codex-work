import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text, or_
from loguru import logger
from app.db.models import ClientReactivationHistory, ReactivationFunnelState, EmailMessage, EmailMatchResult, OnecContact, OnecOwner

# Public email providers where domain-level cooldown must NOT be applied to all clients
PUBLIC_EMAIL_DOMAINS = {
    "gmail.com", "mail.ru", "yandex.ru", "bk.ru", "inbox.ru", "list.ru", 
    "rambler.ru", "ya.ru", "internet.ru", "icloud.com", "outlook.com", "hotmail.com"
}

class CooldownGuard:
    @staticmethod
    def is_email_on_cooldown(db: Session, email: str, days: int = 21) -> tuple[bool, str]:
        """
        Проверяет, было ли сгенерировано или отправлено письмо на этот конкретный email
        в течение последних N дней (по умолчанию 21 день).
        """
        threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        # 1. Проверка в истории реанимаций
        last_hist = db.query(ClientReactivationHistory).filter(
            ClientReactivationHistory.client_email == email,
            ClientReactivationHistory.sent_at >= threshold
        ).order_by(ClientReactivationHistory.sent_at.desc()).first()
        
        if last_hist:
            diff = (datetime.datetime.utcnow() - (last_hist.sent_at.replace(tzinfo=None) if last_hist.sent_at.tzinfo else last_hist.sent_at)).days
            return True, f"На адрес {email} уже генерировалось письмо {diff} дн. назад (кулдаун: {days} дн.)"
            
        return False, ""

    @staticmethod
    def has_pending_draft(db: Session, email: str) -> tuple[bool, str]:
        """
        Проверяет, есть ли по этому клиенту уже созданный, но еще не отправленный черновик в воронке.
        """
        active_draft = db.query(ReactivationFunnelState).filter(
            ReactivationFunnelState.client_email == email,
            ReactivationFunnelState.step_status == "draft_created"
        ).first()
        
        if active_draft:
            return True, f"Для {email} уже ожидает отправки черновик Шага {active_draft.current_step}"
            
        return False, ""

    @staticmethod
    def has_recent_correspondence(db: Session, email: str, owner_ref_key: str = None, days: int = 21) -> tuple[bool, str]:
        """
        Проверяет, была ли любая реальная переписка (входящая или исходящая)
        с этим адресом или компанией за последние N дней.
        """
        threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        # 1. Проверка прямых сообщений по email в email_messages
        recent_msg = db.query(EmailMessage).filter(
            EmailMessage.from_email == email,
            EmailMessage.is_junk == False,
            EmailMessage.received_at >= threshold
        ).order_by(EmailMessage.received_at.desc()).first()
        
        if recent_msg:
            diff = (datetime.datetime.utcnow() - (recent_msg.received_at.replace(tzinfo=None) if recent_msg.received_at.tzinfo else recent_msg.received_at)).days
            return True, f"С адресом {email} была переписка {diff} дн. назад (письмо ID: {recent_msg.message_id})"
            
        # 2. Проверка через сопоставленные результаты 1С
        if owner_ref_key:
            recent_company_msg = db.execute(text("""
                SELECT m.message_id, m.received_at
                FROM email_messages m
                JOIN email_match_results r ON m.message_id = r.message_id
                WHERE r.owner_ref_key = :owner_key
                  AND m.is_junk = false
                  AND m.received_at >= :threshold
                ORDER BY m.received_at DESC
                LIMIT 1
            """), {"owner_key": owner_ref_key, "threshold": threshold}).first()
            
            if recent_company_msg:
                diff = (datetime.datetime.utcnow() - (recent_company_msg[1].replace(tzinfo=None) if recent_company_msg[1].tzinfo else recent_company_msg[1])).days
                return True, f"С компанией {owner_ref_key} была переписка {diff} дн. назад"
                
        return False, ""

    @staticmethod
    def is_company_on_cooldown(db: Session, owner_ref_key: str = None, email: str = "", days: int = 21) -> tuple[bool, str]:
        """
        Проверяет, отправлялись ли письма другим контактам этой же компании за последние N дней,
        чтобы не писать разным сотрудникам одной компании одновременно.
        """
        threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        # 1. Проверка по 1С owner_ref_key
        if owner_ref_key:
            # Находим все emails, принадлежащие этой компании в 1С
            contacts = db.query(OnecContact).filter(OnecContact.owner_ref_key == owner_ref_key).all()
            company_emails = set()
            for c in contacts:
                if c.emails:
                    for e in c.emails:
                        company_emails.add(e.lower().strip())
                        
            # Исключаем сам проверяемый email
            other_emails = [e for e in company_emails if e != email.lower().strip()]
            if other_emails:
                recent_other = db.query(ClientReactivationHistory).filter(
                    ClientReactivationHistory.client_email.in_(other_emails),
                    ClientReactivationHistory.sent_at >= threshold
                ).first()
                if recent_other:
                    diff = (datetime.datetime.utcnow() - (recent_other.sent_at.replace(tzinfo=None) if recent_other.sent_at.tzinfo else recent_other.sent_at)).days
                    return True, f"Коллеге из той же компании ({recent_other.client_email}) уже отправлялось письмо {diff} дн. назад"

        # 2. Проверка по корпоративному домену (если домен не публичный)
        if email and "@" in email:
            domain = email.split("@")[-1].lower().strip()
            if domain and domain not in PUBLIC_EMAIL_DOMAINS:
                recent_domain = db.execute(text("""
                    SELECT client_email, sent_at
                    FROM client_reactivation_history
                    WHERE client_email LIKE :domain_pattern
                      AND client_email != :current_email
                      AND sent_at >= :threshold
                    ORDER BY sent_at DESC
                    LIMIT 1
                """), {
                    "domain_pattern": f"%@{domain}",
                    "current_email": email,
                    "threshold": threshold
                }).first()
                
                if recent_domain:
                    diff = (datetime.datetime.utcnow() - (recent_domain[1].replace(tzinfo=None) if recent_domain[1].tzinfo else recent_domain[1])).days
                    return True, f"На домен @{domain} ({recent_domain[0]}) уже отправлялось письмо {diff} дн. назад"

        return False, ""

    @classmethod
    def can_send_reactivation(cls, db: Session, email: str, owner_ref_key: str = None, days: int = 21, check_company: bool = True) -> tuple[bool, str]:
        """
        Агрегированная проверка всех факторов защиты от спама и дублей.
        Возвращает (True, "OK") или (False, причина_отказа).
        """
        # 1. Проверка ожидающего черновика
        has_draft, reason = cls.has_pending_draft(db, email)
        if has_draft:
            return False, reason
            
        # 2. Проверка прямого кулдауна email
        on_cd, reason = cls.is_email_on_cooldown(db, email, days=days)
        if on_cd:
            return False, reason
            
        # 3. Проверка недавней переписки
        has_corr, reason = cls.has_recent_correspondence(db, email, owner_ref_key=owner_ref_key, days=days)
        if has_corr:
            return False, reason
            
        # 4. Проверка кулдауна на уровне компании и домена
        if check_company:
            comp_cd, reason = cls.is_company_on_cooldown(db, owner_ref_key=owner_ref_key, email=email, days=days)
            if comp_cd:
                return False, reason
                
        return True, "OK"
