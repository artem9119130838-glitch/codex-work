-- marketing_db ingestion cursor/state
-- Restored by Codex (no secrets). Date: 2026-05-11
-- Purpose: persist ingestion cursors for n8n workflows (read/write in Postgres only).

create table if not exists ingestion_cursors (
  cursor_scope text not null,
  cursor_entity text not null,
  cursor_key text not null,
  cursor_value text not null,
  cursor_meta jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (cursor_scope, cursor_entity, cursor_key)
);

create index if not exists ingestion_cursors_entity_key_idx
  on ingestion_cursors (cursor_entity, cursor_key);

create or replace function ingestion_cursors_touch_updated_at()
returns trigger as $$
begin
  new.updated_at := now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_ingestion_cursors_touch on ingestion_cursors;
create trigger trg_ingestion_cursors_touch
before update on ingestion_cursors
for each row execute function ingestion_cursors_touch_updated_at();
