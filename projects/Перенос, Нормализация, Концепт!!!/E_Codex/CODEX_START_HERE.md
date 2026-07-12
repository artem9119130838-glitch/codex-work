# Codex Start Here

Дата сборки базы знаний: 2026-05-10

Это корневой стартовый файл для всех будущих чатов Codex в workspace `E:\Codex_Work`.

## Обязательный старт

Для любого нового чата из этого workspace сначала читать:

1. `E:\Codex_Work\AGENTS.md`
2. `E:\Codex_Work\PROGRESS.md`
3. `E:\Codex_Work\CHAT_DISPATCHER.md`
4. `E:\Codex_Work\ГДЕ_ЧТО_ЛЕЖИТ.md`
5. `E:\Codex_Work\codex_kb\00_global\SECURITY_POLICY.md`
6. `E:\Codex_Work\codex_kb\00_global\BUSINESS_RULES.md`
7. Нужные доменные файлы из `E:\Codex_Work\codex_kb\20_domains`
8. Нужный progress-файл из `E:\Codex_Work\codex_kb\progress`

## Single Source of Truth

`E:\Codex_Work` - единый центр управления.

Markdown-файлы в workspace являются первоисточником знаний. `marketing_db.knowledge_base` и любые RAG-индексы являются производными данными и должны обновляться из `.md`, а не наоборот.

## Постоянная база

Долго живущие объекты:

- Ubuntu VPS `109.248.170.181`
- 1С база `unf` и сервер 1С
- PostgreSQL/Postgres Pro
- Apache
- Docker и n8n
- Bitrix как целевая CRM/задачи
- тендерные процессы и AST GOZ
- клиентские переписки и почта
- AI/RAG слой `marketing_db`
- локальный компьютер и workspace `E:\Codex_Work`
- телефон OnePlus
- роутер Keenetic и VPN-маршрутизация
- Google Calendar / голосовой ввод / мобильные сценарии

## Как выбирать файлы

- Сервер, Docker, Apache, 1С, PostgreSQL: `codex_kb\10_assets\SERVER_VPS.md`.
- 1С/OData/n8n/почта: `codex_kb\20_domains\1c\README.md`, `codex_kb\20_domains\n8n\README.md`, `codex_kb\20_domains\email_client_comms\README.md`.
- AI/RAG/marketing_db: `codex_kb\20_domains\ai_rag_marketing\README.md`.
- Тендеры: `codex_kb\20_domains\tenders\README.md`.
- Bitrix: `codex_kb\20_domains\bitrix\README.md`.
- Роутер, WireGuard, Gemini/OpenAI routing: `codex_kb\10_assets\ROUTER_AND_VPN.md`.
- Локальные файлы, инвентаризация, перенос между компьютерами: `codex_kb\10_assets\LOCAL_COMPUTER.md`.

## Правила готовности

- Перед работой сверить задачу с `CHAT_DISPATCHER.md`.
- Перед любыми секретами сверить `SECURITY_POLICY.md`.
- Если задача касается 1С, проверить metadata blocker в `codex_kb\progress\1C_PROGRESS.md`.
- После значимых изменений обновить `PROGRESS.md` и доменный progress-файл.
- После изменений в `00_global` или `20_domains` проверить необходимость RAG-sync.
- Все `.md` с кириллицей сохранять как UTF-8 with BOM.

## Архив

Сырые экспорты старых чатов сохранены здесь:

```text
E:\Codex_Work\chat_exports
```

Они не удаляются и используются как доказательный архив. Текущая рабочая база знаний:

```text
E:\Codex_Work\codex_kb
```

Текущие рабочие материалы:

```text
E:\Codex_Work\projects
```

Старые черновики и разовые outputs:

```text
E:\Codex_Work\Архив
```
