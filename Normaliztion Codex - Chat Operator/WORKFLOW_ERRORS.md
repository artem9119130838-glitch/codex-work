# Workflow Errors / Known Risks

This file does **not** list old debugging history.  
It lists only the workflow risks that remain useful for future continuation.

## Canonical workflow

- `marketing_db_ingestion_v2_2_master_CANONICAL_FINAL.json`

## What is believed to be solved

- 1C read-only ingestion architecture
- owner upsert flow
- helper dictionary separation
- cursor/state operational layer
- final canonical export for ingestion

## What should be verified first if work continues

### 1. Contact branch behavior

If contacts look incomplete, verify that the contact path still processes the whole owner batch and not only a reduced subset.

Check:

- owner count vs contact count after a controlled run
- whether per-owner contact nodes receive the expected batch items

### 2. Converted lead / buyer detection

Converted leads depend on correct interpretation of 1C completion state.

Check:

- `ВариантЗавершения`
- owner flags for converted leads
- buyer-related branch output

### 3. Backfill progression

Backfill must move forward without rereading the same first block forever.

Check:

- cursor values
- ordering
- skip / paging behavior
- resulting owner count growth between runs

### 4. Smoke-test discipline

Before any new feature work:

1. import the canonical workflow;
2. run one controlled test;
3. compare DB results;
4. only then continue.

## Recommendation for the next engineer

Do **not** redesign ingestion first.

Use the current canonical workflow as the base and move attention to:

1. email intake pilot
2. deterministic email matching
3. short client summaries
4. draft preview

If ingestion must be touched, do it with narrow, measurable fixes only.

