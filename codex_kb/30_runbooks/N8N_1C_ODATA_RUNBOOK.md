# Runbook: n8n to 1C through OData

## Goal

Let n8n read or write 1C data through the standard OData interface.

## Known endpoint

```text
http://artem.medianasoft.spb.ru/unf/odata/standard.odata/$metadata
```

## Server-side check

Find publication:

```bash
sudo find / -name default.vrd 2>/dev/null
```

Check file:

```bash
grep -n 'base=\|ib=\|standardOdata' /path/to/default.vrd
```

Expected:

```xml
base="/unf"
<standardOdata enable="true"
```

Apply Apache config:

```bash
sudo apachectl configtest
sudo systemctl reload apache2
```

If needed:

```bash
sudo systemctl restart apache2
```

## Metadata check

```bash
curl -i -u 'LOGIN:PASSWORD' 'http://artem.medianasoft.spb.ru/unf/odata/standard.odata/$metadata'
```

Good:

- `HTTP 200`
- XML metadata.

Problems:

- `401`: auth/rights problem.
- `404`: wrong publication path or OData not active in real file.
- `500`: server/1C publication problem; check logs.

## n8n credential

Use HTTP Basic Auth with a dedicated 1C user, for example:

```text
n8n_odata
```

Do not use a personal admin user for production workflows.

## n8n HTTP Request test

```text
Method: GET
URL: http://artem.medianasoft.spb.ru/unf/odata/standard.odata/$metadata
Authentication: Basic Auth
```

Then test one entity from `$metadata`:

```text
GET http://artem.medianasoft.spb.ru/unf/odata/standard.odata/<EntitySet>?$format=json&$top=5
```

## Docker caveat

If n8n runs in Docker:

- `127.0.0.1` inside n8n is the container;
- use public domain, host gateway, internal DNS, or VPN address as appropriate.

## Before writing to 1C

- Confirm entity names from `$metadata`.
- Confirm user rights.
- Add dry-run.
- Add duplicate protection.
- Log source email/event/document IDs.
