"""
Secret Leak Scanner & Security Alert Daemon (Optimized Git Index Scanner)
Периодический и pre-flight сканер утечек конфиденциальных данных.
Оповещения:
- Bitrix24 (системный push в колокольчик и личный чат)
- Email: artem9119130828@gmail.com
- Консоль / Syslog
"""

import os
import sys
import re
import json
import urllib.request
import subprocess
from pathlib import Path

# Кодировка вывода
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPOS_TO_SCAN = [
    Path("C:/Codex/projects/n8n_email_ai"),
    Path("C:/Codex/projects/tender-extraction-lab"),
    Path("C:/Codex/projects/1c_odata"),
    Path("D:/Soft/Codex Backup"),
]

B24_WEBHOOK_URL = os.getenv("BITRIX24_WEBHOOK_URL", "https://b24-g4wfjq.bitrix24.ru/rest/1/e89gipx565rig00g").rstrip("/") + "/"
B24_USER_ID = int(os.getenv("B24_ALERT_USER_ID", "1"))
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "artem9119130828@gmail.com")

SECRET_PATTERNS = [
    (r"AIzaSy[0-9A-Za-z_-]{33}", "Google Gemini API Key"),
    (r"sk-[0-9A-Za-z]{24,}", "OpenAI / DeepSeek API Key"),
    (r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PGP)?\s?PRIVATE KEY-----", "Private SSH/PGP Key"),
    (r"https://b24-[a-z0-9]+\.bitrix24\.ru/rest/\d+/[a-z0-9]{16}/", "Bitrix24 Webhook URL with secret"),
    (r'["\'](?:pass|password)["\']\s*[:=]\s*["\'](?!(\$\{|\*|\[REDACTED|<|http)).{6,}["\']', "Plaintext Password Assignment"),
    (r'SENDER_PASS\s*=\s*["\'](?!(\$\{|\*|\[REDACTED)).+["\']', "Hardcoded Email Password"),
    (r'ONEC_PASSWORD\s*=\s*os\.getenv\([^)]+,\s*["\'](?!(\$\{|\*|\[REDACTED|"|\')).+["\']\)', "Hardcoded Fallback OData Password"),
    (r'CosiN09oAr|Artem167259|70341607Lw|saule159753|Chulpan159753|YnlByybXGR|n8n159753!|fK8qPz4wT9mXvB2yD5sR7nJ3', "Known Leaked Project Password"),
]

IGNORE_EXTENSIONS = {
    ".pyc", ".git", ".png", ".jpg", ".jpeg", ".ico", ".pdf", 
    ".zip", ".tar", ".gz", ".mxl", ".erf", ".exe", ".dll", 
    ".sqlite", ".sqlite-wal", ".sqlite-shm", ".db", ".lock",
    ".docx", ".xlsx", ".cf"
}

IGNORE_DIRS = {
    ".git", "venv", ".venv", "node_modules", "__pycache__", 
    ".idea", ".vscode", "AI Backups Victus", "scratch"
}

def is_ignored(path: Path) -> bool:
    if path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    for part in path.parts:
        if part in IGNORE_DIRS or part.startswith("unpacked"):
            return True
        if part.endswith("_backup") or part.endswith(".tmp"):
            return True
    if path.name in [".env", ".env.local", "secret_leak_scanner.py"]:
        return True
    return False

def scan_text(content: str, file_path: str) -> list:
    findings = []
    lines = content.splitlines()
    for idx, line in enumerate(lines, 1):
        if "${" in line or "[REDACTED" in line or ("os.getenv" in line and not "ONEC_PASSWORD" in line):
            if not any(k in line for k in ["CosiN09oAr", "Artem167259", "70341607Lw", "YnlByybXGR", "n8n159753!"]):
                continue
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, line):
                findings.append({
                    "file": file_path,
                    "line": idx,
                    "type": label,
                    "snippet": line.strip()[:100]
                })
    return findings

def get_repo_files(repo_path: Path) -> list:
    files = []
    if (repo_path / ".git").exists():
        try:
            # Быстро получаем список всех отслеживаемых файлов через git ls-files
            cmd = ["git", "-C", str(repo_path), "ls-files"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="ignore")
            for rel in res.stdout.splitlines():
                if rel.strip():
                    files.append(repo_path / rel.strip())
        except Exception:
            pass
    else:
        # Для не-git каталогов
        for root, dirs, fnames in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not is_ignored(Path(root) / d)]
            for fn in fnames:
                p = Path(root) / fn
                if not is_ignored(p):
                    files.append(p)
    return files

def scan_repository(repo_path: Path) -> list:
    findings = []
    if not repo_path.exists():
        return findings

    files = get_repo_files(repo_path)
    for p in files:
        if is_ignored(p):
            continue
        if p.name in [".env", ".env.local", "secret_leak_scanner.py"]:
            continue
        try:
            if p.stat().st_size > 2 * 1024 * 1024:
                continue
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            file_findings = scan_text(content, str(p))
            findings.extend(file_findings)
        except Exception:
            pass

    return findings

def send_b24_alert(findings: list):
    """Отправка мгновенного push-оповещения в Битрикс24"""
    if not B24_WEBHOOK_URL:
        return
    msg_lines = [
        "🚨 <b>[КРИТИЧЕСКИЙ АЛЕРТ БЕЗОПАСНОСТИ] Обнаружена утечка секретов!</b>",
        f"Найдено инцидентов: <b>{len(findings)}</b>",
        ""
    ]
    for item in findings[:5]:
        msg_lines.append(f"⚠️ <b>{item['type']}</b> в <code>{item['file']}:{item['line']}</code>")
        msg_lines.append(f"Строка: <code>{item['snippet']}</code>")
        msg_lines.append("")
    if len(findings) > 5:
        msg_lines.append(f"... и еще {len(findings) - 5} совпадений.")
    msg_lines.append("Коммит и пуш заблокированы до устранения!")

    payload = {
        "USER_ID": B24_USER_ID,
        "MESSAGE": "\n".join(msg_lines),
        "TYPE": "SYSTEM"
    }

    try:
        url = B24_WEBHOOK_URL + "im.notify.system.add"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                print("[ALERT SENT] Уведомление успешно доставлено в Битрикс24.")
    except Exception as e:
        print(f"[ALERT ERROR] Ошибка отправки в Битрикс24: {e}")

def send_email_alert(findings: list):
    """Отправка подробного email-оповещения на почту администратора"""
    env_file = Path("C:/Codex/projects/n8n_email_ai/.env")
    sender_email = None
    sender_pass = None
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MAIL_ACCOUNTS="):
                        val = line.split("=", 1)[1].strip().strip("'\"")
                        accs = json.loads(val)
                        sales = next((a for a in accs if a.get("user") == "sales@longwang.ru"), None)
                        if sales:
                            sender_email = sales.get("user")
                            sender_pass = sales.get("pass")
                        break
        except Exception:
            pass

    if not sender_email or not sender_pass:
        sender_email = os.getenv("ALERT_SMTP_USER")
        sender_pass = os.getenv("ALERT_SMTP_PASS")

    if not sender_email or not sender_pass:
        print("[EMAIL ALERT] Учетные данные SMTP не найдены в .env, пропуск отправки email.")
        return

    import smtplib
    import ssl
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = f"🚨 КРИТИЧЕСКИЙ АЛЕРТ: Обнаружена утечка {len(findings)} секретов в коде"
    msg["From"] = sender_email
    msg["To"] = ALERT_EMAIL

    lines = [
        f"ВНИМАНИЕ! Сканер безопасности обнаружил {len(findings)} потенциальных утечек учетных данных в Git-репозиториях:\n"
    ]
    for idx, item in enumerate(findings, 1):
        lines.append(f"{idx}. [{item['type']}] в {item['file']}:{item['line']}")
        lines.append(f"   Код: {item['snippet']}\n")

    lines.append("Все автоматические пуши и сжатия сессий заблокированы до устранения замечаний.")
    msg.set_content("\n".join(lines))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("mail.hostland.ru", 465, context=ctx, timeout=10) as s:
            s.login(sender_email, sender_pass)
            s.send_message(msg)
        print(f"[EMAIL ALERT] Письмо с алертом успешно отправлено на {ALERT_EMAIL}")
    except Exception as e:
        print(f"[EMAIL ERROR] Не удалось отправить письмо на {ALERT_EMAIL}: {e}")

def run_scan() -> list:
    all_findings = []
    print("=== Быстрое сканирование репозиториев на секреты ===")
    for repo in REPOS_TO_SCAN:
        if repo.exists():
            f = scan_repository(repo)
            if f:
                print(f"[!] {repo.name}: НАЙДЕНО {len(f)} ПОДОЗРИТЕЛЬНЫХ СТРОК!")
                all_findings.extend(f)
            else:
                print(f"[OK] {repo.name}: Чисто.")
        else:
            print(f"[-] {repo.name}: Путь не найден.")

    if all_findings:
        print(f"\n[ВНИМАНИЕ] Всего обнаружено потенциальных утечек: {len(all_findings)}")
        send_b24_alert(all_findings)
        send_email_alert(all_findings)
    else:
        print("\n[OK] Секретов не обнаружено. Все репозитории чисты.")

    return all_findings

if __name__ == "__main__":
    if "--test-alert" in sys.argv:
        print("=== ТЕСТОВАЯ ОТПРАВКА ОПОВЕЩЕНИЙ БЕЗОПАСНОСТИ ===")
        dummy = [{
            "file": "C:/Codex/test_security_alert.py",
            "line": 42,
            "type": "Test Security Alert Verification",
            "snippet": "SECRET_TEST_TOKEN = 'test_verification_token_ok'"
        }]
        send_b24_alert(dummy)
        send_email_alert(dummy)
        sys.exit(0)

    findings = run_scan()
    if findings:
        sys.exit(1)
    sys.exit(0)
