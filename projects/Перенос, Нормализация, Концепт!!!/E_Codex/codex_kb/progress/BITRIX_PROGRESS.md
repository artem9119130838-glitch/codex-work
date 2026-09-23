# Bitrix Progress

Дата обновления: 2026-05-10

## Status

Bitrix is planned as the task/CRM target for n8n workflows. Credentials and exact entity mapping are not finalized.

## Known Target

- Task creation through Bitrix REST.
- Planned method: `tasks.task.add`.
- Required scopes: `tasks`, `user`.

## Blockers

- Full Bitrix webhook URL must not be stored in markdown.
- User IDs and employee mapping are unknown.
- Deal/task choice for tender processing is not finalized.

## Next

- Create or confirm incoming webhook.
- Record non-secret placeholder and storage location for secret.
- Build employee/user ID map outside public markdown if sensitive.
