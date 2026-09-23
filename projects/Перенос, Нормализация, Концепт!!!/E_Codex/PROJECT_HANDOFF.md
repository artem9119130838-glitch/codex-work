# n8n_email_ai - Project Handoff

Дата обновления: 2026-05-29

## 1. Общая задача проекта

Проект `n8n_email_ai` нужен для того, чтобы превратить разрозненную клиентскую переписку и данные из 1С в управляемый рабочий контур:

1. read-only получать клиентов и контакты из 1С в `marketing_db`;
2. сопоставлять письма с клиентами;
3. накапливать короткое клиентское знание по теме интереса и статусу;
4. готовить безопасные черновики follow-up / reactivation писем;
5. в будущем использовать это для задач в Bitrix, AI-ответов и RAG.

Ключевой принцип: **1С только источник данных, `marketing_db` - рабочая AI/email база**.

## 2. Статус по фазам

| Фаза | Статус | Что сделано | Эффективность / результат | Канонические файлы |
|---|---|---|---|---|
| P0. База знаний и workspace | Готово | Собран `codex_kb`, правила безопасности, dispatcher, progress, структура проектов | Новый чат можно быстро вводить в контекст без старых логов | `E:\Codex_Work\AGENTS.md`, `E:\Codex_Work\PROGRESS.md`, `E:\Codex_Work\CHAT_DISPATCHER.md`, `E:\Codex_Work\ГДЕ_ЧТО_ЛЕЖИТ.md` |
| Phase 1. `marketing_db` foundation | Готово | Создана схема БД, ограниченный пользователь `n8n_marketing`, read-only контур 1С OData, owner/contact слой | Получена отдельная рабочая БД под AI/email без записи в 1С | `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V1_POSTMORTEM_2026-05-10.md`, `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_IMPLEMENTATION_PLAN_2026-05-10.md`, `E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_reset_and_v2_patch_2026-05-10.sql` |
| Phase 2. Ingestion from 1C | Готово как рабочий контур | Собран ingestion workflow, backfill, upsert в `onec_owners` / `onec_contacts`, cursor/state logic, operator runbook и SQL monitoring | База клиентов из 1С загружается в `marketing_db`, проект имеет рабочий operational ingestion слой | `E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_ingestion_v2_2_master_CANONICAL_FINAL.json`, `E:\Codex_Work\projects\n8n_email_ai\workflows\v2.3 leads backfill cursor fixed by skip.json`, `E:\Codex_Work\projects\n8n_email_ai\workflows\summary gpt 14-05.md`, `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_OPERATOR_RUNBOOK.md`, `E:\Codex_Work\projects\n8n_email_ai\INGESTION_REPORT.md` |
| RAG / curated KB v1 | Готово как текстовый канон | Собрана curated KB для client emails, статей, objection handling и safe proof points | Есть пригодный текстовый слой для будущих draft-ов и RAG retrieval | `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\00_manifest.md`, `70_input_client_context.md`, `80_template_selection_rules.md`, `90_pre_send_checklist.md`, `95_article_selection_rules.md`, `96_articles_index.md`, `97_services_index.md`, `15_proof_points_from_calls.md`, `35_objection_rebuttal.md` |
| Phase 3. Mail intake / matching / drafts | Не начато как production-pilot | Схема БД для писем и matching уже существует, но рабочий pilot-контур еще не собран | Следующий крупный этап | использовать существующие таблицы `email_messages`, `email_match_results`, `clients_intel` |

## 3. Что уже реально есть в базе данных

### Уже рабочие таблицы

| Таблица | Назначение | Использовать как |
|---|---|---|
| `onec_owners` | Клиенты/лиды/контрагенты из 1С | Главный owner layer для email matching и AI enrichment |
| `onec_contacts` | Контакты из 1С | Поиск по email/телефону/контактному лицу |
| `ingestion_cursors` | Состояние backfill/daily sync | Не перепридумывать, использовать как канон ingestion state |
| `ingestion_event_log` | Журнал ingestion workflow | Операторский контроль |
| `email_messages` | Письма | Использовать для пилота почты, не раздувая raw archive |
| `email_match_results` | Результаты сопоставления писем | Основной matching layer |
| `clients_intel` | Короткая AI/email сводка по клиенту | Легкий клиентский intelligence слой |
| `knowledge_base` | Производный RAG индекс | Только как derived data от curated markdown |

### Уже готовые полезные поля

#### В `onec_owners`

- `owner_search_emails`
- `owner_search_phones`
- `owner_group_path`
- `owner_tags_text`
- `owner_is_important`
- `owner_importance_score`
- `owner_importance_reason`
- `ai_client_segment`
- `ai_email_summary`
- `sent_articles_history`
- `last_contact_date`

#### В `email_messages`

- `message_id`
- `from_email`
- `from_name`
- `subject`
- `received_at`
- `source_mailbox`
- `raw_payload`
- `is_junk`
- `junk_reason`
- `operator_comment`
- `thread_comment`
- `ai_summary`

#### В `email_match_results`

- `message_id`
- `matched_level`
- `decision`
- `decision_reason`
- `contact_entity`
- `contact_ref_key`
- `owner_entity`
- `owner_ref_key`
- `confidence`
- `matched_email`
- `matched_phone`

#### В `clients_intel`

- `email`
- `source_id_1c`
- `company_name`
- `inn`
- `ai_priority`
- `ai_summary`
- `last_topic`
- `current_status`
- `next_followup_at`

## 4. Структура проекта

### Канонические папки

| Путь | Что это |
|---|---|
| `E:\Codex_Work\projects\n8n_email_ai\workflows` | Канонические workflow JSON и краткие финальные пояснения к ним |
| `E:\Codex_Work\projects\n8n_email_ai\sql` | Рабочие SQL для схемы, reset, monitoring, reports |
| `E:\Codex_Work\projects\n8n_email_ai\scripts` | Генераторы и вспомогательные скрипты |
| `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1` | Curated KB для писем, тем, статей, objection handling |
| `E:\Codex_Work\projects\n8n_email_ai\rag_tools` | Инструменты и наработки для будущего RAG/indexing |

### Канонические файлы проекта

| Приоритет | Файл | Роль |
|---|---|---|
| P0 | `E:\Codex_Work\projects\n8n_email_ai\PROJECT_HANDOFF.md` | Главный инженерный паспорт проекта |
| P0 | `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_OPERATOR_RUNBOOK.md` | Как оператору работать с ingestion |
| P0 | `E:\Codex_Work\projects\n8n_email_ai\INGESTION_REPORT.md` | Короткий журнал фактов по ingestion |
| P1 | `E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_ingestion_v2_2_master_CANONICAL_FINAL.json` | Канонический master ingestion workflow |
| P1 | `E:\Codex_Work\projects\n8n_email_ai\workflows\v2.3 leads backfill cursor fixed by skip.json` | Финальная рабочая логика backfill с продвижением по истории |
| P1 | `E:\Codex_Work\projects\n8n_email_ai\workflows\summary gpt 14-05.md` | Краткое описание финальных Phase 2 правок |
| P1 | `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\00_manifest.md` | Главный индекс curated KB |

## 5. Структура чатов проекта

### Главный чат

Использовать для:

- стратегии;
- приемки результатов;
- обновления канона;
- решений о переходе между фазами.

Не использовать для:

- долгой технической отладки одного workflow;
- смешивания ingestion, RAG и email pilot в одном потоке.

### Рабочие чаты

| Приоритет | Чат | Задача | Когда закрывать |
|---|---|---|---|
| P0 | `marketing_db / 1C / n8n ingestion` | Только ingestion из 1С в `marketing_db` | После конкретного deliverable по workflow / backfill |
| P0 | `RAG / curated KB / client emails` | Только curated KB, статьи, правила и drafts logic | После конкретного deliverable по KB / prompts |
| P1 | `Phase 3 mail intake + matching` | Только intake писем, dedup, matching, `email_messages`, `email_match_results` | После pilot на 20–30 клиентов |
| P1 | `Phase 3 AI summary + drafts` | Только `clients_intel`, AI summary, draft preview | После первых качественных draft preview |

Правило: **один чат = один узкий deliverable**. После deliverable чат замораживается, результат переносится в канон.

## 6. Что сделано и с какой эффективностью

| Приоритет | Направление | Статус | Эффективность / что это дало |
|---|---|---|---|
| P0 | Workspace / KB governance | Готово | Проект можно передавать другому инженеру без старых чат-логов |
| P0 | Read-only 1C -> PostgreSQL foundation | Готово | Есть безопасный способ использовать 1С как источник без риска писать в `unf` |
| P0 | Ingestion Phase 2 | Готово как operational слой | Owner/contact данные уже загружаются в `marketing_db`, есть курсоры, runbook и monitoring |
| P0 | Owner enrichment | Готово | Уже есть признаки важности, групп, тегов и contact search для дальнейшего matching/outreach |
| P1 | Curated KB v1 | Готово | Есть текстовая база для drafts, статей и objection handling без сырого мусора |
| P1 | Monitoring / operator layer | Готово v1 | Оператор может контролировать ingestion через SQL и runbook |
| P2 | Email schema readiness | Частично готово | Таблицы для писем, matching и client intel уже есть, но pilot еще не собран |
| P2 | RAG derived index | Частично готово | `knowledge_base` есть, но embeddings/import pipeline еще не production-ready |

## 7. Что запланировано, но не начато / не доделано

| Приоритет | Задача | Статус | Что именно осталось |
|---|---|---|---|
| P0 | Mail intake pilot | Не начато | Поднять intake из отдельной IMAP-папки, дедуп, clean body, записать в `email_messages` |
| P0 | Deterministic email matching | Не начато | Сопоставление писем к `onec_owners` / `onec_contacts`, `needs_review` для не найденных |
| P1 | AI client summary | Не начато | Обновлять `clients_intel.ai_summary`, `last_topic`, `current_status` по matched клиентам |
| P1 | Draft preview | Не начато | Делать безопасные черновики follow-up / reactivation без отправки |
| P1 | RAG embeddings pipeline | Не начато как production | Chunking curated KB, embeddings, import в `knowledge_base`, retrieval check |
| P2 | Production mail send | Отложено | Автоотправку не включать до пилота intake + matching + draft review |
| P2 | AI auto-reply на входящие | Отложено | Только после успешного pilot и ручной проверки качества |
| P2 | Bitrix auto-tasking | Отложено | Только после устойчивого client intelligence и mail parsing |

## 8. Забытые / отложенные задачи

| Приоритет | Тема | Почему отложено |
|---|---|---|
| P1 | Полноценный RAG sync runbook именно для `kb_leads_v1` -> embeddings | Сначала нужен pilot по письмам, иначе retrieval нечему обслуживать |
| P1 | Проверка `pgvector` и quality retrieval | Не блокирует Phase 3 pilot, если drafts пока строятся от curated files напрямую |
| P2 | Полный почтовый архив за все годы | Слишком дорого и шумно для старта, нужен сначала экономный pilot |
| P2 | Хранение полного raw thread archive | На старте не нужно, увеличивает БД и стоимость анализа |
| P2 | Автоматическое создание новых клиентов по сомнительным письмам | Риск замусорить БД, пока нужен `needs_review` |

## 9. Что читать новому инженеру или новому чату

### Обязательный минимум

1. `E:\Codex_Work\AGENTS.md`
2. `E:\Codex_Work\PROGRESS.md`
3. `E:\Codex_Work\CHAT_DISPATCHER.md`
4. `E:\Codex_Work\projects\n8n_email_ai\PROJECT_HANDOFF.md`

### Если задача про ingestion

1. `E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_OPERATOR_RUNBOOK.md`
2. `E:\Codex_Work\projects\n8n_email_ai\INGESTION_REPORT.md`
3. `E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_ingestion_v2_2_master_CANONICAL_FINAL.json`
4. `E:\Codex_Work\projects\n8n_email_ai\workflows\v2.3 leads backfill cursor fixed by skip.json`
5. `E:\Codex_Work\projects\n8n_email_ai\workflows\summary gpt 14-05.md`

### Если задача про drafts / RAG / client emails

1. `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\00_manifest.md`
2. `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\70_input_client_context.md`
3. `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\80_template_selection_rules.md`
4. `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\90_pre_send_checklist.md`
5. `E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\95_article_selection_rules.md`

## 10. Короткий человеческий смысл проекта

Простыми словами:

- Phase 1 дала нам **отдельную рабочую базу**, чтобы не мучить 1С и не строить AI прямо внутри нее.
- Phase 2 дала нам **конвейер загрузки клиентов из 1С** в эту базу.
- Curated KB дала нам **что говорить клиентам и на чем строить drafts**.
- Следующий реальный шаг - **не авторассылка**, а аккуратный pilot старой почты: понять клиента, тему, историю и подготовить черновик.

Итоговая цель проекта:

> иметь систему, которая помнит клиентов, понимает, с чего начался диалог, и помогает регулярно и уместно напоминать о нас через осмысленные черновики, а не через случайные массовые письма.
