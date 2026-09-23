# Source Map

This file maps the stable KB to old exports. The old exports are not deleted and are part of the preserved knowledge.

## Source folders

```text
E:\Codex_Work\chat_exports\2026-05-10_1c_vpn_postgres_ops
E:\Codex_Work\chat_exports\2026-05-10_n8n_bitrix_google_mvp
E:\Codex_Work\chat_exports\2026-05-10_cross_project_ops_1с
E:\Codex_Work\chat_exports\2026-05-10_cross_project_ops_chat
E:\Codex_Work\chat_exports\2026-05-10_goz_ops_chat
E:\Codex_Work\chat_exports\master_doc.md
E:\Codex_Work\projects\1c_odata\verified\default.vrd
```

## How sources were used

### 1C / VPN / PostgreSQL

Source:

```text
2026-05-10_1c_vpn_postgres_ops
2026-05-10_cross_project_ops_chat
```

Mapped into:

```text
10_assets\SERVER_VPS.md
10_assets\ROUTER_AND_VPN.md
20_domains\1c\README.md
30_runbooks\SERVER_OPS_RUNBOOK.md
50_skills_index\SKILLS_INDEX.md
```

### n8n / Google / Bitrix

Source:

```text
2026-05-10_n8n_bitrix_google_mvp
```

Mapped into:

```text
20_domains\n8n\README.md
20_domains\bitrix\README.md
20_domains\google_calendar\README.md
10_assets\SERVER_VPS.md
```

### Current chat: n8n + 1C OData

Source:

```text
current chat on 2026-05-10
E:\Codex_Work\projects\1c_odata\verified\default.vrd
```

Mapped into:

```text
20_domains\1c\README.md
30_runbooks\N8N_1C_ODATA_RUNBOOK.md
```

### Master document: Ци Линь registry

Source:

```text
E:\Codex_Work\chat_exports\master_doc.md
```

Mapped into:

```text
20_domains\ai_rag_marketing\README.md
20_domains\email_client_comms\README.md
20_domains\n8n\README.md
20_domains\tenders\README.md
20_domains\bitrix\README.md
10_assets\SERVER_VPS.md
00_global\KNOWLEDGE_MAP.md
00_global\BUSINESS_RULES.md
```

Important caveat:

`master_doc.md` contains a storage claim that appears broader than earlier operational evidence. Earlier exports say PostgreSQL/Postgres Pro data path is `/var/lib/pgpro/std-14/data`, while Docker data root is `/Storage/docker-data`. Verify before treating all database storage as `/Storage/docker-data`.

### Tenders / AST GOZ / Excel / PDF

Source:

```text
2026-05-10_goz_ops_chat
2026-05-10_cross_project_ops_chat
```

Mapped into:

```text
20_domains\tenders\README.md
30_runbooks\TENDER_DATA_RUNBOOK.md
```

### Local computer / inventory

Source:

```text
2026-05-10_goz_ops_chat
E:\Codex_Work\projects\tenders_ast_goz\legacy_context\CHAT_INDEX.md
E:\Codex_Work\projects\tenders_ast_goz\legacy_context\CURRENT_STATE.md
```

Mapped into:

```text
10_assets\LOCAL_COMPUTER.md
30_runbooks\LOCAL_INVENTORY_RUNBOOK.md
```

### WordPress / ACF

Source:

```text
2026-05-10_cross_project_ops_1с
```

Mapped into:

```text
20_domains\wordpress_acf\README.md
```

## Encoding note

Some Russian strings in old exports are mojibake. Where the meaning was obvious, the KB uses restored Russian names. Where it was not obvious, values remain `unknown`.
