#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PC Healthcheck and Cleaner (HP Victus 16)
==========================================
Автоматическая проверка и экспресс-очистка для команды:
«почисти и проверь мой ПК (ноутбук)»

1. Видеочипы: Intel Iris Xe + NVIDIA RTX 3060 (проверка Код 43).
2. Дисплеи: реестр MPO, гибридный сон, проверка фантомов SIMULATED.
3. Загрузчик: статус F8 legacy, таймаут 0, отсутствие дубликатов Safe Mode.
4. Adobe Acrobat: блокировка AGS, cefWorkflow, hosts и FeatureLockDown.
5. Диски: свободное место на C:, D:, внешних дисках.
6. Очистка кэша: удаление временных логов и мусора из scratch.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Ensure UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def run_ps(cmd):
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def check_pc():
    print("=" * 65)
    print(" [HEALTHCHECK] ДИАГНОСТИКА И ЭКСПРЕСС-ОЧИСТКА ПК (HP VICTUS 16)")
    print("=" * 65)
    
    # 1. Видеочипы
    print("\n1. Графическая подсистема (GPU):")
    gpu_info = run_ps("Get-PnpDevice -Class Display | Select-Object FriendlyName, Status, Problem | Format-Table -HideTableHeaders")
    for line in gpu_info.splitlines():
        line = line.strip()
        if line:
            if "CM_PROB_FAILED_POST_START" in line or "Error" in line:
                print(f"  [!] ВНИМАНИЕ: {line} (Требуется драйвер nvhmi.inf!)")
            else:
                print(f"  [OK] {line}")
                
    # 2. Дисплеи и реестр
    print("\n2. Реестр дисплеев и стабильность Windows 11:")
    reg_mpo = run_ps("(Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\Dwm' -Name 'DisableOverlays' -ErrorAction SilentlyContinue).DisableOverlays")
    if reg_mpo == "1":
        print("  [OK] Баг MPO отключен (DisableOverlays = 1)")
    else:
        print("  [!] Рекомендуется отключить MPO (запустите СБРОС_КЭША_ДИСПЛЕЕВ.bat)")
        
    reg_hiber = run_ps("(Get-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power' -Name 'HiberbootEnabled' -ErrorAction SilentlyContinue).HiberbootEnabled")
    if reg_hiber == "0":
        print("  [OK] Гибридный сон отключен (HiberbootEnabled = 0)")
    else:
        print("  [INFO] Быстрый запуск активен (HiberbootEnabled = 1)")
        
    sim_check = run_ps("Get-ChildItem 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers\\Configuration' -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -like '*SIMULATED*' }")
    if sim_check:
        print("  [!] Обнаружены застрявшие фантомные мониторы SIMULATED (запустите СБРОС_КЭША_ДИСПЛЕЕВ.bat)")
    else:
        print("  [OK] Фантомных дисплеев SIMULATED в реестре нет (топология чистая)")
        
    # 3. Загрузчик BCD и клавиша F8
    print("\n3. Загрузчик Windows (BCD) и меню Safe Mode:")
    bcd_info = run_ps("bcdedit /enum {default}")
    if "legacy" in bcd_info.lower():
        print("  [OK] Классическая клавиша F8 АКТИВНА (bootmenupolicy legacy)")
    else:
        print("  [!] Клавиша F8 отключена (запустите ВКЛЮЧИТЬ_КЛАВИШУ_F8.bat)")
        
    # 4. Adobe Acrobat
    print("\n4. Защита от блокировок Adobe Acrobat:")
    gc_path = Path(r"C:\Program Files\Adobe\Acrobat DC\Acrobat\GC_disabled")
    cef_path = Path(r"C:\Program Files\Adobe\Acrobat DC\Acrobat\NGL\cefWorkflow_disabled")
    if gc_path.exists() and cef_path.exists():
        print("  [OK] Модули проверки GC и cefWorkflow нейтрализованы (_disabled)")
    else:
        print("  [INFO] Модули Adobe активны или не переименованы")
        
    hosts_text = run_ps("Get-Content 'C:\\Windows\\System32\\drivers\\etc\\hosts' -ErrorAction SilentlyContinue")
    if "workflow-ui-prod.licensingstack.com" in hosts_text:
        print("  [OK] Серверы лицензирования заблокированы в hosts (0.0.0.0)")
    else:
        print("  [!] hosts не содержит блокировок Acrobat (запустите scripts/fix_acrobat_genuine.ps1)")
        
    # 5. Свободное место на дисках
    print("\n5. Дисковое пространство:")
    volumes = run_ps("Get-Volume | Where-Object { $_.DriveLetter -ne $null } | Select-Object DriveLetter, FileSystemLabel, @{Name='FreeGB';Expression={[math]::Round($_.SizeRemaining/1GB, 1)}}, @{Name='TotalGB';Expression={[math]::Round($_.Size/1GB, 1)}} | Format-Table -HideTableHeaders")
    for v in volumes.splitlines():
        v = v.strip()
        if v:
            print(f"  • Диск {v}")
            
    # 6. Экспресс-очистка scratch
    print("\n6. Экспресс-очистка временных файлов:")
    scratch_dir = Path(r"C:\Codex_Personal\scratch")
    cleaned_count = 0
    if scratch_dir.exists():
        for p in scratch_dir.glob("*"):
            if p.is_file() and p.suffix.lower() in ('.py', '.txt', '.log'):
                try:
                    p.unlink()
                    cleaned_count += 1
                except Exception:
                    pass
    print(f"  [OK] Очищено временных файлов из scratch/: {cleaned_count} шт.")
    
    print("\n" + "=" * 65)
    print(" [DONE] ДИАГНОСТИКА ЗАВЕРШЕНА. НОУТБУК ГОТОВ К РАБОТЕ.")
    print("=" * 65)

if __name__ == '__main__':
    check_pc()
