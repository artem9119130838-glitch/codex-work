#!/bin/bash
set -e

PROJECT_DIR="/root/tender-rag-api"
LOG_FILE="/var/log/tender_auto_deploy.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cd "$PROJECT_DIR"

# Проверяем наличие обновлений в ветке mikhail-origin/main
git fetch mikhail-origin main >> "$LOG_FILE" 2>&1 || {
    git fetch origin main >> "$LOG_FILE" 2>&1 || true
}

LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse mikhail-origin/main 2>/dev/null || git rev-parse origin/main 2>/dev/null)

if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
    log "🚀 Обнаружены новые коммиты Михаила! ($LOCAL_HASH -> $REMOTE_HASH)"
    
    # Проверяем, изменились ли зависимости или Dockerfile
    REBUILD_NEEDED=0
    if git diff --name-only "$LOCAL_HASH" "$REMOTE_HASH" | grep -E "requirements|Dockerfile|docker-compose" > /dev/null; then
        REBUILD_NEEDED=1
    fi
    
    log "Обновление рабочей директории..."
    git reset --hard "$REMOTE_HASH" >> "$LOG_FILE" 2>&1
    
    log "Проверка синтаксиса Python..."
    if python3 -m py_compile app/main.py app/services/*.py >> "$LOG_FILE" 2>&1; then
        if [ "$REBUILD_NEEDED" -eq 1 ]; then
            log "📦 Изменились зависимости. Пересборка Docker-образа..."
            docker-compose -f docker-compose.prod.yml up -d --build api >> "$LOG_FILE" 2>&1
        else
            log "⚡ Быстрый перезапуск контейнера tender-rag-api-prod..."
            docker restart tender-rag-api-prod >> "$LOG_FILE" 2>&1
        fi
        
        sleep 4
        # Проверка работоспособности
        if curl -s -f http://127.0.0.1:8000/health > /dev/null; then
            log "✅ Деплой успешно завершен! Сервис отдает 200 OK."
        else
            log "⚠️ Внимание: Контейнер перезапущен, но healthcheck не ответил 200."
        fi
    else
        log "❌ Ошибка синтаксиса Python! Деплой отменен, откат изменений..."
        git reset --hard "$LOCAL_HASH" >> "$LOG_FILE" 2>&1
    fi
else
    exit 0
fi
