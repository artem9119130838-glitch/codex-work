import urllib.request
import re
import ssl
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

url = 'https://longwang.ru/supplies-services-china/equipment-from-china/thermo-equipment-china/'
req = urllib.request.Request(url, headers=HEADERS)

try:
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Status: {resp.status}, HTML length: {len(html)}")
        
        # Check JSON-LD
        json_lds = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
        print(f"Total JSON-LD blocks: {len(json_lds)}")
        faqpage_found = False
        for i, raw_j in enumerate(json_lds):
            if 'FAQPage' in raw_j:
                faqpage_found = True
                print(f"  [+] НАЙДЕН FAQPage в блоке #{i+1}!")
                try:
                    d = json.loads(raw_j.strip())
                    print(json.dumps(d, ensure_ascii=False, indent=2)[:600])
                except:
                    print(raw_j[:400])
        if not faqpage_found:
            print("  [-] FAQPage в JSON-LD НЕ НАЙДЕН!")
            
        # Check visible FAQ
        faq_headings = re.findall(r'<h[2-4][^>]*>(.*?)</h[2-4]>', html, re.DOTALL | re.IGNORECASE)
        found_faq_heading = False
        for h in faq_headings:
            clean_h = re.sub(r'<[^>]+>', '', h).strip()
            if any(w in clean_h.lower() for w in ['faq', 'вопрос', 'часто']):
                found_faq_heading = True
                print(f"  [+] Найден визуальный заголовок FAQ: \"{clean_h}\"")
        if not found_faq_heading:
            print("  [-] Визуальный заголовок FAQ не найден среди H2-H4!")
except Exception as e:
    print(f"Error fetching {url}: {e}")
