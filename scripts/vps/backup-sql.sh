#!/bin/sh

# 1C Backup script with failure notification and safe retention
backup_cmd="/opt/pgpro/std-14/bin/pg_dump -U postgres --format=directory --jobs=4 --compress=9"
backup_dir="/Storage/backup"
backup_bases="buh unf money"
current_date=`date +"%Y-%m-%d_%H-%M"`
logfile="/var/log/postgresql/service.log"
webhook_url="https://n8n.3develop.ru/webhook/tender-security-alerts"

echo "`date +"%Y-%m-%d_%H-%M-%S"` Start backup base1c" >> ${logfile}

for base_name in ${backup_bases}
do
    # Run the backup
    if ${backup_cmd} --dbname ${base_name} --file ${backup_dir}/${base_name}-${current_date}; then
        echo "`date +"%Y-%m-%d_%H-%M-%S"` End backup "${base_name} >> ${logfile}
    else
        echo "`date +"%Y-%m-%d_%H-%M-%S"` FAILED backup "${base_name} >> ${logfile}
        # Send notification to the user via webhook
        curl -s -X POST -H "Content-Type: application/json" \
          -d "{\"text\":\"⚠️ [VPS 1C Alert] Ошибка создания бэкапа базы '${base_name}' на сервере 109.248.170.181!\"}" \
          "${webhook_url}" > /dev/null
    fi

    # Safe retention: delete backups older than 2 days, but always keep the single newest backup
    backups_count=$(find ${backup_dir} -maxdepth 1 -name "${base_name}-*" -type d | wc -l)
    if [ "${backups_count}" -gt 1 ]; then
        # Find directories older than 2 days, sort them chronologically, and delete all except the latest one
        find ${backup_dir} -maxdepth 1 -name "${base_name}-*" -type d -mtime +2 -printf '%T@ %p\n' | sort -n | cut -d' ' -f2- | head -n -1 | while read -r old_backup; do
            rm -rf -- "${old_backup}"
            echo "`date +"%Y-%m-%d_%H-%M-%S"` Removed old backup: ${old_backup}" >> ${logfile}
        done
    fi
done
