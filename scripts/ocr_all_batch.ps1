. c:\Codex\scripts\run_ocr_win.ps1
$folder = 'D:\Документы Victus\Рабочее\В работе\Машиностроитель\Агрегат для отжига'
$tifs = @(
    '124554_Оправка раздвижная эскиз, л.1.tif',
    '124556_Оправка раздвижная эскиз, л2.tif',
    '124558_Оправка раздвижная эскиз, л3.tif',
    '124560_Поз.18 оправка.tif'
)
foreach ($t in $tifs) {
    $p = Join-Path $folder $t
    Run-OcrOnFile -FilePath $p
}
