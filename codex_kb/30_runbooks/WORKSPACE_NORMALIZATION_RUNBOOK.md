# Workspace Normalization Runbook

Дата: 2026-05-29

Scope: documentation/templates/registry changes and safe, reversible file operations.

## Reversibility rule (mandatory)

- Before any move/rename, perform a **dry-run** that prints the exact list of planned changes.
- Mass deletion is forbidden.
- Allowed operations are reversible only:
  - copy;
  - rename;
  - move **after dry-run**;
  - archive (move into ARCHIVE/ with a clear reason and an easy rollback path).

## Dry-run examples (PowerShell)

- Rename preview: Rename-Item ... -WhatIf
- Move preview: Move-Item ... -WhatIf
- Copy preview: Copy-Item ... -WhatIf

## Dry-run protocol template

- Planned changes (dry-run output):
- Preconditions:
- Execution command(s):
- Rollback command(s):
- Verification:
- Notes: