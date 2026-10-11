import os
import sys
import json
from loguru import logger

# Add app to path
sys.path.insert(0, '/app')

from imap_tools import MailBox, AND
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import ClientReactivationHistory, ReactivationFunnelState, ClientIntel

def main():
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
            except Exception as e:
                pass
                
    targets_to_delete = {
        "belokobylskayavk@chkpz.ru": "Bounce letter (Undelivered Mail Returned to Sender)",
        "alexey.zelenskiy@trucksvostok.ru": "Auto-reply letter (Автоматический ответ)",
        "n.zamana@pharmasyntez.com": "Malformed subject (Обратный клапан RE: ООО «Лун-Ван» обратная связьпо поставке для Замана...)"
    }
    
    deleted_uids = []
    logger.info(f"Connecting to IMAP {user} at {imap_host} to remove defective drafts...")
    with MailBox(imap_host).login(user, password) as mailbox:
        draft_folder = None
        for f in mailbox.folder.list():
            fn_lower = f.name.lower()
            if fn_lower in ["drafts", "inbox.drafts", "черновики", "inbox.черновики"]:
                draft_folder = f.name
                break
        if not draft_folder:
            draft_folder = "Drafts"
            
        mailbox.folder.set(draft_folder)
        msgs = list(mailbox.fetch(reverse=True, mark_seen=False))
        logger.info(f"Total drafts found before deletion: {len(msgs)}")
        
        for msg in msgs:
            to_list = [t.lower().strip() for t in (msg.to or [])]
            for target_email, reason in targets_to_delete.items():
                if target_email in to_list:
                    logger.warning(f"Deleting draft UID {msg.uid} for {target_email} | Subject: '{msg.subject}' | Reason: {reason}")
                    mailbox.delete([msg.uid])
                    deleted_uids.append(msg.uid)
                    break
                    
    logger.info(f"Successfully deleted {len(deleted_uids)} defective drafts from IMAP {draft_folder}!")
    
    # DB cleanup
    db = SessionLocal()
    try:
        # 1. Handle bounced contact
        bounced_email = "belokobylskayavk@chkpz.ru"
        intel = db.query(ClientIntel).filter(ClientIntel.email == bounced_email).first()
        if intel:
            intel.client_type = "BOUNCE_INVALID"
            logger.info(f"Marked {bounced_email} in ClientIntel as BOUNCE_INVALID.")
            
        # Remove funnel state for bounce so it never runs again
        db.query(ReactivationFunnelState).filter(ReactivationFunnelState.client_email == bounced_email).delete()
        
        # 2. Reset step 2 records for the other 2 contacts
        for email in ["alexey.zelenskiy@trucksvostok.ru", "n.zamana@pharmasyntez.com"]:
            fs = db.query(ReactivationFunnelState).filter(ReactivationFunnelState.client_email == email).first()
            if fs and fs.current_step > 1:
                logger.info(f"Resetting {email} funnel step from {fs.current_step} to 1 (step_status='draft_created')")
                fs.current_step = 1
                fs.step_status = "draft_created"
                
        db.commit()
        logger.info("Database records successfully updated.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed updating DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
