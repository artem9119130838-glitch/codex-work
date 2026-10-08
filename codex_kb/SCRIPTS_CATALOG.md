# Единый каталог скриптов и автоматизаций контура (SCRIPTS_CATALOG)

> **Дата последней автоматической ревизии:** `2026-09-30 11:04:52`  
> **Статус контура:** Компактный индекс активных скриптов контура | Полный архив внешних бэкапов: [DEEP_LEGACY_SCRIPTS_CATALOG.md](file:///C:/Codex/codex_kb/archive/DEEP_LEGACY_SCRIPTS_CATALOG.md).
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
- [15. Сквозная бизнес-аналитика и Metabase BI (DWH)](#metabase_analytics)

---

<a id='ai_chats'></a>
## 1. Выгрузка, парсинг и фильтрация чатов ИИ (Gemini / ChatGPT / Claude)

> *Все исторические утилиты этого домена перенесены в глубокий архив [DEEP_LEGACY_SCRIPTS_CATALOG.md](file:///C:/Codex/codex_kb/archive/DEEP_LEGACY_SCRIPTS_CATALOG.md).*

---

## 2. Снабжение и ВЭД в Китае (Дечжоу / Циндао, фонд 5000 RMB, возврат НДС)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Расширенный** | `generate_supply_rfq_excel.py` | `projects/1c_odata/scripts/generate_supply_rfq_excel.py` | База готовых спецификаций по подтвержденным заявкам (наработки из архива) | 0 |
| **Интеграционный** | `hydramax_dispute_manager.py` | `scripts/hydramax_dispute_manager.py` | Единый комплекс управления документацией по спору ООО «Ци Линь» / ООО «Логистиктранс»: генерация ТЗ юристу (`--action brief`), аналитических писем Дэвиду по трубам (`--action letter-tubes`), стоп-предписания по штокам (`--action letter-rods`), инспекция чертежей (`--action inspect-drawing`), постраничный экспорт CamScanner PDF (`--action extract-pdf`) и перевод таблицы приемки штоков на английский с сохранением форматирования (`--action translate-rods-table`) | 0 |

---

<a id='price_creating'></a>
## 3. Создание прайс-листов и коммерческих предложений из каталогов

> *Все исторические утилиты этого домена перенесены в глубокий архив [DEEP_LEGACY_SCRIPTS_CATALOG.md](file:///C:/Codex/codex_kb/archive/DEEP_LEGACY_SCRIPTS_CATALOG.md).*

---

## 4. Анализ резюме, RAG-база кандидатов и генерация ответов соискателям

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `build_candidates_rag_db.py` | `projects/HR/build_candidates_rag_db.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `generate_three_letters.py` | `scripts/generate_three_letters.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `scratch_parse_resumes.py` | `projects/HR/scratch_parse_resumes.py` | ow 2 contains actual column headers | 0 |
| **Базовый** | `scratch_print_all.py` | `projects/HR/scratch_print_all.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_clean_digits.py` | `projects/HR/search_clean_digits.py` | ove spaces and punctuation | 0 |
| **Расширенный** | `create_candidates_excel.py` | `projects/HR/create_candidates_excel.py` | Sheet 1: Candidates list | 0 |
| **Расширенный** | `scratch_check_specific.py` | `projects/HR/scratch_check_specific.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `scratch_filter_notes.py` | `projects/HR/scratch_filter_notes.py` | Автоматизация рабочего процесса. | 1 |

---

<a id='pc_migration'></a>
## 5. Перенос данных с ПК на ПК (HP Victus ⮂ MateBook ⮂ Mirror_E_Home)

> *Все исторические утилиты этого домена перенесены в глубокий архив [DEEP_LEGACY_SCRIPTS_CATALOG.md](file:///C:/Codex/codex_kb/archive/DEEP_LEGACY_SCRIPTS_CATALOG.md).*

---

## 6. Спринты Михаила, RAG ГОЗ и Архитектура сети VPS

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `add_wait_node.py` | `C:/Users/Артем/tender-rag-api/scratch/add_wait_node.py` | Create the Wait node | 0 |
| **Базовый** | `audit_db.py` | `C:/Users/Артем/tender-rag-api/scratch/audit_db.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `config.py` | `C:/Users/Артем/tender-rag-api/app/core/config.py` | odels | 0 |
| **Базовый** | `cost_calculator.py` | `C:/Users/Артем/tender-rag-api/app/services/cost_calculator.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `cost_schema.py` | `C:/Users/Артем/tender-rag-api/app/schemas/cost_schema.py` | Модель для расчета себестоимости одной товарной позиции из Китая. | 0 |
| **Базовый** | `deploy_metabase_analytics.py` | `C:/Users/Артем/tender-rag-api/scripts/deploy_metabase_analytics.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `disable_deepseek.py` | `C:/Users/Артем/tender-rag-api/scripts/disable_deepseek.py` | place body of _call_deepseek | 0 |
| **Базовый** | `document.py` | `C:/Users/Артем/tender-rag-api/app/api/routers/document.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `fix_n8n_auth.py` | `C:/Users/Артем/tender-rag-api/scripts/fix_n8n_auth.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `fix_n8n_final.py` | `C:/Users/Артем/tender-rag-api/scripts/fix_n8n_final.py` | Fix URLs to include the webhook token | 0 |
| **Базовый** | `fix_n8n_task.py` | `C:/Users/Артем/tender-rag-api/scripts/fix_n8n_task.py` | Fix nomenclature Fix User IDs | 0 |
| **Базовый** | `force_worker_dir.py` | `C:/Users/Артем/tender-rag-api/force_worker_dir.py` | Add root to pythonpath | 0 |
| **Базовый** | `generate_backfill_sql.py` | `C:/Users/Артем/tender-rag-api/analytics/scripts/generate_backfill_sql.py` | Загружаем переменные окружения | 0 |
| **Базовый** | `import_white_base.py` | `C:/Users/Артем/tender-rag-api/scripts/import_white_base.py` | Build paths relative to the project root | 0 |
| **Базовый** | `key_manager.py` | `C:/Users/Артем/tender-rag-api/app/core/key_manager.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `llm_service.py` | `C:/Users/Артем/tender-rag-api/app/services/llm_service.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `logger.py` | `C:/Users/Артем/tender-rag-api/app/core/logger.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `rabbitmq.py` | `C:/Users/Артем/tender-rag-api/app/core/rabbitmq.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `read_docx.py` | `C:/Users/Артем/tender-rag-api/scratch/read_docx.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `rewrite_nomenclature.py` | `C:/Users/Артем/tender-rag-api/scripts/rewrite_nomenclature.py` | Find the extract_nomenclature_from_tables function and replace it | 0 |
| **Базовый** | `setup_bitrix_fields.py` | `C:/Users/Артем/tender-rag-api/scripts/setup_bitrix_fields.py` | Список нужных полей | 0 |
| **Базовый** | `tender_worker.py` | `C:/Users/Артем/tender-rag-api/app/workers/tender_worker.py` | Для тестов по умолчанию стучимся на локальный мок-сервер 5001, а на бою - в n8n | 0 |
| **Базовый** | `update_docs.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs.py` | Update PROGRESS.md | 0 |
| **Базовый** | `update_docs_chat.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs_chat.py` | Update PROGRESS.md | 0 |
| **Базовый** | `update_docs_heuristic.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs_heuristic.py` | 1. Update PROGRESS.md | 0 |
| **Базовый** | `update_docs_report.py` | `C:/Users/Артем/tender-rag-api/scratch/update_docs_report.py` | 1. Update PROGRESS.md Update (2026-07-15) | 0 |
| **Базовый** | `update_summary_fields.py` | `C:/Users/Артем/tender-rag-api/scratch/update_summary_fields.py` | Update Get Deals node | 0 |
| **Базовый** | `ved_audit_service.py` | `C:/Users/Артем/tender-rag-api/app/services/ved_audit_service.py` | Generate embedding using Gemini API with KeyManager rotation. | 0 |
| **Расширенный** | `b24_daily_analytics_sync.py` | `C:/Users/Артем/tender-rag-api/scripts/b24_daily_analytics_sync.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `check_gemini_models.py` | `C:/Users/Артем/tender-rag-api/scripts/check_gemini_models.py` | Get API key from .env.local | 0 |
| **Расширенный** | `nomenclature_parser.py` | `C:/Users/Артем/tender-rag-api/app/services/nomenclature_parser.py` | Checks if a filename likely contains nomenclature. | 0 |
| **Расширенный** | `patch_error_node.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_error_node.py` | Find the node that creates the error task (we can identify it by looking at its parameters) Update the description to include the detailed description field | 0 |
| **Расширенный** | `patch_headers.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_headers.py` | Inject headers | 0 |
| **Расширенный** | `patch_metabase.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_metabase.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `patch_n8n_chat.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_n8n_chat.py` | Update parameters | 0 |
| **Расширенный** | `patch_n8n_deal.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_n8n_deal.py` | ap old codes to new codes | 0 |
| **Расширенный** | `patch_remove_postgres.py` | `C:/Users/Артем/tender-rag-api/scratch/patch_remove_postgres.py` | ove the node named "Insert to Postgres" | 0 |
| **Интеграционный** | `patch_n8n_workflow.py` | `C:/Users/Артем/tender-rag-api/scripts/patch_n8n_workflow.py` | 1. Update workflow name | 0 |
| **Диагностический** | `generate_sql.py` | `C:/Users/Артем/tender-rag-api/analytics/tests/generate_sql.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `load_bulk_csv.py` | `C:/Users/Артем/tender-rag-api/analytics/tests/load_bulk_csv.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `load_test_data.py` | `C:/Users/Артем/tender-rag-api/analytics/tests/load_test_data.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `setup_metabase.py` | `C:/Users/Артем/tender-rag-api/analytics/tests/setup_metabase.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_folder.py` | `C:/Users/Артем/tender-rag-api/scratch/test_folder.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_health.py` | `C:/Users/Артем/tender-rag-api/scratch/test_health.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_local_db.py` | `C:/Users/Артем/tender-rag-api/analytics/tests/test_local_db.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `test_models.py` | `C:/Users/Артем/tender-rag-api/scripts/test_models.py` | Автоматизация рабочего процесса. | 0 |

---

<a id='windows_diagnostics'></a>
## 7. Windows Diagnostics, графика Victus 16, Safe Mode и дисплеи

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `fix_acrobat_genuine.ps1` | `scripts/fix_acrobat_genuine.ps1` | fix_acrobat_genuine.ps1 Comprehensive Adobe Acrobat Genuine & Deactivation Popup Eliminator | 0 |
| **Расширенный** | `check_and_clean_pc.py` | `scripts/check_and_clean_pc.py` | !/usr/bin/env python3 | 0 |

---

<a id='session_compression'></a>
## 8. Анализ истории чата, сжатие сессий и /learn

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `build_index.py` | `scripts/build_index.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `full_gravity_audit.py` | `scripts/full_gravity_audit.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `parse_sprint_summary.py` | `scripts/parse_sprint_summary.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `session_compress.py` | `scripts/session_compress.py` | Определяем корневую директорию проекта на основе расположения скрипта скрипт лежит в <root>/scripts/session_compress.py | 0 |

---

<a id='onec_bitrix_sync'></a>
## 9. Связка 1С:УНФ и Битрикс24 (OData, Контрагенты, Заказы, СКД)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `create_1c_lead.py` | `projects/1c_odata/scripts/create_1c_lead.py` | Dry-run создания нового лида с привязкой к событию: | 0 |
| **Базовый** | `process_deals_without_activities.py` | `projects/1c_odata/scripts/process_deals_without_activities.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `process_today_followup_deals.py` | `projects/1c_odata/scripts/process_today_followup_deals.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `scratch_b24_fetch.py` | `projects/HR/scratch_b24_fetch.py` | Автоматизация рабочего процесса. | 1 |
| **Базовый** | `search_1c_entities.py` | `projects/1c_odata/scripts/search_1c_entities.py` | Быстрый сквозной поиск сущностей в базе 1С:УНФ через OData API без расхода токенов | 0 |
| **Базовый** | `search_bitrix_knowledge.py` | `projects/1c_odata/scripts/search_bitrix_knowledge.py` | Канонический конвейер интеллектуального поиска знаний, задач, созвонов, чатов и протоколов в Битрикс24 по нечетким запросам (`--query`, `--users`, `--task-id`, `--chat-id`) | 0 |
| **Расширенный** | `sync_leads_1c_bitrix.py` | `projects/1c_odata/scripts/sync_leads_1c_bitrix.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `sync_to_bitrix.py` | `projects/1c_odata/scripts/sync_to_bitrix.py` | Автоматизация рабочего процесса. | 1 |

---

<a id='lead_inbound'></a>
## 10. Обработка новых лидов и Inbound-снабжение (Email AI Pipeline)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `fetch_email_8071.py` | `scratch/fetch_email_8071.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `search_imap.py` | `scratch/search_imap.py` | Автоматизация рабочего процесса. | 0 |
| **Интеграционный** | `process_b24_inbound_leads.py` | `projects/1c_odata/scripts/process_b24_inbound_leads.py` | Канонический боевой конвейер обработки входящих лидов CRM Битрикс24 и синхронизации с 1С:УНФ: аргументы `--csv`, `--leads`, `--lead-id`, `--repair-lead`, `--limit`, `--deadline-today`, `--no-reply`, `--force`, `--dry-run`; ветвление Clear RFQ / Ambiguous, Reseller & Ghost RFQ Guard, OEM Real Sector Exemption, Single Deal & Single Task Invariant, создание сделки в стадии `PREPARATION` («Расчет КП»), задачи снабженцу Азату (`user/20`) в проекте 14 с дедлайном сегодня к 18:00 или +4 раб. дня, Triple Activity Binding Guard (тройная привязка дел к Сделке, Контакту, Компании и retargeting COMMUNICATIONS), Email Signature Phone & Details Parser (извлечение телефонов, доб. и должностей из подписи email), Procurement RFQ Specification Engine (заполнение DESCRIPTION задачи полным ТЗ, количеством, допустимостью аналогов и оригинальным текстом клиента; Anti-Phantom Attachment Guard — запрет фиктивных ссылок на файлы при их отсутствии), Result Self-Check Guard (авто-проверка привязки писем, телефонов и ТЗ), каскадный поиск сущностей Multi-Key Cascade Lookup, сквозной СБИС/DaData скоринг, отсев реквизитов РФ по Attachment Hygiene Guard | 0 |
| **Интеграционный** | `process_deals_batch_azat.py` | `projects/1c_odata/scripts/process_deals_batch_azat.py` | Пакетная квалификация созданных сделок, перевод в стадию `PREPARATION` («Расчет КП»), постановка задач снабженцу Азату (`user/20`) со сроком на сегодня к 18:00, генерация и загрузка Excel-спецификаций и оригинальных файлов клиента по регламенту Full RFQ Attachment Guard (`--dry-run`, `--execute`, `--deal-id`) | 0 |

---

<a id='followup_sales'></a>
## 11. Follow-up продаж в сделках и реактивация клиентов

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Канонический** | `update_website_knowledge_index.py` | `projects/lead_reactivation/scripts/update_website_knowledge_index.py` | Автоматический краулер и актуализатор базы знаний: сбор страниц `/useful-articles/` и `/projects/` с сайта longwang.ru, извлечение Title, H1, Description, обновление `96_articles_index.md`. Поддерживает `--dry-run`. | 0 |
| **Канонический** | `run_daily_reactivation.py` | `projects/lead_reactivation/scripts/run_daily_reactivation.py` | Двухпоточный конвейер 6-шаговой воронки реанимации клиентов 1С: Поток 1 (активные воронки, шаги 2–6 с кулдауном 21 день, `--active-limit`); Поток 2 (новые контакты 1С, шаг 1, `--limit`, общесуточный `--max-daily-drafts`). Включает Intent Classification Gate (блокировка воронки при наличии заказов/доставки), Quality Gate (отсечение КП старше 45 дней, анти-тавтология, запрет B2C-скидок 10%), защиту от писем соискателям (HRGuard), кулдаун компаний и переключение на DeepSeek. | 0 |

---

<a id='idempotent_crm_1c'></a>
## 12. Синхронизация лидов и компаний в 1С и Битрикс24 (Idempotent CRM)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Канонический** | `check_contractor.py` | `projects/1c_odata/scripts/check_contractor.py` | Единый модуль комплексной проверки и обогащения досье контрагента по ИНН (DaData API + Saby/СБИС RPC). Автоматическая классификация: Выручка, Масштаб бизнеса, ОКВЭД, Тендеры (Поставщик/Заказчик), Холдинг, Вердикт ИИ (Перепродажник/Завод/Конечник). Синхронная запись в marketing_db, Битрикс24 (COMMENTS + закрепленный комментарий таймлайна) и 1С:УНФ (Комментарий + теги) с проверкой кэша (`is_contractor_already_verified`). | 0 |
| **Канонический** | `sync_leads_1c_bitrix.py` | `projects/1c_odata/scripts/sync_leads_1c_bitrix.py` | Сквозная синхронизация лидов 1С:УНФ и Битрикс24 (Zero-Blank Lead Guard) + синхронизация из выгрузок 1С (.mxl, аргумент `--mxl`) + Tag Integrity Guard & Repair (`--audit-tags`/`--fix-tags`, автозамена опечатки 7e8d7ab6 -> 7e8d7ab8) + Bounce & Unsubscribe Guard (`--clean-email`) + авто-обогащение через СБИС/DaData (`check_contractor.py`). Поддерживает `--dry-run`. | 0 |


---

<a id='tenders_goz'></a>
## 13. Тендеры, АСТ ГОЗ и RAG-пайплайн спецификаций

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Базовый** | `build_full_markdown_artifact.py` | `scripts/build_full_markdown_artifact.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `extract_sprint_points.py` | `scripts/extract_sprint_points.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `find_mail.py` | `scratch/find_mail.py` | Let's search activities where SUBJECT, DESCRIPTION, or COMMUNICATIONS contain '315' or 'liderair' | 0 |
| **Базовый** | `search_interactions.py` | `projects/tilda_migration/search_interactions.py` | 1. Links | 0 |
| **Базовый** | `upload_and_activate.py` | `projects/tilda_migration/upload_and_activate.py` | Get relative files/dirs | 0 |
| **Расширенный** | `check_file_and_acts.py` | `scratch/check_file_and_acts.py` | Let's check disk or file 107738 | 0 |

---

<a id='infra_vps'></a>
## 14. Инфраструктура, VPS-сервер, Docker и Бэкапы

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Канонический** | `keenetic_manager.py` | `scripts/keenetic_manager.py` | Комплексный аудит и CLI-управление роутером Keenetic Hero 4G (RCI API): статусы интерфейсов WAN/Wireguard1, инвентаризация и статусы хостов локальной сети, аудит политик маршрутизации и DoH/DoT DNS-прокси, пинг через туннели | 0 |
| **Базовый** | `analyze_all_details.py` | `scripts/analyze_all_details.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `analyze_forms.py` | `projects/tilda_migration/analyze_forms.py` | Автоматизация рабочего процесса. | 0 |
| **Канонический** | `mine_crm_incidents.py` | `scripts/mine_crm_incidents.py` | Канонический инструмент аудита чатов и сбора инцидентов Битрикс24 (Incident Miner) | 0 |
| **Базовый** | `apply_final_fixes.py` | `projects/tilda_migration/apply_final_fixes.py` | FTP Config | 0 |
| **Базовый** | `audit_archived_transcripts.py` | `scripts/audit_archived_transcripts.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `audit_c_drive_bloat.py` | `scripts/audit_c_drive_bloat.py` | UTF-8 encoding | 0 |
| **Базовый** | `audit_save_and_softe.py` | `scripts/audit_save_and_softe.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `budget_enforcer.py` | `scripts/budget_enforcer.py` | ates per 1M tokens | 0 |
| **Базовый** | `create_theme.py` | `projects/tilda_migration/create_theme.py` | Load resource mapping | 0 |
| **Базовый** | `deep_analysis.py` | `scripts/deep_analysis.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `deep_sprint_reviewer.py` | `scripts/deep_sprint_reviewer.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `download_project_specific_assets.py` | `projects/tilda_migration/download_project_specific_assets.py` | FTP Config | 0 |
| **Базовый** | `download_resources.py` | `projects/tilda_migration/download_resources.py` | Paths | 0 |
| **Базовый** | `dump_chat_md.py` | `scripts/dump_chat_md.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `execute_compression.py` | `scripts/execute_compression.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `execute_lmstudio_and_dism.py` | `scripts/execute_lmstudio_and_dism.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_biohim.py` | `projects/tilda_migration/find_biohim.py` | Search for "БИОХИМ" or "biohim" | 0 |
| **Базовый** | `find_endpoints_in_dashboard.py` | `projects/tilda_migration/find_endpoints_in_dashboard.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_footer_elements.py` | `projects/tilda_migration/find_footer_elements.py` | Let's look at elements inside the footer or bottom of the page We can find all elements with classes containing 'rec' at the end | 0 |
| **Базовый** | `find_live_footer_imgs.py` | `projects/tilda_migration/find_live_footer_imgs.py` | Find all images in the document and print the last few | 0 |
| **Базовый** | `find_live_footer_logo.py` | `projects/tilda_migration/find_live_footer_logo.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_more_paths.py` | `projects/tilda_migration/find_more_paths.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `find_step.py` | `scratch/find_step.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `fix_icons_and_footer.py` | `projects/tilda_migration/fix_icons_and_footer.py` | FTP Config | 0 |
| **Базовый** | `generate_all_commands_reference.py` | `scripts/generate_all_commands_reference.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_desktop_guides.py` | `scripts/generate_desktop_guides.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_readable_review.py` | `scripts/generate_readable_review.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `generate_rod_letter.py` | `scripts/generate_rod_letter.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_days_6_7_cost.py` | `scripts/inspect_days_6_7_cost.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `inspect_deal.py` | `scratch/inspect_deal.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_form_html.py` | `projects/tilda_migration/inspect_form_html.py` | print first 3000 chars of block HTML | 0 |
| **Базовый** | `inspect_forms_detail.py` | `projects/tilda_migration/inspect_forms_detail.py` | Let's find all divs with class 't-form' | 0 |
| **Базовый** | `inspect_images.py` | `projects/tilda_migration/inspect_images.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `inspect_reports_detail.py` | `scripts/inspect_reports_detail.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `inventory.py` | `config/infra_management/scripts/inventory.py` | Configuration | 0 |
| **Базовый** | `merge_and_translate_repare.py` | `scripts/merge_and_translate_repare.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `mirror_vps_scripts.py` | `scripts/mirror_vps_scripts.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `parse_days_detail.py` | `scripts/parse_days_detail.py` | !/usr/bin/env python3 | 0 |
| **Базовый** | `rebuild_try_to_repare_en.py` | `scripts/rebuild_try_to_repare_en.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `rename_assets_and_title.py` | `projects/tilda_migration/rename_assets_and_title.py` | FTP Config | 0 |
| **Базовый** | `safe_system_cleaner.py` | `scripts/safe_system_cleaner.py` | UTF-8 | 0 |
| **Базовый** | `search_all_folders.py` | `scratch/search_all_folders.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `secret_leak_scanner.py` | `scripts/secret_leak_scanner.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_all_projects_pages.py` | `projects/tilda_migration/tilda_fetch_all_projects_pages.py` | 1. Get projects list | 0 |
| **Базовый** | `tilda_fetch_pages_json.py` | `projects/tilda_migration/tilda_fetch_pages_json.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_project_details.py` | `projects/tilda_migration/tilda_fetch_project_details.py` | Try POST | 0 |
| **Базовый** | `tilda_fetch_project_pages.py` | `projects/tilda_migration/tilda_fetch_project_pages.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_fetch_projects_json.py` | `projects/tilda_migration/tilda_fetch_projects_json.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_get_preview.py` | `projects/tilda_migration/tilda_get_preview.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_list_projects.py` | `projects/tilda_migration/tilda_list_projects.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `tilda_session.py` | `projects/tilda_migration/tilda_session.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `trace_session.py` | `scratch/trace_session.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `translate_datasheet.py` | `scripts/translate_datasheet.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `try_submit_login.py` | `projects/tilda_migration/try_submit_login.py` | Автоматизация рабочего процесса. | 0 |
| **Базовый** | `update_form_js.py` | `projects/tilda_migration/update_form_js.py` | FTP Config | 0 |
| **Базовый** | `zip_theme.py` | `projects/tilda_migration/zip_theme.py` | Compute relative path in ZIP (should start with qilin-theme/) | 0 |
| **Расширенный** | `b24_daily_analytics_sync.py` | `scripts/vps/b24_daily_analytics_sync.py` | !/usr/bin/env python3 | 1 |
| **Расширенный** | `build_sprint_evaluation.py` | `scripts/build_sprint_evaluation.py` | !/usr/bin/env python3 | 0 |
| **Расширенный** | `check_content.py` | `projects/tilda_migration/check_content.py` | Print page title | 0 |
| **Расширенный** | `check_deal_mail.py` | `scratch/check_deal_mail.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_form_tag.py` | `projects/tilda_migration/check_form_tag.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_lead_15960.py` | `scratch/check_lead_15960.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `check_range.py` | `scratch/check_range.py` | Автоматизация рабочего процесса. | 0 |
| **Расширенный** | `create_rod_excel.py` | `scripts/create_rod_excel.py` | Автоматизация рабочего процесса. | 0 |
| **Интеграционный** | `mass_replace.py` | `config/infra_management/scripts/mass_replace.py` | Configuration | 0 |
| **Диагностический** | `preflight.py` | `scripts/preflight.py` | Fallback token estimator if tiktoken is not installed Fallback estimation: | 0 |
| **Диагностический** | `test_bindings.py` | `scratch/test_bindings.py` | Check timeline bindings for Deal 2352 | 0 |
| **Диагностический** | `test_ftp.py` | `projects/tilda_migration/test_ftp.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `tilda_auth_test.py` | `projects/tilda_migration/tilda_auth_test.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `tilda_test_projects_param.py` | `projects/tilda_migration/tilda_test_projects_param.py` | Автоматизация рабочего процесса. | 0 |
| **Диагностический** | `verify.py` | `config/infra_management/scripts/verify.py` | Configuration | 0 |

---

<a id='metabase_analytics'></a>
## 15. Сквозная бизнес-аналитика и Metabase BI (DWH)

| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |
| :--- | :--- | :--- | :--- | :--- |
| **Канонический** | `manage_metabase_dashboards.py` | `projects/metabase_analytics/scripts/manage_metabase_dashboards.py` | Единый CLI-конвейер v2.4: деплой дашбордов № 4 и № 8, карточек 54, 49 (динамические Field ID), 3-уровневая группировка расходов LLM (Инициатор -> Пайплайн -> API-Ключ), устранение монолита круговой диаграммы (4 реальных сектора), динамический расчет затрат ($), светофор здоровья ключей, автоименование `[ВРЕМЕННЫЙ] unclassified_<task>`, локаль ru. Включает встроенные субкоманды самодиагностики `--action test-queries` (тестирование исполнения всех 7 карточек) и `--action db-stats` (сводка DWH). Поддерживает `--dry-run`. | 0 |
| **Канонический** | `audit_llm_keys.py` | `projects/metabase_analytics/scripts/audit_llm_keys.py` | Боевой аудит пула API-ключей Gemini и DeepSeek v2.1: проверка доступности и задержки, синхронизация с DWH (`llm_keys_status`) с маппингом канонических масок (`Gemini-1 (..94Cw)`, `DeepSeek-V3 Main`), автоочистка устаревших алиасов (`--cleanup-obsolete`), запрет автоудаления ключей, отправка алертов в чат Битрикс24 (`--notify-b24`). Работает в cron на VPS. | 0 |
| **Канонический** | `search_session_wishes.py` | `projects/metabase_analytics/scripts/search_session_wishes.py` | Канонический инструмент v1.0 сквозного семантического поиска и кластеризации требований и задач пользователя по всей истории диалогов (`brain transcripts`) с поддержкой фильтрации по ключевым словам (`--keywords`), группировки (`--cluster`) и экспорта в JSON (`--export`). | 0 |
| **Канонический** | `sync_analytics_dwh.py` | `projects/metabase_analytics/scripts/sync_analytics_dwh.py` | Боевой ETL-скрипт инкрементальной (`--days N`) и полной (`--full`) синхронизации сделок из Битрикс24 в PostgreSQL `marketing_db` с маппингом стадий и причин отказа. Поддерживает `--dry-run`. | 0 |
| **Канонический** | `llm_tracker.py` | `projects/metabase_analytics/scripts/llm_tracker.py` | Канонический модуль сквозного трекинга токенов: автоопределение инициатора (Артем vs Михаил vs Роботы), таксономия задач, логирование в `llm_usage_logs` и умная ротация ключей SmartKeyManager. | 0 |

