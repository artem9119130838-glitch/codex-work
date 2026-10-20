# Регламент аварийного резервного копирования и быстрого восстановления VPS (Disaster Recovery Runbook)

> **Статус документа:** Боевой регламент аварийного восстановления VPS `109.248.170.181` (Ubuntu 22.04 LTS).  
> **Целевое время восстановления (RTO):** 20–30 минут с момента развертывания базовой ОС.  
> **Связанные документы:** [INFRA_VPS_POLICY.md](file:///C:/Codex/codex_kb/20_domains/infra_vps/INFRA_VPS_POLICY.md), [SERVER_OPS_RUNBOOK.md](file:///C:/Codex/codex_kb/30_runbooks/SERVER_OPS_RUNBOOK.md).  
> **Локальный каталог бэкапов:** `D:\server-backups\full-backup-<YYYY-MM-DD_HH-MM>`

---

## 1. Архитектура и состав аварийного снимка (DRP)

Резервный снимок создается скриптом [/Storage/run_server_backup.sh](file:///C:/Codex/scripts/vps/run_server_backup.sh) и сохраняется в `/Storage/full-backup-<дата>`.

| Компонент | Состав архива | Назначение при восстановлении |
|---|---|---|
| **`databases/`** | `unf.dump` (4 потока, сжатие 9), `buh.dump`, `money.dump`, `money_restored.dump`, `marketing_db.dump`, `nextcloud.dump`, `borich.dump`, `postgres_globals.sql`, `marketing_db_pgvector.sql` (4.9 ГБ) | Полное восстановление кластера PostgreSQL Pro 14 и векторной базы RAG |
| **`configs/`** | `1c_licenses.tar.gz`, `1c_home.tar.gz` (профиль кластера 1С и журнал регистрации), `vrd_www.tar.gz` (веб-публикации 1С), `apache2.tar.gz`, `letsencrypt.tar.gz`, `wireguard.tar.gz`, `wireguard_client_profiles.tar.gz`, `openvpn.tar.gz`, `iptables.rules`, `system_users.tar.gz`, `crontabs.tar.gz` | Восстановление сетевого контура, туннелей VPN, SSL и сервера 1С |
| **`docker/`** | `docker_3x_ui.tar.gz` (панель Xray/VLESS), `docker_n8n.tar.gz`, `docker_n8n_eng.tar.gz` (после SQLite `VACUUM`), `docker_metabase_data.tar.gz` | Восстановление рабочих сред и воркфлоу n8n, VPN-панели и аналитики |
| **`root_projects/`**| `tender_rag_api.tar.gz`, `n8n_email_ai.tar.gz`, `longwang_trend_radar.tar.gz`, `storage_scripts.tar.gz`, `pgvector_db_project.tar.gz` | Исходный код сервисов, ботов, демонов и AI-контуров с их `.env` файлами |

---

## 2. Создание снимка и синхронизация на диск D:

1. **Создание снимка на VPS (в фоне):**
   ```bash
   nohup /bin/bash /Storage/run_server_backup.sh > /Storage/backup_run.log 2>&1 &
   # Контроль хода: tail -f /Storage/backup.log
   ```
2. **Выгрузка на локальный ПК (Windows PowerShell):**
   ```powershell
   powershell.exe -ExecutionPolicy Bypass -File "C:\Codex\scripts\download_vps_backup.ps1"
   ```
   *Скрипт находит последний бэкап на сервере, скачивает его по SCP в `D:\server-backups` и удаляет локальные архивы старше 30 дней.*

---

## 3. Пошаговый регламент аварийного восстановления (20–30 минут)

При полной переустановке ОС Ubuntu 22.04 LTS:

### Шаг 0. Базовая подготовка чистой ОС (5 минут)
```bash
# Установка базовых утилит, Docker, PostgreSQL Pro 14 и платформы 1С
apt-get update && apt-get install -y wireguard openvpn apache2 iptables docker.io docker-compose
# Установить пакеты postgrespro-std-14 и 1cv8 (дистрибутивы из /Storage/1c_distr при наличии)
```

### Шаг 1. Восстановление конфигураций, сети и VPN (5 минут)
Перейти в распакованную директорию бэкапа:
```bash
# 1. Сеть, файрвол и VPN
tar -xzf configs/wireguard.tar.gz -C /etc
tar -xzf configs/openvpn.tar.gz -C /etc
tar -xzf configs/apache2.tar.gz -C /etc
tar -xzf configs/letsencrypt.tar.gz -C /etc
iptables-restore < configs/iptables.rules
tar -xzf configs/system_users.tar.gz -C /

# 2. Лицензии 1С и кластер серверов
mkdir -p /var/1C /Storage/home/usr1cv8
tar -xzf configs/1c_licenses.tar.gz -C /var/1C
tar -xzf configs/1c_home.tar.gz -C /Storage/home/usr1cv8
tar -xzf configs/vrd_www.tar.gz -C /var
chown -R usr1cv8:grp1cv8 /Storage/home/usr1cv8

# 3. Старт сетевых служб и веб-сервера
systemctl restart wg-quick@wg0 openvpn@server apache2 srv1cv8-8.3*
# (WireGuard, OpenVPN, Apache и лицензии 1С уже в строю!)
```

### Шаг 2. Параллельный импорт баз PostgreSQL Pro (12–15 минут)
```bash
# 1. Роли и глобальные привилегии
sudo -u postgres psql -f databases/postgres_globals.sql

# 2. Восстановление базы 1С:УНФ в 4 параллельных потока
sudo -u postgres createdb -T template1 unf
sudo -u postgres /opt/pgpro/std-14/bin/pg_restore -U postgres --format=directory --jobs=4 --dbname=unf databases/unf.dump

# 3. Восстановление Бухгалтерии и малых баз
sudo -u postgres createdb -T template1 buh
sudo -u postgres /opt/pgpro/std-14/bin/pg_restore -U postgres --format=directory --jobs=4 --dbname=buh databases/buh.dump

for db in money money_restored marketing_db nextcloud borich; do
  sudo -u postgres createdb -T template1 $db
  sudo -u postgres /opt/pgpro/std-14/bin/pg_restore -U postgres --format=directory --jobs=4 --dbname=$db databases/$db.dump
done
# (Все базы 1С полностью развернуты и доступны пользователям!)
```

### Шаг 3. Запуск Docker-сервисов и AI-проектов (5 минут)
```bash
# 1. Распаковка Docker томов
mkdir -p /Storage/docker /root
tar -xzf docker/docker_3x_ui.tar.gz -C /Storage/docker
tar -xzf docker/docker_n8n.tar.gz -C /Storage/docker
tar -xzf docker/docker_n8n_eng.tar.gz -C /Storage/docker
tar -xzf docker/docker_metabase_data.tar.gz -C /Storage/docker

# 2. Распаковка AI проектов и скриптов
tar -xzf root_projects/tender_rag_api.tar.gz -C /root
tar -xzf root_projects/n8n_email_ai.tar.gz -C /root
tar -xzf root_projects/storage_scripts.tar.gz -C /Storage
if [ -f "root_projects/longwang_trend_radar.tar.gz" ]; then
  mkdir -p /opt && tar -xzf root_projects/longwang_trend_radar.tar.gz -C /opt
fi

# 3. Импорт pgvector и запуск контейнеров
cd /root/pgvector-db && docker-compose up -d
sleep 5
docker exec -i pgvector-db psql -U vector_user marketing_db < databases/marketing_db_pgvector.sql

cd /Storage/docker/3x-ui && docker-compose up -d
cd /Storage/docker/n8n && docker-compose up -d
cd /Storage/docker/n8n-eng && docker-compose up -d
docker start metabase
cd /root/tender-rag-api && docker-compose up -d

# 4. Восстановление расписания crontab
tar -xzf configs/crontabs.tar.gz -C /
crontab /var/spool/cron/crontabs/root
# (Все сервисы, автоматизации, VPN-панель и BI подняты!)
```

---

## 4. Инварианты надежности и защита от рецидивов

1. **Unix LF Invariant:** Все bash-скрипты бэкапов обязаны создаваться строго с окончаниями строк Unix LF (`\n`). Сохранение CRLF ведет к падению в cron (`syntax error near unexpected token 'do\r'`). Проверка перед развертыванием: `bash -n script.sh`.
2. **Tar Live-Log Rule:** При архивации каталогов с активными службами (журналы регистрации 1С, SQLite, сокеты) архиватор `tar` обязан запускаться с флагом `--warning=no-file-changed`. Это предотвращает аварийное завершение скриптов под `set -e` при дозаписи логов во время чтения.
3. **Safe Retention:** Скрипты обязаны сохранять как минимум 1 последний рабочий бэкап, удаляя старые только после успешного завершения нового.
