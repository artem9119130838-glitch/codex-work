import os
import sys
from pathlib import Path
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def format_mb(b):
    return f"{b / (1024**2):.2f} MB"

def format_gb(b):
    return f"{b / (1024**3):.2f} GB"

def inspect_driveupload():
    p = r"C:\Save\.tmp.driveupload"
    print("=== 1. INSPECTION: C:\\Save\\.tmp.driveupload ===")
    if not os.path.exists(p):
        print("  Path does not exist.")
        return
    total_size = 0
    file_count = 0
    sample_files = []
    try:
        for root, dirs, files in os.walk(p):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    sz = os.path.getsize(fp)
                    total_size += sz
                    file_count += 1
                    if len(sample_files) < 10:
                        sample_files.append((f, sz))
                except Exception:
                    pass
    except Exception as e:
        print("  Error walking .tmp.driveupload:", e)
        
    print(f"  Total Size: {format_gb(total_size)} ({format_mb(total_size)}) | Files: {file_count}")
    print("  Sample files:")
    for fn, sz in sample_files:
        print(f"    {fn} ({format_mb(sz)})")

def audit_soft_e():
    base = r"C:\SOFT E"
    print("\n=== 2. DEEP AUDIT: C:\\SOFT E ===")
    if not os.path.exists(base):
        print("  Path does not exist.")
        return

    ext_stats = defaultdict(lambda: {"count": 0, "size": 0})
    top_large_files = []
    top_subdirs = defaultdict(lambda: {"count": 0, "size": 0})
    total_size = 0
    total_files = 0
    
    try:
        for entry in os.scandir(base):
            if entry.is_dir(follow_symlinks=False):
                subdir_size = 0
                subdir_count = 0
                for root, dirs, files in os.walk(entry.path):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            sz = os.path.getsize(fp)
                            subdir_size += sz
                            subdir_count += 1
                            total_size += sz
                            total_files += 1
                            ext = os.path.splitext(f)[1].lower() or "(no ext)"
                            ext_stats[ext]["count"] += 1
                            ext_stats[ext]["size"] += sz
                            top_large_files.append((fp, sz))
                        except Exception:
                            pass
                top_subdirs[entry.name]["count"] = subdir_count
                top_subdirs[entry.name]["size"] = subdir_size
            else:
                try:
                    sz = entry.stat().st_size
                    total_size += sz
                    total_files += 1
                    ext = os.path.splitext(entry.name)[1].lower() or "(no ext)"
                    ext_stats[ext]["count"] += 1
                    ext_stats[ext]["size"] += sz
                    top_large_files.append((entry.path, sz))
                except Exception:
                    pass
    except Exception as e:
        print("  Error auditing C:\\SOFT E:", e)

    print(f"  Total Size: {format_gb(total_size)} | Total Files: {total_files}")
    
    print("\n  Top Subdirectories by Size:")
    sorted_dirs = sorted(top_subdirs.items(), key=lambda x: x[1]["size"], reverse=True)
    for name, stat in sorted_dirs[:15]:
        print(f"    {name:35} | {format_gb(stat['size']):10} ({format_mb(stat['size']):10}) | {stat['count']:5} files")

    print("\n  File Types / Extensions Distribution:")
    sorted_exts = sorted(ext_stats.items(), key=lambda x: x[1]["size"], reverse=True)
    for ext, stat in sorted_exts[:15]:
        print(f"    {ext:15} | {format_gb(stat['size']):10} ({format_mb(stat['size']):10}) | {stat['count']:5} files")

    print("\n  Top 10 Largest Files in C:\\SOFT E:")
    top_large_files.sort(key=lambda x: x[1], reverse=True)
    for fp, sz in top_large_files[:10]:
        rel = os.path.relpath(fp, base)
        print(f"    {rel:50} | {format_gb(sz)}")

if __name__ == "__main__":
    inspect_driveupload()
    audit_soft_e()
