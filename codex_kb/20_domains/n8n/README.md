# Domain: n8n Automation

## Stable facts

- Public URL: `https://n8n.3develop.ru`
- Container local URL on VPS: `http://127.0.0.1:5678`
- Compose project: `/Storage/docker/n8n`
- Data volume: `/Storage/docker/n8n/n8n_data`
- Docker data root: `/Storage/docker-data`
- Image: `n8nio/n8n:latest`
- Timezone: `Europe/Moscow`

## Role

n8n is the preferred orchestration layer for:

- mail intake;
- 1C data exchange;
- Bitrix tasks;
- Google Calendar workflows;
- `marketing_db` ingestion and updates;
- future LLM parsing;
- notification and error handling.

## Design principles

- Start with deterministic rules.
- Add LLM only as a replaceable parser/fallback.
- Normalize data into stable internal objects before saving to `marketing_db` or sending to Bitrix.
- Keep 1C read-only in the current stage.
- Add dry-run mode before real writes to non-1C systems.
- Store idempotency state to prevent duplicates.

## Important environment variables

```text
N8N_HOST=n8n.3develop.ru
N8N_PORT=5678
N8N_PROTOCOL=https
WEBHOOK_URL=https://n8n.3develop.ru/
GENERIC_TIMEZONE=Europe/Moscow
TZ=Europe/Moscow
N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
```

## Known workflows / planned workflows

### Google Calendar -> Bitrix tasks

Input: work calendar events.  
Output: Bitrix task via `tasks.task.add`.  
Status: planned/begun; final workflow JSON unknown.

### Email -> n8n -> 1C read-only -> marketing_db

Input: incoming mail, attachments, client correspondence.  
Output: structured data in PostgreSQL `marketing_db`, enriched by read-only 1C OData data.  
Status: current direction; OData read access works, `marketing_db` schema is next.

### Future LLM mail parser

Input: email body and attachments.  
Output: normalized business object, table row, draft reply, or task.  
Rule: LLM output must match a schema used by deterministic nodes.

### AI client intelligence workflows

Planned from `master_doc.md`:

- Archive: IMAP -> 1C OData lookup -> enrichment -> PostgreSQL `marketing_db`.
- Triage: LLM classification and priority scoring.
- Follow-up: LLM + RAG draft replies.
- Feedback Loop: update `ai_summary`, `current_status`, and follow-up timing.

## Known n8n issues

- Volume permission can fail unless `/Storage/docker/n8n/n8n_data` is owned by UID/GID `1000:1000`.
- If opened by HTTP while configured for HTTPS, secure-cookie warnings are expected.
- Browser `127.0.0.1` is the user's local computer, not the VPS.
