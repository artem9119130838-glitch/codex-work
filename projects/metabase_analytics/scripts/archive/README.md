# Архив версий скриптов Metabase Analytics

В соответствии с правилом **Canonical Single-Script Invariant** и регламентом **Snapshot Before Edit Guard** (`AGENTS.md` Раздел 3), перед любой модификацией боевых скриптов в каталоге `scripts/` сюда обязательно сохраняется стабильная архивная копия со снимком версии `vX.Y` и описанием изменений.

## Журнал версий
* `2026-10-03` — Исходная консолидация разрозненных скриптов (`deploy_metabase_analytics.py`, `setup_metabase.py`, `patch_metabase.py`) в единый канонический скрипт `manage_metabase_dashboards.py` v1.0.
* `2026-10-03` — Канонизация ETL-скрипта `b24_daily_analytics_sync.py` в `sync_analytics_dwh.py` v1.0 с изоляцией секретов и поддержкой `--dry-run`.
* `2026-10-05` — Снимок `manage_metabase_dashboards_v2_0_before_field_id_fix.py` перед исправлением приведения типов Field Filter (переход со строковых имен `date_create`/`date_close` на динамическое извлечение числовых Field ID из метаданных Metabase).
* `2026-10-05` — Версия `v2.2`: Полная реструктуризация раздела «Расход и статистика LLM» (Collection 7). Архивация пустого Дашборда 5 и устаревших карточек (59, 60, 66), перевод Card 68 и 70 в табличный вид (`display: table`) по правилу Multi-Metric Scale Separation Guard, внедрение динамического расчета затрат (`cost_usd`) и маппинга пулов ключей (`gemini-pool`, `deepseek-main`).
* `2026-10-05` — Снимок `manage_metabase_dashboards_v2_2_before_3level_grouping.py` перед реализацией 3-уровневой группировки (Инициатор -> Проект/Пайплайн -> API-Ключ), устранением монолита в круговой диаграмме Card 69 и внедрением автоименования `[ВРЕМЕННЫЙ] unclassified_<task>`.
* `2026-10-05` — Снимок `audit_llm_keys_v2_0_before_unified_aliases.py` перед обновлением алиасов ключей под канонические названия Metabase (`Gemini-1 (..94Cw)`, `DeepSeek-V3 Main`) и исправлением сквозного экспорта `os.environ` из `.env` файла.
* `2026-10-05` — Версия `v2.4`: Бэкпорт разовых отладочных скриптов в канонические конвейеры. В `manage_metabase_dashboards.py` добавлены субкоманды аппаратной самопроверки `--action test-queries` (тест всех 7 карточек) и `--action db-stats` (сводка DWH). В `audit_llm_keys.py` добавлена автоочистка устаревших ключей `--cleanup-obsolete`. Скрипт аудита поставлен в `crontab` на VPS (08:00 ежедневно).




