#!/bin/bash
BACKUP_DIR="/Storage/vps_backup_archive"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "=== Start VPS backup: $(date) ===" >> /Storage/vps_backup.log

# 1. pg_dump of marketing_db from docker container
docker exec -t pgvector-db pg_dump -U vector_user marketing_db > "$BACKUP_DIR/pgvector_marketing_db_$DATE.sql"
echo "pgvector database marketing_db dumped successfully" >> /Storage/vps_backup.log

# 2. Archive all projects from /root/ (n8n_email_ai, pgvector-db, tender-rag-api, main docker-compose.yml)
tar -czf "$BACKUP_DIR/root_projects_$DATE.tar.gz" \
  -C /root/ \
  --exclude="n8n_email_ai/venv" \
  --exclude="n8n_email_ai/logs" \
  --exclude="n8n_email_ai/scratch" \
  --exclude="tender-rag-api/venv" \
  n8n_email_ai pgvector-db tender-rag-api docker-compose.yml update_vps_compose.py update_email_compose.py
echo "Root projects archived" >> /Storage/vps_backup.log

# 3. Archive n8n data volumes (including workflows, credentials, etc.)
tar -czf "$BACKUP_DIR/n8n_data_$DATE.tar.gz" -C /Storage/docker/ n8n n8n-eng
echo "n8n data volumes archived" >> /Storage/vps_backup.log

# 4. Rotation (delete backups older than 7 days)
find "$BACKUP_DIR" -type f -mtime +7 -delete
echo "Rotation finished" >> /Storage/vps_backup.log
echo "=== VPS Backup completed: $(date) ===" >> /Storage/vps_backup.log
