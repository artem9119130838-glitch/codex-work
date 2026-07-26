# Конфигурация
$VpsIp = "109.248.170.181"
$VpsUser = "root"
$SshKey = "C:\Users\Артем\.ssh\id_ed25519_wlisses"
$LocalBackupDir = "D:\server-backups"
$RemoteStorageDir = "/Storage"
$RetentionDays = 30

Write-Host "=== Запуск скачивания бэкапа VPS ===" -ForegroundColor Cyan

# Проверяем наличие папки для бэкапов
if (!(Test-Path $LocalBackupDir)) {
    New-Item -ItemType Directory -Force -Path $LocalBackupDir | Out-Null
    Write-Host "Создана локальная директория: $LocalBackupDir"
}

# Получаем имя последнего бэкапа с сервера
Write-Host "Поиск последнего бэкапа на сервере..."
$sshCmd = "ssh -i `"$SshKey`" $VpsUser@$VpsIp `"ls -td $RemoteStorageDir/full-backup-* 2>/dev/null | head -n 1`""
$latestRemotePath = Invoke-Expression $sshCmd

if ([string]::IsNullOrEmpty($latestRemotePath)) {
    Write-Error "Не удалось найти бэкапы на сервере в директории $RemoteStorageDir"
    exit 1
}

$latestRemotePath = $latestRemotePath.Trim()
$backupFolderName = Split-Path $latestRemotePath -Leaf
Write-Host "Последний бэкап на сервере: $backupFolderName" -ForegroundColor Yellow

$localDestPath = Join-Path $LocalBackupDir $backupFolderName

# Проверяем, скачан ли уже этот бэкап
if (Test-Path $localDestPath) {
    Write-Host "Бэкап $backupFolderName уже скачан локально. Пропуск." -ForegroundColor Green
} else {
    Write-Host "Запуск скачивания бэкапа $backupFolderName ($latestRemotePath)..." -ForegroundColor Yellow
    $scpCmd = "scp -r -i `"$SshKey`" $VpsUser@$VpsIp:`"$latestRemotePath`" `"$LocalBackupDir`""
    
    $startTime = Get-Date
    Invoke-Expression $scpCmd
    $endTime = Get-Date
    
    if (Test-Path $localDestPath) {
        $duration = ($endTime - $startTime).TotalMinutes
        Write-Host "Бэкап успешно скачан за $($duration.ToString('F1')) мин. Локальный путь: $localDestPath" -ForegroundColor Green
    } else {
        Write-Error "Ошибка при скачивании бэкапа через scp."
        exit 1
    }
}

# Ротация локальных бэкапов
Write-Host "Проверка ротации локальных бэкапов (удаление старше $RetentionDays дней)..."
$limitDate = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $LocalBackupDir -Directory -Filter "full-backup-*" | ForEach-Object {
    if ($_.CreationTime -lt $limitDate) {
        Write-Host "Удаление старого локального бэкапа: $($_.Name)" -ForegroundColor Gray
        Remove-Item $_.FullName -Recurse -Force
    }
}

Write-Host "=== Синхронизация бэкапов завершена ===" -ForegroundColor Green
