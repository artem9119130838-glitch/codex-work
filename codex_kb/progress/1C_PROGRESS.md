# 1C Progress

Дата обновления: 2026-05-10

## Status

UNBLOCKED FOR READ-ONLY TESTS: `$metadata.xml` is valid and contains business entities. 1C remains read-only for this stage.

## Verified Metadata

The verified metadata file is saved here:

```text
E:\Codex_Work\codex_kb\20_domains\1c\metadata\standard_odata_metadata.xml
```

Summary:

```text
E:\Codex_Work\codex_kb\20_domains\1c\metadata\METADATA_SUMMARY.md
```

## Known OData Publication

Local `default.vrd` shows OData enabled:

```text
E:\Codex_Work\projects\1c_odata\verified\default.vrd
```

Expected endpoint:

```text
http://artem.medianasoft.spb.ru/unf/odata/standard.odata/$metadata
```

Known n8n OData user:

```text
odata.user
```

Password is not stored in markdown.

## Allowed Now

- Verify Apache/1C publication.
- Create/read documentation.
- Test read-only OData calls with `$top=1`.
- Prepare n8n workflow skeleton using verified entity names.
- Prepare dry-run parser logic.
- Prepare security and credential placeholders.
- Use 1C only as a source for `marketing_db`.
- Use verified read-only JSON samples from `projects\1c_odata\incoming\odata-tests`.

## Not Allowed Yet

- Write to 1C through OData.
- Create or update real 1C business objects from n8n.
- Plan any 1C write behavior for the current stage.
- Store live 1C credentials in markdown.

## Next

- Create/verify PostgreSQL database `marketing_db`.
- Apply schema file `projects\n8n_email_ai\sql\marketing_db_schema_v1.sql`.
- Use `EMAIL_CONTACT_FIELD_MAPPING.md` for contact/email matching design.
- Keep all 1C write operations blocked.

## Completed Read Tests

Read-only OData JSON tests completed successfully on 2026-05-10:

```text
E:\Codex_Work\projects\1c_odata\notes\ODATA_READ_TEST_2026-05-10.md
```
