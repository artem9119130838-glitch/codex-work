````md
# n8n / 1C OData / PostgreSQL Marketing DB Ingestion — Current State and Continuation Plan

## 1. Project goal

The workflow imports marketing/CRM data from 1C OData into PostgreSQL marketing DB.

Current target entities:

1. 1C Leads  
   Source: `Catalog_Лиды`

2. Lead contacts  
   Source: `Catalog_КонтактыЛидов`

3. Buyer / customer counterparties  
   Source planned, not fully implemented yet: `Catalog_Контрагенты`

4. Buyer contacts  
   Source planned, not fully implemented yet: `Catalog_КонтактныеЛица`

PostgreSQL target tables:

- `onec_owners`
- `onec_contacts`
- `ingestion_cursors`
- `ingestion_event_log`

---

# 2. What has already been fixed

## 2.1 Lead import now works

The lead flow now loads `Catalog_Лиды` into `onec_owners`.

Current main flow:

```text
Load cursors
→ Decide mode
→ Gate schedule
→ Fetch lead folders
→ Fetch tags catalog
→ Restore decide context
→ IF mode=backfill
→ Fetch leads batch (backfill)
→ Validate backfill non-empty
→ IF alert
→ Normalize owner
→ IF owner skipped=false
→ Upsert onec_owners
````

Important fix:

`Fetch lead folders` and `Fetch tags catalog` are only helper dictionaries. Their output must not be passed into `Fetch leads batch`.

A new node was added:

```text
Restore decide context
```

Code:

```js
const decide = $items('Decide mode', 0, 0)?.[0]?.json;

if (!decide) {
  throw new Error('Decide mode context is missing');
}

return [{
  json: decide,
}];
```

Correct connection:

```text
Fetch tags catalog
→ Restore decide context
→ IF mode=backfill
```

The old direct connection must NOT exist:

```text
Fetch tags catalog → IF mode=backfill
```

---

## 2.2 Converted lead detection was fixed

Initial mistake:

The workflow incorrectly assumed there was a direct 1C field:

```text
ПереведенВПокупателя
```

But in actual OData payload this is not a separate field. It is a value inside:

```json
"ВариантЗавершения": "ПереведенВПокупателя"
```

Correct logic in `Normalize owner`:

```js
const finishVariantRaw = typeof row[finishVariantKey] === 'string'
  ? row[finishVariantKey].trim()
  : '';

const finishVariantNorm = finishVariantRaw
  .toLowerCase()
  .replace(/\s+/g, '');

const convertedBy1c =
  finishVariantNorm === 'переведенвпокупателя' ||
  finishVariantNorm === 'переведёнвпокупателя';

const converted = convertedBy1c || convertedByText;
```

Expected output for converted leads:

```json
{
  "owner_converted_to_customer": true,
  "owner_converted_to_customer_1c": true,
  "owner_raw_converted_value": "ПереведенВПокупателя"
}
```

Important:

`КонтактыПеренесены` is not the same as “lead converted to buyer”. It is stored only as a separate diagnostic flag:

```json
"owner_contacts_transferred": false
```

---

## 2.3 `Upsert onec_owners` was fixed

The node `Upsert onec_owners` originally had wrong content: JavaScript code from `Normalize owner` was accidentally placed into PostgreSQL Query.

That was wrong because PostgreSQL Query must contain SQL, not JS.

Now the node uses proper SQL:

```text
INSERT INTO onec_owners (...)
VALUES (...)
ON CONFLICT (owner_entity, owner_ref_key)
DO UPDATE SET ...
RETURNING ...
```

Important columns added to `onec_owners`:

```sql
alter table onec_owners
  add column if not exists owner_created_at timestamptz,
  add column if not exists owner_updated_at timestamptz,
  add column if not exists owner_converted_to_customer_1c boolean,
  add column if not exists owner_contacts_transferred boolean,
  add column if not exists owner_converted_detected_by_text boolean,
  add column if not exists owner_raw_converted_value text,
  add column if not exists owner_raw_contacts_transferred_value text,
  add column if not exists buyer_order_found boolean default false,
  add column if not exists buyer_order_ref_key uuid,
  add column if not exists buyer_ref_key uuid,
  add column if not exists buyer_name text;
```

Important SQL type fixes:

Some columns in PostgreSQL are `text[]`, but query parameters are passed as JSON strings from n8n using `JSON.stringify(...)`.

Therefore SQL must convert JSONB arrays to PostgreSQL `text[]`:

```sql
coalesce(array(select jsonb_array_elements_text($27::jsonb)), array[]::text[])
```

Known mappings in `Upsert onec_owners`:

```text
$27 owner_tags_text       text[]
$28 owner_sites           text[]
$29 owner_addresses       jsonb
$30 owner_contact_names   text[]
$31 owner_contact_count   int
$32 owner_contact_emails  text[]
$33 owner_contact_phones  text[]
$34 owner_all_emails      text[]
$35 owner_all_phones      text[]
```

---

## 2.4 Lead contacts now load correctly

Current flow:

```text
Upsert onec_owners
→ Fetch lead contacts for owner
→ Normalize contact
→ IF contact skipped=false
→ Upsert onec_contacts
```

Main issue found:

Many leads have no separate records in:

```text
Catalog_КонтактыЛидов
```

But they do have phone/email directly in the lead card:

```text
Адреса, телефоны
```

Examples:

* phone in lead card
* email in lead card
* no separate contact person in the 1C lead contacts list

The workflow was previously skipping these leads with:

```json
"reason": "0 contacts for owner"
```

This was wrong.

Fix:

`Normalize contact` now creates a synthetic owner-level contact if `Catalog_КонтактыЛидов` returns empty but the owner itself has contact data.

Synthetic contact fields:

```json
{
  "synthetic_contact": true,
  "contact_entity": "Catalog_Лиды_OwnerContact",
  "contact_ref_key": "<owner_ref_key>",
  "owner_entity": "Catalog_Лиды",
  "owner_ref_key": "<owner_ref_key>",
  "contact_role": "owner_level_contact"
}
```

This prevents losing phone/email from the lead card.

After this fix:

```text
0 leads were skipped due to missing contacts
```

---

## 2.5 Important contact model decision

The workflow currently writes two possible types of lead contact rows into `onec_contacts`:

### Real lead contact

From:

```text
Catalog_КонтактыЛидов
```

Example:

```json
{
  "contact_entity": "Catalog_КонтактыЛидов",
  "contact_ref_key": "<1C contact Ref_Key>",
  "owner_entity": "Catalog_Лиды",
  "owner_ref_key": "<lead Ref_Key>"
}
```

### Synthetic owner-level lead contact

Created from lead card phone/email:

```json
{
  "contact_entity": "Catalog_Лиды_OwnerContact",
  "contact_ref_key": "<lead Ref_Key>",
  "owner_entity": "Catalog_Лиды",
  "owner_ref_key": "<lead Ref_Key>"
}
```

This is intentional.

Synthetic contacts do not overwrite real contacts because `contact_entity` is different.

---

## 2.6 Backfill cursor was fixed

Original cursor used only `ДатаСоздания`.

Problem:

Many leads have identical `ДатаСоздания`, for example:

```text
2022-10-03T00:00:00
```

If cursor advances by date only, two bad things can happen:

1. Same 200 leads are loaded repeatedly.
2. Some leads with the same date can be skipped.

Fix:

Backfill now uses `$skip`.

Backfill logic:

```text
1st run:  $skip=0,   $top=200
2nd run:  $skip=200, $top=200
3rd run:  $skip=400, $top=200
...
```

This is automatic. The user does not manually change skip.

Cursor is stored in:

```text
ingestion_cursors
```

New cursor:

```text
leads_backfill_skip
```

Current cursor state after testing:

```text
leads_backfill_skip = 400
leads_backfill_done = 0
```

Correct backfill behavior confirmed:

```json
{
  "previous_backfill_skip": 200,
  "next_backfill_skip": 400,
  "owners_loaded": 200,
  "backfill_done": false
}
```

---

## 2.7 `Decide mode` fixed for multiple cursor rows

Problem:

`Load cursors` returns multiple rows, but old `Decide mode` code did not properly read all input items.

Correct code pattern:

```js
const rows = $input.all().map((item) => item.json);
```

Not:

```js
const rows = Array.isArray($json) ? $json : [];
```

Because in n8n, multiple SQL result rows arrive as multiple input items.

Correct `Decide mode` output now includes:

```json
{
  "mode": "backfill",
  "source": "ingestion",
  "entity": "Catalog_Лиды",
  "backfill_created_at": "2022-09-01T00:00:00Z",
  "backfill_skip": 400,
  "daily_last_run_at": "...",
  "batch_size": 200,
  "lookback_days": 3
}
```

---

# 3. Current working state

The workflow now correctly handles:

```text
Catalog_Лиды
→ normalize leads
→ upsert leads into onec_owners
→ fetch lead contacts
→ normalize real lead contacts
→ create synthetic contact from lead-level phone/email if no separate contacts exist
→ upsert contacts into onec_contacts
→ move backfill cursor by skip
```

Current confirmed successful behavior:

```text
skip 200 → loaded 200 leads → skip updated to 400
```

The lead part can now be saved as:

```text
v2.3 leads + lead contacts + synthetic contacts + backfill cursor fixed
```

---

# 4. What is NOT ready yet

## 4.1 Buyers are not fully loaded

Current workflow does NOT fully import all buyers/customers.

It only tries this limited path:

```text
Converted lead
→ Fetch buyer order for owner
→ Document_ЗаказПокупателя?$filter=Лид_Key eq guid'<lead_ref_key>'
```

This is not enough.

Reason:

In 1C, a lead may be converted into a buyer/customer without there being a `Document_ЗаказПокупателя` linked by `Лид_Key`.

Examples discovered:

* `БАШЭЛ`
* `СПБ ЗПС`
* `Жорова Жанна Сергеевна ИП`

They exist as buyers/customers in 1C, and may even have sales, but current workflow does not load them as buyers because it searches only by sales order linked to the lead.

---

## 4.2 `Fetch buyer order for owner` is misleading

Current node name:

```text
Fetch buyer order for owner
```

But logically it does not resolve a buyer.

It only tries to find a sales order document by lead:

```text
Document_ЗаказПокупателя by Лид_Key
```

Suggested rename:

```text
Try fetch sales order by lead
```

Current IF:

```text
IF buyer_order_found=true
```

Suggested rename:

```text
IF sales_order_found=true
```

This branch may remain as optional enrichment, but it must not be treated as the main buyer import mechanism.

---

## 4.3 Buyer contacts are not fully loaded

Contacts from buyer/customer cards are not imported unless buyer was resolved through `Document_ЗаказПокупателя`.

This misses buyer contacts visible in 1C under customer cards.

Examples:

### БАШЭЛ

Lead card has:

```text
sklad@bashel.pro
8-800-600-53-31
```

Buyer card has contact:

```text
Феликс Нафиков
felix@bashel.pro
```

Current lead workflow loads only the lead/synthetic contact, not the buyer contact.

### СПБ ЗПС

Lead has its own lead contacts.

Buyer/customer card has separate buyer contacts.

Current workflow does not fully load buyer contacts.

---

# 5. Correct next-stage architecture

Need to add a separate full buyer/customer flow.

## 5.1 New buyer flow

Add independent branch:

```text
Fetch buyers batch
→ Normalize owner buyer
→ IF buyer owner skipped=false
→ Upsert onec_owners
→ Fetch buyer contacts for buyer
→ Normalize contact buyer direct
→ IF contact skipped=false
→ Upsert onec_contacts
```

Source:

```text
Catalog_Контрагенты
```

Contacts source:

```text
Catalog_КонтактныеЛица
```

Target tables remain:

```text
onec_owners
onec_contacts
```

But buyers must be stored as:

```json
{
  "owner_entity": "Catalog_Контрагенты",
  "owner_ref_key": "<Контрагент Ref_Key>",
  "owner_is_buyer": true
}
```

Lead owners remain:

```json
{
  "owner_entity": "Catalog_Лиды",
  "owner_ref_key": "<Lead Ref_Key>"
}
```

This allows both lead and buyer records to coexist.

---

## 5.2 Buyer owner normalization

Need a new node:

```text
Normalize owner buyer
```

It should normalize `Catalog_Контрагенты` into the same `onec_owners` structure as leads, without losing fields.

Expected output fields should match existing `Upsert onec_owners` parameters:

```text
owner_entity
owner_ref_key
owner_name
owner_inn
owner_group
owner_tags
owner_notes
owner_address
owner_site
raw_payload
owner_source_entity
owner_status
owner_is_folder
owner_is_buyer
owner_is_supplier
owner_classification
owner_is_junk
owner_junk_reason
owner_converted_to_customer
owner_search_emails
owner_search_phones
owner_display_name
owner_company_name
owner_topic
owner_source_key
owner_group_path
owner_tags_text
owner_sites
owner_addresses
owner_contact_names
owner_contact_count
owner_contact_emails
owner_contact_phones
owner_all_emails
owner_all_phones
owner_notes_compiled
owner_is_important
owner_importance_score
owner_importance_reason
owner_created_at
owner_updated_at
owner_converted_to_customer_1c
owner_contacts_transferred
owner_converted_detected_by_text
owner_raw_converted_value
owner_raw_contacts_transferred_value
```

For buyers:

```json
{
  "owner_entity": "Catalog_Контрагенты",
  "owner_source_entity": "Catalog_Контрагенты",
  "owner_is_buyer": true,
  "owner_is_supplier": false or value from 1C if available,
  "owner_converted_to_customer": false
}
```

---

## 5.3 Buyer contact fetching

For each buyer owner:

```text
Catalog_КонтактныеЛица?$filter=Parent_Key eq guid'<buyer_ref_key>' and IsFolder eq false and DeletionMark eq false
```

Need a dedicated node:

```text
Fetch buyer contacts for buyer
```

The existing `Fetch buyer contacts for owner` can probably be reused if it receives:

```json
{
  "buyer_ref_key": "<buyer Ref_Key>"
}
```

But for a clean architecture, better create a new node that uses:

```js
const buyerRef = $json.owner_ref_key;
```

because in the standalone buyer flow the current owner is already the buyer.

---

## 5.4 Buyer contact normalization

Need a separate node:

```text
Normalize contact buyer direct
```

It should output contact rows into `onec_contacts` like:

```json
{
  "contact_entity": "Catalog_КонтактныеЛица",
  "contact_ref_key": "<contact Ref_Key>",
  "owner_entity": "Catalog_Контрагенты",
  "owner_ref_key": "<buyer Ref_Key>",
  "contact_name": "...",
  "emails": ["..."],
  "phones": ["..."],
  "contact_channels": [...],
  "raw_payload": {...}
}
```

Also create synthetic buyer contact from buyer card-level phone/email when no separate contact persons exist, same as lead synthetic contacts.

Suggested synthetic buyer contact:

```json
{
  "contact_entity": "Catalog_Контрагенты_OwnerContact",
  "contact_ref_key": "<buyer Ref_Key>",
  "owner_entity": "Catalog_Контрагенты",
  "owner_ref_key": "<buyer Ref_Key>",
  "synthetic_contact": true,
  "contact_role": "owner_level_buyer_contact"
}
```

---

# 6. Buyer backfill cursor plan

Do not mix buyer cursor with lead cursor.

Create separate cursors:

```text
buyers_backfill_skip
buyers_backfill_done
buyers_daily_last_run_at
buyers_backfill_created_at
```

Entity:

```text
Catalog_Контрагенты
```

Example SQL to initialize:

```sql
insert into ingestion_cursors(source, entity, cursor_kind, cursor_value, cursor_meta)
values
  ('ingestion', 'Catalog_Контрагенты', 'buyers_backfill_skip', '0', '{}'::jsonb),
  ('ingestion', 'Catalog_Контрагенты', 'buyers_backfill_done', '0', '{}'::jsonb),
  ('ingestion', 'Catalog_Контрагенты', 'buyers_backfill_created_at', '2022-09-01T00:00:00Z', '{}'::jsonb)
on conflict (source, entity, cursor_kind)
do nothing;
```

Backfill should also use `$skip` for safety.

---

# 7. Suggested buyer fetch URL

Need to confirm exact 1C OData fields, but likely:

```text
Catalog_Контрагенты
```

Possible filter:

```text
IsFolder eq false and DeletionMark eq false
```

Possibly buyer-only filter if field exists:

```text
Покупатель eq true
```

But if unsure, load all non-folder counterparties first and classify:

```text
owner_is_buyer = true if row.Покупатель === true
owner_is_supplier = true if row.Поставщик === true
```

URL draft:

```js
={{ (() => {
  const p = $json;
  const top = Number(p.batch_size || 200);
  const skip = Number(p.backfill_skip || 0);

  return `http://artem.medianasoft.spb.ru/unf/odata/standard.odata/Catalog_%D0%9A%D0%BE%D0%BD%D1%82%D1%80%D0%B0%D0%B3%D0%B5%D0%BD%D1%82%D1%8B?$filter=IsFolder%20eq%20false%20and%20DeletionMark%20eq%20false&$orderby=Description%20asc,Ref_Key%20asc&$skip=${skip}&$top=${top}&$format=json`;
})() }}
```

Need to check if `Description asc,Ref_Key asc` is accepted by 1C OData.

---

# 8. Important warning about n8n item context

Avoid this pattern in processing nodes:

```js
$items('Some node', 0, 0)[0]
```

This often returns the first item of the batch and causes wrong owner/contact pairing.

Use one of these instead:

1. Current `$json` if the required owner fields are passed forward.
2. `$input.all()` and indexed loop if processing multiple input items.
3. Paired-item-aware lookup only if verified in n8n.

This bug previously caused contacts to be fetched for only the first lead in the batch.

---

# 9. Important warning about helper dictionaries

`Fetch lead folders` and `Fetch tags catalog` are helper dictionary nodes.

They must not become the main `$json` context for lead fetching.

That is why `Restore decide context` was added.

If buyer flow also needs helper dictionaries, do the same:

```text
Fetch helper dictionaries
→ Restore buyer decide context
→ Fetch buyers batch
```

---

# 10. Current buyer-order branch status

Current branch:

```text
IF owner converted_to_customer
→ Fetch buyer order for owner
→ Normalize buyer order
→ IF buyer_order_found=true
→ Update owner converted from buyer order
→ Fetch buyer contacts for owner
→ Normalize contact buyer
→ Upsert onec_contacts
```

Fixed:

`Normalize buyer order` now processes all input items, not only one.

Observed after fix:

```text
IF owner converted_to_customer = 25 items
Fetch buyer order for owner = 25 items
Normalize buyer order = 25 items
IF buyer_order_found=true = 0 true / 25 false
```

This is technically correct, but business-wise insufficient.

Reason:

Most converted leads do not have `Document_ЗаказПокупателя` linked by `Лид_Key`.

Do not rely on this branch as buyer loading.

---

# 11. Recommended next steps

## Step 1 — Save current workflow

Save current version as:

```text
v2.3 leads + lead contacts + synthetic contacts + backfill cursor fixed
```

Do not continue editing the same version without backup.

---

## Step 2 — Let lead backfill continue automatically

Current lead cursor:

```text
leads_backfill_skip = 400
leads_backfill_done = 0
```

Next automatic run should load:

```text
$skip=400
```

Then update to:

```text
leads_backfill_skip = 600
```

Do not manually reset `leads_backfill_skip` unless intentionally restarting lead backfill.

---

## Step 3 — Create a new branch for buyers

Implement separate `Catalog_Контрагенты` import.

Do not try to solve buyers through `Document_ЗаказПокупателя`.

---

## Step 4 — Add buyer contacts

Import:

```text
Catalog_КонтактныеЛица
```

by:

```text
Parent_Key = buyer owner_ref_key
```

Also create synthetic buyer owner-level contact from buyer card phone/email.

---

## Step 5 — Later: link leads to buyers

After both leads and buyers are loaded, add optional linking logic.

Possible matching keys:

```text
INN
email
phone
normalized company/person name
1C internal links if found
```

This should probably be a separate table, for example:

```text
onec_owner_links
```

Possible schema:

```sql
create table if not exists onec_owner_links (
  source_owner_entity text not null,
  source_owner_ref_key uuid not null,
  target_owner_entity text not null,
  target_owner_ref_key uuid not null,
  link_type text not null,
  confidence_score int,
  details jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  primary key (source_owner_entity, source_owner_ref_key, target_owner_entity, target_owner_ref_key, link_type)
);
```

Possible link types:

```text
converted_lead_to_buyer_by_1c
matched_by_inn
matched_by_email
matched_by_phone
matched_by_name
matched_by_sales_order
```

---

# 12. Current unresolved questions

Need to inspect `Catalog_Контрагенты` OData payload to confirm exact field names for:

```text
Покупатель
Поставщик
ИНН
КПП
НаименованиеПолное
АдресЭПДляПоиска
НомерТелефонаДляПоиска
КонтактнаяИнформация
ДатаСоздания
ДатаИзменения
```

Need to confirm if `Catalog_Контрагенты` supports:

```text
$orderby=Description asc,Ref_Key asc
```

Need to confirm buyer contact structure in:

```text
Catalog_КонтактныеЛица
```

Fields expected are similar to lead contacts:

```text
Ref_Key
Parent_Key
Description
КонтактнаяИнформация
АдресЭП
НомерТелефона
НомерТелефонаБезКодов
Представление
Тип
ДоменноеИмяСервера
Комментарий
ОсновныеСведения
```

---

# 13. Summary for next model

The lead pipeline is now mostly stable.

Do not redo lead fixes unless needed.

Main remaining work is not to patch the existing buyer-order branch, but to add a separate full import pipeline for `Catalog_Контрагенты`.

The existing buyer-order branch may remain as optional enrichment, but it does not solve buyer import.

The most important design rule:

```text
Leads and buyers are separate owner entities.
Lead contacts and buyer contacts are separate contact sources.
Both must be imported independently.
```

```
```
