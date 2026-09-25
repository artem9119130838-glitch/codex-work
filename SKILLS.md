# Индекс навыков ИИ-ассистента (Личный контур)

Перед решением сложных или типовых задач ИИ-ассистент сверяется с этим индексом и загружает нужный навык (skill) для минимизации расхода токенов.

> 📦 **[SCRIPTS_CATALOG.md](file:///C:/Codex_Personal/codex_kb/SCRIPTS_CATALOG.md)** — **Единый каталог всех автоматизаций и скриптов контура** (сгруппированы по семействам инструментов: CRM Битрикс24, 1С OData, Почта IMAP, HR, Тендеры ГОЗ, VPS бэкапы, Windows Victus). Сверяйтесь с ним перед написанием любого нового скрипта!

## Список доступных навыков (в C:\Users\Артем\.gemini\config\skills\):

1.  **[windows](file:///C:/Users/Артем/.gemini/config/skills/windows/SKILL.md) — Диагностика Windows**
    *   *Когда вызывать:* Зависание Acrobat Reader, проблемы блокировки PDF в Temp, медленная работа Проводника (Explorer), сбои реестра, .bat скрипты, Punto Switcher, гибридная графика Intel/NVIDIA и черный экран, управление BCD и Safe Mode (клавиша F8, msconfig).
2.  **[linux](file:///C:/Users/Артем/.gemini/config/skills/linux/SKILL.md) — Администрирование Linux**
    *   *Когда вызывать:* Настройка и мониторинг VPS-сервера, проверка SSH-ключей, разбор логов авторизации `auth.log`, перезапуск Apache, управление Docker-контейнерами, Keenetic split-routing, бэкапы.
3.  **[git](file:///C:/Users/Артем/.gemini/config/skills/git/SKILL.md) — Git Workflow и Безопасность**
    *   *Когда вызывать:* Настройка pre-push вайтлистов, решение конфликтов, изменение локальных авторов коммитов (email/name) для командной разработки, решение проблем с большими файлами (>100MB).
4.  **[1c_unf](file:///C:/Users/Артем/.gemini/config/skills/1c_unf/SKILL.md) — Разработка и Интеграция 1С**
    *   *Когда вызывать:* OData API запросы, BSL стандарты программирования 1С, конфигурация портов 1С на сервере, сложные нюансы СКД, расчет себестоимости и закрытие месяца.
5.  **[session_management](file:///C:/Users/Артем/.gemini/config/skills/session_management/SKILL.md) — Управление сессиями ИИ**
    *   *Когда вызывать:* Подготовка `SESSION_SUMMARY.md` для архивации контекста, очистка мусора и переход в новый чистый чат (`/compress`).
6.  **[tender_automation](file:///C:/Users/Артем/.gemini/config/skills/tender_automation/SKILL.md) — Автоматизация тендеров и парсинг**
    *   *Когда вызывать:* Написание роботов для АСТ ГОЗ, извлечение спецификаций из DOCX/PDF таблиц, троттлинг запросов к Gemini API, слияние Excel-лотов с сохранением формул и стилей.
7.  **[email_ai_pipelines](file:///C:/Users/Артем/.gemini/config/skills/email_ai_pipelines/SKILL.md) — ИИ-пайплайны почты и follow-up сделок**
    *   *Когда вызывать:* Интеграция n8n с почтой/CRM, парсинг вложений (XLSX, PDF), боевой конвейер follow-up на сегодня (`process_today_followup_deals.py`), генерация черновиков в Roundcube IMAP, эскалация звонков при >=2 письмах, запросы OData 1С, pgvector миграции и SSH-туннели.
8.  **[metabase_analytics_ops](file:///C:/Users/Артем/.gemini/config/skills/metabase_analytics_ops/SKILL.md) — Аналитика и безопасность Metabase**
    *   *Когда вызывать:* Построение SQL-воронок, расчет снижения и НМЦК, скрытие баз данных и настройка прав доступа в Community Free версии Metabase, бэкап H2-базы.
9.  **[llm_quota_and_fallback_manager](file:///C:/Users/Артем/.gemini/config/skills/llm_quota_and_fallback_manager/SKILL.md) — Мультимодельный LLM Fallback и Квоты**
    *   *Когда вызывать:* Двухконтурная архитектура (Gemini ➔ DeepSeek при 429), адаптивный кулдаун RetryDelay, синхронизация таймаутов с n8n, изоляция пулов API-ключей, единое логирование токенов в PostgreSQL.
10. **[n8n_idempotent_crm_pipelines](file:///C:/Users/Артем/.gemini/config/skills/n8n_idempotent_crm_pipelines/SKILL.md) — Надежные n8n пайплайны и CRM**
    *   *Когда вызывать:* Настройка Auto-Retry в n8n, 100% защита от дубликатов сделок/компаний в Битрикс24 при повторах, диагностика flatted-ошибок в SQLite базе.
11. **[infra_management](file:///C:/Users/Артем/.gemini/config/skills/infra_management/SKILL.md) — Управление инфраструктурой и единым реестром**
    *   *Когда вызывать:* Инвентаризация проектов, аудит переменных окружения, массовая замена конфигураций (локально и на VPS), проверка работоспособности сервисов и актуализация карты зависимостей.
