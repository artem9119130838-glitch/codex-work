import ftplib

host = "185.26.122.79"
user = "host1847090_qilinftp"
password = "qilin_ftp"

try:
    ftp = ftplib.FTP()
    ftp.connect(host)
    ftp.login(user, password)
    
    print("Listing htdocs directory:")
    ftp.cwd("htdocs")
    ftp.retrlines('LIST')
    
    # Check if wp-config.php exists
    files = ftp.nlst()
    if "wp-config.php" in files:
        print("\nWordPress is installed! wp-config.php found.")
    else:
        print("\nWordPress is NOT installed in htdocs (wp-config.php not found).")
        
    ftp.quit()
except Exception as e:
    print("Error:", e)
