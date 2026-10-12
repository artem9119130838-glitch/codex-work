import os
import sys
import csv

sys.stdout.reconfigure(encoding='utf-8')

SEO_DIR = r"c:\Codex\projects\SEO"

REDIRECTS = [
    ("/poisk-postavshchikov-v-kitae/", "/supplies-services-china/poisk-i-podbor-postavshika/"),
    ("/poisk-tovara-v-kitae/", "/supplies-services-china/poisk-tovara-v-kitae/"),
    ("/proverka-postavshchika-v-kitae/", "/supplies-services-china/proverka-postavshhika-v-kitae/"),
    ("/dostavka-gruzov-iz-kitaya/", "/supplies-services-china/dostavka-is-kitaya/"),
    ("/aviadostavka-iz-kitaya/", "/supplies-services-china/dostavka-is-kitaya/aviadostavka-iz-kitaya/"),
    ("/avtodostavka-iz-kitaya/", "/supplies-services-china/dostavka-is-kitaya/freight-road-transportation/"),
    ("/zhd-dostavka-iz-kitaya/", "/supplies-services-china/dostavka-is-kitaya/jeleznodorojnaya-dostavka-iz-kitaya/"),
    ("/morskaya-dostavka-iz-kitaya/", "/supplies-services-china/dostavka-is-kitaya/sea-shipping-china/"),
    ("/tamozhennoe-oformlenie-gruzov-iz-kitaya/", "/supplies-services-china/dostavka-is-kitaya/tamojennoe-oformlenie-china/"),
    ("/tamozhennoe-oformlenie/", "/supplies-services-china/dostavka-is-kitaya/tamojennoe-oformlenie-china/"),
    ("/rastamozhka-iz-kitaya/", "/supplies-services-china/dostavka-is-kitaya/tamojennoe-oformlenie-china/"),
    ("/kontrol-kachestva-v-kitae/", "/supplies-services-china/goods-check-china/"),
    ("/inspektsiya-v-kitae/", "/supplies-services-china/goods-check-china/"),
    ("/audit-fabriki-v-kitae/", "/supplies-services-china/proverka-postavshhika-v-kitae/"),
    ("/termooborudovanie-iz-kitaya/", "/supplies-services-china/equipment-from-china/thermo-equipment-china/"),
    ("/oborudovanie-dlya-proizvodstva-iz-kitaya/", "/supplies-services-china/equipment-from-china/"),
    ("/stanki-iz-kitaya/", "/supplies-services-china/equipment-from-china/")
]

def export_all():
    # 1. Redirection Plugin CSV
    csv_file = os.path.join(SEO_DIR, "redirects_redirection_plugin.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "action", "regex", "code", "match"])
        for src, dst in REDIRECTS:
            writer.writerow([src, dst, "url", "0", "301", "url"])
    print(f"Generated: {csv_file}")

    # 2. Apache htaccess
    apache_file = os.path.join(SEO_DIR, "redirects_htaccess.conf")
    with open(apache_file, 'w', encoding='utf-8') as f:
        f.write("# === Longwang.ru 301 Redirects: Fix 404 from old root URLs ===\n")
        for src, dst in REDIRECTS:
            f.write(f"Redirect 301 {src} {dst}\n")
    print(f"Generated: {apache_file}")

    # 3. Nginx config
    nginx_file = os.path.join(SEO_DIR, "redirects_nginx.conf")
    with open(nginx_file, 'w', encoding='utf-8') as f:
        f.write("# === Longwang.ru Nginx 301 Rewrites ===\n")
        for src, dst in REDIRECTS:
            f.write(f"rewrite ^{src}$ {dst} permanent;\n")
    print(f"Generated: {nginx_file}")

if __name__ == '__main__':
    export_all()
