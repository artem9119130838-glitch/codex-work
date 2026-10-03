-- =====================================================================
-- DWH Schema: Metabase Analytics & LLM Token Economics
-- Database: PostgreSQL (marketing_db)
-- Version: 2.1 (2026-10-03)
-- =====================================================================

-- 1. Сделки CRM и Тендерные закупки
CREATE TABLE IF NOT EXISTS analytics_closed_deals (
    deal_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255),
    tender_number VARCHAR(255),
    date_create TIMESTAMP,
    date_close TIMESTAMP,
    stage_id VARCHAR(50),
    close_reason VARCHAR(255),
    responsible_name VARCHAR(255),
    customer_name VARCHAR(255),
    tender_amount NUMERIC,
    our_offer_amount NUMERIC,
    delivery_time VARCHAR(255),
    payment_terms VARCHAR(255),
    raw_data JSONB,
    pipeline_name VARCHAR(100),
    is_won BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_closed_deals_date_close ON analytics_closed_deals(date_close);
CREATE INDEX IF NOT EXISTS idx_closed_deals_pipeline ON analytics_closed_deals(pipeline_name);
CREATE INDEX IF NOT EXISTS idx_closed_deals_reason ON analytics_closed_deals(close_reason);

-- 2. История переходов сделок по этапам (Динамика движения)
CREATE TABLE IF NOT EXISTS analytics_deal_stage_history (
    id SERIAL PRIMARY KEY,
    deal_id VARCHAR(50),
    stage_id VARCHAR(50),
    date_entered TIMESTAMP WITH TIME ZONE,
    UNIQUE (deal_id, stage_id)
);

CREATE INDEX IF NOT EXISTS idx_stage_hist_date_entered ON analytics_deal_stage_history(date_entered);
CREATE INDEX IF NOT EXISTS idx_stage_hist_stage_id ON analytics_deal_stage_history(stage_id);

-- 3. Детальный лог расхода токенов и вызовов LLM
CREATE TABLE IF NOT EXISTS llm_usage_logs (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    initiated_by VARCHAR(50) DEFAULT 'system_automation',
    task_type VARCHAR(50) DEFAULT 'general',
    key_alias VARCHAR(50) DEFAULT 'unknown',
    provider VARCHAR(30) NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    prompt_tokens INT DEFAULT 0,
    completion_tokens INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    cost_usd NUMERIC(10, 6) DEFAULT 0,
    latency_ms INT DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    error_message TEXT
);

-- Migration for existing llm_usage_logs table if created previously
ALTER TABLE llm_usage_logs ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE llm_usage_logs ADD COLUMN IF NOT EXISTS initiated_by VARCHAR(50) DEFAULT 'system_automation';
ALTER TABLE llm_usage_logs ADD COLUMN IF NOT EXISTS task_type VARCHAR(50) DEFAULT 'general';
ALTER TABLE llm_usage_logs ADD COLUMN IF NOT EXISTS key_alias VARCHAR(50) DEFAULT 'unknown';
ALTER TABLE llm_usage_logs ADD COLUMN IF NOT EXISTS cost_usd NUMERIC(10, 6) DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_llm_logs_created_at ON llm_usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_llm_logs_task_type ON llm_usage_logs(task_type);
CREATE INDEX IF NOT EXISTS idx_llm_logs_key_alias ON llm_usage_logs(key_alias, status);
CREATE INDEX IF NOT EXISTS idx_llm_logs_initiator ON llm_usage_logs(initiated_by);

-- 4. Реестр здоровья и доступности API-ключей (Key Health Registry)
CREATE TABLE IF NOT EXISTS llm_keys_status (
    key_alias VARCHAR(50) PRIMARY KEY,
    provider VARCHAR(30) NOT NULL,
    masked_key VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL,
    last_tested_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    last_error_code INT,
    last_error_message TEXT,
    total_calls INT DEFAULT 0,
    total_errors INT DEFAULT 0,
    consecutive_errors INT DEFAULT 0
);
