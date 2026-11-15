#!/bin/bash
set -eo pipefail

BACKUP_NAME="full-backup-$(date +%Y-%m-%d_%H-%M)"
BACKUP_DIR="/Storage/$BACKUP_NAME"
LOG_FILE="/Storage/backup.log"
WEBHOOK_URL="https://n8n.3develop.ru/webhook/tender-security-alerts"

echo "=== STARTING FULL VPS BACKUP AT $(date) ===" > "$LOG_FILE"
echo "Backup target: $BACKUP_DIR" >> "$LOG_FILE"

# Trap handler: in case of error, clean up incomplete folder to prevent disk overflow
cleanup_on_error() {
  local exit_code=$?
  echo "❌ CRITICAL: Backup script encountered error (exit code: $exit_code)!" >> "$LOG_FILE"
  if [ -d "$BACKUP_DIR" ]; then
    echo "Cleaning up incomplete backup folder: $BACKUP_DIR..." >> "$LOG_FILE"
    rm -rf -- "$BACKUP_DIR"
  fi
  # Always ensure Docker containers are brought back up
  cd /Storage/docker/n8n && docker-compose up -d >/dev/null 2>&1 || true
  cd /Storage/docker/n8n-eng && docker-compose up -d >/dev/null 2>&1 || true
  cd /Storage/docker/3x-ui && docker-compose up -d >/dev/null 2>&1 || true
  docker start metabase >/dev/null 2>&1 || true
  curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"text\":\"🚨 [VPS Alert] Сбой еженедельного бэкапа VPS (код $exit_code)! Неполная папка удалена для защиты диска.\"}" \
    "$WEBHOOK_URL" > /dev/null 2>&1 || true
  exit $exit_code
}
trap cleanup_on_error ERR INT TERM

# 0. PRE-EXECUTION RETENTION: Keep STRICTLY 1 previous full backup before starting new one
echo "Enforcing pre-execution retention..." >> "$LOG_FILE"
existing_full=$(find /Storage -maxdepth 1 -name "full-backup-*" -type d 2>/dev/null | wc -l)
if [ "$existing_full" -gt 1 ]; then
  find /Storage -maxdepth 1 -name "full-backup-*" -type d -printf '%T@ %p\n' | sort -n | cut -d' ' -f2- | head -n -1 | while read -r old_b; do
    rm -rf -- "$old_b"
    echo "Pre-cleanup deleted old backup: $old_b" >> "$LOG_FILE"
  done
fi

mkdir -p "$BACKUP_DIR/databases" "$BACKUP_DIR/configs" "$BACKUP_DIR/docker" "$BACKUP_DIR/root_projects"
chown postgres:postgres "$BACKUP_DIR/databases"

# 1. PostgreSQL Pro dumps (Globals + all live databases)
echo "Dumping Postgres Pro globals..." >> "$LOG_FILE"
sudo -u postgres /opt/pgpro/std-14/bin/pg_dumpall -U postgres --globals-only > "$BACKUP_DIR/databases/postgres_globals.sql"

databases="unf buh money money_restored nextcloud marketing_db borich"
for db in $databases; do
  echo "Dumping database: $db..." >> "$LOG_FILE"
  sudo -u postgres /opt/pgpro/std-14/bin/pg_dump -U postgres --dbname="$db" --format=directory --jobs=4 --compress=9 --file="$BACKUP_DIR/databases/$db.dump"
  echo "Dump of $db completed" >> "$LOG_FILE"
done

# 2. Vector database pgvector from Docker
echo "Dumping vector database from Docker..." >> "$LOG_FILE"
docker exec -t pgvector-db pg_dump -U vector_user marketing_db > "$BACKUP_DIR/databases/marketing_db_pgvector.sql"

# 3. Configurations and licenses (1C, VPN, Apache, SSL, users, firewall)
echo "Archiving configurations and licenses..." >> "$LOG_FILE"
tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/1c_licenses.tar.gz" -C /var/1C licenses || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/1c_home.tar.gz" -C /home/usr1cv8 .1cv8 || true
if [ -d "/Storage/home/usr1cv8" ]; then
  tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/1c_storage_home.tar.gz" -C /Storage/home/usr1cv8 .1cv8 || true
fi
tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/apache2.tar.gz" -C /etc apache2 || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/letsencrypt.tar.gz" -C /etc letsencrypt || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/wireguard.tar.gz" -C /etc wireguard || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/openvpn.tar.gz" -C /etc openvpn || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/system_users.tar.gz" /etc/passwd /etc/group /etc/shadow || true
if [ -d "/var/spool/cron/crontabs" ]; then
  tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/crontabs.tar.gz" /var/spool/cron/crontabs /etc/crontab || true
fi
tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/wireguard_client_profiles.tar.gz" -C /root --exclude='.*' $(cd /root && ls *.conf 2>/dev/null || true) || true
iptables-save > "$BACKUP_DIR/configs/iptables.rules" || true

# 4. Web publications 1C
echo "Archiving 1C web publication directories..." >> "$LOG_FILE"
tar --warning=no-file-changed -czf "$BACKUP_DIR/configs/vrd_www.tar.gz" -C /var www || true

# 5. Docker services maintenance & data backup
echo "Stopping Docker containers for SQLite maintenance..." >> "$LOG_FILE"
cd /Storage/docker/n8n && docker-compose down
cd /Storage/docker/n8n-eng && docker-compose down
cd /Storage/docker/3x-ui && docker-compose down
docker stop metabase || true

echo "Running SQLite VACUUM on n8n databases..." >> "$LOG_FILE"
python3 -c "
import sqlite3
for path in ['/Storage/docker/n8n/n8n_data/database.sqlite', '/Storage/docker/n8n-eng/n8n_data/database.sqlite']:
    try:
        conn = sqlite3.connect(path)
        conn.execute('VACUUM;')
        conn.close()
        print('VACUUM successfully completed for:', path)
    except Exception as e:
        print('Error running VACUUM on', path, ':', e)
" >> "$LOG_FILE" 2>&1

echo "Archiving Docker folders..." >> "$LOG_FILE"
tar --warning=no-file-changed -czf "$BACKUP_DIR/docker/docker_n8n.tar.gz" -C /Storage/docker n8n || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/docker/docker_n8n_eng.tar.gz" -C /Storage/docker n8n-eng || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/docker/docker_3x_ui.tar.gz" -C /Storage/docker 3x-ui || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/docker/docker_metabase_data.tar.gz" -C /Storage/docker metabase_data || true

echo "Restarting Docker containers..." >> "$LOG_FILE"
cd /Storage/docker/n8n && docker-compose up -d
cd /Storage/docker/n8n-eng && docker-compose up -d
cd /Storage/docker/3x-ui && docker-compose up -d
docker start metabase || true

# 6. AI Projects and Scripts
echo "Archiving AI projects and system scripts..." >> "$LOG_FILE"
tar --warning=no-file-changed -czf "$BACKUP_DIR/root_projects/n8n_email_ai.tar.gz" -C /root n8n_email_ai || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/root_projects/pgvector_db_project.tar.gz" -C /root pgvector-db || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/root_projects/tender_rag_api.tar.gz" -C /root tender-rag-api || true
tar --warning=no-file-changed -czf "$BACKUP_DIR/root_projects/storage_scripts.tar.gz" -C /Storage scripts || true
if [ -d "/opt/longwang_trend_radar" ]; then
  tar --warning=no-file-changed -czf "$BACKUP_DIR/root_projects/longwang_trend_radar.tar.gz" -C /opt longwang_trend_radar || true
fi

# 7. POST-EXECUTION RETENTION: Keep STRICTLY 1 latest backup, delete previous
echo "Enforcing post-execution retention (keeping strictly 1 latest backup)..." >> "$LOG_FILE"
backups_count=$(find /Storage -maxdepth 1 -name "full-backup-*" -type d 2>/dev/null | wc -l)
if [ "$backups_count" -gt 1 ]; then
  find /Storage -maxdepth 1 -name "full-backup-*" -type d -printf '%T@ %p\n' | sort -n | cut -d' ' -f2- | head -n -1 | while read -r old_b; do
    rm -rf -- "$old_b"
    echo "Deleted previous full backup (kept 1 latest): $old_b" >> "$LOG_FILE"
  done
fi

echo "=== FULL VPS BACKUP COMPLETE: $BACKUP_DIR AT $(date) ===" >> "$LOG_FILE"
