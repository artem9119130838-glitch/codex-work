# Domain: 1C

## Stable facts

- Main 1C database: `unf`
- Server: Ubuntu VPS `109.248.170.181`
- 1C service: `srv1cv8-8.5.1.1150.service`
- Platform path: `/opt/1cv8/x86_64/8.5.1.1150`
- PostgreSQL/Postgres Pro backend.
- Apache publication exists for `/unf`.

## OData publication

Local checked file:

```text
E:\Codex_Work\projects\1c_odata\verified\default.vrd
```

Important values:

```xml
base="/unf"
ib="Srvr=&quot;artem.medianasoft.spb.ru&quot;;Ref=&quot;unf&quot;;"
<standardOdata enable="true"
```

Expected metadata URL:

```text
http://artem.medianasoft.spb.ru/unf/odata/standard.odata/$metadata
```

Base URL:

```text
http://artem.medianasoft.spb.ru/unf/odata/standard.odata/
```

## Metadata status

Current progress status is tracked in:

```text
E:\Codex_Work\codex_kb\progress\1C_PROGRESS.md
```

As of 2026-05-10, metadata is verified and contains business entities. Verified metadata:

```text
E:\Codex_Work\codex_kb\20_domains\1c\metadata\standard_odata_metadata.xml
```

Summary:

```text
E:\Codex_Work\codex_kb\20_domains\1c\metadata\METADATA_SUMMARY.md
```

Read-only tests are allowed. 1C is a read-only source for this stage. New data and matching results go to PostgreSQL `marketing_db`.

## Integration direction

Use OData for n8n integration where possible:

- read catalogs;
- read documents;
- use separate 1C OData user `odata.user` for n8n read-only access.

Do not create or update 1C business objects in the current stage.

## Performance findings from previous work

PostgreSQL did not look like the main cause of sampled 3-5 second UI delays. Likely areas:

- 1C `rphost`;
- form logic;
- extensions;
- client/server round trips;
- external service calls;
- network latency.

Next serious diagnostic: short 1C technological log for one slow action.

## Database size findings

`unf` was much larger than `unf_restored`. Large contributors included:

- `_reference57946`
- `binarydata`
- `_inforg38386x1`
- `_document627`

Do not clean SQL tables directly. Map SQL tables to 1C metadata first.

## Safety

- Do not delete `/var/1C/licenses`.
- Do not run heavy test-and-repair without verified backup and maintenance window.
- Do not close public 1C ports until VPN access works.
- Do not grant n8n full admin rights permanently.
