# Единый каталог скриптов и автоматизаций контура (SCRIPTS_CATALOG)

> **Дата последней автоматической ревизии:** `2026-09-25 23:09:09`  
> **Статус контура:** Уникальных проверенных скриптов: `510` | Отсеяно дубликатов: `596` | Библиотек вендоров: `4385`.  
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
| **Базовый** | `clean_temporary_categories.py` | `projects/AI chats export/src/clean_temporary_categories.py` | Записываем в utf-8-sig (UTF-8 с BOM) | 0 |
| **Базовый** | `clean_temporary_categories.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/clean_temporary_categories.py` | Записываем в utf-8-sig (UTF-8 с BOM) | 0 |
| **Базовый** | `merge_small_files.py` | `projects/AI chats export/src/merge_small_files.py` | Чтение файла и удаление заголовка категории | 0 |
| **Базовый** | `merge_small_files.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/merge_small_files.py` | Чтение файла и удаление заголовка категории | 0 |
| **Базовый** | `parse_unresolved.py` | `projects/AI chats export/src/parse_unresolved.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `parse_unresolved.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/parse_unresolved.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `parse_unresolved_recovered.py` | `projects/AI chats export/src/parse_unresolved_recovered.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `parse_unresolved_recovered.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/parse_unresolved_recovered.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `recover_lost_batches.py` | `projects/AI chats export/src/recover_lost_batches.py` | Setup API Key | 0 |
| **Базовый** | `recover_lost_batches.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/recover_lost_batches.py` | Setup API Key | 0 |
| **Базовый** | `retry_failed_batches.py` | `projects/AI chats export/src/retry_failed_batches.py` | Добавляем папку src в пути поиска модулей | 0 |
| **Базовый** | `retry_failed_batches.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/retry_failed_batches.py` | Добавляем папку src в пути поиска модулей | 0 |
| **Расширенный** | `AI_chats_filter_optimized.py` | `projects/AI chats export/src/AI_chats_filter_optimized.py` | Принудительно настраиваем UTF-8 для вывода в консоль | 0 |
| **Расширенный** | `AI_chats_filter_optimized.py` | `D:/Soft/Codex Backup/projects/AI chats export/src/AI_chats_filter_optimized.py` | Принудительно настраиваем UTF-8 для вывода в консоль | 0 |

---

<a id='supply_china'></a>
## 2. Снабжение и ВЭД в Китае (Дечжоу / Циндао, фонд 5000 RMB, возврат НДС)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `h03__del_relax_supply_gate.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tries/h03__del_relax_supply_gate.py` | !/usr/bin/env python3 | 3 |
| **Расширенный** | `check_import_china.py` | `projects/tilda_migration/check_import_china.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_import_china.py` | `D:/Soft/Codex Backup/projects/tilda_migration/check_import_china.py` | Автоматизация рабочего процесса. | 0 |

---

<a id='price_creating'></a>
## 3. Создание прайс-листов и коммерческих предложений из каталогов

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| - | *Нет зарегистрированных скриптов* | - | - | - |

---

<a id='hr_resume'></a>
## 4. Анализ резюме, RAG-база кандидатов и генерация ответов соискателям

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `build_candidates_rag_db.py` | `projects/HR/build_candidates_rag_db.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `scratch_parse_resumes.py` | `projects/HR/scratch_parse_resumes.py` | ow 2 contains actual column headers | 0 |
| **Базовый** | `scratch_print_all.py` | `projects/HR/scratch_print_all.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_clean_digits.py` | `projects/HR/search_clean_digits.py` | ove spaces and punctuation | 0 |
| **Расширенный** | `check_inbox_reply.py` | `projects/HR/check_inbox_reply.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `create_candidates_excel.py` | `projects/HR/create_candidates_excel.py` | Sheet 1: Candidates list | 0 |
| **Расширенный** | `scratch_check_specific.py` | `projects/HR/scratch_check_specific.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `scratch_filter_notes.py` | `projects/HR/scratch_filter_notes.py` | Автоматизация рабочего процесса. | 0 |

---

<a id='pc_migration'></a>
## 5. Перенос данных с ПК на ПК (HP Victus ⮂ MateBook ⮂ Mirror_E_Home)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `document.py` | `D:/Soft/Codex Backup/AI Backups Victus/Codex_Work/projects/tender-extraction-lab/tender-rag-api/app/schemas/document.py` | Схема для описания структуры одного чанка | 0 |
| **Базовый** | `document.py` | `D:/Soft/Codex Backup/AI Backups Victus/Codex_Work/projects/tender-extraction-lab/tender-rag-api/app/services/document.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `document.py` | `D:/Soft/Codex Backup/AI Backups Victus/Codex_Work/projects/tender-extraction-lab/tender-rag-api/app/api/routers/document.py` | Передаем файл в слой бизнес-логики для парсинга и нарезки | 0 |
| **Базовый** | `main.py` | `D:/Soft/Codex Backup/AI Backups Victus/Codex_Work/projects/tender-extraction-lab/tender-rag-api/app/main.py` | Подключаем наш роутер | 0 |

---

<a id='sprint_mikhail'></a>
## 6. Спринты Михаила, RAG ГОЗ и Архитектура сети VPS

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `add_wait_node.py` | `C:/Users/Артем/tender-rag-api/scratch/add_wait_node.py` | Create the Wait node | 0 |
| **Базовый** | `audit_db.py` | `C:/Users/Артем/tender-rag-api/scratch/audit_db.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `config.py` | `C:/Users/Артем/tender-rag-api/app/core/config.py` | odels | 0 |
| **Базовый** | `deploy-tender.sh` | `scripts/vps/deploy-tender.sh` | Безопасный деплой проекта тендеров tender-rag-api для пользователя mikhail Выполняется через sudo /usr/local/bin/deploy-tender.sh или tender-webhook-deploy | 0 |
| **Базовый** | `deploy_metabase_analytics.py` | `C:/Users/Артем/tender-rag-api/scripts/deploy_metabase_analytics.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `document.py` | `C:/Users/Артем/tender-rag-api/app/api/routers/document.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_backfill_sql.py` | `C:/Users/Артем/tender-rag-api/analytics/scripts/generate_backfill_sql.py` | Загружаем переменные окружения | 0 |
| **Базовый** | `import_white_base.py` | `C:/Users/Артем/tender-rag-api/scripts/import_white_base.py` | Format list into pgvector string format: '[1.0, 2.0, 3.0]' | 0 |
| **Базовый** | `key_manager.py` | `C:/Users/Артем/tender-rag-api/app/core/key_manager.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `llm_service.py` | `C:/Users/Артем/tender-rag-api/app/services/llm_service.py` | Ограничиваем количество чанков (Token-First Vibe Engineering) | 0 |
| **Базовый** | `logger.py` | `C:/Users/Артем/tender-rag-api/app/core/logger.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `rabbitmq.py` | `C:/Users/Артем/tender-rag-api/app/core/rabbitmq.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `read_docx.py` | `C:/Users/Артем/tender-rag-api/scratch/read_docx.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tender_webhook_deploy.py` | `scripts/vps/tender_webhook_deploy.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `tender_worker.py` | `C:/Users/Артем/tender-rag-api/app/workers/tender_worker.py` | Для тестов по умолчанию стучимся на локальный мок-сервер 5001, а на бою - в n8n | 0 |
| **Базовый** | `update_docs.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs.py` | Update PROGRESS.md | 0 |
| **Базовый** | `update_docs_chat.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs_chat.py` | Update PROGRESS.md | 0 |
| **Базовый** | `update_docs_heuristic.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs_heuristic.py` | 1. Update PROGRESS.md | 0 |
| **Базовый** | `update_docs_report.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs_report.py` | 1. Update PROGRESS.md Update (2026-07-15) | 0 |
| **Базовый** | `update_summary_fields.py` | `C:/Users/Артем/tender-rag-api/scratch/update_summary_fields.py` | Update Get Deals node | 0 |
| **Базовый** | `ved_audit_service.py` | `C:/Users/Артем/tender-rag-api/app/services/ved_audit_service.py` | Generate embedding using Gemini API (same model as the White Base import). | 0 |
| **Расширенный** | `b24_daily_analytics_sync.py` | `C:/Users/Артем/tender-rag-api/scripts/b24_daily_analytics_sync.py` | !/usr/bin/env python3 | 0 |
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
| **Базовый** | `fix_acrobat_genuine.ps1` | `scripts/fix_acrobat_genuine.ps1` | fix_acrobat_genuine.ps1 Comprehensive Adobe Acrobat Genuine & Deactivation Popup Eliminator | 0 |
| **Базовый** | `resolve_unassociated.py` | `Shared: projects/n8n_email_ai/scripts/resolve_unassociated.py` | Setup path to import app config and services | 3 |
| **Базовый** | `resolve_unassociated.py` | `Shared: projects/n8n_email_ai_v6_backup/archive/backup_20260805_v4plus/resolve_unassociated.py` | Setup path to import app config and services | 4 |
| **Базовый** | `resolve_unassociated.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/resolve_unassociated.py` | Setup path to import app config and services | 0 |
| **Базовый** | `show_llm_stats.py` | `Shared: projects/n8n_email_ai/scripts/show_llm_stats.py` | Setup path to import app config | 0 |
| **Базовый** | `update_email_compose.py` | `Shared: projects/n8n_email_ai_migration_backup_20260809/vps_backups/update_email_compose.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `update_vps_compose.py` | `Shared: projects/n8n_email_ai_migration_backup_20260809/vps_backups/update_vps_compose.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `weekly_run.bat` | `projects/local_inventory/inventory/weekly_run.bat` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `weekly_run.bat` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/weekly_run.bat` | Автоматизация рабочего процесса. | 2 |
| **Расширенный** | `check_and_clean_pc.py` | `scripts/check_and_clean_pc.py` | !/usr/bin/env python3 | 0 |
| **Диагностический** | `check_db_status.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/check_db_status.py` | Setup path to import app config | 4 |
| **Диагностический** | `update_email_compose.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/diagnostics/update_email_compose.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `update_vps_compose.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/diagnostics/update_vps_compose.py` | Автоматизация рабочего процесса. | 4 |

---

<a id='session_compression'></a>
## 8. Анализ истории чата, сжатие сессий и /learn

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `apply_complete_sintez_summary.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/apply_complete_sintez_summary.py` | 1. Start SSH tunnel locally | 2 |
| **Базовый** | `build_index.py` | `scripts/build_index.py` | normalize path separators | 0 |
| **Базовый** | `build_index.py` | `Shared: scripts/build_index.py` | normalize path separators | 0 |
| **Базовый** | `build_index.py` | `D:/Soft/Codex Backup/scripts/build_index.py` | normalize path separators | 0 |
| **Базовый** | `full_gravity_audit.py` | `scripts/full_gravity_audit.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_local_summary.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/generate_local_summary.py` | 1. Start SSH tunnel locally to connect to VPS Postgres | 2 |
| **Базовый** | `parse_sprint_summary.py` | `scripts/parse_sprint_summary.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `print_xlsx_summary.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/print_xlsx_summary.py` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `run_single_sintez_summary.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/run_single_sintez_summary.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `session_compress.py` | `scripts/session_compress.py` | Определяем корневую директорию проекта на основе расположения скрипта скрипт лежит в <root>/scripts/session_compress.py | 0 |
| **Базовый** | `session_compress.py` | `Shared: scripts/session_compress.py` | Определяем корневую директорию проекта на основе расположения скрипта скрипт лежит в <root>/scripts/session_compress.py | 0 |
| **Базовый** | `session_compress.py` | `D:/Soft/Codex Backup/scripts/session_compress.py` | Определяем корневую директорию проекта на основе расположения скрипта скрипт лежит в <root>/scripts/session_compress.py | 0 |
| **Базовый** | `summary_service.py` | `Shared: projects/n8n_email_ai_funnel_version/app/services/summary_service.py` | 1. Fetch contact messages (both processed and unprocessed to get full context) | 4 |
| **Расширенный** | `audit_archived_transcripts.py` | `scripts/audit_archived_transcripts.py` | Автоматический аудит логов архивных сессий `brain/*/transcript.jsonl` за 14-45 дней: поиск упущенных директив, замечаний пользователя и бизнес-ограничений. Запуск: `py scripts/audit_archived_transcripts.py [дни]`. | 0 |
| **Расширенный** | `check_sintez_summary.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/check_sintez_summary.py` | Автоматизация рабочего процесса. | 2 |

---

<a id='onec_bitrix_sync'></a>
## 9. Связка 1С:УНФ и Битрикс24 (OData, Контрагенты, Заказы, СКД)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `5e469a8be92c_add_unique_constraint_to_onec_owner_.py` | `Shared: projects/n8n_email_ai_funnel_version/alembic/versions/5e469a8be92c_add_unique_constraint_to_onec_owner_.py` | add unique constraint to onec_owner_links | 4 |
| **Базовый** | `a705ca4e0aee_add_onec_owner_links_and_is_synthetic.py` | `Shared: projects/n8n_email_ai_funnel_version/alembic/versions/a705ca4e0aee_add_onec_owner_links_and_is_synthetic.py` | add onec_owner_links and is_synthetic | 4 |
| **Базовый** | `analyze_batch_4.py` | `Shared: projects/1c_odata/scratch/analyze_batch_4.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `analyze_odata.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/analyze_odata.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `b1c2d3e4f5a6_add_knowledge_base.py` | `Shared: projects/n8n_email_ai_funnel_version/alembic/versions/b1c2d3e4f5a6_add_knowledge_base.py` | add knowledge_base | 4 |
| **Базовый** | `b24_chat_intelligence.py` | `Shared: projects/1c_odata/scripts/b24_chat_intelligence.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `build_exam_docx.py` | `Shared: projects/1c_odata/scratch/build_exam_docx.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `build_kpi_erf.py` | `Shared: projects/1c_odata/scripts/build_kpi_erf.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `build_master_regulation_docx.py` | `Shared: projects/1c_odata/scratch/build_master_regulation_docx.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `build_scripts_registry.py` | `Shared: projects/1c_odata/scratch/build_scripts_registry.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `catalog_scripts.py` | `Shared: projects/1c_odata/scratch/catalog_scripts.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `deal_followup_pipeline.py` | `projects/1c_odata/scripts/deal_followup_pipeline.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `deep_chat_inspector.py` | `Shared: projects/1c_odata/scratch/deep_chat_inspector.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `deep_inspect_batch_12.py` | `Shared: projects/1c_odata/scripts/deep_inspect_batch_12.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `deep_inspect_batch_12_first4.py` | `Shared: projects/1c_odata/scripts/deep_inspect_batch_12_first4.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `docx_engine.py` | `Shared: projects/1c_odata/scratch/docx_engine.py` | Color Palette | 0 |
| **Базовый** | `docx_styler.py` | `Shared: projects/1c_odata/scratch/docx_styler.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `dump_lead_groups.py` | `Shared: projects/1c_odata/scratch/dump_lead_groups.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `execute_batch_3.py` | `Shared: projects/1c_odata/scratch/execute_batch_3.py` | ------------------------------------------------------------- CREDENTIALS & CONSTANTS | 0 |
| **Базовый** | `execute_batch_4.py` | `Shared: projects/1c_odata/scratch/execute_batch_4.py` | ------------------------------------------------------------- CREDENTIALS & CONSTANTS | 0 |
| **Базовый** | `execute_batch_pipeline.py` | `Shared: projects/1c_odata/scripts/execute_batch_pipeline.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `extract_all_target_chat_messages.py` | `Shared: projects/1c_odata/scratch/extract_all_target_chat_messages.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `fetch_b24_details.py` | `Shared: projects/1c_odata/scratch/fetch_b24_details.py` | 1. Company 11886 | 0 |
| **Базовый** | `fetch_email_119.py` | `Shared: projects/1c_odata/scripts/fetch_email_119.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_all_target_chats.py` | `Shared: projects/1c_odata/scratch/find_all_target_chats.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_lmz_lead.py` | `Shared: projects/1c_odata/scratch/find_lmz_lead.py` | 1. Search Catalog_Лиды by Description 'ЛМЗ Рыбинск' | 0 |
| **Базовый** | `find_today_activity.py` | `Shared: projects/1c_odata/scratch/find_today_activity.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_batch_4_dry_run.py` | `Shared: projects/1c_odata/scratch/generate_batch_4_dry_run.py` | Constants | 0 |
| **Базовый** | `group_scripts.py` | `Shared: projects/1c_odata/scratch/group_scripts.py` | Categories definition | 0 |
| **Базовый** | `inspect_batch_12.py` | `Shared: projects/1c_odata/scripts/inspect_batch_12.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_batch_4_details.py` | `Shared: projects/1c_odata/scratch/inspect_batch_4_details.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_batch_5_bodies.py` | `Shared: projects/1c_odata/scratch/inspect_batch_5_bodies.py` | Print body preview We can inspect the attachments or bodies | 0 |
| **Базовый** | `inspect_deal_2166.py` | `Shared: projects/1c_odata/scratch/inspect_deal_2166.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_docs_detailed.py` | `Shared: projects/1c_odata/scratch/inspect_docs_detailed.py` | 1. Inspect i7858_Договор_по_КК_РОС.doc xtract text by searching for words in binary doc | 0 |
| **Базовый** | `inspect_item_details.py` | `Shared: projects/1c_odata/scripts/inspect_item_details.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `parse_attachments.py` | `Shared: projects/1c_odata/scratch/parse_attachments.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `print_batch_4_bodies.py` | `Shared: projects/1c_odata/scratch/print_batch_4_bodies.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `print_batch_5.py` | `Shared: projects/1c_odata/scratch/print_batch_5.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `print_bodies_batch_5.py` | `Shared: projects/1c_odata/scratch/print_bodies_batch_5.py` | Let's inspect IMAP bodies from scratch/attachments_batch_41_50 or re-fetch body | 0 |
| **Базовый** | `print_items_35_36_38.py` | `Shared: projects/1c_odata/scratch/print_items_35_36_38.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `process_b24_inbound_leads.py` | `Shared: projects/1c_odata/scripts/process_b24_inbound_leads.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `process_batch_pipeline.py` | `Shared: projects/1c_odata/scripts/process_batch_pipeline.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `process_today_followup_deals.py` | `projects/1c_odata/scripts/process_today_followup_deals.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `process_today_followup_deals.py` | `Shared: projects/1c_odata/scripts/process_today_followup_deals.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `qualify_batch_5.py` | `Shared: projects/1c_odata/scratch/qualify_batch_5.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `read_batch_5_bodies.py` | `Shared: projects/1c_odata/scratch/read_batch_5_bodies.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `read_docx_attachments.py` | `Shared: projects/1c_odata/scratch/read_docx_attachments.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `read_email_thread.py` | `Shared: projects/1c_odata/scratch/read_email_thread.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `scratch_b24_fetch.py` | `projects/HR/scratch_b24_fetch.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_1c_entities.py` | `projects/1c_odata/scripts/search_1c_entities.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_1c_entities.py` | `Shared: projects/1c_odata/scripts/search_1c_entities.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_1c_entities.py` | `D:/Soft/Codex Backup/projects/1c_odata/scripts/search_1c_entities.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_agrosnab.py` | `Shared: projects/1c_odata/scripts/search_agrosnab.py` | 1. Search Leads | 0 |
| **Базовый** | `search_dadata_batch_4.py` | `Shared: projects/1c_odata/scratch/search_dadata_batch_4.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_tasks_and_topics.py` | `Shared: projects/1c_odata/scratch/search_tasks_and_topics.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `summarize_batch_4.py` | `Shared: projects/1c_odata/scratch/summarize_batch_4.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `update_gas_exam.py` | `Shared: projects/1c_odata/scratch/update_gas_exam.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_1c_batch_5.py` | `Shared: projects/1c_odata/scratch/check_1c_batch_5.py` | 1. Counterparty 2. Lead | 0 |
| **Расширенный** | `check_all_folders.py` | `Shared: projects/1c_odata/scratch/check_all_folders.py` | xample: '(\\HasNoChildren \\Drafts) "." Drafts' | 0 |
| **Расширенный** | `check_contact_15984.py` | `Shared: projects/1c_odata/scripts/check_contact_15984.py` | 1. B24 Contact 15984 | 0 |
| **Расширенный** | `check_contractor.py` | `projects/1c_odata/check_contractor.py` | !/usr/bin/env python3 | 1 |
| **Расширенный** | `check_contractor.py` | `Shared: projects/1c_odata/check_contractor.py` | !/usr/bin/env python3 | 3 |
| **Расширенный** | `check_details_batch_5.py` | `Shared: projects/1c_odata/scratch/check_details_batch_5.py` | 1. Map attachments to items | 0 |
| **Расширенный** | `check_item_49_50.py` | `Shared: projects/1c_odata/scratch/check_item_49_50.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_items_json.py` | `Shared: projects/1c_odata/scratch/check_items_json.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_lmz_contacts.py` | `Shared: projects/1c_odata/scratch/check_lmz_contacts.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_msg_7897.py` | `Shared: projects/1c_odata/scratch/check_msg_7897.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_snab_region.py` | `Shared: projects/1c_odata/scripts/check_snab_region.py` | 1. Inspect Lead 000001663 in 1C | 0 |
| **Расширенный** | `inspect_b24_deals.py` | `Shared: projects/1c_odata/scratch/inspect_b24_deals.py` | Also check company for rsce.ru | 0 |
| **Расширенный** | `inspect_item_119.py` | `Shared: projects/1c_odata/scripts/inspect_item_119.py` | Let's check IMAP message for item 119 or scratch files | 0 |
| **Расширенный** | `inspect_petroship_email.py` | `Shared: projects/1c_odata/scratch/inspect_petroship_email.py` | Check activities on Contact 16332 and Lead 17338 | 0 |
| **Расширенный** | `onec_sync_service.py` | `Shared: projects/n8n_email_ai_funnel_version/app/services/onec_sync_service.py` | Автоматизация рабочего процесса. | 3 |
| **Расширенный** | `onec_sync_service.py` | `Shared: projects/n8n_email_ai/app/services/onec_sync_service.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `prepare_excel_for_1c.py` | `Shared: projects/1c_odata/scripts/prepare_excel_for_1c.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `run_check_contractors_batch_4.py` | `Shared: projects/1c_odata/scratch/run_check_contractors_batch_4.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `run_onec_sync.py` | `Shared: projects/n8n_email_ai_funnel_version/app/run_onec_sync.py` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `sync_to_bitrix.py` | `projects/1c_odata/scripts/sync_to_bitrix.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `sync_to_bitrix.py` | `Shared: projects/1c_odata/scripts/sync_to_bitrix.py` | Автоматизация рабочего процесса. | 1 |
| **Интеграционный** | `build_rod_matrix.py` | `Shared: projects/1c_odata/scratch/build_rod_matrix.py` | Sheet 1: Master Rod Matrix | 0 |
| **Диагностический** | `test_chat_search.py` | `Shared: projects/1c_odata/scratch/test_chat_search.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_fetch_chat.py` | `Shared: projects/1c_odata/scratch/test_fetch_chat.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_fetch_saule.py` | `Shared: projects/1c_odata/scratch/test_fetch_saule.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_imap_accounts.py` | `Shared: projects/1c_odata/scratch/test_imap_accounts.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_odata_filters.py` | `Shared: projects/1c_odata/scratch/test_odata_filters.py` | Test 1: substringof in Тема | 0 |
| **Диагностический** | `test_odata_url.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/test_odata_url.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `verify_batch_4.py` | `Shared: projects/1c_odata/scratch/verify_batch_4.py` | Автоматизация рабочего процесса. | 0 |

---

<a id='lead_inbound'></a>
## 10. Обработка новых лидов и Inbound-снабжение (Email AI Pipeline)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `21ff2b48fe8d_add_ai_processed_to_email_match_results.py` | `Shared: projects/n8n_email_ai_funnel_version/alembic/versions/21ff2b48fe8d_add_ai_processed_to_email_match_results.py` | add_ai_processed_to_email_match_results | 4 |
| **Базовый** | `analyze_csv.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/analyze_csv.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `analyze_unassociated.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/analyze_unassociated.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `apply_unassociated_matches.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/apply_unassociated_matches.py` | Автоматизация рабочего процесса. | 9 |
| **Базовый** | `c2d3e4f5a6b7_add_content_hash.py` | `Shared: projects/n8n_email_ai_funnel_version/alembic/versions/c2d3e4f5a6b7_add_content_hash.py` | add content_hash to knowledge_base | 4 |
| **Базовый** | `chunk_kb.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/chunk_kb.py` | Add root project path to sys.path | 4 |
| **Базовый** | `config.py` | `Shared: projects/n8n_email_ai/app/core/config.py` | Database | 3 |
| **Базовый** | `config.py` | `Shared: projects/n8n_email_ai_funnel_version/app/core/config.py` | Database | 0 |
| **Базовый** | `cooldown_guard.py` | `Shared: projects/n8n_email_ai/app/services/cooldown_guard.py` | Public email providers where domain-level cooldown must NOT be applied to all clients | 0 |
| **Базовый** | `d3e4f5a6b7c8_add_emails_metadata_to_clients_intel.py` | `Shared: projects/n8n_email_ai_funnel_version/alembic/versions/d3e4f5a6b7c8_add_emails_metadata_to_clients_intel.py` | add_emails_metadata_to_clients_intel | 4 |
| **Базовый** | `database.py` | `Shared: projects/n8n_email_ai_funnel_version/app/db/database.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `debug_cursors.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/debug_cursors.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `dump_match_results.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/dump_match_results.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `env.py` | `Shared: projects/n8n_email_ai_funnel_version/alembic/env.py` | this is the Alembic Config object, which provides access to the values within the .ini file in use. | 4 |
| **Базовый** | `export_data.bat` | `Shared: projects/n8n_email_ai/export_data.bat` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `export_data.ps1` | `Shared: projects/n8n_email_ai_funnel_version/scripts/export_data.ps1` | nforce UTF-8 output | 4 |
| **Базовый** | `fetch_raw_emails.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/fetch_raw_emails.py` | 1. Start SSH tunnel locally | 2 |
| **Базовый** | `imap_service.py` | `Shared: projects/n8n_email_ai_funnel_version/app/services/imap_service.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `kb_chunk_export.ps1` | `projects/n8n_email_ai/rag_tools/kb_chunk_export.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `kb_chunk_export.ps1` | `Shared: projects/n8n_email_ai_funnel_version/50_rag_tools/kb_chunk_export.ps1` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `list_models.py` | `Shared: projects/n8n_email_ai/scripts/list_models.py` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `list_models.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/list_models.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `llm_service.py` | `Shared: projects/n8n_email_ai_funnel_version/app/services/llm_service.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `llm_service.py` | `Shared: projects/n8n_email_ai/app/services/llm_service.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `llm_service_production.py` | `Shared: projects/n8n_email_ai_funnel_version/app/services/llm_service_production.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `log_service.py` | `Shared: projects/n8n_email_ai_funnel_version/app/services/log_service.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `main.py` | `Shared: projects/n8n_email_ai_funnel_version/app/main.py` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `main.py` | `Shared: projects/n8n_email_ai/app/main.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `models.py` | `Shared: projects/n8n_email_ai_funnel_version/app/db/models.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `models.py` | `Shared: projects/n8n_email_ai/app/db/models.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `remote_n8n_fix.sh` | `projects/server_ops/snapshots/remote_n8n_fix.sh` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `remote_n8n_fix.sh` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/server_ops/snapshots/remote_n8n_fix.sh` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `remote_n8n_fix2.sh` | `projects/server_ops/snapshots/remote_n8n_fix2.sh` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `remote_n8n_fix2.sh` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/server_ops/snapshots/remote_n8n_fix2.sh` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `reset_sintez_db.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/reset_sintez_db.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `run_imap.py` | `Shared: projects/n8n_email_ai_funnel_version/app/run_imap.py` | Load env variables | 4 |
| **Базовый** | `run_rag_vectorize.py` | `Shared: projects/n8n_email_ai_funnel_version/app/run_rag_vectorize.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `run_summaries_batch.py` | `Shared: projects/n8n_email_ai_funnel_version/app/run_summaries_batch.py` | Get up to limit unique from_emails that have unprocessed matched emails | 4 |
| **Базовый** | `schemas.py` | `Shared: projects/n8n_email_ai_funnel_version/app/api/schemas.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `search_imap_all_folders.py` | `projects/HR/search_imap_all_folders.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_system_commands.py` | `Shared: projects/n8n_email_ai_funnel_version/app/search_system_commands.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `text_cleaner.py` | `Shared: projects/n8n_email_ai_funnel_version/app/services/text_cleaner.py` | 1. Если исходный текст совсем пустой, но есть HTML, используем его | 4 |
| **Расширенный** | `check_cursor.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/check_cursor.py` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `check_db.py` | `Shared: projects/n8n_email_ai/check_db.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_db_dates.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/check_db_dates.py` | Автоматизация рабочего процесса. | 2 |
| **Расширенный** | `check_drafts.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/check_drafts.py` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `check_drive_access.py` | `scripts/check_drive_access.py` | Если вы измените эти области доступа, удалите файл token.json. | 0 |
| **Расширенный** | `check_drive_access.py` | `D:/Soft/Codex Backup/scripts/check_drive_access.py` | Если вы измените эти области доступа, удалите файл token.json. | 0 |
| **Расширенный** | `check_folders.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/check_folders.py` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `check_matched_levels.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/check_matched_levels.py` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `check_sintez_emails.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/check_sintez_emails.py` | Автоматизация рабочего процесса. | 2 |
| **Расширенный** | `check_sintez_owner_emails.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/check_sintez_owner_emails.py` | Автоматизация рабочего процесса. | 2 |
| **Расширенный** | `check_today.py` | `Shared: projects/n8n_email_ai/scratch/check_today.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `e4f5a6b7c8d9_add_advanced_intel_fields.py` | `Shared: projects/n8n_email_ai_funnel_version/alembic/versions/e4f5a6b7c8d9_add_advanced_intel_fields.py` | add_advanced_intel_fields | 4 |
| **Расширенный** | `export_to_excel.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/export_to_excel.py` | Database config | 4 |
| **Расширенный** | `run_junk_filter.py` | `Shared: projects/n8n_email_ai_funnel_version/app/run_junk_filter.py` | Get messages that are currently 'needs_review' and not processed by junk filter We can identify them by checking EmailMatchResult.decision == 'needs_review' | 4 |
| **Расширенный** | `sanity_check.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/sanity_check.py` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `search_raw_system.py` | `Shared: projects/n8n_email_ai_funnel_version/app/search_raw_system.py` | Check if it's a RUN_COMMAND tool call | 4 |
| **Расширенный** | `sync_projects_kb.py` | `Shared: projects/n8n_email_ai/scripts/sync_projects_kb.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `check_google_location.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/diagnostics/check_google_location.py` | Save html to examine | 4 |
| **Диагностический** | `diag_check.py` | `Shared: projects/n8n_email_ai/scratch/diag_check.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `llm_service_mock_testing.py` | `Shared: projects/n8n_email_ai_funnel_version/app/services/llm_service_mock_testing.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `manage_test_data.py` | `Shared: projects/n8n_email_ai_funnel_version/app/manage_test_data.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `parse_google_html.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/diagnostics/parse_google_html.py` | Find all occurrences of Cyrillic country or city names or common Russian phrases indicating location | 4 |
| **Диагностический** | `run_test_summaries.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/run_test_summaries.py` | Автоматизация рабочего процесса. | 2 |
| **Диагностический** | `setup_test_matches.py` | `Shared: projects/n8n_email_ai_funnel_version/app/setup_test_matches.py` | 1. Create a dummy owner | 4 |
| **Диагностический** | `test_api.py` | `Shared: projects/n8n_email_ai_funnel_version/tests/test_api.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `test_api_endpoints.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/test_api_endpoints.py` | Load .env to get the API_SECRET_KEY | 4 |
| **Диагностический** | `test_container_dns.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/diagnostics/test_container_dns.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `test_draft_prompt.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/test_draft_prompt.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `test_imap_service.py` | `Shared: projects/n8n_email_ai_funnel_version/tests/test_imap_service.py` | When it's not a forwarded email from longwang.ru | 4 |
| **Диагностический** | `test_llm_service.py` | `Shared: projects/n8n_email_ai_funnel_version/tests/test_llm_service.py` | Setup mock | 4 |
| **Диагностический** | `test_rebuild_sintez.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/test_rebuild_sintez.py` | Автоматизация рабочего процесса. | 2 |
| **Диагностический** | `test_subject_formatting.py` | `Shared: projects/n8n_email_ai/scratch/test_subject_formatting.py` | Автоматизация рабочего процесса. | 0 |

---

<a id='followup_sales'></a>
## 11. Follow-up продаж в сделках и реактивация клиентов

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `run_daily_reactivation.py` | `Shared: projects/n8n_email_ai_v6_backup/app/run_daily_reactivation.py` | Setup path | 0 |
| **Базовый** | `run_daily_reactivation.py` | `Shared: projects/n8n_email_ai_migration_backup_20260809/app/run_daily_reactivation.py` | Setup path | 0 |
| **Базовый** | `run_daily_reactivation.py` | `Shared: projects/n8n_email_ai_funnel_version/app/run_daily_reactivation.py` | Setup path | 0 |
| **Базовый** | `run_daily_reactivation.py` | `Shared: projects/n8n_email_ai_backup/app/run_daily_reactivation.py` | Setup path | 0 |
| **Базовый** | `run_daily_reactivation.py` | `Shared: projects/n8n_email_ai/app/run_daily_reactivation.py` | Setup path | 0 |
| **Расширенный** | `bitrix_golden_phrases.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/bitrix_golden_phrases.py` | Setup path | 4 |
| **Диагностический** | `test_pilot_reactivation.py` | `Shared: projects/n8n_email_ai_v6_backup/scripts/test_pilot_reactivation.py` | Setup path | 1 |
| **Диагностический** | `test_pilot_reactivation.py` | `Shared: projects/n8n_email_ai_v6_backup/archive/backup_20260805_v4plus/test_pilot_reactivation.py` | Setup path | 4 |
| **Диагностический** | `test_pilot_reactivation.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/test_pilot_reactivation.py` | Setup path | 1 |
| **Диагностический** | `test_pilot_reactivation.py` | `Shared: projects/n8n_email_ai/scripts/test_pilot_reactivation.py` | Setup path | 0 |

---

<a id='idempotent_crm_1c'></a>
## 12. Синхронизация лидов и компаний в 1С и Битрикс24 (Idempotent CRM)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Расширенный** | `patch_n8n.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/patch_n8n.py` | Автоматизация рабочего процесса. | 4 |
| **Расширенный** | `patch_n8n_mode.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/patch_n8n_mode.py` | Автоматизация рабочего процесса. | 4 |
| **Интеграционный** | `reconcile_1c_db.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/reconcile_1c_db.py` | Автоматизация рабочего процесса. | 4 |

---

<a id='tenders_goz'></a>
## 13. Тендеры, АСТ ГОЗ и RAG-пайплайн спецификаций

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `add_error_handling.py` | `Shared: projects/tender-extraction-lab/scratch/add_error_handling.py` | --------------------------------------------------------- 1. Error Trigger & Notify Error | 1 |
| **Базовый** | `base.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tries/base.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `build_full_markdown_artifact.py` | `scripts/build_full_markdown_artifact.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `chanker_gemini_1.py` | `ARCHIVE/GOZ/ACT/_РАЗОБРАНО 13-05/chanker_gemini_1.py` | Улучшенные регулярные выражения (убраны полезные слова из негативных паттернов) Теперь исключаем только реальный юридический мусор, не трогая условия приемки | 1 |
| **Базовый** | `chunks_jsonl_to_xlsx.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/chunks_jsonl_to_xlsx.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `clean_signature.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/Доки и записи/clean_signature.py` | 1. Открываем изображение | 3 |
| **Базовый** | `clean_stamp.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/Доки и записи/clean_stamp.py` | 1. перед всем этим установить  pip install pillow | 3 |
| **Базовый** | `compare_built_vs_gold_19_05.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/compare_built_vs_gold_19_05.py` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `compare_with_gold_19_05.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/compare_with_gold_19_05.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `config.py` | `Shared: projects/tender-extraction-lab/app/core/config.py` | odels | 0 |
| **Базовый** | `copy_from_manifest.ps1` | `projects/tender-extraction-lab/scripts/migration/copy_from_manifest.ps1` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `copy_from_manifest.ps1` | `D:/Soft/Codex Backup/projects/tender-extraction-lab/scripts/migration/copy_from_manifest.ps1` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `count_contacts.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/count_contacts.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `debug_live_site.py` | `projects/tilda_migration/debug_live_site.py` | Disable redirect following to see if there is a redirect print first 500 characters of response HTML | 0 |
| **Базовый** | `debug_live_site.py` | `D:/Soft/Codex Backup/projects/tilda_migration/debug_live_site.py` | Disable redirect following to see if there is a redirect print first 500 characters of response HTML | 0 |
| **Базовый** | `debug_rank_lot_builder.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/debug_rank_lot_builder.py` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `dependencies.py` | `Shared: projects/tender-extraction-lab/app/api/dependencies.py` | Функция для инъекции сервиса обработки документов | 2 |
| **Базовый** | `deploy.sh` | `Shared: projects/tender-extraction-lab/scripts/deploy.sh` | Скрипт автоматического развертывания Tender RAG API | 1 |
| **Базовый** | `document.py` | `Shared: projects/tender-extraction-lab/app/schemas/document.py` | Схема для описания структуры одного чанка | 1 |
| **Базовый** | `document.py` | `Shared: projects/tender-extraction-lab/app/services/document.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `document.py` | `Shared: projects/tender-extraction-lab/app/api/routers/document.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `extract_js_context.py` | `projects/tilda_migration/extract_js_context.py` | print 1000 characters before and after | 0 |
| **Базовый** | `extract_js_context.py` | `D:/Soft/Codex Backup/projects/tilda_migration/extract_js_context.py` | print 1000 characters before and after | 0 |
| **Базовый** | `extract_pdf_text.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/extract_pdf_text.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `extract_sprint_points.py` | `scripts/extract_sprint_points.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `h02__del_date_priority.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tries/h02__del_date_priority.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `h04__del_deadline_clause_boost.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tries/h04__del_deadline_clause_boost.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `h05__del_always_scan_docx_raw.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tries/h05__del_always_scan_docx_raw.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `h06__del_force_fixed_date_from_raw.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tries/h06__del_force_fixed_date_from_raw.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `h07__del_accept_ne_pozdnee_date.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tries/h07__del_accept_ne_pozdnee_date.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `h08__del_raw_fixed_date_override.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tries/h08__del_raw_fixed_date_override.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `h09__del_raw_fixed_date_plus_gate.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tries/h09__del_raw_fixed_date_plus_gate.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `h10__pay_drop_no_responsibility.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tries/h10__pay_drop_no_responsibility.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `health.py` | `Shared: projects/tender-extraction-lab/app/api/routers/health.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `inspect_tables_19_05.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/inspect_tables_19_05.py` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `install_webkit_wsl.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/install_webkit_wsl.ps1` | This script sets up a WSL distribution that will be used to run WebKit. | 1 |
| **Базовый** | `key_manager.py` | `Shared: projects/tender-extraction-lab/app/core/key_manager.py` | Deduplicate while preserving order | 0 |
| **Базовый** | `list_mismatched_lots.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/list_mismatched_lots.py` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `llm_service.py` | `Shared: projects/tender-extraction-lab/app/services/llm_service.py` | Ограничиваем количество чанков (Token-First Vibe Engineering) | 0 |
| **Базовый** | `lot_builder_from_chunks_v1.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/lot_builder_from_chunks_v1.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `lot_chunker_md_v1.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/lot_chunker_md_v1.py` | !/usr/bin/env python3 | 15 |
| **Базовый** | `lot_chunker_v1.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/lot_chunker_v1.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `main.py` | `Shared: projects/tender-extraction-lab/app/main.py` | Подключаем наши роутеры | 1 |
| **Базовый** | `md_chunker.py` | `projects/n8n_email_ai/rag_tools/md_chunker.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `md_chunker.py` | `Shared: projects/n8n_email_ai_funnel_version/50_rag_tools/md_chunker.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `read_docx.py` | `Shared: projects/tender-extraction-lab/scratch/read_docx.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `reinstall_chrome_beta_linux.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_beta_linux.sh` | !/usr/bin/env bash | 1 |
| **Базовый** | `reinstall_chrome_beta_mac.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_beta_mac.sh` | !/usr/bin/env bash | 1 |
| **Базовый** | `reinstall_chrome_beta_win.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_beta_win.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `reinstall_chrome_stable_linux.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_stable_linux.sh` | !/usr/bin/env bash | 1 |
| **Базовый** | `reinstall_chrome_stable_mac.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_stable_mac.sh` | !/usr/bin/env bash | 1 |
| **Базовый** | `reinstall_chrome_stable_win.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_chrome_stable_win.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `reinstall_msedge_beta_linux.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_beta_linux.sh` | !/usr/bin/env bash | 1 |
| **Базовый** | `reinstall_msedge_beta_mac.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_beta_mac.sh` | !/usr/bin/env bash | 1 |
| **Базовый** | `reinstall_msedge_beta_win.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_beta_win.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `reinstall_msedge_dev_linux.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_dev_linux.sh` | !/usr/bin/env bash | 1 |
| **Базовый** | `reinstall_msedge_dev_mac.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_dev_mac.sh` | !/usr/bin/env bash | 1 |
| **Базовый** | `reinstall_msedge_dev_win.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_dev_win.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `reinstall_msedge_stable_linux.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_stable_linux.sh` | !/usr/bin/env bash | 1 |
| **Базовый** | `reinstall_msedge_stable_mac.sh` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_stable_mac.sh` | !/usr/bin/env bash | 1 |
| **Базовый** | `reinstall_msedge_stable_win.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/reinstall_msedge_stable_win.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `retroactive_clean_emails.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/retroactive_clean_emails.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `run_chunker_menu.bat` | `projects/tender-extraction-lab/legacy/old_project/ACT/batch/run_chunker_menu.bat` | Force UTF-8 codepage so cmd.exe parses this file reliably even on RU systems. (File is kept ASCII-only; this mainly protects user input/paths.) | 9 |
| **Базовый** | `run_chunker_menu.bat` | `ARCHIVE/GOZ/ACT/Доки и записи/run_chunker_menu.bat` | Автоматизация рабочего процесса. | 5 |
| **Базовый** | `run_goz_parser.bat` | `projects/tender-extraction-lab/legacy/old_project/ACT/batch/run_goz_parser.bat` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `run_min_context_extractor.bat` | `projects/tender-extraction-lab/legacy/old_project/ACT/batch/run_min_context_extractor.bat` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `run_parsed_folders.bat` | `projects/tender-extraction-lab/legacy/old_project/ACT/batch/run_parsed_folders.bat` | Usage: un_parsed_folders.bat "C:\Users\Artem\Downloads\GOZ\_PYRUN_1905" | 3 |
| **Базовый** | `search_interactions.py` | `projects/tilda_migration/search_interactions.py` | 1. Links | 0 |
| **Базовый** | `search_interactions.py` | `D:/Soft/Codex Backup/projects/tilda_migration/search_interactions.py` | 1. Links | 0 |
| **Базовый** | `show_built_row.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/show_built_row.py` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `show_diff_row.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/show_diff_row.py` | Автоматизация рабочего процесса. | 3 |
| **Базовый** | `smart_parser.py` | `ARCHIVE/GOZ/ACT/Доки и записи/Старые парсеры/smart_parser.py` | Извлекает сырой текст из документов, сохраняя структуру таблиц через пайпы | 1 |
| **Базовый** | `smart_parser_v1.py` | `ARCHIVE/GOZ/ACT/Доки и записи/Старые парсеры/smart_parser_v1.py` | Очищенный точечный список ключевых слов для детального логирования | 1 |
| **Базовый** | `smart_parser_v2.py` | `ARCHIVE/GOZ/ACT/Доки и записи/Старые парсеры/smart_parser_v2.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `tender_min_context_extractor_v1.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tender_min_context_extractor_v1.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `tender_min_context_extractor_v1.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/примеры/tender_min_context_extractor_v1.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `tender_min_context_extractor_v1.py` | `ARCHIVE/GOZ/ACT/тест/_РАЗОБРАНО 19-05/tender_min_context_extractor_v1.py` | !/usr/bin/env python3 | 1 |
| **Базовый** | `tender_min_context_extractor_v1.py` | `ARCHIVE/GOZ/ACT/Доки и записи/довольно хорошие версии/tender_min_context_extractor_v1.py` | !/usr/bin/env python3 | 1 |
| **Базовый** | `tender_min_context_extractor_v1.py` | `ARCHIVE/GOZ/ACT/Доки и записи/Старые парсеры/tender_min_context_extractor_v1.py` | !/usr/bin/env python3 | 1 |
| **Базовый** | `tender_min_context_extractor_v2.py` | `ARCHIVE/GOZ/ACT/Доки и записи/довольно хорошие версии/tender_min_context_extractor_v2.py` | !/usr/bin/env python3 | 1 |
| **Базовый** | `tender_min_context_extractor_vDeep Seek 1.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/Доки и записи/tender_min_context_extractor_vDeep Seek 1.py` | !/usr/bin/env python3 | 3 |
| **Базовый** | `upload_and_activate.py` | `projects/tilda_migration/upload_and_activate.py` | Get relative files/dirs | 0 |
| **Базовый** | `upload_and_activate.py` | `D:/Soft/Codex Backup/projects/tilda_migration/upload_and_activate.py` | Get relative files/dirs | 0 |
| **Расширенный** | `eval_min_context_vs_gold_19_05.py` | `projects/tender-extraction-lab/scripts/eval/eval_min_context_vs_gold_19_05.py` | !/usr/bin/env python3 | 3 |
| **Расширенный** | `eval_min_context_vs_gold_19_05.py` | `ARCHIVE/GOZ/ACT/eval_min_context_vs_gold_19_05.py` | !/usr/bin/env python3 | 2 |
| **Расширенный** | `install_media_pack.ps1` | `ARCHIVE/GOZ/Архив/node_dependencies/node_modules_2026-05-10/playwright-core/bin/install_media_pack.ps1` | check if running on Windows Server | 1 |
| **Расширенный** | `patch_bitrix_url.py` | `Shared: projects/tender-extraction-lab/scratch/patch_bitrix_url.py` | Update URL | 1 |
| **Расширенный** | `patch_deal_creation.py` | `Shared: projects/tender-extraction-lab/scratch/patch_deal_creation.py` | 1. Remove "If Data Extracted" and "Notify No Data" nodes | 1 |
| **Расширенный** | `patch_empty_file_task.py` | `Shared: projects/tender-extraction-lab/scratch/patch_empty_file_task.py` | Автоматизация рабочего процесса. | 1 |
| **Расширенный** | `run_smoke_eval.ps1` | `projects/tender-extraction-lab/scripts/smoke/run_smoke_eval.ps1` | Автоматизация рабочего процесса. | 3 |
| **Расширенный** | `run_smoke_eval.ps1` | `D:/Soft/Codex Backup/projects/tender-extraction-lab/scripts/smoke/run_smoke_eval.ps1` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `tender_lot_parser_v7.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/tender_lot_parser_v7.py` | !/usr/bin/env python3 | 3 |
| **Расширенный** | `tender_lot_parser_v7.py` | `projects/tender-extraction-lab/legacy/old_project/ACT/примеры/tender_lot_parser_v7.py` | !/usr/bin/env python3 | 3 |
| **Расширенный** | `tender_lot_parser_v7.py` | `Shared: projects/tender-extraction-lab/app/services/tender_lot_parser_v7.py` | !/usr/bin/env python3 | 1 |
| **Интеграционный** | `check_n8n_workflows.py` | `Shared: projects/n8n_email_ai_funnel_version/scratch/check_n8n_workflows.py` | Check active workflows | 2 |
| **Интеграционный** | `create_bitrix24_workflow.py` | `Shared: projects/tender-extraction-lab/scratch/create_bitrix24_workflow.py` | Автоматизация рабочего процесса. | 1 |
| **Интеграционный** | `generate_v2_1_leads_and_contacts_params_workflow.ps1` | `projects/n8n_email_ai/scripts/generate_v2_1_leads_and_contacts_params_workflow.ps1` | Автоматизация рабочего процесса. | 1 |
| **Интеграционный** | `generate_v2_1_leads_and_contacts_params_workflow.ps1` | `ARCHIVE/n8n_email_ai_2026-05-11/scripts/generate_v2_1_leads_and_contacts_params_workflow.ps1` | Автоматизация рабочего процесса. | 9 |
| **Интеграционный** | `merge_workflows.py` | `Shared: projects/tender-extraction-lab/scratch/merge_workflows.py` | 1. Start with ingest webhook, but add splitting logic | 1 |
| **Интеграционный** | `run_matrix_onlylot.py` | `projects/tender-extraction-lab/scripts/batch/run_matrix_onlylot.py` | !/usr/bin/env python3 | 3 |
| **Интеграционный** | `run_matrix_onlylot.py` | `ARCHIVE/GOZ/ACT/tries/run_matrix_onlylot.py` | !/usr/bin/env python3 | 2 |
| **Диагностический** | `load_test.py` | `Shared: projects/tender-extraction-lab/scratch/load_test.py` | Автоматизация рабочего процесса. | 1 |

---

<a id='infra_vps'></a>
## 14. Инфраструктура, VPS-сервер, Docker и Бэкапы

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `FULL_moz_internal_linking_report.py` | `projects/GoW Project/FULL_moz_internal_linking_report.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `FULL_moz_internal_linking_report.py` | `D:/Soft/Codex Backup/projects/GoW Project/FULL_moz_internal_linking_report.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `analyze_all_details.py` | `scripts/analyze_all_details.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `analyze_forms.py` | `projects/tilda_migration/analyze_forms.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `analyze_forms.py` | `D:/Soft/Codex Backup/projects/tilda_migration/analyze_forms.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `analyze_sprint.py` | `scripts/analyze_sprint.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `apply_final_fixes.py` | `projects/tilda_migration/apply_final_fixes.py` | FTP Config | 0 |
| **Базовый** | `apply_final_fixes.py` | `D:/Soft/Codex Backup/projects/tilda_migration/apply_final_fixes.py` | FTP Config | 0 |
| **Базовый** | `audit_archived_transcripts.py` | `scripts/audit_archived_transcripts.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `budget_enforcer.py` | `scripts/budget_enforcer.py` | ates per 1M tokens | 0 |
| **Базовый** | `budget_enforcer.py` | `Shared: scripts/budget_enforcer.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `budget_enforcer.py` | `D:/Soft/Codex Backup/scripts/budget_enforcer.py` | ates per 1M tokens | 0 |
| **Базовый** | `compare_projects.ps1` | `scratch/compare_projects.ps1` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_snapshots.ps1` | `projects/local_inventory/inventory/compare_snapshots.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `compare_snapshots.ps1` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/compare_snapshots.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `compare_vtb.py` | `projects/GoW Project/compare_vtb.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `compare_vtb.py` | `D:/Soft/Codex Backup/projects/GoW Project/compare_vtb.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `create_theme.py` | `projects/tilda_migration/create_theme.py` | Load resource mapping | 0 |
| **Базовый** | `create_theme.py` | `D:/Soft/Codex Backup/projects/tilda_migration/create_theme.py` | Load resource mapping | 0 |
| **Базовый** | `deep_analysis.py` | `scripts/deep_analysis.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `deep_sprint_reviewer.py` | `scripts/deep_sprint_reviewer.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `deploy_files.ps1` | `Shared: scratch/deploy_files.ps1` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `download_project_specific_assets.py` | `projects/tilda_migration/download_project_specific_assets.py` | FTP Config | 0 |
| **Базовый** | `download_project_specific_assets.py` | `D:/Soft/Codex Backup/projects/tilda_migration/download_project_specific_assets.py` | FTP Config | 0 |
| **Базовый** | `download_resources.py` | `projects/tilda_migration/download_resources.py` | Paths | 0 |
| **Базовый** | `download_resources.py` | `D:/Soft/Codex Backup/projects/tilda_migration/download_resources.py` | Paths | 0 |
| **Базовый** | `download_vps_backup.ps1` | `scripts/download_vps_backup.ps1` | Конфигурация | 1 |
| **Базовый** | `dump_chat_md.py` | `scripts/dump_chat_md.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `explore_htdocs.py` | `projects/tilda_migration/explore_htdocs.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `explore_htdocs.py` | `D:/Soft/Codex Backup/projects/tilda_migration/explore_htdocs.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `explore_www.py` | `projects/tilda_migration/explore_www.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `explore_www.py` | `D:/Soft/Codex Backup/projects/tilda_migration/explore_www.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `export_installed_programs.ps1` | `projects/local_inventory/inventory/export_installed_programs.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `export_installed_programs.ps1` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/export_installed_programs.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `export_sprint_chat.py` | `scripts/export_sprint_chat.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `find_biohim.py` | `projects/tilda_migration/find_biohim.py` | Search for "БИОХИМ" or "biohim" | 0 |
| **Базовый** | `find_biohim.py` | `D:/Soft/Codex Backup/projects/tilda_migration/find_biohim.py` | Search for "БИОХИМ" or "biohim" | 0 |
| **Базовый** | `find_endpoints_in_dashboard.py` | `projects/tilda_migration/find_endpoints_in_dashboard.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_endpoints_in_dashboard.py` | `D:/Soft/Codex Backup/projects/tilda_migration/find_endpoints_in_dashboard.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_footer_elements.py` | `projects/tilda_migration/find_footer_elements.py` | Let's look at elements inside the footer or bottom of the page We can find all elements with classes containing 'rec' at the end | 0 |
| **Базовый** | `find_footer_elements.py` | `D:/Soft/Codex Backup/projects/tilda_migration/find_footer_elements.py` | Let's look at elements inside the footer or bottom of the page We can find all elements with classes containing 'rec' at the end | 0 |
| **Базовый** | `find_live_footer_imgs.py` | `projects/tilda_migration/find_live_footer_imgs.py` | Find all images in the document and print the last few | 0 |
| **Базовый** | `find_live_footer_imgs.py` | `D:/Soft/Codex Backup/projects/tilda_migration/find_live_footer_imgs.py` | Find all images in the document and print the last few | 0 |
| **Базовый** | `find_live_footer_logo.py` | `projects/tilda_migration/find_live_footer_logo.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_live_footer_logo.py` | `D:/Soft/Codex Backup/projects/tilda_migration/find_live_footer_logo.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_more_paths.py` | `projects/tilda_migration/find_more_paths.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_more_paths.py` | `D:/Soft/Codex Backup/projects/tilda_migration/find_more_paths.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `fix_icons_and_footer.py` | `projects/tilda_migration/fix_icons_and_footer.py` | FTP Config | 0 |
| **Базовый** | `fix_icons_and_footer.py` | `D:/Soft/Codex Backup/projects/tilda_migration/fix_icons_and_footer.py` | FTP Config | 0 |
| **Базовый** | `generate_readable_review.py` | `scripts/generate_readable_review.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `inspect_days_6_7_cost.py` | `scripts/inspect_days_6_7_cost.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `inspect_form_html.py` | `projects/tilda_migration/inspect_form_html.py` | print first 3000 chars of block HTML | 0 |
| **Базовый** | `inspect_form_html.py` | `D:/Soft/Codex Backup/projects/tilda_migration/inspect_form_html.py` | print first 3000 chars of block HTML | 0 |
| **Базовый** | `inspect_forms_detail.py` | `projects/tilda_migration/inspect_forms_detail.py` | Let's find all divs with class 't-form' | 0 |
| **Базовый** | `inspect_forms_detail.py` | `D:/Soft/Codex Backup/projects/tilda_migration/inspect_forms_detail.py` | Let's find all divs with class 't-form' | 0 |
| **Базовый** | `inspect_images.py` | `projects/tilda_migration/inspect_images.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_images.py` | `D:/Soft/Codex Backup/projects/tilda_migration/inspect_images.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_reports_detail.py` | `scripts/inspect_reports_detail.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `inventory.py` | `config/infra_management/scripts/inventory.py` | Configuration | 1 |
| **Базовый** | `inventory_common.ps1` | `projects/local_inventory/inventory/inventory_common.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `inventory_common.ps1` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/inventory_common.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `inventory_config.ps1` | `projects/local_inventory/inventory/inventory_config.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `inventory_config.ps1` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/inventory_config.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `llm_service.py` | `Shared: projects/n8n_email_ai_v6_backup/archive/backup_20260805_v4plus/llm_service.py` | Автоматизация рабочего процесса. | 4 |
| **Базовый** | `llm_service.py` | `Shared: projects/n8n_email_ai_v6_backup/app/services/llm_service.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `llm_service.py` | `Shared: projects/n8n_email_ai_migration_backup_20260809/app/services/llm_service.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `llm_service.py` | `Shared: projects/n8n_email_ai_backup/app/services/llm_service.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `make_snapshot.ps1` | `projects/local_inventory/inventory/make_snapshot.ps1` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `make_snapshot.ps1` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/make_snapshot.ps1` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `models.py` | `Shared: projects/n8n_email_ai_v6_backup/app/db/models.py` | Автоматизация рабочего процесса. | 2 |
| **Базовый** | `monitor_disk.sh` | `Shared: scratch/monitor_disk.sh` | Скрипт мониторинга дисков с уведомлением в Битрикс24 | 0 |
| **Базовый** | `moz_internal_linking_report.py` | `projects/GoW Project/moz_internal_linking_report.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `moz_internal_linking_report.py` | `D:/Soft/Codex Backup/projects/GoW Project/moz_internal_linking_report.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `n8n-sqlite-auto-vacuum.sh` | `scripts/vps/n8n-sqlite-auto-vacuum.sh` | Еженедельное автоматическое обслуживание и сжатие SQLite баз данных n8n и n8n-eng Размещается в /usr/local/bin/n8n-sqlite-auto-vacuum.sh и связывается с /etc/cron.weekly/ | 0 |
| **Базовый** | `parse_days_detail.py` | `scripts/parse_days_detail.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `parse_js.py` | `projects/tilda_migration/parse_js.py` | Let's search for URLs or api endpoints | 0 |
| **Базовый** | `parse_js.py` | `D:/Soft/Codex Backup/projects/tilda_migration/parse_js.py` | Let's search for URLs or api endpoints | 0 |
| **Базовый** | `rename_assets_and_title.py` | `projects/tilda_migration/rename_assets_and_title.py` | FTP Config | 0 |
| **Базовый** | `rename_assets_and_title.py` | `D:/Soft/Codex Backup/projects/tilda_migration/rename_assets_and_title.py` | FTP Config | 0 |
| **Базовый** | `run_server_backup_new.sh` | `Shared: scratch/run_server_backup_new.sh` | Скрипт полного бэкапа и автоматического обслуживания SQLite | 0 |
| **Базовый** | `tilda_fetch_all_projects_pages.py` | `projects/tilda_migration/tilda_fetch_all_projects_pages.py` | 1. Get projects list | 0 |
| **Базовый** | `tilda_fetch_all_projects_pages.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_fetch_all_projects_pages.py` | 1. Get projects list | 0 |
| **Базовый** | `tilda_fetch_pages_json.py` | `projects/tilda_migration/tilda_fetch_pages_json.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_pages_json.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_fetch_pages_json.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_project_details.py` | `projects/tilda_migration/tilda_fetch_project_details.py` | Try POST | 0 |
| **Базовый** | `tilda_fetch_project_details.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_fetch_project_details.py` | Try POST | 0 |
| **Базовый** | `tilda_fetch_project_pages.py` | `projects/tilda_migration/tilda_fetch_project_pages.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_project_pages.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_fetch_project_pages.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_projects_json.py` | `projects/tilda_migration/tilda_fetch_projects_json.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_projects_json.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_fetch_projects_json.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_get_preview.py` | `projects/tilda_migration/tilda_get_preview.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_get_preview.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_get_preview.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_guess_endpoints.py` | `projects/tilda_migration/tilda_guess_endpoints.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_guess_endpoints.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_guess_endpoints.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_list_projects.py` | `projects/tilda_migration/tilda_list_projects.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_list_projects.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_list_projects.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_session.py` | `projects/tilda_migration/tilda_session.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_session.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_session.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `try_submit_login.py` | `projects/tilda_migration/try_submit_login.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `try_submit_login.py` | `D:/Soft/Codex Backup/projects/tilda_migration/try_submit_login.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `update_form_js.py` | `projects/tilda_migration/update_form_js.py` | FTP Config | 0 |
| **Базовый** | `update_form_js.py` | `D:/Soft/Codex Backup/projects/tilda_migration/update_form_js.py` | FTP Config | 0 |
| **Базовый** | `vps_server_backup.sh` | `Shared: projects/n8n_email_ai_v6_backup/scripts/vps_server_backup.sh` | 1. pg_dump of marketing_db from docker container | 2 |
| **Базовый** | `watch_and_download_backup.ps1` | `scripts/watch_and_download_backup.ps1` | Configuration | 1 |
| **Базовый** | `zip_theme.py` | `projects/tilda_migration/zip_theme.py` | Compute relative path in ZIP (should start with qilin-theme/) | 0 |
| **Базовый** | `zip_theme.py` | `D:/Soft/Codex Backup/projects/tilda_migration/zip_theme.py` | Compute relative path in ZIP (should start with qilin-theme/) | 0 |
| **Расширенный** | `AI chats filter.py` | `D:/Soft/Codex Backup/ARCHIVE/Архивы чатов ИИ/AI chats filter.py` | ========================================== ========================================== | 0 |
| **Расширенный** | `build_sprint_evaluation.py` | `scripts/build_sprint_evaluation.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `check_broken_links.py` | `projects/tilda_migration/check_broken_links.py` | 1. Stylesheets | 0 |
| **Расширенный** | `check_broken_links.py` | `D:/Soft/Codex Backup/projects/tilda_migration/check_broken_links.py` | 1. Stylesheets | 0 |
| **Расширенный** | `check_content.py` | `projects/tilda_migration/check_content.py` | Print page title | 0 |
| **Расширенный** | `check_content.py` | `D:/Soft/Codex Backup/projects/tilda_migration/check_content.py` | Print page title | 0 |
| **Расширенный** | `check_dns.py` | `projects/tilda_migration/check_dns.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_dns.py` | `D:/Soft/Codex Backup/projects/tilda_migration/check_dns.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_form_tag.py` | `projects/tilda_migration/check_form_tag.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_form_tag.py` | `D:/Soft/Codex Backup/projects/tilda_migration/check_form_tag.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_public_site.py` | `projects/tilda_migration/check_public_site.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_public_site.py` | `D:/Soft/Codex Backup/projects/tilda_migration/check_public_site.py` | Автоматизация рабочего процесса. | 0 |
| **Интеграционный** | `mass_replace.py` | `config/infra_management/scripts/mass_replace.py` | Configuration | 1 |
| **Диагностический** | `open_latest_report.bat` | `projects/local_inventory/inventory/open_latest_report.bat` | Автоматизация рабочего процесса. | 1 |
| **Диагностический** | `open_latest_report.bat` | `ARCHIVE/bootstrap_snapshot_2026-05-30/projects/local_inventory/inventory/open_latest_report.bat` | Автоматизация рабочего процесса. | 2 |
| **Диагностический** | `preflight.py` | `scripts/preflight.py` | Fallback token estimator if tiktoken is not installed Fallback estimation: | 0 |
| **Диагностический** | `preflight.py` | `Shared: scripts/preflight.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `preflight.py` | `D:/Soft/Codex Backup/scripts/preflight.py` | Fallback token estimator if tiktoken is not installed Fallback estimation: | 0 |
| **Диагностический** | `test_all_keys_vps.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/diagnostics/test_all_keys_vps.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `test_ftp.py` | `projects/tilda_migration/test_ftp.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_ftp.py` | `D:/Soft/Codex Backup/projects/tilda_migration/test_ftp.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_vps_curl.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/diagnostics/test_vps_curl.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `test_vps_proxy.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/diagnostics/test_vps_proxy.py` | Force DNS resolution to 87.228.47.204 for Python urllib We do this by modifying the HTTP request host to the IP and setting Host header | 4 |
| **Диагностический** | `test_vps_sdk.py` | `Shared: projects/n8n_email_ai_funnel_version/scripts/diagnostics/test_vps_sdk.py` | Автоматизация рабочего процесса. | 4 |
| **Диагностический** | `tilda_auth_test.py` | `projects/tilda_migration/tilda_auth_test.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `tilda_auth_test.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_auth_test.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `tilda_test_projects_param.py` | `projects/tilda_migration/tilda_test_projects_param.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `tilda_test_projects_param.py` | `D:/Soft/Codex Backup/projects/tilda_migration/tilda_test_projects_param.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `verify.py` | `config/infra_management/scripts/verify.py` | Configuration | 1 |

---
