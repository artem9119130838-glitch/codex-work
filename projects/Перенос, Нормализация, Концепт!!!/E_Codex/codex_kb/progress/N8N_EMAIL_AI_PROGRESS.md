# n8n Email AI Progress

Дата обновления: 2026-05-29

## Status

Проект `n8n_email_ai` разделен на два рабочих направления:

1. `marketing_db / 1C / n8n ingestion`
2. `RAG / curated KB / client emails`

Текущий технический статус:

- 1С OData metadata подтвержден; доступ read-only работает.
- `marketing_db` существует и используется как writable working store.
- `n8n_marketing` существует и ограничен `marketing_db`.
- V1, V2 и V2.1 owner/contact ingestion уже были выполнены.
- Curated KB `kb_leads_v1` создана как активная база для будущих писем и RAG.
- Для `marketing_db` v2.2 зафиксированы: boolean-валидаторы `Validate backfill non-empty` / `Validate daily non-empty`, boolean-check в `IF alert`, helper-узлы `Fetch lead folders` / `Fetch tags catalog` через `$items(...)`, buyer-ветка для converted lead и ручной reset `ingestion_cursors` к backfill-start.
- Для `marketing_db` v2.2 зафиксированы: валидаторы сохраняют исходный payload, `IF alert` читает boolean `alert`, `Normalize owner` использует helper-узлы через `$items(...)`, buyer-ветка для converted lead добавлена, `ingestion_cursors` сброшен к backfill-start.
- Фаза 2 (`ingestion`) отмечена как `СТАБИЛЬНО`:
  - исправлена гонка данных (`data race`) через переход к линейной цепочке;
  - реализована "двойная сеть" контактов: `Catalog_КонтактыЛидов` + `Catalog_КонтактныеЛица` для converted leads;
  - `Normalize owner` не падает на пустых справочниках папок/тегов;
  - backfill / upsert / dedupe работают корректно по текущему контуру.
- Фактическая проверка БД на 2026-05-12 показала уточнение:
  - `ingestion_cursors` обновляется, значит cursor-write path живой;
  - owner backfill идет, но contact-layer пока сломан на batch-level;
  - подтвержден симптом: `onec_owners = 200`, `onec_contacts = 1`;
  - кейс `Акватон`: owner есть в `onec_owners`, но `owner_converted_to_customer` не выставлен и buyer contacts не загружены.
- База данных расширена под Фазу 3:
  - поля сегментации;
  - поля AI-summary;
  - история рассылок (`text[]`).

## Hard Rules

- 1С не менять, только читать.
- Новые данные, matching, письма и AI-выводы писать только в `marketing_db` или в curated KB.
- Mailbox intake не запускать, пока owner/contact snapshots не подтверждены.
- AI/RAG generation не запускать, пока не подтверждены:
  - deterministic matching;
  - quality owner/contact enrichment;
  - clean curated KB.

## Canonical Files

### marketing_db / ingestion

- `E:\Codex_Work\projects\n8n_email_ai\scripts\generate_v2_1_lead_bundle.ps1`
- `E:\Codex_Work\projects\n8n_email_ai\scripts\generate_v2_1_leads_and_contacts_params_workflow.ps1`
- `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V1_POSTMORTEM_2026-05-10.md`
- `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_IMPLEMENTATION_PLAN_2026-05-10.md`
- `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_1_OWNER_ENRICHMENT_PLAN_2026-05-10.md`
- `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_1_VERIFICATION_PASS_2026-05-11.md`
- `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_MAILBOX_INTAKE_READINESS_CHECKLIST_2026-05-11.md`
- `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_RUN_PARAMS_STOP_FIX_2026-05-11.md`
- `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_OPERATOR_RUNBOOK.md`
- `E:\Codex_Work\projects\n8n_email_ai\INGESTION_REPORT.md`
- `E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_ingestion_v2_2_master.json`
- `E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_event_log_table_v2_2.sql`
- `E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_v2_2_last24h_dbeaver_report.sql`
- `E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_inspectors_problem_records_v2_2.sql`
- `E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_odata_leads_contacts_params_v2_1_canonical_candidate_2026-05-11.fixed_connections.json`
- `E:\Codex_Work\projects\n8n_email_ai\workflows\WORKFLOW_STATUS_marketing_db_odata_leads_contacts_params_v2_1.md`
- `E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_odata_leads_contacts_params_v2_1.json` (broken/reference-only)

### curated KB / RAG

- `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\00_manifest.md`
- `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\70_input_client_context.md`
- `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\80_template_selection_rules.md`
- `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\90_pre_send_checklist.md`
- `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\95_article_selection_rules.md`
- `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\96_articles_index.md`
- `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\97_services_index.md`
- `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\99_sources_and_notes.md`

## marketing_db Track

Подтверждено:

- owner/contact dry-runs были импортированы и исполнены;
- V2 schema patch был применен DDL-capable ролью;
- V2.1 owner enrichment добавил owner-level signals;
- outreach scoring теперь отражается в полях `onec_owners`.

Канонические поля для будущей модели/логики:

- `owner_group_path`
- `owner_tags_text`
- `owner_search_emails`
- `owner_search_phones`
- `owner_is_important`
- `owner_importance_score`
- `owner_importance_reason`

Оставшиеся вопросы:

- убедиться, что scoring работает не только на Astravet/Iceberry, но и на review batch 2025;
- убедиться, что `owner_group_path` и `owner_tags_text` стабильны на большем наборе;
- не переносить mailbox intake раньше verification pass.

## Curated KB Track

Подтверждено:

- `kb_leads_v1` создана как активная curated KB;
- raw sources оставлены отдельно в `RAG файлы`;
- канон для “вход -> выбор шаблона -> проверка” уже выделен.

Оставшиеся вопросы:

- проверить и при необходимости исправить mojibake в `96_articles_index.md`;
- проверить `97_services_index.md`;
- подтвердить, что future email/RAG chats работают от curated KB, а не от сырья.

## Current Next Step

### Для marketing_db-чата

- считать owner/cursor path рабочим, но contact/buyer path все еще дефектным;
- использовать `marketing_db_ingestion_v2_2_master.json` как текущий master workflow ingestion только как базу для точечного фикса;
- опираться на факты из `public.onec_owners`, `public.onec_contacts`, `public.ingestion_cursors` и `INGESTION_REPORT.md`;
- сначала исправить:
  - обработку контактов по всему owner batch;
  - detection `owner_converted_to_customer`;
  - buyer contact branch для converted leads;
- не включать mailbox intake до исправления contact/buyer path.

### Канонический handoff проекта

- Для передачи проекта другому инженеру или новому чату использовать:
  - `E:\Codex_Work\projects\n8n_email_ai\PROJECT_HANDOFF.md`
- Этот файл считается кратким каноном по:
  - общей задаче проекта;
  - статусу Phase 1 / Phase 2 / RAG;
  - структуре БД, файлов, папок и чатов;
  - уже завершенным работам;
  - запланированным, но не начатым или отложенным задачам.

Технический note:
- Если workflow "доходит до `Run params` и останавливается", см. fix: `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_RUN_PARAMS_STOP_FIX_2026-05-11.md`

### Для RAG KB-чата

- сделать sanity/readability pass по `kb_leads_v1`;
- проверить и при необходимости исправить:
  - `96_articles_index.md`
  - `97_services_index.md`
- подтвердить канонический набор файлов для будущих email/RAG worker-чатов.
