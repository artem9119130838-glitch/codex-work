## Language Policy
- Всегда общайся со мной и выводи результаты (планы задач, размышления, документацию) только на русском языке.
- Комментарии к коду оставляй на английском или русском.
- Всегда оформляй ссылки на файлы в кликабельном формате: `[filename](file:///C:/Codex/path/to/file)`.

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

---

## 3. Методика скриптов, чистота контекста и Anti-Sprawl
- **Canonical Single-Script Invariant:** РОВНО ОДИН активный боевой скрипт на бизнес-процесс в `projects/<проект>/scripts/`. Запрещены параллельные дубли (`_v1`, `_test`).
- **Snapshot Before Edit:** Перед модификацией боевой скрипт архивируется в `scripts/archive/` со снимком vX.Y и записью в `README.md`. Черновики сохраняются в черновом архиве (Script Retention Guard).
- **Dual Self-Check (Plan & Result):** Обязательная двойная валидация: отсев хардкода на этапе плана и аппаратный аудит лога `--dry-run` на этапе результата.
- **Архивная археология (Backport Rule):** При запросе новых параметров ИИ ищет наработки в `scripts/archive/` и [SCRIPTS_CATALOG.md](file:///C:/Codex/codex_kb/SCRIPTS_CATALOG.md), переносит логику в канонический скрипт новым CLI-аргументом с проверкой `--dry-run`.
- **No-Production-Code-Edit:** При рутинной обработке лидов запрещен рефакторинг боевых скриптов «на лету». При ошибке данных — немедленный Clarify-Fast.
- **Slice Reading Guard:** **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО** читать файлы регламентов и манифестов целиком! Сначала считывать строго строки 1–35 (оглавление TOC), находить нужный раздел и читать только целевой диапазон строк через `view_file` с `StartLine` и `EndLine`.
- **Subagent Context Purge Guard:** Задачи объемного поиска по 1139 скриптам, аудита истории чатов и чтения тяжелых логов (>15 КБ) выполнять СТРОГО через саб-агента `invoke_subagent`. Саб-агент считывает сырые массивы данных, возвращает в основной чат 3–5 строк чистого итога и сгорает, очищая память.

---

## 4. Мгновенное уточнение при сомнении и зависании (Clarify-Fast & Anti-Hang)
- При малейшем сомнении, нехватке параметров или двусмысленности — немедленно уточнить у пользователя, не допуская слепого анализа.
- **30-Second Hang Guard:** При отсутствии ответа фонового процесса (SSH, OData, LLM, IMAP) более 30 сек — остановить ожидание, вывести диагностику и запросить корректировку.

---

## 5. Universal Strict Change Policy & Dry-Run First
- **Read-Only по умолчанию:** Вся файловая система и внешние контуры — СТРОГО READ-ONLY. Модификация файлов разрешена ТОЛЬКО внутри целевой директории задачи. Рабочий Git (`wlissespanchame370-cyber/*`) — строго Read-Only.
- **Dry-Run First для 1С, VPS и Битрикс24:** Любые модифицирующие операции (PATCH/POST OData, создание сущностей CRM, отправка писем, рестарт Docker) разрешены **ИСКЛЮЧИТЕЛЬНО ПОСЛЕ СОГЛАСОВАНИЯ ВЫВОДА В РЕЖИМЕ `--dry-run` С ПОЛЬЗОВАТЕЛЕМ В ЧАТЕ!**

---

## 6. Zero Secrets in Git & Developer Key Isolation
- **Тотальный запрет утечки секретов:** КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО коммитить в Git токены, вебхуки, пароли, ключи SSH и файлы `.env`. Все секреты читаются из переменных окружения.
- **Zero Fallback Secrets:** Запрещены боевые пароли во втором аргументе `os.getenv("VAR", "secret")`. Дефолт обязан быть пустым `os.getenv("VAR", "")`.
- **Developer LLM Key Isolation:** Доступ разработчиков к LLM на VPS изолируется через локальный прокси `http://127.0.0.1:8002` с логированием инициатора без передачи боевого ключа.

---

## 7. Быстрые фразы-триггеры пользователя

| Триггер / Команда | Боевой канонический скрипт | Ключевые правила и регламент |
|---|---|---|
| **«конец чата»** (`/compress`, `!конец`) | `py scripts/session_compress.py` | Zero-Prose. Синхронизация правил, `.ai/SESSION_SUMMARY.md`, git push. |
| **«почисти и проверь мой ПК»** | `py scripts/check_and_clean_pc.py` | Диагностика GPU Код 43, MPO, фантомов SIMULATED, BCD F8, диска. |
| **«полная ревизия и форматирование гравити»** | `py scripts/full_gravity_audit.py` | Сканирование контуров, отсев vendor, пересборка `SCRIPTS_CATALOG.md`. |
| **«follow up deals today»** | `py projects/1c_odata/scripts/process_deals_without_activities.py` | **Dry-run**. Белый список PDF, кулдаун 7 дн, подпись Б24, закрепленное ИИ-резюме. |
| **«обработай лидов [ящик/лид] [ответственный]»** | `py projects/1c_odata/scripts/process_b24_inbound_leads.py` | **Dry-run**. Задача Азату `[USER=20]` (Гр. 14, дедлайн +4 дн / `--deadline-today`, RU+CN), Шаблон №66, Multi-Item RFQ Excel, скоринг СБИС/DaData, 1С OData. |
| **«синхронизируй лидов, создай и обнови»** | `py projects/1c_odata/scripts/sync_leads_1c_bitrix.py` | **Dry-run**. Чистая сверка 1С и Б24 без создания сделок, поддержка `--mxl`. |

> **Explicit Scope Guard:** Если в командах лидов или сделок не указаны сотрудник, ящик или лимит — не запускать вслепую, а немедленно переспросить пользователя!

---

## 8. Cascade On-Demand TOC Dispatcher (Навигатор оглавлений)

> [!IMPORTANT]
> При работе с предметной областью ассистент считывает **СТРОГО ОГЛАВЛЕНИЕ (строки 1–35)** целевого манифеста через `view_file` с `StartLine: 1, EndLine: 35`. Полное чтение файла запрещено (Slice Reading Guard).

| Ключевые темы в запросе | Домен | Целевой манифест (Читать строки 1–35) |
|---|---|---|
| Лиды, входящая почта, заявки КНР | **Лиды & CRM** | [LEAD_PROCESSING_POLICY.md](file:///C:/Codex/projects/1c_odata/LEAD_PROCESSING_POLICY.md) |
| Follow-up, зависшие КП, pre-sale | **Follow-up** | [FOLLOWUP_PROCESS_POLICY.md](file:///C:/Codex/projects/1c_odata/FOLLOWUP_PROCESS_POLICY.md) |
| Спящие клиенты, реактивация | **Реактивация** | [LEAD_REACTIVATION_POLICY.md](file:///C:/Codex/projects/lead_reactivation/LEAD_REACTIVATION_POLICY.md) |
| 1С:УНФ, OData, БСП JSON, скоринг | **ERP 1С:УНФ** | [ERP_1C_POLICY.md](file:///C:/Codex/projects/1c_odata/ERP_1C_POLICY.md) |
| Тендер, ГОЗ, АСТ ГОЗ, извещение | **Тендерный RAG** | [TENDER_RAG_POLICY.md](file:///C:/Codex/codex_kb/20_domains/tenders/TENDER_RAG_POLICY.md) |
| Китай, фабрика, Дечжоу, Miss Wang | **Снабжение КНР** | [CHINA_SUPPLY_POLICY.md](file:///C:/Codex/codex_kb/20_domains/china_supply/CHINA_SUPPLY_POLICY.md) |
| VPS, сервер, docker, nginx, порт | **VPS & DevOps** | [INFRA_VPS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/infra_vps/INFRA_VPS_POLICY.md) |
| Victus, ноутбук, GPU, экран, MPO | **HP Victus 16** | [VICTUS_HARDWARE_POLICY.md](file:///C:/Codex/codex_kb/20_domains/hardware_victus/VICTUS_HARDWARE_POLICY.md) |
| Metabase, дашборд, воронка, SQL | **Аналитика BI** | [METABASE_ANALYTICS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/analytics/METABASE_ANALYTICS_POLICY.md) |
