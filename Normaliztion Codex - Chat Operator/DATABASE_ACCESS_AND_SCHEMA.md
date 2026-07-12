# Database Access and Schema

## Database role in the project

`marketing_db` is the central working database for this project.

It is used to hold:

- client/owner data imported from 1C;
- contact data imported from 1C;
- email-related working data;
- AI/client summaries;
- future RAG index data.

It is **not** the production 1C business database.  
It is the safe AI/email working layer around 1C.

## Access model

### Server

- VPS public IP: `109.248.170.181`

### 1C OData

- Base URL: `http://artem.medianasoft.spb.ru/unf/odata/standard.odata/`
- Metadata URL: `http://artem.medianasoft.spb.ru/unf/odata/standard.odata/$metadata`

### n8n

- Public URL: `https://n8n.3develop.ru`

### Database access

Credentials are provided separately by the project owner.  
Do not store them in files.

Expected access pattern:

- host: provided separately by owner
- port: provided separately by owner
- db name: `marketing_db`
- user: provided separately by owner
- password: provided separately by owner

If a separate read-only engineer user is available, prefer that over a write-capable workflow user.

## Main tables

### `onec_owners`

Purpose:

- the main owner/client layer imported from 1C
- the primary object for later email matching and client intelligence

Why these fields matter:

- `owner_ref_key` - stable 1C link
- `owner_name`, `owner_inn` - human/business identity
- `owner_search_emails`, `owner_search_phones` - practical matching
- `owner_group_path`, `owner_tags_text` - business context and prioritization
- `owner_is_important`, `owner_importance_score`, `owner_importance_reason` - ranking for outreach
- `ai_client_segment`, `ai_email_summary`, `sent_articles_history`, `last_contact_date` - future communication layer

### `onec_contacts`

Purpose:

- contact-level data linked to owners
- exact or near-exact matching layer for email, phone, and person names

Why these fields matter:

- `contact_ref_key` - stable contact identity
- `owner_ref_key` - connects contact to owner
- `emails`, `phones` - main deterministic matching fields
- `contact_name`, `contact_role` - helps when sender email is unclear

### `email_messages`

Purpose:

- working storage for ingested emails
- not a giant perfect raw archive, but the operational email layer

Why these fields matter:

- `message_id` - deduplication
- `from_email`, `from_name` - sender identification
- `subject`, `received_at`, `source_mailbox` - basic threading and chronology
- `raw_payload` - source record when needed
- `is_junk`, `junk_reason` - filtering
- `operator_comment`, `thread_comment`, `ai_summary` - lightweight annotations and summarized meaning

### `email_match_results`

Purpose:

- record how a message was or was not matched to a client/contact

Why these fields matter:

- `decision` - matched / needs review / other routing
- `matched_level` - strength of the match
- `owner_ref_key`, `contact_ref_key` - resulting linkage
- `matched_email`, `matched_phone` - traceability
- `confidence`, `decision_reason` - auditability

### `clients_intel`

Purpose:

- a light client intelligence layer for future follow-up logic

Why these fields matter:

- `ai_summary` - short client memory
- `last_topic` - what the latest relevant subject was
- `current_status` - workflow state
- `next_followup_at` - next intended touchpoint
- `ai_priority` - ranking helper

### `knowledge_base`

Purpose:

- derived RAG index
- not the primary source of truth

Why it exists:

- so curated markdown can later be chunked and indexed for retrieval

## Schema philosophy

The schema is intentionally split into layers:

1. **1C import layer**: `onec_owners`, `onec_contacts`
2. **email working layer**: `email_messages`, `email_match_results`
3. **light intelligence layer**: `clients_intel`
4. **derived retrieval layer**: `knowledge_base`

This keeps responsibilities clear:

- 1C facts stay separate from email processing;
- email processing stays separate from AI summaries;
- markdown remains the source for RAG knowledge.

## Recommended first DB checks for a new engineer

1. inspect row counts in:
   - `onec_owners`
   - `onec_contacts`
   - `email_messages`
   - `email_match_results`
   - `clients_intel`

2. inspect ingestion state in:
   - `ingestion_cursors`
   - `ingestion_event_log`

3. compare actual columns against:
   - `20_sql/columns_202605142106.sql`

## What is intentionally not documented here

- no live credentials
- no passwords
- no secret URLs
- no assumptions about the exact external workstation setup

