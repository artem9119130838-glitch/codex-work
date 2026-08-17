param(
    [string]$OldSnapshot,
    [string]$NewSnapshot
)

$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\inventory_common.ps1"

$snapshotFiles = Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'snapshots') -Filter '*.csv' |
    Sort-Object LastWriteTime

if (-not $OldSnapshot -or -not $NewSnapshot) {
    if ($snapshotFiles.Count -lt 2) {
        throw 'At least two snapshots are required.'
    }
    $OldSnapshot = $snapshotFiles[-2].FullName
    $NewSnapshot = $snapshotFiles[-1].FullName
}

$old = Import-Csv -LiteralPath $OldSnapshot
$new = Import-Csv -LiteralPath $NewSnapshot

$oldMap = @{}
foreach ($item in $old) { $oldMap[$item.FullName] = $item }
$newMap = @{}
foreach ($item in $new) { $newMap[$item.FullName] = $item }

$allPaths = ($oldMap.Keys + $newMap.Keys | Sort-Object -Unique)
$report = foreach ($path in $allPaths) {
    $o = $oldMap[$path]
    $n = $newMap[$path]

    if (-not $o -and $n) {
        [pscustomobject]@{
            Status = 'New'
            FullName = $n.FullName
            Directory = $n.Directory
            Name = $n.Name
            Extension = $n.Extension
            OldLength = ''
            NewLength = $n.Length
            OldLastWriteTime = ''
            NewLastWriteTime = $n.LastWriteTime
        }
        continue
    }

    if ($o -and -not $n) {
        [pscustomobject]@{
            Status = 'Deleted'
            FullName = $o.FullName
            Directory = $o.Directory
            Name = $o.Name
            Extension = $o.Extension
            OldLength = $o.Length
            NewLength = ''
            OldLastWriteTime = $o.LastWriteTime
            NewLastWriteTime = ''
        }
        continue
    }

    if ($o.Length -ne $n.Length -or $o.LastWriteTime -ne $n.LastWriteTime) {
        [pscustomobject]@{
            Status = 'Changed'
            FullName = $n.FullName
            Directory = $n.Directory
            Name = $n.Name
            Extension = $n.Extension
            OldLength = $o.Length
            NewLength = $n.Length
            OldLastWriteTime = $o.LastWriteTime
            NewLastWriteTime = $n.LastWriteTime
        }
    }
}

$timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$basePath = Join-Path $PSScriptRoot "reports\changes_$timestamp"
$report = @($report | Sort-Object Status, Directory, Name)
Export-TableFiles -Rows $report -BasePath $basePath -WorksheetName 'Changes'
Write-Output "Compared:`nOLD = $OldSnapshot`nNEW = $NewSnapshot"
