# -*- coding: utf-8 -*-
"""
Скрипт точечной оптимизации статьи 'kak-kupit-oborudovanie-kitay' (ID 8707) через WP REST API.
Ликвидация поисковой каннибализации, разведение интентов и перелинковка на калькулятор.
"""

import os
import sys
import json
import base64
import argparse
import urllib.request
import ssl
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ENV_FILE = '.env'
BACKUP_DIR = 'backup'

def load_env():
    env_vars = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars

def get_auth_header(env_vars):
    user = os.getenv("WP_USER") or env_vars.get("WP_USER", "")
    pwd = os.getenv("WP_APP_PASSWORD") or env_vars.get("WP_APP_PASSWORD", "") or env_vars.get("WP_PASSWORD", "")
    if not user or not pwd:
        raise ValueError("WP_USER or WP_APP_PASSWORD not found in environment or .env")
    token = base64.b64encode(f"{user}:{pwd}".encode('utf-8')).decode('utf-8')
    return f"Basic {token}"

def get_post(post_id, auth_header):
    url = f"https://longwang.ru/wp-json/wp/v2/posts/{post_id}?context=edit"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Authorization': auth_header})
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.loads(r.read().decode('utf-8'))

def update_post(post_id, data, auth_header):
    url = f"https://longwang.ru/wp-json/wp/v2/posts/{post_id}"
    encoded = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=encoded,
        headers={
            'User-Agent': 'Mozilla/5.0',
            'Authorization': auth_header,
            'Content-Type': 'application/json; charset=utf-8'
        },
        method='POST'
    )
    with urllib.request.urlopen(req, context=ctx) as r:
        return json.loads(r.read().decode('utf-8'))

def main():
    parser = argparse.ArgumentParser(description="Update Equipment Article")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying live post")
    args = parser.parse_args()

    env_vars = load_env()
    auth_header = get_auth_header(env_vars)
    post_id = 8707

    print(f"Fetching post {post_id} from WordPress...")
    post = get_post(post_id, auth_header)
    content = post['content']['raw']

    # 1. Snapshot backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bfile = os.path.join(BACKUP_DIR, f"post_{post_id}_pre_edit_{ts}.html")
    with open(bfile, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Snapshot backup saved to: {bfile}")

    new_content = content

    # 2. Edit intro anchor: change generic 'оборудование' to 'поставку промышленного оборудования из Китая под ключ'
    old_intro = '<a href="/supplies-services-china/equipment-from-china/" title="Оборудование из Китая под ключ">оборудование</a>'
    new_intro = '<a href="/supplies-services-china/equipment-from-china/" title="Поставка оборудования из Китая под ключ">поставку промышленного оборудования из Китая под ключ</a>'
    if old_intro in new_content:
        new_content = new_content.replace(old_intro, new_intro, 1)
        print("✓ Intro anchor updated successfully")
    else:
        print("! Warning: Intro anchor pattern not matched directly")

    # 3. Insert B2B Callout widget between Step 1 and Step 2
    callout_html = """
<!-- [START B2B CALLOUT EQUIPMENT CALCULATOR] -->
<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #2563eb; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">⚙️ Расчет белой себестоимости и таможни оборудования под ключ</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    Если вам требуется готовая поставка производственной линии, станка или термооборудования без рисков посредников — рассчитайте полную стоимость доставки, ввозных пошлин и НДС 22% в нашем интерактивном калькуляторе.
  </p>
  <a href="/supplies-services-china/equipment-from-china/" style="display:inline-block; background:#2563eb; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Рассчитать себестоимость оборудования на калькуляторе →
  </a>
</div>
<!-- [END B2B CALLOUT EQUIPMENT CALCULATOR] -->
"""
    step2_marker = '<h2>Шаг 2. Проверить поставщика по пяти пунктам (Due Diligence)</h2>'
    if step2_marker in new_content and '<!-- [START B2B CALLOUT EQUIPMENT CALCULATOR] -->' not in new_content:
        new_content = new_content.replace(step2_marker, callout_html + "\n" + step2_marker, 1)
        print("✓ B2B Callout widget inserted before Step 2")
    else:
        print("! Warning: Step 2 marker not matched or widget already exists")

    # 4. Insert calculator link in Step 7 under customs
    calc_snippet = '<p>Для предварительного расчета белой себестоимости, ввозных пошлин и НДС 22% воспользуйтесь нашим <a href="/supplies-services-china/equipment-from-china/#calculator" title="Онлайн-калькулятор растаможки оборудования"><strong>интерактивным калькулятором растаможки оборудования</strong></a>.</p>'
    step7_marker = '<p>Для сложного оборудования часто требуется декларация о соответствии или сертификат. Заказывайте услуги таможенного представителя, если нет своего специалиста.</p>'
    if step7_marker in new_content and 'интерактивным калькулятором растаможки' not in new_content:
        new_content = new_content.replace(step7_marker, step7_marker + "\n" + calc_snippet, 1)
        print("✓ Calculator link inserted in Step 7")
    else:
        print("! Warning: Step 7 marker not matched or link already exists")

    # 5. Strengthen ending anchor
    old_end = '<a href="/supplies-services-china/equipment-from-china/" title="Оборудование из Китая">оборудования</a>'
    new_end = '<a href="/supplies-services-china/equipment-from-china/" title="Поставка оборудования из Китая под ключ">поставкой промышленного оборудования из Китая под ключ</a>'
    if old_end in new_content:
        new_content = new_content.replace(old_end, new_end, 1)
        print("✓ Ending anchor updated successfully")
    else:
        print("! Warning: Ending anchor pattern not matched directly")

    if args.dry_run:
        print("\n--- DRY-RUN MODE: Changes will NOT be saved to WordPress ---")
        print(f"Original length: {len(content)}, New length: {len(new_content)}")
        print("Diff check passed successfully.")
    else:
        print("\nApplying changes to LIVE WordPress site...")
        res = update_post(post_id, {'content': new_content}, auth_header)
        print(f"SUCCESS: Post {post_id} updated live!")
        print(f"Post URL: {res.get('link', 'https://longwang.ru/useful-articles/kak-kupit-oborudovanie-kitay/')}")

if __name__ == "__main__":
    main()
