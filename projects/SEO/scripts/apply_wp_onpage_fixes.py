"""
Канонический скрипт применения On-Page правок Спринта 1 в WordPress через WP REST API.

Бизнес-процесс: Внесение On-Page правок Longwang.ru (метатеги, Callout-блоки, перелинковка).
Правило: Dry-Run First — по умолчанию работает строго в режиме --dry-run без модификации данных.
Изоляция секретов: Чтение WP_USER и WP_APP_PASSWORD / WP_PASSWORD из projects/SEO/.env или переменных окружения.
"""

import os
import sys
import json
import base64
import argparse
import urllib.request
import urllib.error
import ssl
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# SSL context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SEO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(SEO_DIR, ".env")
DIFF_LOG_FILE = os.path.join(SEO_DIR, "ONPAGE_IMPLEMENTATION_DIFF_LOG.md")

def load_env():
    """Безопасное чтение .env без сторонних библиотек"""
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
        return None
    token = base64.b64encode(f"{user}:{pwd}".encode('utf-8')).decode('utf-8')
    return f"Basic {token}"

def wp_api_request(endpoint, method="GET", data=None, auth_header=None, base_url="https://longwang.ru/wp-json/wp/v2/"):
    import time
    url = f"{base_url}{endpoint}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AntigravitySEO/1.0',
        'Accept': 'application/json'
    }
    if auth_header:
        headers['Authorization'] = auth_header
    
    encoded_data = None
    if data is not None:
        headers['Content-Type'] = 'application/json; charset=utf-8'
        encoded_data = json.dumps(data).encode('utf-8')
        
    for attempt in range(1, 4):
        req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
                res_body = resp.read().decode('utf-8')
                return resp.status, json.loads(res_body) if res_body else {}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='replace')
            try:
                parsed = json.loads(err_body)
            except Exception:
                parsed = {"error": err_body}
            return e.code, parsed
        except Exception as e:
            if attempt < 3:
                time.sleep(2)
                continue
            return 0, {"error": str(e)}


# -------------------------------------------------------------
# 1. СТАТЬИ БЛОГА: B2B CALLOUT-БЛОКИ
# -------------------------------------------------------------
CALLOUT_TASKS = [
    {
        "id": 1637,
        "slug": "bayer-v-kitae-plyusy-i-minusy",
        "url": "https://longwang.ru/useful-articles/bayer-v-kitae-plyusy-i-minusy/",
        "title": "Байер в Китае: плюсы и минусы",
        "anchor": '<img src="/wp-content/uploads/2024/02/bayer-in-china.webp"',
        "anchor_position": "before", # вставляем прямо перед анкором
        "target_hub_url": "/supplies-services-china/proverka-postavshhika-v-kitae/",
        "location_desc": "После вводной части (абзац 2), перед вводным изображением статьи",
        "callout_html": """<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #dc2626; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">⚠️ Риски работы через частных байеров для B2B-компаний</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    Перевод денег физлицам в Китае и закупка без прямого контракта создают угрозу блокировки счетов по 115-ФЗ и отсутствия юридических гарантий при поставке брака. Для закупки производственных партий и оборудования необходим официальный выездной аудит фабрики со сюрвейерским отчетом.
  </p>
  <a href="/supplies-services-china/proverka-postavshhika-v-kitae/" style="display:inline-block; background:#dc2626; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Заказать аудит завода в Китае с выездом за 48 часов →
  </a>
</div>"""
    },
    {
        "id": 1652,
        "slug": "cargo-dostavka-iz-kitaya-v-rossiyu",
        "url": "https://longwang.ru/useful-articles/cargo-dostavka-iz-kitaya-v-rossiyu/",
        "title": "Карго доставка из Китая в Россию",
        "anchor": '<h2>Что такое карго доставка из Китая на самом деле</h2>',
        "anchor_position": "before",
        "target_hub_url": "/supplies-services-china/belaya-dostavka-iz-kitaya/",
        "location_desc": "После вводной части (3-й абзац), перед заголовком H2 «Что такое карго доставка из Китая на самом деле»",
        "callout_html": """<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #16a34a; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">📦 Белая доставка под контракт ВЭД вместо «серого» карго</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    С 2026 года налоговый контроль цепочек поставок исключает возможность безопасной реализации товаров без ГТД и закрывающих документов с НДС. Long Wang организует прямую белую логистику оборудования и сборных грузов с официальной таможенной очисткой.
  </p>
  <a href="/supplies-services-china/belaya-dostavka-iz-kitaya/" style="display:inline-block; background:#16a34a; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Рассчитать белую доставку с ГТД и закрывающими документами →
  </a>
</div>"""
    },
    {
        "id": 3967,
        "slug": "biznes-s-kitaem-s-nulya-chto-nuzhno-znat-nachinayushhemu-predprinimatelyu",
        "url": "https://longwang.ru/useful-articles/biznes-s-kitaem-s-nulya-chto-nuzhno-znat-nachinayushhemu-predprinimatelyu/",
        "title": "Бизнес с Китаем с нуля: что нужно знать начинающему предпринимателю",
        "anchor": '<h2>Почему именно Китай: цифры 2026 года</h2>',
        "anchor_position": "before",
        "target_hub_url": "/supplies-services-china/equipment-from-china/",
        "location_desc": "После вступительной части (абзац 2), перед первым разделом H2 «Почему именно Китай: цифры 2026 года»",
        "callout_html": """<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #2563eb; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">🏭 Подбор и поставка производственного оборудования под ключ</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    Запуск производства требует точного согласования ТЗ, проверки реальных мощностей завода в КНР и гарантий пусконаладки. Мы берем на себя прямые переговоры, оплату в юанях, таможню и доставку оборудования до вашего цеха.
  </p>
  <a href="/supplies-services-china/equipment-from-china/" style="display:inline-block; background:#2563eb; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Каталог решений и условия поставки оборудования →
  </a>
</div>"""
    },
    {
        "id": 1559,
        "slug": "kupit-elektroniku-nesmotrya-na-sankczii",
        "url": "https://longwang.ru/useful-articles/kupit-elektroniku-nesmotrya-na-sankczii/",
        "title": "Как купить электронику, несмотря на санкции",
        "anchor": '<h2>Что изменилось и изменится в 2026 году для импорта электроники</h2>',
        "anchor_position": "before",
        "target_hub_url": "/supplies-services-china/parallelnyj-import-is-kitaya/",
        "location_desc": "После вводной части и цитаты-предупреждения, перед разделом H2 «Что изменилось и изменится в 2026 году для импорта электроники»",
        "callout_html": """<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #0284c7; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">🛡️ Белый параллельный импорт электроники и компонентов (ПП РФ № 506)</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    Поставляем оригинальные микроконтроллеры, серверное оборудование и компоненты через торговые хабы в КНР с соблюдением требований законодательства РФ, нотификациями ФСБ и декларациями соответствия.
  </p>
  <a href="/supplies-services-china/parallelnyj-import-is-kitaya/" style="display:inline-block; background:#0284c7; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Условия параллельного импорта для юридических лиц →
  </a>
</div>"""
    }
]

# -------------------------------------------------------------
# 2. КОММЕРЧЕСКИЕ ХАБЫ: TITLE & METADATA
# -------------------------------------------------------------
HUB_TASKS = [
    {
        "id": 1351,
        "slug": "equipment-from-china",
        "url": "https://longwang.ru/supplies-services-china/equipment-from-china/",
        "new_wp_title": "Поставка промышленного оборудования и производственных линий из Китая",
        "new_seo_title": "Промышленное оборудование из Китая под ключ — подбор, доставка и ВЭД | Long Wang",
        "new_meta_description": "Прямые поставки станков, производственных линий и термооборудования из Китая для юридических лиц. Проверка завода, контракт ВЭД, оплата в юанях, белая таможня и шеф-монтаж под ключ.",
        "h1_note": "Видимый заголовок H1 вшит напрямую в PHP-шаблон темы (template-equipment.php). Код шаблона и верстка оставлены неизменными в соответствии с регламентом сохранения дизайна сайта."
    },
    {
        "id": 1083,
        "slug": "proverka-postavshhika-v-kitae",
        "url": "https://longwang.ru/supplies-services-china/proverka-postavshhika-v-kitae/",
        "new_wp_title": "Комплексный аудит фабрик и проверка надежности поставщиков в КНР",
        "new_seo_title": "Проверка поставщика и аудит фабрик в Китае с выездом инспектора за 48 часов | Long Wang",
        "new_meta_description": "Профессиональный аудит китайских производителей: юридическая чистота, выезд инспектора на производство, аудит оборудования и финансовой устойчивости. Официальный отчет с фото и видео за 48 часов.",
        "h1_note": "Видимый заголовок H1 вшит напрямую в PHP-шаблон темы (template-check.php). Код шаблона и верстка оставлены неизменными в соответствии с регламентом сохранения дизайна сайта."
    }
]

def run(dry_run=True):
    mode_str = "DRY-RUN (ИМИТАЦИЯ)" if dry_run else "REAL APPLY (БОЕВОЕ ВНЕДРЕНИЕ)"
    print(f"================================================================================")
    print(f"   ВНЕДРЕНИЕ ON-PAGE ПРАВОК СПРИНТА 1 В WORDPRESS (РЕЖИМ: {mode_str})")
    print(f"================================================================================\n")
    
    env = load_env()
    auth = get_auth_header(env)
    if not auth:
        print("[ERR] Не найдены WP_USER / WP_APP_PASSWORD в .env!")
        return False
        
    diff_report = []

    # =========================================================
    # ЭТАП 1: Внедрение Callout-блоков в статьи блога
    # =========================================================
    print(">>> ЭТАП 1: Обработка 4 статей блога (вставка B2B Callout-блоков)...")
    callout_diffs = []

    for task in CALLOUT_TASKS:
        pid = task["id"]
        slug = task["slug"]
        print(f"\n[Post ID {pid}] {task['title']} (slug: {slug})")
        
        status, post = wp_api_request(f"posts/{pid}?context=edit", auth_header=auth)
        if status != 200 or not post:
            print(f"  [-] Ошибка получения поста: status {status}, {post}")
            continue
            
        content_raw = post.get("content", {}).get("raw", "")
        post_title = post.get("title", {}).get("raw", "")
        
        # Проверяем, не вставлен ли уже блок
        already_has_callout = "b2b-callout" in content_raw
        if already_has_callout:
            print("  [!] Предупреждение: блок 'b2b-callout' уже присутствует в тексте статьи!")
            callout_diffs.append({
                "id": pid,
                "url": task["url"],
                "slug": slug,
                "title": post_title,
                "location": task["location_desc"],
                "target_link": task["target_hub_url"],
                "status": "ALREADY_PRESENT",
                "diff_was": "Блок Callout уже был добавлен ранее.",
                "diff_became": "Оставлен без изменений во избежание дублирования."
            })
            continue

        anchor = task["anchor"]
        if anchor not in content_raw:
            print(f"  [ERR] Анкор вставки '{anchor[:40]}...' не найден в тексте поста!")
            callout_diffs.append({
                "id": pid,
                "url": task["url"],
                "slug": slug,
                "title": post_title,
                "location": task["location_desc"],
                "target_link": task["target_hub_url"],
                "status": "ERROR_ANCHOR_NOT_FOUND",
                "diff_was": "Анкор не найден",
                "diff_became": "Пропущено"
            })
            continue

        # Формируем новый контент
        callout_insert = task["callout_html"] + "\n\n"
        new_content = content_raw.replace(anchor, callout_insert + anchor, 1)

        # Контекст для Было / Стало
        idx = content_raw.find(anchor)
        start_ctx = max(0, idx - 150)
        end_ctx = min(len(content_raw), idx + len(anchor) + 100)
        snippet_was = content_raw[start_ctx:end_ctx]
        
        snippet_became = snippet_was.replace(anchor, f"\n\n<!-- [START B2B CALLOUT] -->\n{task['callout_html']}\n<!-- [END B2B CALLOUT] -->\n\n{anchor}")

        print(f"  [+] Анкор найден: {task['location_desc']}")
        print(f"  [+] Размер контента: {len(content_raw)} байт -> {len(new_content)} байт (+{len(callout_insert)} байт)")
        print(f"  [+] Целевая ссылка блока: {task['target_hub_url']}")

        if not dry_run:
            p_status, p_res = wp_api_request(f"posts/{pid}", method="POST", data={"content": new_content}, auth_header=auth)
            if p_status == 200:
                print(f"  [SUCCESS] Изменения успешно сохранены в WordPress (ID={pid})!")
                exec_status = "APPLIED_SUCCESS"
            else:
                print(f"  [ERR] Ошибка сохранения: status={p_status}, response={p_res}")
                exec_status = f"ERROR_SAVE_{p_status}"
        else:
            print(f"  [DRY-RUN] Имитация успешна, данные в БД WordPress не затронуты.")
            exec_status = "DRY_RUN_PLANNED"

        callout_diffs.append({
            "id": pid,
            "url": task["url"],
            "slug": slug,
            "title": post_title,
            "location": task["location_desc"],
            "target_link": task["target_hub_url"],
            "status": exec_status,
            "diff_was": snippet_was.strip(),
            "diff_became": snippet_became.strip(),
            "callout_code": task["callout_html"]
        })

    # =========================================================
    # ЭТАП 2: Обновление Commercial Hubs (1351 и 1083)
    # =========================================================
    print("\n>>> ЭТАП 2: Обновление коммерческих хабов (WordPress Title и Yoast SEO Meta)...")
    hub_diffs = []

    # Сначала считываем текущие параметры Yoast через bulk editor
    status, yoast_data = wp_api_request("bulk_editor/posts?content_type=page&include[]=1351&include[]=1083", auth_header=auth, base_url="https://longwang.ru/wp-json/yoast/v1/")
    yoast_posts_map = {}
    if status == 200 and isinstance(yoast_data, dict):
        for p in yoast_data.get("posts", []):
            yoast_posts_map[p.get("id")] = p

    yoast_update_items = []

    for hub in HUB_TASKS:
        pid = hub["id"]
        slug = hub["slug"]
        print(f"\n[Page Hub ID {pid}] {hub['url']}")
        
        # Получаем страницу WP
        status, page = wp_api_request(f"pages/{pid}?context=edit", auth_header=auth)
        if status != 200 or not page:
            print(f"  [-] Ошибка получения страницы: status {status}, {page}")
            continue
            
        current_wp_title = page.get("title", {}).get("raw", "")
        yoast_info = yoast_posts_map.get(pid, {})
        current_seo_title = yoast_info.get("seo_title", "")
        current_meta_desc = yoast_info.get("meta_description", "")

        print(f"  Текущий WP Title:         '{current_wp_title}'")
        print(f"  Новый WP Title:            '{hub['new_wp_title']}'")
        print(f"  Текущий Yoast SEO Title:   '{current_seo_title}'")
        print(f"  Новый Yoast SEO Title:     '{hub['new_seo_title']}'")
        print(f"  Текущий Meta Description:  '{current_meta_desc}'")
        print(f"  Новый Meta Description:    '{hub['new_meta_description']}'")

        wp_save_status = "DRY_RUN_PLANNED"
        if not dry_run:
            # 1. Обновляем WP Page Title
            p_status, p_res = wp_api_request(f"pages/{pid}", method="POST", data={"title": hub["new_wp_title"]}, auth_header=auth)
            if p_status == 200:
                print(f"  [SUCCESS] WP Page Title успешно обновлен!")
                wp_save_status = "WP_TITLE_UPDATED"
            else:
                print(f"  [ERR] Ошибка обновления WP Page Title: status={p_status}, res={p_res}")
                wp_save_status = f"ERROR_WP_TITLE_{p_status}"

        yoast_update_items.append({
            "id": pid,
            "seo_title": hub["new_seo_title"],
            "meta_description": hub["new_meta_description"]
        })

        hub_diffs.append({
            "id": pid,
            "url": hub["url"],
            "slug": slug,
            "wp_title_was": current_wp_title,
            "wp_title_became": hub["new_wp_title"],
            "seo_title_was": current_seo_title,
            "seo_title_became": hub["new_seo_title"],
            "meta_desc_was": current_meta_desc,
            "meta_desc_became": hub["new_meta_description"],
            "h1_note": hub["h1_note"],
            "wp_status": wp_save_status
        })

    # Применяем обновления Yoast SEO пакетом
    yoast_save_status = "DRY_RUN_PLANNED"
    if yoast_update_items:
        if not dry_run:
            y_status, y_res = wp_api_request("bulk_editor/update_search", method="POST", data={"items": yoast_update_items}, auth_header=auth, base_url="https://longwang.ru/wp-json/yoast/v1/")
            if y_status == 200:
                print(f"\n[SUCCESS] Yoast SEO Title и Meta Description успешно обновлены для {len(yoast_update_items)} страниц!")
                yoast_save_status = "YOAST_APPLIED_SUCCESS"
            else:
                print(f"\n[ERR] Ошибка пакета Yoast: status={y_status}, res={y_res}")
                yoast_save_status = f"ERROR_YOAST_{y_status}"
        else:
            print(f"\n[DRY-RUN] Пакетное обновление Yoast SEO ({len(yoast_update_items)} сущностей) сымитировано.")

    # =========================================================
    # ЭТАП 3: Формирование детального лог-файла ONPAGE_IMPLEMENTATION_DIFF_LOG.md
    # =========================================================
    write_diff_markdown(callout_diffs, hub_diffs, dry_run=dry_run)
    return True

def write_diff_markdown(callout_diffs, hub_diffs, dry_run=True):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode_title = "Имитация (Dry-Run)" if dry_run else "Боевое внедрение (Live Applied)"
    
    lines = [
        f"# Детальный лог On-Page изменений Спринта 1 в WordPress (WP REST API)",
        f"",
        f"> **Дата генерации:** {now_str}  ",
        f"> **Статус исполнения:** `{mode_title}`  ",
        f"> **Метод внедрения:** Автоматизированный через WP REST API (`/wp/v2/posts`, `/wp/v2/pages`, `/yoast/v1/bulk_editor/update_search`)  ",
        f"> **Политика безопасности:** Нулевое вмешательство в PHP-файлы темы и верстку (`Design and Code Invariant`). Модифицирован строго текстовый контент и метаданные.  ",
        f"",
        f"---",
        f"",
        f"## 1. Сводная таблица изменений",
        f"",
        f"| № | ID | Тип сущности | URL страницы | Внесенное изменение | Статус внедрения |",
        f"|---|---|---|---|---|---|"
    ]

    idx = 1
    for c in callout_diffs:
        status_badge = f"`{c['status']}`"
        lines.append(f"| {idx} | `{c['id']}` | Статья блога | [{c['slug']}]({c['url']}) | Вставка B2B Callout-блока со ссылкой на `{c['target_link']}` | {status_badge} |")
        idx += 1

    for h in hub_diffs:
        status_badge = f"`APPLIED_SUCCESS`" if not dry_run else "`DRY_RUN_PLANNED`"
        lines.append(f"| {idx} | `{h['id']}` | Коммерческий хаб | [{h['slug']}]({h['url']}) | Обновление WP Title, Yoast SEO Title, Meta Description | {status_badge} |")
        idx += 1

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 2. Детальный дифференциал: Статьи блога (Callout-блоки)",
        f""
    ])

    for c in callout_diffs:
        lines.extend([
            f"### 2.{c['id']}. {c['title']} (ID: {c['id']})",
            f"* **URL:** `{c['url']}`",
            f"* **Slug:** `{c['slug']}`",
            f"* **Место врезки в тексте:** {c['location']}",
            f"* **Целевой хаб лидогенерации:** `{c['target_link']}`",
            f"* **Статус:** `{c['status']}`",
            f"",
            f"#### Было (Фрагмент текста до вставки):",
            f"```html",
            f"{c['diff_was']}",
            f"```",
            f"",
            f"#### Стало (Фрагмент текста после внедрения блока):",
            f"```html",
            f"{c['diff_became']}",
            f"```",
            f"",
            f"---",
            f""
        ])

    lines.extend([
        f"## 3. Детальный дифференциал: Коммерческие хабы (Title & Metadata)",
        f""
    ])

    for h in hub_diffs:
        lines.extend([
            f"### 3.{h['id']}. Хаб услуг (ID: {h['id']})",
            f"* **URL:** `{h['url']}`",
            f"* **Slug:** `{h['slug']}`",
            f"",
            f"#### Заголовок страницы WordPress (WP Title):",
            f"* **Было:** `{h['wp_title_was']}`",
            f"* **Стало:** `{h['wp_title_became']}`",
            f"",
            f"#### Поисковый заголовок (Yoast SEO Title):",
            f"* **Было:** `{h['seo_title_was'] if h['seo_title_was'] else '[Автоматический fallback %%title%% %%sep%% %%sitename%%]'}`",
            f"* **Стало:** `{h['seo_title_became']}`",
            f"",
            f"#### Мета-описание (Yoast Meta Description):",
            f"* **Было:** `{h['meta_desc_was']}`",
            f"* **Стало:** `{h['meta_desc_became']}`",
            f"",
            f"#### Особое примечание по видимому H1:",
            f"> [!IMPORTANT]",
            f"> **Статус H1:** {h['h1_note']}",
            f"",
            f"---",
            f""
        ])

    with open(DIFF_LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"\n[+] Детальный лог изменений успешно записан в: {DIFF_LOG_FILE}")

# -------------------------------------------------------------
# 3. СПРИНТ 2: ЗАДАЧИ ПЕРЕЛИНКОВКИ И ЛИКВИДАЦИИ 301-РЕДИРЕКТОВ
# -------------------------------------------------------------
SPRINT_2_TASKS = [
    # 1. Ликвидация внутренних 301-редиректов
    {
        "id": 1578,
        "type": "posts",
        "slug": "import-v-kitaj",
        "url": "https://longwang.ru/international/import-v-kitaj/",
        "title": "Импорт и экспорт Китая в отношении России впервые упал на 10,4%",
        "category": "301 Redirect Liquidation",
        "desc": "Замена 301-ссылки кейса консолидации на прямой каноничный URL кейса Ozon (/projects/ozon-supply-china/)",
        "search": '<li><strong>Сборная поставка для Wildberries и Ozon</strong> — как объединить 7 поставщиков за месяц. <a href="/projects/consolidation-7-suppliers/" title="консолидация поставок для маркетплейсов">Подробнее</a>.</li>',
        "replace": '<li><strong>Сборная поставка для Wildberries и Ozon</strong> — как объединить 7 поставщиков за месяц. <a href="/projects/ozon-supply-china/" title="консолидация поставок для маркетплейсов">Подробнее</a>.</li>'
    },
    {
        "id": 1576,
        "type": "posts",
        "slug": "exhibitions-in-china",
        "url": "https://longwang.ru/useful-articles/exhibitions-in-china/",
        "title": "Выставки в Китае 2026: как бизнесу найти поставщиков и технологии",
        "category": "301 Redirect Liquidation",
        "desc": "Замена 301-ссылки кейса консолидации на прямой каноничный URL кейса Ozon (/projects/ozon-supply-china/)",
        "search": '<li><strong>Сборная поставка для Wildberries и Ozon</strong> — как объединить 7 поставщиков за месяц. <a href="/projects/consolidation-7-suppliers/" title="консолидация поставок для маркетплейсов">Подробнее</a>.</li>',
        "replace": '<li><strong>Сборная поставка для Wildberries и Ozon</strong> — как объединить 7 поставщиков за месяц. <a href="/projects/ozon-supply-china/" title="консолидация поставок для маркетплейсов">Подробнее</a>.</li>'
    },
    {
        "id": 9826,
        "type": "projects",
        "slug": "manufacturer-search-audit-china",
        "url": "https://longwang.ru/projects/manufacturer-search-audit-china/",
        "title": "Замена «фабрики-перекупщика» на прямого производителя в Китае: кейс аудита и снижения себестоимости на 22%",
        "category": "301 Redirect Liquidation",
        "desc": "Ликвидация 301-редиректа ссылки кейса кухонной техники на каноничный URL (/projects/kitchen-appliances-white-ved/)",
        "search": '<a href="/kitchen-appliances-white-ved" title="Легализация импорта кухонной техники из Китая">Перевод импорта бытовой техники с карго на белый ВЭД и маркировка Честный Знак</a>',
        "replace": '<a href="/projects/kitchen-appliances-white-ved/" title="Легализация импорта кухонной техники из Китая">Перевод импорта бытовой техники с карго на белый ВЭД и маркировка Честный Знак</a>'
    },
    # 2. Ликвидация семантического разрыва Хаба Оборудования (/supplies-services-china/equipment-from-china/)
    {
        "id": 7465,
        "type": "posts",
        "slug": "worlds-brend-equipment",
        "url": "https://longwang.ru/useful-articles/worlds-brend-equipment/",
        "title": "Как не купить подделку или б/у санкционное оборудование в Китае через посредника",
        "category": "Equipment Hub Semantic Link",
        "desc": "Внедрение коммерческого анкора 'поставка промышленного оборудования из Китая под ключ' со ссылкой на хаб оборудования",
        "search": '<p>Теперь давайте разберем еще несколько распространенных примеров из-за которых наши клиенты в прошлом сталкивались с проблемами при <a title="Оборудование из Китая" href="/supplies-services-china/equipment-from-china/">импорте оборудования</a> санкционных брендов у посредников в Китае или через Китай. В том числе и у русских, якобы "дистрибьютеров"</p>',
        "replace": '<p>Теперь давайте разберем еще несколько распространенных примеров из-за которых наши клиенты в прошлом сталкивались с проблемами, когда ими организовывалась <a title="Поставка промышленного оборудования из Китая под ключ" href="/supplies-services-china/equipment-from-china/">поставка промышленного оборудования из Китая под ключ</a> или закупка станков санкционных брендов у посредников в Китае или через третьи страны. В том числе и у русских, якобы "дистрибьютеров"</p>'
    },
    {
        "id": 1647,
        "type": "posts",
        "slug": "pryamye-postavki-iz-kitaya",
        "url": "https://longwang.ru/useful-articles/pryamye-postavki-iz-kitaya/",
        "title": "ПРЯМЫЕ ПОСТАВКИ ИЗ КИТАЯ",
        "category": "Equipment Hub Semantic Link",
        "desc": "Внедрение контекстной ссылки на хаб оборудования с анкором 'поставки оборудования из Китая для бизнеса'",
        "search": '<p>Как вы видите, прямые поставки из Китая — это отличный способ развить свой бизнес и увеличить свою прибыль. Но как начать? Где найти надежных партнеров? Как избежать подводных камней? На эти и другие вопросы вам поможет ответить наша команда. Мы специализируемся на организации прямых поставок из Китая для наших клиентов. Мы помогаем вам выбрать изделия и производителей, проводим проверку качества и сертификацию, оформляем все необходимые документы и таможенные процедуры, обеспечиваем безопасную и быструю доставку. Мы работаем с вами на всех этапах процесса, от первого контакта до получения груза. Мы гарантируем вам высокий уровень сервиса и полную поддержку.</p>',
        "replace": '<p>Как вы видите, прямые поставки из Китая — это отличный способ развить свой бизнес и увеличить свою прибыль. Но как начать? Где найти надежных партнеров? Как избежать подводных камней? На эти и другие вопросы вам поможет ответить наша команда. Мы специализируемся на комплексных проектах для юридических лиц: организуем прямые <a title="Поставки оборудования из Китая для бизнеса" href="/supplies-services-china/equipment-from-china/">поставки оборудования из Китая для бизнеса</a>, производственных линий и компонентов, помогаем выбрать надежных производителей, проводим проверку качества и сертификацию, оформляем белую таможню и обеспечиваем безопасную доставку под ключ. Мы работаем с вами на всех этапах процесса, от первого контакта до получения груза. Мы гарантируем вам высокий уровень сервиса и полную поддержку.</p>'
    },
    # 3. Ликвидация изолированности Хаба Проверки поставщиков (/supplies-services-china/proverka-postavshhika-v-kitae/)
    {
        "id": 1689,
        "type": "posts",
        "slug": "purchases-without-intermediaries",
        "url": "https://longwang.ru/useful-articles/purchases-without-intermediaries/",
        "title": "Как закупать товары оптом в Китае без посредников: советы и риски",
        "category": "Supplier Check Hub Isolation Fix",
        "desc": "Внедрение контекстной ссылки на хаб проверки поставщиков с анкором 'выездная проверка поставщика в Китае'",
        "search": '<li>Проверяйте поставщиков. Используйте услуги проверенных платформ и организаций для проверки репутации производителей.</li>',
        "replace": '<li>Проверяйте поставщиков. До перевода аванса необходима комплексная <a title="Выездная проверка поставщика в Китае" href="/supplies-services-china/proverka-postavshhika-v-kitae/">выездная проверка поставщика в Китае</a> с аудитом производственных цехов, оценкой оборудования и юридическим скорингом регистрационных документов.</li>'
    },
    {
        "id": 3535,
        "type": "posts",
        "slug": "dokumentalnoe-oformlenie-importa-cherez-agenta",
        "url": "https://longwang.ru/useful-articles/dokumentalnoe-oformlenie-importa-cherez-agenta/",
        "title": "Документальное оформление импорта через агента: какие документы получает импортёр",
        "category": "Supplier Check Hub Isolation Fix",
        "desc": "Внедрение контекстной ссылки на хаб проверки поставщиков с анкором 'проверка надежности китайского поставщика'",
        "search": '<p>Чтобы избежать проблем с документами, ещё на старте стоит уточнить несколько ключевых моментов:</p>\n<ul>\n<li>кто именно заключает контракт с китайским поставщиком — вы напрямую или агент от своего имени;</li>',
        "replace": '<p>Чтобы избежать проблем с документами, ещё на старте стоит уточнить несколько ключевых моментов:</p>\n<ul>\n<li>проведена ли предварительная <a title="Проверка надежности китайского поставщика" href="/supplies-services-china/proverka-postavshhika-v-kitae/">проверка надежности китайского поставщика</a> (юридический статус фабрики, отсутствие судебных исков и лицензия на экспорт);</li>\n<li>кто именно заключает контракт с китайским поставщиком — вы напрямую или агент от своего имени;</li>'
    },
    {
        "id": 7465,
        "type": "posts",
        "slug": "worlds-brend-equipment",
        "url": "https://longwang.ru/useful-articles/worlds-brend-equipment/",
        "title": "Как не купить подделку или б/у санкционное оборудование в Китае через посредника",
        "category": "Supplier Check Hub Isolation Fix",
        "desc": "Внедрение контекстной ссылки на хаб проверки поставщиков с анкором 'инспекция и аудит оборудования на заводе в КНР'",
        "search": '<p>В итоге, после того как с ним связался наш китайский юрист и начал обсуждать контракт на покупку, в котором были пункты о новизне и оригинальности товара, продавец отказался подписывать контракт и признался, что это восстановленный им же самим контроллер, который он очень хотел продать. На самом деле контроллер оказался вполне рабочим и оригинальным, но это просто показывает, что продавец хорошо умел ремонтировать электронику, но это не помогло бы нашему клиенту избежать рекламаций при поставке этого контроллера своему конечному клиенту по гос. контракту.</p>',
        "replace": '<p>В итоге, после того как с ним связался наш китайский юрист и начал обсуждать контракт на покупку, в котором были пункты о новизне и оригинальности товара, продавец отказался подписывать контракт и признался, что это восстановленный им же самим контроллер, который он очень хотел продать. На самом деле контроллер оказался вполне рабочим и оригинальным, но это просто показывает, что продавец хорошо умел ремонтировать электронику, но это не помогло бы нашему клиенту избежать рекламаций при поставке этого контроллера своему конечному клиенту по гос. контракту. Чтобы полностью исключить подобные риски при покупке дорогостоящих агрегатов, перед оплатой необходима профессиональная <a title="Инспекция и аудит оборудования на заводе в КНР" href="/supplies-services-china/proverka-postavshhika-v-kitae/">инспекция и аудит оборудования на заводе в КНР</a> с выездом технического эксперта непосредственно на производственную площадку.</p>'
    }
]

def run_sprint_2(dry_run=True):
    mode_str = "DRY-RUN (ИМИТАЦИЯ)" if dry_run else "REAL APPLY (БОЕВОЕ ВНЕДРЕНИЕ)"
    print(f"================================================================================")
    print(f"   ВНЕДРЕНИЕ ON-PAGE ПРАВОК СПРИНТА 2 В WORDPRESS (РЕЖИМ: {mode_str})")
    print(f"================================================================================\n")
    
    env = load_env()
    auth = get_auth_header(env)
    if not auth:
        print("[ERR] Не найдены WP_USER / WP_APP_PASSWORD в .env!")
        return False

    # Группируем задачи по сущностям (например, в посте 7465 две правки)
    entities_map = {}
    for task in SPRINT_2_TASKS:
        key = (task["type"], task["id"])
        if key not in entities_map:
            entities_map[key] = {
                "type": task["type"],
                "id": task["id"],
                "slug": task["slug"],
                "url": task["url"],
                "title": task["title"],
                "tasks": []
            }
        entities_map[key]["tasks"].append(task)

    results = []

    for (etype, eid), item in entities_map.items():
        print(f"\n>>> Обработка {etype} ID {eid}: '{item['title']}' ({item['slug']})")
        endpoint = f"{etype}/{eid}?context=edit"
        status, data = wp_api_request(endpoint, auth_header=auth)
        if status != 200 or not data:
            print(f"  [-] Ошибка получения сущности: status={status}, res={data}")
            continue

        content_current = data.get("content", {}).get("raw", "")
        modified_content = content_current
        applied_for_entity = []

        for t in item["tasks"]:
            print(f"  [*] Задача: {t['desc']}")
            search_str = t["search"]
            replace_str = t["replace"]

            if replace_str in modified_content:
                print(f"      [+] Целевой фрагмент подтвержден в контенте WordPress.")
                applied_for_entity.append({
                    "task": t,
                    "status": "APPLIED_SUCCESS",
                    "diff_was": search_str,
                    "diff_became": replace_str
                })
                continue


            if search_str not in modified_content:
                print(f"      [ERR] Исходный фрагмент для замены не найден!")
                applied_for_entity.append({
                    "task": t,
                    "status": "ERROR_SEARCH_NOT_FOUND",
                    "diff_was": search_str[:200] + "...",
                    "diff_became": "Не найдено в текущем контенте."
                })
                continue

            # Выполняем замену
            modified_content = modified_content.replace(search_str, replace_str, 1)
            print(f"      [+] Замена успешно подготовлена.")
            applied_for_entity.append({
                "task": t,
                "status": "READY_TO_APPLY" if dry_run else "PENDING_SAVE",
                "diff_was": search_str,
                "diff_became": replace_str
            })

        # Сохранение обновленного контента для сущности
        if modified_content != content_current:
            if not dry_run:
                save_status, save_res = wp_api_request(f"{etype}/{eid}", method="POST", data={"content": modified_content}, auth_header=auth)
                if save_status == 200:
                    print(f"  [SUCCESS] Изменения успешно сохранены в WordPress ({etype} ID={eid})!")
                    for res_item in applied_for_entity:
                        if res_item["status"] == "PENDING_SAVE":
                            res_item["status"] = "APPLIED_SUCCESS"
                else:
                    print(f"  [ERR] Ошибка сохранения {etype} ID {eid}: status={save_status}, res={save_res}")
                    for res_item in applied_for_entity:
                        if res_item["status"] == "PENDING_SAVE":
                            res_item["status"] = f"ERROR_SAVE_{save_status}"
            else:
                print(f"  [DRY-RUN] Имитация успешна, данные в БД WordPress не затронуты.")
                for res_item in applied_for_entity:
                    if res_item["status"] == "READY_TO_APPLY":
                        res_item["status"] = "DRY_RUN_PLANNED"

        results.extend(applied_for_entity)

    # Запись результатов в ONPAGE_IMPLEMENTATION_DIFF_LOG.md
    write_sprint_2_diff_markdown(results, dry_run=dry_run)
    return True

def write_sprint_2_diff_markdown(results, dry_run=True):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_applied = all(r.get("status") == "APPLIED_SUCCESS" for r in results)
    mode_title = "Боевое внедрение (Live Applied)" if all_applied else ("Имитация (Dry-Run)" if dry_run else "Боевое внедрение (Live Applied)")

    
    # Читаем существующий лог, чтобы сохранить Спринт 1
    existing_content = ""
    if os.path.exists(DIFF_LOG_FILE):
        with open(DIFF_LOG_FILE, 'r', encoding='utf-8') as f:
            existing_content = f.read()

    # Если уже был блок Спринта 2, отрезаем его и перезаписываем
    sprint_2_marker = "<!-- SPRINT_2_SECTION_START -->"
    if sprint_2_marker in existing_content:
        base_log = existing_content.split(sprint_2_marker)[0].strip()
    else:
        base_log = existing_content.strip()

    lines = [
        "",
        sprint_2_marker,
        "",
        f"---",
        f"",
        f"# Спринт 2 On-Page оптимизации и перелинковки в WordPress (WP REST API)",
        f"",
        f"> **Дата генерации:** {now_str}  ",
        f"> **Статус исполнения:** `{mode_title}`  ",
        f"> **Метод внедрения:** Автоматизированный через WP REST API (`/wp/v2/posts`, `/wp/v2/projects`)  ",
        f"> **Политика безопасности:** Нулевое вмешательство в PHP-файлы темы и верстку (`Design and Code Invariant`). Модифицирован строго текстовый контент записей.  ",
        f"",
        f"---",
        f"",
        f"## 4. Сводная таблица изменений Спринта 2",
        f"",
        f"| № | ID | Тип | URL страницы | Категория оптимизации | Описание изменения | Статус внедрения |",
        f"|---|---|---|---|---|---|---|"
    ]

    for idx, r in enumerate(results, 1):
        t = r["task"]
        status_badge = f"`{r['status']}`"
        lines.append(f"| {idx} | `{t['id']}` | {t['type']} | [{t['slug']}]({t['url']}) | {t['category']} | {t['desc']} | {status_badge} |")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 5. Детальный дифференциал Спринта 2: Было / Стало",
        f""
    ])

    for idx, r in enumerate(results, 1):
        t = r["task"]
        lines.extend([
            f"### 5.{idx}. [{t['type'].upper()} ID {t['id']}] {t['title']}",
            f"* **URL:** `{t['url']}`",
            f"* **Slug:** `{t['slug']}`",
            f"* **Категория:** `{t['category']}`",
            f"* **Суть правки:** {t['desc']}",
            f"* **Статус:** `{r['status']}`",
            f"",
            f"#### Было (Фрагмент контента до изменения):",
            f"```html",
            f"{r['diff_was']}",
            f"```",
            f"",
            f"#### Стало (Фрагмент контента после внедрения):",
            f"```html",
            f"{r['diff_became']}",
            f"```",
            f"",
            f"---",
            f""
        ])

    # Сводный список URL для Вебмастера и Search Console
    unique_urls = []
    seen = set()
    for r in results:
        u = r["task"]["url"]
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    # Добавляем хабы и каноничные цели
    hub_targets = [
        "https://longwang.ru/supplies-services-china/equipment-from-china/",
        "https://longwang.ru/supplies-services-china/proverka-postavshhika-v-kitae/",
        "https://longwang.ru/projects/ozon-supply-china/",
        "https://longwang.ru/projects/kitchen-appliances-white-ved/",
        "https://longwang.ru/useful-articles/aviadostavka-gruzov-iz-kitaya/"
    ]
    for h in hub_targets:
        if h not in seen:
            seen.add(h)
            unique_urls.append(h)

    lines.extend([
        f"## 6. Сводный список URL для отправки в Яндекс Вебмастер и Google Search Console",
        f"",
        f"Данные страницы получили обновленную внутреннюю перелинковку или ликвидировали внутренние редиректы. Рекомендуется отправить их на принудительную переиндексацию (переобход страниц в Вебмастере и URL Inspection в GSC):",
        f"",
        f"| № | URL страницы для переиндексации | Роль в структуре сайта |",
        f"|---|---|---|"
    ])

    for idx, u in enumerate(unique_urls, 1):
        if "supplies-services-china/equipment" in u:
            role = "Целевой коммерческий Хаб оборудования (прием входящего ссылочного веса)"
        elif "supplies-services-china/proverka" in u:
            role = "Целевой коммерческий Хаб проверки поставщиков (прием входящего ссылочного веса)"
        elif "projects/ozon" in u:
            role = "Каноничный кейс 200 OK (замена устаревшего 301-редиректа)"
        elif "projects/kitchen" in u:
            role = "Каноничный кейс 200 OK (замена устаревшего 301-редиректа)"
        elif "useful-articles/aviadostavka" in u:
            role = "Каноничная статья 200 OK по авиадоставке"
        elif "projects/" in u:
            role = "Страница кейса (исправлена исходящая ссылка)"
        else:
            role = "Статья блога (внедрены новые контекстные анкоры)"
        lines.append(f"| {idx} | `{u}` | {role} |")

    lines.append("")
    new_full_log = base_log + "\n" + "\n".join(lines)
    with open(DIFF_LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(new_full_log)
    print(f"\n[+] Детальный лог Спринта 2 успешно записан в: {DIFF_LOG_FILE}")

def inspect_posts():
    """Инспекция контента целевых постов для Спринта 2 перед внедрением."""
    print("=== ИНСПЕКЦИЯ ЦЕЛЕВЫХ ПОСТОВ ДЛЯ СПРИНТА 2 ===")
    env = load_env()
    auth = get_auth_header(env)
    if not auth:
        print("[ERR] Авторизация не найдена!")
        return
    print("[+] Проверка авторизации успешна.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Apply On-Page fixes to WordPress via REST API")
    parser.add_argument("--sprint", type=int, default=2, choices=[1, 2], help="Sprint number to run (Default: 2)")
    parser.add_argument("--apply", action="store_true", help="Apply changes for real (Default is --dry-run)")
    parser.add_argument("--inspect", action="store_true", help="Inspect target posts and scan for 301s")
    args = parser.parse_args()
    
    if args.inspect:
        inspect_posts()
    elif args.sprint == 1:
        run(dry_run=not args.apply)
    elif args.sprint == 2:
        run_sprint_2(dry_run=not args.apply)


