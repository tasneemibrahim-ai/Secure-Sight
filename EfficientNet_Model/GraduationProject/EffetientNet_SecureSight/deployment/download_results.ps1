# ============================================================
# SecureSight — Download Results from Server
# ============================================================
# Downloads training results, run reports, and comparison plots
# from the server WITHOUT re-training.
# ============================================================
# Usage:
#   cd "e:\tasnim\Graduation project model\SecureSight"
#   .\download_results.ps1
# ============================================================

param(
    [string]$ServerUser = "secure-sight",
    [string]$ServerHost = "10.55.205.205",
    [string]$ServerDir = "/home/secure-sight/SecureSight"
)

$ServerTarget = "${ServerUser}@${ServerHost}"
$LocalDir = $PSScriptRoot
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DownloadDir = Join-Path $LocalDir "downloaded_results" $timestamp

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SecureSight — Download Results" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Server: $ServerTarget" -ForegroundColor Yellow
Write-Host "  Saving to: $DownloadDir" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

New-Item -ItemType Directory -Force -Path $DownloadDir | Out-Null

# Download everything from outputs/
Write-Host "Downloading all outputs..." -ForegroundColor Green
scp -r "${ServerTarget}:${ServerDir}/outputs/" "$DownloadDir/"

Write-Host ""
Write-Host "  ✓ Results downloaded to: $DownloadDir" -ForegroundColor DarkGreen
Write-Host ""

# List what was downloaded
Write-Host "Downloaded files:" -ForegroundColor Yellow
Get-ChildItem -Recurse $DownloadDir | ForEach-Object {
    $rel = $_.FullName.Replace($DownloadDir, "")
    if ($_.PSIsContainer) {
        Write-Host "  📁 $rel" -ForegroundColor Cyan
    } else {
        $size = "{0:N1} KB" -f ($_.Length / 1024)
        Write-Host "  📄 $rel ($size)" -ForegroundColor White
    }
}

Write-Host ""
Start-Process explorer $DownloadDir
