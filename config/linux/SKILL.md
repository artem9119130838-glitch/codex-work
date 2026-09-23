---
name: Linux Server Administration
description: Администрирование Linux (Ubuntu VPS), анализ логов аутентификации auth.log, управление системными службами systemd и контейнерами Docker, настройка бэкапов Docker/pgvector и диагностика сетевых портов.
---

# Навык: Администрирование Linux Server

Этот навык используется при выполнении задач на Ubuntu VPS (например, аудит безопасности, проверка SSH-ключей, управление Docker, настройка бэкапов и ротации логов).

## 1. Проверка SSH-ключей и аудита доступа

### Список разрешенных ключей:
Ключи доступа хранятся в домашней директории пользователей: `~/.ssh/authorized_keys`.
Команда для вывода всех ключей на сервере:
```bash
for user in $(cut -f1 -d: /etc/passwd); do
  home=$(eval echo ~$user)
  if [ -f "$home/.ssh/authorized_keys" ]; then
    echo "=== Пользователь: $user ==="
    cat "$home/.ssh/authorized_keys"
  fi
done
```

### Проверка истории входов по ключам:
Поиск успешных SSH-подключений в логе авторизации `/var/log/auth.log` (включая ротированные архивы):
```bash
sudo zgrep "Accepted publickey" /var/log/auth.log*
```

---

## 2. Управление службами, Docker и Конфликты Портов

### Службы Systemd (1C, PostgreSQL, Apache):
* Проверить статус: `sudo systemctl status <service_name>`
* Перезагрузить веб-сервер Apache безопасно (сначала проверить конфиг):
  ```bash
  sudo apachectl configtest && sudo systemctl reload apache2
  ```

### Работа с Docker и Docker Compose:
* Вывод запущенных контейнеров: `docker ps`
* Логи конкретного контейнера: `docker logs --tail 100 -f <container_name>`
* **Обновление переменных окружения (.env)**: Команда `docker-compose restart <service_name>` **НЕ перечитывает** изменения в файле `.env`, так как она лишь перезапускает процесс внутри существующего контейнера. Для применения изменений в переменных окружения всегда используйте `docker-compose up -d`.

### Разрешение имен в контейнерах (DNS и /etc/hosts):
* **Поведение bridge-контейнеров**: Контейнеры, работающие в bridge-сетях, по умолчанию игнорируют файл `/etc/hosts` хоста. 
* **Решение**: Прописывать `extra_hosts` в `docker-compose.yml` и **пересоздавать** контейнер командой `docker-compose up -d --force-recreate` (простой `restart` НЕ обновляет hosts файлы внутри контейнера).
* **Пример docker-compose.yml с пробросом hosts для Gemini**:
  ```yaml
  services:
    api-service:
      image: my-service-image:latest
      extra_hosts:
        - "generativelanguage.googleapis.com:87.228.47.204"
  ```
* **Host-контейнеры**: Контейнеры с `network_mode: "host"` используют системный `/etc/hosts` хоста автоматически.


### Решение конфликтов сетевых портов:
Если Apache, Nginx или служба 1С не запускаются из-за ошибки `Address already in use`, ИИ должен запустить диагностику:
1. Выявить процесс, занявший порт (например, 80 или 443):
   ```bash
   sudo ss -tulpn | grep :80
   # или
   sudo lsof -i :80
   ```
2. Остановить конфликтующую службу или убить зависший процесс:
   ```bash
   sudo systemctl stop nginx
   # или убить процесс по PID:
   sudo kill -9 <PID>
   ```

---

## 3. Резервное копирование и автоматизация задач обслуживания

При настройке бэкапов на сервере (например, в каталоге `/Storage/`) используйте готовые паттерны скриптов.

### Шаблон скрипта бэкапа (run_server_backup.sh):
Скрипт делает дамп pgvector из контейнера Docker, архивирует ИИ-проекты с их `.env` файлами из `/root/`, ротирует бэкапы на 14 дней и выводит логи:
```bash
#!/bin/bash
BACKUP_DIR="/Storage/vps_backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "=== Старт бэкапа: $(date) ===" >> /Storage/backup.log

# 1. Дамп базы pgvector из Docker контейнера
docker exec -t pgvector-db-container pg_dump -U postgres -d rag_db > "$BACKUP_DIR/pgvector_dump_$DATE.sql"
echo "Дамп pgvector сохранен" >> /Storage/backup.log

# 2. Архивация проектов ИИ из /root/ с .env файлами
tar -czf "$BACKUP_DIR/ai_projects_$DATE.tar.gz" -C /root/ my-ai-project-1 my-ai-project-2
echo "Проекты ИИ архивированы" >> /Storage/backup.log

# 3. Ротация (удаление файлов старше 14 дней)
find "$BACKUP_DIR" -type f -mtime +14 -delete
echo "Ротация завершена" >> /Storage/backup.log
echo "=== Конец бэкапа: $(date) ===" >> /Storage/backup.log
```

### Настройка cron:
*   Полный бэкап по воскресеньям в 02:00:
    `0 2 * * 0 /bin/bash /Storage/run_server_backup.sh`
*   Быстрый бэкап баз 1С по будням в 02:00:
    `0 2 * * 1-5 /bin/bash /Storage/backup-sql.sh`

---

## 4. Маршрутизация трафика на роутерах Keenetic (VPN и DNS)

При решении сетевых проблем с доступом к Gemini API через VPN (Amnezia / WireGuard):
1.  **Проксирование DNS (DoT/DoH на Keenetic)**:
    Использование DNS-прокси (например, `xbox-dns.ru`) перенаправляет трафик заблокированных доменов (таких как Gemini) на сторонние SNI-прокси в РФ (например, `87.228.47.204` в Selectel). Это заставляет трафик идти через основного провайдера РФ, а не через VPN-туннель.
2.  **Задержки (Timeouts)**: Маршрутизация через SNI-прокси увеличивает время ответа API до **5-9 секунд**. Всегда настраивайте таймауты запросов (Connection / Read Timeout) в скриптах и воркфлоу n8n минимум на **30-60 секунд** во избежание ошибок `read operation timed out`.
3.  **Проверка DNS-маршрутизации (Keenetic CLI):**

    Проверьте, привязан ли домен Gemini к интерфейсу VPN:
    `show host google.com` или `show host gemini.google.com`
2.  **Настройка split-tunneling (через ssh на Keenetic под admin):**
    ```bash
    ip route domain gemini.google.com ConnectionName
    system configuration save
    ```
    *(Здесь ConnectionName — название VPN-подключения на Keenetic).*

---

## 5. Защита от сетевых блокировок (SSH Rate Limiting)

* **Лимит частоты подключений:** Не более 3 подключений `ssh`/`scp` в минуту. Частые коннекты ведут к бану IP через `Fail2ban`.
* **Группировка команд (Command Chaining):** Всегда объединяйте несколько команд в одну сессию SSH с помощью операторов `&&` или `;`.
  * *Пример:* `ssh root@IP "cd /opt && ls -la && docker ps"`
* **Пакетное выполнение (Script-First)**: Если нужно выполнить более 3 команд, запишите их в скрипт, отправьте на сервер по `scp` и выполните один раз по `ssh`.
* **Экранирование кавычек при вызове команд по SSH из Windows (PowerShell)**: При передаче команд со сложными кавычками (например, SQL-запросов `psql -c "..."` или команд `sed`) из PowerShell через SSH, кавычки часто ломаются на стороне сервера (`unexpected EOF` или `syntax error`).
  * *Решение*: Запишите SQL-запрос во временный локальный файл (например, `db/query.sql` или `verify.sql`), скопируйте его на сервер через `scp`, запустите его локально на сервере (`psql -f /tmp/query.sql`) и затем удалите. Это полностью исключает ошибки парсинга кавычек.

---

## 6. Экстренное обслуживание баз SQLite (n8n) и очистка диска VPS

### Быстрое сжатие раздутых баз n8n SQLite (без WAL-переполнения):
Когда база n8n разрастается из-за истории запусков (например, до 20-50 ГБ), стандартный `VACUUM` или `DELETE FROM` на HDD забивает диск временным WAL-файлом (`.sqlite-wal`) и зависает на часы.

**Мгновенный способ сжатия (за 1 секунду без потери сценариев и доступов):**
1. Остановить контейнер: `docker-compose down`
2. Переименовать `database.sqlite` в `database_old.sqlite`.
3. Запустить Python-скрипт клонирования схемы из `sqlite_master`:
   ```python
   import sqlite3, os
   conn_old = sqlite3.connect('database_old.sqlite')
   conn_new = sqlite3.connect('database.sqlite')
   # Клонируем таблицы и индексы
   for (sql,) in conn_old.cursor().execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL").fetchall():
       try: conn_new.cursor().execute(sql)
       except: pass
   for (sql,) in conn_old.cursor().execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL").fetchall():
       try: conn_new.cursor().execute(sql)
       except: pass
   # Копируем только настройки и сценарии
   tables = ['user', 'project', 'project_relation', 'role', 'scope', 'role_scope', 'settings', 'tag_entity', 'workflows_tags', 'workflow_entity', 'credentials_entity', 'workflow_dependency', 'shared_workflow', 'shared_credentials']
   conn_new.cursor().execute("PRAGMA foreign_keys = OFF;")
   for t in tables:
       cols = [c[1] for c in conn_old.cursor().execute(f"PRAGMA table_info({t})").fetchall()]
       rows = conn_old.cursor().execute(f"SELECT {', '.join(cols)} FROM {t}").fetchall()
       conn_new.cursor().executemany(f"INSERT INTO {t} VALUES ({','.join(['?']*len(cols))})", rows)
   conn_new.commit()
   ```
4. Удалить `database_old.sqlite*` и запустить n8n: `docker-compose up -d`.

### Безопасная очистка Docker-образов:
При нехватке места очищайте старые неиспользуемые сборки:
```bash
docker image prune -a -f
```

---

## 7. Безопасная ротация бэкапов и работа при переполнении диска

### Правило независимой очистки бэкапов:
* **Никогда** не связывайте создание резервной копии и очистку старых файлов через логическое `&&` (например, `pg_dump ... && find ... -delete`). Если бэкап завершится ошибкой (например, из-за внезапного заполнения диска), очистка не выполнится, что приведет к перманентной блокировке сервера. 
* **Решение:** Выполняйте очистку старых файлов в скрипте всегда, независимо от статуса выполнения команды резервного копирования.

### Защита от стирания всех бэкапов (Safe Retention):
* При ротации файлов по времени (например, `find -mtime +N -delete`) всегда добавляйте проверку количества оставшихся копий. Если бэкапы падают в течение длительного времени, стандартный поиск по времени удалит все старые бэкапы, и система останется с 0 копий.
* **Шаблон безопасной ротации в Bash (сохраняет как минимум 1 последний бэкап):**
  ```bash
  backups_count=$(find /path/to/backups -maxdepth 1 -name "db-*" -type d | wc -l)
  if [ "$backups_count" -gt 1 ]; then
      # Сортируем по времени и удаляем всё, кроме самой последней (свежей) копии
      find /path/to/backups -maxdepth 1 -name "db-*" -type d -mtime +2 -printf '%T@ %p\n' | sort -n | cut -d' ' -f2- | head -n -1 | while read -r old_backup; do
          rm -rf -- "$old_backup"
      done
  fi
  ```

### Загрузка скриптов при 100% заполнении `/tmp` или `/Storage`:
* Если диск `/Storage` (на котором смонтирован `/tmp`) заполнен на 100%, отправка файлов через `scp` в `/tmp` завершится ошибкой `write remote "/tmp/...": Failure`.
* **Решение:** В случае переполнения целевого диска загружайте временные скрипты диагностики/очистки на основной системный раздел (например, в `/root/cleanup.sh`), запускайте их оттуда и удаляйте после выполнения.


