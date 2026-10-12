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

# Extract section around "Какое оборудование купить в Китае:"
m = re.search(r'Какое оборудование купить в Китае:(.*?)<h2', html, re.DOTALL | re.IGNORECASE)
if m:
    print(m.group(1)[:2000])
else:
    print("Section not found")
