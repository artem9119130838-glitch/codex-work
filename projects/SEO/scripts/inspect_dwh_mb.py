import os, sys, psycopg2

env = {}
with open('/Storage/scripts/metabase_analytics/.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('\'"')

conn = psycopg2.connect(
    host=env.get('PG_HOST', '10.10.0.1'),
    port=int(env.get('PG_PORT', 5433)),
    dbname=env.get('PG_DBNAME', 'marketing_db'),
    user=env.get('PG_USER', 'vector_user'),
    password=env.get('PG_PASS', '')
)
cur = conn.cursor()

print("=== DASHBOARD 8: LLM TOKEN & COST ANALYTICS ===")

# 1. Total tokens and cost by provider
cur.execute("""
SELECT provider, model_name, status,
       COUNT(*) as calls,
       COALESCE(SUM(total_tokens), 0) as tokens,
       ROUND(COALESCE(SUM(cost_usd), 0)::numeric, 4) as cost_usd
FROM llm_usage_logs
GROUP BY 1, 2, 3
ORDER BY tokens DESC;
""")
print("\n--- Расход по провайдерам и моделям (Cards 68, 71) ---")
for r in cur.fetchall():
    print(f"Provider: {r[0]:<10} | Model: {r[1]:<20} | Status: {r[2]:<10} | Calls: {r[3]:<6} | Tokens: {r[4]:<12} | Cost: ${r[5]}")

# 2. Consumption by task_type
cur.execute("""
SELECT COALESCE(task_type, 'unknown') as task,
       COUNT(*) as calls,
       COALESCE(SUM(total_tokens), 0) as tokens,
       ROUND(COALESCE(SUM(cost_usd), 0)::numeric, 4) as cost_usd
FROM llm_usage_logs
GROUP BY 1
ORDER BY tokens DESC;
""")
print("\n--- Распределение по бизнес-задачам (Card 69) ---")
for r in cur.fetchall():
    print(f"Task: {r[0]:<28} | Calls: {r[1]:<6} | Tokens: {r[2]:<12} | Cost: ${r[3]}")

# 3. Keys status (Card 72)
cur.execute("""
SELECT key_alias, provider, status, error_count, last_checked
FROM llm_keys_status
ORDER BY last_checked DESC;
""")
print("\n--- Светофор здоровья ключей (Card 72) ---")
for r in cur.fetchall():
    print(f"Key: {r[0]:<25} | Prov: {r[1]:<10} | Status: {r[2]:<15} | Errors: {r[3]} | Checked: {str(r[4])[:19]}")

# 4. Check longwang_trend_radar task in logs
cur.execute("""
SELECT COUNT(*), COALESCE(SUM(total_tokens), 0), MAX(created_at)
FROM llm_usage_logs
WHERE task_type = 'longwang_trend_radar';
""")
r_radar = cur.fetchone()
print(f"\n--- Мониторинг longwang_trend_radar ---")
print(f"Calls: {r_radar[0]} | Tokens: {r_radar[1]} | Last seen: {r_radar[2]}")
