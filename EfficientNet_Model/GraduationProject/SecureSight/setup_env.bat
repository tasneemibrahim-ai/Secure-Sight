@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   SecureSight Environment Setup (Batch)
echo ============================================================
echo.

REM Set paths
set VENV_PYTHON=.venv310\Scripts\python.exe
set VENV_PIP=%VENV_PYTHON% -m pip

REM Step 1: Upgrade pip
echo [1/6] Upgrading pip, setuptools, wheel...
call %VENV_PIP% install --upgrade pip setuptools wheel -q
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    exit /b 1
)
echo OK - pip upgraded
echo.

REM Step 2: Install PyTorch
echo [2/6] Installing PyTorch (CPU)...
call %VENV_PIP% install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu -q
if errorlevel 1 (
    echo ERROR: Failed to install PyTorch
    exit /b 1
)
echo OK - PyTorch installed
echo.

REM Step 3: Verify PyTorch
echo [3/6] Verifying PyTorch...
call %VENV_PYTHON% -c "import torch; print(f'PyTorch {torch.__version__} OK')"
if errorlevel 1 (
    echo ERROR: PyTorch import failed
    exit /b 1
)
echo.

REM Step 4: Install dependencies
echo [4/6] Installing dependencies...
set DEPS=numpy opencv-python pillow matplotlib scikit-learn pandas tqdm onnx onnxruntime psutil pyyaml scipy seaborn requests rich
call %VENV_PIP% install %DEPS% -q
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo OK - Dependencies installed
echo.

REM Step 5: Install airsim packages
echo [5/6] Installing airsim packages (may fail - OK if mock mode)...
call %VENV_PIP% install msgpack-rpc-python -q 2>nul
call %VENV_PIP% install airsim --no-build-isolation -q 2>nul
echo.

REM Step 6: Verify imports
echo [6/6] Verifying imports...
call %VENV_PYTHON% -c "import torch, torchvision, cv2, numpy, onnxruntime; print('All imports OK')"
if errorlevel 1 (
    echo ERROR: Import verification failed
    exit /b 1
)
echo.

echo ============================================================
echo    Setup Complete!
echo ============================================================
echo.
echo Environment ready. To use:
echo   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
echo   .\.venv310\Scripts\Activate.ps1
echo.
echo Or run directly:
echo   .\.venv310\Scripts\python.exe script.py
echo.

