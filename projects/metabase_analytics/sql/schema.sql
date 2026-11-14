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
    is_won BOOLEAN DEFAULT FALSE,
    has_advance BOOLEAN DEFAULT FALSE,
    advance_percent NUMERIC DEFAULT 0,
    advance_details TEXT
);

-- Migrations for existing analytics_closed_deals table
ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS has_advance BOOLEAN DEFAULT FALSE;
ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS advance_percent NUMERIC DEFAULT 0;
ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS advance_details TEXT;

CREATE INDEX IF NOT EXISTS idx_closed_deals_date_close ON analytics_closed_deals(date_close);
CREATE INDEX IF NOT EXISTS idx_closed_deals_pipeline ON analytics_closed_deals(pipeline_name);
CREATE INDEX IF NOT EXISTS idx_closed_deals_reason ON analytics_closed_deals(close_reason);
CREATE INDEX IF NOT EXISTS idx_closed_deals_has_advance ON analytics_closed_deals(has_advance);

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

-- 5. Детальная товарная и поставщиковая аналитика по сделкам (с мая 2026)
CREATE TABLE IF NOT EXISTS analytics_deal_products (
    deal_id VARCHAR(50) NOT NULL,
    item_index INT NOT NULL DEFAULT 1,
    pipeline_name VARCHAR(100),
    title VARCHAR(500),
    tender_number VARCHAR(255),
    customer_name VARCHAR(255),
    date_create TIMESTAMP,
    date_close TIMESTAMP,
    current_stage_id VARCHAR(50),
    current_stage_name VARCHAR(120),
    reached_stage_max VARCHAR(120),
    outcome_bucket VARCHAR(50),
    outcome_label VARCHAR(120),
    close_reason VARCHAR(255),
    responsible_name VARCHAR(255),
    supply_responsible_name VARCHAR(255),
    deal_amount NUMERIC DEFAULT 0,
    is_multi_item BOOLEAN DEFAULT FALSE,
    raw_item_name TEXT,
    wide_group VARCHAR(150),
    narrow_group VARCHAR(180),
    procurement_nature VARCHAR(80),
    brand_or_spec VARCHAR(180),
    supplier_pool_type VARCHAR(150),
    supplier_profile VARCHAR(200),
    actual_supplier VARCHAR(255),
    supplier_interaction_comment TEXT,
    extraction_source VARCHAR(50),
    b24_url VARCHAR(500),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (deal_id, item_index)
);

CREATE INDEX IF NOT EXISTS idx_deal_prod_wide ON analytics_deal_products(wide_group);
CREATE INDEX IF NOT EXISTS idx_deal_prod_narrow ON analytics_deal_products(narrow_group);
CREATE INDEX IF NOT EXISTS idx_deal_prod_pool ON analytics_deal_products(supplier_pool_type);
CREATE INDEX IF NOT EXISTS idx_deal_prod_nature ON analytics_deal_products(procurement_nature);
CREATE INDEX IF NOT EXISTS idx_deal_prod_outcome ON analytics_deal_products(outcome_bucket);
CREATE INDEX IF NOT EXISTS idx_deal_prod_pipeline ON analytics_deal_products(pipeline_name);
CREATE INDEX IF NOT EXISTS idx_deal_prod_date_create ON analytics_deal_products(date_create);

