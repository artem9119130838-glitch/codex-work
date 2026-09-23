# Folder Structure

## Root

- `README.md` - short human overview
- `ENGINEER_START_HERE.md` - fastest route for a new engineer
- `FOLDER_STRUCTURE.md` - what each folder contains
- `WORKFLOW_ERRORS.md` - current workflow risks and what to verify first
- `OVERALL_SYSTEM_IDEA.md` - human explanation of the whole system direction
- `DATABASE_ACCESS_AND_SCHEMA.md` - database role, access model and main tables
- `marketing_db_ingestion_v2_2_master_CANONICAL_FINAL.json` - latest canonical workflow export

## `01_context`

Minimal cross-project context:

- project handoff summary
- global rules
- progress snapshot
- security policy
- business rules

## `10_workflows`

Workflow-facing artifacts:

- short summary of the final Phase 2 fixes
- extra workflow notes / supporting workflow JSON if needed

## `20_sql`

Database-side support:

- cursor schema / seed
- event log table
- inspection queries
- reporting queries
- DB column snapshot

## `30_runbooks`

How to operate and inspect the current ingestion layer.

## `40_curated_kb`

The active knowledge base for:

- client context
- templates
- articles
- objections
- proof points

## `50_rag_tools`

Utilities for future chunking / export / embeddings prep.

## `60_integrations`

Broader system context:

- VPS
- 1C publication and OData
- n8n role
- Bitrix direction
- tender automation direction
