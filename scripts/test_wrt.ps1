Add-Type -AssemblyName 'System.Runtime.WindowsRuntime'
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null

$op = [Windows.Storage.StorageFile]::GetFileFromPathAsync("C:\Windows\System32\notepad.exe")

$method = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { 
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' 
}
$concreteMethod = $method.MakeGenericMethod([Windows.Storage.StorageFile])
$task = $concreteMethod.Invoke($null, @($op))
$task.Wait()
Write-Output "File path: $($task.Result.Path)"
