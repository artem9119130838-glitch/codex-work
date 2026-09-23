param(
    [string]$ConfigPath = "$PSScriptRoot\inventory_config.ps1"
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\inventory_common.ps1"
$config = . $ConfigPath
$timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$basePath = Join-Path $PSScriptRoot "snapshots\snapshot_$timestamp"

$roots = Resolve-ExistingPaths -Paths $config.SnapshotRoots

$rows = foreach ($rootPath in $roots) {
    Get-ChildItem -LiteralPath $rootPath -Recurse -Force -File -ErrorAction SilentlyContinue |
        Where-Object { -not (Test-ExcludedPath -Path $_.FullName -Patterns $config.ExcludePatterns) } |
        Select-Object @{n='FullName';e={$_.FullName}},
                      @{n='Directory';e={$_.DirectoryName}},
                      @{n='Name';e={$_.Name}},
                      @{n='Extension';e={$_.Extension}},
                      @{n='Length';e={$_.Length}},
                      @{n='LastWriteTime';e={$_.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss')}},
                      @{n='CreationTime';e={$_.CreationTime.ToString('yyyy-MM-dd HH:mm:ss')}}
}

$rows = @($rows | Sort-Object FullName)
Export-TableFiles -Rows $rows -BasePath $basePath -WorksheetName 'Snapshot'
Write-Output "Snapshot completed."
