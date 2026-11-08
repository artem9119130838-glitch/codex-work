#!/bin/bash
set -e

ENV_FILE=/Storage/scripts/metabase_analytics/.env
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

echo "=== [1/5] Applying Schema to marketing_db ==="
docker exec -i pgvector-db psql -U vector_user -d marketing_db < /Storage/scripts/metabase_analytics/sql/schema.sql
docker exec -i pgvector-db psql -U vector_user -d marketing_db < /Storage/scripts/metabase_analytics/sql/suppliers_dashboard_schema.sql

echo "=== [2/5] Sourcing .env and Running LLM Key Audit ==="
python3 /Storage/scripts/metabase_analytics/scripts/audit_llm_keys.py --env-file "$ENV_FILE" --db-sync --notify-b24

echo "=== [3/5] Running Bitrix24 Deal Sync into DWH (30 days) ==="
python3 /Storage/scripts/metabase_analytics/scripts/sync_analytics_dwh.py --days 30

echo "=== [4/5] Running China Suppliers & Search Tasks Sync into DWH (30 days) ==="
python3 /Storage/scripts/metabase_analytics/scripts/sync_suppliers_and_tasks_dwh.py --days 30

echo "=== [5/5] Deploying / Updating Metabase Dashboards & Token Analytics Cards ==="
python3 /Storage/scripts/metabase_analytics/scripts/manage_metabase_dashboards.py --action update-cards
python3 /Storage/scripts/metabase_analytics/scripts/manage_metabase_dashboards.py --action token-analytics

echo "=== ALL OPERATIONS COMPLETED SUCCESSFULLY ==="
