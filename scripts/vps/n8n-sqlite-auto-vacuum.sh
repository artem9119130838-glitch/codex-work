#!/bin/bash
# Еженедельное автоматическое обслуживание и сжатие SQLite баз данных n8n и n8n-eng
# Размещается в /usr/local/bin/n8n-sqlite-auto-vacuum.sh и связывается с /etc/cron.weekly/
MAX_SIZE_MB=500

for dir in /Storage/docker/n8n-eng/n8n_data /Storage/docker/n8n/n8n_data; do
    db="$dir/database.sqlite"
    if [ -f "$db" ]; then
        size_mb=$(du -m "$db" | cut -f1)
        if [ "$size_mb" -gt "$MAX_SIZE_MB" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Database $db is ${size_mb}MB (exceeds ${MAX_SIZE_MB}MB). Running VACUUM..." >> /var/log/n8n-vacuum.log
            sqlite3 "$db" "PRAGMA wal_checkpoint(TRUNCATE); VACUUM;" >> /var/log/n8n-vacuum.log 2>&1 || true
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] VACUUM completed for $db." >> /var/log/n8n-vacuum.log
        fi
    fi
done
