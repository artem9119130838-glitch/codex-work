## Language Policy
- Всегда общайся со мной и выводи результаты (планы задач, размышления, документацию) только на русском языке.
- Комментарии к коду оставляй на английском или русском.
- Всегда оформляй ссылки на файлы в кликабельном формате: `[filename](file:///C:/Codex/path/to/file)`.

# Workspace AI Contract (Root Router & System Guard)

Этот файл является компактным диспетчером и корневым контрактом ИИ-ассистента в личном контуре (`C:\Codex`).  
Детальные правила предметных областей вынесены в специализированные доменные манифесты и загружаются **строго по требованию (On-Demand Context Loading)**.

---

## 1. Zero-Prose Guard & Мгновенное исполнение
- **Запрет светской беседы до вызова инструментов:** При получении системных команд-триггеров (например, «конец чата», `/compress`, `/end-session`, `!конец`) ассистенту **КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО** отвечать бытовыми вежливыми фразами («пока», «до свидания», «удачной работы») до завершения исполнения всех шагов сжатия и вызова инструментов.
- Ответ текстом без вызова инструментов считается критическим сбоем дисциплины (L2).

---

## 2. Pre-Flight Token Guard & Runtime Discipline
- **Token Guard First:** Перед стартом работы над **ЛЮБЫМ проектом или задачей** ассистент ОБЯЗАН обратиться к скиллу [token_guard](file:///C:/Users/Артем/.gemini/config/skills/token_guard/SKILL.md) и провести pre-flight контроль экономии токенов и лимитов API.
- **Вызов Python на Windows:** Вызывать интерпретатор **СТРОГО через лаунчер `py`** (например, `py scripts/session_compress.py`). Вызов через `python` падает с ошибкой.
- **Запрет опроса фоновых задач (Reactive Wakeup):** Категорически запрещено использовать `command_status` или `manage_task` в цикле опроса. Платформа работает в режиме реактивного пробуждения и сама уведомит о завершении задачи. Сразу завершайте ход.
- **Пакетное выполнение и группировка (Anti-Ban & Batch Execution):**
  * Не запускать команды и скрипты мелкими разрозненными порциями. Последовательные команды объединять в одну цепочку (через `&&` или `;`) или единый скрипт.
  * На сервере VPS: не более 3 SSH-подключений в минуту; упаковывать скрипты локально, передавать за один `scp` и исполнять за один `ssh`.

---

## 3. Методика написания, объединения и хранения скриптов (Script Lifecycle, Search-First & Anti-Sprawl Guard)
- **Категорический запрет изобретать велосипед (Search-First):** Перед написанием любого нового скрипта сначала проверить единый каталог [SCRIPTS_CATALOG.md](file:///C:/Codex/codex_kb/SCRIPTS_CATALOG.md) и историю репозитория.
- **Приоритет доработки и объединения:** Если аналогичный или смежный скрипт уже существует в проекте — **ДОРАБАТЫВАТЬ И ОБЪЕДИНЯТЬ ЕГО**, а не писать новый с нуля. Запрещено плодить цепочки разрозненных файлов (`step1.py`, `step2.py`); логика объединяется в единый канонический конвейер с субкомандами/аргументами CLI и флагом `--dry-run`.
- **Трехконтурная структура хранения скриптов:**
  1. *Боевой канонический скрипт* (`projects/<проект>/scripts/<script>.py`) — РОВНО ОДИН активный скрипт на бизнес-процесс (**Canonical Single-Script Invariant**). Запрещено держать в продакшене параллельные дублирующие файлы (`_v1`, `_v2`, `_test`).
  2. *Архив версий* (`projects/<проект>/scripts/archive/`) — перед модификацией боевого скрипта текущая стабильная версия обязательно архивируется сюда со снимком vX.Y и фиксацией в `README.md` (**Snapshot Before Edit Guard**).
  3. *Черновики и исследовательские утилиты* (`scratch/` или `archive/<домен>_scratch/`) — промежуточные и отладочные скрипты категорически запрещено удалять, их перемещают в черновой архив (**Script Retention Guard**).
- **Dual Self-Check Guard (Plan & Result):** Любая модификация конвейеров проходит обязательную двойную валидацию: Plan Self-Check (отсев хардкода, проверка контракта аргументов CLI) и Result Self-Check (аппаратный аудит лога `--dry-run`, проверка исключений, валидация сущностей).

---

## 4. Мгновенное уточнение при малейшем сомнении (Clarify-Fast Guard)
- Если в задаче есть хоть малейшее сомнение, двусмысленность или нехватка параметров — **НЕ тратить время на получасовой анализ вслепую**, а НЕМЕДЛЕННО на первом этапе осмысления переспросить пользователя и приступать к исполнению только после получения ответов.

---

## 5. Universal Strict Change Policy & Dry-Run First
- **Режим Read-Only по умолчанию:** Вся файловая система и контуры находятся в режиме **СТРОГО ТОЛЬКО ЧТЕНИЕ (READ-ONLY)**. Модификация файлов разрешена **ТОЛЬКО внутри директории текущего активного проекта** (например, `projects/1c_odata/` при работе с 1С/CRM).
- **Dry-Run First для 1С, VPS и Битрикс24:** В системах 1С:УНФ, CRM Битрикс24 и на сервере VPS **ЛЮБЫЕ модифицирующие операции** (OData PATCH/POST, создание сущностей CRM, отправка писем, перезапуск Docker, деплой) **РАЗРЕШЕНЫ ИСКЛЮЧИТЕЛЬНО ПОСЛЕ СОГЛАСОВАНИЯ ВЫВОДА В РЕЖИМЕ `--dry-run` С ПОЛЬЗОВАТЕЛЕМ В ЧАТЕ!**
- **Рабочий Git (`wlissespanchame370-cyber/*`, включая `tender-rag-api`):** **СТРОГО ТОЛЬКО ЧТЕНИЕ (READ-ONLY)** без прямых указаний пользователя.

---

## 6. Zero Secrets in Git Policy
- **Тотальный запрет на утечку секретов:** КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО публиковать и коммитить в любой Git (личный или рабочий) API-ключи, токены нейросетей, вебхуки Битрикс24, пароли ящиков IMAP/SMTP, SSH-ключи, файлы `.env` и дампы учетных записей.
- Все секреты читаются строго из переменных окружения (`os.getenv`).

---

## 7. Быстрые фразы-триггеры пользователя

| Триггер / Команда | Боевой скрипт | Назначение и обязательные правила |
|---|---|---|
| **«конец чата»** (`/compress`, `/end-session`, `!конец`) | `py scripts/session_compress.py` | **Zero-Prose Guard**. Синхронизация правил, очистка `scratch/`, формирование `.ai/SESSION_SUMMARY.md`, `git push origin master`. |
| **«почисти и проверь мой ПК (ноутбук)»** | `py scripts/check_and_clean_pc.py` | Диагностика GPU Код 43, MPO, фантомов SIMULATED, BCD F8, свободного места. |
| **«полная ревизия и форматирование гравити»** | `py scripts/full_gravity_audit.py` | Сканирование контуров, отсев vendor, пересборка `SCRIPTS_CATALOG.md` и памяток на Рабочем столе. |
| **«follow up deals today»** (`follow up сделки [ответственный] [лимит]`) | `py projects/1c_odata/scripts/process_deals_without_activities.py` | **Dry-run по умолчанию**. Обязательный аппаратный Self-Check, белый список PDF, кулдаун 7 дн, подпись ящика из Б24, запрет сделок «В работе» (только pre-sale), закрепленный комментарий-резюме со стратегическим вердиктом ИИ вверху таймлайна. Читать: [FOLLOWUP_PROCESS_POLICY.md](file:///C:/Codex/projects/1c_odata/FOLLOWUP_PROCESS_POLICY.md). Архив версий: [scripts/archive/](file:///C:/Codex/projects/1c_odata/scripts/archive/). |
| **«обработай лидов [ящик] [ответственный]»** (`/process-sales-leads`) | `py projects/1c_odata/scripts/process_incoming_sales_leads.py` | **Параметры обязательны!** **Dry-run по умолчанию**. Ветвление Clear RFQ vs Ambiguous, задачи Miss Wang `[USER=30]`, Шаблон № 66, отметка прочитанным. Читать: [LEAD_PROCESSING_POLICY.md](file:///C:/Codex/projects/1c_odata/LEAD_PROCESSING_POLICY.md). |
| **«синхронизируй лидов, создай и обнови»** | `py projects/1c_odata/scripts/sync_leads_1c_bitrix.py` | **Параметры обязательны!** Чистая сверка 1С и Б24 без создания сделок и задач. Читать: [ERP_1C_POLICY.md](file:///C:/Codex/projects/1c_odata/ERP_1C_POLICY.md). |

> **Explicit Scope Guard:** Если в командах «follow up сделки», «обработай лидов» или «синхронизируй лидов» не указаны сотрудник, ящик или лимит — **не запускать вслепую, а немедленно переспросить пользователя!**

---

## 8. Dynamic Context Dispatcher (Таблица Маршрутизации к Доменным Манифестам)

> [!IMPORTANT]
> При упоминании в запросе пользователя ключевых тем или триггеров из таблицы ниже, ассистент **ОБЯЗАН ПЕРВЫМ ШАГОМ ПРОЧЕСТЬ УКАЗАННЫЙ ФАЙЛ МАНИФЕСТА ЧЕРЕЗ `view_file`** перед выполнением каких-либо действий.

| Ключевые слова / Темы в запросе | Домен контура | Файл детального регламента (Обязателен к прочтению) |
|---|---|---|
| follow-up, лиды, письма, КП, клиенты, продажи, реанимация | **B2B Продажи & CRM** | [FOLLOWUP_PROCESS_POLICY.md](file:///C:/Codex/projects/1c_odata/FOLLOWUP_PROCESS_POLICY.md)<br>[LEAD_PROCESSING_POLICY.md](file:///C:/Codex/projects/1c_odata/LEAD_PROCESSING_POLICY.md)<br>[B2B_SALES_POLICY.md](file:///C:/Codex/codex_kb/20_domains/b2b_sales/B2B_SALES_POLICY.md) |
| 1С, УНФ, OData, реквизиты, контрагенты, скоринг, себестоимость | **ERP 1С:УНФ** | [ERP_1C_POLICY.md](file:///C:/Codex/projects/1c_odata/ERP_1C_POLICY.md)<br>Скилл: [1c_unf](file:///C:/Users/Артем/.gemini/config/skills/1c_unf/SKILL.md) |
| тендер, ГОЗ, АСТ ГОЗ, спецификация, ЕИС, извещение | **Тендерный RAG** | [TENDER_RAG_POLICY.md](file:///C:/Codex/codex_kb/20_domains/tenders/TENDER_RAG_POLICY.md)<br>Скилл: [tender_automation](file:///C:/Users/Артем/.gemini/config/skills/tender_automation/SKILL.md) |
| китай, снабжение, фабрика, дечжоу, miss wang, брак, рекламация | **ВЭД & Снабжение КНР** | [CHINA_SUPPLY_POLICY.md](file:///C:/Codex/codex_kb/20_domains/china_supply/CHINA_SUPPLY_POLICY.md) |
| регламенты, HR, аттестация, ошибки сотрудников, заместитель | **Операции & HR** | [OPERATIONS_HR_POLICY.md](file:///C:/Codex/codex_kb/20_domains/hr_and_operations/OPERATIONS_HR_POLICY.md) |
| vps, сервер, docker, nginx, apache, порт, бэкап, sqlite, n8n | **VPS & DevOps** | [INFRA_VPS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/infra_vps/INFRA_VPS_POLICY.md)<br>Скилл: [linux](file:///C:/Users/Артем/.gemini/config/skills/linux/SKILL.md) |
| victus, ноутбук, видеокарта, rtx, код 43, экран, mpo, дисплей, bcd | **HP Victus 16** | [VICTUS_HARDWARE_POLICY.md](file:///C:/Codex/codex_kb/20_domains/hardware_victus/VICTUS_HARDWARE_POLICY.md)<br>Скилл: [windows](file:///C:/Users/Артем/.gemini/config/skills/windows/SKILL.md) |
