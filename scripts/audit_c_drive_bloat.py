import os
import sys
import subprocess
from pathlib import Path

# UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def get_size(path):
    total = 0
    file_count = 0
    try:
        if os.path.islink(path):
            return 0, 0
        for entry in os.scandir(path):
            if entry.is_symlink():
                continue
            if entry.is_dir(follow_symlinks=False):
                try:
                    for root, dirs, files in os.walk(entry.path):
                        for f in files:
                            try:
                                fp = os.path.join(root, f)
                                if not os.path.islink(fp):
                                    total += os.path.getsize(fp)
                                    file_count += 1
                            except Exception:
                                pass
                except Exception:
                    pass
            else:
                try:
                    total += entry.stat().st_size
                    file_count += 1
                except Exception:
                    pass
    except Exception as e:
        return 0, 0
    return total, file_count

def format_gb(bytes_val):
    return f"{bytes_val / (1024**3):.2f} GB"

def format_mb(bytes_val):
    return f"{bytes_val / (1024**2):.2f} MB"

def main():
    print("=== C DRIVE BLOAT & AUDIT DIAGNOSTIC ===")
    
    # 1. Check codex_home status
    codex_home = r"C:\codex_home"
    print(f"\n1. STATUS: {codex_home}")
    if os.path.exists(codex_home):
        ch_size, ch_files = get_size(codex_home)
        print(f"  Exists: True | Size: {format_mb(ch_size)} | Files: {ch_files}")
        for root, dirs, files in os.walk(codex_home):
            for f in files:
                p = os.path.join(root, f)
                print(f"    File: {p}")
    else:
        print("  Exists: False (Already deleted)")

    # 2. Check candidate folders to move: LM-Studio, XboxGames, Save, SOFT E, Torrents_Downloads
    candidate_folders = [
        r"C:\LM-Studio",
        r"C:\XboxGames",
        r"C:\Save",
        r"C:\SOFT E",
        r"C:\Torrents_Downloads",
        r"C:\SWSETUP"
    ]
    print("\n2. CANDIDATE LARGE FOLDERS ON C:\\")
    for f in candidate_folders:
        if os.path.exists(f):
            is_link = os.path.islink(f)
            sz, count = get_size(f)
            print(f"  {f:25} | Size: {format_gb(sz):10} ({format_mb(sz):10}) | Files: {count:6} | IsLink: {is_link}")
        else:
            print(f"  {f:25} | DOES NOT EXIST")

    # 3. Check AppData Temp and NVIDIA folders
    print("\n3. APPDATA TEMP & NVIDIA BLOAT")
    nvidia_paths = [
        r"C:\Users\Артем\AppData\Local\Temp",
        r"C:\Users\Артем\AppData\Local\NVIDIA",
        r"C:\Users\Артем\AppData\Local\NVIDIA Corporation",
        r"C:\ProgramData\NVIDIA",
        r"C:\ProgramData\NVIDIA Corporation",
        r"C:\ProgramData\NVIDIA Corporation\Downloader"
    ]
    for np in nvidia_paths:
        if os.path.exists(np):
            sz, count = get_size(np)
            print(f"  {np:45} | Size: {format_gb(sz):10} ({format_mb(sz):10}) | Files: {count:6}")
        else:
            print(f"  {np:45} | Not found")

    # 4. Check Windows bloat items
    print("\n4. WINDOWS DIRECTORY COMPONENTS")
    win_components = [
        r"C:\Windows\WinSxS",
        r"C:\Windows\SoftwareDistribution\Download",
        r"C:\Windows\Temp",
        r"C:\Windows\Installer",
        r"C:\Windows\Logs",
        r"C:\Windows\System32\SleepStudy",
        r"C:\Windows\MEMORY.DMP",
        r"C:\Windows\Minidump",
        r"C:\hiberfil.sys",
        r"C:\pagefile.sys",
        r"C:\swapfile.sys"
    ]
    for wc in win_components:
        if os.path.isfile(wc):
            try:
                sz = os.path.getsize(wc)
                print(f"  {wc:45} | File Size: {format_gb(sz):10} ({format_mb(sz):10})")
            except Exception as e:
                print(f"  {wc:45} | Error getting size: {e}")
        elif os.path.isdir(wc):
            sz, count = get_size(wc)
            print(f"  {wc:45} | Dir Size:  {format_gb(sz):10} ({format_mb(sz):10}) | Files: {count:6}")
        else:
            print(f"  {wc:45} | Not found")

    # 5. Check Disk Free Space
    print("\n5. DRIVE VOLUMES FREE SPACE")
    try:
        ps_cmd = 'Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N="FreeGB";E={[math]::Round($_.Free/1GB,2)}}, @{N="UsedGB";E={[math]::Round($_.Used/1GB,2)}}, @{N="TotalGB";E={[math]::Round(($_.Free+$_.Used)/1GB,2)}} | Format-Table -AutoSize'
        res = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps_cmd], text=True)
        print(res.strip())
    except Exception as e:
        print("Error checking volume sizes:", e)

if __name__ == "__main__":
    main()
