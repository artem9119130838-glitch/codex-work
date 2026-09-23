-- Inspector checks (v2.2)
-- Finds records marked as fix_required and owners without contacts.

-- Owners with missing channels (tagged fix_required)
select
  owner_ref_key,
  owner_name,
  owner_group_path,
  owner_search_emails,
  owner_search_phones,
  owner_tags_text,
  fetched_at
from onec_owners
where
  ('fix_required' = any(owner_tags_text))
  or cardinality(owner_search_emails) = 0
  or cardinality(owner_search_phones) = 0
order by fetched_at desc
limit 200;

-- Contacts with missing channels (tagged fix_required)
select
  contact_ref_key,
  owner_ref_key,
  contact_name,
  emails,
  phones,
  contact_tags,
  fetched_at
from onec_contacts
where
  (contact_tags @> '["fix_required"]'::jsonb)
  or cardinality(emails) = 0
  or cardinality(phones) = 0
order by fetched_at desc
limit 200;

-- Owners that currently have 0 contacts in snapshot
select
  o.owner_ref_key,
  o.owner_name,
  o.fetched_at
from onec_owners o
left join onec_contacts c
  on c.owner_entity = o.owner_entity
 and c.owner_ref_key = o.owner_ref_key
group by o.owner_ref_key, o.owner_name, o.fetched_at
having count(c.contact_ref_key) = 0
order by o.fetched_at desc
limit 200;
