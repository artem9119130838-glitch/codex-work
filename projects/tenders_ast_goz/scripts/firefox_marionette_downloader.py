#!/usr/bin/env python3
"""
AST GOZ Documentation Downloader for Mozilla Firefox via Selenium Marionette.

Скрипт подключается к уже запущенной сессии Mozilla Firefox через протокол Marionette (порт 2828).
В браузере уже должен быть вставлен токен ЭЦП и открыт реестр лотов.

Запуск Firefox перед стартом:
  "C:\\Program Files\\Mozilla Firefox\\firefox.exe" -marionette -start-debugger-server 2828

Требования:
  pip install selenium
  geckodriver.exe (в PATH или рядом со скриптом)
"""

import os
import re
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("astgoz_firefox")

MARIONETTE_PORT = int(os.getenv("ASTGOZ_MARIONETTE_PORT", "2828"))
OUTPUT_DIR = Path(os.getenv("ASTGOZ_OUTPUT_DIR", "C:/AST_GOZ_DOCS"))
MAX_LOTS_PER_RUN = int(os.getenv("ASTGOZ_MAX_LOTS", "30"))


def extract_lot_id(text: str) -> str:
    match = re.search(r"\b26\d{13}\b", text)
    if match:
        return match.group(0)
    match_fallback = re.search(r"\b\d{8,15}\b", text)
    return match_fallback.group(0) if match_fallback else "unknown_lot"


def run():
    try:
        from selenium import webdriver
        from selenium.webdriver.firefox.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        logger.error("Библиотека 'selenium' не установлена! Выполните: pip install selenium")
        logger.info("Примечание: для Firefox рекомендуется использовать готовый Tampermonkey Userscript "
                    "(scripts/ast_goz/astgoz_master_worker.user.js), не требующий внешних библиотек.")
        return

    logger.info(f"Подключение к Firefox Marionette на порту {MARIONETTE_PORT}...")
    try:
        service = Service(service_args=["--marionette-port", str(MARIONETTE_PORT), "--connect-existing"])
        driver = webdriver.Firefox(service=service)
    except Exception as e:
        logger.error(f"Не удалось подключиться к Firefox: {e}")
        logger.info("Убедитесь, что Firefox запущен с параметрами: -marionette -start-debugger-server 2828")
        return

    registry_window = driver.current_window_handle
    logger.info(f"Подключено к Firefox. Текущая страница: {driver.title} ({driver.current_url})")

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    logger.info(f"Всего строк в реестре: {len(rows)}")

    processed_count = 0
    for row in rows:
        if processed_count >= MAX_LOTS_PER_RUN:
            break

        row_text = row.text
        if "Запрос документации" in row_text:
            lot_id = extract_lot_id(row_text)
            logger.info(f"Обработка лота: {lot_id}")

            try:
                request_link = row.find_element(By.XPATH, ".//a[contains(text(), 'Запрос документации') or contains(@href, 'request_documents')]")
                href = request_link.get_attribute("href")

                # Открываем новую вкладку в Firefox
                driver.switch_to.new_window('tab')
                driver.get(href)

                # Шаг 1: Чекбокс
                cb = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox']")))
                if not cb.is_selected():
                    cb.click()

                # Шаг 2: Подписать и отправить
                submit_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Подписать и отправить')] | //a[contains(text(), 'Подписать и отправить')]")))
                submit_btn.click()

                # Шаг 3: Модалка подтверждения
                modal_btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='modal']//button[contains(text(), 'Подписать')] | //*[@id='modal']//a[contains(text(), 'Подписать')]")))
                modal_btn.click()
                time.sleep(2)

                # Шаг 4: Выгрузить на карточке закупки
                unload_btn = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Выгрузить')] | //a[contains(text(), 'Выгрузить')]")))
                unload_btn.click()
                logger.info(f"Нажата выгрузка для лота {lot_id}. Ожидание скачивания...")
                time.sleep(4)

                # Закрываем вкладку лота и возвращаемся в реестр
                driver.close()
                driver.switch_to.window(registry_window)

                # Шаг 5: Простановка метки 'Подготовить документы'
                try:
                    prep_link = row.find_element(By.XPATH, ".//a[contains(@href, 'action=set_documents')]")
                    prep_href = prep_link.get_attribute("href")
                    driver.switch_to.new_window('tab')
                    driver.get(prep_href)
                    time.sleep(1.5)
                    driver.close()
                    driver.switch_to.window(registry_window)
                    logger.info(f"Метка выставлена для {lot_id}")
                except Exception as e_prep:
                    logger.warning(f"Метка не выставлена: {e_prep}")

                processed_count += 1
                time.sleep(3)

            except Exception as e_lot:
                logger.error(f"Ошибка при обработке {lot_id}: {e_lot}")
                # Гарантируем возврат на окно реестра
                if driver.current_window_handle != registry_window:
                    driver.close()
                    driver.switch_to.window(registry_window)

    logger.info(f"Выгрузка завершена. Всего лотов: {processed_count}")


if __name__ == "__main__":
    run()
