import argparse
import json
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import OnecOwner, OnecContact, OnecOwnerLink, EmailMessage, EmailMatchResult, ClientIntel

from decimal import Decimal

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def object_as_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def export_data(filename: str, limit: int = None):
    db = SessionLocal()
    try:
        # Для ограничения объема берем только запрошенное количество писем
        if limit:
            emails = db.query(EmailMessage).limit(limit).all()
        else:
            emails = db.query(EmailMessage).all()
            
        message_ids = [e.message_id for e in emails]
        matches = db.query(EmailMatchResult).filter(EmailMatchResult.message_id.in_(message_ids)).all() if message_ids else []
        
        data = {
            "onec_owners": [object_as_dict(r) for r in db.query(OnecOwner).all()],
            "onec_contacts": [object_as_dict(r) for r in db.query(OnecContact).all()],
            "onec_owner_links": [object_as_dict(r) for r in db.query(OnecOwnerLink).all()],
            "email_messages": [object_as_dict(r) for r in emails],
            "email_match_results": [object_as_dict(r) for r in matches],
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, cls=CustomEncoder, ensure_ascii=False, indent=2)
        print(f"Data exported to {filename} successfully.")
    finally:
        db.close()

def import_data(filename: str):
    db = SessionLocal()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print("Clearing local database...")
        db.query(ClientIntel).delete()
        db.query(EmailMatchResult).delete()
        db.query(EmailMessage).delete()
        db.query(OnecOwnerLink).delete()
        db.query(OnecContact).delete()
        db.query(OnecOwner).delete()
        
        print("Inserting raw data and resetting AI flags...")
        for row in data.get("onec_owners", []):
            if row.get('fetched_at'):
                row['fetched_at'] = datetime.fromisoformat(row['fetched_at'])
            db.add(OnecOwner(**row))
            
        for row in data.get("onec_contacts", []):
            if row.get('fetched_at'):
                row['fetched_at'] = datetime.fromisoformat(row['fetched_at'])
            db.add(OnecContact(**row))
            
        for row in data.get("onec_owner_links", []):
            if 'id' in row: del row['id']
            if row.get('created_at'):
                row['created_at'] = datetime.fromisoformat(row['created_at'])
            db.add(OnecOwnerLink(**row))
            
        for row in data.get("email_messages", []):
            # Возвращаем письма в исходное (сырое) состояние до обработки ИИ
            row['is_junk'] = False
            row['junk_reason'] = None
            row['ai_summary'] = None
            if row.get('received_at'):
                row['received_at'] = datetime.fromisoformat(row['received_at'])
            if row.get('created_at'):
                row['created_at'] = datetime.fromisoformat(row['created_at'])
            db.add(EmailMessage(**row))
            
        for row in data.get("email_match_results", []):
            if 'id' in row: del row['id']
            # Сброс флагов обработки
            row['ai_processed'] = False
            if row.get('decision') == 'junk':
                row['decision'] = 'needs_review'
                row['decision_reason'] = None
            db.add(EmailMatchResult(**row))
            
        db.commit()
        print("Data imported successfully. Raw state restored. Ready for local testing.")
    except Exception as e:
        db.rollback()
        print(f"Error importing data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage raw test data for local testing")
    parser.add_argument("--export", type=str, help="Export data to JSON file")
    parser.add_argument("--limit", type=int, help="Limit the number of emails exported (to keep dump size small)")
    parser.add_argument("--import-file", type=str, help="Import data from JSON file (clears local tables and resets AI flags)")
    
    args = parser.parse_args()
    if args.export:
        export_data(args.export, args.limit)
    elif args.import_file:
        import_data(args.import_file)
    else:
        parser.print_help()
