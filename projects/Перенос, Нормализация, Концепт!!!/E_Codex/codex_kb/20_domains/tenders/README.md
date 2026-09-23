# Domain: Tenders

## Scope

This direction includes:

- AST GOZ site automation;
- tender document downloading;
- lot data extraction;
- PDF quote to Excel conversion;
- Excel lot consolidation and deduplication;
- contract comparison;
- future email intake for tender correspondence.

## Stable workspace references

Older current-state files:

```text
E:\Codex_Work\projects\tenders_ast_goz\legacy_context\CHAT_INDEX.md
E:\Codex_Work\projects\tenders_ast_goz\legacy_context\CURRENT_STATE.md
```

AST GOZ script path from exports:

```text
E:\Codex_Work\scripts\astgoz_tampermonkey\astgoz_dom_runner.user.js
```

Current actual presence of that path should be checked before use.

## AST GOZ automation findings

Preferred approach:

- DOM automation in Firefox/Tampermonkey;
- read hidden row links directly;
- avoid raw mouse coordinate automation.

Known flow:

1. Registry page with filtered list.
2. Detect current row.
3. Read hidden links:
   - request documentation;
   - prepare documents.
4. Open request page.
5. Set consent checkbox.
6. Click main submit.
7. Confirm modal submit.
8. On lot card, click unload.
9. Return and handle prepare-documents state.

Fragile areas:

- return path after unload;
- row/menu state after download;
- prepare-documents step after second return;
- site state changes.

## Excel/PDF tender data

Repeated tasks:

- merge multiple `.xlsx` lot files;
- deduplicate by amount/customer/deadline;
- preserve hyperlinks and formatting;
- convert supplier PDF quotes to Excel with formulas;
- compare DOCX/PDF contracts when PDF may be flattened.

## Future direction

Email intake should feed tender pipeline:

```text
email -> attachments -> table extraction -> tender folder/table -> Bitrix task / 1C / response draft
```

`master_doc.md` also proposes `marketing_db.tenders_archive` for future tender parsing and links to Bitrix24 deals/tasks. Exact schema is still `unknown`.

## Safety

- Do not claim automated text parity if PDF is scanned/flattened.
- Keep manual confirmation for legally/business-critical tender submissions.
- Preserve source files.
