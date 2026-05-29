# tender-extraction-lab

Clean lab project for tender extraction experiments:

- `data/gold/`: human-validated benchmark datasets (tracked).
- `scripts/eval/`: regression/evaluation scripts (tracked).
- `scripts/batch/`: batch runners/orchestrators (tracked).
- `legacy/old_project/`: copied reference-only code and evidence from the old `GOZ` project (tracked, but not modified).
- `data/raw_sample/`: optional local-only tender samples (**ignored by git**).

## Migration

The migration source of truth is `.codex/migration-manifest.csv`.

To copy only the minimal needed subset (gold + eval/batch + legacy evidence):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\migration\copy_from_manifest.ps1
```

## Smoke test

After migration copy, try:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke\run_smoke_eval.ps1
```

