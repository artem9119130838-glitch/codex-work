import os
import sys
import json
import socket
import ssl
import subprocess
import urllib.request
from datetime import datetime

# Configuration
SSH_KEY = r"C:\Users\Артем\.ssh\id_ed25519_wlisses"
VPS_IP = "109.248.170.181"
VPS_USER = "root"

REGISTRY_JSON = r"C:\Codex_Personal\infrastructure_registry\registry.json"

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

def test_dns_and_ssl(domain):
    print(f"  Testing SSL certificate for {domain}...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                expire_str = cert.get('notAfter')
                expire_dt = datetime.strptime(expire_str, '%b %d %H:%M:%S %Y %Z')
                days_left = (expire_dt - datetime.utcnow()).days
                print(f"    SSL Valid. Expires on: {expire_dt.strftime('%Y-%m-%d')} ({days_left} days left)")
                return True, f"SSL Valid ({days_left} days remaining)"
    except Exception as e:
        print(f"    SSL/DNS Check failed for {domain}: {e}")
        return False, str(e)

def test_vps_postgres():
    print("  Testing PostgreSQL (pgvector-db) on VPS...")
    ret, stdout, stderr = run_ssh_command("docker exec pgvector-db pg_isready -U vector_user -d marketing_db")
    if ret == 0:
        print("    Postgres connection test: SUCCESS")
        return True, "Running and accepting connections"
    else:
        print(f"    Postgres connection test: FAILED: {stderr.strip() or stdout.strip()}")
        return False, stdout.strip() or stderr.strip()

def test_gemini_key(key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=" + key
    payload = {
        "contents": [{"parts": [{"text": "Say OK"}]}]
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            body = json.loads(r.read().decode('utf-8'))
            if "candidates" in body:
                text = body['candidates'][0]['content']['parts'][0]['text'].strip()
                return True, f"Valid API Key (Response: {text})"
            else:
                return False, f"Unknown API Response: {body}"
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode('utf-8'))
            err_msg = err_body.get('error', {}).get('message', str(e))
            err_status = err_body.get('error', {}).get('status', '')
            if "RESOURCE_EXHAUSTED" in err_status or e.code == 429:
                return False, "Quota Exceeded (429 Resource Exhausted - limit: 0)"
            if "FAILED_PRECONDITION" in err_status and "location" in err_msg.lower():
                return False, "Geoblocked (User location is not supported)"
            return False, f"API Error: {err_msg}"
        except Exception:
            return False, f"HTTP Error {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Connection Error: {e}"

def main():
    print("=== Infrastructure Health Verification Engine ===")
    if not os.path.exists(REGISTRY_JSON):
        print(f"Error: Registry file not found at {REGISTRY_JSON}. Run inventory.py first.")
        sys.exit(1)
        
    with open(REGISTRY_JSON, "r", encoding="utf-8") as f:
        registry = json.load(f)
        
    report = []
    report.append("# Infrastructure Verification Report")
    report.append(f"Performed on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
    
    all_ok = True
    
    # 1. Test VPS SSH Connectivity
    print("Testing SSH Connection to VPS...")
    ret, stdout, stderr = run_ssh_command("echo OK")
    if ret == 0 and stdout.strip() == "OK":
        print("  VPS SSH: SUCCESS")
        report.append("- [x] **VPS SSH Connectivity**: OK")
    else:
        print("  VPS SSH: FAILED")
        report.append(f"- [ ] **VPS SSH Connectivity**: FAILED ({stderr.strip()})")
        all_ok = False
        
    # 2. Test SSL certificates for domains
    print("\nTesting SSL Certificates...")
    domains = ["n8n-eng.3develop.ru", "n8n.3develop.ru"]
    for d in domains:
        ok, msg = test_dns_and_ssl(d)
        if ok:
            report.append(f"- [x] **SSL Domain** `{d}`: {msg}")
        else:
            report.append(f"- [ ] **SSL Domain** `{d}`: FAILED ({msg})")
            all_ok = False
            
    # 3. Test Databases
    print("\nTesting Databases...")
    db_ok, db_msg = test_vps_postgres()
    if db_ok:
        report.append(f"- [x] **PostgreSQL (pgvector-db)**: {db_msg}")
    else:
        report.append(f"- [ ] **PostgreSQL (pgvector-db)**: FAILED ({db_msg})")
        all_ok = False
        
    # 4. Test API Keys from the registry
    print("\nTesting Gemini API keys...")
    checked_keys = set()
    for proj, data in registry.get("projects", {}).items():
        for env_kind in ["local_env", "vps_env"]:
            env_vars = data.get(env_kind, {})
            for var_name, var_data in env_vars.items():
                if "API_KEY" in var_name and var_data.get("value"):
                    key = var_data["value"]
                    if key.startswith("AQ.") and key not in checked_keys:
                        checked_keys.add(key)
                        print(f"  Testing Key: {key[:15]}...")
                        key_ok, key_msg = test_gemini_key(key)
                        if key_ok:
                            report.append(f"- [x] **Gemini API Key** `{key[:10]}...`: {key_msg}")
                        else:
                            report.append(f"- [ ] **Gemini API Key** `{key[:10]}...`: FAILED ({key_msg})")
                            all_ok = False

    # Save verification report
    report_md = os.path.join(os.path.dirname(REGISTRY_JSON), "VERIFICATION_REPORT.md")
    with open(report_md, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"\n=== Verification Report Saved to: {report_md} ===")
    for line in report[2:]:
        print(line)
        
    if all_ok:
        print("\nAll systems are fully operational! (ALL OK)")
    else:
        print("\nSome systems reported errors or warnings. Please check the checklist above.")

if __name__ == "__main__":
    main()
