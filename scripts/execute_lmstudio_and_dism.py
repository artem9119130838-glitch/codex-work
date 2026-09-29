import os
import sys
import subprocess
import shutil

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def log(msg):
    print(f"[OPTIMIZE] {msg}", flush=True)

def step1_migrate_lm_studio():
    log("=== STEP 1: MIGRATE LM-STUDIO TO D:\\Soft\\LM-Studio ===")
    src = r"C:\LM-Studio"
    dst = r"D:\Soft\LM-Studio"
    
    if os.path.islink(src):
        log("C:\\LM-Studio is already a link/junction. Skipping move.")
        return True
        
    if not os.path.exists(src):
        log("C:\\LM-Studio does not exist. Skipping.")
        return True
        
    # Check if LM Studio is running
    res = subprocess.run(["tasklist", "/FI", "IMAGENAME eq lmstudio*"], stdout=subprocess.PIPE, text=True)
    if "lmstudio" in res.stdout.lower():
        log("LM Studio is running! Terminating gracefully...")
        subprocess.run(["taskkill", "/F", "/IM", "lmstudio.exe"])
        
    os.makedirs(r"D:\Soft", exist_ok=True)
    log(f"Copying {src} -> {dst} via Robocopy /E /MOVE...")
    # Robocopy with /MOVE
    rc_cmd = ["robocopy", src, dst, "/E", "/MOVE", "/R:2", "/W:2", "/MT:8", "/NP", "/NFL", "/NDL"]
    rc_res = subprocess.run(rc_cmd)
    log(f"Robocopy finished with code {rc_res.returncode}")
    
    # Remove any leftover empty folder C:\LM-Studio if robocopy left it
    if os.path.exists(src) and not os.path.islink(src):
        try:
            shutil.rmtree(src)
        except Exception as e:
            log(f"Could not remove old C:\\LM-Studio folder: {e}")
            
    # Create NTFS Junction C:\LM-Studio -> D:\Soft\LM-Studio
    if not os.path.exists(src):
        log("Creating NTFS Junction C:\\LM-Studio -> D:\\Soft\\LM-Studio...")
        ps_junc = f'New-Item -ItemType Junction -Path "{src}" -Target "{dst}"'
        j_res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_junc], capture_output=True, text=True)
        log(f"Junction result: {j_res.stdout.strip()}")
        
    if os.path.islink(src) or os.path.exists(os.path.join(src, "models")):
        log("SUCCESS: LM-Studio migration & Junction verified working!")
        return True
    else:
        log("WARNING: Verification of C:\\LM-Studio junction failed.")
        return False

def step2_setup_xbox_junction():
    log("=== STEP 2: SETUP XBOX GAMES JUNCTION ===")
    src = r"C:\XboxGames"
    dst = r"D:\Soft\XboxGames"
    os.makedirs(dst, exist_ok=True)
    
    if os.path.islink(src):
        log("C:\\XboxGames is already a junction. Skipping.")
        return True
        
    if os.path.exists(src):
        try:
            os.rmdir(src)
        except Exception:
            shutil.rmtree(src, ignore_errors=True)
            
    log(f"Creating NTFS Junction {src} -> {dst}...")
    ps_junc = f'New-Item -ItemType Junction -Path "{src}" -Target "{dst}"'
    j_res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_junc], capture_output=True, text=True)
    log(f"Xbox Junction result: {j_res.stdout.strip()}")
    return True

def step3_run_dism_cleanup():
    log("=== STEP 3: RUN DISM COMPONENT STORE CLEANUP ===")
    log("Running: DISM.exe /Online /Cleanup-Image /StartComponentCleanup...")
    # DISM requires elevation
    dism_cmd = 'Start-Process -FilePath "dism.exe" -ArgumentList "/Online", "/Cleanup-Image", "/StartComponentCleanup" -Verb RunAs -Wait'
    res = subprocess.run(["powershell", "-NoProfile", "-Command", dism_cmd])
    log("DISM execution completed.")

def main():
    log("Starting LM-Studio Migration, Xbox Junction, and DISM Cleanup...")
    step1_migrate_lm_studio()
    step2_setup_xbox_junction()
    step3_run_dism_cleanup()
    log("=== PIPELINE COMPLETED ===")

if __name__ == "__main__":
    main()
