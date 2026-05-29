Param(
  [string]$SourceRoot = "C:\\Users\\Artem\\Downloads\\GOZ",
  [string]$ProjectRoot = "E:\\Codex_Work\\projects\\tender-extraction-lab"
)

$ErrorActionPreference = "Stop"

$manifestPath = Join-Path $ProjectRoot ".codex\\migration-manifest.csv"
$reportPath = Join-Path $ProjectRoot "reports\\migration_copy_report.md"

if (-not (Test-Path -LiteralPath $manifestPath)) {
  throw "Manifest not found: $manifestPath"
}
if (-not (Test-Path -LiteralPath $SourceRoot)) {
  throw "Source root not found: $SourceRoot"
}

function Read-Utf8Csv([string]$path) {
  try {
    return Import-Csv -LiteralPath $path -Encoding UTF8
  } catch {
    $text = Get-Content -LiteralPath $path -Raw -Encoding UTF8
    return $text | ConvertFrom-Csv
  }
}

$rows = Read-Utf8Csv $manifestPath

# Only copy the minimal subset described in the accepted plan.
$allowedPrefixes = @(
  "data/gold/",
  "scripts/eval/",
  "scripts/batch/",
  "legacy/old_project/"
)

$copied = New-Object System.Collections.Generic.List[string]
$missing = New-Object System.Collections.Generic.List[string]
$skipped = New-Object System.Collections.Generic.List[string]

foreach ($r in $rows) {
  $copyAsIs = ($r.copy_as_is -as [string]).ToLowerInvariant() -eq "true"
  if (-not $copyAsIs) {
    $skipped.Add($r.old_path)
    continue
  }

  $newPath = ($r.new_path -as [string]).Replace("\\", "/")
  $allowed = $false
  foreach ($p in $allowedPrefixes) {
    if ($newPath.StartsWith($p)) { $allowed = $true; break }
  }
  if (-not $allowed) {
    $skipped.Add($r.old_path)
    continue
  }

  $src = Join-Path $SourceRoot $r.old_path
  $dst = Join-Path $ProjectRoot $r.new_path

  if (-not (Test-Path -LiteralPath $src)) {
    $missing.Add($r.old_path)
    continue
  }

  $dstDir = Split-Path -Parent $dst
  if (-not (Test-Path -LiteralPath $dstDir)) {
    New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
  }

  Copy-Item -LiteralPath $src -Destination $dst -Force
  $copied.Add($r.old_path)
}

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$report = @()
$report += "# Migration Copy Report"
$report += ""
$report += "- Timestamp: $stamp"
$report += "- SourceRoot: $SourceRoot"
$report += "- ProjectRoot: $ProjectRoot"
$report += "- Manifest: .codex/migration-manifest.csv"
$report += ""
$report += "## Copied"
$report += ""
if ($copied.Count -eq 0) { $report += "(none)" } else { $report += ($copied | Sort-Object | ForEach-Object { "- $_" }) }
$report += ""
$report += "## Missing (not found in source)"
$report += ""
if ($missing.Count -eq 0) { $report += "(none)" } else { $report += ($missing | Sort-Object | ForEach-Object { "- $_" }) }
$report += ""
$report += "## Skipped"
$report += ""
$report += "Skipped means: copy_as_is!=true OR outside allowed prefixes ($($allowedPrefixes -join ', '))."
$report += ""
if ($skipped.Count -eq 0) { $report += "(none)" } else { $report += ($skipped | Sort-Object | ForEach-Object { "- $_" }) }

New-Item -ItemType Directory -Path (Split-Path -Parent $reportPath) -Force | Out-Null
Set-Content -LiteralPath $reportPath -Value ($report -join "`n") -Encoding UTF8

Write-Host "Done. Report: $reportPath"
