import datetime
from imap_tools import MailBox, AND
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.db.models import EmailMessage, EmailMatchResult, OnecOwner, OnecContact
from sqlalchemy import text
import re
import io
import pdfplumber
import docx
from app.services.text_cleaner import clean_email_body

PUBLIC_DOMAINS = {"mail.ru", "gmail.com", "yandex.ru", "ya.ru", "bk.ru", "inbox.ru", "list.ru", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"}

def extract_attachment_text(msg) -> str:
    extracted_texts = []
    for att in msg.attachments:
        filename = att.filename.lower() if att.filename else ""
        if not filename:
            continue
            
        try:
            if filename.endswith(".pdf"):
                with pdfplumber.open(io.BytesIO(att.payload)) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    if text.strip():
                        extracted_texts.append(f"--- Вложение {att.filename} ---\n{text.strip()}")
            elif filename.endswith(".docx"):
                doc = docx.Document(io.BytesIO(att.payload))
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                if text.strip():
                    extracted_texts.append(f"--- Вложение {att.filename} ---\n{text.strip()}")
        except Exception as e:
            logger.warning(f"Failed to parse attachment {att.filename}: {e}")
            
    return "\n\n".join(extracted_texts)

def extract_real_email(from_email: str, text_body: str) -> str:
    from_email = from_email.lower().strip()
    if from_email.endswith("@longwang.ru"):
        match = re.search(r"От кого:.*?<([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)>", text_body, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        match2 = re.search(r"From:.*?<([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)>", text_body, re.IGNORECASE)
        if match2:
            return match2.group(1).lower()
    return from_email

class ImapService:
    def __init__(self, db: Session):
        self.db = db
        
    def fetch_and_match_emails(self, imap_user: str = None, imap_password: str = None, date_since: datetime.date = None, date_to: datetime.date = None, limit: int = None, focus_domains: list = None):
        """
        Connects to IMAP, fetches emails since the specified date from INBOX,
        folders containing "запросы", and folders containing "sent"/"отправленные",
        saves them to email_messages, and performs matching.
        Operates in strictly read-only mode (does not mark as read).
        """
        user = imap_user or settings.IMAP_USER
        password = imap_password or settings.IMAP_PASSWORD
        imap_host = settings.IMAP_HOST or settings.IMAP_SERVER
        
        if not imap_host or not user or not password:
            logger.error("IMAP settings are not fully configured")
            return
            
        logger.info(f"Connecting to IMAP {imap_host} as {user}")
        try:
            with MailBox(imap_host).login(user, password) as mailbox:
                # 1. Get list of all folders
                all_folders = mailbox.folder.list()
                target_folders = []
                # Expanded whitelist based on user's mailbox structure
                allowed_keywords = {
                    "inbox", "запросы", "sent", "отправленные", 
                    "артем", "заявки с формы на проверку зан", "контроль", 
                    "первичные заявки с сайта", "ge", "персонал", 
                    "азат", "ген дир", "моп (i_li)", "пономарева", "сауле"
                }
                
                for folder in all_folders:
                    name_lower = folder.name.lower()
                    if any(kw in name_lower for kw in allowed_keywords):
                        target_folders.append(folder.name)
                
                logger.info(f"Identified target folders for {user}: {target_folders}")
                
                count = 0
                for folder_name in target_folders:
                    if limit and count >= limit:
                        break
                        
                    logger.info(f"Switching to folder '{folder_name}' for {user}")
                    mailbox.folder.set(folder_name)
                    
                    is_sent_folder = any(x in folder_name.lower() for x in ["sent", "отправленные"])
                    
                    if date_since and date_to:
                        criteria = AND(date_gte=date_since, date_lt=date_to)
                    elif date_since:
                        criteria = AND(date_gte=date_since)
                    elif date_to:
                        criteria = AND(date_lt=date_to)
                    else:
                        criteria = AND(all=True)
                    
                    # Fetch messages from current folder without bulk=True to prevent memory/timeout issues
                    for msg in mailbox.fetch(criteria, mark_seen=False, bulk=False):
                        if focus_domains:
                            client_email = msg.to[0].lower() if is_sent_folder and msg.to else msg.from_.lower()
                            client_domain = client_email.split("@")[-1] if "@" in client_email else ""
                            if client_domain not in focus_domains and client_email not in focus_domains:
                                continue

                        # Form unique message id to prevent collisions across folders
                        # For backwards compatibility with already fetched INBOX messages:
                        if folder_name == "INBOX":
                            message_id = msg.uid
                        else:
                            message_id = f"{user}_{folder_name}_{msg.uid}"
                            
                        existing_msg = self.db.query(EmailMessage).filter(EmailMessage.message_id == message_id).first()
                        if existing_msg:
                            continue
                            
                        # If it's sent folder, client is the recipient (to_email)
                        # Otherwise, client is the sender (from_)
                        if is_sent_folder:
                            client_email = msg.to[0] if msg.to else ""
                            client_name = msg.to_values[0].name if (msg.to_values and msg.to_values[0]) else ""
                        else:
                            client_email = msg.from_
                            client_name = msg.from_values.name if msg.from_values else ""
                            
                        subject = msg.subject
                        if is_sent_folder and not subject.startswith("Исх:"):
                            subject = f"Исх: {subject}"

                        logger.info(f"Processing new email in '{folder_name}' UID: {msg.uid} Client: {client_email} Subject: {subject}")
                        
                        new_email = EmailMessage(
                            message_id=message_id,
                            from_email=client_email,
                            from_name=client_name,
                            subject=subject,
                            received_at=msg.date,
                            source_mailbox=user,
                            raw_payload={
                                "text": msg.text,
                                "html": msg.html,
                                "folder": folder_name,
                                "is_sent": is_sent_folder,
                                "to": list(msg.to),
                                "from": msg.from_,
                                "attachments_text": extract_attachment_text(msg),
                                "cleaned_text": clean_email_body(msg.text, msg.html)
                            },
                            created_at=datetime.datetime.now(datetime.timezone.utc),
                            is_junk=False
                        )
                        self.db.add(new_email)
                        self.db.commit()
                        
                        self._match_email(new_email)
                        
                        count += 1
                        if limit and count >= limit:
                            logger.info(f"Reached fetch limit of {limit} messages for {user}. Stopping.")
                            break
                            
        except Exception as e:
            logger.error(f"Error during IMAP fetch for {user}: {e}")
            self.db.rollback()

    def run_rematch(self) -> dict:
        """
        Re-evaluates all emails that are currently in 'needs_review' or 'needs_review_domain' status,
        and not marked as junk.
        """
        matches = self.db.query(EmailMatchResult).join(
            EmailMessage, EmailMatchResult.message_id == EmailMessage.message_id
        ).filter(
            EmailMatchResult.decision.in_(['needs_review', 'needs_review_domain']),
            EmailMessage.is_junk == False
        ).all()
        
        if not matches:
            return {"status": "success", "rematched_count": 0, "message": "No emails to rematch"}
            
        rematched_count = 0
        for match in matches:
            email = self.db.query(EmailMessage).filter(EmailMessage.message_id == match.message_id).first()
            if email:
                logger.info(f"Rematching email {email.message_id}...")
                self._match_email(email)
                # We can check if it changed decision
                new_match = self.db.query(EmailMatchResult).filter(EmailMatchResult.message_id == email.message_id).first()
                if new_match and new_match.decision == 'matched':
                    rematched_count += 1
                    
        return {"status": "success", "rematched_count": rematched_count, "total_processed": len(matches)}

    def _match_email(self, email: EmailMessage):
        real_email = extract_real_email(email.from_email, email.raw_payload.get("text", ""))
        if not real_email:
            return
            
        # Update email with extracted real email (for Fwds) so grouping by from_email works correctly
        if email.from_email != real_email:
            email.from_email = real_email
            self.db.commit()
            
        # 1. Exact match in Contacts
        contact = self.db.query(OnecContact).filter(
            text(":email = ANY(emails)")
        ).params(email=real_email).first()
        
        if contact:
            self._save_match(email, "contact", "matched", "exact email match in contacts", owner_ref_key=contact.owner_ref_key, contact_ref_key=contact.contact_ref_key)
            return

        # 2. Exact match in Owners (company)
        owner = self.db.query(OnecOwner).filter(
            text(":email = ANY(owner_search_emails)")
        ).params(email=real_email).first()
        
        if owner:
            empty_contact = self.db.query(OnecContact).filter(
                OnecContact.owner_ref_key == owner.owner_ref_key,
                text("cardinality(emails) = 0 OR emails IS NULL")
            ).first()
            if empty_contact:
                self._save_match(email, "contact", "matched", "exact match in owner, linked to empty contact", owner_ref_key=owner.owner_ref_key, contact_ref_key=empty_contact.contact_ref_key)
            else:
                self._save_match(email, "owner", "matched", "exact email match in owner", owner_ref_key=owner.owner_ref_key)
            return
            
        # 3. Domain match
        domain = real_email.split("@")[-1] if "@" in real_email else ""
        if domain and domain not in PUBLIC_DOMAINS:
            owner_by_domain = self.db.query(OnecOwner).filter(
                text("EXISTS (SELECT 1 FROM unnest(owner_search_emails) as e WHERE e LIKE :domain_pattern)")
            ).params(domain_pattern=f"%@{domain}").first()
            
            if owner_by_domain:
                self._save_match(email, "none", "needs_review_domain", "domain match found", owner_ref_key=owner_by_domain.owner_ref_key)
                return

        # 4. No match
        self._save_match(email, "none", "needs_review", "no match found")
        
    def _save_match(self, email: EmailMessage, matched_level: str, decision: str, reason: str, owner_ref_key=None, contact_ref_key=None):
        # We also want to delete any existing match result if we are re-matching
        existing_match = self.db.query(EmailMatchResult).filter(EmailMatchResult.message_id == email.message_id).first()
        if existing_match:
            self.db.delete(existing_match)
            self.db.commit()

        extracted_company = None
        extracted_contact_name = None
        extracted_reason = None

        # If it's not a matched email, let's extract details
        if decision != "matched":
            # 1. Heuristics
            # Contact name from from_name
            raw_name = (email.from_name or "").strip()
            # Clean up raw_name from email or quotes
            raw_name = re.sub(r'[<"].*?[>"]', '', raw_name).strip()
            if not raw_name and email.from_email:
                raw_name = email.from_email.split('@')[0]
            extracted_contact_name = raw_name or "Неизвестно"

            # Company name from domain
            from_email = (email.from_email or "").strip().lower()
            if "@" in from_email:
                domain = from_email.split('@')[1]
                if domain not in PUBLIC_DOMAINS:
                    # e.g. way-trade.ru -> WAY-TRADE
                    comp_name = domain.split('.')[0].upper()
                    extracted_company = comp_name
                else:
                    extracted_company = "Неизвестно (личная почта)"
            else:
                extracted_company = "Неизвестно"

            extracted_reason = reason or "Не сопоставлено (нет контакта)"

        match = EmailMatchResult(
            message_id=email.message_id,
            matched_level=matched_level,
            decision=decision,
            decision_reason=reason,
            owner_ref_key=owner_ref_key,
            contact_ref_key=contact_ref_key,
            confidence=1.0 if decision == "matched" else 0.5,
            ai_processed=False,
            extracted_company=extracted_company,
            extracted_contact_name=extracted_contact_name,
            extracted_reason=extracted_reason
        )
        self.db.add(match)
        self.db.commit()
        logger.info(f"Email {email.message_id} -> {decision} ({reason}) [Extracted: {extracted_company} / {extracted_contact_name}]")
