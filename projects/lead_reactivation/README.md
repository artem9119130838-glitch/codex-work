# Проект: Автоматическая реанимация лидов 1С (Lead Reactivation)

> **Статус проекта:** В РАБОТЕ / НЕЗАВЕРШЕННЫЙ (WIP)  
> **Дата инициализации канонического контура:** 03 октября 2026 г.  
> **Манифест:** [LEAD_REACTIVATION_POLICY.md](file:///C:/Codex/projects/lead_reactivation/LEAD_REACTIVATION_POLICY.md)  
> **Карта воронок и пайплайна:** [docs/REACTIVATION_FUNNELS_MAP.md](file:///C:/Codex/projects/lead_reactivation/docs/REACTIVATION_FUNNELS_MAP.md)  
> **Юнит-экономика на 1 лида:** [docs/UNIT_ECONOMICS.md](file:///C:/Codex/projects/lead_reactivation/docs/UNIT_ECONOMICS.md)  
> **Связанный боевой сервис (VPS):** Docker `onec_sync_daemon` (`/root/n8n_email_ai/`)  
> **Связанный почтовый ящик:** `sales@longwang.ru` (IMAP Hostland / Roundcube)

---

## 1. Паспорт и бизнес-цель проекта
Автономный возврат «уснувших» контактов и лидов из базы **1С:УНФ** в активный коммерческий диалог через контролируемое создание черновиков писем в Roundcube по двухпоточной автоворонке.

* В отличие от [process_deals_without_activities.py](file:///C:/Codex/projects/1c_odata/scripts/process_deals_without_activities.py) (который работает по открытым сделкам pre-sale в Битрикс24), данный проект работает **по холодным/спящим контактам 1С:УНФ (`onec_contacts`)**, у которых нет активных сделок и последняя активность была более 30–40 дней назад.
* Каждое письмо создается как черновик (Drafts), менеджер проверяет его в почтовом клиенте и отправляет в один клик.

---

## 2. Структура проекта
```
projects/lead_reactivation/
├── README.md                           # Паспорт проекта, статус WIP и индекс файлов
├── LEAD_REACTIVATION_POLICY.md         # Корпоративный устав и правила генерации
├── docs/
│   ├── REACTIVATION_FUNNELS_MAP.md     # Архитектурная карта пайплайна и 2 вида воронок
│   ├── UNIT_ECONOMICS.md               # Детальный расчет затрат токенов и $ на 1 лида
│   └── POSTMORTEM_AND_IMPROVEMENTS.md  # Анализ слабых мест и план модернизации
├── scripts/
│   ├── run_daily_reactivation.py       # Канонический диспетчер воронки (в разработке)
│   ├── test_pilot_reactivation.py      # Утилита локального тестирования
│   └── update_website_knowledge_index.py # Скрипт актуализации статей и кейсов с сайта
└── sql/
    └── reactivation_schema.sql         # DDL схемы reactivation_funnel_states & history
```

---

## 3. Связь с базой знаний компании (RAG), черновиками и транскрипциями

Конвейер генерации опирается на каноническую базу знаний клиентских коммуникаций **[projects/n8n_email_ai/kb_leads_v1/](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/)**:
* **Оглавление (TOC) и манифест RAG:** [00_manifest.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/00_manifest.md) — полный рубрикатор и архитектура базы.
* **Саммари источников и маппинг:** [99_sources_and_notes.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/99_sources_and_notes.md) — паспорт происхождения данных и аудит источников.
* **Индексы материалов компании:**
  * Индекс 96 статей: [96_articles_index.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/96_articles_index.md) (URL, H1, Title, Description);
  * Каталог услуг компании: [97_services_index.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/97_services_index.md);
  * Правила подбора статей: [95_article_selection_rules.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/95_article_selection_rules.md).
* **Авторские черновики и шаблоны писем:**
  * Шаблоны реактивации спящей базы: [50_reactivation_templates.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/50_reactivation_templates.md);
  * Базовые шаблоны писем: [40_email_templates.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/40_email_templates.md);
  * Правила тональности и запреты: [60_tone_rules.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/60_tone_rules.md) и [90_pre_send_checklist.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/90_pre_send_checklist.md).
* **Транскрибации разговоров (аудио звонков с клиентами):**
  * Safe Proof-Points (канонический RAG-файл): [15_proof_points_from_calls.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/15_proof_points_from_calls.md) — реальные факты, примеры поставок и подтвержденные условия для цитирования клиентам;
  * Дословные транскрипции переговоров Спикера 2 (Артем): [15_call_phrase_candidates_speaker2.md](file:///C:/Codex/projects/n8n_email_ai/kb_leads_v1/15_call_phrase_candidates_speaker2.md) (65 КБ) — речевые обороты, обработка сложных возражений и аргументация.

---

## 4. Выявленные минусы, статус исправлений и бэклог

| Текущий минус | Последствия | Статус и план устранения |
|---|---|---|
| **Изоляция от Битрикс24** | Робот не знает, если менеджер уже ведет диалог с клиентом в CRM, и шлет холодное письмо. | **В разработке:** Pre-flight фильтр `crm.deal.list` (активные стадии) и `crm.activity.list` перед генерацией. |
| **Скриптовые шаблонные тексты** | Письма выглядят шаблонно («Хотели напомнить...»), конверсия падает. | **Внедрено:** Antigravity-промптинг с опорой на номенклатуру `skus_and_amounts` и базу знаний `kb_leads_v1`. |
| **Отсутствие КП во вложениях** | Если клиенту ранее отправлялось КП, робот слал только общую презентацию. | **Реализовано:** Гарантированное вложение `Презентация и референс-лист.pdf` + авто-поиск последнего КП в IMAP Sent. |
| **Ошибки в именах (L1)** | Обращения вида «Куликова, добрый день!» вызывали негатив. | **Реализовано:** Валидатор `HRGuard` со словарем имен (при сомнениях — безопасный дефолт «Добрый день!»). |
| **Сбои прокси и лимитов** | Падение прокси Google и лимит DeepSeek 100 запросов останавливали конвейер. | **Реализовано:** Удален битый DNS-хардкод прокси, лимит поднят до 500 запросов/день (`DEEPSEEK_DAILY_LIMIT=500`). |
| **Bounce & Unsubscribe** | Отправка писем на битые ящики или клиентам, запросившим отписку. | **Реализовано:** Процедура автоматического исключения email из Битрикс24 и 1С:УНФ через пайплайн `sync_leads_1c_bitrix.py`. |
| **Прозрачность для продаж (Таймлайн CRM)** | Менеджеры не видят создание черновика в карточке CRM. | **Бэклог планов:** Отложено по прямому решению руководителя. Сохранено в резерве улучшений. |
| **Актуализация кейсов и статей** | Индекс статей на сайте устаревает со временем. | **Внедрено:** Скрипт парсинга `update_website_knowledge_index.py` для разделов `/projects/` и `/useful-articles/`. |

---

## 5. Юнит-экономика на одного лида

* **Этап 1: Суммаризация переписки (Contact + Company Summary):**
  * Вход: ~1 200 токенов, Выход: ~250 токенов.
  * Стоимость (DeepSeek): **$0.00024** (~0.02 руб.).
* **Этап 2: Генерация одного письма автоворонки:**
  * Вход: ~1 400 токенов, Выход: ~350 токенов.
  * Стоимость (DeepSeek): **$0.00029** (~0.03 руб.).
* **Итого стоимость 1 касания:** **~$0.0005** (0.05 руб.).
* **Полный цикл автоворонки (5 касаний + саммари):** **~$0.0017** (~0.17 руб. на весь возврат клиента!).

