#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import psycopg2
from psycopg2.extras import execute_values

def load_env(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k not in os.environ and v:
                        os.environ[k] = v

load_env("/Storage/scripts/metabase_analytics/.env")
load_env("projects/metabase_analytics/.env")
load_env(".env")

PG_HOST = os.environ.get("PG_HOST", "10.10.0.1")
PG_PORT = int(os.environ.get("PG_PORT", 5433))
PG_DBNAME = os.environ.get("PG_DBNAME", "marketing_db")
PG_USER = os.environ.get("PG_USER", "vector_user")
PG_PASS = os.environ.get("PG_PASS", "")

if not PG_PASS:
    print("[ERROR] PG_PASS not set!")
    sys.exit(1)

json_path = sys.argv[1] if len(sys.argv) > 1 else "deal_supply_mapping.json"
with open(json_path, "r", encoding="utf-8") as f:
    mapping = json.load(f)

print(f"Loaded {len(mapping)} mappings from {json_path}")

conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DBNAME, user=PG_USER, password=PG_PASS)
cur = conn.cursor()

# Schema migration
cur.execute("""
    ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS supply_responsible_name VARCHAR(128);
    ALTER TABLE analytics_closed_deals ADD COLUMN IF NOT EXISTS supply_task_id BIGINT;
    CREATE INDEX IF NOT EXISTS idx_closed_deals_supply_responsible ON analytics_closed_deals(supply_responsible_name);
""")
conn.commit()
print("[OK] Schema updated with supply_responsible_name and supply_task_id.")

# Batch update
rows = [(d_id, v["resp_name"], v["task_id"]) for d_id, v in mapping.items()]
update_sql = """
    UPDATE analytics_closed_deals AS d
    SET supply_responsible_name = m.resp_name,
        supply_task_id = m.task_id::BIGINT
    FROM (VALUES %s) AS m(deal_id, resp_name, task_id)
    WHERE d.deal_id = m.deal_id;
"""
execute_values(cur, update_sql, rows, page_size=200)
conn.commit()

# Verify count of deals with supply_responsible_name
cur.execute("SELECT count(*), supply_responsible_name FROM analytics_closed_deals WHERE pipeline_name = 'Тендеры' GROUP BY 2 ORDER BY 1 DESC;")
stats = cur.fetchall()
print("\n--- DEALS BREAKDOWN BY SUPPLY SPECIALIST IN DWH ---")
for cnt, name in stats:
    print(f"  {cnt} deals: {name or 'NULL / Unassigned'}")

cur.close()
conn.close()
print("\n[SUCCESS] DWH successfully updated with supply assignees!")
