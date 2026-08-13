---
name: LLM Quota and Multi-Tier Fallback Manager
description: Управление квотами LLM API, адаптивные кулдауны RetryDelay Gemini, изоляция пулов ключей и бесшовный фолбэк на DeepSeek.
---

# Навык: LLM Quota and Multi-Tier Fallback Manager

Этот навык регламентирует обеспечение 100% аптайма ИИ-сервисов при жестких суточных лимитах бесплатных API и минимальных затратах.

## 1. Двухконтурная архитектура (Multi-Tier LLM Architecture)
Бесплатные тарифы (например, Gemini 3.5 Flash с лимитом 20 RPD) не могут гарантировать непрерывность бизнес-процессов при пиковых нагрузках.
* **Схема работы:**
  1. *Основной контур:* Запросы направляются в пул бесплатных ключей Gemini (`GEMINI_API_KEYS`).
  2. *Аварийное переключение (Fallback):* При исчерпании суточных лимитов (ошибка 429) сервис мгновенно и без зависаний переключается на DeepSeek API (`https://api.deepseek.com/chat/completions`, модель `deepseek-chat`).
  3. *Автовозврат:* Утром при обновлении бесплатных квот Google сервис автоматически возобновляет работу с бесплатным Gemini.

## 2. Обработка минутных лимитов (RPM RetryDelay)
* При получении ошибки 429 от Gemini сервис обязан парсить точный параметр `retryDelay` из структуры `google.rpc.RetryInfo` (например, `35s`).
* Выдерживать адаптивную паузу `sleep(retryDelay + 2)` вместо быстрых 5-секундных ретраев, сжигающих попытки.

## 3. Синхронизация таймаутов с оркестратором (n8n)
* Общее время ожидания ретраев внутри бэкенда (`retries * sleep`) не должно превышать таймаут входящего HTTP-запроса из n8n (обычно 300 секунд).
* Если Gemini за 1–2 быстрые попытки (до 30–60 сек) не отвечает — немедленно активировать DeepSeek-фолбэк, предотвращая сетевой обрыв (`timeout of 300000ms exceeded`).

## 4. Изоляция пулов ключей и бюджетные предохранители
* **Изоляция:** Категорически запрещено дублировать одни и те же основные Gemini API-ключи между независимыми сервисами (почта vs тендеры). Каждый сервис имеет свой независимый пул ключей в `.env`.
* **Предохранители:** На платных провайдерах (DeepSeek) обязательно внедрять суточный счетчик запросов в JSON (например, лимит 50 вызовов/сутки в почтовом сервисе), гарантирующий защиту от перерасхода бюджета.

## 5. Предотвращение минутных всплесков (RPM Burst Pacing)
* Бесплатные модели Gemini (Flash, Flash-Lite) имеют жесткий лимит 15 RPM (запросов в минуту).
* При пакетной обработке (генерация черновиков, парсинг файлов в цикле) бэкенд обязан делать принудительную паузу не менее 5 секунд (`time.sleep(5.0)`) между запросами, предотвращая ошибку `429 RESOURCE_EXHAUSTED / QUOTA_EXCEEDED`.

## 6. Единая схема учета токенов и расходов (LLM Usage Logging)
Все вызовы LLM должны автоматически логироваться в единую таблицу PostgreSQL `llm_usage_logs`:
```sql
CREATE TABLE IF NOT EXISTS llm_usage_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    provider VARCHAR(50) NOT NULL,            -- 'gemini', 'deepseek', 'openai'
    api_key_masked VARCHAR(50) NOT NULL,      -- 'AQ.Ab8RN...VuTA'
    model_name VARCHAR(100) NOT NULL,         -- 'gemini-2.5-flash', 'deepseek-chat'
    request_type VARCHAR(100),                -- 'generate_draft', 'generate_summary', 'classify_junk'
    prompt_tokens INT DEFAULT 0,
    completion_tokens INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    estimated_cost_rub NUMERIC(10, 4) DEFAULT 0,
    latency_ms INT DEFAULT 0,
    status VARCHAR(20) NOT NULL,              -- 'success', 'rate_limit', 'error'
    error_message TEXT
);
```
Таблица используется для визуализации расходов в Metabase и расчета точной себестоимости генераций.
