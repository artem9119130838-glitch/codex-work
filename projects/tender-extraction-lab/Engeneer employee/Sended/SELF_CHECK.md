# Self Check

Дата обновления: 2026-05-10

This is a local mandatory checklist, not an automatically installed system skill.

Run it mentally or explicitly after code, documentation or workflow changes.

## Checklist

- Did I read `PROGRESS.md` and the relevant domain progress file?
- Did I follow `CHAT_DISPATCHER.md` for this task type?
- Did I check `SECURITY_POLICY.md` before writing commands, workflow examples or docs?
- Did I avoid storing live secrets in permanent files and keep only placeholders or credential names there?
- If I touched server paths or commands, do they match `codex_kb\10_assets\SERVER_VPS.md`?
- If I touched 1C or n8n/1C logic, did I check `codex_kb\progress\1C_PROGRESS.md`?
- If I edited files with Cyrillic, are they UTF-8 with BOM?
- If I changed `00_global`, `20_domains` or `30_runbooks`, is RAG sync needed?
- Did I update `PROGRESS.md` and the relevant domain progress file after meaningful changes?
- Did I avoid modifying archived `chat_exports` unless explicitly asked?

## Failure Response

If any answer is no:

1. Stop before finalizing.
2. Fix the missing file/update/check.
3. Re-run this checklist.
