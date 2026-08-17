# Sources and Notes

## Основные источники (как “сырье”)
- `E:Codex_Workprojectsn8n_email_aiRAG файлыcompany.md`
- `E:Codex_Workprojectsn8n_email_aiRAG файлыclient_segments.md`
- `E:Codex_Workprojectsn8n_email_aiRAG файлыobjections.md`
- `E:Codex_Workprojectsn8n_email_aiRAG файлыemail_templates.md`
- `E:Codex_Workprojectsn8n_email_aiRAG файлыreactivation_templates.md`
- `E:Codex_Workprojectsn8n_email_aiRAG файлыtone_rules.md`
- `E:Codex_Workprojectsn8n_email_aiRAG файлыservices_import_china.md`
- `E:Codex_Workprojectsn8n_email_aiRAG файлыservices_tender_supply.md`
- `E:Codex_Workprojectsn8n_email_aiRAG файлыexport_longwang.ru_статьи.xlsx`
- `E:Codex_Workprojectsn8n_email_aiRAG файлыexport_longwang.ru_услуги.xlsx`
- `E:Codex_Workprojectsn8n_email_aiRAG файлыRAG-база должна быть.docx`
- `E:Codex_Workprojectsn8n_email_aiRAG файлынедоработки по RAG.docx`

## Как “curated KB” получалась из источников
- Убраны повторы “ВЭД — цепочка” и “не обещать без данных” (оставлены в 1–2 местах как канонические правила).
- Длинные файлы (tone_rules/company) сжаты до правил, которые реально нужны при написании письма.
- Все “опасные” места (цены/сроки/комиссии/гарантии) свернуты в запреты и чеклист, без конкретных цифр.
- Для статей и услуг вынесены индексы в markdown, чтобы RAG мог выбирать по Title/Description/H1, а не “угадывать”.

## Маппинг: новый файл -> источники
- `00_manifest.md` -> оба docx (требования к структуре) + общие правила workspace.
- `10_company_core.md` -> `company.md` (позиционирование/ценность/подпись) + ограничения из `tone_rules.md`.
- `20_client_segments.md` -> `client_segments.md` (сжатие до основных сегментов).
- `30_objections.md` -> `objections.md` (сжатые паттерны ответов).
- `40_email_templates.md` -> `email_templates.md` (выжимка ключевых шаблонов) + тендерные принципы из `services_tender_supply.md`.
- `50_reactivation_templates.md` -> `reactivation_templates.md`.
- `60_tone_rules.md` -> `tone_rules.md`.
- `70_input_client_context.md` -> оба docx (пробел про входную карточку) + требования “не считать без вводных”.
- `80_template_selection_rules.md` -> оба docx (пробел про маршрутизатор) + `email_templates.md`.
- `90_pre_send_checklist.md` -> `tone_rules.md` + `email_templates.md` + оба docx.
- `95_article_selection_rules.md` -> `tone_rules.md` + `objections.md` + оба docx.
- `96_articles_index.md` -> `export_longwang.ru_статьи.xlsx`.
- `97_services_index.md` -> `export_longwang.ru_услуги.xlsx`.

## Известные пробелы / что добавить позже (для качества RAG)
- Safe proof points уже добавлены на базе транскрипций: `15_proof_points_from_calls.md`. Но отдельного набора подтвержденных кейсов/референсов (которые можно цитировать как доказательства: “делали X для Y”) пока нет.
- Отдельные “правила тендер-анализа” (чеклист исполнимости, условия отказа) — в источниках упомянуто как пробел.
- Единая утвержденная подпись/нейминг менеджеров (в источниках отмечена неоднозначность).
- Если планируется авто-подбор статей: добавить “теги статей” (ручная разметка топ-30 статей), чтобы не полагаться только на совпадение текста.
## Call transcripts
Raw источник:
- `E:Codex_Workprojectsn8n_email_aiRAG файлытранскрипции звонков*.txt`

Статус файлов в `kb_leads_v1`:
- `15_proof_points_from_calls.md` — канонический safe-файл (разрешен для RAG и генерации писем).
- `15_call_phrase_candidates_speaker2.md` — raw source only (не использовать для прямого RAG retrieval и не использовать для прямой генерации писем).
- `35_objection_rebuttal.md` -> `objections.md` + `tone_rules.md` + `15_proof_points_from_calls.md`.


