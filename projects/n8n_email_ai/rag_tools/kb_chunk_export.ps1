$ErrorActionPreference = "Stop"

$root = "E:\Codex_Work"
$tool = Join-Path $root "projects\n8n_email_ai\rag_tools\md_chunker.py"
$outDir = Join-Path $root "projects\n8n_email_ai\rag_tools\out"

$targets = @(
  @{ Path = (Join-Path $root "codex_kb\00_global"); Category = "infrastructure" },
  @{ Path = (Join-Path $root "codex_kb\20_domains"); Category = "methods" },
  @{ Path = (Join-Path $root "codex_kb\30_runbooks"); Category = "infrastructure" }
)

New-Item -ItemType Directory -Path $outDir -Force | Out-Null

foreach ($t in $targets) {
  $dir = $t.Path
  $category = $t.Category

  if (-not (Test-Path -LiteralPath $dir)) { continue }

  Get-ChildItem -LiteralPath $dir -Recurse -File -Filter *.md | ForEach-Object {
    $inPath = $_.FullName
    $rel = $inPath.Substring($root.Length).TrimStart('\')
    $safeName = ($rel -replace '[\\\\/:*?\"<>|]', '_')
    $outPath = Join-Path $outDir ($safeName + ".jsonl")

    py -3 $tool --in $inPath --category $category --out $outPath | Out-Null
  }
}

Write-Host ("OK: exported JSONL to " + $outDir)

