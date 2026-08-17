$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\inventory_common.ps1"

$paths = @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
)

$items = foreach ($path in $paths) {
    Get-ItemProperty $path -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName } |
        Select-Object @{n='DisplayName';e={$_.DisplayName}},
                      @{n='DisplayVersion';e={$_.DisplayVersion}},
                      @{n='Publisher';e={$_.Publisher}},
                      @{n='InstallDate';e={$_.InstallDate}},
                      @{n='InstallLocation';e={$_.InstallLocation}},
                      @{n='UninstallString';e={$_.UninstallString}}
}

$timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$basePath = Join-Path $PSScriptRoot "programs\installed_programs_$timestamp"
$items = @($items | Sort-Object DisplayName -Unique)
Export-TableFiles -Rows $items -BasePath $basePath -WorksheetName 'Programs'
Write-Output "Programs export completed."
