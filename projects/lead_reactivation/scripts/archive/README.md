# Реестр архивных версий скриптов lead_reactivation

В данном каталоге сохраняются полные рабочие снимки боевых скриптов перед модификацией по правилу **Snapshot Before Edit Guard**.

| Файл архива | Дата | Исходный скрипт | Описание состояния |
|---|---|---|---|
| `2026-10-03_run_daily_reactivation_v1_before_sbis.py` | 03.10.2026 | `run_daily_reactivation.py` | Базовая версия конвейера реанимации до интеграции сквозного СБИС-скоринга и антиспам-фильтров активных диалогов. |
| `2026-10-04_run_daily_reactivation_v2_before_quote_and_company_fix.py` | 04.10.2026 | `run_daily_reactivation.py` | Версия v2.0 со СБИС-скорингом перед ликвидацией багов ложных цитат Артёма, грязных названий компаний и фантомных КП. |
| `2026-10-04_test_pilot_reactivation_v1_before_quote_and_company_fix.py` | 04.10.2026 | `test_pilot_reactivation.py` | Исходная вспомогательная библиотека перед исправлением clean_company_name, get_last_incoming_email_details и Quality Gate. |
| `2026-10-07_llm_service_v1_before_framework_fix.py` | 07.10.2026 | `app/services/llm_service.py` | Снимок перед внедрением Value-Driven B2B Framework, ликвидацией скидок 10% и дедлайнов. |
| `2026-10-07_run_daily_reactivation_v3_before_framework_fix.py` | 07.10.2026 | `app/run_daily_reactivation.py` | Снимок перед интеграцией Intent Classification Gate и проверки активных заказов. |
| `2026-10-07_test_pilot_reactivation_v2_before_framework_fix.py` | 07.10.2026 | `scripts/test_pilot_reactivation.py` | Снимок перед ограничением срока КП 45 днями и Quality Gate 3. |
| `vps_current_*.py` | 07.10.2026 | VPS production mirror | Зеркальные копии боевых файлов, снятые прямо с контейнера VPS перед деплоем исправлений. |
