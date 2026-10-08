import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric, ARRAY, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class KnowledgeBaseChunk(Base):
    __tablename__ = 'knowledge_base'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_file = Column(Text)
    category = Column(Text)
    content = Column(Text)
    content_hash = Column(String(32), unique=True, index=True)
    embedding = Column(Vector(768))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

class OnecOwner(Base):
    __tablename__ = 'onec_owners'
    
    owner_entity = Column(Text, primary_key=True)
    owner_ref_key = Column(UUID(as_uuid=True), primary_key=True)
    owner_name = Column(Text)
    owner_inn = Column(Text)
    owner_search_emails = Column(ARRAY(Text))
    owner_search_phones = Column(ARRAY(Text))
    owner_is_important = Column(Boolean)
    owner_importance_score = Column(Integer)
    ai_client_segment = Column(Text)
    ai_email_summary = Column(Text)
    owner_is_buyer = Column(Boolean)
    
    owner_is_junk = Column(Boolean, default=False)
    owner_tags_text = Column(ARRAY(Text), default=[])
    owner_sites = Column(ARRAY(Text), default=[])
    owner_addresses = Column(JSONB, default=[])
    owner_contact_names = Column(ARRAY(Text), default=[])
    owner_contact_count = Column(Integer, default=0)
    owner_contact_emails = Column(ARRAY(Text), default=[])
    owner_contact_phones = Column(ARRAY(Text), default=[])
    owner_all_emails = Column(ARRAY(Text), default=[])
    owner_all_phones = Column(ARRAY(Text), default=[])
    owner_tags = Column(JSONB, default={})
    raw_payload = Column(JSONB, default={})
    fetched_at = Column(DateTime(timezone=True))

class EmailMessage(Base):
    __tablename__ = 'email_messages'
    
    message_id = Column(Text, primary_key=True)
    from_email = Column(Text)
    from_name = Column(Text)
    subject = Column(Text)
    received_at = Column(DateTime(timezone=True))
    source_mailbox = Column(Text)
    raw_payload = Column(JSONB)
    created_at = Column(DateTime(timezone=True))
    is_junk = Column(Boolean)
    junk_reason = Column(Text)
    operator_comment = Column(Text)
    thread_comment = Column(Text)
    ai_summary = Column(Text)

class EmailMatchResult(Base):
    __tablename__ = 'email_match_results'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Text)
    matched_level = Column(Text)
    decision = Column(Text)
    decision_reason = Column(Text)
    contact_entity = Column(Text)
    contact_ref_key = Column(UUID(as_uuid=True))
    owner_entity = Column(Text)
    owner_ref_key = Column(UUID(as_uuid=True))
    confidence = Column(Numeric)
    matched_email = Column(Text)
    matched_phone = Column(Text)
    ai_processed = Column(Boolean, default=False)
    
    # New columns for unmatched emails extraction
    extracted_company = Column(Text)
    extracted_contact_name = Column(Text)
    extracted_reason = Column(Text)

class ClientIntel(Base):
    __tablename__ = 'clients_intel'
    
    email = Column(Text, primary_key=True) # Note: schema shows email as NO nullable, we can use it as PK
    source_id_1c = Column(Text)
    company_name = Column(Text)
    inn = Column(Text)
    ai_priority = Column(Integer)
    ai_summary = Column(Text)
    last_topic = Column(Text)
    current_status = Column(Text)
    next_followup_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    emails_count = Column(Integer, default=0)
    emails_list = Column(JSONB, default=[])
    timeline = Column(JSONB)
    skus_and_amounts = Column(JSONB)
    last_managers = Column(ARRAY(Text))
    psychological_portrait = Column(Text)
    
    # New columns for advanced client intelligence
    client_type = Column(Text)
    next_action_recommendation = Column(Text)

class IngestionEventLog(Base):
    __tablename__ = 'ingestion_event_log'
    
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    event_at = Column(DateTime(timezone=True))
    workflow_name = Column(Text)
    mode = Column(Text)
    event_type = Column(Text)
    severity = Column(Text)
    owner_ref_key = Column(UUID(as_uuid=True))
    contact_ref_key = Column(UUID(as_uuid=True))
    message = Column(Text)
    details = Column(JSONB)

class OnecContact(Base):
    __tablename__ = 'onec_contacts'
    
    contact_entity = Column(Text, primary_key=True)
    contact_ref_key = Column(UUID(as_uuid=True), primary_key=True)
    owner_entity = Column(Text)
    owner_ref_key = Column(UUID(as_uuid=True))
    contact_name = Column(Text)
    emails = Column(ARRAY(Text))
    phones = Column(ARRAY(Text))
    raw_payload = Column(JSONB)
    fetched_at = Column(DateTime(timezone=True))
    contact_tags = Column(JSONB)
    contact_notes = Column(Text)
    contact_is_primary = Column(Boolean)
    contact_is_junk = Column(Boolean)
    contact_junk_reason = Column(Text)
    contact_role = Column(Text)
    contact_channels = Column(JSONB)
    contact_site = Column(Text)
    contact_address = Column(Text)
    contact_importance_note = Column(Text)
    is_synthetic = Column(Boolean, default=False)

class OnecOwnerLink(Base):
    __tablename__ = 'onec_owner_links'
    __table_args__ = (UniqueConstraint('lead_ref_key', 'contractor_ref_key', name='uq_onec_owner_links_lead_contractor'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_ref_key = Column(UUID(as_uuid=True))
    contractor_ref_key = Column(UUID(as_uuid=True))
    link_reason = Column(Text)
    created_at = Column(DateTime(timezone=True))

class ClientReactivationHistory(Base):
    __tablename__ = 'client_reactivation_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_email = Column(String(255), ForeignKey('clients_intel.email', ondelete='CASCADE'), index=True)
    article_url = Column(Text)
    sent_at = Column(DateTime(timezone=True))
    template_used = Column(String(100))
    subject = Column(Text)
    body = Column(Text)


class ReactivationFunnelState(Base):
    __tablename__ = 'reactivation_funnel_states'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_email = Column(String(255), ForeignKey('clients_intel.email', ondelete='CASCADE'), unique=True, index=True, nullable=False)
    current_step = Column(Integer, default=1)
    step_status = Column(String(50), default='draft_created')
    last_action_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.utcnow())
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.utcnow(), onupdate=lambda: datetime.datetime.utcnow())
