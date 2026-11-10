@echo off
echo Collecting Happ TUN offline diagnostics...
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Codex\scripts\diag_happ_tun.ps1"
echo.
echo You can now turn Happ OFF and return to the chat!
pause
