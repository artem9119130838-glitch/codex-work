# Нормализация `E:\Codex_Work` v1 (минимальные, обратимые добавления)

## Summary
Базовый канон сохраняем как есть: `codex_kb` + `projects` + `ARCHIVE`. Workspace не пересоздаём, существующие файлы не удаляем, массовых переносов не делаем, код проектов не трогаем. Вносим только **документы/шаблоны/правила**, все будущие file-ops — только обратимые и только после dry-run.

## Repo Facts (что уже есть / чего нет)
- Уже есть: `E:\Codex_Work\AGENTS.md`, `CODEX_START_HERE.md`, `CHAT_DISPATCHER.md`, `PROGRESS.md`, `ГДЕ_ЧТО_ЛЕЖИТ.md`, папки `codex_kb`, `projects`, `ARCHIVE`.
- Сейчас отсутствуют (нужно создать): `E:\Codex_Work\PROJECTS_REGISTRY.md`, `PROJECTS_REGISTRY.csv` (опционально), `E:\Codex_Work\_templates\`, `E:\Codex_Work\_workspace_docs\`, `E:\Codex_Work\.gitignore`.

## Key Changes (только документы/шаблоны; без миграций)
1) **Streams Table (только medium/complex)**
- Создать `E:\Codex_Work\_templates\streams_table_template.md`.
- Обновить `E:\Codex_Work\codex_kb\skills\orchestration\stage.md`:
  - правило: streams table обязателен для medium/complex, не обязателен для simple;
  - ссылка на `E:\Codex_Work\_templates\streams_table_template.md`.

2) **Manual fallback для subagents**
- В `E:\Codex_Work\codex_kb\00_global\WORKSPACE_ORCHESTRATION_CONCEPT.md` добавить фразу-правило:
  - если среда не поддерживает visible subagents, заменять их ручным разбиением на независимые шаги с отдельными проверками, без вложенных агентов.
- Если в `E:\Codex_Work\AGENTS.md` есть раздел про агентов/делегирование — добавить туда короткое зеркальное правило (если нет — не раздувать, а дать 1–2 строки).

3) **GitHub sync как обязательный этап после нормализации**
- Создать `E:\Codex_Work\.gitignore` и добавить исключения:
  - `data/raw_sample/`
  - `legacy/`
  - `archive/`
  - `ARCHIVE/`
  - `__pycache__/`
  - `_cache_blocks/`
  - `model_outputs/`
  - `batches/`
  - `candidates/`
  - `.venv/`
  - `node_modules/`
  - `.env`
- Создать `E:\Codex_Work\_workspace_docs\GITHUB_SYNC_CHECKLIST.md`:
  - что коммитить:
    - мастер-файлы корня workspace;
    - `codex_kb`;
    - `_templates`;
    - `projects/*/src`;
    - `projects/*/scripts`;
    - `projects/*/data/gold/`;
    - `projects/*/.codex/` (но **без** `projects/*/.codex/stages/`);
    - `projects/*/PROJECT_HANDOFF.md`, `projects/*/AGENTS.md`, `projects/*/docs/` (если есть).
  - что не коммитить:
    - сырые тендеры/входняки;
    - большие legacy;
    - `archive/` и `ARCHIVE/`;
    - кэши;
    - model outputs;
    - batches;
    - candidates;
    - временные отчёты.
  - порядок синхронизации на двух ПК:
    - сначала нормализация пилотного проекта (scaffold `.codex` + registry + docs);
    - только потом первый commit/push;
    - далее pull на втором ПК, работа только через branch/PR или согласованный порядок (описать явно).
  - “guardrails” по секретам: `.env` и токены никогда не коммитить.

4) **Фиксируем формат `.codex/orchestrator.toml`**
- В `WORKSPACE_ORCHESTRATION_CONCEPT.md` и/или в orchestration skill docs закрепить: `.codex/orchestrator.toml` — единственный формат (не yaml/json).
- В проектных шаблонах (если добавляем) давать только `.toml`.

5) **Явно НЕ внедряем сейчас**
- Не внедрять `~/.agents/skills`, template-router, авто-подтягивание внешних templates.
- В концепции упомянуть это только как “possible future extension”, без реализации.
- Локальные skills остаются в `E:\Codex_Work\codex_kb\skills\`.
- Шаблоны остаются в `E:\Codex_Work\_templates\`.

6) **Registry + проверка ссылок в корневых файлах**
- Создать `E:\Codex_Work\PROJECTS_REGISTRY.md` (минимальный формат: project → status → path → handoff link → next action).
- После создания registry и мастер-доков выполнить “link check” (без перемещений):
  - проверить `E:\Codex_Work\AGENTS.md`
  - `E:\Codex_Work\CHAT_DISPATCHER.md`
  - `E:\Codex_Work\ГДЕ_ЧТО_ЛЕЖИТ.md`
  - `E:\Codex_Work\PROGRESS.md`
  - цель: найти ссылки на несуществующие пути (особенно `Архив`/`chat_exports`) и исправить на фактические (`ARCHIVE`, и только существующие каталоги).

7) **Правило обратимости в runbook**
- Создать `E:\Codex_Work\codex_kb\30_runbooks\WORKSPACE_NORMALIZATION_RUNBOOK.md` и добавить правило:
  - перед любым move/rename — dry-run со списком изменений (пример команд PowerShell с `-WhatIf`);
  - массовые удаления запрещены;
  - разрешены только обратимые операции: copy; rename; move после dry-run; archive.
- В runbook включить шаблон dry-run протокола: “что планировалось”, “что фактически”, “как откатить”.

## Implementation Steps (без кода проектов, без переносов)
1) Добавить структуру: `_templates/`, `_workspace_docs/`.
2) Создать: `PROJECTS_REGISTRY.md`, `.gitignore`, `streams_table_template.md`, `GITHUB_SYNC_CHECKLIST.md`.
3) Добавить: `WORKSPACE_ORCHESTRATION_CONCEPT.md`, `WORKSPACE_NORMALIZATION_RUNBOOK.md`.
4) Добавить/обновить: `codex_kb\skills\orchestration\stage.md` (если папки `orchestration` нет — создать её и минимальный `README.md`/`stage.md`).
5) Выполнить link check и внести правки только в корневые `.md` (без перемещения файлов).

## Acceptance Criteria
- Появились новые документы/шаблоны, при этом существующие файлы не удалены и проекты не перенесены.
- В корневых файлах нет ссылок на несуществующие пути (или они явно помечены как “planned, not created yet”).
- В концепции и skill docs закреплены: streams table only for medium/complex; manual fallback subagents; `.codex/orchestrator.toml`; GitHub sync после пилота.
- В конце работы: список созданных/изменённых файлов + “Next action: пилотный проект (только scaffold `.codex/`, без рефакторинга)”.

## Output (что будет на выходе этого этапа)
- Только создание/обновление документов и шаблонов в `E:\Codex_Work` (без изменений кода проектов, без переносов файлов/папок, без рефакторинга).
- Финальный список созданных/изменённых файлов и next action.
