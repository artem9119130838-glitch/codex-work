# Global Progress

Дата обновления: 2026-06-13

## Current State

`E:\Codex_Work` остается единым центром управления Codex KB.

Markdown-файлы являются Single Source of Truth. `marketing_db.knowledge_base` считается производным индексом, который должен обновляться из `.md`, а не наоборот.

Для проекта `n8n_email_ai` закреплена рабочая схема из 2 специализированных чатов:

- `marketing_db / 1C / n8n ingestion`
- `RAG / curated KB / client emails`

Этот основной чат используется для синхронизации, проверки результатов и обновления канона.

## Active Priorities

1. Довести `marketing_db` до доверяемого owner/contact слоя для реальных лидов.
2. Довести `kb_leads_v1` до чистой канонической curated KB без битой кодировки и сырьевых дублей.
3. Запускать mailbox intake только после проверки owner/contact snapshots и curated KB.
4. Включать AI/RAG generation только после стабильного deterministic matching.
5. Сохранять read-only режим для 1С и не хранить секреты в постоянных файлах workspace.

## Global Blockers

- `1C write`: любые write-операции в 1С вне scope. 1С только read-only.
- `RAG`: `marketing_db` существует, но `pgvector` и реальный production sync `knowledge_base` еще не подтверждены.
- `Encoding`: часть проектных артефактов и индексов требует проверки на mojibake.
- `Secrets`: live tokens/passwords не должны попадать в markdown, JSON, prompts и другие постоянные артефакты workspace.

## Done

- Создана и закреплена структура `codex_kb` как глобального слоя знаний и runbooks.
- Подтвержден read-only доступ к 1С OData; metadata валиден и опубликованные сущности доступны.
- Создана и применена базовая схема `marketing_db`.
- Создан restricted PostgreSQL role `n8n_marketing`; подтвержден доступ только к `marketing_db`, без доступа к `unf`.
- Собран и проверен первый контур n8n dry-run для owner/contact импорта.
- Выполнены V1, V2 и V2.1 итерации owner/contact ingestion в проекте `n8n_email_ai`.
- Для `n8n_email_ai` v2.2 зафиксированы: boolean-валидаторы `Validate backfill non-empty` / `Validate daily non-empty`, boolean-check в `IF alert`, helper-узлы `Fetch lead folders` / `Fetch tags catalog` через `$items(...)`, buyer-ветка `Fetch buyer order for owner` → `Normalize buyer order` → `Fetch buyer contacts for owner` → `Normalize contact buyer`, ручной reset `ingestion_cursors` к `2022-09-01T00:00:00Z` для backfill-start.
- Для `n8n_email_ai` v2.2 зафиксированы: сохранение payload в валидаторах, boolean-check в `IF alert`, общий owner-поток с `Upsert onec_owners` → `Compute cursor next` → `Update cursors`, и ручной reset `ingestion_cursors` к backfill-start.
- Для `n8n_email_ai` Фаза 2 ingestion отмечена как `СТАБИЛЬНО`:
  - переход от хрупкой параллельной загрузки к надежной линейной цепочке;
  - исправлена гонка данных (`data race`) в owner/contact потоке;
  - реализована логика "двойной сети" контактов: `Catalog_КонтактыЛидов` + `Catalog_КонтактныеЛица` для converted leads;
  - `Normalize owner` защищен от пустых справочников папок и тегов в 1С;
  - backfill работает корректно, upsert настроен, дубликаты исключены.
- По фактической проверке `marketing_db` на 2026-05-12 уточнено:
  - owner-layer грузится, курсор `ingestion_cursors` обновляется;
  - contact-layer все еще работает некорректно: после прогона зафиксировано `onec_owners = 200`, `onec_contacts = 1`;
  - кейс `Акватон` подтверждает проблему buyer/contact-ветки: owner присутствует в `onec_owners`, но `owner_converted_to_customer` не выставлен и контакты не подтянулись;
  - старые текстовые гипотезы про cursor-failure не считать каноном без сверки с БД.
- Для `marketing_db` schema зафиксировано расширение под Фазу 3:
  - поля сегментации;
  - поля AI-summary;
  - история рассылок (`text[]`).
- В `marketing_db` введены поля owner enrichment и deterministic importance scoring.
- Правило приоритета по группам/тегам встроено в owner enrichment layer и отражается в полях:
  - `owner_group_path`
  - `owner_tags_text`
  - `owner_search_emails`
  - `owner_search_phones`
  - `owner_is_important`
  - `owner_importance_score`
  - `owner_importance_reason`
- Создана curated KB для лидов и клиентских писем:
  - `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1`
- В curated KB выделены канонические файлы для будущих email/RAG worker-чатов:
  - `70_input_client_context.md`
  - `80_template_selection_rules.md`
  - `90_pre_send_checklist.md`
  - `95_article_selection_rules.md`
- Уточнена политика по секретам:
  - live secrets можно передавать Codex в чате для разовой настройки или проверки;
  - live secrets нельзя сохранять в markdown, workflow JSON, prompts, progress files и другие постоянные артефакты workspace.

- Добавлены канонические файлы для marketing_db verification и следующего узкого шага (intake readiness):
  - `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_1_VERIFICATION_PASS_2026-05-11.md`
  - `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_MAILBOX_INTAKE_READINESS_CHECKLIST_2026-05-11.md`
  - `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_RUN_PARAMS_STOP_FIX_2026-05-11.md`

- Параметризованный workflow для "лиды + контакты" (manual run; run params: `review_year`, `offset`, `limit`, `pool_top`):
  - Canonical candidate JSON: `E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_odata_leads_contacts_params_v2_1_canonical_candidate_2026-05-11.fixed_connections.json`
  - Broken/reference-only JSON (do not import/run): `E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_odata_leads_contacts_params_v2_1.json`
  - Пояснение `pool_top/offset/limit/review_year`: `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_RUN_PARAMS_STOP_FIX_2026-05-11.md`
- Для `n8n_email_ai` v2.2 оформлены рабочие operator artifacts:
  - `E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_ingestion_v2_2_master.json`
  - `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_OPERATOR_RUNBOOK.md`
  - `E:\Codex_Work\projects\n8n_email_ai\INGESTION_REPORT.md`
  - `E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_event_log_table_v2_2.sql`
  - `E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_v2_2_last24h_dbeaver_report.sql`
  - `E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_inspectors_problem_records_v2_2.sql`

## Canonical Work Split

### Chat 1: marketing_db / 1C / n8n ingestion

Отвечает только за:

- 1С OData read-only;
- `marketing_db`;
- n8n workflows;
- enrichment;
- review batches;
- readiness к `email_messages` и `email_match_results`.

### Chat 2: RAG / curated KB / client emails

Отвечает только за:

- `kb_leads_v1`;
- статьи/услуги;
- шаблоны писем;
- tone rules;
- template selection;
- pre-send logic;
- отделение active KB от raw sources.

## Next

- Для `marketing_db`-чата:
  - считать owner/cursor часть v2.2 рабочей, но contact/buyer-ветку еще не считать завершенной;
  - при следующем заходе в этот трек опираться на факты из БД (`onec_owners`, `onec_contacts`, `ingestion_cursors`) и `INGESTION_REPORT.md`, а не на устаревшие narrative-файлы;
  - сначала исправить batch-processing контактов и converted/buyer detection;
  - только после этого переходить к задачам Фазы 3;
  - держать mailbox intake выключенным до исправления contact/buyer-ветки.

- Для всего проекта `n8n_email_ai`:
  - главным инженерным summary и handoff-документом считать `E:\Codex_Work\projects\n8n_email_ai\PROJECT_HANDOFF.md`;
  - использовать его как первый проектный файл для передачи контекста новому инженеру или новому рабочему чату;
  - не тащить в новые чаты промежуточные narrative-файлы, если нужный факт уже зафиксирован в handoff-документе.

- Для `RAG KB`-чата:
  - провести sanity/readability pass по `kb_leads_v1`;
  - проверить и при необходимости исправить `96_articles_index.md` and `97_services_index.md`;
  - подтвердить канонический набор файлов для генерации писем без обращения к сырью.

- Для основного чата:
  - принимать от двух рабочих чатов только короткие outcome-reports;
  - держать глобальный gate перед mailbox intake и AI/RAG generation.

## Update (2026-05-29)

- Implemented minimal migration scaffold for tender-extraction-lab (structure + manifest-driven copy + smoke report). See E:\Codex_Work\projects\tender-extraction-lab.

- 2026-05-30: laptop bootstrap завершён, рабочее дерево переведено в чистое tracked-состояние origin/master.
- Старое содержимое сохранено обратимо в ARCHIVE\bootstrap_snapshot_2026-05-30 (без удалений).

## Update (2026-06-13)

- Разработчик Михаил Денисов собрал прототип FastAPI микросервиса `Tender RAG API` (архив `tender-rag-api.zip` в каталоге `Engeneer employee`), использующий `MarkItDown` для парсинга, `langchain-text-splitters` для чанкинга и `sentence-transformers` с моделью `multilingual-e5-small` для локальной векторизации и In-Memory семантического поиска.
- Выявлен конфликт требований к VPS: локальная модель векторизации требует ~1.5 ГБ RAM, что создает риск сбоев (OOM) на сервере с 1С и Postgres Pro, где свободно лишь 1 ГБ RAM.
- Предложено альтернативное решение: переход на Gemini Embeddings API, позволяющее исключить локальные ML-модели и перегрузку ОЗУ сервера.

## Update (2026-07-12)

- Выполнен аудит дискового пространства и оперативной памяти боевого сервера VPS (109.248.170.181).
- Проведена безопасная очистка дисков (удалено более 82 GB устаревших журналов 1С и старых бэкапов). Настроены лимиты journald (200MB).
- Освобождено 10.6 GB на системном SSD-диске `/` путем безопасного переноса неактивных баз 1С (`unf_restored` и `moving`) на диск `/Storage` с помощью табличных пространств PostgreSQL (Tablespaces). Доступное место на `/` увеличено до 28 GB (65% использования).
- Оптимизировано потребление RAM: остановлены и отключены из автозапуска неиспользуемые GUI-службы (`lightdm`, `xrdp`, `cups`, `avahi-daemon`, `whoopsie`), что снизило фоновую нагрузку и использование Swap.
- Параметры и структура VPS-сервера задокументированы в каноническом файле [SERVER_VPS.md](file:///C:/Codex_Shared/SERVER_VPS.md) в общем контуре `C:\Codex_Shared`, а правила SSH-доступа внесены в [AGENTS.md](file:///C:/Codex_Shared/AGENTS.md).
- Запущен автономный фоновый процесс создания полного бэкапа сервера (дампы всех СУБД, Docker n8n/3x-ui, лицензии 1С и конфиги) на VPS. Лог бэкапа пишется в `/Storage/backup.log`.
