# PROJECT_HANDOFF — tender-extraction-lab

Дата обновления: 2026-05-29
Статус: Active (pilot normalization)
Приоритет: P0

## 1. Purpose
A sandbox project to validate workspace normalization rules for tender extraction pipelines.

## 2. Canonical folders
- incoming/ — raw inputs (do not commit)
- processed/ — normalized intermediate artifacts (usually do not commit)
- outputs/ — final outputs (commit policy depends on size)
- data/ — curated data (commit data/gold/ only)
- schemas/ — schema definitions (commit)
- scripts/ — utilities (commit)
- eports/ — human reports (commit only stable summaries)
- .codex/ — orchestration memory (commit, but exclude stages/)

## 3. Rules
- Do not refactor code in this normalization stage.
- No mass moves/deletes; only reversible operations after dry-run.
- For medium/complex work, use streams table template: E:\Codex_Work\_templates\streams_table_template.md.

## 4. Next action
Create the first .codex task contract and run only doc-level verification (link checks + presence checks).