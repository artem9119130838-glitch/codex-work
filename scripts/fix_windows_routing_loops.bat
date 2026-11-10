@echo off
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo ========================================================
echo  Fixing WireGuard Routing Loops and O+Connect Conflict
echo ========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "foreach ($s in @('O+Connect Service','OplusRemoteService')) { Stop-Service -Name $s -Force -ErrorAction SilentlyContinue; Set-Service -Name $s -StartupType Manual -ErrorAction SilentlyContinue }; Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'O+Connect' -ErrorAction SilentlyContinue; Stop-Process -Name 'O+Connect','devicespace','oplus_remote_service','pantaChannelService' -Force -ErrorAction SilentlyContinue; Start-Sleep -Seconds 1; Disable-NetAdapter -Name 'vgate0' -Confirm:$false -ErrorAction SilentlyContinue; Set-NetIPInterface -AddressFamily IPv4 -Forwarding Disabled -ErrorAction SilentlyContinue; Write-Host '[OK] O+Connect isolated, vgate0 disabled, Forwarding disabled.' -ForegroundColor Green; Get-NetIPInterface -AddressFamily IPv4 | Select-Object InterfaceAlias, Forwarding, InterfaceMetric | Format-Table -AutoSize; Get-NetAdapter | Select-Object Name, Status | Format-Table -AutoSize"

echo.
echo [DONE] WireGuard routing is clean. You can now connect WireGuard!
echo.
pause
