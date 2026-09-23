# n8n_email_ai - Human Handoff Bundle

This folder is a **clean transfer package** for another engineer or another AI chat.

It contains:

- the current project goal;
- the broader system idea around 1C / email / Bitrix / tenders / RAG;
- database access and schema explanation;
- what is done and what is not done;
- the latest canonical workflow;
- the important SQL and runbooks;
- the curated knowledge base for future drafts/RAG;
- the minimum context needed to continue safely.

## Start here

Read in this order:

1. `README.md`
2. `ENGINEER_START_HERE.md`
3. `ENGINEER_ACCESS.md`
4. `PROJECT_STATUS.md`
5. `OVERALL_SYSTEM_IDEA.md`
6. `DATABASE_ACCESS_AND_SCHEMA.md`
7. `WORKFLOW_ERRORS.md`
8. `marketing_db_ingestion_v2_2_master_CANONICAL_FINAL.json`
9. the folder README files, depending on the task

## What this project is

This project turns:

- 1C client data
- client email history
- curated sales knowledge

into a controlled working system for:

- client matching
- client memory
- draft follow-up / reactivation emails
- future RAG / AI assistance

**1C is read-only. `marketing_db` is the working AI/email database.**

## Current status in plain English

- **Foundation is done**: the separate PostgreSQL working database exists.
- **1C ingestion is done as an operational layer**: client data can be loaded into `marketing_db`.
- **Curated KB is done as v1**: text knowledge for client messaging already exists.
- **Email pilot is not done yet**: the next real step is mail intake, matching, and draft preview.
- **Auto-send is not enabled** and should stay off for now.

## Folder map

- `01_context` - project context, rules, global progress, security
- `10_workflows` - workflow explanations and supporting workflow artifacts
- `20_sql` - schema, cursor, monitoring and DB inspection SQL
- `30_runbooks` - operator-level instructions and ingestion notes
- `40_curated_kb` - the active text knowledge base for email/drafts
- `50_rag_tools` - tools for future chunking / embeddings work
- `60_integrations` - broader VPS / 1C / n8n / Bitrix / tenders context

See also:

- `ENGINEER_START_HERE.md`
- `PROJECT_STATUS.md`
- `FOLDER_STRUCTURE.md`
