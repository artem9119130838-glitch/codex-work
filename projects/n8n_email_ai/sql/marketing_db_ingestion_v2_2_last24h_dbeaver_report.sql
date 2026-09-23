-- Master ingestion v2.2: 24h report (single query)
-- Returns a summary row plus detailed event log rows.

with
params as (
  select now() - interval '24 hours' as since_at
),
owners_24h as (
  select count(*) as owners_upserted
  from onec_owners o, params p
  where o.fetched_at >= p.since_at
),
contacts_24h as (
  select count(*) as contacts_upserted
  from onec_contacts c, params p
  where c.fetched_at >= p.since_at
),
contacts_linked_24h as (
  select count(*) as contacts_linked
  from onec_contacts c, params p
  where c.fetched_at >= p.since_at
    and c.owner_ref_key is not null
),
logs_24h as (
  select l.*
  from ingestion_event_log l, params p
  where l.event_at >= p.since_at
)
select
  'summary' as row_type,
  (select since_at from params) as since_at,
  (select owners_upserted from owners_24h) as owners_upserted,
  (select contacts_upserted from contacts_24h) as contacts_upserted,
  (select contacts_linked from contacts_linked_24h) as contacts_linked,
  null::bigint as event_id,
  null::timestamptz as event_at,
  null::text as workflow_name,
  null::text as mode,
  null::text as event_type,
  null::text as severity,
  null::uuid as owner_ref_key,
  null::uuid as contact_ref_key,
  null::text as message,
  null::jsonb as details

union all

select
  'log' as row_type,
  (select since_at from params) as since_at,
  null::bigint as owners_upserted,
  null::bigint as contacts_upserted,
  null::bigint as contacts_linked,
  l.event_id,
  l.event_at,
  l.workflow_name,
  l.mode,
  l.event_type,
  l.severity,
  l.owner_ref_key,
  l.contact_ref_key,
  l.message,
  l.details
from logs_24h l
order by row_type, event_at desc nulls last;
