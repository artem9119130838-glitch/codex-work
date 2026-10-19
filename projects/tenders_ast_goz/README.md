# Автоматизация выгрузки тендеров с АСТ ГОЗ (tenders_ast_goz)

Канонический пакет инструментов для автоматизированного скачивания пакетов тендерной документации с площадки `223.astgoz.ru` в условиях изолированного контура (Air-Gap: работа через защищенный шлюз ViPNet без доступа в публичный интернет).

---

## 🚀 Быстрый старт на любом компьютере

### Вариант 1: В браузере через расширение Tampermonkey (Рекомендуемый для оператора)
*Не требует установки Python или сложного ПО.*

1. **Установка скрипта:**
   * Откройте браузер (Mozilla Firefox или Chromium-ГОСТ).
   * Убедитесь, что установлено расширение **Tampermonkey**.
   * Создайте новый скрипт в Tampermonkey и вставьте код из файла:  
     [`scripts/astgoz_master_worker.user.js`](file:///C:/Codex/projects/tenders_ast_goz/scripts/astgoz_master_worker.user.js) (версия 4.1).
2. **Запуск:**
   * Вставьте токен ЭЦП (Рутокен) и выполните вход на `223.astgoz.ru`.
   * Перейдите в реестр лотов: `https://223.astgoz.ru/registry/view/pr_lots_all`.
   * На панели в правом верхнем углу нажмите **«🚀 ПОЛНЫЙ АВТОМАТ»**.
   * Скрипт поочередно откроет карточки лотов, подпишет согласия, выгрузит архивы в папку «Загрузки» и пометит обработанные строки зеленым бейджем `✔ Выгружен`.

Подробная пошаговая инструкция для менеджера:  
📄 [`docs/instruction_for_aleksandra.md`](file:///C:/Codex/projects/tenders_ast_goz/docs/instruction_for_aleksandra.md)

---

### Вариант 2: Автономный робот через Playwright CDP (Python)
*Для работы снаружи через DevTools-протокол.*

1. Запустите Chromium-ГОСТ с открытым портом отладки через батник:  
   [`scripts/run_astgoz_chromium.bat`](file:///C:/Codex/projects/tenders_ast_goz/scripts/run_astgoz_chromium.bat) (порт `9222`).
2. Войдите по ЭЦП и откройте реестр лотов.
3. Запустите скрипт:  
   ```cmd
   py scripts/playwright_cdp_downloader.py
   ```
   (или запустите [`scripts/run_astgoz_cdp.bat`](file:///C:/Codex/projects/tenders_ast_goz/scripts/run_astgoz_cdp.bat)).

---

### Вариант 3: Автономный робот через Marionette (Mozilla Firefox)
1. Запустите Firefox с флагом `--marionette` через батник:  
   [`scripts/run_astgoz_firefox.bat`](file:///C:/Codex/projects/tenders_ast_goz/scripts/run_astgoz_firefox.bat).
2. Запустите скрипт:  
   ```cmd
   py scripts/firefox_marionette_downloader.py
   ```

---

## 📁 Структура каталога проекта

* **`scripts/`** — рабочие скрипты и батники:
  * [`scripts/astgoz_master_worker.user.js`](file:///C:/Codex/projects/tenders_ast_goz/scripts/astgoz_master_worker.user.js) — боевой Userscript v4.1 для Tampermonkey.
  * [`scripts/playwright_cdp_downloader.py`](file:///C:/Codex/projects/tenders_ast_goz/scripts/playwright_cdp_downloader.py) — CDP-робот на Python.
  * [`scripts/firefox_marionette_downloader.py`](file:///C:/Codex/projects/tenders_ast_goz/scripts/firefox_marionette_downloader.py) — Marionette-робот на Python.
  * [`scripts/ast_goz.zip`](file:///C:/Codex/projects/tenders_ast_goz/scripts/ast_goz.zip) — полный упакованный дистрибутив для переноса на ГОЗ-станцию.
  * [`scripts/README.md`](file:///C:/Codex/projects/tenders_ast_goz/scripts/README.md) — техническое руководство по скриптам.
* **`docs/`** — отчеты, ТЗ и инструкции:
  * [`docs/instruction_for_aleksandra.md`](file:///C:/Codex/projects/tenders_ast_goz/docs/instruction_for_aleksandra.md) — руководство без технического сленга для оператора.
  * [`docs/daily_summary_2026_10_17.md`](file:///C:/Codex/projects/tenders_ast_goz/docs/daily_summary_2026_10_17.md) — отчет Михаила об устранении таймаутов и архитектуре версии 4.1.
  * [`docs/mikhail_task_ast_goz_automation.md`](file:///C:/Codex/projects/tenders_ast_goz/docs/mikhail_task_ast_goz_automation.md) — исходное техническое задание.
* **`legacy_context/`** — хронология предыдущих попыток (OCR, AHK, Bookmarklets).

---

## 🔒 Безопасность и передача данных (Air-Gap)

Во время выгрузки компьютер отрезан от публичной сети. После завершения скачивания:
1. Сессия ViPNet отключается $\to$ интернет восстанавливается (или архивы переносятся на флешке на ПК с интернетом).
2. Архивы перетаскиваются в **Папку 01 (`01_stage1_inbox_national_regime`) на Google Диске**.
3. Облачный каскадный конвейер RAG API автоматически анализирует нацрежим (ПП №1875), условия оплаты и отправляет прошедшие лоты в Битрикс24.
