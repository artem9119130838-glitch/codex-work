-- Cursor seed templates for automated ingestion workflow (backfill + daily).
-- Use this only after applying: marketing_db_ingestion_cursor_state_2026-05-11.sql
--
-- IMPORTANT: This file contains no secrets.

-- Backfill cursor: process leads in ascending order of DateCreated via $skip/$top.
-- Cursor value is the current skip offset (number of rows already processed).
insert into ingestion_cursors (source, entity, cursor_kind, cursor_value, cursor_meta)
values (
  'ingestion',
  'Catalog_Лиды',
  'leads_backfill_skip',
  '0',
  jsonb_build_object(
    'mode', 'backfill',
    'batch_size', 200,
    'odata_orderby', 'ДатаСоздания asc',
    'note', 'Backfill from 2022-09-01 (filter is enforced in workflow URL)'
  )
)
on conflict (source, entity, cursor_kind)
do update set
  cursor_value = excluded.cursor_value,
  cursor_meta = excluded.cursor_meta,
  updated_at = now();

-- Daily cursor: last successful sync timestamp (UTC ISO).
-- Used to fetch a small rolling window for updates; initial value is a safe low watermark.
insert into ingestion_cursors (source, entity, cursor_kind, cursor_value, cursor_meta)
values (
  'ingestion',
  'Catalog_Лиды',
  'leads_daily_last_run_at',
  '2022-09-01T00:00:00Z',
  jsonb_build_object(
    'mode', 'daily',
    'daily_window_days', 3,
    'batch_size', 200,
    'note', 'Daily sync re-fetches a rolling window (created/changed recently) and upserts idempotently'
  )
)
on conflict (source, entity, cursor_kind)
do update set
  cursor_value = excluded.cursor_value,
  cursor_meta = excluded.cursor_meta,
  updated_at = now();

