# Prompt: marketing_db / 1C / n8n ingestion

Открой workspace `E:\Codex_Work`.

Это специализированный рабочий чат только для `marketing_db / 1C / n8n ingestion`.

Этот чат отвечает только за:

- 1С OData read-only;
- `marketing_db`;
- n8n workflows;
- enrichment;
- review batches;
- readiness к `email_messages` и `email_match_results`.

Этот чат не отвечает за curated KB, шаблоны писем, статьи, tone rules и RAG-тексты. Для этого есть отдельный рабочий чат.

Сначала прочитай:

```text
E:\Codex_Work\AGENTS.md
E:\Codex_Work\PROGRESS.md
E:\Codex_Work\CHAT_DISPATCHER.md
E:\Codex_Work\codex_kb\00_global\SECURITY_POLICY.md
E:\Codex_Work\codex_kb\00_global\BUSINESS_RULES.md
E:\Codex_Work\codex_kb\progress\1C_PROGRESS.md
E:\Codex_Work\codex_kb\progress\N8N_EMAIL_AI_PROGRESS.md
E:\Codex_Work\codex_kb\20_domains\1c\README.md
E:\Codex_Work\codex_kb\20_domains\1c\EMAIL_CONTACT_FIELD_MAPPING.md
E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V1_POSTMORTEM_2026-05-10.md
E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_IMPLEMENTATION_PLAN_2026-05-10.md
E:\Codex_Work\projects\n8n_email_ai\N8N_MARKETING_DB_V2_1_OWNER_ENRICHMENT_PLAN_2026-05-10.md
E:\Codex_Work\projects\n8n_email_ai\scripts\generate_v2_1_lead_bundle.ps1
```

Контекст:

- 1С используется только read-only. Никаких записей в 1С.
- Все новые данные и результаты matching пишутся только в PostgreSQL `marketing_db`.
- PostgreSQL user для n8n: `n8n_marketing`.
- 1C OData user для n8n: `odata.user`.
- Пароли, токены и webhook secrets не записывать в markdown/json.
- Mailbox intake и AI/RAG generation пока не запускать.

Текущая ближайшая задача:

1. Сделать verification pass по `v2.1` и review batch 2025.
2. Подтвердить фактическое качество следующих полей:
   - `owner_group_path`
   - `owner_tags_text`
   - `owner_search_emails`
   - `owner_search_phones`
   - `owner_is_important`
   - `owner_importance_score`
   - `owner_importance_reason`
3. Зафиксировать remaining gaps.
4. Подготовить следующий узкий шаг: mailbox intake readiness checklist.

Что нельзя делать в этом чате:

- не строить новую большую ветку ingestion без verification pass;
- не запускать mailbox intake;
- не генерировать письма;
- не править curated KB как основной источник текстов;
- не писать в 1С.

Формат результата:

1. краткий verification outcome;
2. какие поля подтверждены;
3. какие поля еще спорные;
4. какой один следующий узкий шаг нужен перед mailbox intake.
