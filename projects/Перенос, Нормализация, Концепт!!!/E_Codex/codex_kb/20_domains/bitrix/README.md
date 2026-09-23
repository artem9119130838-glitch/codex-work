# Domain: Bitrix

## Role

Bitrix is a stable business system for:

- tasks;
- responsible employees;
- future CRM-related automation;
- possible tender deals from parsed tender emails;
- possible integration with calendar and email workflows.

## Known integration plan

Use incoming Bitrix webhook as the simple authentication method for Bitrix REST API.

Planned method:

```text
tasks.task.add
```

Required scopes/rights:

```text
tasks
user
```

## Unknowns to fill

- Bitrix portal URL.
- Incoming webhook base URL. Do not store full secret URL in markdown.
- User IDs for employees.
- Task field mapping.
- Status update methods.
- Whether CRM entities are needed in addition to tasks.
- Whether tender parsing should create Bitrix24 deals, tasks, or both.

## Data model draft

Normalized task object before Bitrix:

```json
{
  "title": "string",
  "description": "string",
  "responsibleName": "string",
  "responsibleBitrixId": "string",
  "deadline": "ISO datetime or null",
  "source": "email|calendar|manual|1c",
  "sourceId": "string",
  "dryRun": true
}
```

## Safety

- Start in dry-run.
- Log source IDs.
- Store mapping from source object to Bitrix task ID.
- Do not duplicate tasks if a source item is reprocessed.
