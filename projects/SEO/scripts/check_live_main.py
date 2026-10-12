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

def fetch_html(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def check_main_details():
    print("=== LIVE MAIN PAGE DEEP DIVE ===")
    html = fetch_html("https://longwang.ru/")
    
    # Check JSON-LD
    json_lds = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
    print(f"Total JSON-LD blocks: {len(json_lds)}")
    for i, j in enumerate(json_lds):
        print(f"--- Block {i+1} ---")
        try:
            d = json.loads(j.strip())
            print(json.dumps(d, ensure_ascii=False, indent=2)[:800])
        except Exception as e:
            print("Raw:", j[:400])
            
    print("\n=== SEARCHING FOR 'обход' ON LIVE MAIN PAGE ===")
    found_obhod = False
    for line in html.split('\n'):
        if 'обход' in line.lower():
            found_obhod = True
            clean = re.sub(r'<[^>]+>', ' ', line).strip()
            print(f"FOUND 'обход': {clean}")
    if not found_obhod:
        print("НЕТ 'обход' на главной странице!")

    print("\n=== SEARCHING FOR 'санкц' ON LIVE MAIN PAGE ===")
    found_sankc = False
    for line in html.split('\n'):
        if 'санкц' in line.lower():
            found_sankc = True
            clean = re.sub(r'<[^>]+>', ' ', line).strip()
            print(f"FOUND 'санкц': {clean}")
    if not found_sankc:
        print("НЕТ 'санкц' на главной странице!")

if __name__ == '__main__':
    check_main_details()
