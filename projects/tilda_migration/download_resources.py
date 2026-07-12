import os
import re
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Paths
BASE_DIR = "C:/Codex_Personal/projects/tilda_migration"
HTML_FILE = os.path.join(BASE_DIR, "preview_response.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "qilin-theme")

# Subdirectories
IMG_DIR = os.path.join(OUTPUT_DIR, "assets", "img")
CSS_DIR = os.path.join(OUTPUT_DIR, "assets", "css")
JS_DIR = os.path.join(OUTPUT_DIR, "assets", "js")
FONTS_DIR = os.path.join(OUTPUT_DIR, "assets", "fonts")

# Create dirs
for d in [IMG_DIR, CSS_DIR, JS_DIR, FONTS_DIR]:
    os.makedirs(d, exist_ok=True)

def download_file(url, folder):
    if not url.startswith('http'):
        return None
    
    # Try to clean URL (remove query params)
    clean_url = url.split('?')[0]
    parsed = urlparse(clean_url)
    filename = os.path.basename(parsed.path)
    
    if not filename:
        return None
        
    local_path = os.path.join(folder, filename)
    
    # If file already exists, don't download again to save time/bandwidth
    if os.path.exists(local_path):
        return filename
        
    try:
        # print(f"Downloading {url}...")
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(r.content)
            return filename
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return None

def main():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Download CSS and JS files
    # Stylesheets
    css_files = {}
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if href:
            # We want only Tilda CDN or relative stylesheets, not google fonts
            if "tildacdn" in href or href.startswith('/'):
                full_url = urljoin("https://tilda.ru", href)
                filename = download_file(full_url, CSS_DIR)
                if filename:
                    css_files[href] = f"assets/css/{filename}"
                    
    # Javascripts
    js_files = {}
    for script in soup.find_all('script'):
        src = script.get('src')
        if src:
            if "tildacdn" in src or src.startswith('/'):
                full_url = urljoin("https://tilda.ru", src)
                filename = download_file(full_url, JS_DIR)
                if filename:
                    js_files[src] = f"assets/js/{filename}"

    # 2. Download Images
    img_files = {}
    
    # Standard <img> tags
    for img in soup.find_all('img'):
        src = img.get('src')
        original = img.get('data-original')
        
        for url in [src, original]:
            if url and ("tildacdn" in url or url.startswith('/') or "dropbox" in url):
                full_url = urljoin("https://tilda.ru", url)
                filename = download_file(full_url, IMG_DIR)
                if filename:
                    img_files[url] = f"assets/img/{filename}"

    # Background images in styles
    style_tags = soup.find_all(style=True)
    for tag in style_tags:
        style_str = tag.get('style')
        urls = re.findall(r'url\([\'"]?([^\'"\)]+)[\'"]?\)', style_str)
        for url in urls:
            if "tildacdn" in url or url.startswith('/') or "dropbox" in url:
                full_url = urljoin("https://tilda.ru", url)
                filename = download_file(full_url, IMG_DIR)
                if filename:
                    img_files[url] = f"assets/img/{filename}"
                    
    # Also find background images inside <style> tags
    styles = soup.find_all('style')
    for style in styles:
        urls = re.findall(r'url\([\'"]?([^\'"\)]+)[\'"]?\)', style.text)
        for url in urls:
            if "tildacdn" in url or url.startswith('/'):
                full_url = urljoin("https://tilda.ru", url)
                filename = download_file(full_url, IMG_DIR)
                if filename:
                    img_files[url] = f"assets/img/{filename}"

    # Link icons/favicons
    for link in soup.find_all('link', rel=re.compile(r'icon|apple-touch-icon')):
        href = link.get('href')
        if href:
            full_url = urljoin("https://tilda.ru", href)
            filename = download_file(full_url, IMG_DIR)
            if filename:
                img_files[href] = f"assets/img/{filename}"

    print(f"Downloaded: {len(css_files)} CSS files, {len(js_files)} JS files, {len(img_files)} images.")

    # Save mapping for replacement phase
    mapping = {
        'css': css_files,
        'js': js_files,
        'img': img_files
    }
    with open(os.path.join(BASE_DIR, "resource_mapping.json"), "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
    print("Saved resource_mapping.json")

if __name__ == "__main__":
    main()
