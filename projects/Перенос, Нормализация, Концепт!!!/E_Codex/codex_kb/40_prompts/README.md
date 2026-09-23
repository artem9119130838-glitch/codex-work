# Prompts Index

Дата обновления: 2026-05-11

Этот раздел хранит стартовые промпты для новых рабочих чатов.

## Files

- `NEW_CHAT_GENERAL.md` - general Codex KB start.
- `NEW_CHAT_N8N_1C_EMAIL.md` - n8n, 1С, email and AI/RAG.
- `NEW_CHAT_N8N_MARKETING_DB_WORKER.md` - рабочий чат для `marketing_db / 1C / n8n ingestion`.
- `NEW_CHAT_RAG_LEADS_KB_WORKER.md` - рабочий чат для `RAG / curated KB / client emails`.
- `NEW_CHAT_TENDERS.md` - tenders, AST GOZ, PDF/Excel.
- `NEW_CHAT_SERVER_OPS.md` - VPS, Apache, Docker, VPN and server safety.

## Rule

Prompts should point to source files instead of copying large context blocks.

For `n8n_email_ai`, use exactly 2 specialized worker chats:

- `NEW_CHAT_N8N_MARKETING_DB_WORKER.md`
- `NEW_CHAT_RAG_LEADS_KB_WORKER.md`
