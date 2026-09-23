# Overall System Idea

## What this project is in human terms

This is not just “one workflow”.

It is part of a broader internal automation system that is being built step by step around:

- 1C
- PostgreSQL / `marketing_db`
- n8n
- email
- Bitrix24
- Google Drive
- curated AI/RAG knowledge

The business goal is simple:

> stop keeping client knowledge, tender knowledge, and communication history scattered across tools, and turn them into one controlled working system.

## What the system should eventually do

### Client / email side

1. read client data from 1C;
2. keep a working client memory in `marketing_db`;
3. ingest old and new email communication;
4. match emails to real clients;
5. understand what the client originally wanted;
6. help prepare safe follow-up drafts;
7. later support reply assistance and Bitrix actions.

### Tender / document side

1. detect new tender document folders;
2. extract structured data from documents;
3. normalize outputs;
4. later create Bitrix tasks / entities from them.

### RAG / AI side

1. keep curated markdown knowledge as the real source of truth;
2. derive embeddings / retrieval indexes from it;
3. use retrieval only to support good drafts and safe decision-making.

## What is the current project focus

Right now, the live focus is this narrower chain:

`1C -> marketing_db -> old email pilot -> matching -> client summary -> draft preview`

That means:

- we already have the data foundation;
- we already have the client ingestion layer;
- we already have the text knowledge base;
- the next meaningful step is the email pilot.

## Why the architecture is split this way

### Why not write directly into 1C

Because 1C is treated as the operational business source, not as the experimentation area.

So:

- 1C stays read-only;
- `marketing_db` is where enrichment, AI, and email memory live.

### Why not read the whole email archive into the model

Because that would be:

- expensive;
- noisy;
- full of repeated quoted tails;
- hard to control.

So the intended approach is:

- ingest only needed messages;
- deduplicate;
- clean the body;
- summarize compactly;
- generate drafts from a small high-quality context.

### Why Bitrix is not the first step

Because if email matching and client memory are wrong, then task creation and automation on top of them will also be wrong.

So Bitrix is part of the bigger direction, but not the first operational milestone of this project.

## What a new engineer should understand immediately

1. This is a staged system, not a monolith.
2. `marketing_db` is the working layer.
3. 1C is read-only.
4. The current workflow foundation is already usable.
5. The next safe milestone is email intake + matching + draft preview.
6. Auto-send should remain off until the pilot proves the data and summaries are trustworthy.

