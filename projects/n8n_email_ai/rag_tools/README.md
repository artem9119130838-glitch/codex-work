# RAG tools (parser / chunker)

Назначение: локально (без сетевых вызовов) разобрать markdown-файлы на чанки и подготовить JSONL для дальнейшего upsert в `marketing_db.knowledge_base` и/или генерации embeddings.

Важное:

- Секреты (API keys, пароли, webhook URL) сюда не писать.
- Этот пакет не делает DB-writes и не делает embeddings сам по себе — только готовит данные.

## Chunker

Скрипт: `md_chunker.py`

Пример:

```powershell
py -3 E:\Codex_Work\projects\n8n_email_ai\rag_tools\md_chunker.py `
  --in E:\Codex_Work\codex_kb\00_global\SECURITY_POLICY.md `
  --category infrastructure `
  --out E:\Codex_Work\projects\n8n_email_ai\rag_tools\out\SECURITY_POLICY.jsonl
```

## Batch: codex_kb

Скрипт: `kb_chunk_export.ps1`

Экспортирует чанки для набора папок (по умолчанию: `codex_kb\00_global`, `codex_kb\20_domains`, `codex_kb\30_runbooks`) и складывает JSONL в `rag_tools\out`.

Пример:

```powershell
powershell -ExecutionPolicy Bypass -File E:\Codex_Work\projects\n8n_email_ai\rag_tools\kb_chunk_export.ps1
```

