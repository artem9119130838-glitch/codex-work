param (
    [string]$ImagePath
)

Add-Type -AssemblyName 'System.Runtime.WindowsRuntime'

[Windows.Globalization.Language, Windows.Globalization, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null

$script:asTaskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { 
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' 
}

function Await-AsyncOp($op, $resultType) {
    $concrete = $script:asTaskMethod.MakeGenericMethod($resultType)
    $task = $concrete.Invoke($null, @($op))
    $task.Wait()
    return $task.Result
}

function Run-OcrOnFile {
    param([string]$FilePath)
    
    $fullPath = [System.IO.Path]::GetFullPath($FilePath)
    Write-Output "=== PROCESSING: $fullPath ==="
    
    $storageFile = Await-AsyncOp ([Windows.Storage.StorageFile]::GetFileFromPathAsync($fullPath)) ([Windows.Storage.StorageFile])
    $stream = Await-AsyncOp ($storageFile.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await-AsyncOp ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $softBmp = Await-AsyncOp ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    
    $lang = [Windows.Globalization.Language]::new("ru")
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
    if (-not $engine) {
        $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
    }
    
    $ocrResult = Await-AsyncOp ($engine.RecognizeAsync($softBmp)) ([Windows.Media.Ocr.OcrResult])
    Write-Output "--- OCR TEXT START ---"
    Write-Output $ocrResult.Text
    Write-Output "--- OCR TEXT END ---"
    
    $stream.Dispose()
}

if ($ImagePath) {
    Run-OcrOnFile -FilePath $ImagePath
}
