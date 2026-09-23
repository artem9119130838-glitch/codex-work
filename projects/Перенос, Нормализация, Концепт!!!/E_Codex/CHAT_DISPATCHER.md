# Chat Dispatcher

Дата обновления: 2026-05-10

This file routes every new Codex task in `E:\Codex_Work`.

## Pre-flight Checklist

Before answering or acting on any non-trivial request:

1. Read `E:\Codex_Work\PROGRESS.md`.
2. Identify the task domain and read the matching file under `E:\Codex_Work\codex_kb\progress`.
3. Check `E:\Codex_Work\codex_kb\00_global\SECURITY_POLICY.md`.
4. Check `E:\Codex_Work\ГДЕ_ЧТО_ЛЕЖИТ.md` before placing or moving files.
5. Check `E:\Codex_Work\codex_kb\00_global\BUSINESS_RULES.md` if the task involves clients, tenders, mail, Bitrix or AI/RAG.
6. If the task touches 1C, read `E:\Codex_Work\codex_kb\progress\1C_PROGRESS.md` and respect the metadata blocker.
7. Read the relevant domain file under `E:\Codex_Work\codex_kb\20_domains`.
8. After meaningful changes, update `PROGRESS.md` and the relevant domain progress file.
9. After changes in `00_global` or `20_domains`, check `RAG_SYNC_RUNBOOK.md`.
10. After code or docs work, run the checklist in `codex_kb\skills\verification\SELF_CHECK.md`.

Secret handling note:

- live secrets may be provided in chat for one-time setup or verification;
- do not write them into markdown, workflow JSON, prompts, progress files or exported artifacts;
- document only placeholders, credential names and storage locations.

## Routing

### 1C / OData / PostgreSQL

Read:

```text
PROGRESS.md
codex_kb\progress\1C_PROGRESS.md
codex_kb\10_assets\SERVER_VPS.md
codex_kb\20_domains\1c\README.md
codex_kb\30_runbooks\N8N_1C_ODATA_RUNBOOK.md
```

Hard rule: do not build n8n/1C business logic while metadata blocker is active.

### n8n + email + AI/RAG

Read:

```text
PROGRESS.md
codex_kb\progress\N8N_EMAIL_AI_PROGRESS.md
codex_kb\20_domains\n8n\README.md
codex_kb\20_domains\email_client_comms\README.md
codex_kb\20_domains\ai_rag_marketing\README.md
codex_kb\30_runbooks\RAG_SYNC_RUNBOOK.md
```

If workflow writes to 1C, also read `1C_PROGRESS.md`.

### Tenders / AST GOZ / PDF / Excel

Read:

```text
PROGRESS.md
codex_kb\progress\TENDERS_PROGRESS.md
codex_kb\20_domains\tenders\README.md
codex_kb\30_runbooks\TENDER_DATA_RUNBOOK.md
```

### Bitrix

Read:

```text
PROGRESS.md
codex_kb\progress\BITRIX_PROGRESS.md
codex_kb\20_domains\bitrix\README.md
codex_kb\20_domains\email_client_comms\README.md
```

### Server / Apache / Docker / VPN

Read:

```text
PROGRESS.md
codex_kb\progress\SERVER_INFRA_PROGRESS.md
codex_kb\10_assets\SERVER_VPS.md
codex_kb\10_assets\ROUTER_AND_VPN.md
codex_kb\30_runbooks\SERVER_OPS_RUNBOOK.md
```

### Local computer / inventory

Read:

```text
PROGRESS.md
codex_kb\10_assets\LOCAL_COMPUTER.md
codex_kb\30_runbooks\LOCAL_INVENTORY_RUNBOOK.md
```

## Update Rules

- Stable facts go to `codex_kb\10_assets`, `codex_kb\20_domains` or `codex_kb\00_global`.
- Work status goes to `PROGRESS.md` and `codex_kb\progress`.
- Procedures go to `codex_kb\30_runbooks`.
- Raw old context stays in `chat_exports`.
- If a markdown update changes facts that should be searchable by AI/RAG, schedule RAG sync.
