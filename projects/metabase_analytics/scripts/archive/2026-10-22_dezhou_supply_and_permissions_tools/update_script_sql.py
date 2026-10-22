#!/usr/bin/env python3
# -*- coding: utf-8 -*-
with open("projects/metabase_analytics/scripts/manage_metabase_dashboards.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace references to raw_data->>'UF_CRM_SUPPLY_RESPONSIBLE' in deploy_weekly_sync_dashboard
text = text.replace(
    "COALESCE(raw_data->>'UF_CRM_SUPPLY_RESPONSIBLE', 'Офис Дечжоу (Miss Wang / Азат)')",
    "COALESCE(supply_responsible_name, 'Не назначен в CRM')"
)
text = text.replace(
    "COALESCE(raw_data->>'UF_CRM_SUPPLY_RESPONSIBLE', 'Азат Денишов / Офис Дечжоу')",
    "COALESCE(supply_responsible_name, 'Не назначен в CRM')"
)
text = text.replace(
    "COALESCE(raw_data->>'UF_CRM_SUPPLY_RESPONSIBLE', 'Азат')",
    "COALESCE(supply_responsible_name, '')"
)
text = text.replace(
    "[[AND (COALESCE(supply_responsible_name, '') ILIKE '%' || {{supply_responsible}} || '%')]]",
    "[[AND (supply_responsible_name ILIKE '%' || {{supply_responsible}} || '%')]]"
)

with open("projects/metabase_analytics/scripts/manage_metabase_dashboards.py", "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: manage_metabase_dashboards.py updated with native supply_responsible_name column!")
