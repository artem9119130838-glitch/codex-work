# Реестр архивных версий скриптов lead_reactivation

В данном каталоге сохраняются полные рабочие снимки боевых скриптов перед модификацией по правилу **Snapshot Before Edit Guard**.

| Файл архива | Дата | Исходный скрипт | Описание состояния |
|---|---|---|---|
| `2026-10-03_run_daily_reactivation_v1_before_sbis.py` | 03.10.2026 | `run_daily_reactivation.py` | Базовая версия конвейера реанимации до интеграции сквозного СБИС-скоринга и антиспам-фильтров активных диалогов. |
| `2026-10-04_run_daily_reactivation_v2_before_quote_and_company_fix.py` | 04.10.2026 | `run_daily_reactivation.py` | Версия v2.0 со СБИС-скорингом перед ликвидацией багов ложных цитат Артёма, грязных названий компаний и фантомных КП. |
| `2026-10-04_test_pilot_reactivation_v1_before_quote_and_company_fix.py` | 04.10.2026 | `test_pilot_reactivation.py` | Исходная вспомогательная библиотека перед исправлением clean_company_name, get_last_incoming_email_details и Quality Gate. |
