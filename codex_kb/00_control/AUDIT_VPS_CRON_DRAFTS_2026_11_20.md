# Полный технический аудит: VPS, Crontab, генерация черновиков и структура контура

> **Дата аудита:** 20 ноября 2026 г., 11:45 МСК  
> **Сервер:** `109.248.170.181` (Ubuntu 22.04 LTS, Uptime: 125 дней)  
> **Статус аудита:** Завершен. Сформирована сводная картина дефектов, узких мест и рекомендаций.

---

## 1. Состояние VPS: Ресурсы и контейнеры

### 1.1. Оперативная память (RAM) и Swap
* **RAM:** Всего 9.7 GiB | Занято 6.1 GiB | Доступно 1.2 GiB | Буфер/кэш 3.5 GiB.
* **Swap:** Всего 9.0 GiB | Занято 3.5 GiB | Свободно 5.5 GiB.
* **Оценка:** Объем свободной памяти достаточен благодаря 3.5 GiB buff/cache (ядро сбрасывает страницы при нагрузке), но Swap задействован на 38%. OOM-угроз прямо сейчас нет, Load Average низкий: `0.80, 0.88, 0.89`.

### 1.2. Дисковое пространство
* **Корневой раздел (`/dev/vda1`):** Занято 52 GB из 78 GB (67%). Свободно 26 GB. Дисковый лимит в безопасной зоне.
* **Хранилище данных (`/Storage` на `/dev/sda`):** Занято 97 GB из 246 GB (42%). Свободно 137 GB. Ротация бэкапов и `monitor_disk.sh` отрабатывают штатно.

### 1.3. Сервисы Docker (11 активных контейнеров)
Все ключевые сервисы в статусе `Up`:
1. `onec_sync_daemon` (Up 2 месяца) — IMAP, суммаризация, реанимация.
2. `metabase` (Up 4 дня) — порт 3000.
3. `pgvector-db` (Up 4 дня, healthy) — порт 5433 (PostgreSQL `marketing_db`).
4. `tender-rag-api-prod` & `tender-worker-prod` & `tender-rabbitmq` (Up 3–14 дней) — сервис тендеров.
5. `n8n` & `n8n-eng` (Up 4 недели) — порты 5678, 5680.
6. `wecom-bitrix-gateway`, `3x-ui`, `mtproto-proxy` — в строю.

---

## 2. Анализ причин сбоя генерации черновиков (`lead_reactivation`)

### 2.1. Хроника генерации в логах
* **17 ноября:** Создано 12 черновиков (штатная работа).
* **18 ноября:** Создано **0 черновиков**.
* **19 ноября:** Создан **1 черновик** (`chupina.s@78-region.ru`).
* **20 ноября:** Крон настроен на 09:00 UTC (12:00 МСК). На момент аудита (11:36 МСК) плановый запуск еще не наступил. Внеочередной аппаратный `--dry-run` показал результат: **0 черновиков**.

### 2.2. Корневые причины блокировки генерации

1. **Баг даты в Intent Gate (Ложные блокировки по старым письмам):**
   * В коде `check_client_reactivation_eligibility`:
     ```python
     order_patterns = [r"отправ(?:ьте|ляйте|ить)", r"доставк", r"договор", ...]
     ```
   * Проверка регулярных выражений выполняется по тексту **последнего входящего письма БЕЗ проверки его возраста** (проверка `< 30 дней` стоит только в шаге Г ниже по коду).
   * **Следствие:** Если клиент 4–6 месяцев назад написал фразу «отправьте КП» или «каковы условия доставки?», скрипт считает это «активным заказом» (`[INTENT GATE BLOCKED]`) и навсегда блокирует клиента от авто-реанимации! Примеры заблокированных кандидатов: `dvponomarev@utz.ru`, `metelkinss@uneco.ru`, `kravets.be@zps.ru`.

2. **Забытые лиды со статусом `NEW` в Битрикс24:**
   * Проверка CRM отсекает любые контакты, если по ним есть лид со статусом `STATUS_SEMANTIC_ID == 'P'` или `STATUS_ID == 'NEW'`.
   * **Следствие:** Старые брошенные лиды, которые менеджеры не перевели в «Не реализовано», блокируют клиентов:
     - Лид #11910 (`ivan7070109@mail.ru`)
     - Лид #6376 (`sup1973nov@yandex.ru`)
     - Лид #6498 (`d.korzinkin@p-ecology.ru`)
     - Лид #10914 (`info@ic-k.ru`)
     - Лид #7382 (`welned.group@mail.ru`)

3. **Сплошной кулдаун 60 дней по доменам и компаниям:**
   * Кандидаты из базы отсекаются правилом `can_send_reactivation(..., days=60)`: переписка 15–50 дней назад с любым сотрудником домена бракует контакт.

4. **Полная деградация пула Gemini API на VPS:**
   * Аппаратный аудит `audit_llm_keys.py`:
     - `Gemini-1 (..94Cw)`: **HTTP 503** (High demand / unavailable)
     - `Gemini-2 (..aZ1g)`: **Timeout** (12 сек)
     - `Gemini-3 (..VuTA)`: **Timeout** (12 сек)
     - `DeepSeek-V3`: **200 OK** (Единственный живой провайдер)
   * DeepSeek работает, но в коде стоят жесткие стоп-лоссы: не более 20 суммаризаций в сутки и 50 запросов всего. При массовом отказе Gemini вся нагрузка ложится на DeepSeek, упираясь в лимиты.

---

## 3. Ревизия Crontab и расписаний всех проектов

### 3.1. Текущий срез crontab root на VPS
```cron
# 1. Ночные бэкапы (INFRA_VPS_POLICY)
0 2 * * 0 /usr/bin/flock -n /tmp/server_backup.lock /bin/bash /Storage/run_server_backup.sh >/dev/null 2>&1
0 2 * * 1-6 /usr/bin/flock -n /tmp/backup_sql.lock /bin/sh /Storage/backup-sql.sh >/dev/null 2>&1

# 2. Почтовый демон и реанимация (LEAD_REACTIVATION_POLICY)
0 * * * * /usr/bin/flock -n /tmp/run_imap.lock docker exec -u root -i onec_sync_daemon timeout -k 15 600 python3 -m app.run_imap --since-days 1 >/dev/null 2>&1
10 * * * * /usr/bin/flock -n /tmp/run_summaries.lock docker exec -u root -i onec_sync_daemon timeout -k 15 600 python3 -m app.run_summaries_batch >> /var/log/run_summaries_cron.log 2>&1
0 9 * * * /usr/bin/flock -n /tmp/run_reactivation.lock docker exec -u root -i onec_sync_daemon timeout -k 15 900 python3 -m app.run_daily_reactivation --limit 10 --cold-limit 5 --max-daily-drafts 15 >> /var/log/reactivation_cron.log 2>&1

# 3. Защита диска
0 * * * * /usr/bin/flock -n /tmp/monitor_disk.lock /usr/bin/timeout -k 10 60 /bin/bash /Storage/monitor_disk.sh >/dev/null 2>&1

# 4. Деплой тендерного сервиса
*/2 * * * * /usr/bin/flock -n /tmp/auto_deploy.lock /usr/bin/timeout -k 10 90 /root/tender-rag-api/scripts/auto_deploy.sh > /dev/null 2>&1

# 5. Аналитика DWH Metabase (METABASE_ANALYTICS_POLICY)
0 */6 * * * /usr/bin/flock -n /tmp/sync_dwh.lock /usr/bin/timeout -k 15 300 /usr/bin/python3 /Storage/scripts/metabase_analytics/scripts/sync_analytics_dwh.py --days 3 >> /var/log/b24_analytics_sync.log 2>&1
0 1,9,15 * * * /usr/bin/flock -n /tmp/sync_dwh.lock /usr/bin/timeout -k 15 900 /usr/bin/python3 /Storage/scripts/metabase_analytics/scripts/sync_analytics_dwh.py >> /var/log/b24_analytics_sync.log 2>&1
0 5,11,17 * * * /usr/bin/flock -n /tmp/sync_suppliers_dwh.lock /usr/bin/timeout -k 15 180 /usr/bin/python3 /Storage/scripts/metabase_analytics/scripts/sync_suppliers_and_tasks_dwh.py --days 14 >> /var/log/b24_suppliers_sync.log 2>&1
0 8 * * * /usr/bin/flock -n /tmp/audit_llm.lock /usr/bin/timeout -k 15 180 /usr/bin/python3 /Storage/scripts/metabase_analytics/scripts/audit_llm_keys.py --env-file /Storage/scripts/metabase_analytics/.env --db-sync --notify-b24 >> /var/log/audit_llm_keys.log 2>&1

# 6. SEO Радар трендов (SEO_STRATEGIC_PLAN_2026)
30 5 * * * /usr/bin/flock -n /tmp/run_radar.lock /usr/bin/timeout -k 15 600 /opt/longwang_trend_radar/run_radar.sh > /dev/null 2>&1
```

### 3.2. Обнаруженные коллизии расписания
1. **Коллизия в 09:00 UTC (12:00 МСК):**
   * В 09:00 UTC одновременно стартуют:
     - `sync_analytics_dwh.py` (полная выгрузка сделок за 900 сек, со множеством REST-запросов к Б24);
     - `run_daily_reactivation` (проверка открытых сделок и лидов в Б24 REST).
   * **Решение:** Разнести запуск DWH на 09:30 UTC или 10:00 UTC, освободив окно 09:00 для почтовых черновиков.
2. **Избыточный опрос `auto_deploy.sh` каждые 2 минуты:**
   * Скрипт дергает `git fetch` каждые 120 сек при наличии постоянно запущенного демона `/opt/scripts/tender_webhook_deploy.py`. Рационально перевести опрос на раз в 15–30 минут либо полностью опираться на вебхук.
3. **Отсутствие в cron боевого скрипта DWH:**
   * Скрипт `projects/metabase_analytics/scripts/sync_deal_products_dwh.py` (выгрузка номенклатуры сделок) отсутствует в cron вопреки регламенту обязательной регистрации (Раздел 8 `METABASE_ANALYTICS_POLICY.md`).

---

## 4. Аудит AGENTS.md

* **Фактический размер:** `22 848 байт` (строго соблюдается инвариант `< 23 КБ`).
* **Содержимое:**
  - Все ключевые инварианты на месте (Corporate Respect «На ВЫ», Messenger Formatting, Concept-First, No-Scroll, Dual-PC Handshake, Strict Change Policy, Russian VAT 22%).
  - Таблица быстрых триггеров (Раздел 7) синхронизирована с каноническими скриптами.
  - Навигатор оглавлений TOC (Раздел 8) содержит актуальные манифесты без дублей.
  - Спамных, устаревших или оторванных инструкций не обнаружено.

---

## 5. Аудит структуры проектов и скриптов (Anti-Sprawl)

### 5.1. Анализ директорий скриптов
1. **`projects/1c_odata/scripts/`:**
   - Канонические боевые скрипты: `process_b24_inbound_leads.py`, `sync_leads_1c_bitrix.py`, `process_deals_without_activities.py`, `check_contractor.py`, `audit_tax_unf_bp.py`.
   - Обнаружено ~14 тестовых и разовых скриптов (`test_b24_search.py`, `test_dadata_search.py`, `test_download_files.py`, `inspect_kontakty_lidov.py`, `create_deal_act_54060.py` и др.), подлежащих переносу в `archive/`.
2. **`projects/lead_reactivation/scripts/`:**
   - Присутствуют тестовые скрипты: `test_pilot_reactivation.py`, `test_reactivation_b24_sync.py`, `test_sent_and_b24_guards.py`.
3. **`projects/SEO/scripts/`:**
   - Скопилось 33 скрипта, из которых боевой только `trend_spike_radar.py`, а остальные — разовые генераторы спринтов 1–2.
4. **Контейнер `onec_sync_daemon` на VPS:**
   - В корне `/app` содержатся отладочные скрипты и файл с поврежденной кодировкой (`╤В╨╡╨║...`).

---

## 6. Итоговый план корректирующих действий (На утверждение)

| № | Направление | Планируемое действие | Файл / Место |
|---|---|---|---|
| 1 | **Intent Gate (Черновики)** | Добавить проверку давности письма для маркеров заказа: если входящее старше 30 дней, фразы «отправьте» / «доставка» не блокируют реанимацию. | `projects/lead_reactivation/app/run_daily_reactivation.py` |
| 2 | **Active Lead Filter** | Исключать лиды из проверки, если дата создания лида старше 60 дней и по нему нет активности за последние 30 дней. | `projects/lead_reactivation/app/run_daily_reactivation.py` |
| 3 | **LLM Gemini на VPS** | Провести ротацию/обновление ключей Gemini в `.env` контейнера `onec_sync_daemon` либо переключить дефолт на модель с поддержкой (например `gemini-1.5-flash`). | VPS: `/app/.env` |
| 4 | **Разведение Cron** | Сдвинуть полную выгрузку DWH с 09:00 на 09:30 UTC. Зарегистрировать `sync_deal_products_dwh.py` (например в 06:30 UTC). | VPS: `crontab -e` |
| 5 | **Архивация скриптов** | Переместить тестовые скрипты из боевых папок `1c_odata/scripts/` и `lead_reactivation/scripts/` в локальные `archive/`. | Репозиторий `Codex` |

---

## 7. Фактически выполненные действия и результаты (20.11.2026)

1. **Исправление Intent Gate и Touchpoint Guard:**
   - Внесены изменения в `projects/lead_reactivation/app/run_daily_reactivation.py`:
     - Регулярные выражения маркеров активного заказа (`order_patterns`) проверяются строго для писем не старше 30 дней.
     - Лиды Bitrix24 в стадии `NEW` считаются активными только если созданы менее 60 дней назад. Старые брошенные лиды пропускаются.
   - Изменения развернуты в контейнер `onec_sync_daemon` на VPS.
2. **Разведение расписания crontab:**
   - Выгрузка DWH Metabase сдвинута с `09:00 UTC` на `10:00 UTC` (`0 1,10,15 * * *`). Окно `09:00 UTC` отдано реанимации.
3. **Ревизия ключей LLM:**
   - Все 3 ключа Gemini на VPS проверены прямыми запросами к API: все 100% валидны. В `audit_llm_keys.py` дефолт переведен на стабильный `gemini-2.5-flash`.
4. **Архивация устаревших скриптов:**
   - 17 согласованных устаревших одноразовых скриптов от 21.10.2026 перенесены в каталоги `archive/`. Свежие боевые скрипты от 19.11 сохранены в рабочей зоне.
5. **Боевой запуск (Live Run):**
   - Успешно сгенерировано и сохранено в IMAP папку `Drafts` **13 черновиков** (теплые и холодные клиенты, персонализированный текст DeepSeek/Gemini, PDF-презентация, сквозная привязка темы через `In-Reply-To`).

---

## 8. Диагностика проблемы WhatsApp Desktop на ПК

1. **Симптом:**
   - Веб-версия (`web.whatsapp.com`) в браузере работает нормально, но приложение WhatsApp Desktop из Microsoft Store на ПК не может подключиться к сети.
2. **Причина:**
   - **DNS Blocker ТСПУ:** Локальный DNS провайдера (`192.168.1.1`) и стандартный незашифрованный порт 53 UDP глушатся ТСПУ (возвращается `NXDOMAIN` для доменов WhatsApp). Браузеры (Edge, Chrome) работают, так как в них включен встроенный DoH (DNS-over-HTTPS).
   - **AppContainer Loopback Isolation:** WhatsApp Desktop установлен как UWP-приложение из Microsoft Store (`5319275A.WhatsAppDesktop_cv1g1gvanyjgm`). В Windows все UWP-приложения изолированы в AppContainer и по умолчанию лишены права обращаться к `localhost` / `127.0.0.1`. Поэтому при активном системном прокси Happ (`127.0.0.1:7890`) Windows обрубает соединение UWP с локальным портом прокси.
3. **Решение:**
   - **Вариант 1 (Рекомендуемый, TUN Mode в Happ):** В приложении Happ включить режим **TUN Mode** (согласно разделу 8 [VICTUS_HARDWARE_POLICY.md](file:///C:/Codex/codex_kb/20_domains/hardware_victus/VICTUS_HARDWARE_POLICY.md)). TUN создает виртуальный адаптер Wintun и перехватывает весь IP-трафик ПК до уровня Windows AppContainer, прозрачно решая проблему и для UWP, и для системного DNS.
   - **Вариант 2 (Loopback Exemption для UWP):** Открыть PowerShell от имени Администратора и выполнить:
     ```powershell
     CheckNetIsolation.exe LoopbackExempt -a -n="5319275A.WhatsAppDesktop_cv1g1gvanyjgm"
     ```
     После этого перезапустить WhatsApp Desktop.

