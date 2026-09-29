# Единый каталог скриптов и автоматизаций контура (SCRIPTS_CATALOG)

> **Дата последней автоматической ревизии:** `2026-09-29 07:20:27`  
> **Статус контура:** Уникальных проверенных скриптов: `1081` | Отсеяно дубликатов: `1243` | Библиотек вендоров: `4440`.  
> **Архитектурный стандарт:** «Семейства инструментов» (Tool Families). Любые модификации группируются в одной ячейке от базового вызова к расширенным.

---

## 🧭 Навигация по доменам

- [1. Выгрузка, парсинг и фильтрация чатов ИИ (Gemini / ChatGPT / Claude)](#ai_chats)
- [2. Снабжение и ВЭД в Китае (Дечжоу / Циндао, фонд 5000 RMB, возврат НДС)](#supply_china)
- [3. Создание прайс-листов и коммерческих предложений из каталогов](#price_creating)
- [4. Анализ резюме, RAG-база кандидатов и генерация ответов соискателям](#hr_resume)
- [5. Перенос данных с ПК на ПК (HP Victus ⮂ MateBook ⮂ Mirror_E_Home)](#pc_migration)
- [6. Спринты Михаила, RAG ГОЗ и Архитектура сети VPS](#sprint_mikhail)
- [7. Windows Diagnostics, графика Victus 16, Safe Mode и дисплеи](#windows_diagnostics)
- [8. Анализ истории чата, сжатие сессий и /learn](#session_compression)
- [9. Связка 1С:УНФ и Битрикс24 (OData, Контрагенты, Заказы, СКД)](#onec_bitrix_sync)
- [10. Обработка новых лидов и Inbound-снабжение (Email AI Pipeline)](#lead_inbound)
- [11. Follow-up продаж в сделках и реактивация клиентов](#followup_sales)
- [12. Синхронизация лидов и компаний в 1С и Битрикс24 (Idempotent CRM)](#idempotent_crm_1c)
- [13. Тендеры, АСТ ГОЗ и RAG-пайплайн спецификаций](#tenders_goz)
- [14. Инфраструктура, VPS-сервер, Docker и Бэкапы](#infra_vps)

---

<a id='ai_chats'></a>
## 1. Выгрузка, парсинг и фильтрация чатов ИИ (Gemini / ChatGPT / Claude)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `clean_temporary_categories.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/AI chats export/src/clean_temporary_categories.py` | Записываем в utf-8-sig (UTF-8 с BOM) | 1 |
| **Базовый** | `clean_temporary_categories.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/clean_temporary_categories.py` | Записываем в utf-8-sig (UTF-8 с BOM) | 0 |
| **Базовый** | `merge_small_files.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/AI chats export/src/merge_small_files.py` | Чтение файла и удаление заголовка категории | 1 |
| **Базовый** | `merge_small_files.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/merge_small_files.py` | Чтение файла и удаление заголовка категории | 0 |
| **Базовый** | `parse_unresolved.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/AI chats export/src/parse_unresolved.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `parse_unresolved.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/parse_unresolved.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `parse_unresolved_recovered.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/AI chats export/src/parse_unresolved_recovered.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `parse_unresolved_recovered.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/parse_unresolved_recovered.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `recover_lost_batches.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/AI chats export/src/recover_lost_batches.py` | Add src to sys.path | 2 |
| **Базовый** | `retry_failed_batches.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/AI chats export/src/retry_failed_batches.py` | Добавляем папку src в пути поиска модулей | 1 |
| **Базовый** | `retry_failed_batches.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/retry_failed_batches.py` | Добавляем папку src в пути поиска модулей | 0 |
| **Расширенный** | `AI_chats_filter_optimized.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/AI chats export/src/AI_chats_filter_optimized.py` | Принудительно настраиваем UTF-8 для вывода в консоль | 2 |

---

<a id='supply_china'></a>
## 2. Снабжение и ВЭД в Китае (Дечжоу / Циндао, фонд 5000 RMB, возврат НДС)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `h03__del_relax_supply_gate.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tries/h03__del_relax_supply_gate.py` | !/usr/bin/env python3 | 5 |
| **Расширенный** | `check_import_china.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/check_import_china.py` | Автоматизация рабочего процесса. | 2 |

---

<a id='price_creating'></a>
## 3. Создание прайс-листов и коммерческих предложений из каталогов

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Интеграционный** | `build_rod_matrix.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/Price creating/scripts/build_rod_matrix.py` | Simply delegate to the canonical root script | 1 |
| **Интеграционный** | `build_rod_matrix.py` | `D:/Soft/Codex Backup/projects/Price creating/scripts/build_rod_matrix.py` | Simply delegate to the canonical root script | 0 |

---

<a id='hr_resume'></a>
## 4. Анализ резюме, RAG-база кандидатов и генерация ответов соискателям

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `build_candidates_rag_db.py` | `projects/HR/build_candidates_rag_db.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `build_candidates_rag_db.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/build_candidates_rag_db.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `generate_three_letters.py` | `scripts/generate_three_letters.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `scratch_parse_resumes.py` | `projects/HR/scratch_parse_resumes.py` | ow 2 contains actual column headers | 0 |
| **Базовый** | `scratch_parse_resumes.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/scratch_parse_resumes.py` | ow 2 contains actual column headers | 1 |
| **Базовый** | `scratch_print_all.py` | `projects/HR/scratch_print_all.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_clean_digits.py` | `projects/HR/search_clean_digits.py` | ove spaces and punctuation | 0 |
| **Базовый** | `search_clean_digits.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/search_clean_digits.py` | ove spaces and punctuation | 1 |
| **Расширенный** | `check_inbox_reply.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/check_inbox_reply.py` | Автоматизация рабочего процесса. | 2 |
| **Расширенный** | `create_candidates_excel.py` | `projects/HR/create_candidates_excel.py` | Sheet 1: Candidates list | 0 |
| **Расширенный** | `create_candidates_excel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/create_candidates_excel.py` | Sheet 1: Candidates list | 1 |
| **Расширенный** | `scratch_check_specific.py` | `projects/HR/scratch_check_specific.py` | Автоматизация рабочего процесса. | 0 |

---

<a id='pc_migration'></a>
## 5. Перенос данных с ПК на ПК (HP Victus ⮂ MateBook ⮂ Mirror_E_Home)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `document.py` | `D:/Soft/Codex Backup/AI Backups Victus/Codex_Work/projects/tender-extraction-lab/tender-rag-api/app/schemas/document.py` | Схема для описания структуры одного чанка | 0 |
| **Базовый** | `document.py` | `D:/Soft/Codex Backup/AI Backups Victus/Codex_Work/projects/tender-extraction-lab/tender-rag-api/app/services/document.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `document.py` | `D:/Soft/Codex Backup/AI Backups Victus/Codex_Work/projects/tender-extraction-lab/tender-rag-api/app/api/routers/document.py` | Передаем файл в слой бизнес-логики для парсинга и нарезки | 0 |
| **Базовый** | `main.py` | `D:/Soft/Codex Backup/AI Backups Victus/Codex_Work/projects/tender-extraction-lab/tender-rag-api/app/main.py` | Подключаем наш роутер | 0 |
| **Базовый** | `render_and_diff.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/render_and_diff.py` | !/usr/bin/env python3 Render two DOCXs and produce visual + structural diffs. | 0 |

---

<a id='sprint_mikhail'></a>
## 6. Спринты Михаила, RAG ГОЗ и Архитектура сети VPS

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `add_wait_node.py` | `C:/Users/Артем/tender-rag-api/scratch/add_wait_node.py` | Create the Wait node | 0 |
| **Базовый** | `audit_db.py` | `C:/Users/Артем/tender-rag-api/scratch/audit_db.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `auto_deploy.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/auto_deploy.sh` | Проверяем наличие обновлений в ветке mikhail-origin/main | 1 |
| **Базовый** | `auto_deploy.sh` | `D:/Soft/Codex Backup/scripts/vps/auto_deploy.sh` | Проверяем наличие обновлений в ветке mikhail-origin/main | 0 |
| **Базовый** | `config.py` | `C:/Users/Артем/tender-rag-api/app/core/config.py` | odels | 0 |
| **Базовый** | `deploy-tender.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/deploy-tender.sh` | Выполняем git pull | 1 |
| **Базовый** | `deploy-tender.sh` | `D:/Soft/Codex Backup/scripts/vps/deploy-tender.sh` | Выполняем git pull | 0 |
| **Базовый** | `deploy_metabase_analytics.py` | `C:/Users/Артем/tender-rag-api/scripts/deploy_metabase_analytics.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `document.py` | `C:/Users/Артем/tender-rag-api/app/api/routers/document.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_backfill_sql.py` | `C:/Users/Артем/tender-rag-api/analytics/scripts/generate_backfill_sql.py` | Загружаем переменные окружения | 0 |
| **Базовый** | `import_white_base.py` | `C:/Users/Артем/tender-rag-api/scripts/import_white_base.py` | Format list into pgvector string format: '[1.0, 2.0, 3.0]' | 0 |
| **Базовый** | `key_manager.py` | `C:/Users/Артем/tender-rag-api/app/core/key_manager.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `llm_service.py` | `C:/Users/Артем/tender-rag-api/app/services/llm_service.py` | Ограничиваем количество чанков (Token-First Vibe Engineering) | 0 |
| **Базовый** | `logger.py` | `C:/Users/Артем/tender-rag-api/app/core/logger.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `rabbitmq.py` | `C:/Users/Артем/tender-rag-api/app/core/rabbitmq.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `read_docx.py` | `C:/Users/Артем/tender-rag-api/scratch/read_docx.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tender_webhook_deploy.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/tender_webhook_deploy.py` | !/usr/bin/env python3 | 1 |
| **Базовый** | `tender_webhook_deploy.py` | `D:/Soft/Codex Backup/scripts/vps/tender_webhook_deploy.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `tender_worker.py` | `C:/Users/Артем/tender-rag-api/app/workers/tender_worker.py` | Для тестов по умолчанию стучимся на локальный мок-сервер 5001, а на бою - в n8n | 0 |
| **Базовый** | `update_docs.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs.py` | Update PROGRESS.md | 0 |
| **Базовый** | `update_docs_chat.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs_chat.py` | Update PROGRESS.md | 0 |
| **Базовый** | `update_docs_heuristic.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs_heuristic.py` | 1. Update PROGRESS.md | 0 |
| **Базовый** | `update_docs_report.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs_report.py` | 1. Update PROGRESS.md Update (2026-07-15) | 0 |
| **Базовый** | `update_summary_fields.py` | `C:/Users/Артем/tender-rag-api/scratch/update_summary_fields.py` | Update Get Deals node | 0 |
| **Базовый** | `ved_audit_service.py` | `C:/Users/Артем/tender-rag-api/app/services/ved_audit_service.py` | Generate embedding using Gemini API (same model as the White Base import). | 0 |
| **Расширенный** | `nomenclature_parser.py` | `C:/Users/Артем/tender-rag-api/app/services/nomenclature_parser.py` | Checks if a filename likely contains nomenclature. | 0 |
| **Расширенный** | `patch_error_node.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_error_node.py` | Find the node that creates the error task (we can identify it by looking at its parameters) Update the description to include the detailed description field | 0 |
| **Расширенный** | `patch_headers.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_headers.py` | Inject headers | 0 |
| **Расширенный** | `patch_metabase.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_metabase.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `patch_n8n_chat.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_n8n_chat.py` | Update parameters | 0 |
| **Расширенный** | `patch_n8n_deal.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_n8n_deal.py` | ap old codes to new codes | 0 |
| **Расширенный** | `patch_remove_postgres.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_remove_postgres.py` | ove the node named "Insert to Postgres" | 0 |
| **Диагностический** | `generate_sql.py` | `C:/Users/Артем/tender-rag-api/analytics/tests/generate_sql.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `load_bulk_csv.py` | `C:/Users/Артем/tender-rag-api/analytics/tests/load_bulk_csv.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `load_test_data.py` | `C:/Users/Артем/tender-rag-api/analytics/tests/load_test_data.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `mock_webhook_server.py` | `C:/Users/Артем/tender-rag-api/docs/part2_regulatory_sieve/test_contour/mock_webhook_server.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `send_test_tender.py` | `C:/Users/Артем/tender-rag-api/docs/part2_regulatory_sieve/test_contour/send_test_tender.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `setup_metabase.py` | `C:/Users/Артем/tender-rag-api/analytics/tests/setup_metabase.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_fastapi.py` | `C:/Users/Артем/tender-rag-api/test_fastapi.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_folder.py` | `C:/Users/Артем/tender-rag-api/scratch/test_folder.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_health.py` | `C:/Users/Артем/tender-rag-api/scratch/test_health.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_llm.py` | `C:/Users/Артем/tender-rag-api/test_llm.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_llm_large.py` | `C:/Users/Артем/tender-rag-api/test_llm_large.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_local_db.py` | `C:/Users/Артем/tender-rag-api/analytics/tests/test_local_db.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_models.py` | `C:/Users/Артем/tender-rag-api/scripts/test_models.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_monthly_query.py` | `C:/Users/Артем/tender-rag-api/scripts/test_monthly_query.py` | !/usr/bin/env python3 | 0 |

---

<a id='windows_diagnostics'></a>
## 7. Windows Diagnostics, графика Victus 16, Safe Mode и дисплеи

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `audit_c_drive_bloat.py` | `scripts/audit_c_drive_bloat.py` | Полная ревизия диска C:: анализ DXCache, %TEMP%, WinSxS, буфера Google Drive, крупных папок и свободного места. | 0 |
| **Базовый** | `__init__.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate/__init__.py` | Section-level migration code for migrate-to-codex. | 0 |
| **Базовый** | `__init__.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/utils/__init__.py` | igration script helper modules. | 0 |
| **Базовый** | `agents.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate/agents.py` | Convert Claude Code subagents into Codex custom-agent TOML. | 0 |
| **Базовый** | `az-sub-init.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/cluster-azure/terraform/prerequisites/az-sub-init.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `build_ownership_map.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/security-ownership-map/scripts/build_ownership_map.py` | !/usr/bin/env python3 Build a security ownership map from git history. | 0 |
| **Базовый** | `civic_graphql.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/civic-skill/scripts/civic_graphql.py` | !/usr/bin/env python3 Compact CIViC GraphQL client for ChatGPT-imported skills. | 0 |
| **Базовый** | `cli.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/cli.py` | CLI orchestration for migrate-to-codex. | 0 |
| **Базовый** | `clinicaltrials_client.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/clinicaltrials-skill/scripts/clinicaltrials_client.py` | !/usr/bin/env python3 Compact ClinicalTrials.gov v2 helper for ChatGPT-imported skills. | 0 |
| **Базовый** | `clinvar_variation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/clinvar-variation-skill/scripts/clinvar_variation.py` | !/usr/bin/env python3 Compact ClinVar + NCBI Variation helper for ChatGPT-imported skills. | 0 |
| **Базовый** | `codex_config.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate/codex_config.py` | Render Codex config from Claude Code settings and MCP inputs. | 0 |
| **Базовый** | `common.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate/common.py` | Shared data models, frontmatter rendering, reporting, and path helpers. | 0 |
| **Базовый** | `community_maintainers.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/security-ownership-map/scripts/community_maintainers.py` | !/usr/bin/env python3 Report monthly maintainers for a file's community. | 0 |
| **Базовый** | `compose_atlas.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/hatch-pet/scripts/compose_atlas.py` | !/usr/bin/env python3 Compose or normalize a Codex pet spritesheet atlas. | 0 |
| **Базовый** | `deploy.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/vercel-deploy/scripts/deploy.sh` | Vercel Deployment Script (via claimable deploy endpoint) Usage: ./deploy.sh [project-path] | 0 |
| **Базовый** | `derive_running_left_from_running_right.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/hatch-pet/scripts/derive_running_left_from_running_right.py` | !/usr/bin/env python3 Conditionally derive running-left by mirroring the approved running-right strip. | 0 |
| **Базовый** | `ensure_macos_permissions.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/screenshot/scripts/ensure_macos_permissions.sh` | !/usr/bin/env bash | 0 |
| **Базовый** | `extract_strip_frames.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/hatch-pet/scripts/extract_strip_frames.py` | !/usr/bin/env python3 Extract generated horizontal row strips into 192x208 sprite frames. | 0 |
| **Базовый** | `fetch_comments.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/gh-address-comments/scripts/fetch_comments.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `fix_acrobat_genuine.ps1` | `scripts/fix_acrobat_genuine.ps1` | fix_acrobat_genuine.ps1 Comprehensive Adobe Acrobat Genuine & Deactivation Popup Eliminator | 0 |
| **Базовый** | `fix_acrobat_genuine.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/fix_acrobat_genuine.ps1` | fix_acrobat_genuine.ps1 Comprehensive Adobe Acrobat Genuine & Deactivation Popup Eliminator | 1 |
| **Базовый** | `gnomad_graphql.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/gnomad-graphql-skill/scripts/gnomad_graphql.py` | !/usr/bin/env python3 Compact gnomAD GraphQL client for ChatGPT-imported skills. | 0 |
| **Базовый** | `hooks.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate/hooks.py` | Convert supported Claude Code hooks into Codex hook config. | 0 |
| **Базовый** | `inspect_frames.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/hatch-pet/scripts/inspect_frames.py` | !/usr/bin/env python3 Inspect extracted Codex pet frames before atlas composition. | 0 |
| **Базовый** | `install-terraform.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/cluster-azure/terraform/prerequisites/install-terraform.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `install.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/inference-nim-operator/scripts/install.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `install.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/inference-azure/scripts/install.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `instructions.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate/instructions.py` | Discover and classify source instruction files for AGENTS.md migration. | 0 |
| **Базовый** | `make_contact_sheet.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/hatch-pet/scripts/make_contact_sheet.py` | !/usr/bin/env python3 Create a labeled contact sheet from a Codex pet atlas. | 0 |
| **Базовый** | `mcps.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate/mcps.py` | Convert Claude Code MCP/settings JSON into Codex config TOML. | 0 |
| **Базовый** | `migrate-to-codex.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate-to-codex.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `ncbi_datasets.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/ncbi-datasets-skill/scripts/ncbi_datasets.py` | !/usr/bin/env python3 Compact NCBI Datasets v2 helper for imported skills. | 0 |
| **Базовый** | `ncbi_entrez.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/ncbi-entrez-skill/scripts/ncbi_entrez.py` | !/usr/bin/env python3 Compact NCBI Entrez E-Utilities helper for imported skills. | 0 |
| **Базовый** | `ncbi_gene_clinicaltables.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/ncbi-clinicaltables-skill/scripts/ncbi_gene_clinicaltables.py` | !/usr/bin/env python3 Compact Clinical Tables NCBI Gene helper for imported skills. | 0 |
| **Базовый** | `ncbi_pmc.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/ncbi-pmc-skill/scripts/ncbi_pmc.py` | !/usr/bin/env python3 Compact NCBI PMC Open Access helper for imported skills. | 0 |
| **Базовый** | `new_notebook.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/jupyter-notebook/scripts/new_notebook.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `normalize_node_id.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/figma-code-connect-components/scripts/normalize_node_id.py` | !/usr/bin/env python3 Normalize a Figma node-id between URL and tool formats. | 0 |
| **Базовый** | `opentargets_graphql.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/opentargets-skill/scripts/opentargets_graphql.py` | !/usr/bin/env python3 Compact Open Targets GraphQL client for ChatGPT-imported skills. | 0 |
| **Базовый** | `playwright_cli.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/playwright/scripts/playwright_cli.sh` | !/usr/bin/env bash | 0 |
| **Базовый** | `plugins.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate/plugins.py` | Report Claude Code plugin surfaces that need manual Codex migration. | 0 |
| **Базовый** | `prepare_pet_run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/hatch-pet/scripts/prepare_pet_run.py` | !/usr/bin/env python3 Create a Codex pet run folder, prompts, and imagegen job manifest. | 0 |
| **Базовый** | `query_ownership.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/security-ownership-map/scripts/query_ownership.py` | !/usr/bin/env python3 Query ownership-map outputs without loading everything into an LLM context. | 0 |
| **Базовый** | `register-azure-providers.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/cluster-azure/terraform/prerequisites/register-azure-providers.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `render_animation_previews.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/hatch-pet/scripts/render_animation_previews.py` | !/usr/bin/env python3 Render lightweight animated QA previews from extracted Codex pet frames. | 0 |
| **Базовый** | `resolve_unassociated.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scripts/resolve_unassociated.py` | Setup path to import app config and services | 6 |
| **Базовый** | `resolve_unassociated.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_v6_backup/archive/backup_20260805_v4plus/resolve_unassociated.py` | Setup path to import app config and services | 8 |
| **Базовый** | `resolve_unassociated.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/resolve_unassociated.py` | Setup path to import app config and services | 1 |
| **Базовый** | `rest_request.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/uniprot-skill/scripts/rest_request.py` | !/usr/bin/env python3 Generic compact REST client for ChatGPT-imported skills. | 29 |
| **Базовый** | `rest_request.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/eqtl-catalogue-skill/scripts/rest_request.py` | !/usr/bin/env python3 Generic compact REST client for ChatGPT-imported skills. | 0 |
| **Базовый** | `run_ownership_map.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/security-ownership-map/scripts/run_ownership_map.py` | !/usr/bin/env python3 One-shot runner for building the security ownership map. | 0 |
| **Базовый** | `scan.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/utils/scan.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `settings.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate/settings.py` | Shared source path constants for migration discovery/reporting. | 0 |
| **Базовый** | `setup.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/cluster-azure/scripts/setup.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `show_llm_stats.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scripts/show_llm_stats.py` | Setup path to import app config | 0 |
| **Базовый** | `skills.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate/skills.py` | Convert Claude Code skills and commands into Codex skills. | 0 |
| **Базовый** | `sparql_request.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/bgee-skill/scripts/sparql_request.py` | !/usr/bin/env python3 Compact Bgee SPARQL client for ChatGPT-imported skills. | 0 |
| **Базовый** | `take_screenshot.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/screenshot/scripts/take_screenshot.ps1` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `take_screenshot.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/screenshot/scripts/take_screenshot.py` | !/usr/bin/env python3 Cross-platform screenshot helper for Codex skills. | 0 |
| **Базовый** | `text_to_speech.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/speech/scripts/text_to_speech.py` | !/usr/bin/env python3 Generate speech audio with the OpenAI Audio API (TTS). | 0 |
| **Базовый** | `transcribe_diarize.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/transcribe/scripts/transcribe_diarize.py` | !/usr/bin/env python3 Transcribe audio (optionally with speaker diarization) using OpenAI. | 0 |
| **Базовый** | `update_email_compose.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_migration_backup_20260809/vps_backups/update_email_compose.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `update_vps_compose.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_migration_backup_20260809/vps_backups/update_vps_compose.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `util.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/utils/util.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `validate_atlas.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/hatch-pet/scripts/validate_atlas.py` | !/usr/bin/env python3 Validate a Codex pet spritesheet atlas. | 0 |
| **Базовый** | `weekly_run.bat` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/local_inventory/inventory/weekly_run.bat` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `weekly_run.bat` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/weekly_run.bat` | Автоматизация рабочего процесса. | 3 |
| **Расширенный** | `check_agents_md.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/figma-create-design-system-rules/scripts/check_agents_md.sh` | !/usr/bin/env bash Draft helper: report whether AGENTS.md exists at repo root. | 0 |
| **Расширенный** | `check_and_clean_pc.py` | `scripts/check_and_clean_pc.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `check_and_clean_pc.py` | `D:/Soft/Codex Backup/scripts/check_and_clean_pc.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `check_and_clean_pc.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/check_and_clean_pc.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `inspect_pr_checks.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/vendor_imports/skills/skills/.curated/gh-fix-ci/scripts/inspect_pr_checks.py` | !/usr/bin/env python3 | 0 |
| **Диагностический** | `check_db_status.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/check_db_status.py` | Setup path to import app config | 8 |
| **Диагностический** | `preflight.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/osmo-k8s/scripts/preflight.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `preflight.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/osmo-cli/scripts/preflight.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `preflight.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/osmo-azure/scripts/preflight.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `preflight.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/inference-nvcf/scripts/preflight.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `preflight.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/inference-nim-operator/scripts/preflight.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `preflight.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/inference-azure/scripts/preflight.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `preflight.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/cluster-microk8s/scripts/preflight.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `preflight.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/cluster-azure/scripts/preflight.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `system_node_capacity_test.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/physical-ai-infrastructure-setup-and-resilient-scaling/components/cluster-azure/scripts/system_node_capacity_test.sh` | !/usr/bin/env bash SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `update_email_compose.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/diagnostics/update_email_compose.py` | Автоматизация рабочего процесса. | 8 |
| **Диагностический** | `update_vps_compose.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/diagnostics/update_vps_compose.py` | Автоматизация рабочего процесса. | 8 |

---

<a id='session_compression'></a>
## 8. Анализ истории чата, сжатие сессий и /learn

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `apply_complete_sintez_summary.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/apply_complete_sintez_summary.py` | 1. Start SSH tunnel locally | 4 |
| **Базовый** | `build_index.py` | `scripts/build_index.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `build_index.py` | `D:/Soft/Codex Backup/scripts/build_index.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `build_index.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scripts/build_index.py` | normalize path separators | 0 |
| **Базовый** | `build_index.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/build_index.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `export_report.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/morningstar/skills/fund-summarizer/scripts/export_report.py` | !/usr/bin/env python3 Export a rendered Morningstar fund summary HTML report to PDF. | 0 |
| **Базовый** | `full_gravity_audit.py` | `scripts/full_gravity_audit.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `full_gravity_audit.py` | `D:/Soft/Codex Backup/scripts/full_gravity_audit.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `full_gravity_audit.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/full_gravity_audit.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_local_summary.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/generate_local_summary.py` | 1. Start SSH tunnel locally to connect to VPS Postgres | 4 |
| **Базовый** | `icon_embedder.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/morningstar/skills/fund-summarizer/scripts/icon_embedder.py` | Inline Morningstar rating icons into the fund summary template. | 0 |
| **Базовый** | `parse_sprint_summary.py` | `scripts/parse_sprint_summary.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `parse_sprint_summary.py` | `D:/Soft/Codex Backup/scripts/parse_sprint_summary.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `parse_sprint_summary.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/parse_sprint_summary.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `placeholder_defaults.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/morningstar/skills/fund-summarizer/scripts/placeholder_defaults.py` | Placeholder registry and default display values for fund summary reports. | 0 |
| **Базовый** | `print_xlsx_summary.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/print_xlsx_summary.py` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `run_single_sintez_summary.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/run_single_sintez_summary.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `section_builders.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/morningstar/skills/fund-summarizer/scripts/section_builders.py` | Build derived HTML placeholders from structured fund summary data. | 0 |
| **Базовый** | `session_compress.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/session_compress.py` | Определяем корневую директорию проекта на основе расположения скрипта скрипт лежит в <root>/scripts/session_compress.py | 2 |
| **Базовый** | `session_compress.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scripts/session_compress.py` | Определяем корневую директорию проекта на основе расположения скрипта скрипт лежит в <root>/scripts/session_compress.py | 0 |
| **Базовый** | `summary_service.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/services/summary_service.py` | 1. Fetch contact messages (both processed and unprocessed to get full context) | 8 |
| **Расширенный** | `check_sintez_summary.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_funnel_version/scratch/check_sintez_summary.py` | Автоматизация рабочего процесса. | 1 |
| **Расширенный** | `check_sintez_summary.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/check_sintez_summary.py` | Автоматизация рабочего процесса. | 2 |

---

<a id='onec_bitrix_sync'></a>
## 9. Связка 1С:УНФ и Битрикс24 (OData, Контрагенты, Заказы, СКД)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `5e469a8be92c_add_unique_constraint_to_onec_owner_.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/alembic/versions/5e469a8be92c_add_unique_constraint_to_onec_owner_.py` | add unique constraint to onec_owner_links | 8 |
| **Базовый** | `a705ca4e0aee_add_onec_owner_links_and_is_synthetic.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/alembic/versions/a705ca4e0aee_add_onec_owner_links_and_is_synthetic.py` | add onec_owner_links and is_synthetic | 8 |
| **Базовый** | `analyze_odata.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/analyze_odata.py` | Автоматизация рабочего процесса. | 7 |
| **Базовый** | `analyze_odata.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scripts/analyze_odata.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `b24_chat_intelligence.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/b24_chat_intelligence.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `build_exam_docx.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/build_exam_docx.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `build_kpi_erf.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/build_kpi_erf.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `build_master_regulation_docx.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/build_master_regulation_docx.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `build_scripts_registry.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/build_scripts_registry.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `catalog_scripts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/catalog_scripts.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `deal_followup_pipeline.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/1c_odata/scripts/deal_followup_pipeline.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `deal_followup_pipeline.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/deal_followup_pipeline.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `deep_inspect_batch_12.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/deep_inspect_batch_12.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `deep_inspect_batch_12_first4.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/deep_inspect_batch_12_first4.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `docx_engine.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/docx_engine.py` | Color Palette | 0 |
| **Базовый** | `docx_styler.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/docx_styler.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `dump_lead_groups.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/dump_lead_groups.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `execute_batch_3.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/execute_batch_3.py` | ------------------------------------------------------------- CREDENTIALS & CONSTANTS | 0 |
| **Базовый** | `execute_batch_4.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/execute_batch_4.py` | ------------------------------------------------------------- CREDENTIALS & CONSTANTS | 0 |
| **Базовый** | `execute_batch_pipeline.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/execute_batch_pipeline.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `execute_mxl_batch.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/execute_mxl_batch.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `extract_all_target_chat_messages.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/extract_all_target_chat_messages.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `fetch_b24_details.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/fetch_b24_details.py` | 1. Company 11886 | 0 |
| **Базовый** | `fetch_email_119.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/fetch_email_119.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_batch_4_dry_run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/generate_batch_4_dry_run.py` | Constants | 0 |
| **Базовый** | `group_scripts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/group_scripts.py` | Categories definition | 0 |
| **Базовый** | `inspect_batch_12.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/inspect_batch_12.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_batch_4_details.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/inspect_batch_4_details.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_batch_5_bodies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/inspect_batch_5_bodies.py` | Print body preview We can inspect the attachments or bodies | 0 |
| **Базовый** | `inspect_deal_2166.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/inspect_deal_2166.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_docs_detailed.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/inspect_docs_detailed.py` | 1. Inspect i7858_Договор_по_КК_РОС.doc xtract text by searching for words in binary doc | 0 |
| **Базовый** | `inspect_item_details.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/inspect_item_details.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `odata_search_entities.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/odata_search_entities.py` | 1. Search contractors | 0 |
| **Базовый** | `print_batch_4_bodies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/print_batch_4_bodies.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `print_batch_5.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/print_batch_5.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `print_bodies_batch_5.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/print_bodies_batch_5.py` | Let's inspect IMAP bodies from scratch/attachments_batch_41_50 or re-fetch body | 0 |
| **Базовый** | `print_items_35_36_38.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/print_items_35_36_38.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `process_b24_inbound_leads.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/process_b24_inbound_leads.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `process_batch_pipeline.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/process_batch_pipeline.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `process_today_followup_deals.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/1c_odata/scripts/process_today_followup_deals.py` | !/usr/bin/env python3 | 1 |
| **Базовый** | `process_today_followup_deals.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/process_today_followup_deals.py` | !/usr/bin/env python3 | 1 |
| **Базовый** | `qualify_batch_5.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/qualify_batch_5.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_1c_entities.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/1c_odata/scripts/search_1c_entities.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `search_1c_entities.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/search_1c_entities.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_agrosnab.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/search_agrosnab.py` | 1. Search Leads | 0 |
| **Базовый** | `search_b24_emails.py` | `scratch/search_b24_emails.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_dadata_batch_4.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/search_dadata_batch_4.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_tasks_and_topics.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/search_tasks_and_topics.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `summarize_batch_4.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/summarize_batch_4.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `update_gas_exam.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/update_gas_exam.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_contact_15984.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/check_contact_15984.py` | 1. B24 Contact 15984 | 0 |
| **Расширенный** | `check_contractor.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/1c_odata/check_contractor.py` | !/usr/bin/env python3 | 3 |
| **Расширенный** | `check_contractor.py` | `D:/Soft/Codex Backup/projects/1c_odata/check_contractor.py` | !/usr/bin/env python3 | 1 |
| **Расширенный** | `check_contractor.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/check_contractor.py` | !/usr/bin/env python3 | 1 |
| **Расширенный** | `check_niiemp_sync.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/check_niiemp_sync.py` | 1.1 Company by INN | 0 |
| **Расширенный** | `check_snab_region.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/check_snab_region.py` | 1. Inspect Lead 000001663 in 1C | 0 |
| **Расширенный** | `inspect_b24_deals.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/inspect_b24_deals.py` | Also check company for rsce.ru | 0 |
| **Расширенный** | `inspect_item_119.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/inspect_item_119.py` | Let's check IMAP message for item 119 or scratch files | 0 |
| **Расширенный** | `inspect_petroship_email.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/inspect_petroship_email.py` | Check activities on Contact 16332 and Lead 17338 | 0 |
| **Расширенный** | `odata_audit_pavlova_cilin.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/odata_audit_pavlova_cilin.py` | 1. Check document 96 | 0 |
| **Расширенный** | `onec_sync_service.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/services/onec_sync_service.py` | Автоматизация рабочего процесса. | 7 |
| **Расширенный** | `onec_sync_service.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/app/services/onec_sync_service.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `prepare_excel_for_1c.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/prepare_excel_for_1c.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `run_check_contractors_batch_4.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/run_check_contractors_batch_4.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `run_onec_sync.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/run_onec_sync.py` | Автоматизация рабочего процесса. | 8 |
| **Расширенный** | `sync_b24_to_novofon.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/sync_b24_to_novofon.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `sync_to_bitrix.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/1c_odata/scripts/sync_to_bitrix.py` | Автоматизация рабочего процесса. | 1 |
| **Расширенный** | `sync_to_bitrix.py` | `D:/Soft/Codex Backup/projects/1c_odata/scripts/sync_to_bitrix.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `sync_to_bitrix.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scripts/sync_to_bitrix.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_odata_filter.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/test_odata_filter.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_odata_url.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/test_odata_url.py` | Автоматизация рабочего процесса. | 7 |
| **Диагностический** | `test_odata_url.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scripts/test_odata_url.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_patch_row.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/test_patch_row.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `verify_batch_4.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/1c_odata/scratch/verify_batch_4.py` | Автоматизация рабочего процесса. | 0 |

---

<a id='lead_inbound'></a>
## 10. Обработка новых лидов и Inbound-снабжение (Email AI Pipeline)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `analyze_unassociated.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/analyze_unassociated.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `apply_unassociated_matches.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/apply_unassociated_matches.py` | Автоматизация рабочего процесса. | 17 |
| **Базовый** | `fetch_raw_emails.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_funnel_version/scratch/fetch_raw_emails.py` | 1. Start SSH tunnel locally | 1 |
| **Базовый** | `remote_n8n_fix.sh` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/server_ops/snapshots/remote_n8n_fix.sh` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `remote_n8n_fix2.sh` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/server_ops/snapshots/remote_n8n_fix2.sh` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `run_imap.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/run_imap.py` | Load env variables | 8 |
| **Базовый** | `text_cleaner.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/services/text_cleaner.py` | 1. Если исходный текст совсем пустой, но есть HTML, используем его | 8 |
| **Расширенный** | `check_drive_access.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/check_drive_access.py` | Если вы измените эти области доступа, удалите файл token.json. | 1 |
| **Расширенный** | `check_drive_access.py` | `D:/Soft/Codex Backup/scripts/check_drive_access.py` | Если вы измените эти области доступа, удалите файл token.json. | 0 |
| **Расширенный** | `run_junk_filter.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/run_junk_filter.py` | Get messages that are currently 'needs_review' and not processed by junk filter We can identify them by checking EmailMatchResult.decision == 'needs_review' | 8 |

---

<a id='followup_sales'></a>
## 11. Follow-up продаж в сделках и реактивация клиентов

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `run_daily_reactivation.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_v6_backup/app/run_daily_reactivation.py` | Setup path | 1 |
| **Базовый** | `run_daily_reactivation.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_migration_backup_20260809/app/run_daily_reactivation.py` | Setup path | 1 |
| **Базовый** | `run_daily_reactivation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/run_daily_reactivation.py` | Setup path | 1 |
| **Базовый** | `run_daily_reactivation.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_backup/app/run_daily_reactivation.py` | Setup path | 1 |
| **Базовый** | `run_daily_reactivation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/app/run_daily_reactivation.py` | Setup path | 0 |
| **Расширенный** | `bitrix_golden_phrases.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/bitrix_golden_phrases.py` | Setup path | 8 |
| **Диагностический** | `test_pilot_reactivation.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_v6_backup/scripts/test_pilot_reactivation.py` | Setup path | 1 |
| **Диагностический** | `test_pilot_reactivation.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_v6_backup/archive/backup_20260805_v4plus/test_pilot_reactivation.py` | Setup path | 3 |
| **Диагностический** | `test_pilot_reactivation.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_funnel_version/scripts/test_pilot_reactivation.py` | Setup path | 1 |
| **Диагностический** | `test_pilot_reactivation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_v6_backup/scripts/test_pilot_reactivation.py` | Setup path | 1 |
| **Диагностический** | `test_pilot_reactivation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_v6_backup/archive/backup_20260805_v4plus/test_pilot_reactivation.py` | Setup path | 4 |
| **Диагностический** | `test_pilot_reactivation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/test_pilot_reactivation.py` | Setup path | 1 |
| **Диагностический** | `test_pilot_reactivation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scripts/test_pilot_reactivation.py` | Setup path | 0 |

---

<a id='idempotent_crm_1c'></a>
## 12. Синхронизация лидов и компаний в 1С и Битрикс24 (Idempotent CRM)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Расширенный** | `patch_n8n.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/patch_n8n.py` | Автоматизация рабочего процесса. | 8 |
| **Расширенный** | `patch_n8n_mode.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/patch_n8n_mode.py` | Автоматизация рабочего процесса. | 8 |
| **Интеграционный** | `reconcile_1c_db.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/reconcile_1c_db.py` | Автоматизация рабочего процесса. | 8 |

---

<a id='tenders_goz'></a>
## 13. Тендеры, АСТ ГОЗ и RAG-пайплайн спецификаций

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `add_error_handling.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/scratch/add_error_handling.py` | --------------------------------------------------------- 1. Error Trigger & Notify Error | 1 |
| **Базовый** | `analyze_exact_balances.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/analyze_exact_balances.py` | Fetch all balances for suppliers | 0 |
| **Базовый** | `analyze_exact_details.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/analyze_exact_details.py` | Organizations | 0 |
| **Базовый** | `analyze_pavlova_gap.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/analyze_pavlova_gap.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `analyze_target_math.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/analyze_target_math.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `analyze_user_query.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/analyze_user_query.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `audit_bank_commissions.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/audit_bank_commissions.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `audit_contract_952_all.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/audit_contract_952_all.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `audit_pavlova_deep.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/audit_pavlova_deep.py` | 1. Contracts | 0 |
| **Базовый** | `audit_unf_comprehensive.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/audit_unf_comprehensive.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `base.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tries/base.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `build_full_markdown_artifact.py` | `scripts/build_full_markdown_artifact.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `build_full_markdown_artifact.py` | `D:/Soft/Codex Backup/scripts/build_full_markdown_artifact.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `build_full_markdown_artifact.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/build_full_markdown_artifact.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `calc_cilin_reg_sums.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/calc_cilin_reg_sums.py` | Catalog_Валюты | 0 |
| **Базовый** | `calc_exact_categories.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/calc_exact_categories.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `calc_itogo_math.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/calc_itogo_math.py` | The 3 orgs in the report: Long Wang LLC | 0 |
| **Базовый** | `calc_summa_reg_live.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/calc_summa_reg_live.py` | 1. Balances in РасчетыСПокупателями | 0 |
| **Базовый** | `calculate_exact_profit_adjustment.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/calculate_exact_profit_adjustment.py` | 1. Exact Otgruzka total profit In otgruzka, let's find the top organization totals | 0 |
| **Базовый** | `categorize_debts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/categorize_debts.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `chanker_gemini_1.py` | `ARCHIVE/GOZ/ACT/_РАЗОБРАНО 13-05/chanker_gemini_1.py` | Улучшенные регулярные выражения (убраны полезные слова из негативных паттернов) Теперь исключаем только реальный юридический мусор, не трогая условия приемки | 2 |
| **Базовый** | `chunks_jsonl_to_xlsx.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/chunks_jsonl_to_xlsx.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `clean_signature.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/Доки и записи/clean_signature.py` | 1. Открываем изображение | 5 |
| **Базовый** | `clean_stamp.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/Доки и записи/clean_stamp.py` | 1. перед всем этим установить  pip install pillow | 5 |
| **Базовый** | `comments_extract.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/comments_extract.py` | !/usr/bin/env python3 Extract DOCX comments into JSON (with anchored snippet). | 0 |
| **Базовый** | `compare_1c_expenses.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/compare_1c_expenses.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_26_84.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/compare_26_84.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_92_96.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/compare_92_96.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_all_26_96.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/compare_all_26_96.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_built_vs_gold_19_05.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/compare_built_vs_gold_19_05.py` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `compare_cilin_contractors_detailed.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/compare_cilin_contractors_detailed.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_contractors_vz.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/compare_contractors_vz.py` | ad sheet 4_Подрядчики_и_Услуги | 0 |
| **Базовый** | `compare_fields_46_96.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/compare_fields_46_96.py` | Fetch TLНФ-000046 and TLНФ-000096 | 0 |
| **Базовый** | `compare_movements_26_84_96.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/compare_movements_26_84_96.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_orgs_registers.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/compare_orgs_registers.py` | 1. Get all organizations | 0 |
| **Базовый** | `compare_recordsets_26_96.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/compare_recordsets_26_96.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_with_gold_19_05.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/compare_with_gold_19_05.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `config.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/app/core/config.py` | odels | 0 |
| **Базовый** | `consolidated_azat_balance.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/consolidated_azat_balance.py` | Organizations | 0 |
| **Базовый** | `copy_from_manifest.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/scripts/migration/copy_from_manifest.ps1` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `copy_from_manifest.ps1` | `D:/Soft/Codex Backup/projects/tender-extraction-lab/scripts/migration/copy_from_manifest.ps1` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `count_contacts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/count_contacts.py` | Автоматизация рабочего процесса. | 7 |
| **Базовый** | `count_contacts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scripts/count_contacts.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `debug_doc84_keys.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/debug_doc84_keys.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `debug_live_site.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/debug_live_site.py` | Disable redirect following to see if there is a redirect print first 500 characters of response HTML | 2 |
| **Базовый** | `debug_rank_lot_builder.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/debug_rank_lot_builder.py` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `deep_dive.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/deep_dive.py` | --- PART 1: Examine 'долги Ци Линь.xlsx' formulas and structure --- | 0 |
| **Базовый** | `deep_investigation_cost_and_settlements.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/deep_investigation_cost_and_settlements.py` | Organizations | 0 |
| **Базовый** | `dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/app/api/dependencies.py` | Функция для инъекции сервиса обработки документов | 2 |
| **Базовый** | `deploy.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/scripts/deploy.sh` | Скрипт автоматического развертывания Tender RAG API | 1 |
| **Базовый** | `document.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/app/schemas/document.py` | Схема для описания структуры одного чанка | 1 |
| **Базовый** | `document.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/app/services/document.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `document.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/app/api/routers/document.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `dump_all_contract_receipts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/dump_all_contract_receipts.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `export_fines_and_taxes.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/export_fines_and_taxes.py` | 1. Fetch exact details for the 8 documents of "Прочее" + Doc 18 | 0 |
| **Базовый** | `extract-audio-data.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hyperframes/skills/gsap/scripts/extract-audio-data.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `extract_js_context.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/extract_js_context.py` | print 1000 characters before and after | 2 |
| **Базовый** | `extract_pdf_text.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_v6_backup/scripts/extract_pdf_text.py` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `extract_pdf_text.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/extract_pdf_text.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `extract_sprint_points.py` | `scripts/extract_sprint_points.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `extract_sprint_points.py` | `D:/Soft/Codex Backup/scripts/extract_sprint_points.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `extract_sprint_points.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/extract_sprint_points.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `find_10k_gap.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/find_10k_gap.py` | Let's clean the string prefixes like '[ 123] ' | 0 |
| **Базовый** | `find_adjustment_entities.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/find_adjustment_entities.py` | Fetch metadata document list | 0 |
| **Базовый** | `find_aug_2026_receipts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/find_aug_2026_receipts.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_azat_luvan.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/find_azat_luvan.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_doc84_movs.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/find_doc84_movs.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_incoming_emails.py` | `scratch/find_incoming_emails.py` | Query all incoming email activities | 0 |
| **Базовый** | `find_salary_entities.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/find_salary_entities.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_salary_payments.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/find_salary_payments.py` | Search РасходСоСчета | 0 |
| **Базовый** | `find_vz_registers.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/find_vz_registers.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_detailed_reconciliation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/generate_detailed_reconciliation.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_final_analysis_wb.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/generate_final_analysis_wb.py` | ove default sheet | 0 |
| **Базовый** | `get_all_pavlova_contracts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/get_all_pavlova_contracts.py` | Currencies | 0 |
| **Базовый** | `get_currency.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/get_currency.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `get_ql_pav_contracts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/get_ql_pav_contracts.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `get_ql_pav_contracts_fixed.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/get_ql_pav_contracts_fixed.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `h02__del_date_priority.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tries/h02__del_date_priority.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `h04__del_deadline_clause_boost.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tries/h04__del_deadline_clause_boost.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `h05__del_always_scan_docx_raw.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tries/h05__del_always_scan_docx_raw.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `h06__del_force_fixed_date_from_raw.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tries/h06__del_force_fixed_date_from_raw.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `h07__del_accept_ne_pozdnee_date.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tries/h07__del_accept_ne_pozdnee_date.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `h08__del_raw_fixed_date_override.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tries/h08__del_raw_fixed_date_override.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `h09__del_raw_fixed_date_plus_gate.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tries/h09__del_raw_fixed_date_plus_gate.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `h10__pay_drop_no_responsibility.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tries/h10__pay_drop_no_responsibility.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `health.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/app/api/routers/health.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `inspect_acc_reg_format.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_acc_reg_format.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_all_postuplenie.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_all_postuplenie.py` | Currencies | 0 |
| **Базовый** | `inspect_all_receipts_register.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_all_receipts_register.py` | 1. Fetch matching docs | 0 |
| **Базовый** | `inspect_baobo_movements.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_baobo_movements.py` | Search for Changzhou Baobo contractor key | 0 |
| **Базовый** | `inspect_contract_952.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_contract_952.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_contractor_all_regs.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_contractor_all_regs.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_cross_vz_details.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_cross_vz_details.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_desktop_files.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_desktop_files.py` | xtract strings in {"#", "..."} clean unescaped | 0 |
| **Базовый** | `inspect_details_123.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_details_123.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_doc26.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_doc26.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_doc96_registers.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_doc96_registers.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_ozon_per_org.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_ozon_per_org.py` | Let's inspect Ozon records per Organization | 0 |
| **Базовый** | `inspect_pnl_register.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_pnl_register.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_ql_rows.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_ql_rows.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_raw_b_sup.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_raw_b_sup.py` | Balances in РасчетыСПоставщиками | 0 |
| **Базовый** | `inspect_recorder_format.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_recorder_format.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_summa_ucheta.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_summa_ucheta.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_sup_balances_live.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_sup_balances_live.py` | Currencies | 0 |
| **Базовый** | `inspect_tables_19_05.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/inspect_tables_19_05.py` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `inspect_vzaimozachet.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_vzaimozachet.py` | Search for doc 5 and 8 in 2024 | 0 |
| **Базовый** | `inspect_vzaimozachet_1012.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_vzaimozachet_1012.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `install_webkit_wsl.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/install_webkit_wsl.ps1` | This script sets up a WSL distribution that will be used to run WebKit. | 2 |
| **Базовый** | `investigate_azat_luvan_cost.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/investigate_azat_luvan_cost.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `investigate_debts_and_fines.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/investigate_debts_and_fines.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `investigate_discrepancies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/investigate_discrepancies.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `investigate_ozon_and_mxl.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/investigate_ozon_and_mxl.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `investigate_target_org.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/investigate_target_org.py` | Let's inspect all rows under ЦИ ЛИНЬ ООО | 0 |
| **Базовый** | `investigate_user_queries.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/investigate_user_queries.py` | Let's inspect the exact docs that gave 352,880.03 in our previous script | 0 |
| **Базовый** | `key_manager.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/app/core/key_manager.py` | Deduplicate while preserving order | 0 |
| **Базовый** | `list_25_sup_rows.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/list_25_sup_rows.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `list_all_vz.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/list_all_vz.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `list_contract_receipts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/list_contract_receipts.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `list_mismatched_lots.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/list_mismatched_lots.py` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `llm_service.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/app/services/llm_service.py` | Ограничиваем количество чанков (Token-First Vibe Engineering) | 0 |
| **Базовый** | `lot_builder_from_chunks_v1.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/lot_builder_from_chunks_v1.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `lot_chunker_md_v1.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/lot_chunker_md_v1.py` | !/usr/bin/env python3 | 23 |
| **Базовый** | `lot_chunker_v1.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/lot_chunker_v1.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `main.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/app/main.py` | Подключаем наши роутеры | 1 |
| **Базовый** | `make_clean_audit_wb.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/make_clean_audit_wb.py` | Styles | 0 |
| **Базовый** | `make_contact_sheet.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/presentations/26.601.10930/skills/presentations/scripts/make_contact_sheet.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `match_contracts_py.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/match_contracts_py.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `md_chunker.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/n8n_email_ai/rag_tools/md_chunker.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `md_chunker.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/50_rag_tools/md_chunker.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `ngs_epigenomics_utils.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/ngs_epigenomics_utils.py` | !/usr/bin/env python3 Shared epigenomics artifact parsers and browser-track helpers. | 0 |
| **Базовый** | `parse_customs_balances.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/parse_customs_balances.py` | In this report, structure is: L0: Organization | 0 |
| **Базовый** | `parse_mxl_reports.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/parse_mxl_reports.py` | decode utf-8 ignoring errors or look for strings xtract strings in {"#", "..."} | 0 |
| **Базовый** | `parse_pavlova_mxl_full.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/parse_pavlova_mxl_full.py` | Let's save all non-empty strings with their indices to a text file for complete inspection | 0 |
| **Базовый** | `print_all_doc84.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/print_all_doc84.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `print_ql_block.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/print_ql_block.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `print_ql_children.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/print_ql_children.py` | ows under ЦИ ЛИНЬ ООО (from row 108 to 165) | 0 |
| **Базовый** | `print_raw_doc84_row.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/print_raw_doc84_row.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `print_receipts_ops.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/print_receipts_ops.py` | Operations map | 0 |
| **Базовый** | `probe_all_files.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/probe_all_files.py` | 1. Inspect "доходы и расходы по отгрузке.mxl" for personal expenses / dividends | 0 |
| **Базовый** | `query_doc84_movements.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/query_doc84_movements.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `read_docx.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/scratch/read_docx.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `read_updated_debt_file.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/read_updated_debt_file.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `redact_docx.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/redact_docx.py` | !/usr/bin/env python3 Redact/anonymize text in a DOCX while preserving layout as much as possible. | 0 |
| **Базовый** | `reinstall_chrome_beta_linux.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_beta_linux.sh` | !/usr/bin/env bash | 2 |
| **Базовый** | `reinstall_chrome_beta_mac.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_beta_mac.sh` | !/usr/bin/env bash | 2 |
| **Базовый** | `reinstall_chrome_beta_win.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_beta_win.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `reinstall_chrome_stable_linux.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_stable_linux.sh` | !/usr/bin/env bash | 2 |
| **Базовый** | `reinstall_chrome_stable_mac.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_stable_mac.sh` | !/usr/bin/env bash | 2 |
| **Базовый** | `reinstall_chrome_stable_win.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_stable_win.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `reinstall_msedge_beta_linux.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_beta_linux.sh` | !/usr/bin/env bash | 2 |
| **Базовый** | `reinstall_msedge_beta_mac.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_beta_mac.sh` | !/usr/bin/env bash | 2 |
| **Базовый** | `reinstall_msedge_beta_win.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_beta_win.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `reinstall_msedge_dev_linux.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_dev_linux.sh` | !/usr/bin/env bash | 2 |
| **Базовый** | `reinstall_msedge_dev_mac.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_dev_mac.sh` | !/usr/bin/env bash | 2 |
| **Базовый** | `reinstall_msedge_dev_win.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_dev_win.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `reinstall_msedge_stable_linux.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_stable_linux.sh` | !/usr/bin/env bash | 2 |
| **Базовый** | `reinstall_msedge_stable_mac.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_stable_mac.sh` | !/usr/bin/env bash | 2 |
| **Базовый** | `reinstall_msedge_stable_win.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_stable_win.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `render_sprite_preview_sheet.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/game-studio/scripts/render_sprite_preview_sheet.py` | !/usr/bin/env python3 Render a simple contact sheet from a directory of normalized sprite frames. | 0 |
| **Базовый** | `retroactive_clean_emails.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/retroactive_clean_emails.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `run_atacseq_peaks_qc.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_atacseq_peaks_qc.py` | !/usr/bin/env python3 Run or plan local ATAC-seq alignment, QC, peak, signal, and FRiP artifacts. | 0 |
| **Базовый** | `run_bulk_rnaseq_de.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_bulk_rnaseq_de.py` | !/usr/bin/env python3 Run bulk RNA-seq differential expression with validation and audited artifacts. | 0 |
| **Базовый** | `run_chip_cutrun_peaks_qc.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_chip_cutrun_peaks_qc.py` | !/usr/bin/env python3 Run or plan local ChIP-seq, CUT&RUN, or CUT&Tag peak/QC artifacts. | 0 |
| **Базовый** | `run_chunker_menu.bat` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/batch/run_chunker_menu.bat` | Force UTF-8 codepage so cmd.exe parses this file reliably even on RU systems. (File is kept ASCII-only; this mainly protects user input/paths.) | 14 |
| **Базовый** | `run_chunker_menu.bat` | `ARCHIVE/GOZ/ACT/Доки и записи/run_chunker_menu.bat` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `run_fastq_qc.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_fastq_qc.py` | !/usr/bin/env python3 Run local FASTQ QC with validation, Snakemake execution, and artifacts. | 0 |
| **Базовый** | `run_goz_parser.bat` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/batch/run_goz_parser.bat` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `run_min_context_extractor.bat` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/batch/run_min_context_extractor.bat` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `run_parsed_folders.bat` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/batch/run_parsed_folders.bat` | Usage: un_parsed_folders.bat "C:\Users\Artem\Downloads\GOZ\_PYRUN_1905" | 5 |
| **Базовый** | `run_scrnaseq_fastq_to_count.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_scrnaseq_fastq_to_count.py` | !/usr/bin/env python3 Run local scRNA FASTQ-to-count processing with validation, Snakemake execution, and artifacts. | 0 |
| **Базовый** | `run_shotgun_metagenomics.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_shotgun_metagenomics.py` | !/usr/bin/env python3 Run or plan shotgun metagenomics Kraken2/Bracken/HUMAnN backend artifacts. | 0 |
| **Базовый** | `scan_all_postuplenie_defects.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/scan_all_postuplenie_defects.py` | Fetch all Postuplenie recordsets | 0 |
| **Базовый** | `scan_unrecorded_expenses.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/scan_unrecorded_expenses.py` | 1. Inspect Advance Reports (Авансовые отчеты) in 2026 | 0 |
| **Базовый** | `search_doc_96.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/search_doc_96.py` | Search for doc with amount 47232 | 0 |
| **Базовый** | `search_interactions.py` | `projects/tilda_migration/search_interactions.py` | 1. Links | 0 |
| **Базовый** | `search_interactions.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/search_interactions.py` | 1. Links | 1 |
| **Базовый** | `search_pavlova_mxl.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/search_pavlova_mxl.py` | Search for lines around CNY and around 2 778 272 / 2 788 272 print context | 0 |
| **Базовый** | `show_built_row.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/show_built_row.py` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `show_diff_row.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/show_diff_row.py` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `smart_parser.py` | `ARCHIVE/GOZ/ACT/Доки и записи/Старые парсеры/smart_parser.py` | Извлекает сырой текст из документов, сохраняя структуру таблиц через пайпы | 2 |
| **Базовый** | `smart_parser_v1.py` | `ARCHIVE/GOZ/ACT/Доки и записи/Старые парсеры/smart_parser_v1.py` | Очищенный точечный список ключевых слов для детального логирования | 2 |
| **Базовый** | `smart_parser_v2.py` | `ARCHIVE/GOZ/ACT/Доки и записи/Старые парсеры/smart_parser_v2.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `table_geometry.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/table_geometry.py` | !/usr/bin/env python3 Exact Word table geometry helpers for python-docx. | 0 |
| **Базовый** | `tender_min_context_extractor_v1.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tender_min_context_extractor_v1.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `tender_min_context_extractor_v1.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/примеры/tender_min_context_extractor_v1.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `tender_min_context_extractor_v1.py` | `ARCHIVE/GOZ/ACT/тест/_РАЗОБРАНО 19-05/tender_min_context_extractor_v1.py` | !/usr/bin/env python3 | 2 |
| **Базовый** | `tender_min_context_extractor_v1.py` | `ARCHIVE/GOZ/ACT/Доки и записи/довольно хорошие версии/tender_min_context_extractor_v1.py` | !/usr/bin/env python3 | 2 |
| **Базовый** | `tender_min_context_extractor_v1.py` | `ARCHIVE/GOZ/ACT/Доки и записи/Старые парсеры/tender_min_context_extractor_v1.py` | !/usr/bin/env python3 | 2 |
| **Базовый** | `tender_min_context_extractor_v2.py` | `ARCHIVE/GOZ/ACT/Доки и записи/довольно хорошие версии/tender_min_context_extractor_v2.py` | !/usr/bin/env python3 | 2 |
| **Базовый** | `tender_min_context_extractor_vDeep Seek 1.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/Доки и записи/tender_min_context_extractor_vDeep Seek 1.py` | !/usr/bin/env python3 | 5 |
| **Базовый** | `upload_and_activate.py` | `projects/tilda_migration/upload_and_activate.py` | Get relative files/dirs | 0 |
| **Базовый** | `upload_and_activate.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/upload_and_activate.py` | Get relative files/dirs | 1 |
| **Базовый** | `validate_plugin.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/plugin-creator/scripts/validate_plugin.py` | !/usr/bin/env python3 Validate a generated plugin against the plugin ingestion contract. | 0 |
| **Расширенный** | `analyze_business_balance.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/analyze_business_balance.py` | Check if there are numbers | 0 |
| **Расширенный** | `analyze_cilin_excel_math.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/analyze_cilin_excel_math.py` | Scan rows 57 to 113 (ЦИ ЛИНЬ ООО) | 0 |
| **Расширенный** | `analyze_debts_excel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/analyze_debts_excel.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_17_docs_movements.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_17_docs_movements.py` | ap by recorder GUID | 0 |
| **Расширенный** | `check_2026_regs.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_2026_regs.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_84_92_96.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_84_92_96.py` | Check doc 84 and 92 | 0 |
| **Расширенный** | `check_adj_debt_meta.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_adj_debt_meta.py` | Fetch metadata / sample of Document_КорректировкаДолга | 0 |
| **Расширенный** | `check_cilin_register_details.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_cilin_register_details.py` | Catalog_Валюты | 0 |
| **Расширенный** | `check_cny_rates.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_cny_rates.py` | Fetch currency rates for CNY | 0 |
| **Расширенный** | `check_contract_cur.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_contract_cur.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_contract_props.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_contract_props.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_cross_vzaimozachet.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_cross_vzaimozachet.py` | Fetch contracts currency map | 0 |
| **Расширенный** | `check_doc84_flags.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_doc84_flags.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_doc96_updated.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_doc96_updated.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_manual_adj.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_manual_adj.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_movements_84_96.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_movements_84_96.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_movements_all_postuplenie.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_movements_all_postuplenie.py` | Find their ref keys | 0 |
| **Расширенный** | `check_mxl_headers.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_mxl_headers.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_ops_articles.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_ops_articles.py` | Also check articles | 0 |
| **Расширенный** | `check_owner_naming.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_owner_naming.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_petroship_acts.py` | `scratch/check_petroship_acts.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_pnl_by_org.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_pnl_by_org.py` | Check organizations | 0 |
| **Расширенный** | `check_posted_vz.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_posted_vz.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_recorder_name.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_recorder_name.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_recorder_query.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_recorder_query.py` | Let's inspect doc 96 first, since we know it's posted and verified | 0 |
| **Расширенный** | `check_recordtype.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_recordtype.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_register_resources.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_register_resources.py` | Balances in РасчетыСПоставщиками | 0 |
| **Расширенный** | `check_settlement_registers.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_settlement_registers.py` | Check metadata for AccumulationRegister | 0 |
| **Расширенный** | `check_upr_balance_live.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_upr_balance_live.py` | Check AccountingRegister_Управленческий | 0 |
| **Расширенный** | `check_upr_entries_26.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_upr_entries_26.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_vz_recordsets.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_vz_recordsets.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_vz_registers.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_vz_registers.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `deep_parse_mxl_and_excel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/deep_parse_mxl_and_excel.py` | Let's inspect text lines or tokens In 1C MXL UTF-8 text format, cells are often formatted as strings | 0 |
| **Расширенный** | `dissect_excel_math.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/dissect_excel_math.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `dump_debts_excel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/dump_debts_excel.py` | Print all rows with non-empty content | 0 |
| **Расширенный** | `dump_updated_excel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/dump_updated_excel.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `eval_min_context_vs_gold_19_05.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/scripts/eval/eval_min_context_vs_gold_19_05.py` | !/usr/bin/env python3 | 4 |
| **Расширенный** | `eval_min_context_vs_gold_19_05.py` | `ARCHIVE/GOZ/ACT/eval_min_context_vs_gold_19_05.py` | !/usr/bin/env python3 | 3 |
| **Расширенный** | `find_all_docs_for_contract.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/find_all_docs_for_contract.py` | We want to check ПоступлениеНаСчет and РасходСоСчета and any other docs | 0 |
| **Расширенный** | `inspect_excel_header.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/inspect_excel_header.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `install_media_pack.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/install_media_pack.ps1` | check if running on Windows Server | 2 |
| **Расширенный** | `match_excel_to_1c.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/match_excel_to_1c.py` | Load Excel rows for ЦИ ЛИНЬ ООО | 0 |
| **Расширенный** | `patch_bitrix_url.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/scratch/patch_bitrix_url.py` | Update URL | 1 |
| **Расширенный** | `patch_deal_creation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/scratch/patch_deal_creation.py` | 1. Remove "If Data Extracted" and "Notify No Data" nodes | 1 |
| **Расширенный** | `patch_empty_file_task.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/scratch/patch_empty_file_task.py` | Автоматизация рабочего процесса. | 1 |
| **Расширенный** | `print_all_cilin_excel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/print_all_cilin_excel.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `read_desktop_excel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/read_desktop_excel.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `run_smoke_eval.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/scripts/smoke/run_smoke_eval.ps1` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `run_smoke_eval.ps1` | `D:/Soft/Codex Backup/projects/tender-extraction-lab/scripts/smoke/run_smoke_eval.ps1` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `sum_excel_by_curr.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/sum_excel_by_curr.py` | Let's inspect the entire file долги Ци Линь.xlsx to see where every single counterparty belongs! Sum all rows by currency and compare to the headers! | 0 |
| **Расширенный** | `tender_lot_parser_v7.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/tender_lot_parser_v7.py` | !/usr/bin/env python3 | 5 |
| **Расширенный** | `tender_lot_parser_v7.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/legacy/old_project/ACT/примеры/tender_lot_parser_v7.py` | !/usr/bin/env python3 | 5 |
| **Расширенный** | `tender_lot_parser_v7.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/app/services/tender_lot_parser_v7.py` | !/usr/bin/env python3 | 1 |
| **Интеграционный** | `check_n8n_workflows.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/check_n8n_workflows.py` | Check active workflows | 4 |
| **Интеграционный** | `create_bitrix24_workflow.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/scratch/create_bitrix24_workflow.py` | Автоматизация рабочего процесса. | 1 |
| **Интеграционный** | `generate_v2_1_leads_and_contacts_params_workflow.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/n8n_email_ai/scripts/generate_v2_1_leads_and_contacts_params_workflow.ps1` | Автоматизация рабочего процесса. | 2 |
| **Интеграционный** | `generate_v2_1_leads_and_contacts_params_workflow.ps1` | `ARCHIVE/n8n_email_ai_2026-05-11/scripts/generate_v2_1_leads_and_contacts_params_workflow.ps1` | Автоматизация рабочего процесса. | 13 |
| **Интеграционный** | `merge_workflows.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/scratch/merge_workflows.py` | 1. Start with ingest webhook, but add splitting logic | 1 |
| **Интеграционный** | `reconcile_excel_totals.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/reconcile_excel_totals.py` | Organization rows: row 5 (Long Wang), row 37 (Pavlova), row 57 (Cilin), row 114 (Total) | 0 |
| **Интеграционный** | `run_matrix_onlylot.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tender-extraction-lab/scripts/batch/run_matrix_onlylot.py` | !/usr/bin/env python3 | 4 |
| **Интеграционный** | `run_matrix_onlylot.py` | `ARCHIVE/GOZ/ACT/tries/run_matrix_onlylot.py` | !/usr/bin/env python3 | 3 |
| **Интеграционный** | `run_scrnaseq_post_count_qc.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_scrnaseq_post_count_qc.py` | !/usr/bin/env python3 Run matrix-level scRNA post-count QC with raw-count preservation and auditable artifacts. | 0 |
| **Диагностический** | `check_doc96_status.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/check_doc96_status.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `load_test.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tender-extraction-lab/scratch/load_test.py` | Автоматизация рабочего процесса. | 1 |
| **Диагностический** | `test_audit_entities.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/test_audit_entities.py` | Check salary docs | 0 |
| **Диагностический** | `test_counter_balances.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/test_counter_balances.py` | Contractors map | 0 |
| **Диагностический** | `test_exact_defect_filter.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/test_exact_defect_filter.py` | Currencies | 0 |
| **Диагностический** | `test_filtered_defect.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/test_filtered_defect.py` | Contracts currency map | 0 |
| **Диагностический** | `test_salary_tax_checks.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/test_salary_tax_checks.py` | Check salary payments vs accruals in 2026 | 0 |
| **Диагностический** | `test_uncollapsed_advances.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/test_uncollapsed_advances.py` | Contractors map | 0 |
| **Диагностический** | `test_universal_defect_rule.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/test_universal_defect_rule.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `verify_doc84_impact.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/tenders_ast_goz/scripts/verify_doc84_impact.py` | Check document 84 details | 0 |

---

<a id='infra_vps'></a>
## 14. Инфраструктура, VPS-сервер, Docker и Бэкапы

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `21ff2b48fe8d_add_ai_processed_to_email_match_results.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/alembic/versions/21ff2b48fe8d_add_ai_processed_to_email_match_results.py` | add_ai_processed_to_email_match_results | 8 |
| **Базовый** | `FULL_moz_internal_linking_report.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/GoW Project/FULL_moz_internal_linking_report.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `FULL_moz_internal_linking_report.py` | `D:/Soft/Codex Backup/projects/GoW Project/FULL_moz_internal_linking_report.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `a11y_audit.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/a11y_audit.py` | !/usr/bin/env python3 Accessibility (A11y) audit for DOCX with optional safe fixes. | 0 |
| **Базовый** | `aiq.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/aiq-research/scripts/aiq.py` | !/usr/bin/env python3 SPDX-License-Identifier: Apache-2.0 | 0 |
| **Базовый** | `analyze_all_details.py` | `scripts/analyze_all_details.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `analyze_all_details.py` | `D:/Soft/Codex Backup/scripts/analyze_all_details.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `analyze_all_details.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/analyze_all_details.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `analyze_csv.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/analyze_csv.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `analyze_flamegraph_json.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/build-ios-apps/skills/ios-ettrace-performance/scripts/analyze_flamegraph_json.py` | !/usr/bin/env python3 Summarize ETTrace processed flamegraph JSON for performance triage. | 0 |
| **Базовый** | `analyze_forms.py` | `projects/tilda_migration/analyze_forms.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `analyze_forms.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/analyze_forms.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `analyze_sprint.py` | `scripts/analyze_sprint.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `analyze_sprint.py` | `D:/Soft/Codex Backup/scripts/analyze_sprint.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `analyze_sprint.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/analyze_sprint.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `apply_final_fixes.py` | `projects/tilda_migration/apply_final_fixes.py` | FTP Config | 0 |
| **Базовый** | `apply_final_fixes.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/apply_final_fixes.py` | FTP Config | 1 |
| **Базовый** | `apply_template_styles.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/apply_template_styles.py` | !/usr/bin/env python3 Apply a template/style pack (DOTX or DOCX) onto a target DOCX. | 0 |
| **Базовый** | `audit_archived_transcripts.py` | `scripts/audit_archived_transcripts.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `audit_archived_transcripts.py` | `D:/Soft/Codex Backup/scripts/audit_archived_transcripts.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `audit_archived_transcripts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/audit_archived_transcripts.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `auth_manager.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/mixpanel-headless/skills/mixpanelyst/scripts/auth_manager.py` | !/usr/bin/env python3 Plugin auth manager — JSON wrapper around the mixpanel_headless auth namespaces. | 0 |
| **Базовый** | `author_grasp_line.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-conform-profile/references/FET_005_SIMULATE_GRASP_PHYSICS/scripts/author_grasp_line.py` | SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. SPDX-License-Identifier: Apache-2.0 | 0 |
| **Базовый** | `b1c2d3e4f5a6_add_knowledge_base.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/alembic/versions/b1c2d3e4f5a6_add_knowledge_base.py` | add knowledge_base | 8 |
| **Базовый** | `backup-sql.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/backup-sql.sh` | 1C Backup script with failure notification and safe retention | 1 |
| **Базовый** | `backup-sql.sh` | `D:/Soft/Codex Backup/scripts/vps/backup-sql.sh` | 1C Backup script with failure notification and safe retention | 0 |
| **Базовый** | `biobankjapan_phewas.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/biobankjapan-phewas-skill/scripts/biobankjapan_phewas.py` | !/usr/bin/env python3 biobankjapan-phewas | 0 |
| **Базовый** | `budget_enforcer.py` | `scripts/budget_enforcer.py` | ates per 1M tokens | 0 |
| **Базовый** | `budget_enforcer.py` | `D:/Soft/Codex Backup/scripts/budget_enforcer.py` | ates per 1M tokens | 0 |
| **Базовый** | `budget_enforcer.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scripts/budget_enforcer.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `budget_enforcer.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/budget_enforcer.py` | ates per 1M tokens | 0 |
| **Базовый** | `build_private_bundle.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/bundled-marketplaces/openai-bundled/plugins/latex/scripts/build_private_bundle.sh` | !/usr/bin/env bash | 0 |
| **Базовый** | `build_sprite_edit_canvas.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/game-studio/scripts/build_sprite_edit_canvas.py` | !/usr/bin/env python3 Build a transparent edit canvas around a shipped seed sprite frame. | 0 |
| **Базовый** | `c2d3e4f5a6b7_add_content_hash.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/alembic/versions/c2d3e4f5a6b7_add_content_hash.py` | add content_hash to knowledge_base | 8 |
| **Базовый** | `captions_and_crossrefs.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/captions_and_crossrefs.py` | !/usr/bin/env python3 Insert simple captions (Figure/Table) and optional cross-references. | 0 |
| **Базовый** | `capture_sim_memgraph.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/build-ios-apps/skills/ios-memgraph-leaks/scripts/capture_sim_memgraph.sh` | !/usr/bin/env bash | 0 |
| **Базовый** | `chart_builders.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/morningstar/skills/fund-summarizer/scripts/chart_builders.py` | Chart color constants matching template CSS variables. | 0 |
| **Базовый** | `chunk_kb.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/chunk_kb.py` | Add root project path to sys.path | 8 |
| **Базовый** | `cleanup_codex_root.py` | `scripts/cleanup_codex_root.py` | 1. Move old .bak files | 0 |
| **Базовый** | `clear_tmp.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/clear_tmp.sh` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `clear_tmp.sh` | `D:/Soft/Codex Backup/scripts/vps/clear_tmp.sh` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `collect_ios_dsyms.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/build-ios-apps/skills/ios-ettrace-performance/scripts/collect_ios_dsyms.sh` | !/usr/bin/env bash | 0 |
| **Базовый** | `comments_add.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/comments_add.py` | !/usr/bin/env python3 Add one or more Word comments to paragraphs matched by substring. | 0 |
| **Базовый** | `comments_strip.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/comments_strip.py` | !/usr/bin/env python3 Remove all comments from a DOCX (ranges + parts). | 0 |
| **Базовый** | `compare_codex_dirs.py` | `scripts/compare_codex_dirs.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_codex_dirs.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/compare_codex_dirs.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_projects.ps1` | `scratch/compare_projects.ps1` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_projects.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scratch/compare_projects.ps1` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_snapshots.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/local_inventory/inventory/compare_snapshots.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `compare_snapshots.ps1` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/compare_snapshots.ps1` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `compare_vtb.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/GoW Project/compare_vtb.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `compare_vtb.py` | `D:/Soft/Codex Backup/projects/GoW Project/compare_vtb.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compile_latex.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/bundled-marketplaces/openai-bundled/plugins/latex/scripts/compile_latex.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `config.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/app/core/config.py` | Database | 6 |
| **Базовый** | `config.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/core/config.py` | Database | 1 |
| **Базовый** | `content_agent_client.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/content-agents/scripts/content_agent_client.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `content_agent_material_cleanup.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/content-agents/scripts/content_agent_material_cleanup.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `content_controls.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/content_controls.py` | !/usr/bin/env python3 Content controls (SDTs) helper. | 0 |
| **Базовый** | `convert_to_gguf.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/llm-trainer/scripts/convert_to_gguf.py` | !/usr/bin/env python3 /// script | 0 |
| **Базовый** | `cooldown_guard.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/app/services/cooldown_guard.py` | Public email providers where domain-level cooldown must NOT be applied to all clients | 0 |
| **Базовый** | `cot-self-instruct.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/jobs/scripts/cot-self-instruct.py` | /// script quires-python = ">=3.10" | 0 |
| **Базовый** | `create_basic_plugin.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/plugin-creator/scripts/create_basic_plugin.py` | !/usr/bin/env python3 Scaffold a plugin directory and optionally update marketplace.json. | 0 |
| **Базовый** | `create_basic_plugin.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/.agents/skills/plugin-creator/scripts/create_basic_plugin.py` | !/usr/bin/env python3 Scaffold a plugin directory and optionally update marketplace.json. | 0 |
| **Базовый** | `create_reference_slide.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/presentations/26.601.10930/skills/presentations/scripts/create_reference_slide.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `create_reference_slides.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/presentations/26.601.10930/skills/presentations/scripts/create_reference_slides.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `create_theme.py` | `projects/tilda_migration/create_theme.py` | Load resource mapping | 0 |
| **Базовый** | `create_theme.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/create_theme.py` | Load resource mapping | 1 |
| **Базовый** | `d3e4f5a6b7c8_add_emails_metadata_to_clients_intel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/alembic/versions/d3e4f5a6b7c8_add_emails_metadata_to_clients_intel.py` | add_emails_metadata_to_clients_intel | 8 |
| **Базовый** | `database.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/db/database.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `dataset_inspector.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/vision-trainer/scripts/dataset_inspector.py` | !/usr/bin/env python3 /// script | 0 |
| **Базовый** | `dataset_inspector.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/llm-trainer/scripts/dataset_inspector.py` | !/usr/bin/env python3 /// script | 0 |
| **Базовый** | `debug_cursors.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/debug_cursors.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `deep_analysis.py` | `scripts/deep_analysis.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `deep_analysis.py` | `D:/Soft/Codex Backup/scripts/deep_analysis.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `deep_analysis.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/deep_analysis.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `deep_sprint_reviewer.py` | `scripts/deep_sprint_reviewer.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `deep_sprint_reviewer.py` | `D:/Soft/Codex Backup/scripts/deep_sprint_reviewer.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `deep_sprint_reviewer.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/deep_sprint_reviewer.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `deploy_files.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scratch/deploy_files.ps1` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `detect_tectonic.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/bundled-marketplaces/openai-bundled/plugins/latex/scripts/detect_tectonic.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `detect_texlive.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/bundled-marketplaces/openai-bundled/plugins/latex/scripts/detect_texlive.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `diff_personal_shared.py` | `scripts/diff_personal_shared.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `diff_personal_shared.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/diff_personal_shared.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `diff_subdirs.py` | `scripts/diff_subdirs.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `diff_subdirs.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/diff_subdirs.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `docx_table_to_csv.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/docx_table_to_csv.py` | !/usr/bin/env python3 Export a DOCX table to CSV. | 0 |
| **Базовый** | `download_project_specific_assets.py` | `projects/tilda_migration/download_project_specific_assets.py` | FTP Config | 0 |
| **Базовый** | `download_project_specific_assets.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/download_project_specific_assets.py` | FTP Config | 1 |
| **Базовый** | `download_resources.py` | `projects/tilda_migration/download_resources.py` | Paths | 0 |
| **Базовый** | `download_resources.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/download_resources.py` | Paths | 1 |
| **Базовый** | `download_vps_backup.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/download_vps_backup.ps1` | Конфигурация | 2 |
| **Базовый** | `dump_chat_md.py` | `scripts/dump_chat_md.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `dump_chat_md.py` | `D:/Soft/Codex Backup/scripts/dump_chat_md.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `dump_chat_md.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/dump_chat_md.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `dump_match_results.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/dump_match_results.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `env.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/alembic/env.py` | this is the Alembic Config object, which provides access to the values within the .ini file in use. | 8 |
| **Базовый** | `estimate_cost.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/vision-trainer/scripts/estimate_cost.py` | !/usr/bin/env python3 /// script | 0 |
| **Базовый** | `estimate_cost.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/llm-trainer/scripts/estimate_cost.py` | !/usr/bin/env python3 /// script | 0 |
| **Базовый** | `execute_codex_unification.py` | `scripts/execute_codex_unification.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `execute_codex_unification.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/execute_codex_unification.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `execute_compression.py` | `scripts/execute_compression.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `execute_compression.py` | `D:/Soft/Codex Backup/scripts/execute_compression.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `execute_compression.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/execute_compression.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `explore_htdocs.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/explore_htdocs.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `explore_www.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/explore_www.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `export_data.bat` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/export_data.bat` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `export_data.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/export_data.ps1` | nforce UTF-8 output | 8 |
| **Базовый** | `export_installed_programs.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/local_inventory/inventory/export_installed_programs.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `export_installed_programs.ps1` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/export_installed_programs.ps1` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `export_sprint_chat.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/export_sprint_chat.py` | !/usr/bin/env python3 | 1 |
| **Базовый** | `export_sprint_chat.py` | `D:/Soft/Codex Backup/scripts/export_sprint_chat.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `fetch_comments.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/github/skills/gh-address-comments/scripts/fetch_comments.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `fetch_raw_emails.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/fetch_raw_emails.py` | 1. Start SSH tunnel locally | 2 |
| **Базовый** | `fields_materialize.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/fields_materialize.py` | !/usr/bin/env python3 Materialize (freeze) common Word fields into plain text. | 0 |
| **Базовый** | `fields_report.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/fields_report.py` | !/usr/bin/env python3 Report Word fields present in a DOCX. | 0 |
| **Базовый** | `find_biohim.py` | `projects/tilda_migration/find_biohim.py` | Search for "БИОХИМ" or "biohim" | 0 |
| **Базовый** | `find_biohim.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/find_biohim.py` | Search for "БИОХИМ" or "biohim" | 1 |
| **Базовый** | `find_endpoints_in_dashboard.py` | `projects/tilda_migration/find_endpoints_in_dashboard.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_endpoints_in_dashboard.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/find_endpoints_in_dashboard.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `find_footer_elements.py` | `projects/tilda_migration/find_footer_elements.py` | Let's look at elements inside the footer or bottom of the page We can find all elements with classes containing 'rec' at the end | 0 |
| **Базовый** | `find_footer_elements.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/find_footer_elements.py` | Let's look at elements inside the footer or bottom of the page We can find all elements with classes containing 'rec' at the end | 1 |
| **Базовый** | `find_live_footer_imgs.py` | `projects/tilda_migration/find_live_footer_imgs.py` | Find all images in the document and print the last few | 0 |
| **Базовый** | `find_live_footer_imgs.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/find_live_footer_imgs.py` | Find all images in the document and print the last few | 1 |
| **Базовый** | `find_live_footer_logo.py` | `projects/tilda_migration/find_live_footer_logo.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_live_footer_logo.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/find_live_footer_logo.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `find_locking_processes.py` | `scripts/find_locking_processes.py` | start Manager API to find process locking a file | 0 |
| **Базовый** | `find_more_paths.py` | `projects/tilda_migration/find_more_paths.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_more_paths.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/find_more_paths.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `find_nikolaevna.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scratch/find_nikolaevna.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_path_occurrences.py` | `scripts/find_path_occurrences.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_path_occurrences.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/find_path_occurrences.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_petroship_mail.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scratch/find_petroship_mail.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `finepdfs-stats.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/jobs/scripts/finepdfs-stats.py` | /// script quires-python = ">=3.12" | 0 |
| **Базовый** | `finngen_phewas.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/finngen-phewas-skill/scripts/finngen_phewas.py` | !/usr/bin/env python3 finngen-phewas | 0 |
| **Базовый** | `fix_icons_and_footer.py` | `projects/tilda_migration/fix_icons_and_footer.py` | FTP Config | 0 |
| **Базовый** | `fix_icons_and_footer.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/fix_icons_and_footer.py` | FTP Config | 1 |
| **Базовый** | `flatten_ref_fields.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/flatten_ref_fields.py` | !/usr/bin/env python3 Flatten REF/PAGEREF fields to literal text runs. | 0 |
| **Базовый** | `footnotes_report.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/footnotes_report.py` | !/usr/bin/env python3 Report footnotes/endnotes usage in a DOCX. | 0 |
| **Базовый** | `force_delete_old_dirs.ps1` | `scripts/force_delete_old_dirs.ps1` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `genebass_gene_burden.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/genebass-gene-burden-skill/scripts/genebass_gene_burden.py` | !/usr/bin/env python3 genebass-gene-burden | 0 |
| **Базовый** | `generate-responses.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/jobs/scripts/generate-responses.py` | /// script quires-python = ">=3.10" | 0 |
| **Базовый** | `generate_all_commands_reference.py` | `scripts/generate_all_commands_reference.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_all_commands_reference.py` | `D:/Soft/Codex Backup/scripts/generate_all_commands_reference.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_all_commands_reference.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/generate_all_commands_reference.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_desktop_guides.py` | `scripts/generate_desktop_guides.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_desktop_guides.py` | `D:/Soft/Codex Backup/scripts/generate_desktop_guides.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_desktop_guides.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/generate_desktop_guides.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_openai_yaml.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/skill-creator/scripts/generate_openai_yaml.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_rank_input.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/codex-security/scripts/generate_rank_input.py` | !/usr/bin/env python3 Generate and post-process Codex Security scan worklists. | 0 |
| **Базовый** | `generate_readable_review.py` | `scripts/generate_readable_review.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_readable_review.py` | `D:/Soft/Codex Backup/scripts/generate_readable_review.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_readable_review.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/generate_readable_review.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_rod_letter.py` | `scripts/generate_rod_letter.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_rod_letter.py` | `D:/Soft/Codex Backup/scripts/generate_rod_letter.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_rod_letter.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/generate_rod_letter.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_three_letters.py` | `D:/Soft/Codex Backup/scripts/generate_three_letters.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_three_letters.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/generate_three_letters.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `github_utils.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/skill-installer/scripts/github_utils.py` | !/usr/bin/env python3 Shared GitHub helpers for skill install scripts. | 0 |
| **Базовый** | `google_docs_title_sanitize.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/google_docs_title_sanitize.py` | !/usr/bin/env python3 Remove Word Title-style rule/border residue from Google Docs-targeted DOCX files. | 0 |
| **Базовый** | `gtex_eqtl.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/gtex-eqtl-skill/scripts/gtex_eqtl.py` | !/usr/bin/env python3 gtex-eqtl | 0 |
| **Базовый** | `heading_audit.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/heading_audit.py` | !/usr/bin/env python3 Audit heading hierarchy and numbering in a DOCX. | 0 |
| **Базовый** | `help.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/mixpanel-headless/skills/mixpanelyst/scripts/help.py` | !/usr/bin/env python3 Programmatic API documentation lookup for mixpanel_headless. | 0 |
| **Базовый** | `hr_guard.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/app/services/hr_guard.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `image_classification_training.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/vision-trainer/scripts/image_classification_training.py` | /// script dependencies = [ | 0 |
| **Базовый** | `image_gen.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/imagegen/scripts/image_gen.py` | !/usr/bin/env python3 Fallback CLI for explicit image generation or editing with GPT Image models. | 0 |
| **Базовый** | `images_audit.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/images_audit.py` | !/usr/bin/env python3 Audit images in a DOCX (inline vs floating, size, relationship targets). | 0 |
| **Базовый** | `imap_service.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/services/imap_service.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `init_skill.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/skill-creator/scripts/init_skill.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `insert_ref_fields.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/insert_ref_fields.py` | !/usr/bin/env python3 Insert Word cross-references (REF fields) by replacing lightweight markers. | 0 |
| **Базовый** | `insert_toc.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/insert_toc.py` | !/usr/bin/env python3 Insert a Table of Contents (TOC) field at a placeholder paragraph. | 0 |
| **Базовый** | `inspect_codex_folders.py` | `scripts/inspect_codex_folders.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_codex_folders.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/inspect_codex_folders.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_codex_home.py` | `scripts/inspect_codex_home.py` | Let's inspect processes whose CurrentWorkingDirectory or Executable is in C:\Codex | 0 |
| **Базовый** | `inspect_codex_home.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/inspect_codex_home.py` | Let's inspect processes whose CurrentWorkingDirectory or Executable is in C:\codex_home | 0 |
| **Базовый** | `inspect_days_6_7_cost.py` | `scripts/inspect_days_6_7_cost.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `inspect_days_6_7_cost.py` | `D:/Soft/Codex Backup/scripts/inspect_days_6_7_cost.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `inspect_days_6_7_cost.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/inspect_days_6_7_cost.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `inspect_form_html.py` | `projects/tilda_migration/inspect_form_html.py` | print first 3000 chars of block HTML | 0 |
| **Базовый** | `inspect_form_html.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/inspect_form_html.py` | print first 3000 chars of block HTML | 1 |
| **Базовый** | `inspect_forms_detail.py` | `projects/tilda_migration/inspect_forms_detail.py` | Let's find all divs with class 't-form' | 0 |
| **Базовый** | `inspect_forms_detail.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/inspect_forms_detail.py` | Let's find all divs with class 't-form' | 1 |
| **Базовый** | `inspect_images.py` | `projects/tilda_migration/inspect_images.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_images.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/inspect_images.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `inspect_lead_17766.py` | `scratch/inspect_lead_17766.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_reports_detail.py` | `scripts/inspect_reports_detail.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `inspect_reports_detail.py` | `D:/Soft/Codex Backup/scripts/inspect_reports_detail.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `inspect_reports_detail.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/inspect_reports_detail.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `install-skill-from-github.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/skill-installer/scripts/install-skill-from-github.py` | !/usr/bin/env python3 Install a skill from a GitHub repo path into $CODEX_HOME/skills. | 0 |
| **Базовый** | `install_texlive.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/bundled-marketplaces/openai-bundled/plugins/latex/scripts/install_texlive.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `internal_nav.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/internal_nav.py` | !/usr/bin/env python3 Add internal navigation aids to a DOCX (bookmarks + internal hyperlinks). | 0 |
| **Базовый** | `inventory.py` | `config/infra_management/scripts/inventory.py` | Configuration | 0 |
| **Базовый** | `inventory.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/config/infra_management/scripts/inventory.py` | Configuration | 1 |
| **Базовый** | `inventory_common.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/local_inventory/inventory/inventory_common.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `inventory_common.ps1` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/inventory_common.ps1` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `inventory_config.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/local_inventory/inventory/inventory_config.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `inventory_config.ps1` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/inventory_config.ps1` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `kb_chunk_export.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/n8n_email_ai/rag_tools/kb_chunk_export.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `kb_chunk_export.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/50_rag_tools/kb_chunk_export.ps1` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `kit_app_template_cad.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/references/usd-convert-cad/scripts/kit_app_template_cad.py` | SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. SPDX-License-Identifier: Apache-2.0 | 0 |
| **Базовый** | `latex_doctor.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/bundled-marketplaces/openai-bundled/plugins/latex/scripts/latex_doctor.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `list-skills.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/skill-installer/scripts/list-skills.py` | !/usr/bin/env python3 List skills from a GitHub repo path. | 0 |
| **Базовый** | `list_models.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scripts/list_models.py` | Автоматизация рабочего процесса. | 6 |
| **Базовый** | `list_models.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/list_models.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `llm_service.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_v6_backup/archive/backup_20260805_v4plus/llm_service.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `llm_service.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_v6_backup/app/services/llm_service.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `llm_service.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_migration_backup_20260809/app/services/llm_service.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `llm_service.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/services/llm_service.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `llm_service.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_backup/app/services/llm_service.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `llm_service.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/app/services/llm_service.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `llm_service_production.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/services/llm_service_production.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `log_service.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/services/log_service.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `main.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/main.py` | Автоматизация рабочего процесса. | 7 |
| **Базовый** | `main.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/app/main.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `make_snapshot.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/local_inventory/inventory/make_snapshot.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `make_snapshot.ps1` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/make_snapshot.ps1` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `map_locus_to_gene.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/locus-to-gene-mapper-skill/scripts/map_locus_to_gene.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `merge_and_translate_repare.py` | `scripts/merge_and_translate_repare.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `merge_and_translate_repare.py` | `D:/Soft/Codex Backup/scripts/merge_and_translate_repare.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `merge_and_translate_repare.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/merge_and_translate_repare.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `merge_docx_append.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/merge_docx_append.py` | !/usr/bin/env python3 Append the body of one DOCX to another by splicing OOXML. | 0 |
| **Базовый** | `mirror_vps_scripts.py` | `scripts/mirror_vps_scripts.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `mirror_vps_scripts.py` | `D:/Soft/Codex Backup/scripts/mirror_vps_scripts.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `mirror_vps_scripts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/mirror_vps_scripts.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `models.py` | `ARCHIVE/codex_shared_archive/n8n_email_ai_v6_backup/app/db/models.py` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `models.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/db/models.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `models.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/app/db/models.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `monitor_disk.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/monitor_disk.sh` | ???????????? ?????????????????????? ???????????? ?? ???????????????????????? ?? ??????????????24 | 2 |
| **Базовый** | `monitor_disk.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scratch/monitor_disk.sh` | Скрипт мониторинга дисков с уведомлением в Битрикс24 | 0 |
| **Базовый** | `moz_internal_linking_report.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/GoW Project/moz_internal_linking_report.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `moz_internal_linking_report.py` | `D:/Soft/Codex Backup/projects/GoW Project/moz_internal_linking_report.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `n8n-sqlite-auto-vacuum.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/n8n-sqlite-auto-vacuum.sh` | Проверка размера баз n8n и сжатие | 1 |
| **Базовый** | `n8n-sqlite-auto-vacuum.sh` | `D:/Soft/Codex Backup/scripts/vps/n8n-sqlite-auto-vacuum.sh` | Проверка размера баз n8n и сжатие | 0 |
| **Базовый** | `ncbi_blast.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/ncbi-blast-skill/scripts/ncbi_blast.py` | !/usr/bin/env python3 ncbi_blast | 0 |
| **Базовый** | `ngs_planner_utils.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/ngs_planner_utils.py` | !/usr/bin/env python3 Shared table and command-plan helpers for NGS runner build-outs. | 0 |
| **Базовый** | `ngs_resource_gate.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/ngs_resource_gate.py` | !/usr/bin/env python3 Shared reference/database readiness gates for NGS run envelopes. | 0 |
| **Базовый** | `ngs_run_utils.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/ngs_run_utils.py` | !/usr/bin/env python3 Shared helpers for plugin-owned NGS execution runners. | 0 |
| **Базовый** | `ngs_visualization_utils.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/ngs_visualization_utils.py` | !/usr/bin/env python3 Small visualization helpers for plugin-owned NGS runners. | 0 |
| **Базовый** | `normalize_sprite_strip.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/game-studio/scripts/normalize_sprite_strip.py` | !/usr/bin/env python3 Normalize a raw animation strip into fixed-size transparent frames. | 0 |
| **Базовый** | `object_detection_training.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/vision-trainer/scripts/object_detection_training.py` | /// script dependencies = [ | 0 |
| **Базовый** | `openai_generate_image.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/presentations/26.601.10930/skills/presentations/scripts/openai_generate_image.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `package_chatgpt_skills.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/daloopa/scripts/package_chatgpt_skills.py` | !/usr/bin/env python3 Package Daloopa skills as one ChatGPT-uploadable zip per skill. | 0 |
| **Базовый** | `paper_manager.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/paper-publisher/scripts/paper_manager.py` | !/usr/bin/env -S uv run /// script | 0 |
| **Базовый** | `parse_days_detail.py` | `scripts/parse_days_detail.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `parse_days_detail.py` | `D:/Soft/Codex Backup/scripts/parse_days_detail.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `parse_days_detail.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/parse_days_detail.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `parse_js.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/parse_js.py` | Let's search for URLs or api endpoints | 2 |
| **Базовый** | `preview.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/wix/skills/wix-headless/scripts/preview.sh` | !/usr/bin/env bash Build the project and deploy a rotating preview URL. | 0 |
| **Базовый** | `print_hkcu_env.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/print_hkcu_env.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `privacy_scrub.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/privacy_scrub.py` | !/usr/bin/env python3 Remove common personal metadata from a DOCX. | 0 |
| **Базовый** | `quick_validate.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/skill-creator/scripts/quick_validate.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `read_marketplace_name.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/plugin-creator/scripts/read_marketplace_name.py` | !/usr/bin/env python3 Print the top-level marketplace name from any marketplace.json file. | 0 |
| **Базовый** | `read_salman_fast.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/read_salman_fast.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `read_salman_inbox.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/read_salman_inbox.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `rebuild_try_to_repare_en.py` | `scripts/rebuild_try_to_repare_en.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `rebuild_try_to_repare_en.py` | `D:/Soft/Codex Backup/scripts/rebuild_try_to_repare_en.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `rebuild_try_to_repare_en.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/rebuild_try_to_repare_en.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `release.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/wix/skills/wix-headless/scripts/release.sh` | !/usr/bin/env bash Build the project and release to production. Unlike preview.sh, this populates | 0 |
| **Базовый** | `remote_n8n_fix.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/server_ops/snapshots/remote_n8n_fix.sh` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `remote_n8n_fix2.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/server_ops/snapshots/remote_n8n_fix2.sh` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `remove_chroma_key.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/imagegen/scripts/remove_chroma_key.py` | !/usr/bin/env python3 Remove a solid chroma-key background from an image. | 0 |
| **Базовый** | `rename_assets_and_title.py` | `projects/tilda_migration/rename_assets_and_title.py` | FTP Config | 0 |
| **Базовый** | `rename_assets_and_title.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/rename_assets_and_title.py` | FTP Config | 1 |
| **Базовый** | `render.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/morningstar/skills/fund-summarizer/scripts/render.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `render_day_brief.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-curated/google-calendar/c6ea566d/skills/google-calendar-daily-brief/scripts/render_day_brief.py` | !/usr/bin/env python3 Render a one-day Google Calendar brief as polished Markdown. | 1 |
| **Базовый** | `render_docx.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/render_docx.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `render_preview.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-usd-performance-tuning/references/report-templates/render_preview.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `render_report_html.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/codex-security/scripts/render_report_html.py` | !/usr/bin/env python3 Render a Codex Security markdown report as a self-contained HTML file. | 0 |
| **Базовый** | `reset_sintez_db.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/reset_sintez_db.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `restore_postgre.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/restore_postgre.sh` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `restore_postgre.sh` | `D:/Soft/Codex Backup/scripts/vps/restore_postgre.sh` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/validate-usd-minimum/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-validate/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-conform-profile/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-conform-profile/references/FET_004_SIMULATE_MULTI_BODY_PHYSICS/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-conform-profile/references/FET_001_MINIMAL/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-conform-profile/references/FET_000_CORE/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/ovrtx-render-service/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/omni-asset-validate-physics/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/omni-asset-validate-geometry/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/omni-asset-validate/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/nv-core-package-sample-validation/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 1 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/identify-asset-context/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/references/usd-convert-gsplat/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/references/usd-convert-cad/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/references/urdf-usd-converter/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/references/mujoco-usd-converter/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/content-agents/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/content-agents/references/texture-agent-client/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 2 |
| **Базовый** | `run.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/assemble-package-source/scripts/run.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `run_amplicon_microbiome.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_amplicon_microbiome.py` | !/usr/bin/env python3 Run or plan amplicon ASV, taxonomy, diversity, and visualization backends. | 0 |
| **Базовый** | `run_bcl_to_fastq.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_bcl_to_fastq.py` | !/usr/bin/env python3 Validate Illumina BCL run folders and run local BCL-to-FASTQ conversion when available. | 0 |
| **Базовый** | `run_bulk_rnaseq_counts_qc.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_bulk_rnaseq_counts_qc.py` | !/usr/bin/env python3 Run local bulk RNA-seq counts/QC with Salmon, FastQC, MultiQC, and matrices. | 0 |
| **Базовый** | `run_current_compress.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/run_current_compress.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `run_current_compress.py` | `D:/Soft/Codex Backup/scripts/run_current_compress.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `run_dna_germline_variants.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_dna_germline_variants.py` | !/usr/bin/env python3 Run germline DNA variant calling with optional BQSR, gVCF, and joint genotyping. | 0 |
| **Базовый** | `run_dna_somatic_variants.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_dna_somatic_variants.py` | !/usr/bin/env python3 Run or plan local somatic SNV/indel calling with GATK Mutect2. | 0 |
| **Базовый** | `run_dna_umi_panel_variants.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_dna_umi_panel_variants.py` | !/usr/bin/env python3 Run or plan UMI-aware targeted panel variant calling from consensus or raw BAMs. | 0 |
| **Базовый** | `run_dna_variant_calling.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_dna_variant_calling.py` | !/usr/bin/env python3 Run BAM-to-VCF DNA variant calling with samtools and bcftools. | 0 |
| **Базовый** | `run_fastq_assay_package.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_fastq_assay_package.py` | !/usr/bin/env python3 Run FASTQ-based assay packages for epigenomics, amplicon, and metagenomics lanes. | 0 |
| **Базовый** | `run_nfcore_pipeline.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/run_nfcore_pipeline.py` | !/usr/bin/env python3 Generate and optionally execute a standardized nf-core pipeline run envelope. | 0 |
| **Базовый** | `run_rag_vectorize.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/run_rag_vectorize.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `run_server_backup.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/run_server_backup.sh` | ???????????? ?????????????? ???????????? ?? ?????????????????????????????? ???????????????????????? SQLite | 2 |
| **Базовый** | `run_server_backup_new.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scratch/run_server_backup_new.sh` | Скрипт полного бэкапа и автоматического обслуживания SQLite | 0 |
| **Базовый** | `run_summaries_batch.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/run_summaries_batch.py` | Get up to limit unique from_emails that have unprocessed matched emails | 8 |
| **Базовый** | `sam_segmentation_training.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/vision-trainer/scripts/sam_segmentation_training.py` | /// script dependencies = [ | 0 |
| **Базовый** | `scaffold.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/wix/skills/wix-headless/scripts/scaffold.sh` | !/usr/bin/env bash Scaffold a new Wix Managed Headless project using the CLI's preset blank template. | 0 |
| **Базовый** | `schedule_reboot_cleanup.py` | `scripts/schedule_reboot_cleanup.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `schemas.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/api/schemas.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `scratch_b24_fetch.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/scratch_b24_fetch.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `scratch_b24_fetch.py` | `D:/Soft/Codex Backup/projects/HR/scratch_b24_fetch.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `scratch_print_all.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/scratch_print_all.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `script_utils.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/shared/script_utils.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `search_chat_history.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/search_chat_history.py` | !/usr/bin/env python3 | 1 |
| **Базовый** | `search_chat_history.py` | `D:/Soft/Codex Backup/scripts/search_chat_history.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `search_imap_accurate.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scratch/search_imap_accurate.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_imap_all_folders.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/search_imap_all_folders.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `search_system_commands.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/search_system_commands.py` | Автоматизация рабочего процесса. | 8 |
| **Базовый** | `secret_leak_scanner.py` | `scripts/secret_leak_scanner.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `secret_leak_scanner.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scripts/secret_leak_scanner.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `section_audit.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/section_audit.py` | !/usr/bin/env python3 Audit section/page layout settings in a DOCX. | 0 |
| **Базовый** | `seed-utilities.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/wix/skills/wix-headless/scripts/seed-utilities.sh` | !/usr/bin/env bash Frontend-track project prep: copy the skill's shared utilities into the | 0 |
| **Базовый** | `sentry_api.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/sentry/skills/sentry/scripts/sentry_api.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `set_protection.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/set_protection.py` | !/usr/bin/env python3 Set or clear Word document protection flags (restrict editing). | 0 |
| **Базовый** | `setup.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/mixpanel-headless/skills/setup/scripts/setup.sh` | !/usr/bin/env bash Install mixpanel_headless and pandas for CodeMode analytics | 0 |
| **Базовый** | `simready_package.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/shared/simready_package.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `stage_prep.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/ovrtx-render-service/scripts/stage_prep.py` | SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. SPDX-License-Identifier: Apache-2.0 | 0 |
| **Базовый** | `start-server.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/superpowers/skills/brainstorming/scripts/start-server.sh` | !/usr/bin/env bash Start the brainstorm server and output connection info | 0 |
| **Базовый** | `stop-server.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/superpowers/skills/brainstorming/scripts/stop-server.sh` | !/usr/bin/env bash Stop the brainstorm server and clean up | 0 |
| **Базовый** | `style_lint.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/style_lint.py` | !/usr/bin/env python3 Style lint for DOCX (python-docx). | 0 |
| **Базовый** | `style_normalize.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/style_normalize.py` | !/usr/bin/env python3 Normalize styles / reduce formatting drift. | 0 |
| **Базовый** | `summarize_memgraph_leaks.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/build-ios-apps/skills/ios-memgraph-leaks/scripts/summarize_memgraph_leaks.py` | !/usr/bin/env python3 Summarize leaks output from an Apple .memgraph file. | 0 |
| **Базовый** | `tilda_fetch_all_projects_pages.py` | `projects/tilda_migration/tilda_fetch_all_projects_pages.py` | 1. Get projects list | 0 |
| **Базовый** | `tilda_fetch_all_projects_pages.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_fetch_all_projects_pages.py` | 1. Get projects list | 1 |
| **Базовый** | `tilda_fetch_pages_json.py` | `projects/tilda_migration/tilda_fetch_pages_json.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_pages_json.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_fetch_pages_json.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `tilda_fetch_project_details.py` | `projects/tilda_migration/tilda_fetch_project_details.py` | Try POST | 0 |
| **Базовый** | `tilda_fetch_project_details.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_fetch_project_details.py` | Try POST | 1 |
| **Базовый** | `tilda_fetch_project_pages.py` | `projects/tilda_migration/tilda_fetch_project_pages.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_project_pages.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_fetch_project_pages.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `tilda_fetch_projects_json.py` | `projects/tilda_migration/tilda_fetch_projects_json.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_projects_json.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_fetch_projects_json.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `tilda_get_preview.py` | `projects/tilda_migration/tilda_get_preview.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_get_preview.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_get_preview.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `tilda_guess_endpoints.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_guess_endpoints.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `tilda_list_projects.py` | `projects/tilda_migration/tilda_list_projects.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_list_projects.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_list_projects.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `tilda_session.py` | `projects/tilda_migration/tilda_session.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_session.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_session.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `tpmi_phewas.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/tpmi-phewas-skill/scripts/tpmi_phewas.py` | !/usr/bin/env python3 tpmi-phewas | 0 |
| **Базовый** | `train_dpo_example.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/llm-trainer/scripts/train_dpo_example.py` | !/usr/bin/env python3 /// script | 0 |
| **Базовый** | `train_grpo_example.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/llm-trainer/scripts/train_grpo_example.py` | !/usr/bin/env python3 /// script | 0 |
| **Базовый** | `train_sft_example.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/llm-trainer/scripts/train_sft_example.py` | !/usr/bin/env python3 /// script | 0 |
| **Базовый** | `translate_datasheet.py` | `scripts/translate_datasheet.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `translate_datasheet.py` | `D:/Soft/Codex Backup/scripts/translate_datasheet.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `translate_datasheet.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/translate_datasheet.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `try_submit_login.py` | `projects/tilda_migration/try_submit_login.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `try_submit_login.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/try_submit_login.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `turntable.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/ovrtx-render-service/scripts/turntable.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Базовый** | `ukb_topmed_phewas.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/ukb-topmed-phewas-skill/scripts/ukb_topmed_phewas.py` | !/usr/bin/env python3 ukb-topmed-phewas | 0 |
| **Базовый** | `unsloth_sft_example.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/llm-trainer/scripts/unsloth_sft_example.py` | /// script quires-python = ">=3.10" | 0 |
| **Базовый** | `update_form_js.py` | `projects/tilda_migration/update_form_js.py` | FTP Config | 0 |
| **Базовый** | `update_form_js.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/update_form_js.py` | FTP Config | 1 |
| **Базовый** | `update_plugin_cachebuster.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py` | !/usr/bin/env python3 Rewrite a local plugin version to a single Codex cachebuster suffix. | 0 |
| **Базовый** | `validate-render-yaml.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/render/scripts/validate-render-yaml.sh` | !/usr/bin/env bash | 0 |
| **Базовый** | `validate_report_format.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/codex-security/scripts/validate_report_format.py` | !/usr/bin/env python3 Validate the shared Codex Security final report shape. | 0 |
| **Базовый** | `variant_resolution.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/ukb-topmed-phewas-skill/scripts/variant_resolution.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `vps_server_backup.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/vps_server_backup.sh` | 1. pg_dump of marketing_db from docker container | 1 |
| **Базовый** | `vps_server_backup.sh` | `ARCHIVE/codex_shared_archive/n8n_email_ai_v6_backup/scripts/vps_server_backup.sh` | 1. pg_dump of marketing_db from docker container | 4 |
| **Базовый** | `vps_server_backup.sh` | `D:/Soft/Codex Backup/scripts/vps/vps_server_backup.sh` | 1. pg_dump of marketing_db from docker container | 0 |
| **Базовый** | `watch_and_download_backup.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/watch_and_download_backup.ps1` | Configuration | 2 |
| **Базовый** | `watermark_add.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/watermark_add.py` | !/usr/bin/env python3 Add a simple VML watermark-like object into a document header. | 0 |
| **Базовый** | `watermark_audit_remove.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/watermark_audit_remove.py` | !/usr/bin/env python3 Audit and (heuristically) remove watermark-like background elements. | 0 |
| **Базовый** | `xlsx_to_docx_table.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/xlsx_to_docx_table.py` | !/usr/bin/env python3 Convert an XLSX worksheet to a simple DOCX table. | 0 |
| **Базовый** | `zip_theme.py` | `projects/tilda_migration/zip_theme.py` | Compute relative path in ZIP (should start with qilin-theme/) | 0 |
| **Базовый** | `zip_theme.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/zip_theme.py` | Compute relative path in ZIP (should start with qilin-theme/) | 1 |
| **Базовый** | `zotero.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/zotero/skills/zotero/scripts/zotero.py` | !/usr/bin/env python3 Operate Zotero Desktop's local API and connector server. | 0 |
| **Расширенный** | `AI chats filter.py` | `D:/Soft/Codex Backup/ARCHIVE/Архивы чатов ИИ/AI chats filter.py` | ========================================== ========================================== | 0 |
| **Расширенный** | `accept_tracked_changes.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/accept_tracked_changes.py` | !/usr/bin/env python3 Accept/reject tracked changes in a DOCX by patching OOXML. | 0 |
| **Расширенный** | `add_tracked_replacements.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/add_tracked_replacements.py` | !/usr/bin/env python3 Create tracked-change *replacements* in a DOCX by OOXML patching. | 0 |
| **Расширенный** | `applypatch.bat` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/tmp/arg0/codex-arg0m5FXJK/applypatch.bat` | Автоматизация рабочего процесса. | 1 |
| **Расширенный** | `b24_daily_analytics_sync.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/vps/b24_daily_analytics_sync.py` | !/usr/bin/env python3 | 2 |
| **Расширенный** | `b24_daily_analytics_sync.py` | `D:/Soft/Codex Backup/scripts/vps/b24_daily_analytics_sync.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `build_sprint_evaluation.py` | `scripts/build_sprint_evaluation.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `build_sprint_evaluation.py` | `D:/Soft/Codex Backup/scripts/build_sprint_evaluation.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `build_sprint_evaluation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/build_sprint_evaluation.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `check_broken_links.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/check_broken_links.py` | 1. Stylesheets | 2 |
| **Расширенный** | `check_content.py` | `projects/tilda_migration/check_content.py` | Print page title | 0 |
| **Расширенный** | `check_content.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/check_content.py` | Print page title | 1 |
| **Расширенный** | `check_cursor.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/check_cursor.py` | Автоматизация рабочего процесса. | 8 |
| **Расширенный** | `check_db.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/check_db.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_db_dates.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/check_db_dates.py` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/validate-usd-minimum/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-validate/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-conform-profile/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-conform-profile/references/FET_004_SIMULATE_MULTI_BODY_PHYSICS/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-conform-profile/references/FET_001_MINIMAL/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/simready-conform-profile/references/FET_000_CORE/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/ovrtx-render-service/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/omni-asset-validate-physics/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/omni-asset-validate-geometry/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/omni-asset-validate/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/nv-core-package-sample-validation/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 1 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/identify-asset-context/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/references/usd-convert-gsplat/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/references/usd-convert-cad/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/references/urdf-usd-converter/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/convert-to-usd/references/mujoco-usd-converter/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/content-agents/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/content-agents/references/texture-agent-client/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 2 |
| **Расширенный** | `check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/assemble-package-source/scripts/check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_dns.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/check_dns.py` | Автоматизация рабочего процесса. | 2 |
| **Расширенный** | `check_drafts.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/check_drafts.py` | Автоматизация рабочего процесса. | 8 |
| **Расширенный** | `check_folders.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/check_folders.py` | Автоматизация рабочего процесса. | 8 |
| **Расширенный** | `check_form_tag.py` | `projects/tilda_migration/check_form_tag.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_form_tag.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/check_form_tag.py` | Автоматизация рабочего процесса. | 1 |
| **Расширенный** | `check_interconnect.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/dynamo-interconnect-check/scripts/check_interconnect.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_locked_files.py` | `scripts/check_locked_files.py` | Try opening in r+ mode (or appending 0 bytes) to see if file is locked | 0 |
| **Расширенный** | `check_locked_files.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/check_locked_files.py` | Try opening in r+ mode (or appending 0 bytes) to see if file is locked | 0 |
| **Расширенный** | `check_matched_levels.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/check_matched_levels.py` | Автоматизация рабочего процесса. | 8 |
| **Расширенный** | `check_public_site.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/check_public_site.py` | Автоматизация рабочего процесса. | 2 |
| **Расширенный** | `check_reg_env.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/check_reg_env.py` | Автоматизация рабочего процесса. | 1 |
| **Расширенный** | `check_router_health.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/dynamo-router-starter/scripts/check_router_health.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `check_shared_locks.py` | `scripts/check_shared_locks.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_shared_locks.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/check_shared_locks.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_sintez_emails.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/check_sintez_emails.py` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `check_sintez_owner_emails.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/check_sintez_owner_emails.py` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `check_today.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scratch/check_today.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_uac.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/check_uac.py` | Автоматизация рабочего процесса. | 1 |
| **Расширенный** | `comments_apply_patch.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/comments_apply_patch.py` | !/usr/bin/env python3 Apply lifecycle edits to existing Word comments. | 0 |
| **Расширенный** | `content_agent_check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/content-agents/scripts/content_agent_check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `create_rod_excel.py` | `scripts/create_rod_excel.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `create_rod_excel.py` | `D:/Soft/Codex Backup/scripts/create_rod_excel.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `create_rod_excel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/create_rod_excel.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `docx_ooxml_patch.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/docx_ooxml_patch.py` | !/usr/bin/env python3 DOCX patch helper for features missing in python-docx. | 0 |
| **Расширенный** | `e4f5a6b7c8d9_add_advanced_intel_fields.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/alembic/versions/e4f5a6b7c8d9_add_advanced_intel_fields.py` | add_advanced_intel_fields | 8 |
| **Расширенный** | `export_to_excel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/export_to_excel.py` | Database config | 7 |
| **Расширенный** | `export_to_excel.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scripts/export_to_excel.py` | Database config | 0 |
| **Расширенный** | `insert_note.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/insert_note.py` | !/usr/bin/env python3 Insert a true footnote or endnote into a DOCX by patching OOXML. | 0 |
| **Расширенный** | `inspect_eval_uv.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/community-evals/scripts/inspect_eval_uv.py` | /// script quires-python = ">=3.10" | 0 |
| **Расширенный** | `inspect_pr_checks.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/github/skills/gh-fix-ci/scripts/inspect_pr_checks.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `inspect_vllm_uv.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/community-evals/scripts/inspect_vllm_uv.py` | /// script quires-python = ">=3.10" | 0 |
| **Расширенный** | `lighteval_vllm_uv.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/hugging-face/skills/community-evals/scripts/lighteval_vllm_uv.py` | /// script quires-python = ">=3.10" | 0 |
| **Расширенный** | `post_write_figma_parity_check.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/figma/scripts/post_write_figma_parity_check.sh` | !/usr/bin/env bash Draft hook example for future plugin hook runtimes. | 0 |
| **Расширенный** | `sample.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/plugin-eval/fixtures/ts-python-sample/src/sample.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `sanity_check.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/sanity_check.py` | Автоматизация рабочего процесса. | 7 |
| **Расширенный** | `sanity_check.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scripts/sanity_check.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `scratch_check_specific.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/scratch_check_specific.py` | Автоматизация рабочего процесса. | 1 |
| **Расширенный** | `scratch_filter_notes.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/HR/scratch_filter_notes.py` | Автоматизация рабочего процесса. | 1 |
| **Расширенный** | `scratch_filter_notes.py` | `D:/Soft/Codex Backup/projects/HR/scratch_filter_notes.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `search_raw_system.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/search_raw_system.py` | Check if it's a RUN_COMMAND tool call | 8 |
| **Расширенный** | `simready_package_check_dependencies.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/shared/simready_package_check_dependencies.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Расширенный** | `sync-skills.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/render/scripts/sync-skills.sh` | !/usr/bin/env bash | 0 |
| **Расширенный** | `sync_projects_kb.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scripts/sync_projects_kb.py` | Автоматизация рабочего процесса. | 0 |
| **Интеграционный** | `aggregate_salmon_quant.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/workflows/bulk_rnaseq_counts_qc/aggregate_salmon_quant.py` | !/usr/bin/env python3 Aggregate Salmon quant.sf files into transcript- and gene-level matrices. | 0 |
| **Интеграционный** | `mass_replace.py` | `config/infra_management/scripts/mass_replace.py` | Configuration | 0 |
| **Интеграционный** | `mass_replace.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/config/infra_management/scripts/mass_replace.py` | Configuration | 1 |
| **Интеграционный** | `opentargets_disease_heatmap.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/opentargets-skill/scripts/opentargets_disease_heatmap.py` | !/usr/bin/env python3 Fetch Open Targets associated-disease datasource scores as a heatmap matrix. | 0 |
| **Интеграционный** | `run_star_genome_generate.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/workflows/scrnaseq_fastq_to_count/run_star_genome_generate.py` | Автоматизация рабочего процесса. | 0 |
| **Интеграционный** | `run_starsolo.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/workflows/scrnaseq_fastq_to_count/run_starsolo.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `box_cli_smoke.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/box/skills/box/scripts/box_cli_smoke.py` | !/usr/bin/env python3 Minimal Box CLI smoke-test helper. | 0 |
| **Диагностический** | `box_rest.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/box/skills/box/scripts/box_rest.py` | !/usr/bin/env python3 Minimal Box REST smoke-test helper using only the Python standard library. | 0 |
| **Диагностический** | `check_google_location.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/diagnostics/check_google_location.py` | Save html to examine | 8 |
| **Диагностический** | `diag_check.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scratch/diag_check.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `diagnose_acls.py` | `scripts/diagnose_acls.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `diagnose_acls.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/diagnose_acls.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `diagnose_codex_consolidation.py` | `scripts/diagnose_codex_consolidation.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `diagnose_codex_consolidation.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/diagnose_codex_consolidation.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `diagnose_remaining_locks.py` | `scripts/diagnose_remaining_locks.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `find-polluter.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/superpowers/skills/systematic-debugging/find-polluter.sh` | !/usr/bin/env bash Bisection script to find which test creates unwanted files/state | 0 |
| **Диагностический** | `heapprofd_reports.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/test-android-apps/skills/android-performance/scripts/heapprofd_reports.sh` | !/usr/bin/env bash | 0 |
| **Диагностический** | `jql_builder.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/atlassian-rovo/skills/generate-status-report/scripts/jql_builder.py` | !/usr/bin/env python3 | 0 |
| **Диагностический** | `llm_service_mock_testing.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/services/llm_service_mock_testing.py` | Автоматизация рабочего процесса. | 8 |
| **Диагностический** | `make_fixtures.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/scripts/make_fixtures.py` | !/usr/bin/env python3 Create reproducible DOCX fixtures for edge-case testing. | 0 |
| **Диагностический** | `manage_test_data.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/manage_test_data.py` | Автоматизация рабочего процесса. | 8 |
| **Диагностический** | `ngs_preflight.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/ngs_preflight.py` | !/usr/bin/env python3 Check NGS tool availability before suggesting or running installs. | 0 |
| **Диагностический** | `ngs_reference_manager.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/scripts/ngs_reference_manager.py` | !/usr/bin/env python3 Inspect and verify local NGS reference and database bundles. | 0 |
| **Диагностический** | `open_latest_report.bat` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/local_inventory/inventory/open_latest_report.bat` | Автоматизация рабочего процесса. | 2 |
| **Диагностический** | `open_latest_report.bat` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/open_latest_report.bat` | Автоматизация рабочего процесса. | 3 |
| **Диагностический** | `parse_google_html.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/diagnostics/parse_google_html.py` | Find all occurrences of Cyrillic country or city names or common Russian phrases indicating location | 8 |
| **Диагностический** | `preflight.ps1` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/preflight/scripts/preflight.ps1` | SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. SPDX-License-Identifier: Apache-2.0 | 0 |
| **Диагностический** | `preflight.py` | `scripts/preflight.py` | Fallback token estimator if tiktoken is not installed Fallback estimation: | 0 |
| **Диагностический** | `preflight.py` | `D:/Soft/Codex Backup/scripts/preflight.py` | Fallback token estimator if tiktoken is not installed Fallback estimation: | 0 |
| **Диагностический** | `preflight.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/scripts/preflight.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `preflight.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/preflight.py` | Fallback token estimator if tiktoken is not installed Fallback estimation: | 0 |
| **Диагностический** | `preflight.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/preflight/scripts/preflight.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `preflight.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/references/preflight/scripts/preflight.sh` | !/usr/bin/env sh SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `preflight_manifest.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/shared/preflight_manifest.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `run_test_summaries.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/run_test_summaries.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `setup_test_matches.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/app/setup_test_matches.py` | 1. Create a dummy owner | 8 |
| **Диагностический** | `simpleperf_hotspots.sh` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/test-android-apps/skills/android-performance/scripts/simpleperf_hotspots.sh` | !/usr/bin/env bash | 0 |
| **Диагностический** | `test_admin_and_delete.py` | `scripts/test_admin_and_delete.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_admin_and_delete.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/scripts/test_admin_and_delete.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_all_keys_vps.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/diagnostics/test_all_keys_vps.py` | Автоматизация рабочего процесса. | 8 |
| **Диагностический** | `test_api.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/tests/test_api.py` | Автоматизация рабочего процесса. | 8 |
| **Диагностический** | `test_api_endpoints.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/test_api_endpoints.py` | Load .env to get the API_SECRET_KEY | 8 |
| **Диагностический** | `test_bcl_to_fastq_runner.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/tests/test_bcl_to_fastq_runner.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_bulk_rnaseq_counts_qc_runner.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/tests/test_bulk_rnaseq_counts_qc_runner.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_compile_latex_strategy.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/bundled-marketplaces/openai-bundled/plugins/latex/tests/test_compile_latex_strategy.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_container_dns.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/diagnostics/test_container_dns.py` | Автоматизация рабочего процесса. | 8 |
| **Диагностический** | `test_draft_prompt.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/test_draft_prompt.py` | Автоматизация рабочего процесса. | 8 |
| **Диагностический** | `test_fixes_verification.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/tests/test_fixes_verification.py` | 1. 1C string with surname + name + position 2. Surname + Name | 0 |
| **Диагностический** | `test_ftp.py` | `projects/tilda_migration/test_ftp.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_ftp.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/test_ftp.py` | Автоматизация рабочего процесса. | 1 |
| **Диагностический** | `test_imap_service.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/tests/test_imap_service.py` | When it's not a forwarded email from longwang.ru | 8 |
| **Диагностический** | `test_install_texlive_profile.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/bundled-marketplaces/openai-bundled/plugins/latex/tests/test_install_texlive_profile.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_llm_service.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/tests/test_llm_service.py` | Setup mock | 8 |
| **Диагностический** | `test_map_locus_to_gene.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/locus-to-gene-mapper-skill/scripts/test_map_locus_to_gene.py` | !/usr/bin/env python3 | 0 |
| **Диагностический** | `test_ncbi_blast.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/ncbi-blast-skill/scripts/test_ncbi_blast.py` | !/usr/bin/env python3 Unit tests for ncbi_blast.py. | 0 |
| **Диагностический** | `test_new_backend_planners.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/tests/test_new_backend_planners.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_ngs_preflight.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/tests/test_ngs_preflight.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_rebuild_sintez.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scratch/test_rebuild_sintez.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `test_render.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/morningstar/skills/fund-summarizer/scripts/test_render.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_rest_request.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/life-science-research/skills/eqtl-catalogue-skill/scripts/test_rest_request.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_sample.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/plugin-eval/fixtures/ts-python-sample/tests/test_sample.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_scrnaseq_post_count_qc_runner.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/ngs-analysis/tests/test_scrnaseq_post_count_qc_runner.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_subject_formatting.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai/scratch/test_subject_formatting.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_vps_curl.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/diagnostics/test_vps_curl.py` | Автоматизация рабочего процесса. | 8 |
| **Диагностический** | `test_vps_proxy.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/diagnostics/test_vps_proxy.py` | Force DNS resolution to 87.228.47.204 for Python urllib We do this by modifying the HTTP request host to the IP and setting Host header | 8 |
| **Диагностический** | `test_vps_sdk.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Shared/projects/n8n_email_ai_funnel_version/scripts/diagnostics/test_vps_sdk.py` | Автоматизация рабочего процесса. | 8 |
| **Диагностический** | `tilda_auth_test.py` | `projects/tilda_migration/tilda_auth_test.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `tilda_auth_test.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_auth_test.py` | Автоматизация рабочего процесса. | 1 |
| **Диагностический** | `tilda_test_projects_param.py` | `projects/tilda_migration/tilda_test_projects_param.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `tilda_test_projects_param.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/projects/tilda_migration/tilda_test_projects_param.py` | Автоматизация рабочего процесса. | 1 |
| **Диагностический** | `ui_pick.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/test-android-apps/skills/android-emulator-qa/scripts/ui_pick.py` | !/usr/bin/env python3 | 0 |
| **Диагностический** | `ui_tree_summarize.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/test-android-apps/skills/android-emulator-qa/scripts/ui_tree_summarize.py` | !/usr/bin/env python3 | 0 |
| **Диагностический** | `usd_convert_cad_diagnostics.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/codex_home/.tmp/plugins/plugins/nvidia/skills/omniverse-cad-to-simready/shared/usd_convert_cad_diagnostics.py` | !/usr/bin/env python3 SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. | 0 |
| **Диагностический** | `verify.py` | `config/infra_management/scripts/verify.py` | Configuration | 0 |
| **Диагностический** | `verify.py` | `D:/Soft/Codex Backup/migration_snapshot_2026-09-29/Codex_Personal/config/infra_management/scripts/verify.py` | Configuration | 1 |
| **Диагностический** | `verify_no_old_paths.py` | `scripts/verify_no_old_paths.py` | Автоматизация рабочего процесса. | 0 |

---
