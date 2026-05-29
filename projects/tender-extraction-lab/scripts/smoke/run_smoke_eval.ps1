Param(
  [string]$ProjectRoot = "E:\\Codex_Work\\projects\\tender-extraction-lab"
)

$ErrorActionPreference = "Stop"

$evalScript = Join-Path $ProjectRoot "scripts\\eval\\eval_min_context_vs_gold_19_05.py"
if (-not (Test-Path -LiteralPath $evalScript)) {
  throw "Eval script not found. Run migration copy first: $evalScript"
}

$goldXlsxDir = Join-Path $ProjectRoot "data\\gold\\19-05"
$goldXlsx = $null
if (Test-Path -LiteralPath $goldXlsxDir) {
  $goldXlsx = Get-ChildItem -LiteralPath $goldXlsxDir -Filter "*.xlsx" -File | Where-Object { $_.Name -like "*19-05*" } | Select-Object -First 1
}
$triesResults = Join-Path $ProjectRoot "legacy\\old_project\\ACT\\tries\\results.jsonl"
$legacyExtractor = Join-Path $ProjectRoot "legacy\\old_project\\ACT\\tender_min_context_extractor_v1.py"
$outReport = Join-Path $ProjectRoot "reports\\smoke_eval_report.md"

New-Item -ItemType Directory -Path (Split-Path -Parent $outReport) -Force | Out-Null

$script:lines = @()
$script:lines += "# Smoke Eval Report"
$script:lines += ""
$script:lines += "- Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$script:lines += "- ProjectRoot: $ProjectRoot"
$script:lines += ""

function Add-Check([string]$name, [bool]$ok, [string]$details) {
  $status = if ($ok) { "OK" } else { "FAIL" }
  $script:lines += "## $name"
  $script:lines += ""
  $script:lines += "- Status: $status"
  if ($details) {
    $script:lines += "- Details: $details"
  }
  $script:lines += ""
}

Add-Check "Gold XLSX present" ($null -ne $goldXlsx) ($(if ($null -ne $goldXlsx) { $goldXlsx.FullName } else { $goldXlsxDir }))
Add-Check "Tries results present" (Test-Path -LiteralPath $triesResults) $triesResults
Add-Check "Legacy extractor present" (Test-Path -LiteralPath $legacyExtractor) $legacyExtractor

Push-Location $ProjectRoot
try {
  $helpOut = (py -3 $evalScript -h 2>&1 | Out-String).Trim()
  Add-Check "Eval script help runs" ($helpOut.Length -gt 0) "Captured -h output"
  $script:lines += "### eval_min_context_vs_gold_19_05.py -h"
  $script:lines += ""
  $script:lines += "~~~text"
  $script:lines += $helpOut
  $script:lines += "~~~"
  $script:lines += ""
} catch {
  Add-Check "Eval script help runs" $false $_.Exception.Message
} finally {
  Pop-Location
}

Set-Content -LiteralPath $outReport -Value ($script:lines -join "`n") -Encoding UTF8
Write-Host "Done. Smoke report: $outReport"
