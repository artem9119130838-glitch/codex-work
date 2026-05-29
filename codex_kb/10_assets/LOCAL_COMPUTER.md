# Asset: Local Computer

## Workspace

Primary shared workspace:

```text
E:\Codex_Work
```

Purpose:

- central Codex workspace;
- stable knowledge base;
- active project files;
- archived old exports and one-off outputs;
- portable context between chats and possibly machines.

## Important Root Items

```text
E:\Codex_Work\AGENTS.md
E:\Codex_Work\CODEX_START_HERE.md
E:\Codex_Work\PROGRESS.md
E:\Codex_Work\CHAT_DISPATCHER.md
E:\Codex_Work\ГДЕ_ЧТО_ЛЕЖИТ.md
E:\Codex_Work\codex_kb
E:\Codex_Work\projects
E:\Codex_Work\chat_exports
E:\Codex_Work\Архив
```

## Inventory

Inventory folder:

```text
E:\Codex_Work\projects\local_inventory\inventory
```

Known scripts from exports:

```text
weekly_run.bat
open_latest_report.bat
make_snapshot.ps1
compare_snapshots.ps1
export_installed_programs.ps1
inventory_common.ps1
inventory_config.ps1
```

Workflow:

1. First run creates baseline.
2. Later runs compare new/changed/deleted files.
3. Review reports in Excel.
4. Move important changed data to `E:` manually or with FreeFileSync.

## Old AST GOZ Context

The older `CHAT_INDEX.md` and `CURRENT_STATE.md` mainly describe AST GOZ automation. They now live under:

```text
E:\Codex_Work\projects\tenders_ast_goz\legacy_context
```

They remain useful, but new global context should live in `codex_kb`.

## Known local paths from old work

- `C:\Users\Artem\Downloads\GOZ`
- `D:\server-backups\full-backup-2026-05-03_11-52`
- `E:\Codex_Work\Архив\old_outputs`
- `E:\Codex_Work\projects\n8n_bitrix\source_docs`

## Safety

- Do not overwrite old exports.
- Keep `chat_exports` as archive.
- Put reusable, stable facts into `codex_kb`.
- Put active working files into `projects`.
- Put one-off or superseded material into `Архив`.
