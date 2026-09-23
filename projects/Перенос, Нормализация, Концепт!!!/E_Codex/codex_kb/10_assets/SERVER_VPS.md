# Asset: Ubuntu VPS

## Identity

- Public IP: `109.248.170.181`
- Ubuntu: `20.04 LTS`
- Hostname observed: `server`
- Role: production-like server for 1C, PostgreSQL/Postgres Pro, Apache, Docker/n8n, WireGuard, OpenVPN.

## Critical services

```text
apache2
docker
srv1cv8-8.5.1.1150.service
postgrespro-std-14.service
wg-quick@wg0
OpenVPN service name: unknown
```

## 1C

- Platform: `/opt/1cv8/x86_64/8.5.1.1150`
- Service: `srv1cv8-8.5.1.1150.service`
- License path: `/var/1C/licenses`
- Important ports:
  - `1540`
  - `1541`
  - `1560-1591`
- Target security model: 1C access through VPN, not public internet.

## PostgreSQL / Postgres Pro

- Service: `postgrespro-std-14.service`
- Binaries: `/opt/pgpro/std-14/bin`
- PGDATA: `/var/lib/pgpro/std-14/data`
- Databases observed:
  - `unf`
  - `unf_restored`
  - `buh`
  - `moving`
  - `money`
  - `money_restored`
  - `nextcloud`
- Planned/possible AI database from `master_doc.md`:
  - `marketing_db` - status `unknown`

Note: `master_doc.md` says Docker and database data are on `/Storage/docker-data`, but earlier operational exports identify PGDATA as `/var/lib/pgpro/std-14/data`. Treat database storage location as a fact to verify before making disk or backup decisions.

## Apache

- Hosts n8n and 1C publication.
- Use `sudo apachectl configtest` before reload.
- Prefer:

```bash
sudo systemctl reload apache2
```

## Docker / n8n

- Docker data root: `/Storage/docker-data`
- n8n compose project: `/Storage/docker/n8n`
- n8n data: `/Storage/docker/n8n/n8n_data`
- n8n public URL: `https://n8n.3develop.ru`
- n8n local URL on VPS: `http://127.0.0.1:5678`

## Storage

Do not delete casually:

- `/Storage/docker-data`
- `/Storage/home`
- `/Storage/data`

Known full backup:

- Server: `/Storage/full-backup-2026-05-03_11-52`
- Windows: `D:\server-backups\full-backup-2026-05-03_11-52`
- Size: about `21.17 GB`

## Known risks

- Public 1C ports were observed reachable.
- Package repositories had warnings around pgAdmin/PostgresPro in older work.
- Docker modifies iptables; save firewall state before big Docker changes.
