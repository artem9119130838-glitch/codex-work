## Language Policy
- Всегда общайся со мной и выводи результаты (планы задач, размышления, документацию) только на русском языке.
- Комментарии к коду оставляй на английском или русском.
- Всегда оформляй ссылки на файлы в кликабельном формате: `[filename](file:///C:/Codex/path/to/file)`.
- **Corporate Respect & Partner Discipline Invariant («На ВЫ» и запрет фамильярности):** Во всех проектах, сообщениях, шаблонах задач и деловой переписке от лица Артема обращение к любым сотрудникам, клиентам и внешним партнерам / контрагентам оформляется СТРОГО уважительно, на «Вы» / «вы» (в китайском языке — строго «您»). Панибратство, сленг и фамильярный тон («brother», «дружище», «兄弟» и т.п.) категорически запрещены.
- **Concept-First Invariant (Сначала концепция):** При выработке стратегии и сложных технических/таможенных решений ассистент обязан сначала сформулировать краткую, структурированную концепцию (3–4 тезиса) без многословия, согласовать ее с пользователем, и только после утверждения готовить итоговые тексты писем и документов.
- **No-Scroll Explicit Output Invariant (Полный текст на выходе без отсылок назад):** Запрещено отсылать пользователя к «тексту из предыдущего сообщения» при завершении задачи или плана. Если готовился текст письма, ТЗ, документа или регламента для отправки человеку, ассистент обязан: (1) вывести полный готовый текст непосредственно в финальном сообщении; (2) сохранить его в отдельный артефакт/файл с кликабельной ссылкой для удобного копирования.

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
- **SSH Non-Interactive & Fast Timeout Invariant:** Вызовы SSH/SCP строго неинтерактивные через настроенные алиасы (`~/.ssh/config`, хост `vps`) с флагами `BatchMode yes` и `ConnectTimeout 10`. Запрещены «голые» вызовы SSH без настроенного алиаса или без флагов `-o BatchMode=yes -o ConnectTimeout=10`.
- **Dual-PC Git Handshake Invariant (Victus ⮂ MateBook):** Единый канонический путь репозитория на обоих ПК — строго `C:\Codex`. Запрещен запуск задач в оторванных подкаталогах (`Codex_Shared`). При смене машины обязательна эстафета: `git push origin master` («конец чата») на первом ПК ➔ `git pull origin master` («подтяни обновления») на втором ПК.
- **Monorepo Awareness Guard:** При поиске модулей бизнес-процессов (лиды, СБИС, CRM, 1С) ассистент обязан учитывать, что они находятся внутри монорепозитория `codex-work.git` (`projects/...`), а не в виде отдельных изолированных репозиториев на GitHub. Запрещены ложные отчеты об «отсутствии проекта».

---

## 3. Методика скриптов, чистота контекста и Anti-Sprawl
- **Canonical Single-Script Invariant:** РОВНО ОДИН активный боевой скрипт на бизнес-процесс в `projects/<проект>/scripts/`. Запрещены параллельные дубли (`_v1`, `_test`).
- **Snapshot Before Edit:** Перед модификацией боевой скрипт архивируется в `scripts/archive/` со снимком vX.Y и записью в `README.md`. Черновики сохраняются в черновом архиве (Script Retention Guard).
- **Dual Self-Check (Plan & Result):** Обязательная двойная валидация: отсев хардкода на этапе плана и аппаратный аудит лога `--dry-run` на этапе результата.
- **Архивная археология (Backport Rule):** При запросе новых параметров ИИ ищет наработки в `scripts/archive/` и [SCRIPTS_CATALOG.md](file:///C:/Codex/codex_kb/SCRIPTS_CATALOG.md), переносит логику в канонический скрипт новым CLI-аргументом с проверкой `--dry-run`.
- **No-Production-Code-Edit:** При рутинном исполнении бизнес-процессов и обработке данных запрещен рефакторинг боевых скриптов «на лету». При ошибке данных — немедленный Clarify-Fast.
- **Slice Reading Guard:** **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО** читать файлы регламентов и манифестов целиком! Сначала считывать строго строки 1–35 (оглавление TOC), находить нужный раздел и читать только целевой диапазон строк через `view_file` с `StartLine` и `EndLine`.
- **Subagent Context Purge Guard:** Задачи объемного поиска по каталогу скриптов, аудита истории чатов и чтения тяжелых логов (>15 КБ) выполнять СТРОГО через саб-агента `invoke_subagent`. Саб-агент считывает сырые массивы данных, возвращает в основной чат 3–5 строк чистого итога и сгорает, очищая память.
- **Single-Source Task Registry:** Кадровые реестры задач ведутся в Markdown (`tasks_registry_<name>.md`). Таблицы `.xlsx` — строго производные витрины.
- **Top-Level Anti-Pollution Guard:** Запрещено засорять `AGENTS.md` прикладными деталями проектов (договоры, частные шаблоны, списки полей, специфика отдельных воронок). Корневой файл — ультра-легкий маршрутизатор (< 23 КБ). Все детальные правила и отраслевые регламенты ведутся строго в локальных манифестах (`projects/...`, `codex_kb/20_domains/...`).
- **Deal & Domain Isolation Invariant:** Контекст сделок по кастомным металлоизделиям (гидроцилиндры, трубы, штоки, чертежи, рекламации и допуски) строго изолируется внутри выделенных сессий. Запрещено подтягивать детали металлоизделий в общие задачи Price Clearing (таможня, пошлины, сборные грузы, чужие лиды), и наоборот.

---

## 4. Pre-Flight Narrowing Gatekeeper & Clarify-Fast (Шлюз сужения запросов)
- **Zero-Blind-Search Guard (Запрет слепого поиска):** При получении абстрактного, надиктованного или многосоставного запроса ИИ **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО** немедленно начинать глубокий поиск по истории чатов, коммитов или базам данных!
- **Автоматический шлюз сужения (Без необходимости ручного `/grill-me`):** Первым ответом выдать: (1) сужающую вилку из 2–3 вариантов; (2) предупреждение о стоимости в токенах (Cost Warning). Выполнять тяжелые действия только после явного выбора ветки пользователем.
- **30-Second Hang Guard & Active Kill:** При отсутствии ответа фонового процесса (SSH, OData, LLM, IMAP) более 30 сек — запрещено пассивно ожидать! Ассистент обязан немедленно принудительно прервать фоновую задачу через `manage_task(Action='kill')`, вывести диагностику и запросить корректировку.
- **Session Close Clarification & Grill-Me Gatekeeper:** Даже при молчаливом закрытии сессии (`/compress`, «конец чата») агент обязан провести ретроспективный анализ сессии, сформировать список предложений (логи ошибок, политики, скрипты — по принципу «лучше больше, чем меньше») и предложить пользователю план завершения сессии на утверждение до коммита.

---

## 5. Universal Strict Change Policy & Dry-Run First
- **Read-Only по умолчанию:** Вся файловая система и внешние контуры — СТРОГО READ-ONLY. Модификация файлов разрешена ТОЛЬКО внутри целевой директории задачи. Внешние репозитории — строго Read-Only.
- **Dry-Run First для 1С, VPS и Битрикс24:** Любые модифицирующие операции (PATCH/POST OData, создание сущностей CRM, отправка писем, рестарт Docker) разрешены **ИСКЛЮЧИТЕЛЬНО ПОСЛЕ СОГЛАСОВАНИЯ ВЫВОДА В РЕЖИМЕ `--dry-run` С ПОЛЬЗОВАТЕЛЕМ В ЧАТЕ!**
- **Strict Fact-Check Invariant:** Запрещено делать выводы об ошибках, несоответствиях или дефектах данных по шаблонам или именам файлов без фактической аппаратной проверки. При аудите данных обязателен запуск Python-скрипта к целевым записям/ячейкам с фиксацией точных счетчиков (`count == 0` — зеленая зона) и строковыми ссылками.

---

## 6. Zero Secrets in Git & Developer Key Isolation
- **Тотальный запрет утечки секретов:** КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО коммитить в Git токены, вебхуки, пароли, ключи SSH и файлы `.env`. Все секреты читаются из переменных окружения.
- **Zero Fallback Secrets:** Запрещены боевые пароли во втором аргументе `os.getenv("VAR", "secret")`. Дефолт обязан быть пустым `os.getenv("VAR", "")`.
- **Developer LLM Key Isolation:** Доступ разработчиков к LLM на сервере изолируется через локальный прокси-шлюз с логированием инициатора без передачи боевого ключа.

---

## 7. Быстрые фразы-триггеры пользователя

| Триггер / Команда | Боевой канонический скрипт | Регламент / Манифест (Читать TOC 1–35) |
|---|---|---|
| **«конец чата»** (`/compress`, `!конец`) | `py scripts/session_compress.py` | Zero-Prose. Синхронизация правил, `.ai/SESSION_SUMMARY.md`, git push. |
| **«почисти и проверь мой ПК»** | `py scripts/check_and_clean_pc.py` | Диагностика GPU, MPO, диска. См. [VICTUS_HARDWARE_POLICY.md](file:///C:/Codex/codex_kb/20_domains/hardware_victus/VICTUS_HARDWARE_POLICY.md). |
| **«полная ревизия и форматирование гравити»** | `py scripts/full_gravity_audit.py` | Сканирование контуров, отсев vendor, пересборка `SCRIPTS_CATALOG.md`. |
| **«follow up deals today»** | `py projects/1c_odata/scripts/process_deals_without_activities.py` | **Dry-run**. Белый список PDF, кулдаун 7 дн. См. [FOLLOWUP_PROCESS_POLICY.md](file:///C:/Codex/projects/1c_odata/FOLLOWUP_PROCESS_POLICY.md). |
| **«обработай лидов [ящик/лид] [ответственный]»** | `py projects/1c_odata/scripts/process_b24_inbound_leads.py` | **Dry-run**. Квалификация, CRM и снабжение КНР. См. [LEAD_PROCESSING_POLICY.md](file:///C:/Codex/projects/1c_odata/LEAD_PROCESSING_POLICY.md). |
| **«обработай обращение контакта [ID]»** | `py projects/1c_odata/scripts/process_b24_contact_inquiries.py` | **Dry-run**. Повторные заявки от контактов CRM. См. [LEAD_PROCESSING_POLICY.md](file:///C:/Codex/projects/1c_odata/LEAD_PROCESSING_POLICY.md). |
| **«синхронизируй лидов, создай и обнови»** | `py projects/1c_odata/scripts/sync_leads_1c_bitrix.py` | **Dry-run**. Сверка 1С и Б24 без создания сделок. См. [ERP_1C_POLICY.md](file:///C:/Codex/projects/1c_odata/ERP_1C_POLICY.md). |
| **«синхронизируй поставщиков 1С в битрикс»** | `py projects/1c_odata/scripts/sync_suppliers_1c_bitrix.py` | **Dry-run**. Перенос и Safe Merge фабрик КНР. См. [CHINA_SUPPLY_POLICY.md](file:///C:/Codex/codex_kb/20_domains/china_supply/CHINA_SUPPLY_POLICY.md). |
| **«статус ключей llm»** (`«аудит metabase llm»`) | `py projects/metabase_analytics/scripts/audit_llm_keys.py --db-sync` | Пинг Gemini/DeepSeek, синхронизация в DWH. См. [METABASE_ANALYTICS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/analytics/METABASE_ANALYTICS_POLICY.md). |
| **«запуск trend radar»** (`«радар трендов»`) | `py projects/SEO/scripts/trend_spike_radar.py --dry-run` | **Dry-run**. Радар перехвата B2B-хайпа и карго. См. [SEO_STRATEGIC_PLAN_2026.md](file:///C:/Codex/projects/SEO/docs/SEO_STRATEGIC_PLAN_2026.md). |
| **«аудит тендеров sla»** | `py projects/1c_odata/scripts/audit_tender_sla_compliance.py` | Аудит воронки тендеров и снабжения КНР. См. [TENDER_SUPPLY_SLA_POLICY.md](file:///C:/Codex/codex_kb/20_domains/tenders/TENDER_SUPPLY_SLA_POLICY.md). |

> **Explicit Scope Guard:** Если в командах обработки данных (лиды, сделки, синхронизации) не указаны обязательные параметры (сотрудник, ящик, лимит, период) — не запускать вслепую, а немедленно запросить уточнение у пользователя!

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
| Китай, фабрика, снабжение, металлоизделия, трубы/штоки | **Снабжение КНР** | [CHINA_SUPPLY_POLICY.md](file:///C:/Codex/codex_kb/20_domains/china_supply/CHINA_SUPPLY_POLICY.md) |
| VPS, сервер, docker, nginx, порт | **VPS & DevOps** | [INFRA_VPS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/infra_vps/INFRA_VPS_POLICY.md) |
| Victus, Xbox, роутер, техника, GPU | **Личная техника & Victus** | [VICTUS_HARDWARE_POLICY.md](file:///C:/Codex/codex_kb/20_domains/hardware_victus/VICTUS_HARDWARE_POLICY.md) |
| Metabase, дашборд, воронка, SQL | **Аналитика BI** | [METABASE_ANALYTICS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/analytics/METABASE_ANALYTICS_POLICY.md) |
| Аварии, сбои бюджета, инциденты LLM | **Архитектура & Контроль** | [INCIDENTS_LOG.md](file:///C:/Codex/codex_kb/00_control/INCIDENTS_LOG.md) |
