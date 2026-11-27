## Language Policy
- Всегда общайся со мной и выводи результаты (планы задач, размышления, документацию) только на русском языке.
- Комментарии к коду оставляй на английском или русском.
- Всегда оформляй ссылки на файлы в кликабельном формате: `[filename](file:///C:/Codex/path/to/file)`.
- **Corporate Respect («На ВЫ»):** В переписке, шаблонах задач и чатах от лица Артема обращение к сотрудникам, клиентам и партнерам СТРОГО уважительное, на «Вы» / «вы» (в китайском — «您»). Панибратство и сленг («brother», «дружище», «兄弟») категорически запрещены.
- **Messenger Formatting:** Готовые тексты оформлять в блоки ````text с маркировкой канала:
  1. **Битрикс24:** Без тегов `[LIST]`, `[*]`. Списки через маркеры (`🔹`, `👉`, `⚠️`, `-`). Заголовки: `[B]...[/B]` и `[I]...[/I]`.
  2. **Telegram / WhatsApp:** Разметка: `*жирный*`, `_курсив_`, маркеры (`•`, `🔹`, `—`). Без markdown-решеток (`###`), HTML и BB-тегов.
  3. **WeChat:** Чистый текст. Отступы строк, эмодзи (`🔹`, `▶️`, `⚠️`, `✅`) и разделители (`---`, `【Раздел】`).
- **Concept-First & No-Scroll:** Сначала краткая концепция (3–4 тезиса) на утверждение, затем итоговые тексты. Запрещено отсылать к прошлым сообщениям: выводить полный готовый текст и сохранять в файл со ссылкой.

# Workspace AI Contract (Root Router & Cascade Guard)

Компактный диспетчер и корневой контракт ИИ-ассистента в личном контуре (`C:\Codex`).  
Детальные правила загружаются строго каскадно по требованию (**Cascade On-Demand Loading**).

---

## 1. Zero-Prose Guard & Мгновенное исполнение
- При системных триггерах («конец чата», `/compress`, `!конец`) **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНА** светская беседа до исполнения всех шагов и вызова инструментов. Ответ текстом без инструментов — сбой L2.

---

## 2. Pre-Flight Token Guard & Runtime Discipline
- **Token Guard:** Скилл [token_guard](file:///C:/Users/Артем/.gemini/config/skills/token_guard/SKILL.md) вшит в системный контекст. Запрещено пре-флайт чтение файла скилла — соблюдать лимиты API нативно.
- **Zero-Preflight Reading:** Запрещено на старте автоматически читать `.ai/SESSION_SUMMARY.md` или `README.md` без прямого триггера («подтяни обновления», «эстафета»).
- **Python на Windows:** Вызывать интерпретатор **СТРОГО через лаунчер `py`** (`py script.py`).
- **Запрет опроса (Reactive Wakeup):** Запрещено опрашивать `command_status` или `manage_task` в цикле. Платформа пробуждается сама.
- **Пакетное выполнение & SSH:** Объединять команды через `&&` или `;`. SSH/SCP строго через алиасы (`vps`) с флагами `-o BatchMode=yes -o ConnectTimeout=10`. Не более 3 SSH-подключений в минуту. Реестр: [INFRA_VPS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/infra_vps/INFRA_VPS_POLICY.md).
- **Dual-PC Git Handshake (Victus ⮂ MateBook):** Канонический путь репозитория — строго `C:\Codex`. Эстафета: `git push origin master` на первом ПК ➔ `git pull origin master` на втором ПК.
- **Monorepo Awareness:** Модули бизнес-процессов находятся внутри монорепозитория `codex-work.git` (`projects/...`), а не в виде отдельных репозиториев на GitHub.

---

## 3. Методика скриптов, чистота контекста и Anti-Sprawl
- **Canonical Single-Script Invariant:** РОВНО ОДИН активный боевой скрипт на бизнес-процесс в `projects/<проект>/scripts/`. Дубли запрещены.
- **Snapshot Before Edit:** Перед правкой скрипт архивируется в `scripts/archive/` со снимком vX.Y и записью в `README.md`.
- **Dual Self-Check:** Обязательная валидация: отсев хардкода на этапе плана и аппаратный аудит лога `--dry-run` на этапе результата.
- **Архивная археология:** Чтение `scripts/archive/README.md` разрешено ИСКЛЮЧИТЕЛЬНО на этапе написания кода.
- **No-Production-Code-Edit:** При рутинной обработке данных запрещен рефакторинг боевых скриптов «на лету».
- **Slice Reading Guard:** **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО** читать манифесты целиком! Считывать строго строки 1–35 (TOC), затем целевой диапазон через `view_file` с `StartLine` и `EndLine`.
- **Subagent Context Purge:** Поиск по каталогам, аудит истории чатов и чтение логов (>15 КБ) выполнять СТРОГО через `invoke_subagent`. Саб-агент возвращает 3–5 строк и сгорает.
- **Single-Source Task Registry:** Кадровые реестры задач ведутся в Markdown (`tasks_registry_<name>.md`).
- **Top-Level Anti-Pollution:** Запрещено засорять `AGENTS.md` прикладными деталями проектов. Корневой файл — легкий маршрутизатор (< 23 КБ).
- **Deal & Domain Isolation:** Контекст изолированных отраслевых сделок (кастомные изделия, чертежи, претензии) изолируется внутри сессий. Регламент: [CHINA_SUPPLY_POLICY.md](file:///C:/Codex/codex_kb/20_domains/china_supply/CHINA_SUPPLY_POLICY.md).

---

## 4. Pre-Flight Narrowing Gatekeeper & Clarify-Fast
- **Zero-Blind-Search Guard:** При абстрактном запросе ЗАПРЕЩЕНО немедленно начинать глубокий поиск по базам или чатам!
- **Авто-шлюз сужения:** Первым ответом выдать: (1) сужающую вилку из 2–3 вариантов; (2) предупреждение о стоимости в токенах (Cost Warning).
- **30-Second Hang Guard:** При отсутствии ответа фонового процесса (SSH, OData, LLM) >30 сек — немедленный kill через `manage_task` и запрос корректировки.
- **Session Close Gatekeeper:** При закрытии сессии (`/compress`, «конец чата») провести ретроспективный анализ сессии, сформировать список предложений и предложить план закрытия на утверждение до коммита.

---

## 5. Universal Strict Change Policy & Dry-Run First
- **Read-Only по умолчанию:** Вся файловая система и внешние контуры — READ-ONLY. Модификация разрешена ТОЛЬКО внутри целевой директории задачи.
- **Dry-Run First:** Модифицирующие операции (PATCH/POST OData, CRM, почта, Docker) разрешены ИСКЛЮЧИТЕЛЬНО ПОСЛЕ СОГЛАСОВАНИЯ ВЫВОДА В РЕЖИМЕ `--dry-run` В ЧАТЕ!
- **Strict Fact-Check Invariant:** Запрещено делать выводы о данных без фактической аппаратной проверки. Обязателен запуск Python-скрипта с фиксацией счетчиков (`count == 0` — зеленая зона).
- **Russian VAT 22% Invariant:** Во всех контурах (таможня, КНР, тендеры, 1С:УНФ, CRM, КП) ставка НДС в РФ составляет СТРОГО 22% (не 20%!).

---

## 6. Zero Secrets in Git & Developer Key Isolation
- **Запрет утечки секретов:** КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО коммитить в Git токены, вебхуки, пароли, ключи SSH и `.env`.
- **Zero Fallback Secrets:** Запрещены боевые пароли во втором аргументе `os.getenv("VAR", "secret")`. Дефолт обязан быть пустым `os.getenv("VAR", "")`.
- **Developer LLM Key Isolation:** Доступ разработчиков к LLM изолируется через локальный прокси-шлюз с логированием без передачи боевого ключа.

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
| **«проверь расчет налогов»** (`«аудит ндс унф бп»`) | `py projects/1c_odata/scripts/audit_tax_unf_bp.py --dry-run` | **Dry-run**. Сверка УНФ и БП, аудит налоговой базы. См. [ERP_1C_POLICY.md](file:///C:/Codex/projects/1c_odata/ERP_1C_POLICY.md). |
| **«добавь лидов на реанимацию [N]»** | `py projects/lead_reactivation/scripts/ingest_1c_cold_leads.py --batch-size [N]` | **Dry-run**. Дозированный импорт спящих лидов 1С в DWH. См. [LEAD_REACTIVATION_POLICY.md](file:///C:/Codex/projects/lead_reactivation/LEAD_REACTIVATION_POLICY.md). |
| **«kpi китайских менеджеров»** | `py projects/1c_odata/scripts/build_china_kpi_erf.py` | Сборка отчета снабжения КНР (1% CNY). См. [ERP_1C_POLICY.md](file:///C:/Codex/projects/1c_odata/ERP_1C_POLICY.md). |
| **«прочитай документ [файл/папка]»** | `py scripts/inspect_doc.py --file [путь] [--stdout]` | Инспекция PDF, Word DOCX, Excel XLSX, картинок в UTF-8. См. [SKILL.md](file:///C:/Users/Артем/.gemini/config/skills/session_management/SKILL.md). |

> **Explicit Scope Guard:** Если в командах обработки данных не указаны обязательные параметры (сотрудник, ящик, лимит, период) — запросить уточнение у пользователя!

---

## 8. Cascade On-Demand TOC Dispatcher (Навигатор оглавлений)

> [!IMPORTANT]
> Считывать **СТРОГО ОГЛАВЛЕНИЕ (строки 1–35)** целевого манифеста через `view_file` с `StartLine: 1, EndLine: 35`. Полное чтение файла запрещено (Slice Reading Guard).

| Ключевые темы в запросе | Домен | Целевой манифест (Читать строки 1–35) |
|---|---|---|
| SEO Longwang, аудит, тренды, B2B | **SEO Longwang** | [SEO_STRATEGIC_PLAN_2026.md](file:///C:/Codex/projects/SEO/docs/SEO_STRATEGIC_PLAN_2026.md) |
| Лиды, входящая почта, заявки КНР | **Лиды & CRM** | [LEAD_PROCESSING_POLICY.md](file:///C:/Codex/projects/1c_odata/LEAD_PROCESSING_POLICY.md) |
| Follow-up, зависшие КП, pre-sale | **Follow-up** | [FOLLOWUP_PROCESS_POLICY.md](file:///C:/Codex/projects/1c_odata/FOLLOWUP_PROCESS_POLICY.md) |
| Спящие клиенты, реактивация | **Реактивация** | [LEAD_REACTIVATION_POLICY.md](file:///C:/Codex/projects/lead_reactivation/LEAD_REACTIVATION_POLICY.md) |
| 1С:УНФ, OData, БСП JSON, скоринг | **ERP 1С:УНФ** | [ERP_1C_POLICY.md](file:///C:/Codex/projects/1c_odata/ERP_1C_POLICY.md) |
| Тендер, ГОЗ, АСТ ГОЗ, извещение | **Тендерный RAG** | [TENDER_RAG_POLICY.md](file:///C:/Codex/codex_kb/20_domains/tenders/TENDER_RAG_POLICY.md) |
| Тендеры, снабжение, закупки, сделки, задачи, сотрудники (Александра, Азат, КНР) | **Тендер-Снабжение SLA** | [TENDER_SUPPLY_SLA_POLICY.md](file:///C:/Codex/codex_kb/20_domains/tenders/TENDER_SUPPLY_SLA_POLICY.md) |
| Китай, фабрика, снабжение, металлоизделия, трубы/штоки, закупщицы КНР | **Снабжение КНР** | [CHINA_SUPPLY_POLICY.md](file:///C:/Codex/codex_kb/20_domains/china_supply/CHINA_SUPPLY_POLICY.md) |
| VPS, сервер, docker, nginx, порт | **VPS & DevOps** | [INFRA_VPS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/infra_vps/INFRA_VPS_POLICY.md) |
| Victus, Xbox, роутер, техника, GPU | **Личная техника & Victus** | [VICTUS_HARDWARE_POLICY.md](file:///C:/Codex/codex_kb/20_domains/hardware_victus/VICTUS_HARDWARE_POLICY.md) |
| Metabase, дашборд, воронка, SQL | **Аналитика BI** | [METABASE_ANALYTICS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/analytics/METABASE_ANALYTICS_POLICY.md) |
| Аварии, сбои бюджета, инциденты LLM | **Архитектура & Контроль** | [INCIDENTS_LOG.md](file:///C:/Codex/codex_kb/00_control/INCIDENTS_LOG.md) |

> [!NOTE]
> **Управление сотрудниками (Тендеры / Снабжение):** При любом анализе сделок, задач, переписок тендерного отдела и снабжения (Александра, Азат, КНР) агент обращается к [TENDER_SUPPLY_SLA_POLICY.md](file:///C:/Codex/codex_kb/20_domains/tenders/TENDER_SUPPLY_SLA_POLICY.md) и в ПЕРВУЮ ОЧЕРЕДЬ проверяет соблюдение регламентов (воронка 90–120, запрет закрытия по НМЦК, DeepSeek 12ч, веерная рассылка, торг, ежедневные обновления). По логистике — аналогичный манифест.
