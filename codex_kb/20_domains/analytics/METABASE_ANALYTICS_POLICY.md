# Регламент сквозной аналитики и эксплуатации Metabase (Metabase Analytics Policy)

> **Статус документа:** Непререкаемый стандарт архитектуры витрин данных (DWH), дашбордов и безопасности BI-сервера Metabase.  
> **Хост BI:** `http://109.248.170.181:3000` (Docker `metabase`).  
> **База DWH:** PostgreSQL `marketing_db` (порт `5433`, хост `10.10.0.1`, изолированный пользователь `vector_user`).  
> **Связанный проект:** [metabase_analytics](file:///C:/Codex/projects/metabase_analytics/README.md)  
> **Связанные навыки:** [metabase_analytics_ops](file:///C:/Users/Артем/.gemini/config/skills/metabase_analytics_ops/SKILL.md), [linux](file:///C:/Users/Артем/.gemini/config/skills/linux/SKILL.md).

---

## 1. Архитектурная модель данных (DWH & Marts)

1. **Изоляция боевых систем:**
   * Аналитические запросы Metabase категорически запрещено направлять напрямую в рабочую базу 1С:УНФ (`unf`).
   * Источником аналитики является реплицированное хранилище PostgreSQL `marketing_db`.
2. **Канонические витрины данных:**
   * `analytics_closed_deals`: агрегированные карточки закрытых сделок (сумма НМЦК, сумма нашего предложения, причины отказов, ФИО ответственного, наименование заказчика, сырой payload JSONB).
   * `analytics_deal_stage_history`: хронология переходов сделок по этапам воронок (`deal_id`, `stage_id`, `date_entered`).

---

## 2. Стандарты построения SQL-карточек и воронок

1. **Финансовые метрики выигранных сделок:**
   * Для всех таблиц и срезов побед обязательны 4 финансовых поля:
     1. `НМЦК (руб)` — `tender_amount`
     2. `Сумма контракта (руб)` — `our_offer_amount`
     3. `Разница (руб)` — `(tender_amount - our_offer_amount)`
     4. `Снижение (%)` — `ROUND(((tender_amount - our_offer_amount) / NULLIF(tender_amount, 0)) * 100, 2)`
   * В итоговых строках виджета Metabase выводить: сумму по деньгам и **среднее значение** по проценту снижения.
2. **Защита от сбоев кодировок (Windows / Linux / SSH):**
   * В фильтрах `WHERE` и условиях `CASE` использовать латинские идентификаторы стадий (`WON`, `C4:LOSE`, `C4:EXECUTING`) либо маппинг из `CLOSE_REASON_MAP`.
3. **Глобальное форматирование чисел:**
   * Разделитель тысяч — строго **пробел** (`41 041 212.76`), разделитель десятичных знаков — **точка**, валюта — **RUB**.

---

## 3. Разграничение прав доступа (Community Free Edition)

В бесплатной редакции Metabase прямое отключение баз через UI выдает ошибку 500. Для надежной изоляции данных от менеджеров применяется регламент:
1. **Группа «All Users» (ID 1):**
   * `"view-data": "legacy-no-self-service"`
   * `"create-queries": "no"`
   * Это скрывает раздел «Данные» и SQL-редактор, защищая базу от неоптимальных или несанкционированных запросов.
2. **Коллекция менеджеров:**
   * Менеджеры имеют права `read` только на свою коллекцию (например, «Аналитика продаж»). На корневые и системные коллекции устанавливается `none`.

---

## 4. Ресурсная дисциплина и OOM Guard (VPS)

1. **Потребление оперативной памяти:**
   * Контейнер Metabase потребляет ~3.5 ГБ RAM из-за JVM.
2. **Правило тяжелых сборок (Heavy Docker Build Rule):**
   * При сборке тяжелых образов (например, `tender-rag-api`) контейнер Metabase временно останавливается (`docker stop metabase`) во избежание падения сервера по Out Of Memory (код 137).
   * После завершения деплоя контейнер перезапускается (`docker start metabase`), а порт 3000 проверяется через `ss -tulpn`.
3. **Запрет `docker-compose down`:**
   * При обновлении соседних сервисов запрещено использовать `docker-compose down`, так как это сносит общую docker-сеть, к которой подключен Metabase.

---

## 5. Резервное копирование и управление паролями H2

1. **Регламент бэкапа:**
   * Файл БД H2 `/Storage/docker/metabase_data/metabase.db/metabase.db.mv.db` копируется скриптом `/Storage/run_server_backup.sh` строго после кратковременного `docker stop metabase`.
2. **Сброс паролей в H2:**
   * Пароли в Metabase солятся UUID-значением из `PASSWORD_SALT`. Формула: `bcrypt(PASSWORD_SALT + RAW_PASSWORD)`.
   * Рекомендуемый путь сброса пароля без доступа к UI — вызов встроенного jar через Docker CLI:
     ```bash
     docker stop metabase && \
     docker run --rm -v /Storage/docker/metabase_data:/metabase-data \
       -e MB_DB_FILE=/metabase-data/metabase.db/metabase.db \
       --entrypoint "/opt/java/openjdk/bin/java" \
       metabase/metabase:latest -jar /app/metabase.jar reset-password <EMAIL> && \
     docker start metabase
     ```

---

## 6. Жизненный цикл скриптов и Dry-Run First

1. **Канонические скрипты:**
   * `projects/metabase_analytics/scripts/manage_metabase_dashboards.py`
   * `projects/metabase_analytics/scripts/sync_analytics_dwh.py`
2. **Обязательный Dry-run:** Любое обновление карточек или массовая синхронизация сначала проверяются с ключом `--dry-run`.
3. **Zero Secrets:** Токены вебхуков CRM, пароли базы данных и Metabase API передаются строго через переменные окружения (`B24_WEBHOOK_URL`, `PG_PASS`, `METABASE_ADMIN_PASSWORD`).

---

## 7. Сквозной учет токенов LLM и атрибуция инициаторов

1. **Таблицы учета:**
   * `llm_usage_logs`: детальный аудит каждого вызова нейросетей (токены, стоимость, время ответа, статус).
   * `llm_keys_status`: мониторинг здоровья API-ключей (`ACTIVE`, `RATE_LIMITED_DAILY`, `DEAD_REVOKED`).
2. **Обязательная таксономия задач (`task_type`):**
   * `tenders_extraction` (тендеры), `lead_inbound_triage` (почта), `lead_rfq_drafting` (расчет КП), `sales_followup` (сделки), `china_supplier_audit` (ВЭД), `client_scoring_dossier` (скоринг), `system_test_dev` (тесты).
   * **Группа «Реанимация старых лидов» (`lead_reactivation`):**
     - `reactivation_email_summary`: суммаризация истории переписки (ежечасный сбор контекста).
     - `reactivation_draft_generation`: генерация черновиков реанимации клиентам.
3. **3-уровневая атрибуция инициатора (`initiated_by`):**
   * `artem` (ПК Артема, `os.getlogin() == 'Артем'`).
   * `mikhail` (VPS контур `/home/mikhail/tender-rag-api`).
   * `system_cron` / `system_automation` (фоновые демоны).
   * `b24_user_<ID>` (действия менеджеров в Битрикс24, передаваемые через вебхук).
4. **Multi-Metric Scale Separation Guard (Визуальная дисциплина дашбордов):**
   * Запрещено выводить на одну столбчатую диаграмму метрики с разницей порядков более $10^2$ (например, "Всего токенов" ~600 000 000 и "Затраты ($)" ~150).
   * Для комплексных срезов (Инициатор, Ключ, Статус) использовать строго **табличный вид** (`display: table`).
   * Для графиков и диаграмм выводить **ровно одну ключевую метрику** (например, только Затраты ($) или только Доля вызовов %).
5. **Инвариант типизации Field Filter (Integer Field ID Invariant):**
   * В Native SQL запросах Metabase параметры типа `dimension` (Field Filter) в структуре `template-tags` обязаны содержать **числовой идентификатор поля** (`["field", field_id, None]`), полученный через API метаданных `/api/database/:id/metadata`.
   * Категорически запрещено передавать строковое имя колонки (например, `["field", "date_create", ...]`), так как внутренняя база Metabase (H2) при выполнении выборки из `METABASE_FIELD` падает с ошибкой приведения типов `Data conversion error [22018-214]`.
6. **Каноническая структура раздела «Расход и статистика LLM» (Collection 7):**
   * Единый активный дашборд: **«Мониторинг лимитов и ключей LLM» (Dashboard ID 8)**. Пустые и дублирующие дашборды подлежат немедленной архивации.
   * Виджеты дашборда:
     - Card 68 (`display: table`): Расход токенов по API-ключам (`gemini-pool`, `deepseek-main`), разделение успешных вызовов и таймаутов, расчет затрат ($).
     - Card 70 (`display: table`): Расход токенов по инициаторам (`artem`, `mikhail`, `system_automation`) с разделением успешных вызовов и ошибок.
     - Card 72 (`display: table`): Светофор здоровья пула API-ключей (`llm_keys_status`).
     - Card 69 (`display: pie`): Распределение токенов по типам бизнес-задач (`task_type`).
     - Card 71 (`display: line`): Хронологическая динамика расхода токенов и затрат по дням и провайдерам.
7. **Утилиты управления:**
   * Диагностика и отсев ключей: `py projects/metabase_analytics/scripts/audit_llm_keys.py`.
   * Модуль логирования: `projects/metabase_analytics/scripts/llm_tracker.py`.
   * Канонический конвейер деплоя: `py projects/metabase_analytics/scripts/manage_metabase_dashboards.py`.

---

## 8. Регламент ночной реконсилиации DWH (Nightly Reconciliation Cron)

1. **Назначение:** Довыгрузка сделок за последние 3 дня на случай сбоев или таймаутов входящих вебхуков n8n.
2. **Расписание на сервере VPS:**
   ```bash
   # Выполняется ежедневно в 03:00 ночи
   0 3 * * * /usr/bin/python3 /Storage/scripts/sync_analytics_dwh.py --days 3 >> /var/log/sync_analytics_dwh.log 2>&1
   ```
