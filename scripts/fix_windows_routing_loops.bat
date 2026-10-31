@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-NetIPInterface -Forwarding Disabled; Get-NetIPInterface -AddressFamily IPv4 | Select-Object InterfaceAlias, Forwarding | Format-Table -AutoSize"

echo.
echo [DONE] Forwarding has been disabled!
echo You can now close this window and reconnect WireGuard.
echo.
pause
