import os
import sys
import shutil
import time

# UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def safe_remove_file(path):
    try:
        sz = os.path.getsize(path)
        os.remove(path)
        return sz
    except Exception:
        return 0

def safe_remove_dir(path):
    freed = 0
    try:
        for root, dirs, files in os.walk(path, topdown=False):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    freed += os.path.getsize(fp)
                    os.remove(fp)
                except Exception:
                    pass
            for d in dirs:
                dp = os.path.join(root, d)
                try:
                    os.rmdir(dp)
                except Exception:
                    pass
        try:
            os.rmdir(path)
        except Exception:
            pass
    except Exception:
        pass
    return freed

def clean_nvidia_dxcache():
    dxcache = r"C:\Users\Артем\AppData\Local\NVIDIA\DXCache"
    print("\n--- Cleaning NVIDIA DXCache ---")
    if not os.path.exists(dxcache):
        print("DXCache does not exist.")
        return 0
    freed = 0
    deleted_files = 0
    skipped_files = 0
    for root, dirs, files in os.walk(dxcache, topdown=False):
        for f in files:
            fp = os.path.join(root, f)
            sz = safe_remove_file(fp)
            if sz > 0:
                freed += sz
                deleted_files += 1
            else:
                skipped_files += 1
    print(f"DXCache: Deleted {deleted_files} files ({freed / (1024**3):.2f} GB freed), Skipped (in-use): {skipped_files}")
    return freed

def clean_user_temp():
    user_temp = r"C:\Users\Артем\AppData\Local\Temp"
    print("\n--- Cleaning User %TEMP% ---")
    if not os.path.exists(user_temp):
        print("User temp does not exist.")
        return 0
    freed = 0
    deleted_files = 0
    skipped_files = 0
    
    # 1. Specifically clean RarSFX0
    rarsfx = os.path.join(user_temp, "RarSFX0")
    if os.path.exists(rarsfx):
        sz = safe_remove_dir(rarsfx)
        freed += sz
        print(f"Removed RarSFX0: {sz / (1024**3):.2f} GB freed")

    # 2. Clean temporary files
    now = time.time()
    for item in os.scandir(user_temp):
        try:
            if item.name.startswith("bx_") and item.name.endswith(".tmp"):
                # Skip locked bitrix/tc files
                continue
            if item.is_file(follow_symlinks=False):
                # If older than 1 hour or temporary extension
                ext = os.path.splitext(item.name)[1].lower()
                if (now - item.stat().st_mtime > 3600) or ext in ['.tmp', '.log', '.progress', '.dmp']:
                    sz = safe_remove_file(item.path)
                    if sz > 0:
                        freed += sz
                        deleted_files += 1
                    else:
                        skipped_files += 1
            elif item.is_dir(follow_symlinks=False):
                if item.name in ["Tensor", "Diagnostics"] or item.name.startswith("Update-") or item.name.startswith("nsl") or item.name.startswith("nss"):
                    sz = safe_remove_dir(item.path)
                    freed += sz
                    deleted_files += 1
        except Exception:
            skipped_files += 1
            
    print(f"User Temp: Deleted {deleted_files} items ({freed / (1024**2):.2f} MB freed), Skipped (in-use): {skipped_files}")
    return freed

def main():
    print("=== SAFE EXPRESS SYSTEM CLEANER ===")
    total_freed = 0
    total_freed += clean_nvidia_dxcache()
    total_freed += clean_user_temp()
    print(f"\n[DONE] Total Space Reclaimed: {total_freed / (1024**3):.2f} GB ({total_freed / (1024**2):.2f} MB)")

if __name__ == "__main__":
    main()
