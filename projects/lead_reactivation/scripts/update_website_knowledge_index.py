#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/lead_reactivation/scripts/update_website_knowledge_index.py
===================================================================
Канонический скрипт краулинга и актуализации базы знаний сайта Long Wang:
1. Сканирует разделы:
   - Полезные статьи: https://longwang.ru/useful-articles/
   - Проекты и кейсы: https://longwang.ru/projects/
   - Или sitemap.xml: https://longwang.ru/sitemap.xml
2. Извлекает мета-атрибуты: URL, Title, Description, H1.
3. Сверяет со существующим индексом 96_articles_index.md.
4. Добавляет новые публикации и актуализирует существующие без потери данных.
5. Поддерживает строгий режим --dry-run.

Регламенты: AGENTS.md, token_guard, LEAD_REACTIVATION_POLICY.md.
"""

import os
import sys
import re
import argparse
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import requests
from html import unescape

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AntigravityKnowledgeBot/1.0"
HEADERS = {"User-Agent": USER_AGENT}

DEFAULT_INDEX_PATH = r"C:\Codex\projects\n8n_email_ai\kb_leads_v1\96_articles_index.md"
TARGET_PREFIXES = ["https://longwang.ru/useful-articles/", "https://longwang.ru/projects/"]


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)
    # Удаляем символы пайпа | чтобы не ломать markdown-таблицу
    text = text.replace("|", "/")
    return text.strip()


def extract_meta_from_html(html: str, url: str) -> dict:
    """Извлекает Title, H1 и Description из HTML разметки"""
    # Title
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = clean_text(title_match.group(1)) if title_match else ""

    # H1
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    h1 = ""
    if h1_match:
        # Убираем внутренние теги
        h1_raw = re.sub(r"<[^>]+>", "", h1_match.group(1))
        h1 = clean_text(h1_raw)
    if not h1:
        h1 = title

    # Description
    desc = ""
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE | re.DOTALL)
    if not desc_match:
        desc_match = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*name=["\']description["\']', html, re.IGNORECASE | re.DOTALL)
    if desc_match:
        desc = clean_text(desc_match.group(1))
    
    # Fallback description из первого абзаца если meta пустая
    if not desc:
        p_match = re.search(r"<p[^>]*>(.*?)</p>", html, re.IGNORECASE | re.DOTALL)
        if p_match:
            p_raw = re.sub(r"<[^>]+>", "", p_match.group(1))
            desc = clean_text(p_raw)[:150]

    return {
        "url": url,
        "title": title[:160],
        "desc": desc[:180],
        "h1": h1[:160]
    }


def discover_urls_from_sitemap(sitemap_url: str = "https://longwang.ru/sitemap.xml") -> list:
    """Пытается получить URL из sitemap.xml"""
    discovered = []
    try:
        r = requests.get(sitemap_url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            # namespaces
            ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            # Check sitemapindex or urlset
            locs = root.findall(".//ns:loc", ns) or root.findall(".//loc")
            for loc in locs:
                url = loc.text.strip() if loc.text else ""
                if any(url.startswith(prefix) for prefix in TARGET_PREFIXES):
                    # Исключаем сами корневые листинги
                    if url.rstrip('/') not in ["https://longwang.ru/useful-articles", "https://longwang.ru/projects"]:
                        discovered.append(url)
    except Exception as e:
        print(f"  [SITEMAP-WARN] Не удалось разобрать sitemap ({sitemap_url}): {e}")
    return sorted(list(set(discovered)))


def discover_urls_from_html_listing(listing_url: str) -> list:
    """Извлекает ссылки из страницы листинга статей или проектов"""
    discovered = []
    try:
        r = requests.get(listing_url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            html = r.text
            # Ищем все ссылки a href
            hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
            for href in hrefs:
                full_url = urljoin(listing_url, href).split("?")[0].split("#")[0]
                if any(full_url.startswith(prefix) for prefix in TARGET_PREFIXES):
                    if full_url.rstrip('/') not in ["https://longwang.ru/useful-articles", "https://longwang.ru/projects"]:
                        discovered.append(full_url)
    except Exception as e:
        print(f"  [LISTING-WARN] Ошибка скачивания листинга {listing_url}: {e}")
    return sorted(list(set(discovered)))


def parse_existing_index(file_path: str) -> dict:
    """Читает существующий 96_articles_index.md в словарь {url: item}"""
    existing = {}
    if not os.path.exists(file_path):
        return existing

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str.startswith("|") and not line_str.startswith("|---") and "URL" not in line_str:
                parts = [p.strip() for p in line_str.split("|")]
                if len(parts) >= 5:
                    url = parts[1]
                    title = parts[2]
                    desc = parts[3]
                    h1 = parts[4]
                    if url.startswith("http"):
                        existing[url] = {
                            "url": url,
                            "title": title,
                            "desc": desc,
                            "h1": h1
                        }
    return existing


def main():
    parser = argparse.ArgumentParser(description="Актуализация индекса статей и кейсов с сайта longwang.ru")
    parser.add_argument("--index-path", default=DEFAULT_INDEX_PATH, help="Путь к файлу 96_articles_index.md")
    parser.add_argument("--limit", type=int, default=100, help="Максимальное количество страниц для скачивания")
    parser.add_argument("--dry-run", action="store_true", help="Режим предпросмотра без изменения файла")
    args = parser.parse_args()

    print("=" * 80)
    print("АКТУАЛИЗАЦИЯ ИНДЕКСА СТАТЕЙ И КЕЙСОВ LONGWANG.RU")
    print(f"Целевой индекс: {args.index_path}")
    print(f"Режим: {'DRY-RUN (предпросмотр)' if args.dry_run else 'БОЕВОЙ'}")
    print("=" * 80)

    # 1. Загрузка существующего индекса
    existing_items = parse_existing_index(args.index_path)
    print(f"Текущих записей в индексе: {len(existing_items)}")

    # 2. Поиск URL через Sitemap и прямые листинги
    print("\n[1/3] Поиск целевых URL (/useful-articles/ и /projects/)...")
    discovered_urls = discover_urls_from_sitemap()
    print(f"  Найдено через sitemap: {len(discovered_urls)} шт.")

    # Дополнительно опрашиваем листинги
    listing_urls = ["https://longwang.ru/useful-articles/", "https://longwang.ru/projects/"]
    for lurl in listing_urls:
        l_urls = discover_urls_from_html_listing(lurl)
        print(f"  Найдено со страницы {lurl}: {len(l_urls)} шт.")
        discovered_urls.extend(l_urls)

    all_target_urls = sorted(list(set(discovered_urls)))
    print(f"Всего уникальных URL обнаружено: {len(all_target_urls)}")

    if not all_target_urls:
        print("[WARN] Ссылки не найдены, завершение.")
        return

    # 3. Скачивание и извлечение мета-данных
    print(f"\n[2/3] Обход страниц (лимит {args.limit} шт.)...")
    scanned = 0
    new_count = 0
    updated_count = 0
    merged_items = dict(existing_items)

    for url in all_target_urls[:args.limit]:
        scanned += 1
        is_new = url not in merged_items
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code == 200:
                meta = extract_meta_from_html(r.text, url)
                if is_new:
                    new_count += 1
                    print(f"  [+] НОВАЯ ({scanned}): {url} -> {meta['h1'][:50]}")
                else:
                    updated_count += 1
                merged_items[url] = meta
            else:
                print(f"  [-] HTTP {r.status_code}: {url}")
        except Exception as e:
            print(f"  [!] Ошибка при запросе {url}: {e}")

    print(f"\n[3/3] Результаты сканирования:")
    print(f"  Проверено страниц: {scanned}")
    print(f"  Новых материалов: {new_count}")
    print(f"  Итоговый размер базы: {len(merged_items)} материалов")

    # 4. Сохранение обновленного файла
    if not args.dry_run:
        # Резервная копия перед перезаписью
        if os.path.exists(args.index_path):
            backup_path = args.index_path + ".bak"
            with open(args.index_path, "r", encoding="utf-8") as src, open(backup_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())

        with open(args.index_path, "w", encoding="utf-8") as f:
            f.write("# Articles and Projects Index (longwang.ru)\n\n")
            f.write("Источник: автоматический краулер `update_website_knowledge_index.py` (разделы /useful-articles/ и /projects/).\n\n")
            f.write("Поля: URL, Title, Description, H1. Легковесный индекс для семантического RAG.\n\n")
            f.write("| URL | Title | Description | H1 |\n")
            f.write("|---|---|---|---|\n")
            for url, item in sorted(merged_items.items(), key=lambda x: x[0]):
                f.write(f"| {item['url']} | {item['title']} | {item['desc']} | {item['h1']} |\n")

        print(f"\n[OK] Индекс успешно обновлен и сохранен в {args.index_path}")
    else:
        print("\n[DRY-RUN] Файл не модифицировался (запустите без --dry-run для применения)")


if __name__ == "__main__":
    main()
