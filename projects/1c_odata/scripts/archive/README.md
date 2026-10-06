# Реестр архивных версий скриптов CRM (Follow-up & Leads Processing)

В данном каталоге хранятся полные рабочие снапшоты скриптов follow-up перед внесением изменений и рефакторингом по новому ТЗ согласно политике **Snapshot Before Edit Guard**.

---

## Хронология версий

| Файл архива | Дата | Исходный скрипт | Описание состояния и назначение |
|---|---|---|---|
| `2026-09-29_deal_followup_pipeline_v1.py` | 29.09.2026 | `deal_followup_pipeline.py` | Первая базовая версия конвейера follow-up: кэш вложений на диске, RFC 2231, сохранение в IMAP Drafts. |
| `2026-09-30_process_today_followup_deals_v1.py` | 30.09.2026 | `process_today_followup_deals.py` | Версия для обработки сделок **с делами на сегодня** (дедлайн <= сегодня), закрытие дел и создание CRM_TODO. |
| `2026-10-01_process_deals_without_activities_v2_selfcheck.py` | 01.10.2026 | `process_deals_without_activities.py` | **Стабильная боевая версия v2.0**: аппаратный 7-ступенчатый `pre_send_self_check`, промышленный шлюз безопасности вложений (СТРОГО `.pdf` > 5 КБ, отсев `.docx`/`.jpg`/`.png`), санитизация HTML-цитирования от `<!DOCTYPE>`, защита от двойной отправки почтовым сервером Битрикс24 (`salman@longwang.ru`), закрепление аналитического ИИ-резюме и вердикта на закрытие (`crm.timeline.comment.add` + `crm.timeline.item.pin`), постановка дела контроля (`crm.activity.todo.add`). |
| `2026-10-01_process_incoming_sales_leads_v1_legacy.py` | 01.10.2026 | `process_incoming_sales_leads.py` | **Исходная версия конвейера лидов v1.0 (до рефакторинга)**: ветвление Clear RFQ / Ambiguous, баг с `COMMUNICATIONS` при привязке письма к Сделке, хардкод товаров Китая на 5 позиций, отправка Шаблона № 66 без аппаратного Self-Check. |
| `2026-10-02_sync_to_bitrix_legacy.py` | 02.10.2026 | `sync_to_bitrix.py` | **Устаревший дубликат утилиты обогащения Б24**: перенесен в архив в рамках чистки Script Sprawl; функционал интегрирован в канонический `sync_leads_1c_bitrix.py`. |
| `2026-10-02_sync_leads_1c_bitrix_v1_legacy.py` | 02.10.2026 | `sync_leads_1c_bitrix.py` | **Исходная версия скрипта синхронизации v1.0**: отсутствие реальных флагов `--since`, `--folder`, примитивный `argparse` без фильтров выборки. |
| `2026-10-02_generate_supply_rfq_excel_v1_legacy.py` | 02.10.2026 | `generate_supply_rfq_excel.py` | **Исходная версия генератора Excel v1.0**: жесткая привязка к диску D: без fallback-шаблона, хардкод 4 компаний в `KNOWN_SPECIFICATIONS`. |
| `2026-10-03_sync_leads_1c_bitrix_v2_before_bounce_clean.py` | 03.10.2026 | `sync_leads_1c_bitrix.py` | **Стабильная версия v2.0 перед добавлением Bounce & Unsubscribe Guard**: поддержка чистой синхронизации лидов Б24 и 1С:УНФ, фильтры `--since`, `--folder`, обогащение контактов и компаний. |
| `2026-10-03_sync_leads_1c_bitrix_v3_before_sbis_enrichment.py` | 03.10.2026 | `sync_leads_1c_bitrix.py` | **Версия v3.0 перед подключением авто-скоринга СБИС**: Bounce & Unsubscribe Guard протестирован и активен. |
| `2026-10-03_check_contractor_v2_before_cache_and_db.py` | 03.10.2026 | `check_contractor.py` | **Версия v2.0 перед интеграцией с DWH marketing_db и функцией проверки кэша**: поддержка DaData + Saby, запись в Б24 и 1С. |
| `2026-10-04_sync_leads_1c_bitrix_v4_before_tag_integrity_guard.py` | 04.10.2026 | `sync_leads_1c_bitrix.py` | **Версия v4.0 перед интеграцией Tag Integrity Guard**: чистая синхронизация, Bounce/Unsubscribe Guard, скоринг Saby. |
| `2026-10-04_create_1c_lead_v1_before_tag_constants_update.py` | 04.10.2026 | `create_1c_lead.py` | **Версия v1.0 перед расширением констант тегов**: 4 базовых тега без `Крупный`, `Холдинг`, `Физик` и без авто-исправления опечаток. |
| `2026-10-04_check_contractor_v3_before_no_fallback_secrets.py` | 04.10.2026 | `check_contractor.py` | **Версия v3.0 перед удалением fallback-секретов**: наличие дефолтных паролей в `os.getenv` устранено по правилу No Fallback Secrets Guard. |
| `2026-10-04_process_deals_without_activities_v2_before_zagotovki_fix.py` | 04.10.2026 | `process_deals_without_activities.py` | **Снимок v2.0 перед ликвидацией бага Заготовки**: сохранение велось в ДВЕ папки (Drafts и Заготовки), задваивание при перезапусках dry-run, пустые блоки цитирования. |

---

## Правила работы с архивом
1. **Запрет удаления:** Любые снапшоты в этом каталоге являются персистентными и не подлежат удалению при очистке `scratch/`.
2. **Откат (Rollback):** Для отката к любой предыдущей версии достаточно скопировать нужный файл из этого каталога поверх боевого скрипта в `projects/1c_odata/scripts/`.
3. **Ротация при новом ТЗ:** Перед внесением изменений в боевой скрипт текущая стабильная версия сначала копируется сюда с новой датой и описанием.
