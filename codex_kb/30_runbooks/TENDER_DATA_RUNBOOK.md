# Runbook: Tender Data

## AST GOZ automation

Use DOM automation where possible:

1. Start from filtered registry page.
2. Detect current row.
3. Read hidden row links.
4. Open request documentation link directly.
5. Set consent checkbox.
6. Click main submit and modal confirmation.
7. On lot card, click unload.
8. Return to registry.
9. Apply prepare-documents step after state settles.

## PDF quote to Excel

1. Extract text/tables from PDF.
2. Identify products, quantities, unit prices, totals, weights.
3. Rebuild formulas in Excel.
4. Verify totals match source after rounding.
5. Preserve original PDF.

## Excel lot consolidation

1. Inspect headers in all source workbooks.
2. Normalize columns.
3. Preserve hyperlinks.
4. Deduplicate by business keys:
   - amount + customer;
   - amount + deadline.
5. Prefer richer row when duplicates conflict.
6. Write clean `.xlsx`.
7. Verify row counts and hyperlinks.

## Contract comparison

1. Extract DOCX text.
2. Try PDF text extraction.
3. If PDF is flattened/scanned, compare metadata, page count, and visible key fields manually.
4. Report only confirmed differences.
