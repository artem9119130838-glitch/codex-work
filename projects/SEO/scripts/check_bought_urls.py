import urllib.request
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0'}

test_bought_urls = [
    "https://longwang.ru/uslugi-v-kitae/parallelnyj-import-is-kitaya/",
    "https://longwang.ru/uslugi-v-kitae/dostavka-is-kitaya/",
    "https://longwang.ru/products/parallelnyj-import-cherez-serbiyu-kitaj-kazahtsan/",
    "https://longwang.ru/ved-s-kitaem/",
    "https://longwang.ru/uslugi-v-kitae/dostavka-is-kitaya/jeleznodorojnaya-dostavka-iz-kitaya/",
    "https://longwang.ru/products/rabota-po-akkreditivu-lizing-s-knr/"
]

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(NoRedirectHandler)

print("=== CHECKING BOUGHT GOGETLINKS TARGET URLS LIVE ===")
for u in test_bought_urls:
    req = urllib.request.Request(u, headers=HEADERS)
    try:
        resp = opener.open(req, timeout=8)
        print(f"[{resp.status}] {u}")
    except urllib.error.HTTPError as e:
        loc = e.headers.get('Location')
        redir = f" -> {loc}" if loc else ""
        print(f"[{e.code}] {u}{redir}")
    except Exception as e:
        print(f"[ERR] {u} : {e}")
