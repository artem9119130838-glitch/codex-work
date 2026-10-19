#!/bin/bash
set -e

BACKUP_NAME="full-backup-$(date +%Y-%m-%d_%H-%M)"
BACKUP_DIR="/Storage/$BACKUP_NAME"
LOG_FILE="/Storage/backup.log"

echo "=== STARTING FULL VPS BACKUP AT $(date) ===" > "$LOG_FILE"
echo "Backup folder: $BACKUP_DIR" >> "$LOG_FILE"

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
tar -czf "$BACKUP_DIR/configs/1c_licenses.tar.gz" -C /var/1C licenses
tar -czf "$BACKUP_DIR/configs/1c_home.tar.gz" -C /home/usr1cv8 .1cv8
if [ -d "/Storage/home/usr1cv8" ]; then
  tar -czf "$BACKUP_DIR/configs/1c_storage_home.tar.gz" -C /Storage/home/usr1cv8 .1cv8
fi
tar -czf "$BACKUP_DIR/configs/apache2.tar.gz" -C /etc apache2
tar -czf "$BACKUP_DIR/configs/letsencrypt.tar.gz" -C /etc letsencrypt
tar -czf "$BACKUP_DIR/configs/wireguard.tar.gz" -C /etc wireguard
tar -czf "$BACKUP_DIR/configs/openvpn.tar.gz" -C /etc openvpn
tar -czf "$BACKUP_DIR/configs/system_users.tar.gz" /etc/passwd /etc/group /etc/shadow
if [ -d "/var/spool/cron/crontabs" ]; then
  tar -czf "$BACKUP_DIR/configs/crontabs.tar.gz" /var/spool/cron/crontabs /etc/crontab
fi
tar -czf "$BACKUP_DIR/configs/wireguard_client_profiles.tar.gz" -C /root --exclude='.*' $(cd /root && ls *.conf 2>/dev/null || true)
iptables-save > "$BACKUP_DIR/configs/iptables.rules"

# 4. Web publications 1C
echo "Archiving 1C web publication directories..." >> "$LOG_FILE"
tar -czf "$BACKUP_DIR/configs/vrd_www.tar.gz" -C /var www

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
tar -czf "$BACKUP_DIR/docker/docker_n8n.tar.gz" -C /Storage/docker n8n
tar -czf "$BACKUP_DIR/docker/docker_n8n_eng.tar.gz" -C /Storage/docker n8n-eng
tar -czf "$BACKUP_DIR/docker/docker_3x_ui.tar.gz" -C /Storage/docker 3x-ui
tar -czf "$BACKUP_DIR/docker/docker_metabase_data.tar.gz" -C /Storage/docker metabase_data

echo "Restarting Docker containers..." >> "$LOG_FILE"
cd /Storage/docker/n8n && docker-compose up -d
cd /Storage/docker/n8n-eng && docker-compose up -d
cd /Storage/docker/3x-ui && docker-compose up -d
docker start metabase || true

# 6. AI Projects and Scripts
echo "Archiving AI projects and system scripts..." >> "$LOG_FILE"
tar -czf "$BACKUP_DIR/root_projects/n8n_email_ai.tar.gz" -C /root n8n_email_ai
tar -czf "$BACKUP_DIR/root_projects/pgvector_db_project.tar.gz" -C /root pgvector-db
tar -czf "$BACKUP_DIR/root_projects/tender_rag_api.tar.gz" -C /root tender-rag-api
tar -czf "$BACKUP_DIR/root_projects/storage_scripts.tar.gz" -C /Storage scripts
if [ -d "/opt/longwang_trend_radar" ]; then
  tar -czf "$BACKUP_DIR/root_projects/longwang_trend_radar.tar.gz" -C /opt longwang_trend_radar
fi

# 7. Retention: keep latest 1 full backup, remove older
echo "Running retention policy (keeping only latest full backup)..." >> "$LOG_FILE"
backups_count=$(find /Storage -maxdepth 1 -name "full-backup-*" -type d | wc -l)
if [ "$backups_count" -gt 1 ]; then
  find /Storage -maxdepth 1 -name "full-backup-*" -type d -printf '%T@ %p\n' | sort -n | cut -d' ' -f2- | head -n -1 | while read -r old_backup; do
    rm -rf -- "$old_backup"
    echo "Deleted old backup: $old_backup" >> "$LOG_FILE"
  done
fi

echo "=== FULL VPS BACKUP COMPLETE: $BACKUP_DIR AT $(date) ===" >> "$LOG_FILE"
