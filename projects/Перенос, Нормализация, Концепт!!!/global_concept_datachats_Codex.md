Да, это нужно включить в “концепцию”. Обновляю тезисы и стандарт, уже с тем, что ты перечислил.

**Ключевые правила (обязательные)**
- **Нормализация/перенос**: любые старые проекты/чаты приводятся к одному стандарту через *migration rules* (что переименовываем, что переносим в `archive/`, что превращаем в `handoff/current-task/stages`), и делается это итеративно, с обратимостью (rename/move, без массового удаления).
- **Orchestrator = диспетчер контрактов**: он не “делает работу”, он выдаёт/проверяет task contracts, запускает lifecycle-цепочку и следит за доказательствами.
- **Streams table обязателен для medium/complex**: перед исполнением строится таблица потоков (streams) с `write-zone`, `deps`, `verif`, `artifacts`, `owner/agent`. Без неё — только simple tasks.
- **Делегирование medium/complex**: сложные задачи режутся на независимые streams и делегируются специализированным агентам/шаблонам; оркестратор собирает результат и запускает closeout.
- **Handoff не история**: `handoff.md` всегда “текущее состояние + следующий шаг + риски”; история уходит в `stages/`/`docs/history/`.
- **Completion event ≠ acceptance**: “агент сказал, что закончил” не означает “принято”; acceptance только после verify + evidence + обновления памяти (handoff/current-task) + регистрации результата.
- **Центральные skills**: в корне workspace обязательно есть `~/.agents/skills/` (или эквивалентная папка), а не только “внутри проектов”, чтобы процедуры были едиными и переиспользуемыми.

**Структура (универсально, для любой папки и любого ИИ)**
- Workspace root:
  - `PROJECTS_REGISTRY.md`
  - `CHAT_DISPATCHER.md`
  - `_templates/`
  - `~/.agents/skills/` (глобальные playbooks/skills)
  - `_workspace_docs/` (каноника процесса/политики/матрицы)
- Project root (минимум):
  - `AGENTS.md` (кратко, практично)
  - `.codex/` или `.ai/`:
    - `project-index.md`, `current-task.md`, `handoff.md`, `orchestrator.(toml|yaml)`
    - `stages/YYMMDD-*/` (история и evidence)

**Логика разделения по lifecycle (обязательная)**
- `setup` (lifecycle проекта): инициализация структуры, registry entry, базовые политики, initial handoff.
- `stage` (lifecycle этапа): план этапа, definition-of-done, streams table, артефакты этапа.
- `router` (routing внутри этапа): диспетчеризация streams → выбор агентов/шаблонов → контроль write-zones → сбор результатов.
- `closeout` (безопасное закрытие): verify/evidence, acceptance checklist, обновление памяти, упаковка истории в `stages/`.

**Что именно держать в `~/.agents/skills/` (ядро)**
- `setup.md` (инициализация проекта)
- `stage.md` (шаблон этапа + streams table)
- `router.md` (правила делегирования, write-zones, сборка результатов)
- `closeout.md` (acceptance checklist + evidence правила)
- `handoff_compaction.md` (сжатие памяти)
- `github_sync.md` (ветки, PR/closeout, частота push, политика артефактов, секреты)

**Streams table (минимальный стандарт полей)**
- `stream_id | goal | inputs | write_zone | deps | owner(agent/template) | artifacts | verify | risk`
И правило: если два stream пишут в одну write_zone — они не параллельны, нужно разделить зоны или сериализовать.

**Чем заменить в Codex: Superpowers / Beads / Template Bridge**
- `Superpowers` (агенты-исполнители) в Codex: набор “исполнительных агентов” как шаблоны/скиллы + диспетчер в `router` (встроенная оркестрация + правила контрактов).
- `Beads` (атомарные блоки/шаги/стадии) в Codex: `stages/YYMMDD-*/` + стандартизированный `closeout` (каждый bead = stage с артефактами и evidence).
- `Template Bridge` (твой плагин) в Codex-архитектуре: **канонический источник шаблонов агентов** для `router`:
  - router выбирает “template id” из Bridge,
  - Bridge подтягивает свежий шаблон по необходимости (не бандлит локально),
  - оркестратор фиксирует, какой шаблон/версия использованы (в stage metadata), чтобы результат был воспроизводим.

Если хочешь — следующим шагом я оформлю это как один “канонический документ концепции” (например `WORKSPACE_ORCHESTRATION_CONCEPT.md`) + минимальные шаблоны файлов (registry, dispatcher, handoff/current-task, stage+streams, closeout+acceptance).