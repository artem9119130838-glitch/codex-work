# Индекс навыков ИИ-ассистента (Личный контур)

Перед решением сложных или типовых задач ИИ-ассистент сверяется с этим индексом и загружает нужный навык (skill) для минимизации расхода токенов.

> 📦 **[SCRIPTS_CATALOG.md](file:///C:/Codex_Personal/codex_kb/SCRIPTS_CATALOG.md)** — **Единый каталог всех автоматизаций и скриптов контура** (сгруппированы по семействам инструментов: CRM Битрикс24, 1С OData, Почта IMAP, HR, Тендеры ГОЗ, VPS бэкапы, Windows Victus). Сверяйтесь с ним перед написанием любого нового скрипта!

## Список активных навыков (в C:\Users\Артем\.gemini\config\skills\):

1. **[token_guard](file:///C:/Users/Артем/.gemini/config/skills/token_guard/SKILL.md) — Token Guard and Context Discipline**
   * *Когда вызывать:* **Перед каждым шагом и командой в сессии.** Чек-лист Pre-flight (4 вопроса), запрет микро-скриптов, сырых дампов >10 КБ и фонового сканирования.
2. **[session_management](file:///C:/Users/Артем/.gemini/config/skills/session_management/SKILL.md) — Управление сессиями ИИ и сжатие (/compress)**
   * *Когда вызывать:* Завершение чата (`/compress`, `/end-session`, `!конец`), Zero-Prose Guard, создание `.ai/SESSION_SUMMARY.md` в один абзац, очистка `scratch/` и `git push`.
3. **[n8n_crm_email_engine](file:///C:/Users/Артем/.gemini/config/skills/n8n_crm_email_engine/SKILL.md) — n8n CRM and Email Engine (Мастер-конвейер)**
   * *Когда вызывать:* Интеграция n8n с почтой IMAP Hostland, парсинг вложений (XLSX, PDF), идемпотентное создание сделок в Битрикс24, защита от дублей, авторетраи, джиттер при шквале вебхуков, диагностика и безопасный вакуум SQLite без WAL. *(Объединил `email_ai_pipelines`, `n8n_idempotent_crm_pipelines` и `n8n_crm_diagnostics`)*.
4. **[1c_unf](file:///C:/Users/Артем/.gemini/config/skills/1c_unf/SKILL.md) — Разработка и Интеграция 1С:УНФ**
   * *Когда вызывать:* OData API запросы (`substringof`), JSON-структуры адресов БСП (`make_bsp_address_json`), запрет самодельных формул расчета прибыли/себестоимости, СКД и физические таблицы регистров.
5. **[infra_management](file:///C:/Users/Артем/.gemini/config/skills/infra_management/SKILL.md) — Управление инфраструктурой и единым реестром**
   * *Когда вызывать:* Инвентаризация проектов (`/audit`), аудит переменных `.env`, массовая замена конфигураций (`/replace`), проверка работоспособности сервисов (`/verify`) и карта зависимостей `INFRASTRUCTURE.md`.
6. **[linux](file:///C:/Users/Артем/.gemini/config/skills/linux/SKILL.md) — Администрирование Linux Server**
   * *Когда вызывать:* Настройка и мониторинг Ubuntu VPS (`109.248.170.181`), аудит SSH-ключей, управление Docker Compose (стандарт 3.3), защита от коллизий Apache vs Nginx, инвентарь скриптов `/Storage/`.
7. **[windows](file:///C:/Users/Артем/.gemini/config/skills/windows/SKILL.md) — Диагностика Windows и HP Victus 16**
   * *Когда вызывать:* Видеокарта NVIDIA RTX 3060 (Код 43, драйвер `nvhmi.inf`), базовый видеоадаптер Intel Iris, сброс кэша дисплеев и MPO, клавиша F8 Safe Mode в BCD, нейтрализация popup Adobe Acrobat.
8. **[tender_automation](file:///C:/Users/Артем/.gemini/config/skills/tender_automation/SKILL.md) — Автоматизация тендеров и парсинг ГОЗ**
   * *Когда вызывать:* Парсинг DOCX/PDF таблиц спецификаций MarkItDown, жесткое извлечение 15-значного номера процедуры (на `26...`), запрет 11-значного ЕИС, слияние Excel-лотов, троттлинг Gemini API.
9. **[llm_quota_and_fallback_manager](file:///C:/Users/Артем/.gemini/config/skills/llm_quota_and_fallback_manager/SKILL.md) — LLM Quota and Multi-Tier Fallback**
   * *Когда вызывать:* Двухконтурная архитектура API (Gemini ➔ DeepSeek при ошибке 429), адаптивный кулдаун `retryDelay`, синхронизация таймаутов n8n, логирование расхода токенов.
10. **[git](file:///C:/Users/Артем/.gemini/config/skills/git/SKILL.md) — Git Workflow и Безопасность**
    * *Когда вызывать:* Разграничение доступов: Личный Git (`Codex_Personal` — Read/Write) vs Рабочий Git (`tender-rag-api` — Strict Read-Only), защита от утечек секретов.
11. **[metabase_analytics_ops](file:///C:/Users/Артем/.gemini/config/skills/metabase_analytics_ops/SKILL.md) — Аналитика и безопасность Metabase**
    * *Когда вызывать:* Построение SQL-воронок продаж, бэкап H2-базы Metabase, права доступа в Community Free версии.

---

## 🗄️ Архивные навыки (в C:\Users\Артем\.gemini\config\skills_archive\):
* `email_ai_pipelines`, `n8n_idempotent_crm_pipelines`, `n8n_crm_diagnostics` — консолидированы в `n8n_crm_email_engine`.
* `migrate-workflows`, `generative_ui` — архивированы из встроенного меню, чтобы не засорять меню `/`.
