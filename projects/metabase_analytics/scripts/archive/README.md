# Архив версий скриптов Metabase Analytics

В соответствии с правилом **Canonical Single-Script Invariant** и регламентом **Snapshot Before Edit Guard** (`AGENTS.md` Раздел 3), перед любой модификацией боевых скриптов в каталоге `scripts/` сюда обязательно сохраняется стабильная архивная копия со снимком версии `vX.Y` и описанием изменений.

## Журнал версий
* `2026-10-03` — Исходная консолидация разрозненных скриптов (`deploy_metabase_analytics.py`, `setup_metabase.py`, `patch_metabase.py`) в единый канонический скрипт `manage_metabase_dashboards.py` v1.0.
* `2026-10-03` — Канонизация ETL-скрипта `b24_daily_analytics_sync.py` в `sync_analytics_dwh.py` v1.0 с изоляцией секретов и поддержкой `--dry-run`.
