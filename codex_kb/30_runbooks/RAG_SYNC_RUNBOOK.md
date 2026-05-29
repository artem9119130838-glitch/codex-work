# Runbook: RAG Sync

Дата обновления: 2026-05-10

## Principle

Markdown files in `E:\Codex_Work` are the Single Source of Truth.

`marketing_db.knowledge_base` is a derived search/RAG index and must be rebuilt or updated from `.md` files.

## When to Sync

Run or schedule RAG sync after meaningful changes in:

```text
E:\Codex_Work\codex_kb\00_global
E:\Codex_Work\codex_kb\20_domains
E:\Codex_Work\codex_kb\30_runbooks
```

Especially after changes to:

- business rules;
- security policy;
- domain facts;
- server paths;
- 1C/OData metadata;
- email/AI/RAG workflows.

## Safety

- Do not run real DB writes until `marketing_db`, schema and `pgvector` are verified.
- First generate a dry-run report listing changed files and chunks.
- Do not put secrets into RAG.
- Treat markdown as primary if DB content conflicts with files.
- AI/RAG work starts only after deterministic 1C/contact/email matching is stable.

## Proposed Schema

```sql
create table if not exists knowledge_base (
  id bigserial primary key,
  source_path text not null,
  source_section text,
  chunk_index integer not null,
  content text not null,
  category text not null,
  content_hash text not null,
  updated_at timestamptz not null default now(),
  is_active boolean not null default true,
  embedding vector
);

create unique index if not exists knowledge_base_source_chunk_uidx
  on knowledge_base (source_path, chunk_index);
```

The `embedding vector` column requires `pgvector`. If `pgvector` is unavailable, create the table without `embedding` first and add it later.

## Upsert Pattern

Use this only after schema verification:

```sql
insert into knowledge_base (
  source_path,
  source_section,
  chunk_index,
  content,
  category,
  content_hash,
  updated_at,
  is_active
) values (
  ${SOURCE_PATH},
  ${SOURCE_SECTION},
  ${CHUNK_INDEX},
  ${CONTENT},
  ${CATEGORY},
  ${CONTENT_HASH},
  now(),
  true
)
on conflict (source_path, chunk_index)
do update set
  source_section = excluded.source_section,
  content = excluded.content,
  category = excluded.category,
  content_hash = excluded.content_hash,
  updated_at = now(),
  is_active = true;
```

## Deactivation Pattern

Before importing chunks for a changed file:

```sql
update knowledge_base
set is_active = false,
    updated_at = now()
where source_path = ${SOURCE_PATH};
```

Then upsert current chunks as active.

## Chunking Rules

- Preserve headings as `source_section`.
- Keep chunks human-readable.
- Prefer 500-1200 words per chunk for long files.
- Do not split code blocks unless necessary.
- Exclude files containing secrets.

## Current Status

- `marketing_db` exists.
- Base `knowledge_base` schema has been applied without a verified `embedding vector` column.
- `pgvector`: not verified.
- Real sync: not approved yet.
- AI/RAG work starts only after deterministic 1C/contact/email matching is stable.
