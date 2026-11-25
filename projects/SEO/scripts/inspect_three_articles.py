# -*- coding: utf-8 -*-
import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

urls = {
    'equipment': 'https://longwang.ru/useful-articles/kak-kupit-oborudovanie-kitay/',
    'air': 'https://longwang.ru/useful-articles/aviadostavka-gruzov-iz-kitaya/',
    'payment': 'https://longwang.ru/useful-articles/payment-methods-china/'
}

for k, u in urls.items():
    req = urllib.request.Request(u, headers=headers)
    html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8', errors='ignore')
    title = re.search(r'<title>(.*?)</title>', html, re.I)
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.I)
    print(f"\n==================== {k.upper()} ====================")
    print("URL:", u)
    print("Title:", title.group(1).strip() if title else "")
    print("H1:", re.sub(r'<[^>]+>', '', h1.group(1)).strip() if h1 else "")
    
    # Check target hub links in body
    eq_links = re.findall(r'href=["\'][^"\']*equipment-from-china[^"\']*["\']', html)
    air_links = re.findall(r'href=["\'][^"\']*aviadostavka[^"\']*["\']', html)
    pay_links = re.findall(r'href=["\'][^"\']*platezhi[^"\']*["\']', html)
    print(f"Links found -> eq: {len(eq_links)}, air: {len(air_links)}, pay: {len(pay_links)}")

    # Let's find specific phrases
    if k == 'equipment':
        phrases = re.findall(r'([^.!?\n]*купить оборудование[^.!?\n]*)', html, re.I)
        print("Sentences with 'купить оборудование':", len(phrases))
        for p in phrases[:3]:
            print("  -", re.sub(r'<[^>]+>', '', p).strip())
            
    elif k == 'air':
        phrases = re.findall(r'([^.!?\n]*авиадоставк[^.!?\n]*)', html, re.I)
        print("Sentences with 'авиадоставка':", len(phrases))
        for p in phrases[:3]:
            print("  -", re.sub(r'<[^>]+>', '', p).strip())
            
    elif k == 'payment':
        phrases = re.findall(r'([^.!?\n]*перевести деньги[^.!?\n]*)', html, re.I)
        print("Sentences with 'перевести деньги':", len(phrases))
        for p in phrases[:3]:
            print("  -", re.sub(r'<[^>]+>', '', p).strip())

print("\n==================== INTERNAL ANCHORS IN ARTICLES ====================")
for k, u in urls.items():
    req = urllib.request.Request(u, headers=headers)
    html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8', errors='ignore')
    # search for content links specifically
    anchors = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.I | re.S)
    print(f"\n--- {k.upper()} ---")
    for href, text in anchors:
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        if any(x in href for x in ['supplies-services-china', 'useful-articles', 'projects']):
            if clean_text and len(clean_text) < 60 and clean_text != 'Услуги':
                print(f"   [{clean_text}] -> {href}")
