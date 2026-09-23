# Runbook: Local Inventory

## Folder

```text
E:\Codex_Work\projects\local_inventory\inventory
```

## Weekly run

```text
weekly_run.bat
```

First run creates baseline only.

Second and later runs create comparison reports:

- new files;
- changed files;
- deleted files.

Open latest report:

```text
open_latest_report.bat
```

## Review

1. Filter by new/changed/deleted.
2. Focus on user folders and known work areas.
3. Ignore system/app-cache noise unless investigating storage.
4. Copy important changed data to `E:`.
5. Use BCU for unwanted programs, then leftover scan.

## Optional cleanup

```text
Dism.exe /online /Cleanup-Image /StartComponentCleanup
```
