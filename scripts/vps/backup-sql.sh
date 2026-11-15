#!/bin/sh

# 1C Backup script with failure notification and STRICT SINGLE-BACKUP retention
backup_cmd="/opt/pgpro/std-14/bin/pg_dump -U postgres --format=directory --jobs=4 --compress=9"
backup_dir="/Storage/backup"
backup_bases="buh unf money"
current_date=`date +"%Y-%m-%d_%H-%M"`
logfile="/var/log/postgresql/service.log"
webhook_url="https://n8n.3develop.ru/webhook/tender-security-alerts"

echo "`date +"%Y-%m-%d_%H-%M-%S"` Start backup base1c" >> ${logfile}

for base_name in ${backup_bases}
do
    # 1. Pre-execution retention: ensure never more than 1 backup exists before starting new dump
    existing_count=$(find ${backup_dir} -maxdepth 1 -name "${base_name}-*" -type d 2>/dev/null | wc -l)
    if [ "${existing_count}" -gt 1 ]; then
        find ${backup_dir} -maxdepth 1 -name "${base_name}-*" -type d -printf '%T@ %p\n' | sort -n | cut -d' ' -f2- | head -n -1 | while read -r old_b; do
            rm -rf -- "${old_b}"
            echo "`date +"%Y-%m-%d_%H-%M-%S"` Pre-cleanup removed old backup: ${old_b}" >> ${logfile}
        done
    fi

    # 2. Run the backup
    target_dir="${backup_dir}/${base_name}-${current_date}"
    if ${backup_cmd} --dbname ${base_name} --file "${target_dir}"; then
        echo "`date +"%Y-%m-%d_%H-%M-%S"` End backup ${base_name}" >> ${logfile}

        # 3. Post-execution retention: delete previous backup, keeping STRICTLY 1 latest backup
        backups_count=$(find ${backup_dir} -maxdepth 1 -name "${base_name}-*" -type d 2>/dev/null | wc -l)
        if [ "${backups_count}" -gt 1 ]; then
            find ${backup_dir} -maxdepth 1 -name "${base_name}-*" -type d -printf '%T@ %p\n' | sort -n | cut -d' ' -f2- | head -n -1 | while read -r old_b; do
                rm -rf -- "${old_b}"
                echo "`date +"%Y-%m-%d_%H-%M-%S"` Removed previous backup (kept 1 latest): ${old_b}" >> ${logfile}
            done
        fi
    else
        echo "`date +"%Y-%m-%d_%H-%M-%S"` FAILED backup ${base_name}" >> ${logfile}
        # If failed, clean up incomplete target directory to protect disk
        rm -rf -- "${target_dir}"
        curl -s -X POST -H "Content-Type: application/json" \
          -d "{\"text\":\"⚠️ [VPS 1C Alert] Ошибка создания бэкапа базы '${base_name}' на сервере 109.248.170.181!\"}" \
          "${webhook_url}" > /dev/null
    fi
done
