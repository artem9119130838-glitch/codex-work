# Манифест боевых скриптов VPS (109.248.170.181)

> Автоматически синхронизировано из боевого контура за 1 сессию SSH.
> Всего выгружено скриптов: 10 + crontab.

## Реестр зеркалированных скриптов

| Имя файла | Путь на VPS | Права | Размер | Назначение / Триггер |
| :--- | :--- | :--- | :--- | :--- |
| `run_server_backup.sh` | `/Storage/run_server_backup.sh` | `755` | 4877 B | Еженедельный полный бэкап VPS, дампы БД и SQLite maintenance |
| `backup-sql.sh` | `/Storage/backup-sql.sh` | `777` | 1766 B | Ежедневный дамп баз данных PostgreSQL / MySQL |
| `monitor_disk.sh` | `/Storage/monitor_disk.sh` | `755` | 1047 B | Мониторинг дискового пространства VPS с алертом в Битрикс24 |
| `restore_postgre.sh` | `/Storage/restore_postgre.sh` | `644` | 644 B | Восстановление PostgreSQL из резервной копии |
| `b24_daily_analytics_sync.py` | `/Storage/scripts/b24_daily_analytics_sync.py` | `755` | 12806 B | Ежедневная синхронизация аналитики Битрикс24 в БД |
| `clear_tmp.sh` | `/root/clear_tmp.sh` | `755` | 125 B | Очистка временных файлов и кэша |
| `vps_server_backup.sh` | `/root/vps_server_backup.sh` | `755` | 1328 B | Скрипт бэкапа n8n и pg_dump |
| `auto_deploy.sh` | `/root/tender-rag-api/scripts/auto_deploy.sh` | `755` | 2311 B | Автодеплой tender-rag-api по крону |
| `deploy-tender.sh` | `/usr/local/bin/deploy-tender.sh` | `755` | 871 B | Скрипт деплоя тендерного сервиса без удаления сети |
| `n8n-sqlite-auto-vacuum.sh` | `/usr/local/bin/n8n-sqlite-auto-vacuum.sh` | `755` | 702 B | Сжатие и очистка SQLite баз данных n8n без WAL |

## Активное расписание Crontab на VPS
```cron
0 2 * * 0 /bin/bash /Storage/run_server_backup.sh >/dev/null 2>&1
0 2 * * 1-6 /bin/sh /Storage/backup-sql.sh >/dev/null 2>&1
0 * * * * docker exec -u root -i onec_sync_daemon python3 -m app.run_imap --since-days 1 >/dev/null 2>&1
10 * * * * docker exec -u root -i onec_sync_daemon python3 -m app.run_summaries_batch >/dev/null 2>&1
0 9 * * * docker exec -u root -i onec_sync_daemon python3 -m app.run_daily_reactivation >/dev/null 2>&1
0 */4 * * * /bin/bash /Storage/monitor_disk.sh >/dev/null 2>&1
*/2 * * * * /root/tender-rag-api/scripts/auto_deploy.sh > /dev/null 2>&1
0 4 * * * /usr/bin/python3 /Storage/scripts/b24_daily_analytics_sync.py >> /var/log/b24_analytics_sync.log 2>&1
```
