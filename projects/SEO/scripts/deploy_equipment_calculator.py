#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical Deployment Pipeline for Longwang Equipment Customs Calculator
Target Page: /supplies-services-china/equipment-from-china/
Mode: Supports --dry-run (default) and --execute.
"""

import os
import sys
import json
import re
import argparse
import urllib.request
import base64

sys.stdout.reconfigure(encoding='utf-8')

def load_wp_config():
    config = {
        "WP_URL": "https://longwang.ru",
        "WP_USER": "",
        "WP_APP_PASSWORD": ""
    }
    env_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
        ".env"
    ]
    for p in env_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k in config and not config[k]:
                            config[k] = v
    for k in config:
        if os.environ.get(k):
            config[k] = os.environ.get(k)
    return config

def get_page_by_slug(wp_url: str, slug: str, auth_header: str) -> dict:
    url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/pages?slug={slug}&context=edit"
    req = urllib.request.Request(url, headers={
        "User-Agent": "LongwangDeployer/2.0",
        "Authorization": auth_header
    })
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and isinstance(data, list):
                return data[0]
    except Exception as e:
        print(f"[-] Ошибка получения страницы WP: {e}")
    return {}

def run_deployment(dry_run: bool = True):
    print("=" * 80)
    print("=== ДЕПЛОЙ B2B-КАЛЬКУЛЯТОРА НА ХАБ /equipment-from-china/ ===")
    print(f"Режим: {'DRY-RUN (Холостой прогон / Безопасная симуляция)' if dry_run else 'EXECUTE (Боевое обновление WordPress)'}")
    print("=" * 80)

    # 1. Read Widget HTML
    widget_path = os.path.join(os.path.dirname(__file__), "..", "widgets", "equipment_calculator.html")
    if not os.path.exists(widget_path):
        print(f"[-] Файл виджета не найден: {widget_path}")
        return

    with open(widget_path, "r", encoding="utf-8") as f:
        widget_html = f.read()
    print(f"[+] Виджет загружен: {widget_path} ({len(widget_html)} байт)")

    # 2. Connect to WordPress
    cfg = load_wp_config()
    if not cfg["WP_USER"] or not cfg["WP_APP_PASSWORD"]:
        print("[-] Учетные данные WordPress (WP_USER / WP_APP_PASSWORD) не найдены в .env!")
        return

    creds = f"{cfg['WP_USER']}:{cfg['WP_APP_PASSWORD']}"
    auth_header = f"Basic {base64.b64encode(creds.encode('utf-8')).decode('utf-8')}"

    print("[*] Поиск страницы хаба 'equipment-from-china' в WordPress REST API...")
    page = get_page_by_slug(cfg["WP_URL"], "equipment-from-china", auth_header)
    if not page:
        print("[-] Страница 'equipment-from-china' не найдена в WordPress!")
        return

    page_id = page.get("id")
    page_title = page.get("title", {}).get("rendered", "")
    content = page.get("content", {}).get("raw") or page.get("content", {}).get("rendered", "")
    print(f"[+] Найдена страница [ID={page_id}]: «{page_title}»")
    print(f"    Текущая длина контента: {len(content)} символов")

    # 3. Check if widget already installed
    if 'id="lw-calculator-widget"' in content:
        print("[!] Виджет уже установлен на этой странице. Будет произведено обновление блока.")
        new_content = re.sub(
            r'<!-- B2B EQUIPMENT CUSTOMS & DELIVERY CALCULATOR.*?</script>',
            widget_html,
            content,
            flags=re.DOTALL
        )
    else:
        # Find anchor for insertion: before <h2>Стоимость работы</h2> or before <h2>Поставка и импорт</h2>
        anchor = "<h2>Стоимость работы</h2>"
        if anchor in content:
            print(f"[+] Найдена якорная точка вставки: '{anchor}'")
            new_content = content.replace(anchor, f"{widget_html}\n\n{anchor}")
        else:
            # Fallback anchor: before Contact/FAQ form
            alt_anchor = "<h2>Часто задаваемые вопросы</h2>"
            if alt_anchor in content:
                print(f"[+] Найдена альтернативная точка вставки: '{alt_anchor}'")
                new_content = content.replace(alt_anchor, f"{widget_html}\n\n{alt_anchor}")
            else:
                print("[+] Якорные заголовки не найдены, виджет будет добавлен в конец контента")
                new_content = f"{content}\n\n{widget_html}"

    print(f"[+] Новый размер контента страницы: {len(new_content)} символов (+{len(new_content) - len(content)})")

    if dry_run:
        print("\n" + "=" * 80)
        print("[DRY-RUN SUCCESS] Симуляция завершена успешно!")
        print("- Авторизация WP REST API: Подтверждена")
        print(f"- Целевой пост ID: {page_id}")
        print("- Точка интеграции: Перед блоком 'Стоимость работы'")
        print("- Боевое обновление страницы пропущено (для применения запустите с флагом --execute)")
        print("=" * 80)
        return

    # Execute update via WP REST API
    update_url = f"{cfg['WP_URL'].rstrip('/')}/wp-json/wp/v2/pages/{page_id}"
    payload = json.dumps({"content": new_content}).encode('utf-8')
    req = urllib.request.Request(
        update_url,
        data=payload,
        headers={
            "User-Agent": "LongwangDeployer/2.0",
            "Content-Type": "application/json",
            "Authorization": auth_header
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            print(f"[+] Страница [ID={page_id}] успешно обновлена в боевом WordPress!")
            print(f"    URL: {res_json.get('link')}")
    except Exception as e:
        print(f"[-] Ошибка обновления страницы WordPress: {e}")

def main():
    parser = argparse.ArgumentParser(description="Deploy Equipment Calculator to WordPress")
    parser.add_argument('--execute', action='store_true', help="Execute real update to WordPress (default is dry-run)")
    args = parser.parse_args()

    run_deployment(dry_run=not args.execute)

if __name__ == '__main__':
    main()
