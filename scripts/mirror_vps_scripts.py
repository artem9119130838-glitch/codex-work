#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/mirror_vps_scripts.py
Скрипт односессионного опроса и зеркалирования боевых скриптов с VPS в scripts/vps/:
- Опрашивает хост 109.248.170.181 за 1 SSH-сессию (Anti-Ban & Token Economy).
- Скачивает боевые скрипты из /Storage/, /root/, /usr/local/bin/, cron.
- Сохраняет crontab в scripts/vps/vps_crontab.cron.
- Создает манифест боевых скриптов VPS (scripts/vps/VPS_SCRIPTS_MANIFEST.md).
"""

import os
import sys
from pathlib import Path
import paramiko

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HOST = "109.248.170.181"
USER = "root"
KEY_PATH = Path.home() / ".ssh" / "id_ed25519_wlisses"
LOCAL_VPS_DIR = Path(r"C:\Codex_Personal\scripts\vps")
LOCAL_VPS_DIR.mkdir(parents=True, exist_ok=True)

REMOTE_FILES = [
    ("/Storage/run_server_backup.sh", "run_server_backup.sh", "Еженедельный полный бэкап VPS, дампы БД и SQLite maintenance"),
    ("/Storage/backup-sql.sh", "backup-sql.sh", "Ежедневный дамп баз данных PostgreSQL / MySQL"),
    ("/Storage/monitor_disk.sh", "monitor_disk.sh", "Мониторинг дискового пространства VPS с алертом в Битрикс24"),
    ("/Storage/restore_postgre.sh", "restore_postgre.sh", "Восстановление PostgreSQL из резервной копии"),
    ("/Storage/scripts/b24_daily_analytics_sync.py", "b24_daily_analytics_sync.py", "Ежедневная синхронизация аналитики Битрикс24 в БД"),
    ("/root/clear_tmp.sh", "clear_tmp.sh", "Очистка временных файлов и кэша"),
    ("/root/vps_server_backup.sh", "vps_server_backup.sh", "Скрипт бэкапа n8n и pg_dump"),
    ("/root/tender-rag-api/scripts/auto_deploy.sh", "auto_deploy.sh", "Автодеплой tender-rag-api по крону"),
    ("/usr/local/bin/deploy-tender.sh", "deploy-tender.sh", "Скрипт деплоя тендерного сервиса без удаления сети"),
    ("/usr/local/bin/n8n-sqlite-auto-vacuum.sh", "n8n-sqlite-auto-vacuum.sh", "Сжатие и очистка SQLite баз данных n8n без WAL"),
]

def mirror_scripts():
    print(f"Подключение к VPS {USER}@{HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    downloaded = []
    try:
        pkey = paramiko.Ed25519Key.from_private_key_file(str(KEY_PATH))
        client.connect(hostname=HOST, username=USER, pkey=pkey, timeout=12)
        print("SSH-соединение успешно установлено (1 сессия).")
        
        # 1. Получаем crontab
        stdin, stdout, stderr = client.exec_command("crontab -l 2>/dev/null")
        cron_text = stdout.read().decode('utf-8', errors='replace')
        cron_path = LOCAL_VPS_DIR / "vps_crontab.cron"
        cron_path.write_text(cron_text, encoding='utf-8')
        print(f"Crontab сохранен в {cron_path}")
        
        # 2. SFTP скачивание файлов
        sftp = client.open_sftp()
        for remote_p, local_name, desc in REMOTE_FILES:
            target_p = LOCAL_VPS_DIR / local_name
            try:
                # Проверим атрибуты на сервере
                attrs = sftp.stat(remote_p)
                sftp.get(remote_p, str(target_p))
                mode_oct = oct(attrs.st_mode)[-3:] if attrs.st_mode else "644"
                downloaded.append({
                    "remote_path": remote_p,
                    "local_name": local_name,
                    "local_path": str(target_p),
                    "size_bytes": attrs.st_size,
                    "mode": mode_oct,
                    "desc": desc
                })
                print(f"  [OK] {remote_p} -> {local_name} ({attrs.st_size} bytes)")
            except Exception as e:
                print(f"  [SKIP] {remote_p}: {e}")
        sftp.close()
        
    finally:
        client.close()
        print("SSH-соединение закрыто.")

    # 3. Формируем манифест в scripts/vps/VPS_SCRIPTS_MANIFEST.md
    manifest_lines = [
        "# Манифест боевых скриптов VPS (109.248.170.181)",
        "",
        "> Автоматически синхронизировано из боевого контура за 1 сессию SSH.",
        f"> Всего выгружено скриптов: {len(downloaded)} + crontab.",
        "",
        "## Реестр зеркалированных скриптов",
        "",
        "| Имя файла | Путь на VPS | Права | Размер | Назначение / Триггер |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    for it in downloaded:
        manifest_lines.append(f"| `{it['local_name']}` | `{it['remote_path']}` | `{it['mode']}` | {it['size_bytes']} B | {it['desc']} |")
        
    manifest_lines.extend([
        "",
        "## Активное расписание Crontab на VPS",
        "```cron",
        cron_text.strip(),
        "```",
        ""
    ])
    
    manifest_path = LOCAL_VPS_DIR / "VPS_SCRIPTS_MANIFEST.md"
    manifest_path.write_text("\n".join(manifest_lines), encoding='utf-8')
    print(f"Манифест успешно записан: {manifest_path}")
    return downloaded

if __name__ == "__main__":
    mirror_scripts()
