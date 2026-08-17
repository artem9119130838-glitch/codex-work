# Marketing DB Ingestion Report

Правило: в этом файле фиксируются только факты запусков и короткие заметки о ручных правках/ошибках, найденных во время smoke test.
Никаких секретов, никаких логов чата.

## Format

- `run_at`: ISO datetime
- `owners_upserted`: N
- `contacts_upserted`: N
- `fix_required_owner_ids`: [uuid,...] — Email/Phone отсутствует
- `fix_required_contact_ids`: [uuid,...] — Email/Phone отсутствует
- `zero_contacts_owner_ids`: [uuid,...] — по owner не найдено контактов

## Runs

## Manual smoke notes

- 2026-05-11: `Normalize owner` падал из-за битого JS-токена между `fixRequired` и следующим `if`; исправление сделано вручную в n8n.
- 2026-05-11: `Fetch lead contacts for owner` возвращал `400` с OData `$filter` parse error из-за неверной/пустой даты в URL; исправление сделано вручную в n8n.
- 2026-05-11: `Throw alert` срабатывал намеренно после `Log alert`; для smoke test ветку временно обходили вручную, затем нужно вернуть обратно.
- 2026-05-11: `Load cursors` / `Update cursors` пришлось привести к реальной схеме `ingestion_cursors` (`source`, `entity`, `cursor_kind`, `cursor_value`, `cursor_meta`).

## 2026-05-12 notes

- `Validate backfill non-empty` и `Validate daily non-empty` сохраняют исходный payload и добавляют `alert`, `alert_type`, `alert_message`, `rows_count`, `mode`.
- `IF alert` проверяет boolean `alert`.
- `Normalize owner` читает `Fetch lead folders` и `Fetch tags catalog` через `$items(...)`; helper-ноды должны выполниться в том же run.
- Для converted lead добавлена buyer-ветка: `Fetch buyer order for owner` → `Normalize buyer order` → `Fetch buyer contacts for owner` → `Normalize contact buyer`.
- `ingestion_cursors` вручную возвращён к backfill-start: `leads_backfill_created_at = 2022-09-01T00:00:00Z`, `leads_backfill_done = 0`, `leads_daily_last_run_at = 2022-09-01T00:00:00Z`; `leads_backfill_skip` удалён.
- `Update cursors` приведён к схеме `ingestion_cursors(source, entity, cursor_kind, cursor_value, cursor_meta)`.
- `Throw alert` оставлен только на alert-ветке и использует намеренный stop после `Log alert`.
- Факт проверки БД после ручного backfill-run:
  - `onec_owners = 200`
  - `onec_contacts = 1`
  - `ingestion_cursors.leads_backfill_created_at = 2023-06-30T00:00:00.000Z`
  - `ingestion_cursors.leads_backfill_done = 0`
- Это означает:
  - cursor update path отработал;
  - owner batch был записан;
  - contact branch отработал не по полному owner batch.
- Контрольный кейс `Акватон`:
  - owner присутствует в `onec_owners`;
  - `owner_converted_to_customer` не выставлен;
  - контакты по `owner_ref_key` отсутствуют.
- Старый файл `erorк lead contacts.md` считать hypothesis-note, а не каноническим диагнозом; опираться на факты из БД и current workflow JSON.
