import os
import argparse
from loguru import logger
from app.db.database import SessionLocal
from app.db.models import EmailMessage, EmailMatchResult
from app.services.llm_service import llm_service

def run_junk_filter(limit: int = 100):
    db = SessionLocal()
    try:
        # Get messages that are currently 'needs_review' and not processed by junk filter
        # We can identify them by checking EmailMatchResult.decision == 'needs_review'
        # and EmailMessage.is_junk == False
        matches = db.query(EmailMatchResult).join(EmailMessage, EmailMatchResult.message_id == EmailMessage.message_id).filter(
            EmailMatchResult.decision == 'needs_review',
            EmailMessage.is_junk == False,
            EmailMatchResult.ai_processed == False
        ).limit(limit).all()

        if not matches:
            logger.info("No needs_review emails found for junk filtering.")
            return

        logger.info(f"Found {len(matches)} emails to classify for junk.")
        
        for match in matches:
            email_msg = db.query(EmailMessage).filter(EmailMessage.message_id == match.message_id).first()
            if not email_msg:
                continue
                
            text_body = email_msg.raw_payload.get("text", "") if email_msg.raw_payload else ""
            
            logger.info(f"Classifying {email_msg.message_id}: {email_msg.subject}")
            
            try:
                result = llm_service.classify_junk_email(email_msg.subject, text_body)
                
                if result.get("is_junk"):
                    email_msg.is_junk = True
                    email_msg.junk_reason = result.get("reason", "AI determined as junk")
                    # Update match result to junk to hide it from review lists
                    match.decision = "junk"
                    match.decision_reason = email_msg.junk_reason
                    logger.info(f"  -> Marked as JUNK: {email_msg.junk_reason}")
                else:
                    # Mark ai_processed as True so we don't classify it again
                    match.ai_processed = True
                    logger.info("  -> Not junk, left as needs_review")
                    
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"  -> Error classifying email {email_msg.message_id}, skipping for now: {e}")
                continue
            
    except Exception as e:
        logger.error(f"Error during junk filtering: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    logger.add("logs/run_junk_filter_{time}.log", rotation="1 day")
    logger.info("Starting Junk Filter Job")
    
    parser = argparse.ArgumentParser(description="Classify needs_review emails to find junk/spam")
    parser.add_argument("--limit", type=int, default=100, help="Max emails to process per run")
    args = parser.parse_args()
    
    run_junk_filter(limit=args.limit)
