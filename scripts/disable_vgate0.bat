@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Запрос прав администратора...
    powershell -Command "Start-Process cmd -ArgumentList '/c netsh interface set interface \"vgate0\" disable & echo Адаптер vgate0 успешно отключен! & pause' -Verb RunAs"
    exit /b
)
netsh interface set interface "vgate0" disable
echo Адаптер vgate0 успешно отключен!
pause
