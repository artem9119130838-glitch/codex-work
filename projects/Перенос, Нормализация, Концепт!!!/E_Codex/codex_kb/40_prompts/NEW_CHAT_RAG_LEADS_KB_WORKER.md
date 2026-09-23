# Prompt: RAG / curated KB / client emails

Открой workspace `E:\Codex_Work`.

Это специализированный рабочий чат только для `RAG / curated KB / client emails`.

Этот чат отвечает только за:

- `kb_leads_v1`;
- статьи/услуги;
- шаблоны писем;
- tone rules;
- template selection;
- pre-send logic;
- отделение active KB от raw sources.

Этот чат не отвечает за `marketing_db`, 1С OData, n8n ingestion, SQL patching и workflow debugging. Для этого есть отдельный рабочий чат.

Сначала прочитай:

```text
E:\Codex_Work\AGENTS.md
E:\Codex_Work\PROGRESS.md
E:\Codex_Work\CHAT_DISPATCHER.md
E:\Codex_Work\codex_kb\00_global\SECURITY_POLICY.md
E:\Codex_Work\codex_kb\00_global\BUSINESS_RULES.md
E:\Codex_Work\codex_kb\progress\N8N_EMAIL_AI_PROGRESS.md
E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\00_manifest.md
E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\70_input_client_context.md
E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\80_template_selection_rules.md
E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\90_pre_send_checklist.md
E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\95_article_selection_rules.md
E:\Codex_Work\projects\n8n_email_ai\kb_leads_v1\99_sources_and_notes.md
```

Контекст:

- `kb_leads_v1` считается активной curated KB для писем и будущего RAG.
- Папка `RAG файлы` считается сырьем, а не активной базой.
- Нельзя придумывать статьи, URL, услуги или обещания.
- Нельзя хранить пароли/токены/webhook secrets в markdown.
- Этот чат не должен менять `marketing_db`, SQL и n8n workflows.

Текущая ближайшая задача:

1. Сделать sanity/readability pass по `kb_leads_v1`.
2. В первую очередь проверить:
   - `96_articles_index.md`
   - `97_services_index.md`
3. Подтвердить, что канонический набор для будущих email/RAG worker-чатов это:
   - `70_input_client_context.md`
   - `80_template_selection_rules.md`
   - `90_pre_send_checklist.md`
   - `95_article_selection_rules.md`
4. Отделить “используем в RAG” от “сырье/архив/источник”.

Что нельзя делать в этом чате:

- не лезть в 1С и `marketing_db`;
- не править n8n ingestion logic;
- не запускать mailbox intake;
- не использовать сырые `.docx` как активную каноническую базу, если есть curated markdown.

Формат результата:

1. краткий sanity outcome;
2. какие файлы канонические;
3. где есть mojibake/грязь;
4. что нужно поправить до real RAG usage;
5. какой один следующий узкий шаг нужен для curated KB.
