# GitHub Sync Checklist (Workspace)

Goal: sync E:\Codex_Work across two PCs safely.

## Preconditions

## Tools

- Git CLI must be installed on the PC running sync. (Currently, git is not found in PATH on this machine.)

- Do **not** do the first commit/push until the **pilot project** is normalized (minimal .codex/ scaffold + registry + docs).
- Never commit secrets.

## What to commit

- Workspace master files in root (e.g., AGENTS.md, CODEX_START_HERE.md, CHAT_DISPATCHER.md, PROGRESS.md, ГДЕ_ЧТО_ЛЕЖИТ.md, PROJECTS_REGISTRY.md).
- codex_kb/ (policies, runbooks, skills, templates).
- _templates/.
- Project code and stable artifacts:
  - projects/*/src/
  - projects/*/scripts/
  - projects/*/data/gold/
  - projects/*/.codex/ **excluding** projects/*/.codex/stages/
  - projects/*/PROJECT_HANDOFF.md, projects/*/AGENTS.md, projects/*/docs/ (if present)

## What NOT to commit

- Raw tender inputs / incoming dumps.
- Large legacy folders.
- rchive/, ARCHIVE/.
- Caches (__pycache__, _cache_blocks, etc.).
- model_outputs/.
- atches/, candidates/.
- Temporary reports.
- .env and any tokens/keys.

## Two-PC sync order

1) PC#1: Normalize the pilot project (docs-only normalization; add .codex/ scaffold; update registry).
2) PC#1: Initialize git repo, add .gitignore, commit, push.
3) PC#2: Clone/pull.
4) Ongoing work:
   - Prefer feature branches + PRs, or strictly serialize changes by agreement.
   - Do not edit the same knowledge files concurrently on two PCs.

## Secret guardrails

- .env is local-only and must never be committed.
- Use placeholders in docs, e.g. ${ONEC_ODATA_PASSWORD}.