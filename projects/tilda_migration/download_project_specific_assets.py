import os
import requests
from tilda_session import get_session
import ftplib

BASE_DIR = "C:/Codex_Personal/projects/tilda_migration"
THEME_DIR = os.path.join(BASE_DIR, "qilin-theme")
INDEX_PHP = os.path.join(THEME_DIR, "index.php")

# FTP Config
host = "185.26.122.79"
user = "host1847090_qilinftp"
password = "qilin_ftp"

def download_and_update():
    session = get_session()
    
    # 1. Download project-specific style and js
    project_id = "8151446"
    style_url = f"https://tilda.ru/projects/style/?projectid={project_id}"
    js_url = f"https://tilda.ru/projects/js/?projectid={project_id}"
    
    local_style_path = os.path.join(THEME_DIR, "assets", "css", "project-style.css")
    local_js_path = os.path.join(THEME_DIR, "assets", "js", "project-scripts.js")
    
    print(f"Downloading project CSS from {style_url}...")
    r_style = session.get(style_url)
    print("CSS Status:", r_style.status_code)
    if r_style.status_code == 200:
        with open(local_style_path, "w", encoding="utf-8") as f:
            f.write(r_style.text)
        print("Saved CSS to assets/css/project-style.css")
    else:
        print("FAILED to download project CSS. Body:", r_style.text[:200])
        
    print(f"Downloading project JS from {js_url}...")
    r_js = session.get(js_url)
    print("JS Status:", r_js.status_code)
    if r_js.status_code == 200:
        with open(local_js_path, "w", encoding="utf-8") as f:
            f.write(r_js.text)
        print("Saved JS to assets/js/project-scripts.js")
    else:
        print("FAILED to download project JS. Body:", r_js.text[:200])
        
    # 2. Update index.php
    print("Updating index.php to use localized CSS/JS...")
    with open(INDEX_PHP, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replacements
    # Tilda preview links might be relative or absolute (with and without domains)
    replacements = [
        ("/projects/style/?projectid=8151446", "assets/css/project-style.css"),
        ("/projects/style/?projectid=8151446", "assets/css/project-style.css"),
        ("/projects/js/?projectid=8151446", "assets/js/project-scripts.js"),
        # Try with quotes and spaces just in case
        ("href=\"/projects/style/?projectid=8151446\"", "href=\"<?php echo get_template_directory_uri(); ?>/assets/css/project-style.css\""),
        ("src=\"/projects/js/?projectid=8151446\"", "src=\"<?php echo get_template_directory_uri(); ?>/assets/js/project-scripts.js\""),
    ]
    
    # Let's use clean replace for the strings
    # We will replace any match of the URL pattern
    content = content.replace("/projects/style/?projectid=8151446", "<?php echo get_template_directory_uri(); ?>/assets/css/project-style.css")
    content = content.replace("/projects/js/?projectid=8151446", "<?php echo get_template_directory_uri(); ?>/assets/js/project-scripts.js")
    
    # Also clean up any possible double <?php echo get_template_directory_uri(); ?>
    content = content.replace("<?php echo get_template_directory_uri(); ?><?php echo get_template_directory_uri(); ?>", "<?php echo get_template_directory_uri(); ?>")
    
    with open(INDEX_PHP, "w", encoding="utf-8") as f:
        f.write(content)
    print("index.php updated.")
    
    # 3. Upload files to FTP
    print("Uploading updated files to Hostland FTP...")
    ftp = ftplib.FTP()
    ftp.connect(host)
    ftp.login(user, password)
    
    # Upload CSS
    remote_css = "htdocs/www/wp-content/themes/qilin-theme/assets/css/project-style.css"
    with open(local_style_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_css}", f)
    print("Uploaded CSS to FTP.")
    
    # Upload JS
    remote_js = "htdocs/www/wp-content/themes/qilin-theme/assets/js/project-scripts.js"
    with open(local_js_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_js}", f)
    print("Uploaded JS to FTP.")
    
    # Upload index.php
    remote_index = "htdocs/www/wp-content/themes/qilin-theme/index.php"
    with open(INDEX_PHP, "rb") as f:
        ftp.storbinary(f"STOR {remote_index}", f)
    print("Uploaded index.php to FTP.")
    
    ftp.quit()
    print("All assets uploaded and updated successfully.")

if __name__ == "__main__":
    download_and_update()
