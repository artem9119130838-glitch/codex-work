import uuid
from app.db.database import SessionLocal
from app.db.models import EmailMessage, EmailMatchResult, OnecOwner, OnecContact, OnecOwnerLink

db = SessionLocal()

# 1. Create a dummy owner
owner_id = uuid.uuid4()
owner = OnecOwner(
    owner_entity="Catalog_Лиды",
    owner_ref_key=owner_id,
    owner_name="Test Chunking Company",
    owner_search_emails=[]
)
db.add(owner)

# 2. Find emails for kubarev_ms@mail.ru and tokarev@invatika.com
emails1 = db.query(EmailMessage).filter(EmailMessage.from_email == 'kubarev_ms@mail.ru').all()
emails2 = db.query(EmailMessage).filter(EmailMessage.from_email == 'tokarev@invatika.com').all()

# 3. Create match results for them
for e in emails1 + emails2:
    match = db.query(EmailMatchResult).filter(EmailMatchResult.message_id == e.message_id).first()
    if match:
        match.decision = 'matched'
        match.owner_ref_key = owner_id
        match.ai_processed = False
db.commit()

print(f"Linked {len(emails1)} emails from kubarev_ms and {len(emails2)} emails from tokarev to owner {owner_id}")
db.close()
