import argparse
import datetime
import json
import os
from loguru import logger
import dotenv

dotenv.load_dotenv()

# Load env variables
from app.core.config import settings
from app.db.database import SessionLocal
from app.services.imap_service import ImapService

def get_mail_accounts():
    accounts = []
    
    # 1. Try to read JSON-based list MAIL_ACCOUNTS
    mail_accounts_json = os.getenv("MAIL_ACCOUNTS")
    if mail_accounts_json:
        try:
            accounts = json.loads(mail_accounts_json)
            if accounts:
                logger.info(f"Loaded {len(accounts)} mail accounts from MAIL_ACCOUNTS JSON env variable.")
                return accounts
        except Exception as e:
            logger.error(f"Failed to parse MAIL_ACCOUNTS JSON: {e}")
            
    # 2. Try to read numbered variables
    try:
        count_str = os.getenv("MAIL_ACCOUNTS_COUNT")
        if count_str:
            count = int(count_str)
            for i in range(1, count + 1):
                user = os.getenv(f"MAIL_ACCOUNT_{i}_USER")
                password = os.getenv(f"MAIL_ACCOUNT_{i}_PASS")
                if user and password:
                    accounts.append({"user": user, "pass": password})
            if accounts:
                logger.info(f"Loaded {len(accounts)} mail accounts from numbered environment variables.")
                return accounts
    except Exception as e:
        logger.error(f"Failed to load numbered mail accounts: {e}")
        
    # 3. Fallback to settings
    if settings.IMAP_USER and settings.IMAP_PASSWORD:
        logger.info("Loaded default single mail account from settings.")
        accounts.append({"user": settings.IMAP_USER, "pass": settings.IMAP_PASSWORD})
        
    return accounts

from app.services.log_service import write_db_log

def run_imap_sync(since_date: datetime.date = None, limit: int = None, date_to: datetime.date = None):
    accounts = get_mail_accounts()
    db = SessionLocal()
    
    if not accounts:
        logger.error("No mail accounts configured in environment.")
        write_db_log(db, "email_imap_sync", "sync_error", "error", "No mail accounts configured in environment.")
        db.close()
        return
        
    focus_domains = None
    if os.path.exists("focus_group.txt"):
        with open("focus_group.txt", "r") as f:
            focus_domains = [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]
        if focus_domains:
            logger.info(f"Loaded {len(focus_domains)} focus domains: {focus_domains}")
            
    try:
        write_db_log(db, "email_imap_sync", "sync_start", "info", f"Starting IMAP sync for {len(accounts)} accounts since {since_date} (limit: {limit})")
        imap_service = ImapService(db)
        for i, acc in enumerate(accounts, 1):
            user = acc.get("user")
            password = acc.get("pass")
            if not user or not password:
                continue
            write_db_log(db, "email_imap_sync", "account_sync_start", "info", f"Syncing account {i}/{len(accounts)}: {user}")
            imap_service.fetch_and_match_emails(imap_user=user, imap_password=password, date_since=since_date, date_to=date_to, limit=limit, focus_domains=focus_domains)
        write_db_log(db, "email_imap_sync", "sync_success", "info", "IMAP sync batch completed successfully.")
    except Exception as e:
        error_msg = f"Error during IMAP sync batch run: {e}"
        logger.error(error_msg)
        write_db_log(db, "email_imap_sync", "sync_error", "error", error_msg)
    finally:
        db.close()
 
if __name__ == "__main__":
    logger.add("logs/run_imap_{time}.log", rotation="1 day")
    logger.info("Starting IMAP Sync Job")
    
    parser = argparse.ArgumentParser(description="Sync emails from IMAP accounts to database")
    parser.add_argument("--since", type=str, default=None, help="Start date for syncing (YYYY-MM-DD)")
    parser.add_argument("--since-days", type=int, default=None, help="Sync emails received in the last N days")
    parser.add_argument("--to", type=str, default=None, help="End date for syncing (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=None, help="Max emails to fetch per account per run")
    args = parser.parse_args()
    
    since_date = None
    if args.since_days is not None:
        since_date = (datetime.datetime.now() - datetime.timedelta(days=args.since_days)).date()
        logger.info(f"Syncing emails from the last {args.since_days} days (since {since_date})")
    elif args.since:
        try:
            since_date = datetime.datetime.strptime(args.since, "%Y-%m-%d").date()
        except Exception as e:
            logger.error(f"Invalid date format for --since: {args.since}. Use YYYY-MM-DD.")
            exit(1)
    else:
        # Default fallback to 2025-01-01 if neither is specified
        since_date = datetime.date(2025, 1, 1)
            
    to_date = None
    if args.to:
        try:
            to_date = datetime.datetime.strptime(args.to, "%Y-%m-%d").date()
        except Exception as e:
            logger.error(f"Invalid date format for --to: {args.to}. Use YYYY-MM-DD.")
            exit(1)
            
    run_imap_sync(since_date=since_date, date_to=to_date, limit=args.limit)
