# Local Operator Setup Notes

This file is a private operator summary for repeating the recent setup work on another machine or in another chat.

Secrets are intentionally **not** stored here.
Use placeholders and paste live credentials separately when needed.

## What was completed

### 1. Separate engineer n8n instance

A separate `n8n-eng` instance was created for external engineer work.

Purpose:

- isolate engineer work from the main `n8n`
- avoid giving access to the main n8n workspace
- keep DB access scoped to `marketing_db`

Result:

- public URL: `https://n8n-eng.3develop.ru`
- local container port mapping: `5679 -> 5678`
- separate Docker project path: `/Storage/docker/n8n-eng`
- separate data path: `/Storage/docker/n8n-eng/n8n_data`

### 2. DNS and HTTPS

The subdomain was set up and confirmed working externally.

Required DNS:

- `A` record
- host: `n8n-eng`
- target: `109.248.170.181`

HTTPS was issued with Certbot and Apache reverse proxy.

### 3. Apache proxy

Two Apache vhosts were used:

- `/etc/apache2/sites-available/n8n-eng.conf`
- `/etc/apache2/sites-available/n8n-eng-le-ssl.conf`

The proxy target is:

- `http://127.0.0.1:5679/`

### 4. PostgreSQL engineer role

An engineer-scoped PostgreSQL role was prepared:

- role: `eng_marketing_rw`

Purpose:

- access `marketing_db`
- no VPS access
- no database creation
- no superuser privileges
- no access to other project databases

Confirmed:

- direct connection to `marketing_db` works through `n8n-eng`
- connection to other databases such as `unf` should fail

### 5. n8n credential

Inside `n8n-eng`, a Postgres credential was created and successfully tested for:

- host: `10.0.3.1`
- port: `5432`
- database: `marketing_db`
- user: `eng_marketing_rw`

Important note:

- `127.0.0.1` did not work from the container
- `10.0.3.1` was required because Postgres is reachable there from the Docker network

### 6. PostgreSQL network access for container

`pg_hba.conf` was updated to allow the `n8n-eng` Docker network to connect to `marketing_db` for `eng_marketing_rw`.

Added rule:

```text
host    marketing_db    eng_marketing_rw    172.20.0.0/16    md5
```

Then PostgreSQL config was reloaded.

## Repeatable step-by-step sequence

### A. Create separate n8n instance

1. Create folder:

```bash
sudo mkdir -p /Storage/docker/n8n-eng
sudo mkdir -p /Storage/docker/n8n-eng/n8n_data
```

2. Set permissions:

```bash
sudo chown -R 1000:1000 /Storage/docker/n8n-eng
```

3. Create compose file in:

```text
/Storage/docker/n8n-eng/docker-compose.yml
```

4. Use separate env values for:

- `N8N_HOST`
- `N8N_PROTOCOL`
- `WEBHOOK_URL`
- basic auth user
- basic auth password

5. Start with:

```bash
cd /Storage/docker/n8n-eng
docker-compose up -d
```

### B. Configure Apache

1. Create `/etc/apache2/sites-available/n8n-eng.conf`
2. Enable proxy modules if needed
3. Enable the site
4. Run:

```bash
sudo apachectl configtest
sudo systemctl reload apache2
```

### C. Issue HTTPS certificate

Use:

```bash
sudo certbot --apache -d n8n-eng.3develop.ru
```

Choose redirect to HTTPS.

### D. Create / adjust PostgreSQL role

1. Enter PostgreSQL:

```bash
sudo -u postgres /opt/pgpro/std-14/bin/psql -d postgres
```

2. Create or alter role:

- role name: `eng_marketing_rw`
- no superuser
- no createdb
- no createrole

3. Grant `CONNECT` to `marketing_db`
4. Revoke access to other DBs
5. In `marketing_db`, grant required schema/table rights

### E. Allow container to connect

1. Edit:

```text
/var/lib/pgpro/std-14/data/pg_hba.conf
```

2. Add:

```text
host    marketing_db    eng_marketing_rw    172.20.0.0/16    md5
```

3. Reload PostgreSQL:

```bash
sudo systemctl reload postgrespro-std-14
```

### F. Create n8n Postgres credential

In `n8n-eng` use:

- host: `10.0.3.1`
- port: `5432`
- database: `marketing_db`
- user: `eng_marketing_rw`
- password: `${ENG_MARKETING_RW_PASSWORD}`

Then test connection and save.

## Access model that exists now

### Given

- separate `n8n-eng`
- separate DB role for `marketing_db`

### Not given

- no VPS shell access for engineer
- no SSH access yet
- no direct access to other PostgreSQL databases

## Known local workstation issue

The local Windows PC resolved `n8n-eng.3develop.ru` incorrectly during setup.

Temporary workaround that was used:

```text
109.248.170.181    n8n-eng.3develop.ru
```

added as a separate line to:

```text
C:\Windows\System32\drivers\etc\hosts
```

This was added **in addition to**, not instead of:

```text
109.248.170.181    server
```

## Possible future access models for engineer

Two future direct DB access ideas were discussed:

1. direct DBeaver/PostgreSQL access without fixed IP, using strict DB role limits
2. safer SSH-tunnel model with separate SSH key and tunnel-only access

These were only discussed and not finalized in this step.

## Related files

Main project transfer folder:

```text
E:\Codex_Work\projects\n8n_email_ai\HANDOFF_BUNDLE
```

Most relevant files there:

- `README.md`
- `ENGINEER_START_HERE.md`
- `ENGINEER_ACCESS.md`
- `PROJECT_STATUS.md`
- `DATABASE_ACCESS_AND_SCHEMA.md`
- `WORKFLOW_ERRORS.md`
