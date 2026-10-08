import time
import argparse
from app.db.database import SessionLocal
from app.db.models import EmailMatchResult, EmailMessage
from app.services.summary_service import get_summary_service
from loguru import logger
from sqlalchemy import distinct

from app.services.log_service import write_db_log

def run_batch(limit: int = 100, sleep_delay: float = 4.5):
    db = SessionLocal()
    try:
        # Get up to limit unique from_emails that have unprocessed matched emails
        emails_query = db.query(distinct(EmailMessage.from_email)).join(
            EmailMatchResult, EmailMessage.message_id == EmailMatchResult.message_id
        ).filter(
            EmailMatchResult.decision == 'matched',
            EmailMatchResult.ai_processed == False
        ).limit(limit).all()
        
        email_addresses = [e[0] for e in emails_query if e[0] is not None]
        
        if not email_addresses:
            logger.info("No unprocessed matched emails found. Batch complete.")
            write_db_log(db, "email_ai_summarizer", "batch_complete", "info", "No unprocessed matched emails found.")
            return
 
        write_db_log(db, "email_ai_summarizer", "batch_start", "info", f"Found {len(email_addresses)} unique emails to process in this batch (limit={limit}, sleep_delay={sleep_delay}s).")
        summary_service = get_summary_service(db)
        
        processed_count = 0
        for email_addr in email_addresses:
            logger.info(f"Processing email {email_addr}")
            try:
                result = summary_service.process_email_summary(email_addr)
                if result:
                    processed_count += 1
                    write_db_log(db, "email_ai_summarizer", "client_summary_success", "info", f"Generated summary for {email_addr}")
                
                # Add delay to avoid 429 Rate Limits (max 15 RPM for free Gemini Flash API)
                time.sleep(sleep_delay)
            except Exception as e:
                db.rollback()
                error_msg = f"Failed to process summary for {email_addr}: {e}"
                logger.error(error_msg)
                write_db_log(db, "email_ai_summarizer", "client_summary_error", "error", error_msg)
                time.sleep(1.0)
                continue
                
        write_db_log(db, "email_ai_summarizer", "batch_success", "info", f"Batch completed. Successfully processed {processed_count}/{len(email_addresses)} emails.")
        
    except Exception as e:
        error_msg = f"Error running summary batch: {e}"
        logger.error(error_msg)
        write_db_log(db, "email_ai_summarizer", "batch_error", "error", error_msg)
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch generation of client summaries using Gemini LLM.")
    parser.add_argument("--limit", type=int, default=100, help="Max unique emails to process in this run.")
    parser.add_argument("--sleep", type=float, default=4.5, help="Sleep time in seconds between requests.")
    args = parser.parse_args()

    logger.add("logs/run_summaries_batch_{time}.log", rotation="1 day")
    logger.info(f"Starting AI Summary Batch Job with limit={args.limit}, sleep={args.sleep}s")
    run_batch(limit=args.limit, sleep_delay=args.sleep)

