# Project Status

## High-level objective

Build a safe working system that:

1. reads client data from 1C into `marketing_db`;
2. ingests old emails;
3. matches emails to clients;
4. builds short client memory;
5. prepares safe draft follow-up emails;
6. later supports RAG, Bitrix actions, and more advanced AI workflows.

## Status table

| Priority | Area | Status | What it means in human terms |
|---|---|---|---|
| P0 | 1C -> `marketing_db` foundation | Done | The separate working database exists and 1C is already a read-only source. |
| P0 | Ingestion workflow | Done as operational layer | Client data can already be loaded from 1C into `marketing_db`. |
| P0 | Security / project governance | Done | The project already has operating rules, security rules, and a clean handoff structure. |
| P1 | Curated KB | Done as v1 | There is already a good text base for future drafts and RAG retrieval. |
| P1 | Monitoring / runbooks | Done as v1 | There is enough operator documentation to inspect the ingestion layer. |
| P1 | Email intake pilot | Not started | Old emails are not yet being ingested in a controlled pilot workflow. |
| P1 | Deterministic email matching | Not started | Emails are not yet reliably linked to existing owners/contacts. |
| P1 | AI client summary | Not started | The system does not yet build compact client memory from real email history. |
| P1 | Draft preview | Not started | The system does not yet generate draft reactivation emails from old conversations. |
| P2 | Embeddings / derived RAG index | Partially ready | Tools and KB exist, but the production indexing pipeline is not complete. |
| P2 | Auto-send / auto-reply / Bitrix automation | Deliberately postponed | These should not be enabled before the safe email pilot works. |

## What is already successful

- A real `marketing_db` exists.
- 1C OData is being used as a read-only source.
- A canonical ingestion workflow exists.
- Useful enrichment fields already exist in `onec_owners`.
- A curated email/RAG knowledge base exists.

## What is next

The next real project step is:

1. mail intake pilot from a dedicated IMAP folder;
2. deterministic matching to existing clients;
3. short client summary;
4. draft preview only;
5. no automatic sending.

## Where to look next

- overall start: `ENGINEER_START_HERE.md`
- overall system idea: `OVERALL_SYSTEM_IDEA.md`
- database and access: `DATABASE_ACCESS_AND_SCHEMA.md`
- workflow risk and verification: `WORKFLOW_ERRORS.md`
- operational ingestion instructions: `30_runbooks/N8N_MARKETING_DB_OPERATOR_RUNBOOK.md`
- text knowledge base: `40_curated_kb/`
