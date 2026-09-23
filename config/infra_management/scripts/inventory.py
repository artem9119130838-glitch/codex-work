import os
import json
import subprocess
from datetime import datetime

# Configuration
SSH_KEY = r"C:\Users\Артем\.ssh\id_ed25519_wlisses"
VPS_IP = "109.248.170.181"
VPS_USER = "root"

PROJECTS_SHARED_DIR = r"C:\Codex_Shared\projects"
PROJECTS_PERSONAL_DIR = r"C:\Codex_Personal\projects"
ROUTER_CONFIGS_DIR = r"C:\Codex_Personal\projects\server_ops\clients configs"
REGISTRY_DIR = r"C:\Codex_Personal\infrastructure_registry"
REGISTRY_JSON = os.path.join(REGISTRY_DIR, "registry.json")
REGISTRY_MD = os.path.join(REGISTRY_DIR, "INFRASTRUCTURE.md")

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

def parse_env_file(filepath):
    variables = {}
    if not os.path.exists(filepath):
        return variables
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    parts = line.split("=", 1)
                    key = parts[0].strip()
                    val = parts[1].strip().strip("'").strip('"')
                    var_type = "generic"
                    if "KEY" in key or "PASSWORD" in key or "PASS" in key or "SECRET" in key or "TOKEN" in key:
                        var_type = "sensitive"
                    variables[key] = {
                        "value": val,
                        "type": var_type
                    }
    except Exception as e:
        print(f"Error parsing env file {filepath}: {e}")
    return variables

def parse_remote_env(content):
    variables = {}
    if not content:
        return variables
    for line in content.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            parts = line.split("=", 1)
            key = parts[0].strip()
            val = parts[1].strip().strip("'").strip('"')
            var_type = "generic"
            if "KEY" in key or "PASSWORD" in key or "PASS" in key or "SECRET" in key or "TOKEN" in key:
                var_type = "sensitive"
            variables[key] = {
                "value": val,
                "type": var_type
            }
    return variables

def scan_router_configs():
    router_data = {"dns_proxy": [], "wireguard_interfaces": [], "fqdn_lists": {}}
    if not os.path.exists(ROUTER_CONFIGS_DIR):
        return router_data
    
    config_files = [f for f in os.listdir(ROUTER_CONFIGS_DIR) if f.endswith(".txt") and "router_startup" in f]
    if not config_files:
        return router_data
    
    config_files.sort()
    latest_config = os.path.join(ROUTER_CONFIGS_DIR, config_files[-1])
    router_data["source_file"] = latest_config
    
    try:
        with open(latest_config, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            
        current_fqdn_list = None
        for line in lines:
            line_strip = line.strip()
            if "xbox-dns.ru" in line_strip:
                router_data["dns_proxy"].append(line_strip)
            elif line_strip.startswith("interface Wireguard"):
                router_data["wireguard_interfaces"].append(line_strip)
            elif line_strip.startswith("object-group fqdn "):
                current_fqdn_list = line_strip.split(" ")[-1]
                router_data["fqdn_lists"][current_fqdn_list] = []
            elif current_fqdn_list:
                if line_strip.startswith("!"):
                    current_fqdn_list = None
                elif line_strip.startswith("include "):
                    domain = line_strip.replace("include ", "").strip()
                    router_data["fqdn_lists"][current_fqdn_list].append(domain)
    except Exception as e:
        print(f"Error scanning router config: {e}")
    return router_data

def generate_markdown(registry):
    md = []
    md.append("# Unified Infrastructure and Configuration Registry")
    md.append(f"\n*Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    md.append("\n## 1. VPS Infrastructure Map")
    md.append(f"* **VPS IP**: `{VPS_IP}`")
    
    md.append("\n### Running Containers on VPS")
    containers = registry.get("vps", {}).get("containers", [])
    if containers:
        md.append("| Name | Image | Status | Ports |")
        md.append("| --- | --- | --- | --- |")
        for c in containers:
            md.append(f"| {c['name']} | {c['image']} | {c['status']} | {c['ports']} |")
    else:
        md.append("No active containers found or VPS offline.")
        
    md.append("\n### VPS `/etc/hosts` Mappings")
    hosts = registry.get("vps", {}).get("hosts_mappings", [])
    if hosts:
        for ip, domain in hosts:
            md.append(f"* `{ip}` -> `{domain}`")
    else:
        md.append("No custom hosts mappings found.")
        
    md.append("\n## 2. Project Variables & Secrets")
    
    for proj, data in registry.get("projects", {}).items():
        md.append(f"\n### Project: `{proj}`")
        
        # Local env
        local_vars = data.get("local_env", {})
        if local_vars:
            md.append("\n#### Local Environment Configuration (.env)")
            md.append("| Variable Name | Type | Value (masked if secret) |")
            md.append("| --- | --- | --- |")
            for k, v in local_vars.items():
                val_display = v['value']
                if v['type'] == 'sensitive':
                    val_display = val_display[:6] + "..." if len(val_display) > 6 else "..."
                md.append(f"| `{k}` | {v['type']} | `{val_display}` |")
        
        # VPS env
        vps_vars = data.get("vps_env", {})
        if vps_vars:
            md.append("\n#### VPS Environment Configuration (.env)")
            md.append("| Variable Name | Type | Value (masked if secret) |")
            md.append("| --- | --- | --- |")
            for k, v in vps_vars.items():
                val_display = v['value']
                if v['type'] == 'sensitive':
                    val_display = val_display[:6] + "..." if len(val_display) > 6 else "..."
                md.append(f"| `{k}` | {v['type']} | `{val_display}` |")
                
    md.append("\n## 3. Router Configuration & DNS Proxy")
    r_data = registry.get("router", {})
    if r_data:
        md.append(f"\n* **Latest Config File**: `{os.path.basename(r_data.get('source_file', ''))}`")
        md.append("\n### Active DNS Proxies (DoH/DoT)")
        for proxy in r_data.get("dns_proxy", []):
            md.append(f"* `{proxy}`")
        
        md.append("\n### WireGuard Interfaces")
        for wg in r_data.get("wireguard_interfaces", []):
            md.append(f"* `{wg}`")
            
        md.append("\n### FQDN Routing Lists (Bypass Groups)")
        for group, domains in r_data.get("fqdn_lists", {}).items():
            if domains:
                md.append(f"\n**Group**: `{group}`")
                for d in domains:
                    md.append(f"* `{d}`")
                    
    # Добавляем каталог всех директорий проектов
    md.append("\n## 4. Projects Directory Catalog")
    catalogs = registry.get("project_catalogs", {})
    
    if catalogs.get("personal"):
        md.append("\n### Personal Projects (C:\\Codex_Personal\\projects)")
        for p in catalogs["personal"]:
            env_status = "Contains .env" if p in registry.get("projects", {}) and registry["projects"][p].get("source") == "personal" else "No .env"
            md.append(f"* `{p}` ({env_status})")
            
    if catalogs.get("shared"):
        md.append("\n### Shared Projects (C:\\Codex_Shared\\projects)")
        for p in catalogs["shared"]:
            env_status = "Contains .env" if p in registry.get("projects", {}) and registry["projects"][p].get("source") == "shared" else "No .env"
            md.append(f"* `{p}` ({env_status})")
            
    return "\n".join(md)

def main():
    print("Starting system infrastructure audit...")
    os.makedirs(REGISTRY_DIR, exist_ok=True)
    
    registry = {
        "last_audit_time": datetime.now().isoformat() + "Z",
        "vps": {
            "ip": VPS_IP,
            "containers": [],
            "hosts_mappings": []
        },
        "projects": {},
        "project_catalogs": {
            "shared": [],
            "personal": []
        },
        "router": {}
    }
    
    # 1. Audit VPS via SSH
    print("Auditing VPS via SSH...")
    ret, stdout, stderr = run_ssh_command("docker ps --format '{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}'")
    if ret == 0:
        for line in stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                if len(parts) >= 4:
                    registry["vps"]["containers"].append({
                        "name": parts[0],
                        "image": parts[1],
                        "status": parts[2],
                        "ports": parts[3]
                    })
    else:
        print("Failed to get Docker container status from VPS:", stderr)

    # Read VPS hosts file
    ret, stdout, stderr = run_ssh_command("cat /etc/hosts")
    if ret == 0:
        for line in stdout.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[0]
                    domain = parts[1]
                    if not ip.startswith(("127.", "::", "fe00", "ff00", "ff02")):
                        registry["vps"]["hosts_mappings"].append((ip, domain))
                        
    # 2. Audit Projects
    print("Auditing local and VPS project environments...")
    vps_paths = {
        "n8n_email_ai": "/root/n8n_email_ai/.env",
        "tender-extraction-lab": "/root/tender-rag-api/.env"
    }
    
    # Сбор каталогов проектов
    if os.path.exists(PROJECTS_SHARED_DIR):
        for name in os.listdir(PROJECTS_SHARED_DIR):
            if os.path.isdir(os.path.join(PROJECTS_SHARED_DIR, name)):
                registry["project_catalogs"]["shared"].append(name)
                
    if os.path.exists(PROJECTS_PERSONAL_DIR):
        for name in os.listdir(PROJECTS_PERSONAL_DIR):
            if os.path.isdir(os.path.join(PROJECTS_PERSONAL_DIR, name)):
                registry["project_catalogs"]["personal"].append(name)
                
    registry["project_catalogs"]["shared"].sort()
    registry["project_catalogs"]["personal"].sort()
    
    # Собираем список всех уникальных названий проектов из обеих директорий
    all_projects = set(registry["project_catalogs"]["shared"] + registry["project_catalogs"]["personal"])
    
    for proj in sorted(all_projects):
        # Ищем .env локально в Shared и в Personal
        local_shared_env = os.path.join(PROJECTS_SHARED_DIR, proj, ".env")
        local_personal_env = os.path.join(PROJECTS_PERSONAL_DIR, proj, ".env")
        
        local_env_path = None
        source_label = ""
        if os.path.exists(local_shared_env):
            local_env_path = local_shared_env
            source_label = "shared"
        elif os.path.exists(local_personal_env):
            local_env_path = local_personal_env
            source_label = "personal"
            
        # Также проверяем VPS путь
        vps_env_content = None
        if proj in vps_paths:
            ret, stdout, stderr = run_ssh_command(f"cat {vps_paths[proj]}")
            if ret == 0:
                vps_env_content = stdout
                
        # Если нашли хотя бы локальный .env или VPS .env
        if local_env_path or vps_env_content:
            registry["projects"][proj] = {
                "source": source_label,
                "local_env": {},
                "vps_env": {}
            }
            if local_env_path:
                registry["projects"][proj]["local_env"] = parse_env_file(local_env_path)
            if vps_env_content:
                registry["projects"][proj]["vps_env"] = parse_remote_env(vps_env_content)
                
    # 3. Audit Router Configuration
    print("Auditing router settings...")
    registry["router"] = scan_router_configs()
    
    # 4. Save Registry
    with open(REGISTRY_JSON, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"Registry database updated: {REGISTRY_JSON}")
    
    # 5. Generate Markdown Map
    markdown_content = generate_markdown(registry)
    with open(REGISTRY_MD, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Infrastructure Markdown map updated: {REGISTRY_MD}")
    
if __name__ == "__main__":
    main()
