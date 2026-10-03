# Комплексный аудит наработок по Metabase и план стандартизации по Новой Системе

> **Дата аудита:** 03 октября 2026 г.  
> **Статус:** Анализ завершен, сформирован инвентарь артефактов и пошаговый план миграции.  
> **Связанный навык:** [metabase_analytics_ops](file:///C:/Users/Артем/.gemini/config/skills/metabase_analytics_ops/SKILL.md)  
> **Инфраструктурный паспорт:** [SERVER_VPS.md](file:///C:/Codex/codex_kb/10_assets/SERVER_VPS.md)

---

## 1. Резюме аудита: Что у нас есть сейчас

В контуре проделан колоссальный объем работы по созданию сквозной бизнес-аналитики. У нас развернут боевой сервис Metabase, настроены аналитические таблицы в PostgreSQL, созданы пайплайны синхронизации с Битрикс24 и автоматизирована сборка дашбордов через API.

Однако эти наработки создавались до утверждения текущей модульной архитектуры Codex. Они разрознены, частично хранятся в read-only репозитории `tender-rag-api`, содержат хардкод секретов и не имеют собственного проекта и доменного манифеста в `C:\Codex`.

---

## 2. Полный реестр существующих наработок

### 2.1. Инфраструктура и серверные активы (VPS)
* **Хост:** `http://109.248.170.181:3000` (Docker-контейнер `metabase`).
* **Внутренняя база (H2):** `/Storage/docker/metabase_data/metabase.db/metabase.db.mv.db`.
* **Потребление ресурсов:** ~3.5 ГБ RAM. Регламентировано отключение контейнера при тяжелых сборках Docker во избежание OOM 137.
* **Бэкапы:** включены в еженедельный скрипт сервера `/Storage/run_server_backup.sh` с предварительным `docker stop`.

### 2.2. База данных хранилища (DWH / Data Marts)
* **СУБД:** PostgreSQL (`marketing_db`, порт `5433`, хост `10.10.0.1`, пользователь `vector_user`).
* **Схема DDL:** [schema.sql](file:///C:/Users/Артем/tender-rag-api/analytics/db/schema.sql):
  - `analytics_closed_deals` (сделка, номер тендера, даты создания/закрытия, стадия, причина отказа, суммы, raw_data JSONB).
  - `analytics_deal_stage_history` (история переходов по стадиям воронок).

### 2.3. Скрипты синхронизации данных (ETL)
* **Ежедневная синхронизация B24 -> Postgres:** [b24_daily_analytics_sync.py](file:///C:/Users/Артем/tender-rag-api/scripts/b24_daily_analytics_sync.py):
  - Выкачивает закрытые сделки и историю стадий из CRM Битрикс24 через REST API.
  - Маппит 16 причин отказа (Нацрежим, Не нашли поставщика, Проиграли по цене и т.д.).
  - Нормализует стадии двух направлений (Общая воронка и Тендеры/Категория 4).
* **Генерация бэкфилла:** [generate_backfill_sql.py](file:///C:/Users/Артем/tender-rag-api/analytics/scripts/generate_backfill_sql.py).
* **Сценарии n8n (автосинхронизация по вебхуку):**
  - `n8n_analytics_sync_production.json` — продакшн-воркфлоу real-time синхронизации сделок по вебхукам `ONCRMDEALADD` и `ONCRMDEALUPDATE`.
  - `Analytics_Closed_Deals.json` и `Analytics_Stage_History.json`.

### 2.4. Скрипты деплоя дашбордов и управления Metabase API
* **Боевой деплой карточек и дашбордов:** [deploy_metabase_analytics.py](file:///C:/Users/Артем/tender-rag-api/scripts/deploy_metabase_analytics.py):
  - Автоматически настраивает Дашборд № 4 ("Сводная аналитика продаж").
  - Карточка 54: "Сквозная воронка" с поддержкой фильтра дат `{{date_range}}`.
  - Карточка 49: "Выигранные тендеры - Детали" (расчет НМЦК, дельты и снижения).
  - Карточка 61: "Динамика сквозной воронки по периодам (помесячно)".
  - Карточка 62: "Сравнение периодов: Август vs Июль (Google Analytics Style)".
* **Первичный мастер-сетап:** [setup_metabase.py](file:///C:/Users/Артем/tender-rag-api/analytics/tests/setup_metabase.py) — подключение базы `marketing_db`, создание базовых виджетов, круговых диаграмм отказов и прав доступа для менеджеров.
* **Черновой скрипт патчей:** [patch_metabase.py](file:///C:/Users/Артем/tender-rag-api/scratch/patch_metabase.py) — установка локали `ru`, разделителей тысяч (пробелы вместо запятых) и создание роли менеджера.

### 2.5. Скилл и документация
* **Готовый навык:** [metabase_analytics_ops](file:///C:/Users/Артем/.gemini/config/skills/metabase_analytics_ops/SKILL.md):
  - SQL-стандарты финансовых колонок (НМЦК, Сумма, Дельта, Снижение %).
  - Обход ограничений бесплатной Community Edition (`legacy-no-self-service`, скрытие сырых таблиц от менеджеров).
  - Сброс паролей в БД H2 через UUID salt + bcrypt или вызов CLI jar.
* **Руководство:** [metabase_guide_for_manager.md](file:///C:/Users/Артем/tender-rag-api/analytics/metabase_guide_for_manager.md) — пошаговый гайд запуска и проверки аналитики для руководителя.
* **Архивные ТЗ:** [ТЗ Аналитика тендеров в Metabase.docx](file:///C:/Users/Артем/tender-rag-api/docs/archive_tz/ТЗ%20Аналитика%20тендеров%20в%20Metabase.docx).

---

## 3. Гэп-анализ: Что не соответствует Новой Системе Codex

| № | Требование Новой Системы Codex (`AGENTS.md`) | Текущее фактическое состояние | В чем риск / проблема |
|---|---|---|---|
| **1** | **Изолированный проект в `C:\Codex\projects/`** | Все скрипты и схемы лежат в `C:\Users\Артем\tender-rag-api/` | Репозиторий `tender-rag-api` находится в режиме **Strict Read-Only**. Любая правка аналитики заблокирована правилами контура. |
| **2** | **Доменный манифест второго уровня (`codex_kb/20_domains/`)** | Манифест отсутствует. В `codex_kb/00_control/` скилл есть, но предметного регламента нет. | ИИ-ассистент при запросах про аналитику «не видит» контекст и не знает архитектурных ограничений. |
| **3** | **Маршрутизация в `AGENTS.md` (Раздел 8)** | Нет ключевых слов `metabase`, `дашборд`, `сквозная аналитика`, `воронка` | Нет автоматической On-Demand загрузки контекста аналитики. |
| **4** | **Canonical Single-Script Invariant** | Логика размазана между 5 скриптами (`deploy_metabase_analytics.py`, `setup_metabase.py`, `patch_metabase.py`, `b24_daily_analytics_sync.py`, `generate_backfill_sql.py`) | Дублирование кода авторизации, сложность поддержки, отсутствие единого CLI. |
| **5** | **Strict Change Policy & `--dry-run`** | В скриптах деплоя дашбордов нет флага `--dry-run` | Невозможно безопасно проверить планируемые изменения карточек до их применения через API. |
| **6** | **Zero Secrets Policy** | В скриптах присутствуют захардкоженные URL вебхуков Б24, пароли и логины | Риск утечки учетных данных в логи и репозитории. |
| **7** | **Архивирование версий (`scripts/archive/`)** | Архив версий отсутствует, промежуточные скрипты брошены в `scratch/` | Нарушение регламента версионирования при доработках. |

---

## 4. План наведения порядка (Roadmap стандартизации)

### Этап 1. Создание проектной структуры в Codex
Создать канонический проект: `C:\Codex\projects\metabase_analytics/`:
```text
C:\Codex\projects\metabase_analytics/
├── README.md                           # Паспорт проекта и архитектура DWH
├── docs/
│   ├── METABASE_GUIDE.md               # Перенос и актуализация metabase_guide_for_manager.md
│   └── ARCHITECTURE.md                 # Описание потоков данных (B24 -> Postgres -> Metabase)
├── sql/
│   ├── schema.sql                      # Каноническая DDL-схема таблиц аналитики
│   └── views/                          # SQL-запросы ключевых карточек (54, 49, 61, 62)
├── workflows/                          # Экспорт эталонных JSON сценариев n8n
│   └── n8n_analytics_sync_production.json
├── scripts/
│   ├── sync_analytics_dwh.py           # Единый боевой ETL-скрипт синхронизации данных (из b24_daily_analytics_sync.py)
│   ├── manage_metabase_dashboards.py   # Единый боевой скрипт деплоя карточек и дашбордов (из deploy/setup/patch)
│   └── archive/                        # Снимки версий скриптов перед модификациями
└── scratch/                            # Черновые и отладочные утилиты
```

### Этап 2. Создание Доменного Манифеста
Создать манифест `C:\Codex\codex_kb\20_domains\analytics\METABASE_ANALYTICS_POLICY.md`:
* Стандарты именования карточек и дашбордов.
* Правила разграничения прав доступа (Community Edition).
* Регламенты безопасности при обращении к базе `marketing_db` (Read-only пользователи, индексы).
* Защита от OOM при работе Metabase в Docker на VPS.

### Этап 3. Доработка и объединение скриптов (Single-Script Invariant)
1. **`manage_metabase_dashboards.py`**:
   - Объединить функционал `deploy_metabase_analytics.py`, `setup_metabase.py` и `patch_metabase.py`.
   - Добавить аргументы CLI: `--setup`, `--update-cards`, `--patch-locale`, `--create-manager`.
   - Внедрить обязательный флаг `--dry-run` с выводом diff обновляемых карточек.
   - Исключить хардкод учетных данных: читать из `os.getenv("METABASE_ADMIN_PASSWORD")` и `os.getenv("METABASE_URL")`.
2. **`sync_analytics_dwh.py`**:
   - Вынести учетные данные PostgreSQL и вебхука Битрикс24 в переменные окружения.
   - Добавить субкоманды `--incremental` (за последние N дней), `--full-backfill`, `--dry-run`.

### Этап 4. Регистрация в диспетчерах и каталогах Codex
1. **Обновление `AGENTS.md`**:
   - Добавить строку в Таблицу Маршрутизации (Раздел 8): ключевые слова «metabase, дашборд, аналитика, сквозная воронка, dwh» -> ссылка на `METABASE_ANALYTICS_POLICY.md`.
2. **Обновление скилла `metabase_analytics_ops`**:
   - Добавить прямые ссылки на проект `C:\Codex\projects\metabase_analytics\`, схемы DWH и канонические скрипты.
3. **Обновление [SCRIPTS_CATALOG.md](file:///C:/Codex/codex_kb/SCRIPTS_CATALOG.md)**:
   - Перелинковать скрипты Metabase из `tender-rag-api` на новый канонический проект в `projects/metabase_analytics/`.
