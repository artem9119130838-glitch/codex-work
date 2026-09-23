# AI Chats Export & Normalization

Проект автоматической тематической кластеризации и очистки логов диалогов с ИИ (ChatGPT и Gemini) для последующего формирования базы знаний в Google NotebookLM.

## Быстрый старт

1. Убедитесь, что ваши сырые архивы (`conversations.json`, `МоиДействия.html`, и т.д.) лежат в папке [data/raw/](file:///C:/Antigravity/projects/AI%20chats%20export/data/raw).
2. Запустите скрипт сортировки:
   ```bash
   py src/AI_chats_filter_optimized.py
   ```
3. Результаты сортировки в формате Markdown появятся в папке [data/done/](file:///C:/Antigravity/projects/AI%20chats%20export/data/done).

## Документация проекта

- Подробный инженерный паспорт проекта: [PROJECT_HANDOFF.md](file:///C:/Antigravity/projects/AI%20chats%20export/PROJECT_HANDOFF.md)
- Правила разработки и запуска для ИИ-агентов: [AGENTS.md](file:///C:/Antigravity/projects/AI%20chats%20export/AGENTS.md)
- Индекс файлов: [.codex/project-index.md](file:///C:/Antigravity/projects/AI%20chats%20export/.codex/project-index.md)
- Лог прогресса: [progress.md](file:///C:/Antigravity/projects/AI%20chats%20export/progress.md)
