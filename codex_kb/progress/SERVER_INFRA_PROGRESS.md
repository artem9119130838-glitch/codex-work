# Server Infrastructure Progress

Дата обновления: 2026-05-10

## Status

Server facts are documented. Changes must be conservative because the VPS is production-like.

## Current Known Services

- Apache
- Docker/n8n
- 1C Enterprise
- PostgreSQL/Postgres Pro
- WireGuard
- OpenVPN

## Risks

- Public 1C ports were previously observed reachable.
- Docker and firewall changes can affect networking.
- PostgreSQL data path and `master_doc.md` storage claim must be verified before storage operations.

## Next

- Keep Apache changes behind `apachectl configtest`.
- Avoid 1C/PostgreSQL restarts without explicit approval.
- Verify Docker root remains `/Storage/docker-data`.
- Keep `E:\Codex_Work` KB structure as the active Codex workspace control plane.
