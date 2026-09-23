import os
import sys
import json
import argparse
import subprocess

# Configuration
SSH_KEY = r"C:\Users\Артем\.ssh\id_ed25519_wlisses"
VPS_IP = "109.248.170.181"
VPS_USER = "root"

PROJECTS_SHARED_DIR = r"C:\Codex_Shared\projects"
PROJECTS_PERSONAL_DIR = r"C:\Codex_Personal\projects"
REGISTRY_JSON = r"C:\Codex_Personal\infrastructure_registry\registry.json"

vps_paths = {
    "n8n_email_ai": "/root/n8n_email_ai/.env",
    "tender-extraction-lab": "/root/tender-rag-api/.env"
}

def run_ssh_command(cmd):
    ssh_cmd = [
        "ssh",
        "-o", "ConnectTimeout=5",
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=no",
        "-i", SSH_KEY,
        f"{VPS_USER}@{VPS_IP}",
        cmd
    ]
    try:
        res = subprocess.run(ssh_cmd, capture_output=True, timeout=10)
        stdout = res.stdout.decode('utf-8', errors='ignore') if res.stdout else ""
        stderr = res.stderr.decode('utf-8', errors='ignore') if res.stderr else ""
        return res.returncode, stdout, stderr
    except Exception as e:
        return -1, "", str(e)

def replace_in_local_file(filepath, var_name, old_val, new_val, dry_run=True):
    if not os.path.exists(filepath):
        return False
    
    modified = False
    new_lines = []
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_strip = line.strip()
            if line_strip.startswith(f"{var_name}="):
                parts = line.split("=", 1)
                curr_val = parts[1].strip().strip("'").strip('"')
                if not old_val or curr_val == old_val:
                    print(f"  [Match Found] {filepath}: changing {var_name}={curr_val} to {var_name}={new_val}")
                    new_lines.append(f"{var_name}={new_val}\n")
                    modified = True
                    continue
            new_lines.append(line)
            
    if modified and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"  [Updated] Local file saved: {filepath}")
        
    return modified

def replace_in_remote_file(project, var_name, old_val, new_val, dry_run=True):
    vps_path = vps_paths.get(project)
    if not vps_path:
        return False
    
    ret, stdout, stderr = run_ssh_command(f"cat {vps_path}")
    if ret != 0:
        print(f"  [Error] Failed to read {vps_path} from VPS: {stderr}")
        return False
        
    lines = stdout.split("\n")
    modified = False
    new_lines = []
    
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith(f"{var_name}="):
            parts = line.split("=", 1)
            curr_val = parts[1].strip().strip("'").strip('"')
            if not old_val or curr_val == old_val:
                print(f"  [Match Found] VPS {vps_path}: changing {var_name}={curr_val} to {var_name}={new_val}")
                new_lines.append(f"{var_name}={new_val}")
                modified = True
                continue
        new_lines.append(line)
        
    if modified and not dry_run:
        escaped_content = "\n".join(new_lines).replace("'", "'\\''")
        write_cmd = f"echo '{escaped_content}' > {vps_path}"
        ret, stdout, stderr = run_ssh_command(write_cmd)
        if ret == 0:
            print(f"  [Updated] VPS file saved: {vps_path}")
        else:
            print(f"  [Error] Failed to write modified {vps_path} to VPS: {stderr}")
            return False
            
    return modified

def main():
    parser = argparse.ArgumentParser(description="Mass Replace variables in configurations.")
    parser.add_argument("--var", required=True, help="Environment variable name to change (e.g. LLM_API_KEY)")
    parser.add_argument("--new", required=True, help="New value for the variable")
    parser.add_argument("--old", help="Optional old value to match (only replace if matches)")
    parser.add_argument("--confirm", action="store_true", help="Confirm execution (runs in dry-run mode if missing)")
    
    args = parser.parse_args()
    
    dry_run = not args.confirm
    if dry_run:
        print("=== DRY RUN MODE: Scanning for changes (no files will be modified) ===")
    else:
        print("=== EXECUTION MODE: Applying changes ===")
        
    changes_made = False
    
    # 1. Local Replacements
    print("\nScanning local files...")
    # Scan Shared projects
    if os.path.exists(PROJECTS_SHARED_DIR):
        for proj in os.listdir(PROJECTS_SHARED_DIR):
            local_path = os.path.join(PROJECTS_SHARED_DIR, proj, ".env")
            if replace_in_local_file(local_path, args.var, args.old, args.new, dry_run):
                changes_made = True
    # Scan Personal projects
    if os.path.exists(PROJECTS_PERSONAL_DIR):
        for proj in os.listdir(PROJECTS_PERSONAL_DIR):
            local_path = os.path.join(PROJECTS_PERSONAL_DIR, proj, ".env")
            if replace_in_local_file(local_path, args.var, args.old, args.new, dry_run):
                changes_made = True
            
    # 2. VPS Replacements
    print("\nScanning remote VPS files...")
    for proj in vps_paths.keys():
        if replace_in_remote_file(proj, args.var, args.old, args.new, dry_run):
            changes_made = True
            
    if not changes_made:
        print("\nNo matching variables found to replace.")
        return
        
    if dry_run:
        print("\nScan completed. Run the command with '--confirm' to apply these changes.")
    else:
        print("\nAll changes successfully applied! Updating infrastructure registry...")
        
        try:
            scripts_dir = os.path.dirname(os.path.abspath(__file__))
            inventory_script = os.path.join(scripts_dir, "inventory.py")
            subprocess.run(["python", inventory_script], check=True)
            print("Registry updated successfully.")
        except Exception as e:
            print("Warning: Failed to update registry automatically:", e)
            
        try:
            verify_script = os.path.join(scripts_dir, "verify.py")
            if os.path.exists(verify_script):
                print("\nTriggering health checks...")
                subprocess.run(["python", verify_script], check=True)
        except Exception as e:
            print("Warning: Failed to run verification checks automatically:", e)

if __name__ == "__main__":
    main()
