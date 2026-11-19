. c:\Codex\scripts\run_ocr_win.ps1
$folder = 'c:\Codex\scratch\crops_bom'
$files = Get-ChildItem -Path $folder -Filter "*.png"
foreach ($f in $files) {
    Run-OcrOnFile -FilePath $f.FullName
}
