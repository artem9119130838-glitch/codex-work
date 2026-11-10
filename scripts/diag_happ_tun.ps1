$ErrorActionPreference = 'SilentlyContinue'
if (-not (Test-Path 'C:\Codex\scratch')) {
    New-Item -ItemType Directory -Path 'C:\Codex\scratch' | Out-Null
}
$out = 'C:\Codex\scratch\happ_diag_report.txt'

'=== HAPP TUN DIAGNOSTIC SNAPSHOT ===' | Out-File $out -Encoding utf8
(Get-Date).ToString('yyyy-MM-dd HH:mm:ss') | Out-File $out -Append -Encoding utf8

"`n--- PROCESSES ---" | Out-File $out -Append -Encoding utf8
Get-Process -Name 'Happ','happd','xray','sing-box','tun2proxy*','wireguard*','O+Connect*','devicespace*' |
    Select-Object Id, ProcessName, Path | Format-Table -AutoSize | Out-String | Out-File $out -Append -Encoding utf8

"`n--- NET ADAPTERS ---" | Out-File $out -Append -Encoding utf8
Get-NetAdapter | Select-Object Name, Status, InterfaceDescription, InterfaceIndex |
    Format-Table -AutoSize | Out-String | Out-File $out -Append -Encoding utf8

"`n--- IPv4 INTERFACES ---" | Out-File $out -Append -Encoding utf8
Get-NetIPInterface -AddressFamily IPv4 |
    Select-Object InterfaceAlias, InterfaceIndex, Forwarding, InterfaceMetric, ConnectionState |
    Format-Table -AutoSize | Out-String | Out-File $out -Append -Encoding utf8

"`n--- DNS SERVERS ---" | Out-File $out -Append -Encoding utf8
Get-DnsClientServerAddress -AddressFamily IPv4 |
    Select-Object InterfaceAlias, ServerAddresses |
    Format-Table -AutoSize | Out-String | Out-File $out -Append -Encoding utf8

"`n--- ROUTES (DEFAULT / TUN) ---" | Out-File $out -Append -Encoding utf8
Get-NetRoute -AddressFamily IPv4 |
    Where-Object { $_.DestinationPrefix -in @('0.0.0.0/0','0.0.0.0/1','128.0.0.0/1') -or $_.InterfaceAlias -like '*happ*' -or $_.InterfaceAlias -like '*vgate*' -or $_.RouteMetric -lt 300 } |
    Select-Object DestinationPrefix, NextHop, InterfaceAlias, RouteMetric, InterfaceMetric |
    Format-Table -AutoSize | Out-String | Out-File $out -Append -Encoding utf8

"`n--- LISTENING PORTS ---" | Out-File $out -Append -Encoding utf8
(netstat -ano | Select-String ':10808|:7890|:1080|:53 ') | Out-String | Out-File $out -Append -Encoding utf8

"`n--- PING & DNS TEST ---" | Out-File $out -Append -Encoding utf8
(ping -n 2 -w 2000 8.8.8.8) | Out-String | Out-File $out -Append -Encoding utf8
(nslookup google.com 1.1.1.1 2>&1) | Out-String | Out-File $out -Append -Encoding utf8

"`n--- HAPPD LOG TAIL (80 lines) ---" | Out-File $out -Append -Encoding utf8
if (Test-Path 'C:\ProgramData\Happ\logs\happd.log') {
    Get-Content 'C:\ProgramData\Happ\logs\happd.log' -Tail 80 -Encoding utf8 | Out-File $out -Append -Encoding utf8
}

Write-Host '[DONE] Report saved to C:\Codex\scratch\happ_diag_report.txt' -ForegroundColor Green
