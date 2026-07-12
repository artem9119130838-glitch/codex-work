import os
from bs4 import BeautifulSoup
import ftplib

BASE_DIR = "C:/Codex_Personal/projects/tilda_migration"
INDEX_PHP = os.path.join(BASE_DIR, "qilin-theme", "index.php")

# FTP Config
host = "185.26.122.79"
user = "host1847090_qilinftp"
password = "qilin_ftp"

def apply_fixes():
    # 1. Modify index.php
    print("Modifying index.php...")
    with open(INDEX_PHP, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # Replace the serialize call to support <div> forms
    old_serialize = "var formData = $form.serialize();"
    new_serialize = "var formData = $form.find('input, textarea, select').serialize();"
    if old_serialize in html_content:
        html_content = html_content.replace(old_serialize, new_serialize)
        print("Replaced $form.serialize() with $form.find().serialize()")
    else:
        # Check if it was already updated or has different spacing
        print("Warning: serialize string not found in raw format, checking BeautifulSoup...")
        
    # Parse with BeautifulSoup to remove the Biohim logo column
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the footer block rec673087820
    footer_block = soup.find(id='rec673087820')
    if footer_block:
        # Find the column with class t463__logo or containing img
        logo_img = footer_block.find('img', class_='t463__logo')
        if logo_img:
            # Find the parent column of this logo
            logo_col = logo_img.find_parent(class_='t463__col')
            if logo_col:
                print("Found Biohim logo column in footer. Removing it...")
                logo_col.decompose()
            else:
                print("Found logo image but no parent column. Removing image...")
                logo_img.decompose()
        else:
            # Try to search for any img with noroot.png inside footer
            noroot_img = footer_block.find('img', src=lambda x: x and 'noroot.png' in x)
            if noroot_img:
                logo_col = noroot_img.find_parent(class_='t463__col')
                if logo_col:
                    print("Found Biohim logo column by noroot.png image. Removing it...")
                    logo_col.decompose()
                else:
                    noroot_img.decompose()
    else:
        print("Footer block rec673087820 not found.")
        
    # Overwrite
    new_html = str(soup)
    # Restore PHP tags if BS escaped them
    new_html = new_html.replace("&lt;?php", "<?php").replace("?&gt;", "?>")
    
    # Also double check serialize replacement in output html string just in case BS modified it
    if old_serialize in new_html:
        new_html = new_html.replace(old_serialize, new_serialize)
        print("Double check: replaced serialize in final output string.")
        
    with open(INDEX_PHP, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("index.php saved.")
    
    # 2. Upload to FTP
    print("Uploading updated index.php to Hostland FTP...")
    ftp = ftplib.FTP()
    ftp.connect(host)
    ftp.login(user, password)
    
    with open(INDEX_PHP, "rb") as f:
        ftp.storbinary("STOR htdocs/www/wp-content/themes/qilin-theme/index.php", f)
        
    ftp.quit()
    print("FTP upload complete. Fixes deployed successfully.")

if __name__ == "__main__":
    apply_fixes()
