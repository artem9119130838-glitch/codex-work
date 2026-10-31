Set-NetIPInterface -Forwarding Disabled -ErrorAction SilentlyContinue
netsh interface ipv4 set interface "Ethernet" forwarding=disabled
netsh interface ipv4 set interface "Беспроводная сеть" forwarding=disabled
Write-Host "=== Forwarding успешно отключен! ===" -ForegroundColor Green
Get-NetIPInterface -AddressFamily IPv4 | Select-Object InterfaceAlias, Forwarding | Format-Table -AutoSize
Write-Host "Нажмите любую клавишу для закрытия..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
