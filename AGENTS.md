## Language Policy
- Всегда общайся со мной и выводи результаты (планы, размышления, документацию) только на русском языке.
- Комментарии к коду оставляй на английском или русском.
- Всегда оформляй ссылки на файлы в кликабельном формате: `[filename](file:///C:/Codex/path/to/file)`.
- **Corporate Respect & Partner Discipline Invariant («На ВЫ»):** Обращение к сотрудникам (Азату, Александре, Михаилу и др.) и **партнерам/фабрикам КНР (Дэвиду и др.)** оформляется СТРОГО на «Вы» (в китайском — «您», «大卫», запрещены «brother», «дружище», «兄弟»). Панибратство категорически запрещено.
- **Concept-First Invariant:** При выработке стратегии и решений сначала выдать краткую концепцию (3–4 тезиса), согласовать с пользователем, и только после утверждения готовить документы.
- **No-Scroll Explicit Output Invariant:** Запрещено отсылать пользователя назад. Готовый текст письма, ТЗ или регламента выводить полностью в финальном сообщении и сохранять в файл с кликабельной ссылкой.

# Workspace AI Contract (Root Router & Cascade Guard)

Компактный диспетчер и корневой контракт ИИ-ассистента в личном контуре (`C:\Codex`).  
Детальные правила загружаются строго каскадно по требованию (**Cascade On-Demand Loading**).

---

## 1. Zero-Prose Guard & Мгновенное исполнение
- При системных триггерах («конец чата», `/compress`, `!конец`) **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНА** светская беседа до исполнения всех шагов и вызова инструментов. Ответ текстом без инструментов — сбой L2.

---

## 2. Pre-Flight Token Guard & Runtime Discipline
- **Token Guard First:** Перед стартом задачи обратиться к скиллу [token_guard](file:///C:/Users/Артем/.gemini/config/skills/token_guard/SKILL.md) для контроля токенов и лимитов API.
- **Python на Windows:** Вызывать интерпретатор **СТРОГО через лаунчер `py`** (`py script.py`). Вызов через `python` падает с ошибкой.
- **Запрет опроса (Reactive Wakeup):** Запрещено опрашивать `command_status` или `manage_task` в цикле. Платформа пробуждается автоматически.
- **Пакетное выполнение:** Объединять команды через `&&` или `;`. На VPS: не более 3 SSH-подключений в минуту; упаковка локально, передача за 1 `scp`, запуск за 1 `ssh`.
- **SSH Non-Interactive Invariant:** Вызовы SSH/SCP строго неинтерактивные через хост `vps` (`109.248.170.181`, ключ `id_ed25519_wlisses`) с флагами `-o BatchMode=yes -o ConnectTimeout=10`.

---

## 3. Методика скриптов, чистота контекста и Anti-Sprawl
- **Canonical Single-Script Invariant:** РОВНО ОДИН активный боевой скрипт на бизнес-процесс в `projects/<проект>/scripts/`. Запрещены параллельные дубли (`_v1`, `_test`).
- **Snapshot Before Edit:** Перед модификацией боевой скрипт архивируется в `scripts/archive/` со снимком vX.Y и записью в `README.md`. Черновики сохраняются в черновом архиве.
- **Dual Self-Check (Plan & Result):** Двойная валидация: отсев хардкода на этапе плана и аппаратный аудит лога `--dry-run` на этапе результата.
- **Архивная археология (Backport Rule):** Искать наработки в `scripts/archive/` и [SCRIPTS_CATALOG.md](file:///C:/Codex/codex_kb/SCRIPTS_CATALOG.md), переносить логику в канонический скрипт аргументом CLI с проверкой `--dry-run`.
- **No-Production-Code-Edit:** При рутинной обработке лидов запрещен рефакторинг боевых скриптов «на лету». При ошибке данных — Clarify-Fast.
- **Slice Reading Guard:** Читать регламенты целиком запрещено! Сначала считывать строки 1–35 (TOC), затем целевой диапазон через `view_file` с `StartLine` и `EndLine`.
- **Subagent Context Purge Guard:** Поиск по 1139 скриптам, аудит истории чатов и чтение логов (>15 КБ) выполнять СТРОГО через `invoke_subagent` с возвратом 3–5 строк и сбросом памяти.
- **Single-Source Task Registry:** Реестры задач вести в Markdown (`tasks_registry_<name>.md`). Таблицы `.xlsx` — строго производные витрины.
- **Top-Level Anti-Pollution Guard:** Запрещено засорять `AGENTS.md` деталями проектов. Корневой файл — ультра-легкий маршрутизатор ($\le 16$ КБ). Спецификации процессов фиксируются строго в локальных манифестах (`projects/...`, `codex_kb/20_domains/...`).

---

## 4. Pre-Flight Narrowing Gatekeeper & Clarify-Fast (Шлюз сужения запросов)
- **Zero-Blind-Search Guard:** При абстрактном или надиктованном запросе запрещен слепой поиск по истории или БД!
- **Автоматический шлюз сужения:** Первым ответом выдать: (1) сужающую вилку из 2–3 вариантов; (2) Cost Warning. Выполнять тяжелые действия только после подтверждения.
- **30-Second Hang Guard & Active Kill:** При отсутствии ответа фонового процесса более 30 сек — немедленно прервать через `manage_task(Action='kill')` и запросить корректировку.
- **Clarification & Grill-Me Gatekeeper:** При неясном контексте, нехватке параметров или при закрытии сессии (сомнения, куда и что фиксировать) — агент ОБЯЗАН задать уточняющие вопросы пользователю (сужающая вилка или мини `/grill-me`), запрещено действовать вслепую.

---

## 5. Universal Strict Change Policy & Dry-Run First
- **Read-Only по умолчанию:** Файловая система и внешние контуры — Read-Only. Модификация разрешена только в целевой директории задачи. Git `wlissespanchame370-cyber/*` — строго Read-Only.
- **Dry-Run First для 1С, VPS и Битрикс24:** Модифицирующие операции (PATCH/POST OData, CRM, почта, Docker) разрешены **ИСКЛЮЧИТЕЛЬНО ПОСЛЕ СОГЛАСОВАНИЯ ВЫВОДА `--dry-run` В ЧАТЕ!**
- **Strict Fact-Check Invariant:** Запрещено делать выводы по шаблонам/именам. Обязателен запуск Python-скрипта к целевым данным с фиксацией счетчиков (`count == 0` — зеленая зона) и ссылками на строки.

---

## 6. Zero Secrets in Git & Developer Key Isolation
- **Запрет утечки секретов:** Запрещено коммитить токены, пароли, ключи SSH и `.env`. Секреты читаются из окружения.
- **Zero Fallback Secrets:** Запрещены боевые пароли во 2-м аргументе `os.getenv("VAR", "")`.
- **Developer LLM Key Isolation:** Доступ разработчиков к LLM изолируется через локальный прокси `http://127.0.0.1:8002` с логированием без боевого ключа.

---

## 7. Быстрые фразы-триггеры пользователя

| Триггер / Команда | Боевой канонический скрипт | Ключевые правила и регламент |
|---|---|---|
| **«конец чата»** (`/compress`, `!конец`) | `py scripts/session_compress.py` | Zero-Prose. Синхронизация правил, `.ai/SESSION_SUMMARY.md`, git push. |
| **«почисти и проверь мой ПК»** | `py scripts/check_and_clean_pc.py` | Диагностика GPU Код 43, MPO, фантомов SIMULATED, BCD F8, диска. |
| **«полная ревизия и форматирование гравити»** | `py scripts/full_gravity_audit.py` | Сканирование контуров, отсев vendor, пересборка `SCRIPTS_CATALOG.md`. |
| **«follow up deals today»** | `py projects/1c_odata/scripts/process_deals_without_activities.py` | **Dry-run**. Белый список PDF, кулдаун 7 дн, подпись Б24, ИИ-резюме. См. [FOLLOWUP_PROCESS_POLICY.md](file:///C:/Codex/projects/1c_odata/FOLLOWUP_PROCESS_POLICY.md). |
| **«обработай лидов [ящик/лид] [ответственный]»** | `py projects/1c_odata/scripts/process_b24_inbound_leads.py` | **Dry-run**. Маска 4-сост., Задача=Сделка, Азат `[USER=20]` (Гр. 14, +4 дн / `--deadline-today`), RFQ Excel (карточки РФ отсечь). См. [LEAD_PROCESSING_POLICY.md](file:///C:/Codex/projects/1c_odata/LEAD_PROCESSING_POLICY.md). |
| **«обработай обращение контакта [ID]»** | `py projects/1c_odata/scripts/process_b24_contact_inquiries.py` | **Dry-run**. Сделка `PREPARATION`, маска, Задача=Сделка, перепривязка дел, Азат `[USER=20]`, RFQ Excel. См. [LEAD_PROCESSING_POLICY.md](file:///C:/Codex/projects/1c_odata/LEAD_PROCESSING_POLICY.md). |
| **«синхронизируй лидов, создай и обнови»** | `py projects/1c_odata/scripts/sync_leads_1c_bitrix.py` | **Dry-run**. Сверка 1С и Б24 без сделок, поддержка `--mxl`. См. [ERP_1C_POLICY.md](file:///C:/Codex/projects/1c_odata/ERP_1C_POLICY.md). |
| **«синхронизируй поставщиков 1С в битрикс»** | `py projects/1c_odata/scripts/sync_suppliers_1c_bitrix.py` | **Dry-run**. Safe Merge поставщиков КНР, теги папок 1С, реквизиты, банк. См. [CHINA_SUPPLY_POLICY.md](file:///C:/Codex/codex_kb/20_domains/china_supply/CHINA_SUPPLY_POLICY.md). |
| **«статус ключей llm»** (`«аудит metabase llm»`) | `py projects/metabase_analytics/scripts/audit_llm_keys.py --db-sync` | Пинг Gemini/DeepSeek, синхронизация `llm_keys_status` в DWH, алерт в Б24. |
| **«запуск trend radar»** (`«радар трендов»`) | `py projects/SEO/scripts/trend_spike_radar.py --dry-run` | **Dry-run**. Радар перехвата B2B-хайпа, карго, публикация в Б24 и DWH. См. [SEO_STRATEGIC_PLAN_2026.md](file:///C:/Codex/projects/SEO/docs/SEO_STRATEGIC_PLAN_2026.md). |
| **«аудит тендеров sla»** | `py projects/1c_odata/scripts/audit_tender_sla_compliance.py --since 2026-08-13` | Сквозной аудит воронки «Тендеры» и побед в «Заказчиках», изоляция Группы 14. См. [TENDER_SUPPLY_SLA_POLICY.md](file:///C:/Codex/codex_kb/20_domains/tenders/TENDER_SUPPLY_SLA_POLICY.md). |

> **Explicit Scope Guard:** Если в командах лидов или сделок не указаны сотрудник, ящик или лимит — не запускать вслепую, а немедленно переспросить пользователя!

---

## 8. Cascade On-Demand TOC Dispatcher (Навигатор оглавлений)

> [!IMPORTANT]
> При работе с предметной областью ассистент считывает **СТРОГО ОГЛАВЛЕНИЕ (строки 1–35)** целевого манифеста через `view_file` с `StartLine: 1, EndLine: 35`. Полное чтение файла запрещено (Slice Reading Guard).

| Ключевые темы в запросе | Домен | Целевой манифест (Читать строки 1–35) |
|---|---|---|
| SEO Longwang, аудит, тренды, B2B | **SEO Longwang** | [SEO_STRATEGIC_PLAN_2026.md](file:///C:/Codex/projects/SEO/docs/SEO_STRATEGIC_PLAN_2026.md) |
| Лиды, входящая почта, заявки КНР | **Лиды & CRM** | [LEAD_PROCESSING_POLICY.md](file:///C:/Codex/projects/1c_odata/LEAD_PROCESSING_POLICY.md) |
| Follow-up, зависшие КП, pre-sale | **Follow-up** | [FOLLOWUP_PROCESS_POLICY.md](file:///C:/Codex/projects/1c_odata/FOLLOWUP_PROCESS_POLICY.md) |
| Спящие клиенты, реактивация | **Реактивация** | [LEAD_REACTIVATION_POLICY.md](file:///C:/Codex/projects/lead_reactivation/LEAD_REACTIVATION_POLICY.md) |
| 1С:УНФ, OData, БСП JSON, скоринг | **ERP 1С:УНФ** | [ERP_1C_POLICY.md](file:///C:/Codex/projects/1c_odata/ERP_1C_POLICY.md) |
| Тендер, ГОЗ, АСТ ГОЗ, извещение | **Тендерный RAG** | [TENDER_RAG_POLICY.md](file:///C:/Codex/codex_kb/20_domains/tenders/TENDER_RAG_POLICY.md) |
| Тендер ↔ Снабжение SLA, закупки КНР | **Тендер-Снабжение SLA** | [TENDER_SUPPLY_SLA_POLICY.md](file:///C:/Codex/codex_kb/20_domains/tenders/TENDER_SUPPLY_SLA_POLICY.md) |
| Китай, фабрика, Дечжоу, Miss Wang | **Снабжение КНР** | [CHINA_SUPPLY_POLICY.md](file:///C:/Codex/codex_kb/20_domains/china_supply/CHINA_SUPPLY_POLICY.md) |
| VPS, сервер, docker, nginx, порт | **VPS & DevOps** | [INFRA_VPS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/infra_vps/INFRA_VPS_POLICY.md) |
| Victus, ноутбук, GPU, экран, MPO | **HP Victus 16** | [VICTUS_HARDWARE_POLICY.md](file:///C:/Codex/codex_kb/20_domains/hardware_victus/VICTUS_HARDWARE_POLICY.md) |
| Metabase, дашборд, воронка, SQL | **Аналитика BI** | [METABASE_ANALYTICS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/analytics/METABASE_ANALYTICS_POLICY.md) |
| Аварии, сбои бюджета, инциденты LLM | **Архитектура & Контроль** | [INCIDENTS_LOG.md](file:///C:/Codex/codex_kb/00_control/INCIDENTS_LOG.md) |
