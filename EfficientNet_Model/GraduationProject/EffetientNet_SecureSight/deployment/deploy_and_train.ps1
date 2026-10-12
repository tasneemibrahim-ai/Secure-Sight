# ============================================================
# tasnim - Deploy, Train, and Download Results
# ============================================================
# This script:
#   1. Creates a project folder on the server
#   2. Uploads all tasnim code files
#   3. Runs training on the server
#   4. Downloads results (CSV, plots, reports) back to local
# ============================================================
# Usage:
#   cd "e:\tasnim\Graduation project model\tasnim"
#   .\deploy_and_train.ps1
#
# Optional parameters:
#   .\deploy_and_train.ps1 -Epochs 30 -BatchSize 16 -LR 0.0001 -RunName "experiment_1"
# ============================================================

param(
    [int]$Epochs = 50,
    [int]$BatchSize = 32,
    [string]$LR = "1e-4",
    [string]$Dropout = "0.3",
    [string]$RunName = "",
    [string]$ServerUser = "secure-sight",
    [string]$ServerHost = "10.55.205.205",
    [string]$ServerDir = "/home/secure-sight/tasnim"
)

$ErrorActionPreference = "Stop"

#  Configuration 
$ServerTarget = "${ServerUser}@${ServerHost}"
$LocalDir = $PSScriptRoot  # Directory where this script lives
$ResultsLocalDir = Join-Path $LocalDir "downloaded_results"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  tasnim - Deploy & Train Pipeline" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Server:     $ServerTarget" -ForegroundColor Yellow
Write-Host "  Remote Dir: $ServerDir" -ForegroundColor Yellow
Write-Host "  Epochs:     $Epochs" -ForegroundColor Yellow
Write-Host "  Batch Size: $BatchSize" -ForegroundColor Yellow
Write-Host "  LR:         $LR" -ForegroundColor Yellow
if ($RunName) {
    Write-Host "  Run Name:   $RunName" -ForegroundColor Yellow
}
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 
# STEP 1: Create project folder on server
# 
Write-Host "[STEP 1/5] Creating project folder on server..." -ForegroundColor Green
ssh $ServerTarget "mkdir -p $ServerDir/outputs/logs $ServerDir/outputs/checkpoints $ServerDir/outputs/runs"
Write-Host "   Folder created: $ServerDir" -ForegroundColor DarkGreen

# 
# STEP 2: Upload all project files
# 
Write-Host ""
Write-Host "[STEP 2/5] Uploading project files to server..." -ForegroundColor Green

# Upload Python files + requirements + run script
$FilesToUpload = @(
    "config.py",
    "dataset.py",
    "model.py",
    "train.py",
    "utils.py",
    "run_tracker.py",
    "diagnostics.py",
    "run_final_pipeline.py",
    "secure_leakage_reconstruction.py",
    "autonomous_fix_pipeline.py",
    "requirements.txt",
    "run.sh"
)

foreach ($file in $FilesToUpload) {
    $localFile = Join-Path $LocalDir $file
    if (Test-Path $localFile) {
        scp $localFile "${ServerTarget}:${ServerDir}/${file}"
        Write-Host "   Uploaded: $file" -ForegroundColor DarkGreen
    } else {
        Write-Host "   File not found: $file" -ForegroundColor Red
    }
}

# Make run.sh executable
ssh $ServerTarget "chmod +x $ServerDir/run.sh"
Write-Host "   All files uploaded successfully" -ForegroundColor DarkGreen

# 
# STEP 3: Install dependencies on server
# 
Write-Host ""
Write-Host "[STEP 3/5] Installing dependencies on server..." -ForegroundColor Green
ssh $ServerTarget "cd $ServerDir && pip install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt"
Write-Host "   Dependencies installed" -ForegroundColor DarkGreen

# 
# STEP 4: Run training on server
# 
Write-Host ""
Write-Host "[STEP 4/5] Starting training on server..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Training will stream output below." -ForegroundColor Yellow
Write-Host "  Results are recorded after EVERY epoch." -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to cancel (progress is saved)." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Build train command
$TrainCmd = "cd $ServerDir && python3 train.py --epochs $Epochs --batch_size $BatchSize --lr $LR --dropout $Dropout"
if ($RunName) {
    $TrainCmd += " --run_name $RunName"
}

# Run training via SSH with live output streaming
ssh $ServerTarget $TrainCmd

Write-Host ""
Write-Host "   Training completed!" -ForegroundColor DarkGreen

# 
# STEP 5: Download results back to local machine
# 
Write-Host ""
Write-Host "[STEP 5/5] Downloading results from server..." -ForegroundColor Green

# Create local results directory with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DownloadDir = Join-Path $ResultsLocalDir $timestamp
New-Item -ItemType Directory -Force -Path $DownloadDir | Out-Null

# Download outputs directory (logs, runs, checkpoints)
scp -r "${ServerTarget}:${ServerDir}/outputs/logs" "$DownloadDir/"
Write-Host "   Downloaded: logs/ (CSV + plots)" -ForegroundColor DarkGreen

scp -r "${ServerTarget}:${ServerDir}/outputs/runs" "$DownloadDir/"
Write-Host "   Downloaded: runs/ (per-run results)" -ForegroundColor DarkGreen

# Download the all-runs report and comparison plot
scp "${ServerTarget}:${ServerDir}/outputs/all_runs_report.txt" "$DownloadDir/" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Downloaded: all_runs_report.txt" -ForegroundColor DarkGreen
}

scp "${ServerTarget}:${ServerDir}/outputs/all_runs_comparison.png" "$DownloadDir/" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Downloaded: all_runs_comparison.png" -ForegroundColor DarkGreen
}

# Download best model checkpoint
$CheckpointDir = Join-Path $DownloadDir "checkpoints"
New-Item -ItemType Directory -Force -Path $CheckpointDir | Out-Null
scp "${ServerTarget}:${ServerDir}/outputs/checkpoints/best_model.pth" "$CheckpointDir/" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Downloaded: best_model.pth" -ForegroundColor DarkGreen
}

# 
# SUMMARY
# 
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Pipeline Complete!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Local results saved to:" -ForegroundColor Yellow
Write-Host "    $DownloadDir" -ForegroundColor White
Write-Host ""
Write-Host "  Key files:" -ForegroundColor Yellow
Write-Host "    - training_results.csv     (epoch-by-epoch metrics)" -ForegroundColor White
Write-Host "    - training_curves.png      (loss/acc/F1 plots)" -ForegroundColor White
Write-Host "    - all_runs_report.txt      (all training runs summary)" -ForegroundColor White
Write-Host "    - all_runs_comparison.png  (cross-run comparison graphs)" -ForegroundColor White
Write-Host "    - best_model.pth           (best model weights)" -ForegroundColor White
Write-Host ""
Write-Host "  Server files remain at:" -ForegroundColor Yellow
Write-Host "    ${ServerTarget}:${ServerDir}/outputs/" -ForegroundColor White
Write-Host ""

# Open the results folder
Write-Host "Opening results folder..." -ForegroundColor Green
Start-Process explorer $DownloadDir

