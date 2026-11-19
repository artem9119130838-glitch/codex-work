param (
    [string]$ImagePath
)

$winmdList = @(
    "C:\Windows\System32\WinMetadata\Windows.Foundation.winmd",
    "C:\Windows\System32\WinMetadata\Windows.Storage.winmd",
    "C:\Windows\System32\WinMetadata\Windows.Graphics.winmd",
    "C:\Windows\System32\WinMetadata\Windows.Media.winmd",
    "C:\Windows\System32\WinMetadata\Windows.Globalization.winmd",
    "System.Runtime.WindowsRuntime",
    "System.Drawing"
)

Add-Type -ReferencedAssemblies $winmdList -TypeDefinition @'
using System;
using System.IO;
using System.Threading.Tasks;
using Windows.Globalization;
using Windows.Graphics.Imaging;
using Windows.Media.Ocr;
using Windows.Storage;

public class WinOcr {
    public static async Task<string> RecognizeFileAsync(string filePath) {
        StorageFile file = await StorageFile.GetFileFromPathAsync(filePath);
        using (var stream = await file.OpenAsync(FileAccessMode.Read)) {
            var decoder = await BitmapDecoder.CreateAsync(stream);
            var softwareBitmap = await decoder.GetSoftwareBitmapAsync();
            var engine = OcrEngine.TryCreateFromLanguage(new Language("ru")) ?? OcrEngine.TryCreateFromUserProfileLanguages();
            var result = await engine.RecognizeAsync(softwareBitmap);
            return result.Text;
        }
    }

    public static string Recognize(string filePath) {
        return RecognizeFileAsync(filePath).GetAwaiter().GetResult();
    }
}
'@

function Run-OcrOnFile {
    param([string]$FilePath)
    
    Write-Output "=== PROCESSING: $FilePath ==="
    
    $fullPath = [System.IO.Path]::GetFullPath($FilePath)
    $bmp = [System.Drawing.Bitmap]::FromFile($fullPath)
    $origW = $bmp.Width
    $origH = $bmp.Height
    Write-Output "Dimensions: ${origW} x ${origH}"
    
    $scale = 1.0
    $maxDim = [Math]::Max($origW, $origH)
    if ($maxDim > 3500) {
        $scale = 3500.0 / $maxDim
    }
    
    $tempPng = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "ocr_temp_" + [System.Guid]::NewGuid().ToString("N") + ".png")
    if ($scale -ne 1.0 -or $FilePath.ToLower().EndsWith(".tif")) {
        $newW = [int]($origW * $scale)
        $newH = [int]($origH * $scale)
        $resized = new-object System.Drawing.Bitmap $newW, $newH
        $g = [System.Drawing.Graphics]::FromImage($resized)
        $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $g.DrawImage($bmp, 0, 0, $newW, $newH)
        $g.Dispose()
        $bmp.Dispose()
        $resized.Save($tempPng, [System.Drawing.Imaging.ImageFormat]::Png)
        $resized.Dispose()
        $processPath = $tempPng
    } else {
        $bmp.Dispose()
        $processPath = $fullPath
    }
    
    try {
        $text = [WinOcr]::Recognize($processPath)
        Write-Output "--- OCR TEXT START ---"
        Write-Output $text
        Write-Output "--- OCR TEXT END ---"
    }
    finally {
        if (Test-Path $tempPng) {
            Remove-Item $tempPng -Force -ErrorAction SilentlyContinue
        }
    }
}

if ($ImagePath) {
    Run-OcrOnFile -FilePath $ImagePath
}
