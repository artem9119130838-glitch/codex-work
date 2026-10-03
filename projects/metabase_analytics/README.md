# Проект: Metabase Analytics & Business Intelligence (DWH)

> **Статус:** Активен (Канонический контур аналитики)  
> **Инфраструктурный хост:** `http://109.248.170.181:3000` (Docker)  
> **База данных DWH:** PostgreSQL `marketing_db` (порт 5433, хост 10.10.0.1)  
> **Доменный манифест:** [METABASE_ANALYTICS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/analytics/METABASE_ANALYTICS_POLICY.md)  
> **Связанный навык:** [metabase_analytics_ops](file:///C:/Users/Артем/.gemini/config/skills/metabase_analytics_ops/SKILL.md)

---

## 1. Назначение проекта

Проект обеспечивает сбор, нормализацию, хранение и интерактивную визуализацию бизнес-метрик коммерческого и тендерного направлений:
1. **Сквозная воронка продаж:** отслеживание конверсий между стадиями (Анализ -> ВЭД -> Расчет КП -> Подача -> Победа/Проигрыш).
2. **Анализ выигранных тендеров:** финансовые показатели (НМЦК, сумма предложения, процент снижения, абсолютная маржа).
3. **Анализ причин отказов:** сегментация потерь (нацрежим, проигрыш по цене, не успели подать заявку и т.д.).
4. **Процессный пульс CRM:** динамика продвижения сделок менеджерами по календарным месяцам.

---

## 2. Архитектура потоков данных (ETL & BI)

```
CRM Битрикс24 (Сделки, Контакты, Компании)
   │
   ├─► Real-Time Webhook (ONCRMDEALADD / UPDATE) ──► n8n (workflows/n8n_analytics_sync_production.json)
   │                                                        │
   └─► Периодический / Инкрементальный ETL                  ▼
       (scripts/sync_analytics_dwh.py) ──────────────► PostgreSQL DWH (marketing_db)
                                                             │  - analytics_closed_deals
                                                             │  - analytics_deal_stage_history
                                                             ▼
                                                      Metabase BI Server (:3000)
                                                        (управление: scripts/manage_metabase_dashboards.py)
                                                             │
                                                             ▼
                                                      Дашборды и Виджеты (Дашборд № 4)
```

---

## 3. Структура каталога

* **`docs/`**:
  * [METABASE_GUIDE.md](file:///C:/Codex/projects/metabase_analytics/docs/METABASE_GUIDE.md) — пошаговое руководство администратора и менеджера.
* **`sql/`**:
  * [schema.sql](file:///C:/Codex/projects/metabase_analytics/sql/schema.sql) — DDL-схемы витрин данных.
* **`workflows/`**:
  * `n8n_analytics_sync_production.json` — сценарий n8n для real-time синхронизации сделок по вебхукам.
* **`scripts/`**:
  * `manage_metabase_dashboards.py` — единый боевой CLI-скрипт деплоя карточек, дашбордов и управления правами через Metabase REST API (поддерживает `--dry-run`).
  * `sync_analytics_dwh.py` — боевой ETL-скрипт синхронизации данных из CRM в PostgreSQL (инкремент / полный бэкфилл, `--dry-run`).
  * `archive/` — версионные снимки скриптов перед модификациями.
* **`scratch/`**:
  * черновики и разовые отладочные запросы.
