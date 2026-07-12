# Asset: Ubuntu VPS

## Identity

- Public IP: `109.248.170.181`
- Ubuntu: `20.04 LTS`
- Hostname observed: `server`
- Role: production-like server for 1C, PostgreSQL/Postgres Pro, Apache, Docker/n8n, WireGuard, OpenVPN.

## Critical services

```text
apache2
docker (с контейнерами n8n и 3x-ui)
srv1cv8-8.5.1.1150.service
postgrespro-std-14.service
wg-quick@wg0 (классический WireGuard)
3x-ui (контейнер VLESS Reality VPN)
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

## Docker / 3X-UI (VLESS Reality VPN)

- Image: `ghcr.io/mhsanaei/3x-ui:latest` (активный форк 3x-ui)
- Compose path: `/Storage/docker/3x-ui`
- DB path: `/Storage/docker/3x-ui/db`
- Web panel port: `2053` (TCP, открыт в ufw)
- VLESS-Reality port: `8443` (TCP, открыт в ufw, маскировка под dl.google.com или аналогичный)
- Резервные домены для маскировки (из той же подсети `109.248.170.X`), найденные сканером 21.06.2026:
  - `gitlab-datalake.astanahubcloud.com` (IP `109.248.170.174`)
  - `academy.kz` (IP `109.248.170.157`)
  - `openapi.zhasalash.kz` (IP `109.248.170.199`)
  - `image.zhasalash.kz` (IP `109.248.170.200`)
  - `subsecprotect.mooo.com` (IP `109.248.170.205`)
  - `relnet.su` (IP `109.248.170.206`)
- Откат (остановка):
  ```bash
  cd /Storage/docker/3x-ui && docker-compose down
  ```

## Docker / MTProto Proxy (mtg)

- **Статус**: Активен. Восстановлен 21.06.2026.
- Image: `ghcr.io/9seconds/mtg:latest` (Go-based MTProto proxy v2)
- Port: `8585` (TCP, открыт наружу)
- Secret (hex): `eeef4d9631cfeba1f2ef85ad737db106f26a6f6a6f712e6b7a` (маскировка под `jojoq.kz`, секрет: `7u9NljHP66Hy74Wtc32xBvJqb2pvcS5reg`)
- Запуск:
  ```bash
  docker run -d --name mtproto-proxy --restart unless-stopped -p 8585:3128 ghcr.io/9seconds/mtg:latest simple-run 0.0.0.0:3128 7u9NljHP66Hy74Wtc32xBvJqb2pvcS5reg
  ```
- Откат (остановка):
  ```bash
  docker rm -f mtproto-proxy
  ```



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
