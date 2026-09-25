#!/bin/bash
# Безопасный деплой проекта тендеров tender-rag-api для пользователя mikhail
# Выполняется через sudo /usr/local/bin/deploy-tender.sh или tender-webhook-deploy
set -e
LOG_FILE="/var/log/tender-deploy.log"
mkdir -p /var/log
echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Starting tender deployment ===" >> "$LOG_FILE"
cd /home/mikhail/tender-rag-api

# Выполняем git pull
if git remote get-url origin >/dev/null 2>&1; then
    echo "Pulling from origin main..." >> "$LOG_FILE"
    git pull origin main >> "$LOG_FILE" 2>&1 || true
fi

# Точечный перезапуск только контейнера tender-rag-api
echo "Rebuilding and restarting tender-rag-api-prod..." >> "$LOG_FILE"
docker-compose -f docker-compose.prod.yml up -d --build --no-deps api >> "$LOG_FILE" 2>&1

sleep 3
HEALTH=$(curl -s http://127.0.0.1:8000/health || echo "HEALTH_CHECK_FAILED")
echo "Healthcheck response: $HEALTH" >> "$LOG_FILE"
echo "=== Deployment finished successfully at $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG_FILE"
