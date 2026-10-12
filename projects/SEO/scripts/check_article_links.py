import urllib.request
import re
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = "https://longwang.ru/useful-articles/kak-kupit-oborudovanie-kitay/"
req = urllib.request.Request(url, headers=HEADERS)
html = urllib.request.urlopen(req, context=ctx, timeout=10).read().decode('utf-8', errors='ignore')

# Extract all links inside the main article content (exclude header, footer, sidebar)
print(f"=== LINKS IN ARTICLE: {url} ===")
links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)

print(f"Total links on page: {len(links)}")
content_links = []
for href, anc in links:
    clean_anc = re.sub(r'<[^>]+>', '', anc).strip()
    # Filter header/footer links
    if any(h in href for h in ['#', 'wp-content', 'tel:', 'mailto:', 'vk.com', 't.me', 'whatsapp']):
        continue
    if clean_anc in ['Главная', 'Услуги', 'О нас', 'Документы', 'Контакты', 'Блог', 'Проекты']:
        continue
    content_links.append((href, clean_anc))

print(f"Content / Contextual links ({len(content_links)}):")
for href, anc in content_links:
    print(f"  - [{anc}] -> {href}")
