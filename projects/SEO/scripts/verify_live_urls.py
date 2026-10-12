import urllib.request
import urllib.error
import re
import ssl
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')

# Disable SSL verification issues if any
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 AntigravitySEO/1.0'
}

TEST_URLS = [
    # Main & Hubs
    "https://longwang.ru/",
    "https://longwang.ru/supplies-services-china/",
    "https://longwang.ru/equipment-from-china/",
    # VED conflict pair
    "https://longwang.ru/autsorsing-ved/",
    "https://longwang.ru/ved-s-kitaem/",
    # Sourcing / Verification conflict pair
    "https://longwang.ru/poisk-postavshchikov-v-kitae/",
    "https://longwang.ru/poisk-tovara-v-kitae/",
    "https://longwang.ru/proverka-postavshchika-v-kitae/",
    # Logistics Hub & branches
    "https://longwang.ru/dostavka-gruzov-iz-kitaya/",
    "https://longwang.ru/aviadostavka-iz-kitaya/",
    "https://longwang.ru/avtodostavka-iz-kitaya/",
    "https://longwang.ru/zhd-dostavka-iz-kitaya/",
    "https://longwang.ru/morskaya-dostavka-iz-kitaya/",
    # Customs
    "https://longwang.ru/tamozhennoe-oformlenie-gruzov-iz-kitaya/",
    "https://longwang.ru/tamozhennoe-oformlenie/",
    "https://longwang.ru/rastamozhka-iz-kitaya/",
    # Inspection / Control
    "https://longwang.ru/kontrol-kachestva-v-kitae/",
    "https://longwang.ru/inspektsiya-v-kitae/",
    "https://longwang.ru/audit-fabriki-v-kitae/",
    # Thermal & Equipment subhubs
    "https://longwang.ru/termooborudovanie-iz-kitaya/",
    "https://longwang.ru/oborudovanie-dlya-proizvodstva-iz-kitaya/",
    "https://longwang.ru/stanki-iz-kitaya/",
    # Content Hubs
    "https://longwang.ru/projects/",
    "https://longwang.ru/useful-articles/",
    "https://longwang.ru/useful-articles/kak-kupit-oborudovanie-kitay/",
    # Test for 410 / Redirection rules mentioned in ChatGPT audit
    "https://longwang.ru/?pagespeed=1",
    "https://longwang.ru/test%2C",
    "https://longwang.ru/?__mjo=1",
    "https://longwang.ru/non-existent-page-404-test"
]

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Do not follow redirect automatically, report it
        return None

def check_url(url):
    req = urllib.request.Request(url, headers=HEADERS)
    opener = urllib.request.build_opener(NoRedirectHandler)
    
    start = time.time()
    try:
        with opener.open(req, timeout=10) as resp:
            elapsed = round((time.time() - start) * 1000, 1)
            status = resp.status
            content = resp.read(15000).decode('utf-8', errors='ignore')
            
            # Extract title
            title_m = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            title = title_m.group(1).strip() if title_m else ""
            
            # Extract canonical
            canon_m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', content, re.IGNORECASE)
            canonical = canon_m.group(1) if canon_m else ""
            
            # Extract robots
            robots_m = re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
            robots = robots_m.group(1) if robots_m else ""
            
            return {
                "url": url,
                "status": status,
                "redirect_to": None,
                "title": title[:70],
                "canonical": canonical,
                "robots": robots,
                "time_ms": elapsed
            }
    except urllib.error.HTTPError as e:
        elapsed = round((time.time() - start) * 1000, 1)
        redirect_to = e.headers.get('Location')
        return {
            "url": url,
            "status": e.code,
            "redirect_to": redirect_to,
            "title": "",
            "canonical": "",
            "robots": "",
            "time_ms": elapsed
        }
    except Exception as e:
        elapsed = round((time.time() - start) * 1000, 1)
        return {
            "url": url,
            "status": f"ERR: {str(e)[:40]}",
            "redirect_to": None,
            "title": "",
            "canonical": "",
            "robots": "",
            "time_ms": elapsed
        }

def run_live_check():
    print(f"Starting Live Check for {len(TEST_URLS)} key URLs on https://longwang.ru/...")
    results = []
    for u in TEST_URLS:
        res = check_url(u)
        results.append(res)
        st = str(res['status'])
        redir = f" -> {res['redirect_to']}" if res['redirect_to'] else ""
        can = f" [can: {res['canonical']}]" if res['canonical'] else ""
        rob = f" [robots: {res['robots']}]" if res['robots'] else ""
        tit = f" \"{res['title']}\"" if res['title'] else ""
        print(f"[{st:3}] {u}{redir}{can}{rob}{tit} ({res['time_ms']}ms)")
        time.sleep(0.15) # gentle delay
        
    out_file = r"c:\Codex\projects\SEO\scripts\live_urls_results.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved results to {out_file}")

if __name__ == '__main__':
    run_live_check()
