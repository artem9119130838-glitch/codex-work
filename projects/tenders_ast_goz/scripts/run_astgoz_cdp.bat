@echo off
chcp 65001 >nul
title AST GOZ Documentation Downloader (Playwright CDP)

echo =====================================================================
echo  АВТОМАТИЗАЦИЯ ВЫГРУЗКИ ДОКУМЕНТАЦИИ АСТ ГОЗ (223.astgoz.ru)
echo  Контур: Изолированный (Air-Gap / ViPNet Client)
echo =====================================================================
echo.

set BROWSER_EXE=
if exist "C:\Program Files\Chromium-Gost\chrome.exe" set BROWSER_EXE=C:\Program Files\Chromium-Gost\chrome.exe
if not defined BROWSER_EXE if exist "C:\Program Files (x86)\Chromium-Gost\chrome.exe" set BROWSER_EXE=C:\Program Files (x86)\Chromium-Gost\chrome.exe
if not defined BROWSER_EXE if exist "%LOCALAPPDATA%\Chromium-Gost\chrome.exe" set BROWSER_EXE=%LOCALAPPDATA%\Chromium-Gost\chrome.exe
if not defined BROWSER_EXE if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set BROWSER_EXE=C:\Program Files\Google\Chrome\Application\chrome.exe
if not defined BROWSER_EXE if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set BROWSER_EXE=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
if not defined BROWSER_EXE if exist "%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe" set BROWSER_EXE=%LOCALAPPDATA%\Yandex\YandexBrowser\Application\browser.exe

if not defined BROWSER_EXE (
    echo [ВНИМАНИЕ] Браузер Chromium-ГОСТ/Chrome не найден по стандартным путям.
    echo Пожалуйста, запустите ваш браузер вручную с параметрами:
    echo chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\astgoz_browser_profile"
    echo.
) else (
    echo [ИНФО] Найден браузер: "%BROWSER_EXE%"
    echo [ИНФО] Запуск браузера с портом отладки 9222...
    start "" "%BROWSER_EXE%" --remote-debugging-port=9222 --user-data-dir="C:\astgoz_browser_profile"
)

echo.
echo ---------------------------------------------------------------------
echo  ДЕЙСТВИЯ ОПЕРАТОРА (выполняются в открывшемся браузере):
echo   1. Убедитесь, что аппаратный токен (Рутокен) вставлен.
echo   2. Выполните вход по ЭЦП в личный кабинет: https://223.astgoz.ru
echo   3. Откройте реестр лотов (например, с фильтром "Интересно"):
echo      https://223.astgoz.ru/registry/view/pr_lots_all
echo   4. Оставьте вкладку реестра открытой!
echo ---------------------------------------------------------------------
echo.
pause

echo.
echo [ИНФО] Запуск Playwright CDP робота...
python playwright_cdp_downloader.py

echo.
echo =====================================================================
echo  Сессия выгрузки завершена. Файлы сохранены в C:\AST_GOZ_DOCS
echo =====================================================================
pause
