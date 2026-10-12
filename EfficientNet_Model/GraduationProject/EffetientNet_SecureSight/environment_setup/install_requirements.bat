@echo off
REM ============================================================
REM  SecureSight — Environment Setup (Windows)
REM  AI Video Anomaly Detection — EfficientNet-B0
REM ============================================================
REM  Usage:  install_requirements.bat
REM  Run from the Recovered_Project\environment_setup\ folder
REM ============================================================

echo ============================================================
echo   SecureSight Environment Setup
echo ============================================================
echo.

REM Step 1: Check Python
echo [1/5] Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Install Python 3.9+ first.
    pause
    exit /b 1
)

REM Step 2: Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if not exist "..\venv" (
    python -m venv ..\venv
    echo   Virtual environment created at ..\venv
) else (
    echo   Virtual environment already exists.
)

REM Step 3: Activate venv
echo.
echo [3/5] Activating virtual environment...
call ..\venv\Scripts\activate.bat

REM Step 4: Upgrade pip
echo.
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip

REM Step 5: Install requirements
echo.
echo [5/5] Installing requirements...
pip install -r requirements.txt

REM Extra: Install deployment dependencies
echo.
echo [EXTRA] Installing deployment dependencies...
pip install fastapi uvicorn paramiko onnx onnxruntime psutil

echo.
echo ============================================================
echo   Setup complete!
echo   Activate with: ..\venv\Scripts\activate.bat
echo ============================================================
pause
