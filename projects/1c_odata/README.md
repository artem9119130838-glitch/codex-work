# Домен ERP 1С:УНФ, B2B Продажи и Снабжение КНР (`projects/1c_odata`)

Канонический контур интеграции CRM Битрикс24, 1С:УНФ OData, входящих лидов и работы со снабжением.

---

## 🛠️ Канонические боевые скрипты (`scripts/`)

| Боевой скрипт | Назначение и регламент | Аргументы CLI |
|---|---|---|
| `create_barentscool_order.py` | Импорт номенклатуры, регистрация цен закупки КНР (CNY) и формирование Заказа покупателя в 1С:УНФ для ООО «БАРЕНЦКУЛ» из Excel | `--dry-run`, `--commit`, `--excel <path>` |
| `process_deals_batch_azat.py` | Пакетная квалификация созданных сделок, перевод в стадию `PREPARATION` («Расчет КП»), постановка задач снабженцу Азату (`user/20`) со сроком на сегодня к 18:00, прикрепление Excel-спецификаций и оригинальных файлов клиента по регламенту Full RFQ Attachment Guard | `--dry-run` (дефолт), `--execute`, `--deal-id <ID>` |
| `process_incoming_sales_leads.py` | Монолитный конвейер полной квалификации и обработки входящих лидов из почты: ветвление Clear RFQ / Ambiguous, постановка задач снабжению, автоответ по Шаблону № 66, двухфазная запись в 1С (Zero-Blank Lead Guard) | `--dry-run`, `--mailbox <email>`, `--assigned <user>`, `--limit <N>` |
| `process_b24_inbound_leads.py` | Обработка лидов CRM: сделка в `PREPARATION`, задача снабженцу Азату (`user/20`) в группе 14, отсев реквизитов РФ, чат на китайском, Single Task Invariant | `--dry-run`, `--execute`, `--limit <N>` |
| `process_deals_without_activities.py` | Конвейер Follow-up по зависшим сделкам: белый список PDF, кулдаун 7 дн., цитирование в цепочке, подпись ящика из Б24, ИИ-резюме | `--dry-run`, `--assigned <user>`, `--limit <N>` |
| `generate_supply_rfq_excel.py` | Генератор чистовых Excel-спецификаций для снабжения КНР по эталонному шаблону «Запрос КП [оборудование] [Компания].xlsx» | `--company <название>`, `--item <наименование>`, `--dry-run` |
| `check_contractor.py` | Валидатор контрагентов: контрольная сумма ИНН, DaData, ОКВЭД, торги Saby (отсев перепродажников) | `<ИНН>`, `--verbose` |
| `sync_leads_1c_bitrix.py` | Чистая синхронизация лидов между 1С:УНФ OData и Битрикс24 без создания сделок | `--dry-run`, `--limit <N>` |

---

## 📜 Регламенты домена
- [LEAD_PROCESSING_POLICY.md](file:///C:/Codex/projects/1c_odata/LEAD_PROCESSING_POLICY.md) — регламент входящих лидов, снабжения КНР, Full RFQ Attachment Guard и Azat Supply Override.
- [FOLLOWUP_PROCESS_POLICY.md](file:///C:/Codex/projects/1c_odata/FOLLOWUP_PROCESS_POLICY.md) — регламент реанимации и Follow-up сделок.
- [ERP_1C_POLICY.md](file:///C:/Codex/projects/1c_odata/ERP_1C_POLICY.md) — регламент 1С:УНФ OData, Zero-Blank Lead Guard и АдресЭП.

---

## 🗄️ Архив снимков боевых скриптов (`scripts/archive/`)
- `2026-10-26_process_b24_inbound_leads_v20_before_requisite_inn_and_single_lead_guard.py` — Снимок `process_b24_inbound_leads.py` перед добавлением записи ИНН в основной блок `crm.requisite` (`RQ_INN`), поиском лидов в 1С по `АдресЭПДляПоиска` и обработкой префиксов «ТД/Торговый Дом».

