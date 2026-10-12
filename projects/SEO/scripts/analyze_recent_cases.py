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

def analyze_case(url):
    print(f"\n==========================================")
    print(f"CASE URL: {url}")
    req = urllib.request.Request(url, headers=HEADERS)
    html = urllib.request.urlopen(req, context=ctx, timeout=10).read().decode('utf-8', errors='ignore')
    
    # Title & H1
    title_m = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    print("TITLE:", title_m.group(1).strip() if title_m else "")
    h1_m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    print("H1:", re.sub(r'<[^>]+>', '', h1_m.group(1)).strip() if h1_m else "")
    
    # Meta description
    desc_m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    print("DESCRIPTION:", desc_m.group(1).strip() if desc_m else "НЕТ")
    
    # Headings
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL | re.IGNORECASE)
    print(f"H2 headings ({len(h2s)}):", [re.sub(r'<[^>]+>', '', x).strip() for x in h2s[:5]])
    
    # Schema.org
    json_lds = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
    types = []
    for j in json_lds:
        try:
            d = json.loads(j)
            if isinstance(d, dict):
                types.append(d.get('@type', ''))
                if '@graph' in d:
                    types.extend([item.get('@type', '') for item in d['@graph']])
        except:
            pass
    print("Schema.org Types:", types)
    
    # Word count estimation in body
    text = re.sub(r'<[^>]+>', ' ', html)
    words = [w for w in text.split() if len(w) > 2]
    print(f"Approx words in page: {len(words)}")

analyze_case("https://longwang.ru/projects/leasing-equipment-china/")
analyze_case("https://longwang.ru/projects/kompressornoe-oborudovanie-china-delivery/")
analyze_case("https://longwang.ru/projects/reshenie-problem-s-avansom-i-postavshchikom-v-kitae/")
