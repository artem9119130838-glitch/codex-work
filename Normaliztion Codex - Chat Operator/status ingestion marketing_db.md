**Что готово в целом**
- Развернута и закреплена рабочая БД `marketing_db` с основными таблицами для клиентов, контактов, писем, матчинга, knowledge base и курсоров.
- Подтвержден read-only доступ к 1С OData и собран контур загрузки данных в PostgreSQL.
- Собрана curated KB для будущих писем и RAG-логики.
- Есть канонические operator/runbook-файлы, по которым можно продолжать без старых чатов.

**Фаза 1 — база и каркас данных**
Выполнено:
- создана схема `marketing_db`;
- настроен ограниченный пользователь `n8n_marketing`;
- подтвержден импорт сущностей 1С в PostgreSQL;
- подготовлен owner/contact слой для дальнейшего матчинга и email-логики.

Итоговые файлы:
- [E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V1_POSTMORTEM_2026-05-10.md](E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V1_POSTMORTEM_2026-05-10.md)
- [E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_IMPLEMENTATION_PLAN_2026-05-10.md](E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_IMPLEMENTATION_PLAN_2026-05-10.md)
- [E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_reset_and_v2_patch_2026-05-10.sql](E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_reset_and_v2_patch_2026-05-10.sql)

Результат:
- эффективность хорошая как у “фундамента”: база и связи подготовлены, owner/contact структура создана, проект ушел от ручных разрозненных выгрузок к нормальному хранилищу.

**Фаза 2 — ingestion из 1С в marketing_db**
Выполнено:
- собран и стабилизирован ingestion workflow;
- реализован backfill-контур по лидам;
- настроен upsert в `onec_owners` и `onec_contacts`;
- добавлен cursor-based режим и затем рабочий `skip`-based backfill для продвижения по истории;
- owner enrichment вынесен в рабочий слой с признаками важности, групп, тегов, email/phone search;
- подготовлены operator artifacts и SQL-отчеты для контроля.

Итоговые файлы:
- [E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_ingestion_v2_2_master.json](E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_ingestion_v2_2_master.json)
- [E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_ingestion_v2_2_master_CANONICAL_FINAL.json](E:\Codex_Work\projects\n8n_email_ai\workflows\marketing_db_ingestion_v2_2_master_CANONICAL_FINAL.json)
- [E:\Codex_Work\projects\n8n_email_ai\workflows\v2.3 leads backfill cursor fixed by skip.json](E:\Codex_Work\projects\n8n_email_ai\workflows\v2.3%20leads%20backfill%20cursor%20fixed%20by%20skip.json)
- [E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_OPERATOR_RUNBOOK.md](E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_OPERATOR_RUNBOOK.md)
- [E:\Codex_Work\projects\n8n_email_ai\INGESTION_REPORT.md](E:\Codex_Work\projects\n8n_email_ai\INGESTION_REPORT.md)
- [E:\Codex_Work\projects\n8n_email_ai\workflows\summary gpt 14-05.md](E:\Codex_Work\projects\n8n_email_ai\workflows\summary%20gpt%2014-05.md)

Результат:
- эффективность высокая именно как у ingestion-слоя: **лиды и owner-данные уже загружаются в `marketing_db`, курсоры и backfill-механика собраны, БД готова быть основой для следующего этапа**.
- То есть Фаза 2 дала не “прототип”, а уже рабочий operational контур, на который можно опираться дальше.

**RAG / база знаний — статус**
Сейчас база знаний для писем и клиентской коммуникации **собрана в curated-виде** и уже пригодна как канонический текстовый слой. То есть RAG-часть не “с нуля”, а в состоянии **рабочего v1**.

**Что готово**
Создана curated KB:
- [E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\00_manifest.md](E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\00_manifest.md)
- [E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\70_input_client_context.md](E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\70_input_client_context.md)
- [E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\80_template_selection_rules.md](E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\80_template_selection_rules.md)
- [E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\90_pre_send_checklist.md](E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\90_pre_send_checklist.md)
- [E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\95_article_selection_rules.md](E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\95_article_selection_rules.md)
- [E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\96_articles_index.md](E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\96_articles_index.md)
- [E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\97_services_index.md](E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\97_services_index.md)
- [E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\99_sources_and_notes.md](E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\99_sources_and_notes.md)

Дополнительно собраны:
- [E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\15_proof_points_from_calls.md](E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\15_proof_points_from_calls.md)
- [E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\35_objection_rebuttal.md](E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\35_objection_rebuttal.md)

**Результат**
- есть канон для:
  - входного контекста клиента,
  - выбора шаблона,
  - pre-send проверки,
  - подбора статей,
  - objection handling,
  - safe proof points.
- raw-материалы уже отделены от активной KB.
- для генерации черновиков этого слоя уже достаточно.

**Что требует доделки**
1. Еще нет production-контура embeddings/RAG retrieval.
2. `knowledge_base` в `marketing_db` есть, но это пока скорее заготовка, чем подтвержденный рабочий индекс.
3. Нужен финальный chunking/import pipeline из curated `.md` в `knowledge_base`.
4. Нужно подтвердить `pgvector` и реальную схему поиска по embeddings.
5. Нужен один короткий runbook именно для:
   - как обновлять curated KB,
   - как переиндексировать embeddings,
   - как проверять retrieval quality.

**План перевода в embeddings**
Коротко, без лишней архитектуры:
1. Источник истины остается `.md` в `kb_leads_v1`.
2. Каждый канонический `.md` режется на небольшие смысловые chunks.
3. Chunks пишутся в `marketing_db.knowledge_base` с:
   - `source_path`
   - `source_section`
   - `chunk_index`
   - `content`
   - `category`
   - `content_hash`
   - `updated_at`
   - `is_active`
4. Для каждого chunk считаются embeddings.
5. Поиск для модели идет не по всем файлам, а по top-k релевантным chunks.
6. Переиндексация запускается только после изменений в curated KB, а не постоянно.

Итог:
- **.md остается главным источником**
- `knowledge_base + embeddings` — производный индекс
- это уже соответствует твоей общей логике workspace

---

**Что еще есть в проекте, кроме Фазы 1/2 и RAG**

**1. Owner enrichment / scoring слой — готов**
Это отдельный важный кусок, не просто часть ingestion.
Зафиксирован owner-level intelligence:
- `owner_group_path`
- `owner_tags_text`
- `owner_search_emails`
- `owner_search_phones`
- `owner_is_important`
- `owner_importance_score`
- `owner_importance_reason`

Опорные файлы:
- [E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_1_OWNER_ENRICHMENT_PLAN_2026-05-10.md](E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_1_OWNER_ENRICHMENT_PLAN_2026-05-10.md)
- [E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_1_VERIFICATION_PASS_2026-05-11.md](E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_1_VERIFICATION_PASS_2026-05-11.md)

**Статус:** готов как data-layer для будущего matching/outreach.

**2. Operator / monitoring слой — готов v1**
Собраны рабочие operator artifacts:
- [E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_OPERATOR_RUNBOOK.md](E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_OPERATOR_RUNBOOK.md)
- [E:\Codex_Work\projects\n8n_email_ai\INGESTION_REPORT.md](E:\Codex_Work\projects\n8n_email_ai\INGESTION_REPORT.md)
- [E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_event_log_table_v2_2.sql](E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_event_log_table_v2_2.sql)
- [E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_v2_2_last24h_dbeaver_report.sql](E:\Codex_Work\projects\n8n_email_ai\sql\marketing_db_ingestion_v2_2_last24h_dbeaver_report.sql)

**Статус:** готов для контроля ingestion, но не для почтового production-контура.

**3. Email/matching слой — заготовлен, но не доведен**
В БД уже есть:
- `email_messages`
- `email_match_results`
- `clients_intel`

**Статус:**
- схема уже есть;
- production-поток intake/matching еще не доведен;
- это как раз следующий большой рабочий слой.

**4. Глобальная KB / runbooks / security — готово**
В workspace уже собран общий operational memory:
- `AGENTS.md`
- `PROGRESS.md`
- `CHAT_DISPATCHER.md`
- `codex_kb\00_global\SECURITY_POLICY.md`
- `codex_kb\00_global\BUSINESS_RULES.md`

