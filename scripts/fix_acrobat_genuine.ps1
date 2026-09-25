# fix_acrobat_genuine.ps1
# Comprehensive Adobe Acrobat Genuine & Deactivation Popup Eliminator

$logFile = "C:\Codex_Personal\scripts\fix_acrobat_genuine.log"
Start-Transcript -Path $logFile -Force

Write-Host "1. Stopping all Adobe background processes..." -ForegroundColor Cyan
$processes = @(
    "Acrobat", "AdobeCollabSync", "AcroCEF", "AcroBroker", "acrodist", 
    "acrotray", "ADNotificationManager", "AdobeARM", "armsvc", 
    "CRLogTransport", "CRWindowsClientService", "LogTransport2",
    "AGSService", "adobe_licensing_wf_acro", "adobe_licensing_wf_helper_acro",
    "FullTrustNotifier"
)
foreach ($proc in $processes) {
    Get-Process -Name $proc -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

Write-Host "2. Disabling GC (Genuine Client) and NGL cefWorkflow binaries..." -ForegroundColor Cyan
$gcPath = "C:\Program Files\Adobe\Acrobat DC\Acrobat\GC"
if (Test-Path $gcPath) {
    Rename-Item -Path $gcPath -NewName "GC_disabled" -Force -ErrorAction SilentlyContinue
    Write-Host "Disabled GC folder" -ForegroundColor Green
}

$wfPath = "C:\Program Files\Adobe\Acrobat DC\Acrobat\NGL\cefWorkflow"
if (Test-Path $wfPath) {
    Rename-Item -Path $wfPath -NewName "cefWorkflow_disabled" -Force -ErrorAction SilentlyContinue
    Write-Host "Disabled cefWorkflow folder" -ForegroundColor Green
}

Write-Host "3. Applying Enterprise FeatureLockDown Policies (Offline Mode & Suppress Upsell)..." -ForegroundColor Cyan
$policyHives = @(
    "HKLM:\SOFTWARE\Policies\Adobe\Adobe Acrobat\DC\FeatureLockDown",
    "HKLM:\SOFTWARE\WOW6432Node\Policies\Adobe\Adobe Acrobat\DC\FeatureLockDown"
)

foreach ($basePolicy in $policyHives) {
    if (-not (Test-Path $basePolicy)) {
        New-Item -Path $basePolicy -Force | Out-Null
    }
    Set-ItemProperty -Path $basePolicy -Name "bAcroSuppressUpsell" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $basePolicy -Name "bShowMsgAtLaunch" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $basePolicy -Name "bUsageMeasurement" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path $basePolicy -Name "bUpdater" -Value 0 -Type DWord -Force

    $ipmPolicy = "$basePolicy\cIPM"
    if (-not (Test-Path $ipmPolicy)) {
        New-Item -Path $ipmPolicy -Force | Out-Null
    }
    Set-ItemProperty -Path $ipmPolicy -Name "bDontShowMsgWhenViewingDoc" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $ipmPolicy -Name "bShowMsgAtLaunch" -Value 0 -Type DWord -Force

    $servicesPolicy = "$basePolicy\cServices"
    if (-not (Test-Path $servicesPolicy)) {
        New-Item -Path $servicesPolicy -Force | Out-Null
    }
    Set-ItemProperty -Path $servicesPolicy -Name "bToggleAdobeDocumentServices" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $servicesPolicy -Name "bToggleAdobeSign" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $servicesPolicy -Name "bTogglePrefManualSend" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $servicesPolicy -Name "bToggleWebConnectors" -Value 1 -Type DWord -Force
}
Write-Host "Applied FeatureLockDown offline policies" -ForegroundColor Green

Write-Host "4. Resetting cached user entitlement and notification state in Registry..." -ForegroundColor Cyan
Remove-Item -Path "HKCU:\Software\Adobe\Adobe Acrobat\DC\AVEntitlement" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "HKCU:\Software\Adobe\Adobe Acrobat\DC\IPM" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "HKCU:\Software\Adobe\Adobe Acrobat\DC\AVAlert" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "5. Clearing cached licensing data and CEF storage..." -ForegroundColor Cyan
$cacheDirs = @(
    "$env:LOCALAPPDATA\Adobe\AcroCef",
    "$env:LOCALAPPDATA\Adobe\NGL",
    "$env:APPDATA\Adobe\NGL",
    "$env:LOCALAPPDATA\Adobe\Acrobat\DC\Cache",
    "$env:LOCALAPPDATA\Adobe\Acrobat\DC\ToolsSearchCacheAcro"
)
foreach ($c in $cacheDirs) {
    if (Test-Path $c) {
        Remove-Item -Path "$c\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Cleared cache: $c" -ForegroundColor Green
    }
}

Write-Host "6. Updating hosts file with modern licensing & workflow endpoints (0.0.0.0)..." -ForegroundColor Cyan
$hostsPath = "$env:windir\System32\drivers\etc\hosts"
$domains = @(
    "workflow-ui-prod.licensingstack.com",
    "ic.adobe.io",
    "1hzopx6ugi.adobe.io",
    "adobereport.adobe.io",
    "cc-api-data.adobe.io",
    "lcs-cpc.adobe.io",
    "lcs-ropc.adobe.io",
    "p13n.adobe.io",
    "c534-ic.adobe.io",
    "ims-na1.adobelogin.com",
    "na1r.services.adobe.com",
    "auth.services.adobe.com",
    "armmf.adobe.com",
    "hcs.adobe.com",
    "aoa-cpc.adobe.io",
    "da.adobe.io",
    "cclibraries-defaults-cdn.adobe.com",
    "secondary.licenses.adobe.com",
    "ims-prod06.adobelogin.com",
    "oobe.adobe.com",
    "edge-notifications.adobe.com",
    "platform-cs.adobe.io",
    "gw-cpc.adobe.io",
    "api-cpc.adobe.io",
    "genuine.adobe.com",
    "prod.adobegenuine.com",
    "lmlicenses.wip4.adobe.com",
    "lm.licenses.adobe.com",
    "uds.licenses.adobe.com",
    "adobe.io",
    "cc-api-data-stage.adobe.io",
    "cctypekit.adobe.io",
    "activate.adobe.com",
    "practivate.adobe.com",
    "practivate-da1.adobe.com",
    "licenses.adobe.com",
    "license.adobe.com",
    "helpexamples.com",
    "0ojupfm51u.adobe.io",
    "0mo5a70cqa.adobe.io",
    "pojvrj7ho5.adobe.io",
    "i7pq6fgbsl.adobe.io",
    "ph0f2h2csf.adobe.io",
    "r3zj0yju1q.adobe.io",
    "guzg78logz.adobe.io",
    "2ftem87osk.adobe.io",
    "3d3wqt96ht.adobe.io",
    "23ynjitwt5.adobe.io",
    "3ca52znvmj.adobe.io",
    "r5hacgq5w6.adobe.io",
    "lre1kgz2u4.adobe.io",
    "ij0gdyrfka.adobe.io",
    "8ncdzpmmrg.adobe.io",
    "7sj9n87sls.adobe.io",
    "7m31guub0q.adobe.io",
    "7g2gzgk9g1.adobe.io",
    "cd536oo20y.adobe.io",
    "dxyeyf6ecy.adobe.io",
    "jc95y2v12r.adobe.io",
    "m59b4msyph.adobe.io",
    "vajcbj9qgq.adobe.io",
    "p7uxzbht8h.adobe.io",
    "vcorzsld2a.adobe.io",
    "p0bjuoe16a.adobe.io",
    "fqaq3pq1o9.adobe.io",
    "aoorovjtha.adobe.io",
    "bam.nr-data.net",
    "adobe-dns-01.adobe.com",
    "adobe.demdex.net",
    "adobe.tt.omtrdc.net",
    "adobedc.demdex.net",
    "adobeid-na1.services.adobe.com",
    "auth-cloudfront.prod.ims.adobejanus.com"
)

if (Test-Path $hostsPath) {
    $currentHosts = Get-Content $hostsPath -Raw -Encoding UTF8
    $sb = [System.Text.StringBuilder]::new()
    foreach ($d in $domains) {
        if ($currentHosts -notmatch [regex]::Escape($d)) {
            [void]$sb.AppendLine("0.0.0.0 $d")
        }
    }
    if ($sb.Length -gt 0) {
        Add-Content -Path $hostsPath -Value "`r`n# Adobe 2026 Extended Block`r`n$($sb.ToString())" -Encoding UTF8
        Write-Host "Added new domains to hosts file" -ForegroundColor Green
    }
}

Write-Host "7. Flushing DNS cache..." -ForegroundColor Cyan
Clear-DnsClientCache

Write-Host "`nAll operations completed successfully!" -ForegroundColor Green
Stop-Transcript
