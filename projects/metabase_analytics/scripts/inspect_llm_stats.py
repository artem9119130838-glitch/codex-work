#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inspects LLM usage statistics from marketing_db.llm_usage_logs.
"""
import os
import sys
import json
import psycopg2

try:
    from app.core.config import settings
    DATABASE_URL = settings.DATABASE_URL
except Exception:
    DATABASE_URL = os.environ.get("DATABASE_URL", "")

if "+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# 0. Backfill cost_usd for historical deepseek records
cur.execute("""
UPDATE llm_usage_logs 
SET cost_usd = ROUND((prompt_tokens * 0.14 + completion_tokens * 0.28) / 1000000.0, 6)
WHERE provider = 'deepseek' AND (cost_usd IS NULL OR cost_usd = 0) AND total_tokens > 0;
""")
updated_rows = cur.rowcount
conn.commit()
print(f"\n[DWH BACKFILL] Обновлено исторических записей DeepSeek: {updated_rows}")

print("\n=== 1. ОБЩИЙ РАСХОД ПО ПРОВАЙДЕРАМ И МОДЕЛЯМ ===")
cur.execute("""
SELECT 
    provider, 
    model_name, 
    status,
    COUNT(*) as total_calls, 
    COALESCE(SUM(total_tokens), 0) as tokens, 
    ROUND(COALESCE(SUM(estimated_cost), 0)::numeric, 4) as est_cost,
    ROUND(COALESCE(SUM(cost_usd), 0)::numeric, 4) as cost_usd,
    MIN(created_at) as first_seen,
    MAX(created_at) as last_seen
FROM llm_usage_logs
GROUP BY 1, 2, 3
ORDER BY tokens DESC;
""")
for r in cur.fetchall():
    print(f"Provider: {r[0]:<10} | Model: {r[1]:<22} | Status: {r[2]:<10} | Calls: {r[3]:<6} | Tokens: {r[4]:<10} | EstCost: ${r[5]:<8} | CostUSD: ${r[6]:<8} | First: {str(r[7])[:16]} | Last: {str(r[8])[:16]}")

print("\n=== 2. РАСХОД DEEPSEEK ПО ДНЯМ ===")
cur.execute("""
SELECT 
    DATE(created_at) as day,
    model_name,
    status,
    COUNT(*) as calls,
    COALESCE(SUM(total_tokens), 0) as tokens,
    ROUND(COALESCE(SUM(estimated_cost), 0)::numeric, 4) as est_cost
FROM llm_usage_logs
WHERE provider = 'deepseek' OR model_name LIKE '%deepseek%'
GROUP BY 1, 2, 3
ORDER BY day DESC;
""")
for r in cur.fetchall():
    print(f"Day: {str(r[0])} | Model: {r[1]:<18} | Status: {r[2]:<10} | Calls: {r[3]:<6} | Tokens: {r[4]:<10} | EstCost: ${r[5]}")

print("\n=== 3. РАСХОД DEEPSEEK ПО ИНИЦИАТОРАМ И ТИПАМ ЗАДАЧ ===")
cur.execute("""
SELECT 
    initiated_by,
    task_type,
    project_name,
    status,
    COUNT(*) as calls,
    COALESCE(SUM(total_tokens), 0) as tokens,
    ROUND(COALESCE(SUM(cost_usd), 0)::numeric, 4) as cost_usd
FROM llm_usage_logs
WHERE provider = 'deepseek' OR model_name LIKE '%deepseek%'
GROUP BY 1, 2, 3, 4
ORDER BY tokens DESC;
""")
for r in cur.fetchall():
    print(f"Initiator: {str(r[0]):<20} | Task: {str(r[1]):<30} | Project: {str(r[2]):<15} | Status: {r[3]:<10} | Calls: {r[4]:<5} | Tokens: {r[5]:<10} | Cost: ${r[6]}")

print("\n=== 4. ПОСЛЕДНИЕ 10 ЗАПИСЕЙ DEEPSEEK ===")
cur.execute("""
SELECT 
    created_at,
    initiated_by,
    task_type,
    prompt_tokens,
    completion_tokens,
    total_tokens,
    cost_usd,
    status,
    error_message
FROM llm_usage_logs
WHERE provider = 'deepseek' OR model_name LIKE '%deepseek%'
ORDER BY created_at DESC
LIMIT 10;
""")
for r in cur.fetchall():
    err = (r[8][:50] if r[8] else "None")
    print(f"Time: {str(r[0])[:19]} | Init: {str(r[1]):<15} | Task: {str(r[2]):<25} | Tokens: {r[5]:<6} | Cost: ${r[6]:<7} | Status: {r[7]} | Err: {err}")

conn.close()
