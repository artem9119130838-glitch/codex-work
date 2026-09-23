# Configuration
$VpsIp = "109.248.170.181"
$VpsUser = "root"
$SshKey = "$env:USERPROFILE\.ssh\id_ed25519_wlisses"
$LocalBackupDir = "D:\server-backups"
$LogFile = "D:\server-backups\auto_download.log"

if (!(Test-Path $LocalBackupDir)) {
    New-Item -ItemType Directory -Force -Path $LocalBackupDir | Out-Null
}

function Log-Message($msg) {
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $formatted = "[$timestamp] $msg"
    Write-Host $formatted -ForegroundColor Cyan
    Add-Content -Path $LogFile -Value $formatted
}

Log-Message "=== Waiting for VPS full backup to finish and downloading to D:\ ==="

$maxMinutes = 180
$elapsed = 0

while ($elapsed -lt $maxMinutes) {
    $checkCmd = "ssh -i `"$SshKey`" $VpsUser@$VpsIp `"pgrep -f run_server_backup.sh`""
    $runningPid = Invoke-Expression $checkCmd 2>$null
    
    if ([string]::IsNullOrWhiteSpace($runningPid)) {
        Log-Message "[+] VPS Backup script finished!"
        break
    }
    
    Log-Message "[-] Backup in progress on server (PID: $runningPid). Waiting 30s... (Elapsed: $elapsed min)"
    Start-Sleep -Seconds 30
    $elapsed += 0.5
}

Log-Message "[+] Starting download to D:\server-backups..."
& "$PSScriptRoot\download_vps_backup.ps1"

Log-Message "=== Full backup successfully downloaded to D:\server-backups! ==="
