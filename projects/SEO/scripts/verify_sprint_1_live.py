import urllib.request
import re
import ssl
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def check_task_1_1():
    print("=== ПРОВЕРКА ЗАДАЧИ 1.1 (Главная: FAQ) ===")
    url = "https://longwang.ru/"
    req = urllib.request.Request(url, headers=HEADERS)
    html = urllib.request.urlopen(req, context=ctx, timeout=10).read().decode('utf-8', errors='ignore')
    
    # Check if 'обход' is still there
    obhod = [line.strip() for line in html.split('\n') if 'обход' in line.lower()]
    print(f"Найдено строк со словом 'обход': {len(obhod)}")
    for l in obhod:
        print("  Line:", l[:120])
        
    # Check 506 or OEM
    oem_matches = [line.strip() for line in html.split('\n') if '506' in line.lower() or 'oem' in line.lower()]
    print(f"Найдено строк с новым текстом (506 / OEM): {len(oem_matches)}")
    for l in oem_matches[:3]:
        print("  New text sample:", re.sub(r'<[^>]+>', ' ', l).strip()[:140])

def check_task_1_4():
    print("\n=== ПРОВЕРКА ЗАДАЧИ 1.4 (Хаб оборудования: блок 10 печей) ===")
    url = "https://longwang.ru/supplies-services-china/equipment-from-china/"
    req = urllib.request.Request(url, headers=HEADERS)
    html = urllib.request.urlopen(req, context=ctx, timeout=10).read().decode('utf-8', errors='ignore')
    
    # Check for furnace links
    furnace_slugs = [
        'muffle-furnaces-china',
        'vacuum-drying-chambers',
        'chamber-furnaces-china',
        'tubular-furnaces-china',
        'drying-cabinets-china',
        'vacuum-soldering-furnaces',
        'specialized-industrial-furnaces',
        'drying-cultivation-cabinets',
        'water-baths-thermostats',
        'tubular-compact-furnaces'
    ]
    
    found = []
    for slug in furnace_slugs:
        if slug in html:
            found.append(slug)
            
    print(f"Найдено ссылок на печи на странице оборудования: {len(found)} из {len(furnace_slugs)}")
    for f in found:
        print(f"  [+] {f}")
        
    if "item-which__sublinks" in html or "Поставляемые типы" in html or "Каталог поставляемых" in html:
        print("  [+] Блок стилизован и успешно внедрен!")
    else:
        print("  [-] Названия классов блока не обнаружены в явном виде, но ссылки есть.")

def check_gogetlinks():
    print("\n=== ПРОВЕРКА ФАЙЛОВ GOGETLINKS В c:\\Codex\\projects\\SEO ===")
    files = os.listdir(r"c:\Codex\projects\SEO")
    for f in files:
        if any(w in f.lower() for w in ['goget', 'link', 'csv', 'xlsx']) and not f.startswith('redirect'):
            fp = os.path.join(r"c:\Codex\projects\SEO", f)
            print(f"Found candidate: {f} ({os.path.getsize(fp)} bytes)")

if __name__ == '__main__':
    check_task_1_1()
    check_task_1_4()
    check_gogetlinks()
