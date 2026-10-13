import os
import sys
import ssl
import csv
import urllib.request
import urllib.error
import re
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

# SSL context for live checks
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

PAGES_SPRINT_2 = [
    "https://longwang.ru/international/import-v-kitaj/",
    "https://longwang.ru/useful-articles/exhibitions-in-china/",
    "https://longwang.ru/projects/manufacturer-search-audit-china/",
    "https://longwang.ru/useful-articles/worlds-brend-equipment/",
    "https://longwang.ru/useful-articles/pryamye-postavki-iz-kitaya/",
    "https://longwang.ru/useful-articles/purchases-without-intermediaries/",
    "https://longwang.ru/useful-articles/dokumentalnoe-oformlenie-importa-cherez-agenta/",
    "https://longwang.ru/supplies-services-china/equipment-from-china/",
    "https://longwang.ru/supplies-services-china/proverka-postavshhika-v-kitae/",
    "https://longwang.ru/projects/ozon-supply-china/",
    "https://longwang.ru/projects/kitchen-appliances-white-ved/",
    "https://longwang.ru/useful-articles/aviadostavka-gruzov-iz-kitaya/"
]

def check_live_status(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=12)
        code = resp.status
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract meta robots
        robots_match = re.search(r'<meta[^>]+name=[\'"]robots[\'"][^>]+content=[\'"]([^\'"]+)[\'"]', html, re.I)
        robots_val = robots_match.group(1) if robots_match else "not_found"
        
        # Extract canonical
        canonical_match = re.search(r'<link[^>]+rel=[\'"]canonical[\'"][^>]+href=[\'"]([^\'"]+)[\'"]', html, re.I)
        canonical_val = canonical_match.group(1) if canonical_match else "not_found"
        
        # Extract title
        title_match = re.search(r'<title>([^<]+)</title>', html, re.I)
        title_val = title_match.group(1).strip() if title_match else "not_found"
        
        return {
            'status': code,
            'robots': robots_val,
            'canonical': canonical_val,
            'title': title_val,
            'error': None
        }
    except urllib.error.HTTPError as e:
        return {'status': e.code, 'robots': None, 'canonical': None, 'title': None, 'error': f"HTTP {e.code}"}
    except Exception as e:
        return {'status': 0, 'robots': None, 'canonical': None, 'title': None, 'error': str(e)}

def check_screaming_frog(pages):
    sf_csv = r"c:\Codex\projects\SEO\Screaming Frog\2026.10.12.20.54.20\internal_all.csv"
    results = {}
    if not os.path.exists(sf_csv):
        return results
        
    with open(sf_csv, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader, [])
        header_map = {col.strip(): idx for idx, col in enumerate(header)}
        
        addr_idx = header_map.get('Address')
        idx_status_idx = header_map.get('Indexability Status')
        idxability_idx = header_map.get('Indexability')
        status_code_idx = header_map.get('Status Code')
        canonical_idx = header_map.get('Canonical Link Element 1')
        meta_robots_idx = header_map.get('Meta Robots 1')
        
        for row in reader:
            if not row or addr_idx is None or addr_idx >= len(row):
                continue
            addr = row[addr_idx].strip()
            for p in pages:
                if addr.rstrip('/') == p.rstrip('/'):
                    results[p] = {
                        'status_code': row[status_code_idx] if status_code_idx < len(row) else '',
                        'indexability': row[idxability_idx] if idxability_idx < len(row) else '',
                        'indexability_status': row[idx_status_idx] if idx_status_idx < len(row) else '',
                        'canonical': row[canonical_idx] if canonical_idx < len(row) else '',
                        'meta_robots': row[meta_robots_idx] if meta_robots_idx < len(row) else ''
                    }
    return results

def check_siteanalyzer(pages):
    sa_xlsx = r"c:\Codex\projects\SEO\export_longwang.ru.xlsx"
    results = {}
    if not os.path.exists(sa_xlsx):
        return results
        
    wb = openpyxl.load_workbook(sa_xlsx, read_only=True)
    # Find sheet with main URLs
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return results
    header = [str(c).strip() if c is not None else '' for c in rows[0]]
    url_col = 0
    status_col = None
    for idx, col in enumerate(header):
        if 'url' in col.lower() or 'адрес' in col.lower():
            url_col = idx
        if 'код' in col.lower() or 'status' in col.lower():
            status_col = idx
            
    for row in rows[1:]:
        if not row or url_col >= len(row):
            continue
        val = str(row[url_col]).strip() if row[url_col] is not None else ''
        for p in pages:
            if val.rstrip('/') == p.rstrip('/'):
                results[p] = {
                    'found': True,
                    'status': row[status_col] if status_col is not None and status_col < len(row) else 'N/A'
                }
    return results

def check_gsc_exports(pages):
    gsc_dir = r"c:\Codex\projects\SEO\gsc_extracted"
    results = {p: [] for p in pages}
    if not os.path.exists(gsc_dir):
        return results
        
    for root, dirs, files in os.walk(gsc_dir):
        for file in files:
            if not file.endswith('.csv'):
                continue
            fp = os.path.join(root, file)
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for r in reader:
                    row_str = " ".join(r)
                    for p in pages:
                        p_norm = p.rstrip('/')
                        if p_norm in row_str or p in row_str:
                            results[p].append(f"{os.path.basename(root)}/{file}")
    # Deduplicate
    for p in results:
        results[p] = list(set(results[p]))
    return results

def check_ruselectronic_status():
    print("\n" + "="*80)
    print("=== АУДИТ ДОНОРА RUSELECTRONIC.COM В GOGETLINKS И LIVE ===")
    print("="*80)
    
    # Check paid.csv
    paid_csv = r"c:\Codex\projects\SEO\paid.csv"
    in_paid = False
    if os.path.exists(paid_csv):
        with open(paid_csv, 'r', encoding='cp1251', errors='ignore') as f:
            for line in f:
                if 'ruselectronic' in line.lower():
                    in_paid = True
                    print(f"[!] ruselectronic найден в paid.csv: {line.strip()}")
    if not in_paid:
        print("[-] ruselectronic.com ОТСУТСТВУЕТ в paid.csv (сделка еще не закрыта / не оплачена в истории)")
        
    # Check donor metadata in donors_parsed.json
    import json
    parsed_json = r"c:\Codex\projects\SEO\donors_parsed.json"
    if os.path.exists(parsed_json):
        with open(parsed_json, 'r', encoding='utf-8') as f:
            donors = json.load(f)
            r_info = next((d for d in donors if 'ruselectronic' in d.get('domain', '')), None)
            if r_info:
                print(f"[+] Найден в donors_parsed.json:")
                print(f"    Domain: {r_info.get('domain')}")
                print(f"    Site ID в GoGetLinks: {r_info.get('site_id')}")
                print(f"    ИКС Яндекса: {r_info.get('iks')}")
                print(f"    PR-CY Rank: {r_info.get('pr_cy')}")
                print(f"    Трафик (уников/сутки): {r_info.get('traffic')}")
                print(f"    Скорость размещения: {r_info.get('speed')}/10")
                print(f"    Цена размещения статьи: {r_info.get('price')} руб.")
                print(f"    Статус: {'NEW (Новая площадка)' if r_info.get('is_new') else 'Ранее проверена'}")
                print(f"    Ссылка прикрепления в GGL: https://gogetlinks.net/articles/attach/articleId/0/siteId/{r_info.get('site_id')}")

    # Check live site
    print("\n[*] Проверка доступности live-сайта ruselectronic.com:")
    req = urllib.request.Request("https://ruselectronic.com/", headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"    [+] HTTP Status: {resp.status} OK")
        # Check if longwang is already mentioned
        has_lw = 'longwang' in html.lower()
        print(f"    [+] Упоминание longwang.ru на главной: {'ДА' if has_lw else 'НЕТ'}")
    except Exception as e:
        print(f"    [-] Ошибка подключения к ruselectronic.com: {e}")

def main():
    print("="*80)
    print("=== АППАРАТНАЯ ПРОВЕРКА 12 СТРАНИЦ СПРИНТА 2 (INDEXATION & TECHNICAL AUDIT) ===")
    print("="*80)
    
    sf_data = check_screaming_frog(PAGES_SPRINT_2)
    sa_data = check_siteanalyzer(PAGES_SPRINT_2)
    gsc_data = check_gsc_exports(PAGES_SPRINT_2)
    
    print(f"\nВсего страниц в проверке: {len(PAGES_SPRINT_2)}")
    print("-" * 80)
    
    all_ok = True
    for i, p in enumerate(PAGES_SPRINT_2, 1):
        live = check_live_status(p)
        sf = sf_data.get(p, {})
        sa = sa_data.get(p, {})
        gsc = gsc_data.get(p, [])
        
        status_ok = (live.get('status') == 200)
        canonical_ok = (live.get('canonical') == p)
        robots_ok = ('noindex' not in (live.get('robots') or '').lower())
        
        if not (status_ok and canonical_ok and robots_ok):
            all_ok = False
            
        print(f"[{i:02d}] {p}")
        print(f"     LIVE HTTP: {live.get('status')} | Robots: {live.get('robots')} | Canonical OK: {canonical_ok}")
        print(f"     Title: {live.get('title')[:70]}...")
        if sf:
            print(f"     Screaming Frog: Status={sf.get('status_code')}, Indexability={sf.get('indexability')} ({sf.get('indexability_status')})")
        else:
            print(f"     Screaming Frog: [Не найдена в crawl dump]")
        if sa:
            print(f"     SiteAnalyzer: Status={sa.get('status')}")
        if gsc:
            print(f"     GSC Coverage/Performance files: {len(gsc)} files ({', '.join(gsc[:2])})")
        else:
            print(f"     GSC Coverage: [Новый URL / Ожидает очередной выгрузки]")
        print()
        
    print("-" * 80)
    print(f"ИТОГ ПО 12 СТРАНИЦАМ: {'ВСЕ 12 СТРАНИЦ ОТДАЮТ 200 OK И ОТКРЫТЫ К ИНДЕКСАЦИИ' if all_ok else 'ОБНАРУЖЕНЫ ОТКЛОНЕНИЯ'}")
    
    check_ruselectronic_status()

if __name__ == '__main__':
    main()
