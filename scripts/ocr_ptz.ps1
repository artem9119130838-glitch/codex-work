. c:\Codex\scripts\run_ocr_win.ps1
$folder = 'c:\Codex\scratch\ptz_pages'
$files = Get-ChildItem -Path $folder -Filter "*.png"
foreach ($f in $files) {
    Run-OcrOnFile -FilePath $f.FullName
}
