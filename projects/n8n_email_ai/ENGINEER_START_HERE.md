# Engineer Start Here

## Goal

Continue the `n8n_email_ai` project without reading old chats or archives.

## Project outcome we want

We want a system that:

1. reads clients and contacts from 1C into `marketing_db`;
2. ingests old emails;
3. matches emails to clients;
4. builds short client memory;
5. produces safe email drafts;
6. later can support RAG, Bitrix tasks, and more advanced AI actions.

## What is already complete

### Phase 1

- `marketing_db` foundation exists
- 1C OData read-only access is set
- core owner/contact schema exists

### Phase 2

- canonical ingestion workflow exists
- operators have a runbook
- DB monitoring SQL exists
- curated KB exists

## What is not complete

### Not started as production pilot

- mail intake from IMAP
- deterministic email matching
- AI client summaries from real email history
- draft preview workflow
- production embeddings pipeline

## If you only have 10 minutes

Read:

1. `01_context/PROJECT_HANDOFF.md`
2. `30_runbooks/N8N_MARKETING_DB_OPERATOR_RUNBOOK.md`
3. `DATABASE_ACCESS_AND_SCHEMA.md`
4. `WORKFLOW_ERRORS.md`
5. `40_curated_kb/00_manifest.md`

Then choose the track:

- ingestion / DB / workflow -> `10_workflows`, `20_sql`, `30_runbooks`
- email / drafts / knowledge -> `40_curated_kb`

## Important safety

- Do not write to 1C.
- Do not store secrets in files.
- Do not enable auto-send.
- Treat this bundle as the clean handoff package, not the whole history.
