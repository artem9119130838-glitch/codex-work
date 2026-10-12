import urllib.request
import re
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = "https://longwang.ru/supplies-services-china/equipment-from-china/"
req = urllib.request.Request(url, headers=HEADERS)
html = urllib.request.urlopen(req, context=ctx, timeout=10).read().decode('utf-8', errors='ignore')

print("=== EQUIPMENT HUB STRUCTURE ===")
h1_m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
print("H1:", re.sub(r'<[^>]+>', '', h1_m.group(1)).strip() if h1_m else "")

h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL | re.IGNORECASE)
print(f"\nH2 sections ({len(h2s)}):")
for h in h2s:
    print(" -", re.sub(r'<[^>]+>', '', h).strip())
    
# Find equipment cards or categories on page
links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)
cat_links = [l for l in links if 'thermo-equipment' in l[0] or 'stanki' in l[0] or 'oborudovanie' in l[0]]
print(f"\nEquipment category links on page ({len(cat_links)}):")
for h, a in cat_links[:10]:
    print(" -", re.sub(r'<[^>]+>', '', a).strip(), "->", h)
