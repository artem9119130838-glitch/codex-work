# Workspace Instructions for Codex

This workspace is the long-term operational memory for Artem's Codex work.

Before starting non-trivial work, read:

1. `E:\Codex_Work\CODEX_START_HERE.md`
2. `E:\Codex_Work\PROGRESS.md`
3. `E:\Codex_Work\CHAT_DISPATCHER.md`
4. `E:\Codex_Work\ГДЕ_ЧТО_ЛЕЖИТ.md`
5. `E:\Codex_Work\codex_kb\00_global\SECURITY_POLICY.md`
6. `E:\Codex_Work\codex_kb\00_global\BUSINESS_RULES.md`
7. The relevant domain file under `E:\Codex_Work\codex_kb\20_domains`
8. The relevant progress file under `E:\Codex_Work\codex_kb\progress`

Do not treat old chat exports as the first source of truth unless the current KB points there for detail. The old exports are preserved under `E:\Codex_Work\ARCHIVE`.

## Standing Rules

- `E:\Codex_Work` is the single source of truth for Codex operational memory.
- Markdown files are primary knowledge; PostgreSQL/RAG indexes are derived data.
- Live secrets may be provided in chat for one-time setup or troubleshooting, but never write secrets, passwords, private keys, Bitrix webhook URLs, OAuth secrets, or WireGuard private keys into markdown, workflow JSON, prompts, progress files, or other permanent workspace artifacts.
- Use placeholders such as `${ONEC_ODATA_PASSWORD}` or `${BITRIX_WEBHOOK_BASE_URL}` in commands, n8n snippets, and docs.
- The Ubuntu VPS is production-like. Be careful with Apache, Docker, 1C, PostgreSQL/Postgres Pro, WireGuard, OpenVPN, and firewall changes.
- Do not restart 1C or PostgreSQL unless the user explicitly approves or a maintenance window is confirmed.
- Prefer Apache `reload` after config tests; use `restart` only when necessary.
- Do not delete `/var/1C/licenses`, `/Storage/docker-data`, `/Storage/home`, or `/Storage/data` without explicit confirmation and a rollback plan.
- Keep project-specific experiments in project folders; keep stable facts in `codex_kb`.
- Put new working files under `E:\Codex_Work\projects` according to `ГДЕ_ЧТО_ЛЕЖИТ.md`.
- Put old one-off files under `E:\Codex_Work\ARCHIVE`.
- Save markdown files that contain Cyrillic as UTF-8 with BOM.
- After changing `00_global` or `20_domains`, check whether `RAG_SYNC_RUNBOOK.md` applies.
- After code or docs changes, run the local checklist in `codex_kb\skills\verification\SELF_CHECK.md`.

## Stable Knowledge Areas

- Server and infrastructure: `codex_kb\10_assets\SERVER_VPS.md`
- 1C: `codex_kb\20_domains\1c\README.md`
- n8n automation: `codex_kb\20_domains\n8n\README.md`
- Bitrix: `codex_kb\20_domains\bitrix\README.md`
- Tenders and AST GOZ: `codex_kb\20_domains\tenders\README.md`
- Email and client correspondence: `codex_kb\20_domains\email_client_comms\README.md`
- Local computer and inventory: `codex_kb\10_assets\LOCAL_COMPUTER.md`
- Router/VPN: `codex_kb\10_assets\ROUTER_AND_VPN.md`
- Phone/voice capture: `codex_kb\10_assets\PHONE_ONEPLUS.md`
- AI/RAG marketing memory: `codex_kb\20_domains\ai_rag_marketing\README.md`
