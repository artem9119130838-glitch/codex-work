#!/bin/bash
# Disk space monitor with Bitrix24 webhook alerts and auto-safety guard
WEBHOOK_URL="https://n8n.3develop.ru/webhook/tender-security-alerts"
HOSTNAME=$(hostname)

# 1. Check root filesystem /
root_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$root_usage" -gt 85 ]; then
  curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"text\":\"🚨 [VPS Alert] Диск '/' на сервере $HOSTNAME заполнен на $root_usage%! Срочно освободите место.\"}" \
    "$WEBHOOK_URL" > /dev/null 2>&1 || true
fi

# 2. Check /Storage filesystem
storage_usage=$(df /Storage | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$storage_usage" -gt 85 ]; then
  curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"text\":\"🚨 [VPS Alert] Диск '/Storage' на сервере $HOSTNAME заполнен на $storage_usage%! Достигнут порог 85%.\"}" \
    "$WEBHOOK_URL" > /dev/null 2>&1 || true

  # Emergency guard: if over 90%, prune older archives automatically to prevent crash loop
  if [ "$storage_usage" -gt 90 ]; then
    echo "$(date) Emergency prune triggered: Storage usage at $storage_usage%" >> /var/log/disk_emergency.log
    # Delete any full backup beyond the 1 newest
    find /Storage -maxdepth 1 -name "full-backup-*" -type d -printf '%T@ %p\n' | sort -n | cut -d' ' -f2- | head -n -1 | while read -r b; do
      rm -rf -- "$b"
      echo "Emergency deleted old backup: $b" >> /var/log/disk_emergency.log
    done
    # Delete daily 1C backups older than 1 day
    for base in buh unf money; do
      find /Storage/backup -maxdepth 1 -name "${base}-*" -type d -printf '%T@ %p\n' | sort -n | cut -d' ' -f2- | head -n -1 | while read -r b; do
        rm -rf -- "$b"
        echo "Emergency deleted old 1C backup: $b" >> /var/log/disk_emergency.log
      done
    done
  fi
fi
