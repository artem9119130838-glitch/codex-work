import subprocess
import json
import os
import sys

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.stdout.strip(), p.stderr.strip(), p.returncode

print("=== 1. TABLES & VIEWS IN marketing_db ===")
sql = "SELECT table_type, table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_type, table_name;"
stdout, _, _ = run_cmd(f"docker exec pgvector-db psql -U vector_user -d marketing_db -c \"{sql}\"")
print(stdout)

print("\n=== 2. INDEXES IN marketing_db ===")
sql_indexes = """
SELECT tablename, indexname, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"""
stdout, _, _ = run_cmd(f"docker exec pgvector-db psql -U vector_user -d marketing_db -c \"{sql_indexes}\"")
print(stdout)

print("\n=== 3. CONTOUR SUMMARY (BY CURRENT STAGE) ===")
sql_stages = """
SELECT 
    current_stage,
    COUNT(*) as total_folders,
    ROUND(SUM(COALESCE(nmck_amount, 0))::numeric / 1000000, 2) as sum_mln_rub,
    MIN(created_at) as earliest_created,
    MAX(created_at) as latest_created,
    MIN(updated_at) as earliest_updated,
    MAX(updated_at) as latest_updated
FROM analytics_cascade_folders
GROUP BY current_stage
ORDER BY current_stage;
"""
stdout, _, _ = run_cmd(f"docker exec pgvector-db psql -U vector_user -d marketing_db -c \"{sql_stages}\"")
print(stdout)

print("\n=== 4. TOTAL FOLDERS & DISCREPANCY CHECK (DELTA) ===")
sql_delta = """
WITH stage_counts AS (
    SELECT 
        COUNT(*) as total_incoming,
        COUNT(*) FILTER (WHERE current_stage = '01_stage1_inbox_national_regime') as stage1_cnt,
        COUNT(*) FILTER (WHERE current_stage = '02_stage2_terms_and_payment') as stage2_cnt,
        COUNT(*) FILTER (WHERE current_stage = '03_stage3_approved_to_crm') as stage3_cnt
    FROM analytics_cascade_folders
)
SELECT 
    total_incoming,
    stage1_cnt,
    stage2_cnt,
    stage3_cnt,
    (total_incoming - (stage1_cnt + stage2_cnt + stage3_cnt)) as delta_folders
FROM stage_counts;
"""
stdout, _, _ = run_cmd(f"docker exec pgvector-db psql -U vector_user -d marketing_db -c \"{sql_delta}\"")
print(stdout)

print("\n=== 5. DETAILED REASONS PER STAGE ===")
sql_reasons = """
SELECT 
    current_stage,
    COALESCE(rejection_reason, 'GREEN_APPROVED / NO_REASON') as reason,
    COUNT(*) as folders_count,
    ROUND(SUM(COALESCE(nmck_amount, 0))::numeric / 1000000, 2) as sum_mln_rub
FROM analytics_cascade_folders
GROUP BY current_stage, rejection_reason
ORDER BY current_stage, folders_count DESC;
"""
stdout, _, _ = run_cmd(f"docker exec pgvector-db psql -U vector_user -d marketing_db -c \"{sql_reasons}\"")
print(stdout)

print("\n=== 6. ACTIVITY IN LAST 7 DAYS (2026-11-09 TO 2026-11-16) ===")
sql_last_7d = """
SELECT 
    date_trunc('day', updated_at) as day,
    current_stage,
    COUNT(*) as cnt,
    ROUND(SUM(COALESCE(nmck_amount, 0))::numeric / 1000000, 2) as sum_mln_rub
FROM analytics_cascade_folders
WHERE updated_at >= NOW() - INTERVAL '7 days'
GROUP BY 1, 2
ORDER BY 1 DESC, 2;
"""
stdout, _, _ = run_cmd(f"docker exec pgvector-db psql -U vector_user -d marketing_db -c \"{sql_last_7d}\"")
print(stdout)

print("\n=== 7. REVERSE CHECK VIEW (v_cascade_gd_crm_reconciliation) ===")
sql_recon = """
SELECT 
    reconciliation_status,
    COUNT(*) as folders_count,
    ROUND(SUM(COALESCE(nmck_amount, 0))::numeric / 1000000, 2) as sum_mln_rub
FROM v_cascade_gd_crm_reconciliation
GROUP BY reconciliation_status
ORDER BY folders_count DESC;
"""
stdout, _, _ = run_cmd(f"docker exec pgvector-db psql -U vector_user -d marketing_db -c \"{sql_recon}\"")
print(stdout)

# Sample rows from reconciliation view
sql_recon_sample = """
SELECT folder_name, purchase_number, current_stage, crm_deal_id, reconciliation_status, linkage_source
FROM v_cascade_gd_crm_reconciliation
LIMIT 15;
"""
stdout, _, _ = run_cmd(f"docker exec pgvector-db psql -U vector_user -d marketing_db -c \"{sql_recon_sample}\"")
print("\nReconciliation Sample:\n" + stdout)

print("\n=== 8. TRANSITIONS TABLE (BATCH & LIVE SYNC METRICS) ===")
sql_trans = """
SELECT 
    source_stage,
    target_stage,
    action,
    trigger_type,
    COUNT(*) as cnt,
    MIN(transition_time) as min_time,
    MAX(transition_time) as max_time
FROM analytics_cascade_transitions
GROUP BY source_stage, target_stage, action, trigger_type
ORDER BY cnt DESC;
"""
stdout, _, _ = run_cmd(f"docker exec pgvector-db psql -U vector_user -d marketing_db -c \"{sql_trans}\"")
print(stdout)

print("\n=== 9. METABASE CARDS TEST (CARDS 91..105 VIA METABASE DB) ===")
# Inspect sqlite3 or mb_db
sql_mb = """
SELECT id, name, collection_id, archived 
FROM report_card 
WHERE id BETWEEN 90 AND 110 OR name LIKE '%Контур 2%' OR name LIKE '%АСТ ГОЗ%'
ORDER BY id;
"""
# Metabase runs with H2 or postgres? Let's check docker exec metabase
stdout, _, _ = run_cmd("docker exec metabase ls -la /metabase-data")
print("Metabase data dir:\n" + stdout)

# Let's check Metabase API directly with curl from localhost:3000
# First check if dashboard 12 exists
stdout, _, _ = run_cmd("curl -s http://localhost:3000/api/dashboard/12 | head -c 500")
print("\nDashboard 12 API response:\n" + stdout)
