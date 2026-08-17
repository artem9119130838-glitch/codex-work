# N8N Marketing DB Operator Runbook (v2.2)

Дата: 2026-05-11

Эта инструкция описывает ТОЛЬКО актуальную логику ingestion v2.2.

Ограничения:
- 1C OData: строго read-only.
- Запись только в PostgreSQL `marketing_db`.
- Никакой почты / mailbox / email workflows.

## Канонический workflow

- `E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_ingestion_v2_2_master.json`

Назначение:
- Backfill лидов (owners) пачками по 200 + контакты для этих owners.
- Автопереход в daily sync после завершения backfill.
- Inspectors (качество данных) + лог событий в Postgres.

## Cursor/state (обязательно)

Схема:
- `E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_cursor_state_2026-05-11.sql`

В таблице `ingestion_cursors` используются ключи:
- `leads_backfill_created_at` — ISO datetime, старт backfill (по умолчанию `2022-09-01T00:00:00Z`).
- `leads_backfill_done` — `0/1`.
- `leads_daily_last_run_at` — ISO datetime последнего успешного запуска.

Схема таблицы курсоров: `source`, `entity`, `cursor_kind`, `cursor_value`, `cursor_meta`, `updated_at`.

Seed (пример):

```sql
insert into ingestion_cursors(source,entity,cursor_kind,cursor_value,cursor_meta)
values
  ('ingestion','Catalog_Лиды','leads_backfill_created_at','2022-09-01T00:00:00Z','{}'::jsonb),
  ('ingestion','Catalog_Лиды','leads_backfill_done','0','{}'::jsonb),
  ('ingestion','Catalog_Лиды','leads_daily_last_run_at','2022-09-01T00:00:00Z','{}'::jsonb)
on conflict (source,entity,cursor_kind)
do update set
  cursor_value = excluded.cursor_value,
  cursor_meta = excluded.cursor_meta;
```

## Режимы и частота

В workflow есть два расписания + gating:
- `Cron backfill (30m)` — каждые 30 минут, работает ТОЛЬКО пока `mode=backfill`.
- `Cron daily` — 1 раз в день (сейчас `03:10`), работает ТОЛЬКО когда `mode=daily`.
- `Manual Trigger` — всегда разрешён (smoke test).

`mode` вычисляется из `ingestion_cursors.leads_backfill_done`:
- `0` → backfill
- `1` → daily

Backfill считается завершённым, когда в одном запуске owners загружено меньше `batch_size` (200) — тогда выставляется `leads_backfill_done=1`.

## Inspectors и логирование

### fix_required

- Owner: если отсутствует email ИЛИ phone (по `owner_search_emails` / `owner_search_phones`) → добавляется тег `fix_required` в `onec_owners.owner_tags_text`.
- Contact: если отсутствует email ИЛИ phone → добавляется тег `fix_required` в `onec_contacts.contact_tags`.

### zero_contacts

Если для owner найдено 0 контактов:
- workflow НЕ падает
- событие пишется в Postgres таблицу `public.ingestion_event_log` с `event_type='zero_contacts'`.

### alert (защита от пустых прогонов)

Если OData вернул 0 лидов в батче:
- пишется событие в `public.ingestion_event_log` с `event_type='alert'`
- workflow падает с ошибкой `ALERT: OData returned 0 leads for this run`

Таблица логов создаётся SQL:
- `E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_event_log_table_v2_2.sql`
В SQL уже включены индексы по времени, типу события, `owner_ref_key` и `contact_ref_key`.

## Smoke test (ручной запуск)

1) Импортируй `marketing_db_ingestion_v2_2_master.json`.
2) В Postgres-нодах выбери credential `marketing_db / n8n_marketing`.
3) В HTTP Request нодах выбери credential для 1C OData (read-only).
4) Убедись, что в `ingestion_cursors` есть seed (см. выше).
5) Нажми `Execute workflow` (Manual Trigger).
6) Проверь, что `Upsert onec_owners` и `Upsert onec_contacts` отработали успешно.

