@echo off
chcp 65001 >nul
title AST GOZ Documentation Downloader (Mozilla Firefox)

echo =====================================================================
echo  АВТОМАТИЗАЦИЯ ВЫГРУЗКИ ДОКУМЕНТАЦИИ АСТ ГОЗ (223.astgoz.ru)
echo  Контур: Изолированный (Air-Gap / ViPNet Client)
echo  Браузер: Mozilla Firefox
echo =====================================================================
echo.

set FIREFOX_EXE=
if exist "C:\Program Files\Mozilla Firefox\firefox.exe" set FIREFOX_EXE=C:\Program Files\Mozilla Firefox\firefox.exe
if not defined FIREFOX_EXE if exist "C:\Program Files (x86)\Mozilla Firefox\firefox.exe" set FIREFOX_EXE=C:\Program Files (x86)\Mozilla Firefox\firefox.exe
if not defined FIREFOX_EXE if exist "%LOCALAPPDATA%\Mozilla Firefox\firefox.exe" set FIREFOX_EXE=%LOCALAPPDATA%\Mozilla Firefox\firefox.exe

if not defined FIREFOX_EXE (
    echo [ВНИМАНИЕ] Mozilla Firefox не найден по стандартным путям.
    echo Пожалуйста, запустите Firefox вручную.
    echo.
) else (
    echo [ИНФО] Найден Firefox: "%FIREFOX_EXE%"
)

echo Выберите вариант автоматизации:
echo   [1] Tampermonkey Master-Worker 4.0 (РЕКОМЕНДУЕТСЯ: внутри браузера, без Python)
echo   [2] Python Marionette робот (внешний процесс, порт 2828)
echo.
set /p MODE="Введите 1 или 2 (по умолчанию 1): "
if "%MODE%"=="" set MODE=1

if "%MODE%"=="1" (
    echo.
    echo [ИНФО] Запуск Firefox для Tampermonkey...
    if defined FIREFOX_EXE (
        start "" "%FIREFOX_EXE%" "https://223.astgoz.ru/registry/view/pr_lots_all"
    )
    echo ---------------------------------------------------------------------
    echo  ДЕЙСТВИЯ:
    echo   1. Убедитесь, что скрипт astgoz_master_worker.user.js установлен в Tampermonkey.
    echo   2. В настройках Firefox отключите запрос папки скачивания (сохранять в Загрузки).
    echo   3. Вставьте Рутокен и войдите в АСТ ГОЗ.
    echo   4. Нажмите зеленую кнопку "🚀 ПОЛНЫЙ АВТОМАТ" на панели AST-GOZ CONTROL 4.0.
    echo ---------------------------------------------------------------------
    pause
    exit /b
)

if "%MODE%"=="2" (
    echo.
    echo [ИНФО] Запуск Firefox с поддержкой Marionette на порту 2828...
    if defined FIREFOX_EXE (
        start "" "%FIREFOX_EXE%" -marionette -start-debugger-server 2828 "https://223.astgoz.ru/registry/view/pr_lots_all"
    )
    echo ---------------------------------------------------------------------
    echo  ДЕЙСТВИЯ:
    echo   1. Вставьте токен ЭЦП и авторизуйтесь в открывшемся Firefox.
    echo   2. Откройте реестр лотов и выставьте нужные фильтры.
    echo   3. Нажмите любую клавишу для старта Python-скрипта...
    echo ---------------------------------------------------------------------
    pause
    echo.
    echo [ИНФО] Запуск Python Marionette робота...
    python firefox_marionette_downloader.py
    echo.
    echo =====================================================================
    echo  Выгрузка завершена.
    echo =====================================================================
    pause
    exit /b
)
