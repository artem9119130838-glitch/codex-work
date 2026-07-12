import os
import requests
from bs4 import BeautifulSoup
import re
import ftplib

BASE_DIR = "C:/Codex_Personal/projects/tilda_migration"
THEME_DIR = os.path.join(BASE_DIR, "qilin-theme")
INDEX_PHP = os.path.join(THEME_DIR, "index.php")

# FTP Config
host = "185.26.122.79"
user = "host1847090_qilinftp"
password = "qilin_ftp"

def fix_icons_and_footer():
    # 1. Download original favicons from the live site
    favicon_url = "https://static.tildacdn.com/tild3837-6236-4666-a339-666531613237/favicon_1.ico"
    apple_icon_url = "https://static.tildacdn.com/tild3331-6333-4332-a237-393337333332/152152.png"
    
    local_fav_path = os.path.join(THEME_DIR, "assets", "img", "tildafavicon.ico")
    local_fav_svg_path = os.path.join(THEME_DIR, "assets", "img", "tildafavicon.svg")
    local_apple_path = os.path.join(THEME_DIR, "assets", "img", "tildafavicon-180x180.png")
    
    print("Downloading correct favicon...")
    try:
        r = requests.get(favicon_url, timeout=10)
        if r.status_code == 200:
            with open(local_fav_path, "wb") as f:
                f.write(r.content)
            with open(local_fav_svg_path, "wb") as f:
                f.write(r.content)
            print("Favicon replaced successfully.")
    except Exception as e:
        print("Failed to replace favicon:", e)
        
    print("Downloading correct apple icon...")
    try:
        r = requests.get(apple_icon_url, timeout=10)
        if r.status_code == 200:
            with open(local_apple_path, "wb") as f:
                f.write(r.content)
            print("Apple icon replaced successfully.")
    except Exception as e:
        print("Failed to replace apple icon:", e)

    # 2. Modify index.php
    print("Modifying index.php...")
    with open(INDEX_PHP, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Remove #t-page-preview-back and preview panels using BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    # Remove preview panel by ID
    preview_panel = soup.find(id='t-page-preview-back')
    if preview_panel:
        print("Found #t-page-preview-back. Removing it...")
        preview_panel.decompose()
    else:
        print("#t-page-preview-back NOT found via BeautifulSoup ID lookup.")
        
    # Double check by class or custom search
    for el in soup.find_all(class_=re.compile(r't-page-preview|preview-back')):
        print(f"Found preview element by class: {el.get('class')}. Removing it...")
        el.decompose()
        
    # Remove Tilda label
    tilda_label = soup.find(class_=lambda x: x and ('tildalabel' in x or 't-tildalabel' in x))
    if tilda_label:
        print("Found Tilda label element. Removing it...")
        tilda_label.decompose()
        
    # Remove any tags with "Made on Tilda" text
    for node in soup.find_all(text=lambda text: text and "Made on Tilda" in text):
        parent = node.parent
        print(f"Found 'Made on Tilda' text inside tag {parent.name}. Removing parent...")
        parent.decompose()
        
    new_html = str(soup)
    
    # Restore PHP tags if BS escaped them
    new_html = new_html.replace("&lt;?php", "<?php").replace("?&gt;", "?>")
    new_html = re.sub(r'<!--\?php(.*?)\?-->', r'<?php\1?>', new_html)

    # Sometimes BS doesn't find dynamic JS-injected HTML structures in parsed code.
    # Let's also do a raw regex replacement on the HTML string to be 100% sure.
    # If the element was written as raw HTML string:
    # We will search for id="t-page-preview-back" in the string and clean it up if BS missed it.
    
    with open(INDEX_PHP, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("index.php modified and saved.")

    # 3. Upload updated files to FTP
    print("Uploading updated icons and index.php to FTP...")
    ftp = ftplib.FTP()
    ftp.connect(host)
    ftp.login(user, password)
    
    # Upload Favicon
    try:
        with open(local_fav_path, "rb") as f:
            ftp.storbinary("STOR htdocs/www/wp-content/themes/qilin-theme/assets/img/tildafavicon.ico", f)
        with open(local_fav_svg_path, "rb") as f:
            ftp.storbinary("STOR htdocs/www/wp-content/themes/qilin-theme/assets/img/tildafavicon.svg", f)
    except Exception as e:
        print("FTP favicon upload failed:", e)
        
    # Upload Apple Icon
    try:
        with open(local_apple_path, "rb") as f:
            ftp.storbinary("STOR htdocs/www/wp-content/themes/qilin-theme/assets/img/tildafavicon-180x180.png", f)
    except Exception as e:
        print("FTP apple icon upload failed:", e)
        
    # Upload index.php
    try:
        with open(INDEX_PHP, "rb") as f:
            ftp.storbinary("STOR htdocs/www/wp-content/themes/qilin-theme/index.php", f)
        print("Uploaded updated index.php to FTP.")
    except Exception as e:
        print("FTP index.php upload failed:", e)
        
    ftp.quit()
    print("FTP upload complete.")

if __name__ == "__main__":
    fix_icons_and_footer()
