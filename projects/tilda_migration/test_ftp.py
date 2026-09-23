import ftplib

hosts = [
    "ftp.hostland.ru",
    "185.26.122.79",     # IP from DNS settings screenshot
    "176.57.65.201",     # Resolved IP
    "host1847090.hostland.pro"
]

user = "host1847090_qilinftp"
password = "qilin_ftp"

for host in hosts:
    print(f"Trying FTP connection to {host}...")
    try:
        ftp = ftplib.FTP(timeout=10)
        ftp.connect(host)
        ftp.login(user, password)
        print(f"SUCCESS: Connected to {host}!")
        print("Directory list:")
        ftp.retrlines('LIST')
        ftp.quit()
        # Save working host
        with open("C:/Codex_Personal/projects/tilda_migration/ftp_host.txt", "w") as f:
            f.write(host)
        break
    except Exception as e:
        print(f"Failed to connect to {host}: {e}")
