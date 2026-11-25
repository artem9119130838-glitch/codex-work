# -*- coding: utf-8 -*-
"""
Скрипт точечной оптимизации статей 2 и 3 через WP REST API:
- Post 7704: aviadostavka-gruzov-iz-kitaya (Авиадоставка грузов)
- Post 4772: payment-methods-china (Способы оплаты в Китай)
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

def update_air_article(post_id, auth_header, dry_run=False):
    print(f"\n==================== PROCESSING POST {post_id} (Авиадоставка) ====================")
    post = get_post(post_id, auth_header)
    content = post['content']['raw']

    # Backup snapshot
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bfile = os.path.join(BACKUP_DIR, f"post_{post_id}_pre_edit_{ts}.html")
    with open(bfile, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Snapshot backup saved to: {bfile}")

    new_content = content

    # 1. Update H2: Актуальные тарифы и сроки авиадоставки в 2025 году -> Структура тарифов и реальные сроки авиадоставки грузов
    old_h2 = '<h2>Актуальные тарифы и сроки авиадоставки в 2025 году</h2>'
    new_h2 = '<h2>Структура тарифов и реальные сроки авиадоставки грузов</h2>'
    if old_h2 in new_content:
        new_content = new_content.replace(old_h2, new_h2, 1)
        print("✓ H2 updated: 'Структура тарифов...'")
    else:
        print("! Warning: H2 2025 marker not found directly")

    # 2. Insert B2B Callout widget before H2 'Структура тарифов'
    callout_air = """
<!-- [START B2B CALLOUT AIR FREIGHT] -->
<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #0284c7; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">✈️ Срочная авиадоставка коммерческих партий из Китая под ключ</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    Организуем регулярные грузовые рейсы из Пекина, Шанхая, Гуанчжоу и Шэньчжэня от 3 дней. Полное таможенное оформление в Шереметьево/Домодедово, закрывающие документы по безналичному расчету с НДС 22%.
  </p>
  <a href="/supplies-services-china/dostavka-is-kitaya/aviadostavka-iz-kitaya/" style="display:inline-block; background:#0284c7; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Тарифы и условия авиадоставки грузов →
  </a>
</div>
<!-- [END B2B CALLOUT AIR FREIGHT] -->
"""
    target_pos = new_h2 if new_h2 in new_content else old_h2
    if target_pos in new_content and '<!-- [START B2B CALLOUT AIR FREIGHT] -->' not in new_content:
        new_content = new_content.replace(target_pos, callout_air + "\n" + target_pos, 1)
        print("✓ B2B Callout widget inserted for Air Freight")

    # 3. Fix CTA block button link to point directly to subhub /aviadostavka-iz-kitaya/ instead of general form
    old_btn = '<a href="/supplies-services-china/dostavka-is-kitaya/#form" \n   title="Как доставить груз из Китая самолётом"'
    new_btn = '<a href="/supplies-services-china/dostavka-is-kitaya/aviadostavka-iz-kitaya/" \n   title="Авиадоставка грузов из Китая под ключ"'
    if old_btn in new_content:
        new_content = new_content.replace(old_btn, new_btn, 1)
        print("✓ CTA button link updated to dedicated /aviadostavka-iz-kitaya/")
    else:
        # Fallback without exact whitespace
        import re
        new_content = re.sub(
            r'href="/supplies-services-china/dostavka-is-kitaya/#form"\s+title="[^"]*"',
            'href="/supplies-services-china/dostavka-is-kitaya/aviadostavka-iz-kitaya/" title="Авиадоставка грузов из Китая под ключ"',
            new_content
        )
        print("✓ CTA button link updated via regex")

    # 4. Contextual link in intro
    old_intro_phrase = '<p>Выбор авиатранспорта должен быть осознанным. Ниже — сжатый анализ его сильных и слабых сторон.</p>'
    new_intro_phrase = '<p>Выбор авиатранспорта должен быть осознанным. Если вашей компании необходима <a href="/supplies-services-china/dostavka-is-kitaya/aviadostavka-iz-kitaya/" title="Прямая грузовая авиадоставка из Китая">прямая грузовая авиадоставка из Китая</a> с гарантией сроков и белой таможней — изучите условия и требования перевозки. Ниже — сжатый анализ сильных и слабых сторон.</p>'
    if old_intro_phrase in new_content:
        new_content = new_content.replace(old_intro_phrase, new_intro_phrase, 1)
        print("✓ Intro contextual anchor added for Air Freight")

    if dry_run:
        print(f"DRY RUN (Post {post_id}): Old length {len(content)}, New length {len(new_content)}")
    else:
        res = update_post(post_id, {'content': new_content}, auth_header)
        print(f"SUCCESS: Post {post_id} updated live!")
        print(f"Post URL: {res.get('link')}")

def update_payment_article(post_id, auth_header, dry_run=False):
    print(f"\n==================== PROCESSING POST {post_id} (Платежи в Китай) ====================")
    post = get_post(post_id, auth_header)
    content = post['content']['raw']

    # Backup snapshot
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bfile = os.path.join(BACKUP_DIR, f"post_{post_id}_pre_edit_{ts}.html")
    with open(bfile, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Snapshot backup saved to: {bfile}")

    new_content = content

    # 1. Update intro paragraph with target anchor
    old_intro = '<p>С марта 2024 года остановились практически все оплаты в Китай напрямую из России. С этим столкнулись все, кому необходимо покупать китайские товары и оплачивать китайским поставщикам. На сегодня уже появились варианты оплат в юанях и в рублях в Китай, основные эти возможности мы и рассмотрим в этой статье.</p>'
    new_intro = '<p>С марта 2024 года остановились практически все прямые межбанковские переводы в юрисдикцию КНР. Бизнес, закупающий сырье и оборудование, вынужден искать легальные и безопасные финансовые шлюзы. В статье разберем, как законно <a href="/supplies-services-china/autsorsing-ved/platezhi-v-kitai/" title="Платежи в Китай по агентскому договору ВЭД">перевести деньги в Китай поставщику</a> и какие схемы несут риски блокировок со стороны комплаенса и налоговой.</p>'
    if old_intro in new_content:
        new_content = new_content.replace(old_intro, new_intro, 1)
        print("✓ Intro paragraph updated with commercial anchor")
    else:
        print("! Warning: Intro paragraph marker not matched directly")

    # 2. Insert B2B Callout widget after first H2 section
    callout_pay = """
<!-- [START B2B CALLOUT CHINA PAYMENTS] -->
<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #16a34a; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">💳 Безопасные B2B-платежи в Китай по агентскому договору ВЭД</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    Оплата инвойсов китайских производителей в юанях за 24–48 часов. Полное закрытие сделки по безналичному расчету с НДС 22%, предоставление ГТД и подтверждающих документов без риска блокировок по 115-ФЗ.
  </p>
  <a href="/supplies-services-china/autsorsing-ved/platezhi-v-kitai/" style="display:inline-block; background:#16a34a; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Рассчитать условия и комиссию перевода →
  </a>
</div>
<!-- [END B2B CALLOUT CHINA PAYMENTS] -->
"""
    sec2_marker = '<h2 class="wp-block-heading">Оплата в Китай напрямую через агентов в третьих странах</h2>'
    if sec2_marker in new_content and '<!-- [START B2B CALLOUT CHINA PAYMENTS] -->' not in new_content:
        new_content = new_content.replace(sec2_marker, callout_pay + "\n" + sec2_marker, 1)
        print("✓ B2B Callout widget inserted for Payments")
    else:
        print("! Warning: Section 2 marker not matched directly")

    # 3. Update ending link anchor
    old_end_anchor = '<a title="Как оплатить в Китай из России" href="/supplies-services-china/autsorsing-ved/platezhi-v-kitai/">оплат в Китай</a>'
    new_end_anchor = '<a title="Платежи в Китай по агентскому договору ВЭД" href="/supplies-services-china/autsorsing-ved/platezhi-v-kitai/">официальных платежей в Китай поставщику</a>'
    if old_end_anchor in new_content:
        new_content = new_content.replace(old_end_anchor, new_end_anchor, 1)
        print("✓ Ending anchor updated successfully")
    else:
        print("! Warning: Ending anchor not matched directly")

    if dry_run:
        print(f"DRY RUN (Post {post_id}): Old length {len(content)}, New length {len(new_content)}")
    else:
        res = update_post(post_id, {'content': new_content}, auth_header)
        print(f"SUCCESS: Post {post_id} updated live!")
        print(f"Post URL: {res.get('link')}")

def main():
    parser = argparse.ArgumentParser(description="Update Articles 2 and 3")
    parser.add_argument("--dry-run", action="store_true", help="Preview without modifying live posts")
    args = parser.parse_args()

    env_vars = load_env()
    auth_header = get_auth_header(env_vars)

    update_air_article(7704, auth_header, dry_run=args.dry_run)
    update_payment_article(4772, auth_header, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
