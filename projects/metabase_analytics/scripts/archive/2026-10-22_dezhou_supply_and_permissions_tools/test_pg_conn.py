#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import psycopg2

pg_host = os.environ.get("PG_HOST", "10.10.0.1")
pg_port = int(os.environ.get("PG_PORT", 5433))
pg_dbname = os.environ.get("PG_DBNAME", "marketing_db")
pg_user = os.environ.get("PG_USER", "vector_user")

# Read PG_PASS from projects/1c_odata/.env
env_path = "projects/1c_odata/.env"
pg_pass = ""
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("PG_PASS=") or line.startswith("POSTGRES_PASSWORD="):
                pg_pass = line.split("=", 1)[1].strip().strip("'\"")

print(f"Connecting to {pg_user}@{pg_host}:{pg_port}/{pg_dbname}...")
try:
    conn = psycopg2.connect(host=pg_host, port=pg_port, dbname=pg_dbname, user=pg_user, password=pg_pass, connect_timeout=5)
    print("[SUCCESS] Direct PostgreSQL connection established!")
    conn.close()
except Exception as e:
    print("[FAIL] Direct connection:", e)
