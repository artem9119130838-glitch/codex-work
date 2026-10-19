#!/usr/bin/env python3
"""
AST GOZ Automated Documentation Downloader via Chrome DevTools Protocol (CDP).

Скрипт подключается к уже запущенному браузеру с активным профилем ГОСТ/КриптоПро,
находит открытую вкладку реестра АСТ ГОЗ, обрабатывает лоты во временных вкладках,
скачивает архивы документации и сохраняет их по номерам процедур.

Запуск браузера перед стартом:
  chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\astgoz_browser_profile"
"""

import os
import re
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("astgoz_downloader")

CDP_URL = os.getenv("ASTGOZ_CDP_URL", "http://localhost:9222")
OUTPUT_DIR = Path(os.getenv("ASTGOZ_OUTPUT_DIR", "C:/AST_GOZ_DOCS"))
MAX_LOTS_PER_RUN = int(os.getenv("ASTGOZ_MAX_LOTS", "30"))


def extract_lot_id(text: str) -> str:
    """Извлекает 15-значный номер процедуры или fallback на 8+ цифр."""
    match = re.search(r"\b26\d{13}\b", text)
    if match:
        return match.group(0)
    match_fallback = re.search(r"\b\d{8,15}\b", text)
    return match_fallback.group(0) if match_fallback else "unknown_lot"


def process_lot(context, registry_page, row_element) -> bool:
    """
    Обрабатывает один лот: открывает карточку во второй вкладке,
    подписывает запрос, выгружает архив, закрывает вкладку.
    """
    row_text = row_element.inner_text()
    lot_id = extract_lot_id(row_text)
    logger.info(f"==> Обработка лота: {lot_id}")

    lot_dir = OUTPUT_DIR / lot_id
    lot_dir.mkdir(parents=True, exist_ok=True)
    target_zip = lot_dir / f"{lot_id}.zip"

    # Дедупликация: если архив уже скачан, не тратим время на повторный запрос
    if target_zip.exists() and target_zip.stat().st_size > 1024:
        logger.info(f"Архив для лота {lot_id} уже существует ({target_zip.stat().st_size} байт). Пропуск скачивания.")
        return True

    # Ищем ссылку на запрос документации
    request_link_elem = row_element.query_selector('a:has-text("Запрос документации"), a[href*="request_documents"]')
    if not request_link_elem:
        logger.warning(f"Ссылка 'Запрос документации' не найдена для лота {lot_id}. Пропуск.")
        return False

    request_href = request_link_elem.get_attribute("href")
    if not request_href:
        logger.warning(f"Пустой href запроса для лота {lot_id}. Пропуск.")
        return False

    # Преобразуем относительный URL в абсолютный при необходимости
    if not request_href.startswith("http"):
        base_url = "https://223.astgoz.ru"
        request_href = base_url + ("" if request_href.startswith("/") else "/") + request_href

    # Открываем вторую вкладку — реестр не перезагружается!
    work_page = context.new_page()
    try:
        logger.info(f"Переход на страницу запроса: {request_href}")
        work_page.goto(request_href, wait_until="domcontentloaded", timeout=30000)

        # Шаг 1: Чекбокс согласия
        checkbox = work_page.wait_for_selector('input[type="checkbox"]', timeout=15000)
        if checkbox and not checkbox.is_checked():
            checkbox.check()
            work_page.evaluate("""() => {
                const cb = document.querySelector('input[type="checkbox"]');
                if (cb) {
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""")
            logger.info("Чекбокс согласия установлен.")

        # Шаг 2: Клик 'Подписать и отправить'
        submit_btn = work_page.wait_for_selector('button:has-text("Подписать и отправить"), a:has-text("Подписать и отправить")', timeout=10000)
        submit_btn.click()
        logger.info("Нажата кнопка 'Подписать и отправить'.")

        # Шаг 3: Модальное окно подтверждения
        modal_btn = work_page.wait_for_selector('#modal button:has-text("Подписать"), #modal a:has-text("Подписать"), .modal button:has-text("Подписать")', timeout=20000)
        modal_btn.click()
        logger.info("Подтверждено в модальном окне.")
        # Пауза на подписание плагином КриптоПро
        time.sleep(2)

        # Шаг 4: Ожидание перехода на карточку и кнопки 'Выгрузить'
        unload_btn = work_page.wait_for_selector('a:has-text("Выгрузить"), button:has-text("Выгрузить")', timeout=35000)

        # Шаг 5: Перехват события скачивания
        with work_page.expect_download(timeout=60000) as download_info:
            unload_btn.click()
            logger.info("Нажата кнопка 'Выгрузить'. Ожидание скачивания архива...")

        download = download_info.value
        download.save_as(str(target_zip))
        logger.info(f"Архив успешно сохранен: {target_zip} (Размер: {target_zip.stat().st_size} байт)")

        # Шаг 6: Простановка статусной метки «Подготовить документы»
        try:
            prep_link = row_element.query_selector('a[href*="action=set_documents"], a:has-text("Подготовить документы")')
            if prep_link:
                prep_href = prep_link.get_attribute("href")
                if prep_href:
                    if not prep_href.startswith("http"):
                        base_url = "https://223.astgoz.ru"
                        prep_href = base_url + ("" if prep_href.startswith("/") else "/") + prep_href
                    prep_page = context.new_page()
                    try:
                        prep_page.goto(prep_href, wait_until="domcontentloaded", timeout=15000)
                        logger.info(f"Метка 'Подготовить документы' выставлена для лота {lot_id}.")
                        time.sleep(1)
                    finally:
                        prep_page.close()
                else:
                    prep_link.click()
                    time.sleep(1)
        except Exception as e_prep:
            logger.warning(f"Не удалось установить метку для лота {lot_id}: {e_prep}")

        return True

    except PlaywrightTimeoutError as te:
        logger.error(f"Таймаут ожидания элемента при обработке {lot_id}: {te}")
        return False
    except Exception as e:
        logger.error(f"Ошибка при обработке {lot_id}: {e}")
        return False
    finally:
        # Всегда закрываем рабочую вкладку
        work_page.close()


def run(cdp_url: str = CDP_URL, output_dir: Path = OUTPUT_DIR, max_lots: int = MAX_LOTS_PER_RUN):
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Подключение к браузеру через CDP: {cdp_url}")
    logger.info(f"Целевая папка сохранения: {output_dir}")
    logger.info(f"Лимит лотов за прогон: {max_lots}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
        except Exception as e_conn:
            logger.error(f"Не удалось подключиться к CDP по адресу {cdp_url}. "
                         f"Убедитесь, что браузер запущен с ключом --remote-debugging-port=9222. Ошибка: {e_conn}")
            return

        default_context = browser.contexts[0] if browser.contexts else browser.new_context()

        # Ищем открытую вкладку реестра АСТ ГОЗ
        registry_page = None
        for page in default_context.pages:
            if "astgoz.ru" in page.url and "pr_lots_all" in page.url:
                registry_page = page
                break

        if not registry_page:
            logger.error("Не найдена открытая вкладка с реестром лотов (223.astgoz.ru/registry/view/pr_lots_all)!")
            logger.info("Пожалуйста, откройте реестр в браузере и примените нужные фильтры перед запуском.")
            return

        logger.info(f"Найдена активная вкладка реестра: {registry_page.url}")

        rows = registry_page.query_selector_all("table tbody tr")
        logger.info(f"Всего строк в таблице реестра: {len(rows)}")

        processed_count = 0
        for row in rows:
            if processed_count >= max_lots:
                logger.info(f"Достигнут лимит обработки за запуск ({max_lots} лотов). Завершение.")
                break

            text = row.inner_text()
            if "Запрос документации" in text:
                success = process_lot(default_context, registry_page, row)
                if success:
                    processed_count += 1
                    # Пауза между запросами для стабильности площадки
                    time.sleep(3)

        if processed_count > 0:
            try:
                apply_btn = registry_page.query_selector('button:has-text("Применить фильтры"), input[value*="Применить"], button:has-text("Применить")')
                if apply_btn:
                    apply_btn.click()
                    logger.info("Фильтры реестра успешно обновлены.")
            except Exception as e_filter:
                logger.warning(f"Не удалось обновить фильтры: {e_filter}")

        logger.info(f"Работа завершена. Всего успешно выгружено лотов: {processed_count}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AST GOZ Automated Documentation Downloader via Playwright CDP")
    parser.add_argument("--cdp-url", default=CDP_URL, help="CDP URL (default: %(default)s)")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Каталог для выгрузки (default: %(default)s)")
    parser.add_argument("--max-lots", type=int, default=MAX_LOTS_PER_RUN, help="Максимум лотов (default: %(default)s)")
    args = parser.parse_args()

    run(cdp_url=args.cdp_url, output_dir=args.output_dir, max_lots=args.max_lots)
