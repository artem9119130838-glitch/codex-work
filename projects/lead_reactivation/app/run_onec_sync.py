import time
import schedule
from loguru import logger
from app.db.database import SessionLocal
from app.services.onec_sync_service import OnecSyncService

def job():
    logger.info("Starting scheduled 1C sync job...")
    db = SessionLocal()
    try:
        service = OnecSyncService(db)
        service.run_full_sync()
    except Exception as e:
        logger.error(f"Job failed: {e}")
    finally:
        db.close()
    logger.info("Scheduled 1C sync job finished.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run sync once and exit")
    args = parser.parse_args()

    if args.once:
        job()
    else:
        logger.info("Starting 1C sync scheduler (every 30 minutes)")
        schedule.every(30).minutes.do(job)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
