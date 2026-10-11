import os
import sys
from loguru import logger

sys.path.insert(0, '/app')

from app.services.email_composer import get_existing_draft_recipients
from app.db.database import SessionLocal
from app.db.models import OnecContact
from app.run_daily_reactivation import check_client_reactivation_eligibility

def main():
    logger.info("1. Testing get_existing_draft_recipients...")
    draft_recipients = get_existing_draft_recipients()
    logger.info(f"Found {len(draft_recipients)} recipients in IMAP Drafts:")
    for r in sorted(draft_recipients):
        logger.info(f"  - {r}")
        
    logger.info("\n2. Testing B24 Webhook and eligibility check...")
    db = SessionLocal()
    # Test on a known contact
    test_email = "yuriy.emkin@multonpartners.com"
    contact_1c = db.query(OnecContact).filter(OnecContact.emails.any(test_email)).first()
    eligible, reason, intent_info = check_client_reactivation_eligibility(db, test_email, contact_1c=contact_1c)
    logger.info(f"Eligibility result for {test_email}: eligible={eligible}, reason='{reason}', intent={intent_info.get('intent')}")
    
    logger.info("\nVerification completed successfully!")

if __name__ == "__main__":
    main()
