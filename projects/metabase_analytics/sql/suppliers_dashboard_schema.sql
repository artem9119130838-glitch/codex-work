-- =====================================================================
-- DWH Schema: Supplier Base & Search Tasks Analytics (China Supply)
-- Database: PostgreSQL (marketing_db)
-- Version: 1.0 (2026-11-08)
-- =====================================================================

-- 1. Реестр задач на поиск поставщиков (RFQ / 找货)
CREATE TABLE IF NOT EXISTS analytics_supplier_search_tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500),
    responsible_id INT,
    responsible_name VARCHAR(255),
    created_date TIMESTAMP WITH TIME ZONE,
    closed_date TIMESTAMP WITH TIME ZONE,
    status INT, -- 2: Ждет выполнения, 3: В работе, 5: Завершена
    group_id INT,
    template_id INT,
    tags JSONB DEFAULT '[]'::jsonb,
    uf_crm_raw JSONB DEFAULT '[]'::jsonb,
    attached_companies_count INT DEFAULT 0,
    attached_company_ids JSONB DEFAULT '[]'::jsonb,
    has_supplier_attached BOOLEAN DEFAULT FALSE,
    b24_url VARCHAR(500),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_supp_tasks_closed_date ON analytics_supplier_search_tasks(closed_date);
CREATE INDEX IF NOT EXISTS idx_supp_tasks_resp ON analytics_supplier_search_tasks(responsible_id);
CREATE INDEX IF NOT EXISTS idx_supp_tasks_has_supp ON analytics_supplier_search_tasks(has_supplier_attached);

-- 2. Реестр созданных компаний-поставщиков в CRM Битрикс24
CREATE TABLE IF NOT EXISTS analytics_supplier_companies (
    company_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500),
    company_type VARCHAR(50), -- SUPPLIER, CONTRACTOR, CUSTOMER
    created_by_id INT,
    created_by_name VARCHAR(255),
    assigned_by_id INT,
    date_create TIMESTAMP WITH TIME ZONE,
    has_contact BOOLEAN DEFAULT FALSE,
    has_phone BOOLEAN DEFAULT FALSE,
    has_email BOOLEAN DEFAULT FALSE,
    has_wechat BOOLEAN DEFAULT FALSE,
    has_comment BOOLEAN DEFAULT FALSE,
    comment_text TEXT,
    phone_numbers JSONB DEFAULT '[]'::jsonb,
    email_addresses JSONB DEFAULT '[]'::jsonb,
    is_complete BOOLEAN DEFAULT FALSE, -- 100% заполненность
    completeness_score INT DEFAULT 0, -- 0..100%
    missing_fields JSONB DEFAULT '[]'::jsonb,
    b24_url VARCHAR(500),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_supp_comp_date_create ON analytics_supplier_companies(date_create);
CREATE INDEX IF NOT EXISTS idx_supp_comp_creator ON analytics_supplier_companies(created_by_id);
CREATE INDEX IF NOT EXISTS idx_supp_comp_complete ON analytics_supplier_companies(is_complete);

-- 3. Аналитическое представление: Еженедельная и ежедневная матрица выполнения нормы
CREATE OR REPLACE VIEW v_supplier_weekly_performance AS
WITH daily_stats AS (
    SELECT
        created_by_id AS user_id,
        created_by_name AS user_name,
        DATE(date_create AT TIME ZONE 'Asia/Shanghai') AS work_date,
        COUNT(*) AS suppliers_added,
        COUNT(*) FILTER (WHERE is_complete = TRUE) AS suppliers_complete
    FROM analytics_supplier_companies
    WHERE created_by_id IN (30, 44, 84, 86, 20)
    GROUP BY created_by_id, created_by_name, DATE(date_create AT TIME ZONE 'Asia/Shanghai')
),
daily_tasks AS (
    SELECT
        responsible_id AS user_id,
        responsible_name AS user_name,
        DATE(closed_date AT TIME ZONE 'Asia/Shanghai') AS work_date,
        COUNT(*) AS tasks_closed,
        COUNT(*) FILTER (WHERE has_supplier_attached = FALSE) AS tasks_without_supplier
    FROM analytics_supplier_search_tasks
    WHERE status = 5 AND responsible_id IN (30, 44, 84, 86, 20)
    GROUP BY responsible_id, responsible_name, DATE(closed_date AT TIME ZONE 'Asia/Shanghai')
)
SELECT
    COALESCE(s.user_id, t.user_id) AS user_id,
    COALESCE(s.user_name, t.user_name) AS user_name,
    COALESCE(s.work_date, t.work_date) AS work_date,
    TO_CHAR(COALESCE(s.work_date, t.work_date), 'Dy') AS day_of_week,
    EXTRACT(ISODOW FROM COALESCE(s.work_date, t.work_date)) AS day_num,
    DATE_TRUNC('week', COALESCE(s.work_date, t.work_date))::DATE AS week_start,
    COALESCE(s.suppliers_added, 0) AS suppliers_added,
    COALESCE(s.suppliers_complete, 0) AS suppliers_complete,
    COALESCE(t.tasks_closed, 0) AS tasks_closed,
    COALESCE(t.tasks_without_supplier, 0) AS tasks_without_supplier,
    CASE 
        WHEN COALESCE(s.suppliers_added, 0) >= 3 THEN 'Норма выполнена (3+)'
        WHEN COALESCE(s.suppliers_added, 0) BETWEEN 1 AND 2 THEN 'Частично (1-2)'
        ELSE 'Пропуск (0)'
    END AS daily_status
FROM daily_stats s
FULL OUTER JOIN daily_tasks t 
    ON s.user_id = t.user_id AND s.work_date = t.work_date;
