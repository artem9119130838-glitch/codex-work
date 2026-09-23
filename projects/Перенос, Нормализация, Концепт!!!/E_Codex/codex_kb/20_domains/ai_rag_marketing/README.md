# Domain: AI / RAG / Marketing DB

## Source

Added from:

```text
E:\Codex_Work\chat_exports\master_doc.md
```

This file describes a target architecture and backlog. Some items are plans, not yet verified as implemented.

## Purpose

Create an isolated AI/business-intelligence layer so mail analysis, client summaries, RAG, and tender intelligence do not overload or directly mutate the working 1C database `unf`.

Markdown files in `E:\Codex_Work` are the Single Source of Truth. `marketing_db.knowledge_base` is a derived RAG index and should be updated from markdown according to:

```text
E:\Codex_Work\codex_kb\30_runbooks\RAG_SYNC_RUNBOOK.md
```

## Planned database

Database:

```text
marketing_db
```

Status: created; base schema applied on 2026-05-10. Restricted PostgreSQL role `n8n_marketing` is created and cannot connect to `unf`.

Reason:

- keep AI logic separate from 1C;
- keep 1C as a read-only source for this stage;
- store client intelligence;
- store RAG knowledge;
- prepare tender archive and Bitrix links.

## Planned tables

### `clients_intel`

Purpose: client intelligence and correspondence state.

Planned fields:

```text
email primary key
source_id_1c
company_name
inn
ai_priority
ai_summary
last_topic
current_status
next_followup_at
```

This table should store the normalized result of matching email correspondence to a lead/counterparty/contact from read-only 1C OData.

`ai_priority`: expected scale `1-10`.

`current_status`: examples:

```text
active
waiting_reply
```

### `knowledge_base`

Purpose: RAG content for company methods, logistics, infrastructure and working style.

Planned fields:

```text
content
category
embedding
```

Planned categories:

```text
infrastructure
methods
logistics
```

Requires PostgreSQL extension:

```text
pgvector
```

### `tenders_archive`

Purpose:

- future tender parsing;
- archive of tender inputs;
- possible links to Bitrix24 deals/tasks.

Exact schema: `unknown`.

## Planned n8n workflows

### Workflow: Archive

```text
IMAP email
-> parse mail
-> find email/client in 1C through OData
-> enrich with INN / importance / 1C data
-> write to marketing_db
```

Important: do not write back to 1C in this workflow.

### Workflow: Triage

Goal: analyze incoming mail text, seriousness, priority and segment.

Model from source:

```text
Gemini 1.5 Flash
```

Note: model choice should be re-checked when implementing, because model availability changes.

### Workflow: Follow-up

Goal: generate draft replies using:

- stronger LLM;
- RAG knowledge base;
- Artem's working methods;
- client history.

Model from source:

```text
Gemini 1.5 Pro
```

Note: model choice should be re-checked when implementing.

### Workflow: Feedback Loop

```text
watch client replies
-> update current_status
-> update ai_summary
-> schedule next follow-up
```

## Business methodology notes

These are working-style facts from `master_doc.md`; use carefully and refine as the real process evolves.

- Specification priority: the specification is the main meaningful document; avoid unnecessary extra requests.
- Azat: China sourcing, niche search, supplier control.
- Saule: work only within Russia; not subordinate to Azat.
- Angelika / Irina: data entry in 1C and Ozon.

## Integration with 1C

Preferred path:

```text
marketing_db / n8n reads from 1C through OData
```

Known 1C OData user for n8n:

```text
odata.user
```

Store its password only in n8n credentials or another secure vault, not in markdown.

Avoid:

```text
direct SQL writes to 1C tables
OData writes to 1C business objects at this stage
```

## Integration with Bitrix

Future tender/email intelligence can create or update:

- Bitrix tasks;
- possibly Bitrix24 deals.

Exact Bitrix entity model remains `unknown`.

## Implementation backlog

- Verify whether `marketing_db` exists.
- Restricted n8n PostgreSQL role was created from:

```text
E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_n8n_role.sql
```

- Password was set interactively on the server:

```text
\password n8n_marketing
```

- On the VPS, use Postgres Pro binaries directly if commands are not in `PATH`:

```text
/opt/pgpro/std-14/bin/psql
/opt/pgpro/std-14/bin/createdb
```

- Create SQL schema from:

```text
E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_schema_v1.sql
```

- Check whether `pgvector` is installed and compatible.
- Build n8n Archive workflow first.
- Load initial RAG content:
  - company working methods;
  - employee/team instructions;
  - price/logistics knowledge;
  - infrastructure notes.
- Add Triage only after deterministic ingestion works.
- Add Follow-up as draft-only before allowing auto-send.

## Safety

- Do not auto-send generated replies at first.
- Keep original email/message IDs for traceability.
- Do not store secrets in RAG.
- Do not store unnecessary personal data if a summary is enough.
- Treat model names as implementation-time choices, not permanent facts.
