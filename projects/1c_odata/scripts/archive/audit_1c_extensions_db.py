#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
audit_1c_extensions_db.py — Диагностика и бэкап расширений 1С:Предприятия в PostgreSQL (база unf на VPS).
Позволяет быстро выявлять неактивные расширения, вызывающие системные предупреждения при старте клиента,
а также снимать бинарные дампы системных записей перед их удалением.

Использование:
  py projects/1c_odata/scripts/audit_1c_extensions_db.py --list
  py projects/1c_odata/scripts/audit_1c_extensions_db.py --check-inactive
  py projects/1c_odata/scripts/audit_1c_extensions_db.py --backup Расширение_Обмен
"""

import os
import sys
import argparse
import subprocess

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SSH_HOST = "vps"
SSH_FLAGS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10"]
DB_NAME = "unf"

def run_psql(query, binary=False):
    ssh_cmd = ["ssh"] + SSH_FLAGS + [SSH_HOST, f'sudo -u postgres psql -d {DB_NAME} -c "{query}"']
    if binary:
        res = subprocess.run(ssh_cmd, capture_output=True)
        return res.stdout, res.returncode
    else:
        res = subprocess.run(ssh_cmd, capture_output=True, text=True, encoding="utf-8")
        return res.stdout, res.returncode

def list_extensions():
    print(f"[*] Получение списка расширений из базы {DB_NAME} на сервере {SSH_HOST}...")
    query = "SELECT _extensionorder AS order_no, _extname AS name, _version AS ver, _extensionusepurpose AS purpose, _updatetime AS updated FROM _extensionsinfo ORDER BY _extensionorder;"
    out, code = run_psql(query)
    if code != 0:
        print("[ERROR] Не удалось выполнить запрос к PostgreSQL")
        return
    print(out)

def check_inactive():
    print(f"[*] Проверка неактивных расширений в базе {DB_NAME}...")
    # В таблице _extensionsinfo расширения с нулевой или пустой датой обновления или флагами деактивации
    query = "SELECT _extensionorder AS order_no, _extname AS name, _version AS ver, _updatetime AS updated FROM _extensionsinfo WHERE _updatetime = '0001-01-01 00:00:00' OR _extname LIKE '%Обмен%';"
    out, code = run_psql(query)
    print(out)

def backup_extension(ext_name, output_dir=None):
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archive")
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, f"ext_backup_{ext_name}.bin")
    
    print(f"[*] Создание бинарного бэкапа записи расширения '{ext_name}' в {out_file}...")
    query = f"COPY (SELECT * FROM _extensionsinfo WHERE _extname LIKE '%{ext_name}%') TO STDOUT WITH BINARY;"
    data, code = run_psql(query, binary=True)
    if code != 0 or len(data) == 0:
        print(f"[ERROR] Не удалось выгрузить данные для '{ext_name}'. Код: {code}, байт: {len(data)}")
        return False
        
    with open(out_file, "wb") as f:
        f.write(data)
    print(f"[SUCCESS] Бэкап сохранен ({len(data)} байт): {out_file}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Аудит и бэкап расширений 1С в PostgreSQL")
    parser.add_argument("--list", action="store_true", help="Вывести список расширений")
    parser.add_argument("--check-inactive", action="store_true", help="Проверить потенциально неактивные расширения")
    parser.add_argument("--backup", type=str, help="Имя расширения для экспорта бинарного бэкапа")
    args = parser.parse_args()

    if args.list:
        list_extensions()
    elif args.check_inactive:
        check_inactive()
    elif args.backup:
        backup_extension(args.backup)
    else:
        parser.print_help()
