# Engineer Access

This file describes the access model for the external engineer.

## What the engineer gets

The engineer gets access to:

1. `n8n-eng`
2. `marketing_db` only
3. the handoff bundle files

The engineer does **not** get:

- SSH access to the VPS
- root access
- access to other PostgreSQL databases
- access to 1C write operations

## n8n access

Use:

- URL: `https://n8n-eng.3develop.ru`
- login: provided separately by owner
- password: provided separately by owner

Purpose:

- inspect and build project workflows
- use project credentials that are explicitly created for this engineer scope

## DBeaver / PostgreSQL access

Use these connection settings:

- Host: `109.248.170.181`
- Port: `5432`
- Database: `marketing_db`
- User: `eng_marketing_rw`
- Password: provided separately by owner

Important:

- this user is intended for `marketing_db` only
- access to other databases must fail
- if direct DBeaver access does not work yet, the owner may still need to whitelist the engineer's public IP in PostgreSQL `pg_hba.conf` and in the server firewall

## What the engineer should test first

1. log in to `n8n-eng`
2. confirm the Postgres credential works
3. connect to `marketing_db` from DBeaver
4. confirm that access to `unf` or other databases is denied

## What to read first

Read in this order:

1. `README.md`
2. `ENGINEER_START_HERE.md`
3. `PROJECT_STATUS.md`
4. `OVERALL_SYSTEM_IDEA.md`
5. `DATABASE_ACCESS_AND_SCHEMA.md`
6. `WORKFLOW_ERRORS.md`

## Secret handling

- credentials are sent separately by the owner
- do not store passwords in project markdown or workflow JSON
- if passwords are rotated, update only the actual system credentials, not the handoff files
