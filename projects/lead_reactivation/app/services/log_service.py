from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models import IngestionEventLog
from loguru import logger

def write_db_log(db: Session, workflow_name: str, event_type: str, severity: str, message: str, details: dict = None, mode: str = "pilot"):
    """
    Writes an execution event log entry directly into the PostgreSQL ingestion_event_log table.
    Allows remote monitoring by developers over VPN.
    """
    try:
        log_entry = IngestionEventLog(
            event_at=datetime.now(timezone.utc),
            workflow_name=workflow_name,
            mode=mode,
            event_type=event_type,
            severity=severity,
            message=message,
            details=details or {}
        )
        db.add(log_entry)
        db.commit()
        logger.info(f"[DB Log] [{severity.upper()}] {message}")
    except Exception as e:
        logger.error(f"Failed to write log to DB: {e}")
        db.rollback()
