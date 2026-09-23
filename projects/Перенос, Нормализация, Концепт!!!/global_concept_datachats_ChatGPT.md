Ниже — без привязки к твоим конкретным папкам и проектам. Это универсальная концепция, которую можно внедрить в любой workspace, с любым AI-кодинг-агентом: Codex, Claude Code, Cursor, Gemini CLI, Copilot Agent и т.д.

# 1. Главная цель системы

Создать не “один умный чат”, а **долгоживущую инженерную систему управления AI-проектами**.

Проблема, которую решаем:

```text
много проектов
много чатов
много старого кода
много незавершённых задач
много повторных объяснений
много ложных “готово”
работа на нескольких ПК
потеря контекста
хаотичный перенос файлов
```

Цель:

```text
любой проект должен за 2–5 минут становиться понятен новому AI-чату или человеку
```

Для этого память проекта должна жить не в чате, а в файлах.

---

# 2. Главный принцип

Неправильно:

```text
чат = проект
```

Правильно:

```text
проект = файловая память + задачи + проверки + история решений
чат = временный исполнитель
```

Чат можно закрыть, потерять, заменить, переполнить. Проект не должен от этого ломаться.

---

# 3. Оркестратор — это не вечный чат

Оркестратор должен быть **диспетчером контрактов**, а не “главным бесконечным диалогом”.

Оркестратор отвечает за:

```text
что делать
в каком проекте
в каком слое
какие файлы можно трогать
какие нельзя
какие проверки нужны
когда задача считается завершённой
когда задача считается принятой
куда записать handoff
что обновить в registry
```

Оркестратор не обязан писать код. Его основная роль — маршрутизация, контроль границ и закрытие задач.

---

# 4. Completion event ≠ acceptance

Это критично.

```text
Completion event = AI сказал “я сделал”, код изменён, команда запущена.

Acceptance = результат проверен, метрики/тесты прошли, регрессия не ухудшилась, человек или отдельный review-процесс принял результат.
```

Нельзя считать задачу принятой только потому, что Codex написал “done”.

Правило:

```text
AI может завершить implementation,
но acceptance требует отдельного evidence:
- тесты;
- отчёт;
- diff;
- список рисков;
- список ухудшений;
- обновлённый handoff;
- понятный next action.
```

---

# 5. Слои памяти проекта

## Слой 1. Оперативная память

Живёт дни/недели.

```text
.codex/current-task.md
.codex/handoff.md
reports/latest.md
```

Задача: быстро продолжить работу.

## Слой 2. Текущая архитектура

Живёт месяцы.

```text
PROJECT_HANDOFF.md
AGENTS.md
.codex/project-index.md
.codex/orchestrator.toml
```

Задача: объяснить проект новому чату или человеку.

## Слой 3. Решения

Живёт годами.

```text
decisions/ADR-001-*.md
decisions/ADR-002-*.md
```

Задача: объяснить, почему были приняты важные архитектурные решения.

## Слой 4. История

Не читается автоматически.

```text
docs/history/
archive/
.codex/stages/
old_reports/
legacy/
```

Задача: сохранить прошлое, но не засорять текущий контекст.

---

# 6. `handoff.md` не должен становиться историей

Очень важное правило:

```text
handoff.md = текущее состояние
не история проекта
```

Плохо:

```text
handoff.md на 200 страниц
вся история
все старые ошибки
все старые решения
все старые планы
```

Правильно:

```text
текущий статус
что работает
что сломано
что делать дальше
какие файлы важны
какие проверки последние
какие риски сейчас
```

История должна уходить в:

```text
docs/history/
archive/
.codex/stages/
decisions/ADR-*.md
```

---

# 7. Базовая структура любого AI-workspace

Универсально:

```text
AI_Workspace/
  AGENTS.md
  PROJECTS_REGISTRY.md
  PROJECTS_REGISTRY.csv
  CHAT_DISPATCHER.md
  PROGRESS.md
  WHERE_IS_WHAT.md
  DECISIONS.md
  YEAR_PLAN.md

  _workspace_docs/
    orchestration_principles.md
    workspace_rules.md
    chat_lifecycle.md
    project_memory_model.md
    verification_gates.md

  _templates/
    project_template/

  _global_skills/
    ...

  projects/
    project_a/
    project_b/
    project_c/

  migration_plans/
  sandbox/
  archive/
```

---

# 8. Структура каждого проекта

```text
project_name/
  PROJECT_HANDOFF.md
  AGENTS.md
  README.md

  .codex/
    orchestrator.toml
    project-index.md
    current-task.md
    handoff.md
    stop-conditions.md
    verification.md
    iteration-log.md
    failure-log.md
    decisions.md
    stages/
      README.md
    stage-artifact-template.md
    subagent-task-contract.md

  docs/
    architecture.md
    runbook.md
    history/

  decisions/
    ADR-000-template.md

  reports/
    latest.md

  src/
  scripts/
  tests/
  data/
  legacy/
  archive/
```

---

# 9. Глобальные skills

Должны быть **не только внутри каждого проекта**, но и на уровне пользователя / основного workspace.

Логика такая:

```text
~/.agents/skills/
  orchestration-setup/
  orchestrator-stage/
  task-router/
  orchestration-closeout/
  no-false-completion/
  one-layer-change-only/
  regression-gatekeeper/
  migration-auditor/
  project-handoff-writer/
```

На Windows это может быть:

```text
%USERPROFILE%\.agents\skills\
```

А внутри workspace можно держать исходник/канон:

```text
AI_Workspace/_global_skills/
```

И дальше:

```text
_global_skills/ = твой редактируемый источник
~/.agents/skills/ = установленная копия для AI-агентов
project/.agents/skills/ = локальные project-specific skills
```

---

# 10. Логика разделения skills

## 1. Lifecycle проекта — `orchestration-setup`

Используется при создании или нормализации проекта.

Задачи:

```text
создать структуру
создать PROJECT_HANDOFF.md
создать AGENTS.md
создать .codex/*
создать reports/latest.md
проверить, что проект управляем
```

Не пишет бизнес-логику.

---

## 2. Lifecycle этапа — `orchestrator-stage`

Используется, когда начинается конкретный этап.

Задачи:

```text
определить слой
зафиксировать allowed files
зафиксировать forbidden files
описать входы/выходы
описать проверки
создать stage artifact
```

---

## 3. Routing внутри этапа — `task-router`

Используется, когда непонятно, куда относится задача.

Задачи:

```text
какой проект?
какой слой?
какой тип задачи?
нужны ли subagents?
какие файлы читать?
какие файлы трогать нельзя?
какая проверка?
```

`task-router` не пишет код.

---

## 4. Безопасное закрытие — `orchestration-closeout`

Используется в конце задачи.

Проверяет:

```text
что изменено
какие тесты запущены
какой результат
что ухудшилось
какие риски
обновлён ли handoff
обновлён ли iteration-log
нужен ли registry update
```

---

# 11. Дополнительные обязательные skills

## `no-false-completion`

Запрещает говорить “готово” без доказательств.

## `one-layer-change-only`

Запрещает менять несколько слоёв за одну задачу.

## `regression-gatekeeper`

Ловит ситуацию:

```text
один кейс улучшили
десять сломали
```

## `migration-auditor`

Используется перед переносом старых проектов.

## `project-handoff-writer`

Создаёт короткий, полезный handoff без истории на 100 страниц.

---

# 12. Таблица Streams для medium/complex задач

Для любой средней или сложной задачи AI должен сначала заполнить таблицу.

```text
Stream | Goal | Files/write zone | Dependencies | Verification | Parallel/Sequential | Risk | Owner/Subagent
```

Пример:

| Stream         | Goal                  | Files/write zone    | Dependencies      | Verification       | Parallel/Sequential  | Risk                   | Owner/Subagent               |
| -------------- | --------------------- | ------------------- | ----------------- | ------------------ | -------------------- | ---------------------- | ---------------------------- |
| Inventory      | Понять текущие файлы  | read-only           | none              | inventory report   | parallel             | неверная классификация | subagent-code-inspection     |
| Tests          | Найти проверки        | tests/, reports/    | inventory         | test map           | parallel             | тесты устарели         | subagent-regression          |
| Implementation | Изменить один слой    | scripts/module_x.py | inventory + tests | targeted test      | sequential           | сломать соседний слой  | main/subagent-implementation |
| Risk review    | Проверить последствия | read-only           | implementation    | risk report        | after implementation | скрытая регрессия      | subagent-risk-review         |
| Closeout       | Обновить память       | handoff, reports    | all               | closeout checklist | final                | ложное “готово”        | main                         |

Правило:

```text
medium/complex задача без streams-table не начинается
```

---

# 13. Делегирование medium/complex задач

Для medium/complex задач надо требовать visible subagents.

Минимум 3 роли:

```text
1. Code inspection subagent
2. Regression/testing subagent
3. Risk review subagent
```

Главный агент не должен тащить в основной контекст все детали.

Главный агент должен получить от subagents:

```text
findings
risks
recommended action
files inspected
tests found
```

---

# 14. Правила переноса старых проектов

Нельзя переносить старый проект сразу как “новый чистый production”.

Сначала:

```text
audit → manifest → questions → handoff → copy plan → dry run → safe copy → normalization
```

## Этап 1. Audit старой папки

Создать:

```text
OLD_WORKSPACE_INVENTORY.md
MIGRATION_MANIFEST.csv
MIGRATION_QUESTIONS.md
OLD_WORKSPACE_HANDOFF.md
```

## Этап 2. Manifest

Колонки:

```text
old_path
new_path
project
category
copy_as_is
reason
risk
notes
```

Категории:

```text
project_canonical
project_legacy
project_docs
project_reports
project_data_gold
project_raw_sample
global_template_candidate
global_skill_candidate
chat_export
discard
unknown_review_needed
```

## Этап 3. Copy plan

Нельзя копировать всё.

Действия:

```text
copy_to_project
copy_to_legacy
copy_to_archive
skip
review_required
```

## Этап 4. Dry run

Сначала только dry-run report.

## Этап 5. Safe copy

Только после подтверждения.

---

# 15. Правила нормализации проекта

Нормализация — это не рефакторинг.

Нормализация делает проект управляемым:

```text
создать PROJECT_HANDOFF.md
создать AGENTS.md
создать .codex/*
разделить legacy и active
описать current-task
описать проверки
обновить registry
```

Нормализация не должна:

```text
улучшать код
переписывать парсер
менять бизнес-логику
запускать LLM extraction
делать большой refactor
```

---

# 16. Правила работы с legacy

По умолчанию:

```text
legacy = read-only reference
```

Старый код можно читать, анализировать, классифицировать.

Нельзя:

```text
автоматически считать его production
молча переносить в src/
переписывать без current-task
использовать как canonical без проверки
```

---

# 17. GitHub-синхронизация

GitHub нужен не как “папка для всего”, а как versioned source of truth.

## Что хранить в Git

```text
AGENTS.md
PROJECTS_REGISTRY.md
CHAT_DISPATCHER.md
_workspace_docs/
_templates/
_global_skills/
projects/*/PROJECT_HANDOFF.md
projects/*/AGENTS.md
projects/*/.codex/
projects/*/docs/
projects/*/decisions/
projects/*/scripts/
projects/*/src/
projects/*/tests/
projects/*/schemas/
projects/*/reports/latest.md
requirements.txt
pyproject.toml
package.json
```

## Что не хранить в Git

```text
.env
secrets/
.venv/
node_modules/
__pycache__/
.cache/
tmp/
large raw archives
model_outputs/
huge batches
personal downloads
private credentials
```

## Базовая логика работы на нескольких ПК

На ПК-1:

```text
git pull
работа
tests/checks
git add
git commit
git push
```

На ПК-2:

```text
git pull
работа
git commit
git push
```

Правило:

```text
не редактировать один и тот же проект одновременно на двух ПК без pull/push
```

---

# 18. GitHub как замена части Beads

Beads в такой архитектуре можно заменить или дополнить несколькими вариантами.

## Минимальный вариант

```text
.codex/current-task.md
.codex/iteration-log.md
PROJECTS_REGISTRY.md
reports/latest.md
```

## Более сильный вариант

```text
GitHub Issues = task source of truth
GitHub Projects = board/status
Pull Requests = implementation evidence
Labels = phase/layer/status
Milestones = project phases
```

## Локальный вариант без GitHub Issues

```text
tasks/
  TASK-001-gold-loader.md
  TASK-002-candidate-recall.md
  TASK-003-batch-builder.md

tasks/index.csv
```

## Универсальное правило

Нужен один источник правды по задачам:

```text
либо Beads
либо GitHub Issues
либо local tasks/*.md
либо PROJECTS_REGISTRY + current-task
```

Нельзя, чтобы задачи жили одновременно в 5 местах без синхронизации.

---

# 19. Чем заменить Superpowers в Codex

Superpowers по смыслу — это набор практик, skills и workflow-дисциплины.

В Codex это заменяется так:

```text
~/.agents/skills/
project/.agents/skills/
AGENTS.md
.codex/orchestrator.toml
.codex/current-task.md
.codex/stages/
orchestration-closeout
```

То есть аналог Superpowers — не один файл, а связка:

```text
global skills
project-local skills
короткий AGENTS.md
task contracts
stage artifacts
closeout rules
```

---

# 20. Чем заменить Beads в Codex

Beads — это task-truth / lightweight issue tracker / состояние задач.

В Codex можно заменить:

## Вариант A — GitHub Issues

Лучше всего для нескольких ПК и долгих проектов.

```text
GitHub Issues = задачи
GitHub Labels = layer/status
GitHub Projects = доска
Pull Requests = evidence
```

## Вариант B — local markdown tasks

```text
tasks/
  TASK-001.md
  TASK-002.md
tasks/index.csv
```

## Вариант C — `.codex/current-task.md`

Для маленького проекта достаточно:

```text
.codex/current-task.md
.codex/iteration-log.md
reports/latest.md
```

Оптимально:

```text
GitHub Issues для долгих проектов
current-task.md для текущего шага
iteration-log.md для локальной истории
```

---

# 21. Чем заменить Template Bridge

Template Bridge по смыслу:

```text
склеивает Superpowers + Beads
добавляет доступ к большому каталогу агент-шаблонов
не бандлит всё локально
подтягивает нужное по требованию
```

Универсальная замена:

```text
_template_registry/
  templates-index.json
  sources.md
  cache/
  selected/
```

И отдельный skill:

```text
template-router
```

Логика:

```text
1. task-router определяет тип задачи;
2. template-router ищет подходящий шаблон;
3. если шаблон не установлен — предлагает подтянуть;
4. шаблон фиксируется в selected/ или cache/;
5. current-task.md указывает, какой шаблон использован;
6. closeout фиксирует результат.
```

Важно:

```text
не надо бандлить 400+ шаблонов локально
```

Лучше:

```text
иметь registry
иметь whitelist
иметь cache
иметь manifest
подтягивать только нужное
фиксировать версию/дату источника
```

---

# 22. Универсальный Template Bridge replacement

Структура:

```text
_template_bridge/
  TEMPLATE_BRIDGE.md
  templates-index.json
  allowed-sources.md
  selected/
  cache/
  fetch-log.md
  template-use-log.md
```

`templates-index.json`:

```json
[
  {
    "name": "python-debugging-agent",
    "source": "remote_or_local",
    "category": "debugging",
    "status": "available",
    "last_checked": "YYYY-MM-DD",
    "local_path": "cache/python-debugging-agent/"
  }
]
```

Правила:

```text
не скачивать всё
не использовать неизвестные шаблоны без review
не менять проект под шаблон
шаблон — помощник, не источник истины
```

---

# 23. Логика “4 lifecycle skills” как ядро системы

Вся система держится на 4 главных lifecycle skills:

## 1. `orchestration-setup`

Когда создаём/нормализуем проект.

## 2. `orchestrator-stage`

Когда запускаем этап.

## 3. `task-router`

Когда надо понять, куда относится задача.

## 4. `orchestration-closeout`

Когда надо безопасно закрыть задачу.

Остальные skills вспомогательные.

---

# 24. Как должен выглядеть каждый AI-запрос

Не так:

```text
Сделай проект лучше
```

А так:

```text
Read:
- PROJECT_HANDOFF.md
- AGENTS.md
- .codex/current-task.md
- .codex/handoff.md
- reports/latest.md

Task:
<одно действие>

Allowed files:
<список>

Forbidden:
<список>

Verification:
<команды/отчёты>

Closeout:
update handoff, iteration-log, reports/latest
```

---

# 25. Универсальный workflow

```text
1. Setup workspace
2. Normalize existing projects
3. Audit old folders
4. Create migration manifests
5. Plan copy
6. Dry run
7. Safe copy
8. Normalize each project
9. Create current-task
10. Execute one stage
11. Run verification
12. Closeout
13. Update registry
14. Commit to GitHub
15. Start new session when context grows
```

---

# 26. Как бороться с разрастанием памяти

Раз в 2–4 недели:

```text
handoff compaction
AGENTS.md compaction
archive old reports
move old decisions to ADR
clean current-task
update registry
```

Промпт:

```text
Compact project memory.
Keep current state.
Move history to docs/history.
Keep PROJECT_HANDOFF under 5–10 screens.
Keep AGENTS.md short.
Do not delete evidence.
```

---

# 27. Главная итоговая формула

```text
Workspace = операционная система
Project = управляемая единица
Chat = временная сессия
AGENTS.md = конституция
current-task.md = текущий контракт
handoff.md = сменная записка
orchestrator.toml = машинные правила
skills = повторяемые процедуры
GitHub = версия и синхронизация
Issues/tasks = источник задач
reports/latest.md = доказательство результата
closeout = безопасное завершение
acceptance = отдельная проверка, не слова AI
```

---

# 28. Самый короткий план внедрения

1. Создать единый workspace.
2. Создать global `AGENTS.md`.
3. Создать `_workspace_docs/orchestration_principles.md`.
4. Создать `~/.agents/skills/` и `_global_skills/`.
5. Создать project template.
6. Создать registry.
7. Проаудировать старые папки.
8. Создать migration manifest.
9. Переносить только через dry-run и copy manifest.
10. Нормализовать проекты по одному.
11. Подключить GitHub.
12. Работать только через current-task.
13. Для medium/complex задач требовать streams-table и subagents.
14. Закрывать задачи только через closeout.
15. Acceptance делать отдельно от completion.
