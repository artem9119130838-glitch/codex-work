# Server Infrastructure Progress

Дата обновления: 2026-06-20

## Status

Server facts are documented. Changes must be conservative because the VPS is production-like.

## Current Known Services

- Apache
- Docker/n8n
- 1C Enterprise
- PostgreSQL/Postgres Pro
- WireGuard (классический, замедляется ТСПУ на мобильных)
- OpenVPN
- 3X-UI / VLESS-Reality (развернут в Docker 20.06.2026 для обхода блокировок)

## Изменения инфраструктуры (Лог обновлений)

### 20 июня 2026 г.
- **Проблема**: Критическое падение скорости WireGuard на мобильных устройствах (iOS/Android) из-за сигнатурных блокировок ТСПУ (DPI).
- **Решение**: Параллельно классическому WireGuard развернута панель **3X-UI** в Docker (`/Storage/docker/3x-ui`).
- **Спецификация**:
  - Образ: `ghcr.io/mhsanaei/3x-ui:latest` (docker-compose v3).
  - Порт панели: `2053` (TCP, открыт в ufw).
  - Порт VLESS-Reality: `8443` (TCP, открыт в ufw).
- **Статус**: Панель успешно запущена, VLESS-Reality настроен в параллельном режиме. Проводной WireGuard (`wg0`) на порту `51820` оставлен для пользователей без изменений.

### 21 июня 2026 г.
- **Проблема**: Проблемы с усыплением VPN-клиентов в фоне на iOS/Android и ограничениями песочницы на iOS, ломающие стабильную работу Telegram.
- **Решение**: Развернут контейнер **MTProto-прокси** (`ghcr.io/9seconds/mtg:latest`) на порту `8585` с маскировкой Fake TLS под `jojoq.kz`.
- **Статус**: Активен. Был временно остановлен, но возвращен по запросу пользователя. Прокси работает нестабильно (с обрывами) из-за сигнатурного подавления ТСПУ/DPI и периодических блокировок подсетей. Reality VPN работает параллельно.

## Next

- Найти альтернативный сервер (например, в другой локации) для проксирования Telegram, если это критично.
- Keep Apache changes behind `apachectl configtest`.
- Avoid 1C/PostgreSQL restarts without explicit approval.
- Verify Docker root remains `/Storage/docker-data`.
- Keep `C:\Codex_Personal` KB structure as the active Codex workspace control plane.

