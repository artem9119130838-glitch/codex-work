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

def check_main_page():
    print("=== 1. ПРОВЕРКА ГЛАВНОЙ СТРАНИЦЫ (https://longwang.ru/) ===")
    html = fetch_html("https://longwang.ru/")
    print(f"Длина HTML: {len(html)} символов")
    
    # JSON-LD
    json_lds = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
    print(f"Найдено блоков JSON-LD: {len(json_lds)}")
    faq_found = False
    for i, raw_j in enumerate(json_lds):
        try:
            parsed = json.loads(raw_j.strip())
            types = []
            if isinstance(parsed, dict):
                types.append(parsed.get('@type', ''))
                if '@graph' in parsed:
                    types.extend([item.get('@type', '') for item in parsed['@graph'] if isinstance(item, dict)])
            elif isinstance(parsed, list):
                types.extend([item.get('@type', '') for item in parsed if isinstance(item, dict)])
            print(f"  JSON-LD блок #{i+1}: Типы = {types}")
            if any('FAQPage' in str(t) for t in types):
                faq_found = True
                print("  -> Найдена разметка FAQPage! Содержимое:")
                print(raw_j[:600])
        except Exception as e:
            print(f"  JSON-LD блок #{i+1}: Ошибка парсинга JSON: {e}")
            if 'FAQPage' in raw_j:
                faq_found = True
                print("  -> В сыром виде содержит FAQPage")

    # Sanctions check
    sanctions = re.findall(r'[^.!?\n]*санкц[^.!?\n]*', html, re.IGNORECASE)
    print(f"\nУпоминания корня 'санкц' на главной странице ({len(sanctions)} шт.):")
    for s in sanctions[:10]:
        print(f"  - {s.strip()}")
        
    obhod = re.findall(r'[^.!?\n]*обход[^.!?\n]*', html, re.IGNORECASE)
    print(f"\nУпоминания корня 'обход' на главной странице ({len(obhod)} шт.):")
    for o in obhod[:10]:
        print(f"  - {o.strip()}")

def check_article_links():
    url = "https://longwang.ru/useful-articles/kak-kupit-oborudovanie-kitay/"
    print(f"\n=== 2. ПРОВЕРКА СТАТЬИ О ПОКУПКЕ ОБОРУДОВАНИЯ ({url}) ===")
    html = fetch_html(url)
    
    # Extract links inside article body
    # Find links
    links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)
    print(f"Всего тегов <a> на странице: {len(links)}")
    
    internal_links = []
    for href, anchor in links:
        clean_anchor = re.sub(r'<[^>]+>', '', anchor).strip()
        if 'longwang.ru' in href or href.startswith('/'):
            internal_links.append((href, clean_anchor))
            
    print(f"Внутренних ссылок: {len(internal_links)}")
    print("Примеры ссылок в тексте (с анкорами):")
    content_links = [l for l in internal_links if not any(x in l[0] for x in ['#', 'wp-content', 'tel:', 'mailto:']) and len(l[1]) > 0]
    for href, anc in content_links[:25]:
        print(f"  - [{anc}] -> {href}")

def check_projects_cases():
    url = "https://longwang.ru/projects/"
    print(f"\n=== 3. ПРОВЕРКА РАЗДЕЛА КЕЙСОВ ({url}) ===")
    html = fetch_html(url)
    
    # Extract case cards/links
    case_links = re.findall(r'<a\s+[^>]*href=["\'](https://longwang\.ru/projects/[^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)
    if not case_links:
        case_links = re.findall(r'<a\s+[^>]*href=["\'](/projects/[^"\']+)["\'][^>]*>(.*?)</a>', html, re.DOTALL | re.IGNORECASE)
        
    unique_cases = {}
    for href, anchor in case_links:
        clean_anchor = re.sub(r'<[^>]+>', '', anchor).strip()
        if href != '/projects/' and href != 'https://longwang.ru/projects/':
            if href not in unique_cases or (not unique_cases[href] and clean_anchor):
                unique_cases[href] = clean_anchor
                
    print(f"Найдено уникальных ссылок на кейсы: {len(unique_cases)}")
    for href, title in list(unique_cases.items())[:10]:
        print(f"  - {href} : \"{title}\"")

if __name__ == '__main__':
    check_main_page()
    check_article_links()
    check_projects_cases()
